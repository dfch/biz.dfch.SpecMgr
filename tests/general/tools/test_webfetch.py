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

"""Tests for the ``webfetch`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import os
import unittest
from unittest import mock

import httpx

from biz.dfch.specmgr.general.tools.webfetch import (
    WEBFETCH_BASE_URL_ENV_VAR,
    WEBFETCH_BEARER_ENV_VAR,
    WebfetchNotConfiguredError,
    WebfetchUrlNotAllowedError,
    webfetch,
)

_BASE_URL = "https://example.atlassian.net/wiki"
_TOKEN = "s3cr3t-token"


class TestWebfetchTool(unittest.TestCase):
    """Tests for the webfetch tool."""

    def test_url_outside_base_is_rejected_without_http_call(self) -> None:
        """A URL outside the configured base must raise, with no HTTP call made."""
        with mock.patch.dict(
            os.environ,
            {WEBFETCH_BASE_URL_ENV_VAR: _BASE_URL, WEBFETCH_BEARER_ENV_VAR: _TOKEN},
        ):
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(WebfetchUrlNotAllowedError):
                    webfetch("https://not-allowed.example.com/page")
                mock_get.assert_not_called()

    def test_case_insensitive_scheme_host_match_is_accepted(self) -> None:
        """A URL matching the base with different casing in scheme/host must be accepted."""
        with mock.patch.dict(
            os.environ,
            {WEBFETCH_BASE_URL_ENV_VAR: _BASE_URL, WEBFETCH_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = mock.Mock(spec=httpx.Response)
            mock_response.text = "page content"
            mock_response.raise_for_status = mock.Mock()
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                result = webfetch("HTTPS://Example.atlassian.net/wiki/page")

                self.assertEqual(result, "page content")
                mock_get.assert_called_once()

    def test_case_insensitive_configured_base_url_is_accepted(self) -> None:
        """A URL matching a differently-cased configured base URL must be accepted."""
        with mock.patch.dict(
            os.environ,
            {WEBFETCH_BASE_URL_ENV_VAR: "HTTPS://EXAMPLE.ATLASSIAN.NET/WIKI", WEBFETCH_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = mock.Mock(spec=httpx.Response)
            mock_response.text = "page content"
            mock_response.raise_for_status = mock.Mock()
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                result = webfetch("https://example.atlassian.net/wiki/page")

                self.assertEqual(result, "page content")
                mock_get.assert_called_once()

    def test_missing_base_url_env_var_raises_not_configured(self) -> None:
        """Missing the base-URL env var must raise WebfetchNotConfiguredError."""
        with mock.patch.dict(os.environ, {WEBFETCH_BEARER_ENV_VAR: _TOKEN}, clear=True):
            os.environ.pop(WEBFETCH_BASE_URL_ENV_VAR, None)
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(WebfetchNotConfiguredError):
                    webfetch(f"{_BASE_URL}/page")
                mock_get.assert_not_called()

    def test_missing_bearer_env_var_raises_not_configured(self) -> None:
        """Missing the bearer-token env var must raise WebfetchNotConfiguredError."""
        with mock.patch.dict(os.environ, {WEBFETCH_BASE_URL_ENV_VAR: _BASE_URL}, clear=True):
            os.environ.pop(WEBFETCH_BEARER_ENV_VAR, None)
            with mock.patch("httpx.get") as mock_get:
                with self.assertRaises(WebfetchNotConfiguredError):
                    webfetch(f"{_BASE_URL}/page")
                mock_get.assert_not_called()

    def test_missing_both_env_vars_raises_not_configured(self) -> None:
        """Missing both env vars must raise WebfetchNotConfiguredError."""
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop(WEBFETCH_BASE_URL_ENV_VAR, None)
            os.environ.pop(WEBFETCH_BEARER_ENV_VAR, None)
            with self.assertRaises(WebfetchNotConfiguredError):
                webfetch(f"{_BASE_URL}/page")

    def test_successful_call_sends_bearer_header_and_returns_body(self) -> None:
        """A successful call must send the Authorization header and return raw body text."""
        with mock.patch.dict(
            os.environ,
            {WEBFETCH_BASE_URL_ENV_VAR: _BASE_URL, WEBFETCH_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = mock.Mock(spec=httpx.Response)
            mock_response.text = "<html>raw body</html>"
            mock_response.raise_for_status = mock.Mock()
            with mock.patch("httpx.get", return_value=mock_response) as mock_get:
                url = f"{_BASE_URL}/spaces/FOO/pages/123"
                result = webfetch(url)

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
            {WEBFETCH_BASE_URL_ENV_VAR: _BASE_URL, WEBFETCH_BEARER_ENV_VAR: _TOKEN},
        ):
            mock_response = mock.Mock(spec=httpx.Response)
            mock_response.text = "not found"
            mock_response.raise_for_status = mock.Mock(
                side_effect=httpx.HTTPStatusError("404", request=mock.Mock(), response=mock_response)
            )
            with mock.patch("httpx.get", return_value=mock_response):
                with self.assertRaises(httpx.HTTPStatusError):
                    webfetch(f"{_BASE_URL}/missing")


if __name__ == "__main__":
    unittest.main()
