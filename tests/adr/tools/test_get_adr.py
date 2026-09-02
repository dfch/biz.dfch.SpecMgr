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


#: A well-formed but non-existent canonical UUID (feat-38-39-41-43-44 Phase 4: the id
#: must be well-formed to reach the domain's own not-found error past the new
#: ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: A well-formed canonical UUID (feat-38-39-41-43-44 Phase 4 added "adr" to
#: ``_path_safety``'s UUID-shaped domains, so this fixture id must be UUID-shaped).
_MY_ID = "0d8f4c2a-1b3e-4f5a-9c7d-2e6b8a0f1c3d"


class TestGetAdr(TempAdrDirTestCase):
    """Tests for the get_adr tool."""

    def test_returns_matching_document(self):
        """get_adr must return the parsed document matching the given id."""
        self.existing_adr(id_=_MY_ID)
        result = get_adr(_MY_ID)
        self.assertEqual(result.frontmatter.id, _MY_ID)
        self.assertEqual(result.body.title, "A title")

    def test_raises_not_found_for_unknown_id(self):
        """get_adr must raise AdrNotFoundError, with the standardized message, for an unknown id."""
        with self.assertRaises(AdrNotFoundError) as ctx:
            get_adr(_MISSING_UUID)
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)


if __name__ == "__main__":
    unittest.main()
