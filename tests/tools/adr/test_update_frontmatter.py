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
from biz.dfch.specmgr.tools.adr._paths import AdrNotFoundError
from biz.dfch.specmgr.tools.adr.get_adr import get_adr
from biz.dfch.specmgr.tools.adr.update_frontmatter import update_frontmatter

from ._helpers import TempAdrDirTestCase


class TestUpdateFrontmatter(TempAdrDirTestCase):
    """Tests for the update_frontmatter tool."""

    def test_replaces_frontmatter_but_preserves_id(self):
        """update_frontmatter must apply the whole-object replace but keep the resolved id."""
        self.existing_adr(id_="keep-me")
        new_frontmatter = AdrFrontmatter(id="attacker-supplied-id", status="accepted")
        result = update_frontmatter("keep-me", new_frontmatter)

        self.assertEqual(result.frontmatter.id, "keep-me")
        self.assertEqual(result.frontmatter.status, "accepted")

        on_disk = get_adr("keep-me")
        self.assertEqual(on_disk.frontmatter.status, "accepted")
        self.assertEqual(on_disk.frontmatter.id, "keep-me")

    def test_raises_not_found_for_unknown_id(self):
        """update_frontmatter must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            update_frontmatter("no-such-id", AdrFrontmatter())


if __name__ == "__main__":
    unittest.main()
