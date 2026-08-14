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

"""Tests for the shared, dependency-free `_paths` module."""

import unittest

from biz.dfch.specmgr._paths import DOCS_DIR, REPO_ROOT


class TestPaths(unittest.TestCase):
    """Tests for `REPO_ROOT`/`DOCS_DIR` resolution."""

    def test_repo_root_contains_pyproject_toml(self):
        """REPO_ROOT must point at the actual repository root."""
        sut = REPO_ROOT

        self.assertTrue((sut / "pyproject.toml").is_file())

    def test_docs_dir_is_repo_root_slash_docs(self):
        """DOCS_DIR must be exactly REPO_ROOT / 'docs'."""
        sut = DOCS_DIR

        self.assertEqual(sut, REPO_ROOT / "docs")


if __name__ == "__main__":
    unittest.main()
