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

from biz.dfch.specmgr.models.md.markdown_str import MarkdownStr

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
