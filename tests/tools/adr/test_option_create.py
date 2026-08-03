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

"""Tests for the ``option_create`` ``@mcp.tool()`` wrapper (plan §5, §8, §9a)."""

import unittest

from biz.dfch.specmgr.tools.adr.option_create import option_create
from biz.dfch.specmgr.tools.adr.option_list import option_list
from biz.dfch.specmgr.tools.adr.option_read import option_read

from ._helpers import TempAdrDirTestCase


class TestOptionCreate(TempAdrDirTestCase):
    """Tests for the option_create tool."""

    def test_option_create_writes_new_option_and_returns_full_title(self):
        """option_create must append the new option on disk and return its full title."""
        self.existing_adr(id_="doc-id")
        full_title = option_create("doc-id", "First option", "Some content.")
        self.assertEqual(full_title, "Option 1: First option")
        self.assertEqual(option_list("doc-id"), ["Option 1: First option"])
        self.assertEqual(option_read("doc-id", full_title), "Some content.")


if __name__ == "__main__":
    unittest.main()
