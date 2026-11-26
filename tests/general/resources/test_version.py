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

"""Tests for the specmgr://version resource (incl. the `fastembed` field, feat-134 Phase 7)."""

import unittest
from importlib.metadata import PackageNotFoundError, version
from importlib.util import find_spec
from unittest import mock

from biz.dfch.specmgr.general.resources.version import version_info
from biz.dfch.specmgr.models import VersionInfo


class TestVersionResource(unittest.TestCase):
    """Tests for the `version_info` resource function (`specmgr://version`)."""

    def test_returns_version_info(self):
        """The resource must return a `VersionInfo` instance."""
        result = version_info()
        self.assertIsInstance(result, VersionInfo)

    def test_matches_installed_package_version(self):
        """The field must mirror the installed package's version."""
        result = version_info()
        self.assertEqual(result.specmgr, version("biz-dfch-specmgr"))

    @unittest.skipUnless(
        find_spec("fastembed") is not None,
        "the similarity extra (fastembed) is not installed in this test environment; the ACC-019 "
        "positive path needs it (it is in the repo's own `dev` extra, so CI's "
        "`uv sync --frozen --all-extras` always has it)",
    )
    def test_reports_installed_fastembed_version(self):
        """ACC-019: `fastembed` must mirror `importlib.metadata.version("fastembed")` when installed."""
        result = version_info()
        self.assertEqual(result.fastembed, version("fastembed"))

    def test_reports_none_when_fastembed_not_installed(self):
        """ACC-019: a simulated `PackageNotFoundError` -> `fastembed` is None (`specmgr` unaffected)."""

        def _fake_version(name: str) -> str:
            if name == "fastembed":
                raise PackageNotFoundError(name)
            return version(name)

        with mock.patch("biz.dfch.specmgr.general.resources.version.version", side_effect=_fake_version):
            result = version_info()

        self.assertIsNone(result.fastembed)
        self.assertEqual(result.specmgr, version("biz-dfch-specmgr"))


if __name__ == "__main__":
    unittest.main()
