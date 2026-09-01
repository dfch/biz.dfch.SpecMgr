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

"""Tests for ``general.tools._confluence_config`` (shared env var config helper)."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from biz.dfch.specmgr.general.tools._confluence_config import (
    CONFLUENCE_BASE_URL_ENV_VAR,
    CONFLUENCE_BEARER_ENV_VAR,
    ConfluenceNotConfiguredError,
    confluence_config,
)

_BASE_URL = "https://example.atlassian.net/wiki"
_TOKEN = "s3cr3t-token"


class TestConfluenceConfig(unittest.TestCase):
    """Tests for the confluence_config() helper."""

    def test_returns_configured_base_url_and_bearer_token(self) -> None:
        """Both env vars set must return the (base_url, bearer_token) pair, read fresh."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            result = confluence_config()

            self.assertEqual(result, (_BASE_URL, _TOKEN))

    def test_reads_environment_fresh_on_every_call_no_caching(self) -> None:
        """A changed env var value must be reflected on the very next call (no caching)."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL, CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            self.assertEqual(confluence_config(), (_BASE_URL, _TOKEN))

            os.environ[CONFLUENCE_BASE_URL_ENV_VAR] = "https://other.example.com"
            self.assertEqual(confluence_config(), ("https://other.example.com", _TOKEN))

    def test_missing_base_url_env_var_raises_not_configured(self) -> None:
        """Missing the base-URL env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {CONFLUENCE_BEARER_ENV_VAR: _TOKEN}, clear=True):
            os.environ.pop(CONFLUENCE_BASE_URL_ENV_VAR, None)
            with self.assertRaises(ConfluenceNotConfiguredError):
                confluence_config()

    def test_missing_bearer_env_var_raises_not_configured(self) -> None:
        """Missing the bearer-token env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {CONFLUENCE_BASE_URL_ENV_VAR: _BASE_URL}, clear=True):
            os.environ.pop(CONFLUENCE_BEARER_ENV_VAR, None)
            with self.assertRaises(ConfluenceNotConfiguredError):
                confluence_config()

    def test_missing_both_env_vars_raises_not_configured(self) -> None:
        """Missing both env vars must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop(CONFLUENCE_BASE_URL_ENV_VAR, None)
            os.environ.pop(CONFLUENCE_BEARER_ENV_VAR, None)
            with self.assertRaises(ConfluenceNotConfiguredError):
                confluence_config()

    def test_blank_base_url_env_var_raises_not_configured(self) -> None:
        """A blank (empty-string) base-URL env var must raise ConfluenceNotConfiguredError."""
        with mock.patch.dict(
            os.environ,
            {CONFLUENCE_BASE_URL_ENV_VAR: "", CONFLUENCE_BEARER_ENV_VAR: _TOKEN},
        ):
            with self.assertRaises(ConfluenceNotConfiguredError):
                confluence_config()


if __name__ == "__main__":
    unittest.main()
