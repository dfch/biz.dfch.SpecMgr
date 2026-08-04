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

"""Tests for the ``get_adr`` ``@mcp.tool()`` wrapper (plan §8, §9a)."""

import unittest

from biz.dfch.specmgr.adr.tools._paths import AdrNotFoundError
from biz.dfch.specmgr.adr.tools.get_adr import get_adr

from ._helpers import TempAdrDirTestCase


class TestGetAdr(TempAdrDirTestCase):
    """Tests for the get_adr tool."""

    def test_returns_matching_document(self):
        """get_adr must return the parsed document matching the given id."""
        self.existing_adr(id_="my-id")
        result = get_adr("my-id")
        self.assertEqual(result.frontmatter.id, "my-id")
        self.assertEqual(result.body.title, "A title")

    def test_raises_not_found_for_unknown_id(self):
        """get_adr must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            get_adr("no-such-id")


if __name__ == "__main__":
    unittest.main()
