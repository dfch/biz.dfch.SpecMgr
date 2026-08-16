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

"""Tests for `parse_iso25010`, exercised end-to-end against the real,
packaged ``general/data/general_iso25010.md`` (Task 0.8.5).
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.models import Characteristic, Iso25010, parse_iso25010


class TestParseIso25010(unittest.TestCase):
    """Tests for `parse_iso25010` against the packaged ISO/IEC 25010:2023 data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("general", "iso25010", "md")

    def test_returns_iso25010_instance(self):
        """The parser must return an `Iso25010` instance."""
        result = parse_iso25010(self.text)
        self.assertIsInstance(result, Iso25010)

    def test_has_nine_names_and_nine_characteristics(self):
        """Exactly 9 characteristic names and 9 parsed characteristics."""
        result = parse_iso25010(self.text)
        self.assertEqual(len(result.names), 9)
        self.assertEqual(len(result.characteristics), 9)

    def test_captures_leading_comment(self):
        """The leading copyright/fair-use HTML comment must be captured."""
        result = parse_iso25010(self.text)
        comment = result.comment
        assert comment is not None
        self.assertIn("Copyright ISO/IEC 2023", comment.text)

    def test_functional_suitability_characteristic(self):
        """Spot-check the first characteristic's name, description, and sub-characteristics."""
        result = parse_iso25010(self.text)
        characteristic: Characteristic = result.characteristics[0]
        self.assertEqual(characteristic.text, "Functional Suitability")
        self.assertIn("meet stated and implied needs", characteristic.description.text)
        sub_names = [sub.text for sub in characteristic.sub_characteristics]
        self.assertEqual(
            sub_names,
            ["Functional Completeness", "Functional Correctness", "Functional Appropriateness"],
        )

    def test_safety_characteristic(self):
        """Spot-check the last characteristic's name and a sub-characteristic description."""
        result = parse_iso25010(self.text)
        characteristic: Characteristic = result.characteristics[-1]
        self.assertEqual(characteristic.text, "Safety")
        sub_by_name = {sub.text: sub.description.text for sub in characteristic.sub_characteristics}
        self.assertIn("Hazard Warning", sub_by_name)
        self.assertIn("unacceptable risks", sub_by_name["Hazard Warning"])


if __name__ == "__main__":
    unittest.main()
