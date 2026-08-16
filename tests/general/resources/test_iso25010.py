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

"""Tests for the specmgr://iso25010 resource (Task 0.8.6)."""

import unittest

from biz.dfch.specmgr.general.resources.iso25010 import iso25010
from biz.dfch.specmgr.models import Iso25010


class TestIso25010Resource(unittest.TestCase):
    """Tests for the `iso25010` resource function (`specmgr://iso25010`)."""

    def test_returns_iso25010_instance(self):
        """The resource must return an `Iso25010` instance."""
        result = iso25010()
        self.assertIsInstance(result, Iso25010)

    def test_has_nine_characteristics(self):
        """The packaged data has exactly 9 main characteristics (and 9 names)."""
        result = iso25010()
        self.assertEqual(len(result.characteristics), 9)
        self.assertEqual(len(result.names), 9)


if __name__ == "__main__":
    unittest.main()
