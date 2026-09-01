# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the ``confluence_fetch`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import httpx

from biz.dfch.specmgr.general.tools._confluence_config import (
    CONFLUENCE_BASE_URL_ENV_VAR,
    CONFLUENCE_BEARER_ENV_VAR,
    ConfluenceNotConfiguredError,
)
from biz.dfch.specmgr.general.tools.confluence_fetch import (
    ConfluenceAuthRedirectError,
    ConfluenceDestinationPathRequiredError,
    ConfluenceTinyLinkNotSupportedError,
    ConfluenceUrlNotAllowedError,
    confluence_fetch,
)

_BASE_URL = "https://example.atlassian.net/wiki"
_TOKEN = "s3cr3t-token"


def _make_response(
    *,
    text: str = "",
    content: bytes = b"",
    content_type: str = "text/html",
    url: str = f"{_BASE_URL}/final",
) -> mock.Mock:
    """Build a mocked ``httpx.Response`` with the attributes confluence_fetch inspects."""
    response = mock.Mock(spec=httpx.Response)
    response.text = text
    response.content = content
    response.headers = {"content-type": content_type}
    response.url = httpx.URL(url)
    response.raise_for_status = mock.Mock()
    return response


class TestConfluenceFetchTool(unittest.TestCase):
    """Tests for the confluence_fetch tool."""

    def test_url_outside_base_is_rejected_without_http_call(self) -> None:
        """A URL outside the configured base must raise, with no HTTP call made."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(ConfluenceUrlNotAllowedError):
                    confluence_fetch("https://not-allowed.example.com/page")
                mock_get.assert_not_called()

    def test_case_insensitive_scheme_host_match_is_accepted(self) -> None:
        """A URL matching the base with different casing in scheme/host must be accepted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text="page content")
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                result = confluence_fetch("HTTPS://Example.atlassian.net/wiki/page")

                self.assertEqual(result, "page content")
                mock_get.assert_called_once()

    def test_case_insensitive_configured_base_url_is_accepted(self) -> None:
        """A URL matching a differently-cased configured base URL must be accepted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: "HTTPS://EXAMPLE.ATLASSIAN.NET/WIKI", CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text="page content")
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                result = confluence_fetch("https://example.atlassian.net/wiki/page")

                self.assertEqual(result, "page content")
                mock_get.assert_called_once()

    def test_missing_base_url_env_var_raises_not_configured(self) -> None:
        """Missing the base-URL env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {CONFLUENCE_BEARER_ENV_VAR: _TOKEN}, clear=True):
            os.environ.pop(CONFLUENCE_BASE_URL_ENV_VAR, None)
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(ConfluenceNotConfiguredError):
                    confluence_fetch(f"{_BASE_URL}/page")
                mock_get.assert_not_called()

    def test_missing_bearer_env_var_raises_not_configured(self) -> None:
        """Missing the bearer-token env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL}, clear=True):
            os.environ.pop(CONFLUENCE_BEARER_ENV_VAR, None)
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(ConfluenceNotConfiguredError):
                    confluence_fetch(f"{_BASE_URL}/page")
                mock_get.assert_not_called()

    def test_missing_both_env_vars_raises_not_configured(self) -> None:
        """Missing both env vars must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop(CONFLUENCE_BASE_URL_ENV_VAR, None)
            os.environ.pop(CONFLUENCE_BEARER_ENV_VAR, None)
            with self.assertRaises(ConfluenceNotConfiguredError):
                confluence_fetch(f"{_BASE_URL}/page")

    def test_successful_call_sends_bearer_header_and_returns_body(self) -> None:
        """A successful call must send the Authorization header and return raw body text."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text="<html>raw body</html>")
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                # No page id extractable and not a spaces/pages/pageId URL -- fetched unchanged.
                url = f"{_BASE_URL}/overview"
                result = confluence_fetch(url)

                self.assertEqual(result, "<html>raw body</html>")
                mock_get.assert_called_once()
                call_args, call_kwargs = mock_get.call_args
                self.assertEqual(call_args[0], url)
                self.assertEqual(call_kwargs["headers"], {"Authorization": f"Bearer {_TOKEN}"})
                self.assertTrue(call_kwargs["follow_redirects"])
                mock_response.raise_for_status.assert_called_once()

    def test_non_2xx_response_raises(self) -> None:
        """A non-2xx response must raise (via response.raise_for_status())."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text="not found")
            mock_response.raise_for_status = mock.Mock(
                side_effect=httpx.HTTPStatusError("404", request=mock.Mock(), response=mock_response)
            )
            with mock.patch("httpx.get", return_value=mock_response):
                with self.assertRaises(httpx.HTTPStatusError):
                    confluence_fetch(f"{_BASE_URL}/missing")

    # -- ACC-001: automatic REST URL construction -----------------------------------------------

    def test_cloud_style_pages_url_is_converted_to_rest_content_url(self) -> None:
        """A Cloud-style /pages/<id>/<title> URL must be converted to the REST content URL."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text='{"body": {}}', content_type="application/json")
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                url = f"{_BASE_URL}/spaces/FOO/pages/123456/My+Page"
                result = confluence_fetch(url)

                self.assertEqual(result, '{"body": {}}')
                call_args, _call_kwargs = mock_get.call_args
                self.assertEqual(call_args[0], f"{_BASE_URL}/rest/api/content/123456?expand=body.storage")

    def test_server_style_pageid_url_is_converted_to_rest_content_url(self) -> None:
        """A Server-style ?pageId=<id> URL must be converted to the REST content URL."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text='{"body": {}}', content_type="application/json")
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                url = f"{_BASE_URL}/pages/viewpage.action?pageId=789"
                result = confluence_fetch(url)

                self.assertEqual(result, '{"body": {}}')
                call_args, _call_kwargs = mock_get.call_args
                self.assertEqual(call_args[0], f"{_BASE_URL}/rest/api/content/789?expand=body.storage")

    def test_rest_or_download_url_is_passed_through_unchanged(self) -> None:
        """A URL that already looks like a REST/download URL must not be re-converted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text='{"already": "rest"}', content_type="application/json")
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                # Note: this URL also contains a numeric /pages/<id>/ segment that extract_page_id
                # would otherwise match -- looks_like_rest_or_download_url must take priority.
                url = f"{_BASE_URL}/rest/api/content/123?expand=body.storage"
                result = confluence_fetch(url)

                self.assertEqual(result, '{"already": "rest"}')
                call_args, _call_kwargs = mock_get.call_args
                self.assertEqual(call_args[0], url)

    def test_download_url_is_passed_through_unchanged(self) -> None:
        """A URL that already looks like a download URL must not be re-converted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                destination_path = str(Path(tmp_dir) / "image.png")
                mock_response = _make_response(content=b"\x89PNG", content_type="image/png")
                with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                    url = f"{_BASE_URL}/download/attachments/123/image.png"
                    result = confluence_fetch(url, destination_path=destination_path)

                    self.assertEqual(result, destination_path)
                    call_args, _call_kwargs = mock_get.call_args
                    self.assertEqual(call_args[0], url)

    # -- ACC-002: tiny-link rejection ------------------------------------------------------------

    def test_tiny_link_url_raises_without_http_call(self) -> None:
        """A /x/<tinyid> tiny link must raise, with no HTTP call made."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(ConfluenceTinyLinkNotSupportedError):
                    confluence_fetch(f"{_BASE_URL}/x/AbCdEf")
                mock_get.assert_not_called()

    # -- ACC-003: SSO-redirect detection ----------------------------------------------------------

    def test_redirect_to_different_host_raises_auth_redirect_error(self) -> None:
        """A response whose final URL host differs from the configured base must raise."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(
                text="<html>please log in</html>",
                url="https://sso.example.com/login?redirect=foo",
            )
            with mock.patch("httpx.get", return_value=mock_response):
                with self.assertRaises(ConfluenceAuthRedirectError):
                    confluence_fetch(f"{_BASE_URL}/spaces/FOO/pages/123/Title")

    def test_redirect_to_same_host_different_case_is_accepted(self) -> None:
        """A response whose final URL host differs only in case from the base must be accepted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(
                text="page content",
                url="https://EXAMPLE.ATLASSIAN.NET/wiki/rest/api/content/123",
            )
            with mock.patch("httpx.get", return_value=mock_response):
                result = confluence_fetch(f"{_BASE_URL}/spaces/FOO/pages/123/Title")

                self.assertEqual(result, "page content")

    # -- ACC-004: binary/image download -----------------------------------------------------------

    def test_binary_response_with_destination_path_writes_file_and_returns_path(self) -> None:
        """A non-text response with a destination_path must be written to disk and its path returned."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                destination_path = str(Path(tmp_dir) / "nested" / "image.png")
                png_bytes = b"\x89PNG\r\n\x1a\n"
                mock_response = _make_response(content=png_bytes, content_type="image/png")
                with mock.patch("httpx.get", return_value=mock_response):
                    result = confluence_fetch(
                        f"{_BASE_URL}/rest/api/content/123/child/attachment/456/data",
                        destination_path=destination_path,
                    )

                    self.assertEqual(result, destination_path)
                    self.assertEqual(Path(destination_path).read_bytes(), png_bytes)

    def test_binary_response_without_destination_path_raises_with_no_file_written(self) -> None:
        """A non-text response without a destination_path must raise, writing nothing."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(content=b"\x89PNG", content_type="image/png")
            with mock.patch("httpx.get", return_value=mock_response):
                with self.assertRaises(ConfluenceDestinationPathRequiredError):
                    confluence_fetch(f"{_BASE_URL}/rest/api/content/123/child/attachment/456/data")

    def test_text_response_ignores_destination_path(self) -> None:
        """A text response must be returned as text even when destination_path is given."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                destination_path = str(Path(tmp_dir) / "unused.txt")
                mock_response = _make_response(text="plain text body", content_type="text/plain")
                with mock.patch("httpx.get", return_value=mock_response):
                    result = confluence_fetch(f"{_BASE_URL}/rest/api/content/123", destination_path=destination_path)

                    self.assertEqual(result, "plain text body")
                    self.assertFalse(Path(destination_path).exists())

    def test_json_with_charset_parameter_is_treated_as_text(self) -> None:
        """A Content-Type with a charset parameter must still be classified as text."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text='{"a": 1}', content_type="application/json; charset=utf-8")
            with mock.patch("httpx.get", return_value=mock_response):
                result = confluence_fetch(f"{_BASE_URL}/rest/api/content/123")

                self.assertEqual(result, '{"a": 1}')

    def test_vendor_json_content_type_is_treated_as_text(self) -> None:
        """A vendor-specific +json Content-Type must be classified as text."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = _make_response(text='{"a": 1}', content_type="application/vnd.api+json")
            with mock.patch("httpx.get", return_value=mock_response):
                result = confluence_fetch(f"{_BASE_URL}/rest/api/content/123")

                self.assertEqual(result, '{"a": 1}')


if __name__ == "__main__":
    unittest.main()
