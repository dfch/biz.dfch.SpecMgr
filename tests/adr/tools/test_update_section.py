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

"""Tests for the ``update_section`` ``@mcp.tool()`` wrapper (plan §4, §8, §9a)."""

import unittest

from biz.dfch.specmgr.models.adr import AdrSectionError
from biz.dfch.specmgr.adr.tools._paths import AdrNotFoundError
from biz.dfch.specmgr.adr.tools.get_adr import get_adr
from biz.dfch.specmgr.adr.tools.update_section import update_section

from ._helpers import TempAdrDirTestCase

#: A well-formed canonical UUID (feat-38-39-41-43-44 Phase 4 added "adr" to
#: ``_path_safety``'s UUID-shaped domains, so ``get_adr`` now requires this shape).
_DOC_ID = "0d8f4c2a-1b3e-4f5a-9c7d-2e6b8a0f1c3d"

#: A well-formed but non-existent canonical UUID, for the unknown-id not-found case.
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"


class TestUpdateSection(TempAdrDirTestCase):
    """Tests for the update_section tool."""

    def test_replaces_section_on_disk(self):
        """update_section must write the new section content back to disk."""
        self.existing_adr(id_=_DOC_ID)
        update_section(_DOC_ID, "decision_drivers", "* A driver")
        on_disk = get_adr(_DOC_ID)
        self.assertEqual(on_disk.body.decision_drivers, "* A driver")

    def test_section_error_propagates_and_does_not_write(self):
        """An AdrSectionError (e.g. removing a mandatory section) must propagate untouched."""
        self.existing_adr(id_=_DOC_ID)
        with self.assertRaises(AdrSectionError):
            update_section(_DOC_ID, "title", "")
        on_disk = get_adr(_DOC_ID)
        self.assertEqual(on_disk.body.title, "A title")

    def test_raises_not_found_for_unknown_id(self):
        """update_section must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            update_section(_MISSING_UUID, "decision_drivers", "value")


if __name__ == "__main__":
    unittest.main()
