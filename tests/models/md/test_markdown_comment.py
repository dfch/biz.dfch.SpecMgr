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

"""Unit tests for MarkdownComment.get_extent, from_text, __str__, and text."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md import MarkdownComment, MarkdownStr


class _InvalidCommentWithField(MarkdownComment):
    """A subclass declaring a nested field, used only to prove the leaf-only guard."""

    extra: MarkdownStr


class TestMarkdownCommentGetExtent(unittest.TestCase):
    """Tests for MarkdownComment.get_extent."""

    def test_no_extent_when_first_token_is_not_a_comment(self) -> None:
        """A text not starting with a comment block has no extent."""
        text = mdformat.text("Just text.\n")
        result = MarkdownComment.get_extent(text)
        self.assertEqual(result, 0)

    def test_extent_covers_the_whole_comment_block(self) -> None:
        """The extent spans the entire comment block, delimiters included."""
        text = mdformat.text("<!-- a note -->\n")
        result = MarkdownComment.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_extent_does_not_extend_past_the_comment(self) -> None:
        """Content after the comment block is not consumed."""
        text = mdformat.text("<!-- a note -->\n\nAfter.\n")
        own_span = mdformat.text("<!-- a note -->\n").splitlines()
        result = MarkdownComment.get_extent(text)
        self.assertEqual(result, len(own_span))

    def test_leaf_only_guard_rejects_a_subclass_declaring_a_field(self) -> None:
        """get_extent fails loudly if called on a subclass declaring a nested field."""
        text = mdformat.text("<!-- a note -->\n")
        with self.assertRaises(AssertionError):
            _InvalidCommentWithField.get_extent(text)


class TestMarkdownCommentFromTextAndStr(unittest.TestCase):
    """Tests for MarkdownComment.from_text, __str__ (round-trip), and text."""

    def test_round_trips_verbatim_including_delimiters(self) -> None:
        """_value and __str__ hold/return the complete extent verbatim."""
        text = mdformat.text("<!-- a note -->\n")
        instance = MarkdownComment.from_text(text)
        self.assertEqual(instance._value, text)
        self.assertEqual(str(instance), text)

    def test_rejects_text_not_starting_with_a_comment(self) -> None:
        """from_text fails loudly when text doesn't start with an html_block comment."""
        text = mdformat.text("Just text.\n")
        with self.assertRaises(AssertionError):
            MarkdownComment.from_text(text)

    def test_leaf_only_guard_rejects_a_subclass_declaring_a_field(self) -> None:
        """from_text fails loudly if called on a subclass declaring a nested field."""
        text = mdformat.text("<!-- a note -->\n")
        with self.assertRaises(AssertionError):
            _InvalidCommentWithField.from_text(text)

    def test_text_computed_field_returns_raw_content_including_delimiters(self) -> None:
        """text returns the comment's raw content, including `<!--`/`-->`."""
        text = mdformat.text("<!-- a note -->\n")
        instance = MarkdownComment.from_text(text)
        self.assertEqual(instance.text, "<!-- a note -->\n")


if __name__ == "__main__":
    unittest.main()
