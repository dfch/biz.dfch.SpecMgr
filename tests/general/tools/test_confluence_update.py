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

"""Tests for the ``confluence_update`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import httpx
from markdown_it import MarkdownIt

from biz.dfch.specmgr.general.tools._confluence_config import (
    CONFLUENCE_BASE_URL_ENV_VAR,
    CONFLUENCE_BEARER_ENV_VAR,
    ConfluenceNotConfiguredError,
)
from biz.dfch.specmgr.general.tools._confluence_url import ConfluenceAuthRedirectError
from biz.dfch.specmgr.general.tools.confluence_fetch import ConfluenceTinyLinkNotSupportedError
from biz.dfch.specmgr.general.tools.confluence_update import (
    ConfluencePageIdNotResolvedError,
    ConfluenceUnexpectedResponseShapeError,
    confluence_update,
)

_BASE_URL = "https://example.atlassian.net/wiki"
_TOKEN = "s3cr3t-token"
_PAGE_ID = "123456"
_TITLE = "fetch and update"
_MARKDOWN_SOURCE = "# Heading\n\nSome *body* text.\n"


def _make_get_response(
    *,
    version_number: int = 3,
    title: str = _TITLE,
    url: str = f"{_BASE_URL}/rest/api/content/{_PAGE_ID}",
    json_payload: dict | None = None,
) -> mock.Mock:
    """Build a mocked ``httpx.Response`` for the GET version/title lookup."""
    response = mock.Mock(spec=httpx.Response)
    if json_payload is None:
        json_payload = {"version": {"number": version_number}, "title": title}
    response.json = mock.Mock(return_value=json_payload)
    response.url = httpx.URL(url)
    response.raise_for_status = mock.Mock()
    return response


def _make_put_response(*, url: str = f"{_BASE_URL}/rest/api/content/{_PAGE_ID}") -> mock.Mock:
    """Build a mocked ``httpx.Response`` for the PUT call."""
    response = mock.Mock(spec=httpx.Response)
    response.url = httpx.URL(url)
    response.raise_for_status = mock.Mock()
    return response


def _write_markdown_file(tmp_dir: str, content: str = _MARKDOWN_SOURCE) -> str:
    """Write ``content`` to a temporary Markdown file inside ``tmp_dir`` and return its path."""
    path = Path(tmp_dir) / "page.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


class TestConfluenceUpdateTool(unittest.TestCase):
    """Tests for the confluence_update tool."""

    # -- ACC-006: core write flow -----------------------------------------------------------------

    def test_put_payload_has_incremented_version_unchanged_title_and_rendered_body(self) -> None:
        """The PUT payload must have version N+1, the unchanged title, and the rendered HTML fragment."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response(version_number=5, title=_TITLE)
                put_response = _make_put_response()
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put", return_value=put_response) as mock_put:
                        result = confluence_update(_PAGE_ID, markdown_file_path)

                expected_html = MarkdownIt("commonmark").render(_MARKDOWN_SOURCE)

                mock_put.assert_called_once()
                _call_args, call_kwargs = mock_put.call_args
                payload = call_kwargs["json"]
                self.assertEqual(payload["version"]["number"], 6)
                self.assertEqual(payload["title"], _TITLE)
                self.assertEqual(payload["body"]["storage"]["value"], expected_html)
                self.assertEqual(payload["body"]["storage"]["representation"], "storage")
                self.assertEqual(payload["type"], "page")

                self.assertEqual(result, {"id": _PAGE_ID, "title": _TITLE, "version": 6})

    def test_get_and_put_urls_target_the_same_rest_content_endpoint(self) -> None:
        """Both the GET and the PUT must target {base}/rest/api/content/{id}."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                put_response = _make_put_response()
                with mock.patch("httpx.get", return_value=get_response) as mock_get:
                    with mock.patch("httpx.put", return_value=put_response) as mock_put:
                        confluence_update(_PAGE_ID, markdown_file_path)

                get_call_args, get_call_kwargs = mock_get.call_args
                self.assertEqual(get_call_args[0], f"{_BASE_URL}/rest/api/content/{_PAGE_ID}?expand=version,title")
                self.assertEqual(get_call_kwargs["headers"], {"Authorization": f"Bearer {_TOKEN}"})

                put_call_args, put_call_kwargs = mock_put.call_args
                self.assertEqual(put_call_args[0], f"{_BASE_URL}/rest/api/content/{_PAGE_ID}")
                self.assertEqual(put_call_kwargs["headers"], {"Authorization": f"Bearer {_TOKEN}"})

    # -- REQ-007: shared configuration -------------------------------------------------------------

    def test_missing_base_url_env_var_raises_not_configured(self) -> None:
        """Missing the base-URL env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {CONFLUENCE_BEARER_ENV_VAR: _TOKEN}, clear=True):
            os.environ.pop(CONFLUENCE_BASE_URL_ENV_VAR, None)
            with mock.patch("httpx.get") as mock_get, mock.patch("httpx.put") as mock_put:
                with self.assertRaises(ConfluenceNotConfiguredError):
                    confluence_update(_PAGE_ID, "unused.md")
                mock_get.assert_not_called()
                mock_put.assert_not_called()

    def test_missing_bearer_env_var_raises_not_configured(self) -> None:
        """Missing the bearer-token env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL}, clear=True):
            os.environ.pop(CONFLUENCE_BEARER_ENV_VAR, None)
            with mock.patch("httpx.get") as mock_get, mock.patch("httpx.put") as mock_put:
                with self.assertRaises(ConfluenceNotConfiguredError):
                    confluence_update(_PAGE_ID, "unused.md")
                mock_get.assert_not_called()
                mock_put.assert_not_called()

    # -- page id resolution: bare id / browsable URL / pageId query URL ---------------------------

    def test_bare_page_id_resolves_to_rest_content_url(self) -> None:
        """A bare numeric page id must resolve to {base}/rest/api/content/{id}."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                put_response = _make_put_response()
                with mock.patch("httpx.get", return_value=get_response) as mock_get:
                    with mock.patch("httpx.put", return_value=put_response) as mock_put:
                        confluence_update(_PAGE_ID, markdown_file_path)

                self.assertTrue(mock_get.call_args[0][0].startswith(f"{_BASE_URL}/rest/api/content/{_PAGE_ID}"))
                self.assertEqual(mock_put.call_args[0][0], f"{_BASE_URL}/rest/api/content/{_PAGE_ID}")

    def test_browsable_pages_url_resolves_to_same_rest_content_url(self) -> None:
        """A Cloud-style /pages/<id>/<title> URL must resolve to the same target as the bare id."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                put_response = _make_put_response()
                url = f"{_BASE_URL}/spaces/FOO/pages/{_PAGE_ID}/My+Page"
                with mock.patch("httpx.get", return_value=get_response) as mock_get:
                    with mock.patch("httpx.put", return_value=put_response) as mock_put:
                        confluence_update(url, markdown_file_path)

                self.assertTrue(mock_get.call_args[0][0].startswith(f"{_BASE_URL}/rest/api/content/{_PAGE_ID}"))
                self.assertEqual(mock_put.call_args[0][0], f"{_BASE_URL}/rest/api/content/{_PAGE_ID}")

    def test_pageid_query_url_resolves_to_same_rest_content_url(self) -> None:
        """A Server-style ?pageId=<id> URL must resolve to the same target as the bare id."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                put_response = _make_put_response()
                url = f"{_BASE_URL}/pages/viewpage.action?pageId={_PAGE_ID}"
                with mock.patch("httpx.get", return_value=get_response) as mock_get:
                    with mock.patch("httpx.put", return_value=put_response) as mock_put:
                        confluence_update(url, markdown_file_path)

                self.assertTrue(mock_get.call_args[0][0].startswith(f"{_BASE_URL}/rest/api/content/{_PAGE_ID}"))
                self.assertEqual(mock_put.call_args[0][0], f"{_BASE_URL}/rest/api/content/{_PAGE_ID}")

    # -- tiny-link rejection ------------------------------------------------------------------------

    def test_tiny_link_raises_without_http_call(self) -> None:
        """A /x/<tinyid> tiny link must raise, with no HTTP call made."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with mock.patch("httpx.get") as mock_get, mock.patch("httpx.put") as mock_put:
                with self.assertRaises(ConfluenceTinyLinkNotSupportedError):
                    confluence_update(f"{_BASE_URL}/x/AbCdEf", "unused.md")
                mock_get.assert_not_called()
                mock_put.assert_not_called()

    # -- SSO-redirect detection ----------------------------------------------------------------------

    def test_get_redirected_to_different_host_raises_and_skips_put(self) -> None:
        """A GET response redirected off the configured base URL's host must raise; no PUT is attempted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response(url="https://sso.example.com/login?redirect=foo")
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put") as mock_put:
                        with self.assertRaises(ConfluenceAuthRedirectError):
                            confluence_update(_PAGE_ID, markdown_file_path)
                        mock_put.assert_not_called()

    def test_put_redirected_to_different_host_raises(self) -> None:
        """A PUT response redirected off the configured base URL's host must raise."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                put_response = _make_put_response(url="https://sso.example.com/login?redirect=foo")
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put", return_value=put_response):
                        with self.assertRaises(ConfluenceAuthRedirectError):
                            confluence_update(_PAGE_ID, markdown_file_path)

    # -- unexpected GET response shape --------------------------------------------------------------

    def test_get_response_missing_version_raises_unexpected_response_shape(self) -> None:
        """A GET response missing the version key must raise ConfluenceUnexpectedResponseShapeError."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response(json_payload={"title": _TITLE})
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put") as mock_put:
                        with self.assertRaises(ConfluenceUnexpectedResponseShapeError):
                            confluence_update(_PAGE_ID, markdown_file_path)
                        mock_put.assert_not_called()

    def test_get_response_missing_title_raises_unexpected_response_shape(self) -> None:
        """A GET response missing the title key must raise ConfluenceUnexpectedResponseShapeError."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response(json_payload={"version": {"number": 1}})
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put") as mock_put:
                        with self.assertRaises(ConfluenceUnexpectedResponseShapeError):
                            confluence_update(_PAGE_ID, markdown_file_path)
                        mock_put.assert_not_called()

    def test_get_response_missing_version_number_raises_unexpected_response_shape(self) -> None:
        """A GET response with version but no number must raise ConfluenceUnexpectedResponseShapeError."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response(json_payload={"version": {}, "title": _TITLE})
                with mock.patch("httpx.get", return_value=get_response):
                    with self.assertRaises(ConfluenceUnexpectedResponseShapeError):
                        confluence_update(_PAGE_ID, markdown_file_path)

    # -- unresolvable page id -------------------------------------------------------------------------

    def test_unresolvable_page_url_or_id_raises_without_http_call(self) -> None:
        """A page_url_or_id that cannot be resolved to a page id must raise, with no HTTP call made."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with mock.patch("httpx.get") as mock_get, mock.patch("httpx.put") as mock_put:
                with self.assertRaises(ConfluencePageIdNotResolvedError):
                    confluence_update(f"{_BASE_URL}/wiki/spaces/FOO/overview", "unused.md")
                mock_get.assert_not_called()
                mock_put.assert_not_called()

    # -- non-2xx responses ------------------------------------------------------------------------

    def test_non_2xx_get_response_raises(self) -> None:
        """A non-2xx GET response must raise (via response.raise_for_status())."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                get_response.raise_for_status = mock.Mock(
                    side_effect=httpx.HTTPStatusError("404", request=mock.Mock(), response=get_response)
                )
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put") as mock_put:
                        with self.assertRaises(httpx.HTTPStatusError):
                            confluence_update(_PAGE_ID, markdown_file_path)
                        mock_put.assert_not_called()

    def test_non_2xx_put_response_raises(self) -> None:
        """A non-2xx PUT response must raise (via response.raise_for_status())."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                markdown_file_path = _write_markdown_file(tmp_dir)
                get_response = _make_get_response()
                put_response = _make_put_response()
                put_response.raise_for_status = mock.Mock(
                    side_effect=httpx.HTTPStatusError("500", request=mock.Mock(), response=put_response)
                )
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put", return_value=put_response):
                        with self.assertRaises(httpx.HTTPStatusError):
                            confluence_update(_PAGE_ID, markdown_file_path)

    # -- missing markdown file ------------------------------------------------------------------------

    def test_missing_markdown_file_raises_file_not_found(self) -> None:
        """A missing markdown_file_path must raise FileNotFoundError, with no PUT attempted."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                missing_path = str(Path(tmp_dir) / "does-not-exist.md")
                get_response = _make_get_response()
                with mock.patch("httpx.get", return_value=get_response):
                    with mock.patch("httpx.put") as mock_put:
                        with self.assertRaises(FileNotFoundError):
                            confluence_update(_PAGE_ID, missing_path)
                        mock_put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
