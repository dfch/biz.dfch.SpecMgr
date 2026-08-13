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

"""Unit tests for MarkdownParagraph.get_extent, from_text, and __str__."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md.alias import alias, AliasType
from biz.dfch.specmgr.models.md import (
    MarkdownStr,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
)


class _RestBlock(MarkdownStr):
    """A leaf `MarkdownStr` field standing in for "whatever follows the paragraph"."""


class _IntroParagraph(MarkdownParagraph):
    """A composite paragraph: its own intro sentence, then a delegated `rest` field."""

    rest: _RestBlock


@alias(value=".+", type=AliasType.REGEX)
class _FollowingSection(MarkdownSection3):
    """A plain h3 section used to prove a composite paragraph stops before a heading."""


class TestMarkdownParagraphGetExtent(unittest.TestCase):
    """Tests for MarkdownParagraph.get_extent."""

    def test_no_extent_when_first_token_is_not_a_paragraph(self) -> None:
        """A text not starting with a paragraph has no extent."""
        text = mdformat.text("## Not a paragraph\ncontent\n")
        result = MarkdownParagraph.get_extent(text)
        self.assertEqual(result, 0)

    def test_leaf_extent_is_just_the_paragraphs_own_span(self) -> None:
        """A leaf MarkdownParagraph's extent is exactly its own line span --
        content that follows (even another paragraph) is not consumed."""
        text = mdformat.text("Leaf paragraph text.\n\nAnother paragraph, not consumed.\n")
        result = MarkdownParagraph.get_extent(text)
        own_span = mdformat.text("Leaf paragraph text.\n").splitlines()
        self.assertEqual(result, len(own_span))

    def test_leaf_extent_covers_a_multi_line_paragraph(self) -> None:
        """A paragraph spanning several source lines is a single block --
        its own extent covers every one of those lines."""
        text = mdformat.text("Line one of the paragraph.\nLine two of the paragraph.\n")
        result = MarkdownParagraph.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_composite_extent_extends_to_end_of_input_when_no_stopping_heading(self) -> None:
        """With no heading following, a composite paragraph's extent reaches the end."""
        text = mdformat.text("Intro sentence.\n\nBody content.\nMore body content.\n")
        result = _IntroParagraph.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_composite_extent_does_not_stop_at_a_sibling_paragraph(self) -> None:
        """A paragraph can never contain a heading, so a following paragraph
        does not stop the extent -- only a heading does."""
        text = mdformat.text("Intro sentence.\n\nBody paragraph one.\n\nBody paragraph two.\n")
        result = _IntroParagraph.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_composite_extent_stops_before_any_heading_level(self) -> None:
        """A composite paragraph's extent stops before the next heading, of any
        level (h1-h6) -- a paragraph has no level of its own to compare against."""
        for level, marker in ((1, "#"), (2, "##"), (3, "###"), (4, "####"), (5, "#####"), (6, "######")):
            with self.subTest(level=level):
                text = mdformat.text(f"Intro sentence.\n\nBody content.\n\n{marker} Next\nmore\n")
                lines = text.splitlines()
                stop_line = next(i for i, line in enumerate(lines) if line.startswith(f"{marker} Next"))
                result = _IntroParagraph.get_extent(text)
                self.assertEqual(result, stop_line)


