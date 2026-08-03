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

"""Tests for the specmgr://version resource."""

import unittest
from importlib.metadata import version

from biz.dfch.specmgr.models import VersionInfo
from biz.dfch.specmgr.resources.version import version_info


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


if __name__ == "__main__":
    unittest.main()
