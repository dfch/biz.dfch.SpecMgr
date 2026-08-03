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

"""Tests for the ``validate_adr`` ``@mcp.tool()`` wrapper (plan §7, §8, §9a)."""

import unittest

from biz.dfch.specmgr.tools.adr._paths import AdrNotFoundError
from biz.dfch.specmgr.tools.adr.validate_adr import validate_adr

from ._helpers import TempAdrDirTestCase


class TestValidateAdr(TempAdrDirTestCase):
    """Tests for the validate_adr tool."""

    def test_returns_true_for_valid_document(self):
        """validate_adr must return True for a valid, parseable document."""
        self.existing_adr(id_="doc-id")
        self.assertIs(validate_adr("doc-id"), True)

    def test_raises_not_found_for_unknown_id(self):
        """validate_adr must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            validate_adr("no-such-id")


if __name__ == "__main__":
    unittest.main()
