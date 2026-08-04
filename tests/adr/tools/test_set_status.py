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

"""Tests for the ``set_status`` ``@mcp.tool()`` wrapper (plan §8, §9a)."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.adr.tools.get_adr import get_adr
from biz.dfch.specmgr.adr.tools.set_status import set_status

from ._helpers import TempAdrDirTestCase


class TestSetStatus(TempAdrDirTestCase):
    """Tests for the set_status tool."""

    def test_sets_plain_status_on_disk(self):
        """set_status must write the new status back to disk."""
        self.existing_adr(id_="doc-id")
        set_status("doc-id", "accepted")
        self.assertEqual(get_adr("doc-id").frontmatter.status, "accepted")

    def test_composes_superseded_by_status(self):
        """set_status with superseded_by must compose the 'superseded by ...' string."""
        self.existing_adr(id_="doc-id")
        set_status("doc-id", "accepted", superseded_by="other-id")
        self.assertEqual(get_adr("doc-id").frontmatter.status, "superseded by other-id")

    def test_invalid_status_raises_and_does_not_write(self):
        """An invalid status must fail validation without writing."""
        self.existing_adr(id_="doc-id")
        with self.assertRaises(ValidationError):
            set_status("doc-id", "not-a-real-status")
        self.assertEqual(get_adr("doc-id").frontmatter.status, "draft")


if __name__ == "__main__":
    unittest.main()
