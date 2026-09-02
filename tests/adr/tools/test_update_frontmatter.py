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

"""Tests for the ``update_frontmatter`` ``@mcp.tool()`` wrapper (plan §8, §9a)."""

import unittest

from biz.dfch.specmgr.models.adr import AdrFrontmatter
from biz.dfch.specmgr.adr.tools._paths import AdrNotFoundError
from biz.dfch.specmgr.adr.tools.get_adr import get_adr
from biz.dfch.specmgr.adr.tools.update_frontmatter import update_frontmatter

from ._helpers import TempAdrDirTestCase

#: A well-formed canonical UUID (feat-38-39-41-43-44 Phase 4 added "adr" to
#: ``_path_safety``'s UUID-shaped domains, so ``get_adr`` now requires this shape).
_KEEP_ME_ID = "0d8f4c2a-1b3e-4f5a-9c7d-2e6b8a0f1c3d"

#: A well-formed but non-existent canonical UUID, for the unknown-id not-found case.
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"


class TestUpdateFrontmatter(TempAdrDirTestCase):
    """Tests for the update_frontmatter tool."""

    def test_replaces_frontmatter_but_preserves_id(self):
        """update_frontmatter must apply the whole-object replace but keep the resolved id."""
        self.existing_adr(id_=_KEEP_ME_ID)
        new_frontmatter = AdrFrontmatter(id="attacker-supplied-id", status="accepted")
        result = update_frontmatter(_KEEP_ME_ID, new_frontmatter)

        self.assertEqual(result.frontmatter.id, _KEEP_ME_ID)
        self.assertEqual(result.frontmatter.status, "accepted")

        on_disk = get_adr(_KEEP_ME_ID)
        self.assertEqual(on_disk.frontmatter.status, "accepted")
        self.assertEqual(on_disk.frontmatter.id, _KEEP_ME_ID)

    def test_raises_not_found_for_unknown_id(self):
        """update_frontmatter must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            update_frontmatter(_MISSING_UUID, AdrFrontmatter())


if __name__ == "__main__":
    unittest.main()
