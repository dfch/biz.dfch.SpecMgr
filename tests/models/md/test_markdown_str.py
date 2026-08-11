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

"""Unit tests for MarkdownStr class."""

import unittest
from typing import ClassVar, Optional

import mdformat

from biz.dfch.specmgr.models.md import alias, AliasType, MarkdownStr, MarkdownSection1, MarkdownSection2

from .various_models import CharacteristicInformation, RelatedInformation, MainDocument


class _FixedExtentField(MarkdownStr):
    """Test double: claims a fixed number of leading lines, regardless of content.

    Isolates `MarkdownStr.from_text`'s line-distribution/cursor logic from
    real markdown-heading semantics (covered separately by
    `MarkdownSection.get_extent`/`from_text` tests).
    """

    _FIXED_EXTENT: ClassVar[int] = 0

    @classmethod
    def get_extent(cls, text: str) -> int:
        return min(cls._FIXED_EXTENT, len(text.splitlines()))


class _TwoLineField(_FixedExtentField):
    _FIXED_EXTENT: ClassVar[int] = 2


class _OneLineField(_FixedExtentField):
    _FIXED_EXTENT: ClassVar[int] = 1


class _TwoFieldContainer(MarkdownStr):
    first: _TwoLineField
    second: _OneLineField


class _OneFieldContainer(MarkdownStr):
    only: _OneLineField


class _AlwaysAbsentField(_FixedExtentField):
    """Test double: `get_extent` always returns 0, regardless of remaining text.

    Used as an `Optional[...]` field type to exercise the "declared but never
    present" branch of `from_text`/`process_field`.
    """

    _FIXED_EXTENT: ClassVar[int] = 0


class _MiddleOptionalContainer(MarkdownStr):
    """A required field, an always-absent optional field, then another required field."""

    first: _OneLineField
    middle: Optional[_AlwaysAbsentField] = None
    second: _OneLineField


class _TrailingOptionalContainer(MarkdownStr):
    """Two required fields fully consume the text; a trailing optional field is absent."""

    first: _OneLineField
    second: _OneLineField
    trailing: Optional[_OneLineField] = None


class _PresentOptionalContainer(MarkdownStr):
    """An optional field that does find an extent in the remaining text."""

    first: _TwoLineField
    optional_second: Optional[_OneLineField] = None


class _MarkerItemField(MarkdownStr):
    """Test double: claims exactly one line if it starts with a marker, else no extent.

    Used as the item type of a `list[...]` field, so a `process_list_field`
    loop can be driven by real content (marker present/absent) instead of a
    fixed line count, isolating "keep matching while the marker is present"
    from `MarkdownSection`'s heading-specific semantics.

    Deliberately *not* real markdown list syntax (`"- "`/`"* "`): joining
    several already-`mdformat`-rendered leaf blocks with a blank line (as
    `MarkdownStr.__str__` always does) turns a *tight* markdown list back
    into a *loose* one, which would make a round-trip assertion fail for a
    reason unrelated to list-*field* support itself. A plain-text marker
    avoids that orthogonal quirk, so each item is just an ordinary paragraph.
    """

    _MARKER: ClassVar[str] = "item: "

    @classmethod
    def get_extent(cls, text: str) -> int:
        lines = text.splitlines()
        if not lines or not lines[0].startswith(cls._MARKER):
            return 0
        return 1


@alias(type=AliasType.SPACE_SEPARATED)
class SectionLevel1(MarkdownSection1):
    """SectionLevel1."""

    @alias(value="Section Level 2 .*", type=AliasType.REGEX)
    class SectionLevel2(MarkdownSection2): ...

    """SectionLevel2."""

    items: list[SectionLevel2]


class _RequiredListContainer(MarkdownStr):
    """A single mandatory `list[...]` field."""

    items: list[_MarkerItemField]


class _TrailingOptionalListContainer(MarkdownStr):
    """A required field fully consumes the text; a trailing optional list field is absent."""

    first: _OneLineField
    items: Optional[list[_MarkerItemField]] = None


class _PresentOptionalListContainer(MarkdownStr):
    """An optional `list[...]` field that does find items in the remaining text."""

    first: _OneLineField
    items: Optional[list[_MarkerItemField]] = None


class _ListThenTrailingContainer(MarkdownStr):
    """A mandatory `list[...]` field followed by another required scalar field."""

    items: list[_MarkerItemField]
    trailing: _OneLineField