class TestMarkdownParagraphFromTextAndStr(unittest.TestCase):
    """Tests for MarkdownParagraph.from_text and __str__ (round-trip)."""

    def test_leaf_paragraph_round_trips_verbatim(self) -> None:
        """A leaf MarkdownParagraph (no declared fields) stores and re-emits
        its complete extent verbatim."""
        text = mdformat.text("Just a plain paragraph.\n")
        instance = MarkdownParagraph.from_text(text)
        self.assertEqual(instance._value, text)
        self.assertEqual(str(instance), text)

    def test_leaf_paragraph_preserves_inline_formatting(self) -> None:
        """Inline markdown markup inside a paragraph round-trips verbatim."""
        text = mdformat.text("A paragraph with *emphasis* and **strong** text.\n")
        instance = MarkdownParagraph.from_text(text)
        self.assertEqual(str(instance), text)

    def test_leaf_paragraph_rejects_text_not_starting_with_a_paragraph(self) -> None:
        """from_text fails loudly when text doesn't start with a paragraph_open/p token."""
        text = mdformat.text("## Not a paragraph\ncontent\n")
        with self.assertRaises(AssertionError):
            MarkdownParagraph.from_text(text)

    def test_composite_paragraph_splits_intro_text_and_delegates_rest_to_field(self) -> None:
        """A composite paragraph's own `_value` holds only its own inline text;
        everything after its own line span is delegated to the declared field."""
        text = mdformat.text("Intro sentence.\n\nBody content.\nMore body content.\n")
        instance = _IntroParagraph.from_text(text)
        self.assertEqual(instance._value, "Intro sentence.")
        self.assertEqual(instance.rest._value, "Body content.\nMore body content.\n")

    def test_composite_paragraph_round_trips_exactly(self) -> None:
        """str(instance) reproduces the exact source text, byte-exact."""
        text = mdformat.text("Intro sentence.\n\nBody content.\nMore body content.\n")
        instance = _IntroParagraph.from_text(text)
        self.assertEqual(str(instance), text)

    def test_composite_paragraph_leaves_a_following_heading_for_a_sibling_field(self) -> None:
        """When a composite paragraph is one field among several in a larger
        document, its own consumption stops before the next heading, leaving
        that heading (and everything after it) available for a sibling field."""
        text = mdformat.text("Intro sentence.\n\nBody content.\n\n### Following Section\n\nSection content.\n")
        remaining_lines = text.splitlines()[_IntroParagraph.get_extent(text) :]
        remaining_text = mdformat.text("\n".join(remaining_lines))
        section = _FollowingSection.from_text(remaining_text)
        self.assertEqual(str(section), mdformat.text("### Following Section\n\nSection content.\n"))

    def test_heading_with_two_paragraphs_and_section2(self) -> None:

        class Document(MarkdownSection1):
            class FirstParagraph(MarkdownParagraph): ...

            class SecondParagraph(MarkdownParagraph): ...

            class Section2(MarkdownSection2): ...

            first: FirstParagraph
            second: SecondParagraph
            section2: Section2

        text = mdformat.text("""# Document

This is the *first* paragraph. And this sentence is still part of that paragraph.

And _this_ is the *second* (but also the **last**) paragraph.

## Section 2

This is a section 2.

""")
        sut = Document.from_text(text)
        assert isinstance(sut, Document), type(Document)
        expected = str(sut)
        self.assertEqual(expected, text)

        parts = [
            expected.splitlines()[0],
            str(sut.first),
            str(sut.second),
            str(sut.section2),
        ]
        result = mdformat.text("\n".join(parts))

        self.assertEqual(result, expected)

    def test_heading_with_two_paragraphs_and_optional_paragraph_and_section2(self) -> None:

        class Document(MarkdownSection1):
            class FirstParagraph(MarkdownParagraph): ...

            class SecondParagraph(MarkdownParagraph): ...

            class OptionalParagraph(MarkdownParagraph): ...

            class Section2(MarkdownSection2): ...

            first: FirstParagraph
            second: SecondParagraph
            optional: OptionalParagraph | None = None
            section2: Section2

        text = mdformat.text("""# Document

This is the *first* paragraph. And this sentence is still part of that paragraph.

And _this_ is the *second* (but also the **last**) paragraph.

## Section 2

This is a section 2.

""")
        sut = Document.from_text(text)
        assert isinstance(sut, Document), type(Document)
        expected = str(sut)
        self.assertEqual(expected, text)

        self.assertIsNone(sut.optional, sut.optional)
        parts = [
            expected.splitlines()[0],
            str(sut.first),
            str(sut.second),
            str(sut.section2),
        ]
        result = mdformat.text("\n".join(parts))

        self.assertEqual(result, expected)

    def test_heading_with_two_paragraphs_and_existing_optional_paragraph_and_section2(self) -> None:

        class Document(MarkdownSection1):
            class FirstParagraph(MarkdownParagraph): ...

            class SecondParagraph(MarkdownParagraph): ...

            class OptionalParagraph(MarkdownParagraph): ...

            class Section2(MarkdownSection2): ...

            first: FirstParagraph
            second: SecondParagraph
            optional: OptionalParagraph | None = None
            section2: Section2

        text = mdformat.text("""# Document

This is the *first* paragraph. And this sentence is still part of that paragraph.

And _this_ is the *second* (but **not** the **last**) paragraph.

This is an optional *third* paragraph.

## Section 2

This is a section 2.

""")
        sut = Document.from_text(text)
        assert isinstance(sut, Document), type(Document)
        expected = str(sut)
        self.assertEqual(expected, text)

        self.assertIsNotNone(sut.optional)
        parts = [
            expected.splitlines()[0],
            str(sut.first),
            str(sut.second),
            str(sut.optional),
            str(sut.section2),
        ]
        result = mdformat.text("\n".join(parts))

        self.assertEqual(result, expected)


