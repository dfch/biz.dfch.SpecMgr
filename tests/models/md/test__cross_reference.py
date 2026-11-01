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

"""Tests for `models.md._cross_reference` (feat-135-related-artifacts-risks, Task 100.130).

Covers `build_cross_reference_pattern` (single-tag and multi-tag pattern
construction) and `validate_cross_reference_items` (the shared
`"<TAG> <uuid>: <title>"` format check `sysrs`, `vcr`, and the new
`RequirementsBase`/`DecisionsBase`/`GoalsBase`/`RisksBase` base classes all
rely on): a valid match, a wrong type tag, a malformed uuid, a missing
title, a multi-tag pattern, and the `re.DOTALL` soft-wrap case.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md import MarkdownListItemWithNotes
from biz.dfch.specmgr.models.md._cross_reference import (
    UUID_PATTERN,
    build_cross_reference_pattern,
    validate_cross_reference_items,
)
from biz.dfch.specmgr.models.md._markdown import format_text

_VALID_UUID = "12345678-1234-1234-1234-123456789abc"


def _item(markdown: str) -> MarkdownListItemWithNotes:
    return MarkdownListItemWithNotes.from_text(format_text(markdown))  # type: ignore[return-value]


class TestBuildCrossReferencePattern(unittest.TestCase):
    """Tests for `build_cross_reference_pattern()`."""

    def test_single_tag_renders_bare_literal(self) -> None:
        pattern = build_cross_reference_pattern("REQ")
        self.assertEqual(pattern, rf"^REQ {UUID_PATTERN}: .+$")

    def test_multi_tag_renders_parenthesized_alternation(self) -> None:
        pattern = build_cross_reference_pattern("REQ", "UC")
        self.assertEqual(pattern, rf"^(REQ|UC) {UUID_PATTERN}: .+$")

    def test_no_tags_raises(self) -> None:
        with self.assertRaises(AssertionError):
            build_cross_reference_pattern()


class TestValidateCrossReferenceItems(unittest.TestCase):
    """Tests for `validate_cross_reference_items()`."""

    def test_valid_match_passes(self) -> None:
        pattern = build_cross_reference_pattern("REQ")
        items = [_item(f"- REQ {_VALID_UUID}: A title\n")]

        result = validate_cross_reference_items(items, pattern)

        self.assertEqual(result, items)

    def test_wrong_tag_raises(self) -> None:
        pattern = build_cross_reference_pattern("REQ")
        items = [_item(f"- GOL {_VALID_UUID}: A title\n")]

        with self.assertRaises(ValueError):
            validate_cross_reference_items(items, pattern)

    def test_malformed_uuid_uppercase_raises(self) -> None:
        pattern = build_cross_reference_pattern("REQ")
        items = [_item(f"- REQ {_VALID_UUID.upper()}: A title\n")]

        with self.assertRaises(ValueError):
            validate_cross_reference_items(items, pattern)

    def test_malformed_uuid_wrong_group_length_raises(self) -> None:
        pattern = build_cross_reference_pattern("REQ")
        items = [_item("- REQ 1234567-1234-1234-1234-123456789abc: A title\n")]

        with self.assertRaises(ValueError):
            validate_cross_reference_items(items, pattern)

    def test_missing_title_raises(self) -> None:
        pattern = build_cross_reference_pattern("REQ")
        items = [_item(f"- REQ {_VALID_UUID}:\n")]

        with self.assertRaises(ValueError):
            validate_cross_reference_items(items, pattern)

    def test_multi_tag_pattern_accepts_either_tag(self) -> None:
        pattern = build_cross_reference_pattern("REQ", "UC")

        validate_cross_reference_items([_item(f"- REQ {_VALID_UUID}: A title\n")], pattern)
        validate_cross_reference_items([_item(f"- UC {_VALID_UUID}: A title\n")], pattern)

    def test_multi_tag_pattern_rejects_a_third_tag(self) -> None:
        pattern = build_cross_reference_pattern("REQ", "UC")
        items = [_item(f"- DEC {_VALID_UUID}: A title\n")]

        with self.assertRaises(ValueError):
            validate_cross_reference_items(items, pattern)

    def test_dotall_soft_wrapped_item_still_matches(self) -> None:
        """A soft-wrapped (lazy-continuation) bullet's `.text` keeps an embedded newline

        (`mdformat` does not reflow); `re.DOTALL` lets `.+` still match across it.
        """
        pattern = build_cross_reference_pattern("REQ")
        items = [_item(f"- REQ {_VALID_UUID}: a soft-wrapped\n  title\n")]

        result = validate_cross_reference_items(items, pattern)

        self.assertIn("\n", items[0].text)
        self.assertEqual(result, items)


if __name__ == "__main__":
    unittest.main()
