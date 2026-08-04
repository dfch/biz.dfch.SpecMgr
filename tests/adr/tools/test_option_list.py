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

"""Tests for the ``option_list`` ``@mcp.tool()`` wrapper (plan §5, §8, §9a)."""

import unittest

from biz.dfch.specmgr.adr.tools.option_list import option_list

from ._helpers import TempAdrDirTestCase


class TestOptionList(TempAdrDirTestCase):
    """Tests for the option_list tool."""

    def test_option_list_empty_for_fresh_document(self):
        """option_list must return an empty list for a document with no options."""
        self.existing_adr(id_="doc-id")
        self.assertEqual(option_list("doc-id"), [])


if __name__ == "__main__":
    unittest.main()