class TestMarkdownParagraphText(unittest.TestCase):
    """Tests for MarkdownParagraph.text (computed_field).

    Regression coverage for the bug where `MarkdownParagraph` was the only
    `MarkdownStr` leaf subclass without a `text` computed_field: `_value` is
    a private attribute, invisible to `model_dump()`/`model_dump_json()`
    (the serialization path an MCP server uses to transmit a tool's return
    value), so a `MarkdownParagraph`-backed field silently serialized to an
    empty object even though `str()` on it still returned its full markdown.
    """

    def test_text_is_empty_before_from_text(self) -> None:
        """`_value` is unset on a bare instance, so `.text` is the empty string."""
        instance = MarkdownParagraph()
        self.assertEqual(instance.text, "")

    def test_text_returns_a_leaf_paragraphs_full_inline_text(self) -> None:
        """A leaf paragraph's `.text` is its complete inline text, stripped."""
        text = mdformat.text("Just a plain paragraph.\n")
        instance = MarkdownParagraph.from_text(text)
        self.assertEqual(instance.text, "Just a plain paragraph.")

    def test_text_preserves_embedded_line_breaks_in_a_multi_line_paragraph(self) -> None:
        """A paragraph spanning several source lines keeps its internal line
        breaks verbatim in `.text` -- no collapsing/joining into one line."""
        text = mdformat.text("Line one of the paragraph.\nLine two of the paragraph.\n")
        instance = MarkdownParagraph.from_text(text)
        self.assertEqual(instance.text, "Line one of the paragraph.\nLine two of the paragraph.")

    def test_text_strips_inline_markup_source_but_keeps_it_verbatim(self) -> None:
        """Inline markdown markup is part of `.text` verbatim (not rendered away)."""
        text = mdformat.text("A paragraph with *emphasis* and **strong** text.\n")
        instance = MarkdownParagraph.from_text(text)
        self.assertEqual(instance.text, "A paragraph with *emphasis* and **strong** text.")

    def test_text_of_a_composite_paragraph_is_only_its_own_intro_sentence(self) -> None:
        """A composite paragraph's `.text` is its own inline text -- the
        delegated field's content is available through that field, not here."""
        text = mdformat.text("Intro sentence.\n\nBody content.\nMore body content.\n")
        instance = _IntroParagraph.from_text(text)
        self.assertEqual(instance.text, "Intro sentence.")

    def test_model_dump_exposes_text(self) -> None:
        """`model_dump()` surfaces the paragraph's content via `text` -- the
        exact regression this computed_field fixes (previously `{}`)."""
        text = mdformat.text("Content that must survive serialization.\n")
        instance = MarkdownParagraph.from_text(text)
        self.assertEqual(instance.model_dump(), {"text": "Content that must survive serialization."})


if __name__ == "__main__":
    unittest.main()
