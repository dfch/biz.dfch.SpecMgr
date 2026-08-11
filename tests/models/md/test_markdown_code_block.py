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

"""Unit tests for MarkdownCodeBlock.get_extent, from_text, __str__, and text."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md import MarkdownCodeBlock, MarkdownStr


class _InvalidCodeBlockWithField(MarkdownCodeBlock):
    """A subclass declaring a nested field, used only to prove the leaf-only guard."""

    extra: MarkdownStr


class TestMarkdownCodeBlockGetExtent(unittest.TestCase):
    """Tests for MarkdownCodeBlock.get_extent."""

    def test_no_extent_when_first_token_is_not_a_fence(self) -> None:
        """A text not starting with a fenced code block has no extent."""
        text = mdformat.text("Just text.\n")
        result = MarkdownCodeBlock.get_extent(text)
        self.assertEqual(result, 0)

    def test_extent_covers_the_whole_fence_including_content(self) -> None:
        """The extent spans both fence marker lines and the code content."""
        text = mdformat.text("```\nprint(1)\n```\n")
        result = MarkdownCodeBlock.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_extent_covers_a_multi_line_code_block(self) -> None:
        """A fence spanning several code lines is a single block --
        its extent covers every one of those lines."""
        text = mdformat.text("```\nline one\nline two\nline three\n```\n")
        result = MarkdownCodeBlock.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_extent_does_not_extend_past_the_closing_fence(self) -> None:
        """Content after the closing fence is not consumed."""
        text = mdformat.text("```\nprint(1)\n```\n\nAfter.\n")
        own_span = mdformat.text("```\nprint(1)\n```\n").splitlines()
        result = MarkdownCodeBlock.get_extent(text)
        self.assertEqual(result, len(own_span))

    def test_extent_with_a_language_info_string(self) -> None:
        """An info string after the opening fence does not change the extent."""
        text = mdformat.text("```python\nprint(1)\n```\n")
        result = MarkdownCodeBlock.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_extent_of_an_empty_fence(self) -> None:
        """An empty fence (no code lines) still has a valid extent."""
        text = mdformat.text("```\n```\n")
        result = MarkdownCodeBlock.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_leaf_only_guard_rejects_a_subclass_declaring_a_field(self) -> None:
        """get_extent fails loudly if called on a subclass declaring a nested field."""
        text = mdformat.text("```\nprint(1)\n```\n")
        with self.assertRaises(AssertionError):
            _InvalidCodeBlockWithField.get_extent(text)


class TestMarkdownCodeBlockFromTextAndStr(unittest.TestCase):
    """Tests for MarkdownCodeBlock.from_text, __str__ (round-trip), and text."""

    def test_round_trips_verbatim_including_fence_markers(self) -> None:
        """_value and __str__ hold/return the complete extent verbatim."""
        text = mdformat.text("```\nprint(1)\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(instance._value, text)
        self.assertEqual(str(instance), text)

    def test_round_trips_with_a_language_info_string(self) -> None:
        """The info string is preserved verbatim as part of _value/__str__."""
        text = mdformat.text("```python\nprint(1)\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(str(instance), text)

    def test_round_trips_a_multi_line_code_block_preserving_whitespace(self) -> None:
        """Indentation and blank lines inside the code content round-trip exactly."""
        text = mdformat.text("```\ndef f():\n    return 1\n\ndef g():\n    return 2\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(str(instance), text)

    def test_round_trips_an_empty_fence(self) -> None:
        """An empty fence (no code lines) round-trips exactly."""
        text = mdformat.text("```\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(str(instance), text)

    def test_rejects_text_not_starting_with_a_fence(self) -> None:
        """from_text fails loudly when text doesn't start with a fence/code token."""
        text = mdformat.text("Just text.\n")
        with self.assertRaises(AssertionError):
            MarkdownCodeBlock.from_text(text)

    def test_leaf_only_guard_rejects_a_subclass_declaring_a_field(self) -> None:
        """from_text fails loudly if called on a subclass declaring a nested field."""
        text = mdformat.text("```\nprint(1)\n```\n")
        with self.assertRaises(AssertionError):
            _InvalidCodeBlockWithField.from_text(text)

    def test_text_computed_field_returns_inner_content_only(self) -> None:
        """text excludes both fence marker lines, returning only the code content."""
        text = mdformat.text("```\nprint(1)\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(instance.text, "print(1)\n")

    def test_text_computed_field_excludes_the_language_info_string(self) -> None:
        """text excludes the info string, same as it excludes the fence markers."""
        text = mdformat.text("```python\nprint(1)\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(instance.text, "print(1)\n")

    def test_text_computed_field_of_an_empty_fence_is_empty(self) -> None:
        """An empty fence's text is an empty string."""
        text = mdformat.text("```\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(instance.text, "")

    def test_text_computed_field_preserves_multiple_code_lines(self) -> None:
        """text preserves every code line, including internal blank lines."""
        text = mdformat.text("```\nline one\n\nline three\n```\n")
        instance = MarkdownCodeBlock.from_text(text)
        self.assertEqual(instance.text, "line one\n\nline three\n")


if __name__ == "__main__":
    unittest.main()
