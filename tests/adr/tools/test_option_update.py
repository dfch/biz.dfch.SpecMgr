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

"""Tests for the ``option_update`` ``@mcp.tool()`` wrapper (plan §5, §8, §9a)."""

import unittest

from biz.dfch.specmgr.models.adr import AdrOptionNotFoundError
from biz.dfch.specmgr.adr.tools.option_create import option_create
from biz.dfch.specmgr.adr.tools.option_read import option_read
from biz.dfch.specmgr.adr.tools.option_update import option_update

from ._helpers import TempAdrDirTestCase


class TestOptionUpdate(TempAdrDirTestCase):
    """Tests for the option_update tool."""

    def test_option_update_replaces_content_on_disk(self):
        """option_update must replace the option's content on disk and return the new value."""
        self.existing_adr(id_="doc-id")
        full_title = option_create("doc-id", "First option", "Old content.")
        new_content = option_update("doc-id", full_title, "New content.")
        self.assertEqual(new_content, "New content.")
        self.assertEqual(option_read("doc-id", full_title), "New content.")

    def test_option_update_missing_raises(self):
        """option_update must raise AdrOptionNotFoundError for an unknown full_title."""
        self.existing_adr(id_="doc-id")
        with self.assertRaises(AdrOptionNotFoundError):
            option_update("doc-id", "Option 9: Missing", "value")


if __name__ == "__main__":
    unittest.main()
