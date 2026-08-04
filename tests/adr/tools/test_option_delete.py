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

"""Tests for the ``option_delete`` ``@mcp.tool()`` wrapper (plan §5, §8, §9a)."""

import unittest

from biz.dfch.specmgr.models.adr import AdrOptionNotFoundError
from biz.dfch.specmgr.adr.tools.option_create import option_create
from biz.dfch.specmgr.adr.tools.option_delete import option_delete
from biz.dfch.specmgr.adr.tools.option_list import option_list

from ._helpers import TempAdrDirTestCase


class TestOptionDelete(TempAdrDirTestCase):
    """Tests for the option_delete tool."""

    def test_option_delete_removes_option_and_returns_remaining(self):
        """option_delete must remove the option on disk and return the remaining titles."""
        self.existing_adr(id_="doc-id")
        option_create("doc-id", "First option", "content")
        second_title = option_create("doc-id", "Second option", "content")
        remaining = option_delete("doc-id", "Option 1: First option")
        self.assertEqual(remaining, [second_title])
        self.assertEqual(option_list("doc-id"), [second_title])

    def test_option_delete_missing_raises(self):
        """option_delete must raise AdrOptionNotFoundError for an unknown full_title."""
        self.existing_adr(id_="doc-id")
        with self.assertRaises(AdrOptionNotFoundError):
            option_delete("doc-id", "Option 9: Missing")


if __name__ == "__main__":
    unittest.main()