class TestFromText(unittest.TestCase):
    """Tests for from_text class method."""

    def test_leaf_class_stores_value_verbatim(self) -> None:
        """A class with no nested MarkdownStr fields stores `v` in `_value` unchanged."""
        text = mdformat.text("some raw content\nline 2")
        instance = MarkdownStr.from_text(text)
        self.assertEqual(instance._value, text)

    def test_distributes_lines_across_fields_using_get_extent(self) -> None:
        """from_text slices exactly `get_extent()` lines per field, in declaration order."""
        text = mdformat.text("line0\nline1\nline2")
        instance = _TwoFieldContainer.from_text(text)
        self.assertIsInstance(instance, _TwoFieldContainer)
        self.assertEqual(instance.first._value, mdformat.text("line0\nline1"))
        self.assertEqual(instance.second._value, mdformat.text("line2"))
        self.assertEqual(instance._value, text)

    def test_raises_when_a_field_has_no_extent(self) -> None:
        """If a field's get_extent finds nothing in the remaining text, from_text fails loudly."""
        with self.assertRaises(AssertionError):
            _TwoFieldContainer.from_text(mdformat.text("only one line"))

    def test_raises_when_leftover_text_remains_after_all_fields(self) -> None:
        """from_text fails loudly if the declared fields don't consume all of the input text."""
        text = mdformat.text("line0\nline1\nline2")
        with self.assertRaises(AssertionError):
            _OneFieldContainer.from_text(text)

    def test_optional_field_with_no_extent_is_skipped_and_left_none(self) -> None:
        """An `Optional[...]` field whose `get_extent` is 0 is skipped, not an error.

        `from_text` must not consume any text for it, must leave the attribute
        `None` (pydantic default), and must continue on to the next declared
        field with the remainder untouched.
        """
        text = mdformat.text("line0\nline1")
        instance = _MiddleOptionalContainer.from_text(text)
        self.assertIsInstance(instance, _MiddleOptionalContainer)
        self.assertIsNone(instance.middle)
        self.assertEqual(instance.first._value, mdformat.text("line0"))
        self.assertEqual(instance.second._value, mdformat.text("line1"))
        self.assertEqual(instance._value, text)

    def test_optional_field_absent_when_remaining_text_is_empty(self) -> None:
        """A trailing optional field is left `None` once prior required fields consume all text."""
        text = mdformat.text("line0\nline1")
        instance = _TrailingOptionalContainer.from_text(text)
        self.assertIsInstance(instance, _TrailingOptionalContainer)
        self.assertIsNone(instance.trailing)
        self.assertEqual(instance.first._value, mdformat.text("line0"))
        self.assertEqual(instance.second._value, mdformat.text("line1"))
        self.assertEqual(instance._value, text)

    def test_optional_field_is_populated_when_extent_is_found(self) -> None:
        """An `Optional[...]` field behaves like a required one once its `get_extent` is non-zero."""
        text = mdformat.text("line0\nline1\nline2")
        instance = _PresentOptionalContainer.from_text(text)
        self.assertIsInstance(instance, _PresentOptionalContainer)
        self.assertIsNotNone(instance.optional_second)
        assert instance.optional_second is not None, type(instance.optional_second)
        self.assertEqual(instance.first._value, mdformat.text("line0\nline1"))
        self.assertEqual(instance.optional_second._value, mdformat.text("line2"))
        self.assertEqual(instance._value, text)

    def test_mandatory_list_field_collects_all_matching_items(self) -> None:
        """A `list[X]` field repeatedly matches `X` until `X.get_extent` finds no further item."""
        text = mdformat.text("item: one\n\nitem: two\n\nitem: three")
        instance = _RequiredListContainer.from_text(text)
        self.assertIsInstance(instance, _RequiredListContainer)
        self.assertEqual(len(instance.items), 3)
        for item in instance.items:
            self.assertIsInstance(item, _MarkerItemField)
        self.assertEqual(instance._value, text)
        self.assertEqual(str(instance), text)

    def test_space_separated_with_leading_number_must_not_fail(self) -> None:
        """A `list[X]` field repeatedly matches `X` until `X.get_extent` finds no further item."""
        text = mdformat.text("""# Section Level 1

## Section Level 2 ABC

## Section Level 2 DEF

""")
        instance = SectionLevel1.from_text(text)
        self.assertIsInstance(instance, SectionLevel1)
        self.assertEqual(len(instance.items), 2)
        for item in instance.items:
            self.assertIsInstance(item, SectionLevel1.SectionLevel2)
        self.assertEqual(str(instance), text)

    def test_mandatory_list_field_raises_when_no_item_matches(self) -> None:
        """A mandatory `list[X]` field with zero matched items fails loudly, like a scalar field."""
        with self.assertRaises(AssertionError):
            _RequiredListContainer.from_text(mdformat.text("plain text, no marker"))

    def test_optional_list_field_absent_when_remaining_text_is_empty(self) -> None:
        """A trailing `Optional[list[X]]` field is left `None` once prior fields consume all text."""
        text = mdformat.text("line0")
        instance = _TrailingOptionalListContainer.from_text(text)
        self.assertIsInstance(instance, _TrailingOptionalListContainer)
        self.assertIsNone(instance.items)
        self.assertEqual(instance.first._value, mdformat.text("line0"))
        self.assertEqual(instance._value, text)

    def test_optional_list_field_is_populated_when_items_are_found(self) -> None:
        """An `Optional[list[X]]` field behaves like a mandatory one once items are found."""
        text = mdformat.text("line0\n\nitem: one\n\nitem: two")
        instance = _PresentOptionalListContainer.from_text(text)
        self.assertIsInstance(instance, _PresentOptionalListContainer)
        self.assertIsNotNone(instance.items)
        assert instance.items is not None, type(instance.items)
        self.assertEqual(len(instance.items), 2)
        self.assertEqual(instance.first._value, mdformat.text("line0"))
        self.assertEqual(str(instance), text)

    def test_list_field_stops_at_first_non_matching_item_and_next_field_continues(self) -> None:
        """Only the first item of a `list[X]` field is mandatory; the list stops once `X` no longer matches,
        leaving the remainder for the next declared field."""
        text = mdformat.text("item: one\n\nitem: two\n\nplain line")
        instance = _ListThenTrailingContainer.from_text(text)
        self.assertIsInstance(instance, _ListThenTrailingContainer)
        self.assertEqual(len(instance.items), 2)
        self.assertEqual(instance.trailing._value, mdformat.text("plain line"))
        self.assertEqual(str(instance), text)

    def test_main_document_from_text(self) -> None:
        """Test creating MainDocument from a realistic, multi-heading document.

        Covers two levels of nesting (`MainDocument` h1 -> `CharacteristicInformation`/
        `RelatedInformation` h2 -> their h3 leaf children) and confirms
        `MarkdownSection._value` semantics: a *composite* section (has nested
        fields) holds only its own heading title, since its body is fully
        represented by its children; a *leaf* section (no nested fields)
        holds its complete extent verbatim (heading and body), since nothing
        else retains that text. Also confirms inline formatting markup inside
        a heading (`*Goal*`) is preserved verbatim, and that `str(doc)`
        reproduces the original input byte-for-byte.
        """
        text = mdformat.text(
            "# Main Title\n"
            "\n"
            "## Characteristic Information\n"
            "\n"
            "### *Goal* In Context\n"
            "\n"
            "Some goal text.\n"
            "\n"
            "### Scope\n"
            "\n"
            "Some scope text.\n"
            "\n"
            "## Related Information\n"
            "\n"
            "### Notes\n"
            "\n"
            "Some notes text.\n"
            "\n"
            "### Assumptions\n"
            "\n"
            "Some assumptions text.\n"
        )

        doc = MainDocument.from_text(text)
        self.assertIsInstance(doc, MainDocument)
        assert isinstance(doc, MainDocument), type(doc)
        self.assertEqual(doc._value, "Main Title")

        self.assertIsInstance(doc.characteristic_information, CharacteristicInformation)
        ci = doc.characteristic_information
        self.assertEqual(ci._value, "Characteristic Information")
        self.assertEqual(ci.goal_in_context._value, mdformat.text("### *Goal* In Context\n\nSome goal text.\n"))
        self.assertEqual(ci.scope._value, mdformat.text("### Scope\n\nSome scope text.\n"))

        self.assertIsInstance(doc.related_information, RelatedInformation)
        ri = doc.related_information
        self.assertEqual(ri._value, "Related Information")
        self.assertEqual(ri.notes._value, mdformat.text("### Notes\n\nSome notes text.\n"))
        self.assertEqual(ri.assumptions._value, mdformat.text("### Assumptions\n\nSome assumptions text.\n"))

        self.assertEqual(str(doc), text)


class TestGetExtent(unittest.TestCase):
    """Tests for get_extent class method."""

    def test_empty_string(self) -> None:
        """Test get_extent with empty input."""
        text = mdformat.text("")
        lines = text.splitlines()
        expected = len(lines)
        print("")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            print(f"[{i}] {line}")
        result = MarkdownStr.get_extent(text)
        self.assertEqual(result, expected)

    def test_single_line(self) -> None:
        """Test get_extent with a single heading on line 0 (0-based)."""
        text = mdformat.text("# Title")
        lines = text.splitlines()
        expected = len(lines)
        print("")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            print(f"[{i}] {line}")
        result = MarkdownStr.get_extent(text)
        self.assertEqual(result, expected)

    def test_multiple_lines(self) -> None:
        """Test get_extent with content spanning multiple lines."""
        text = mdformat.text("# Title\nParagraph on line 2.\n\n\n## *More* `heading`")
        lines = text.splitlines()
        expected = len(lines)
        print("")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            print(f"[{i}] {line}")
        result = MarkdownStr.get_extent(text)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
