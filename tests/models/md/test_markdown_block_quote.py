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

"""Unit tests for MarkdownBlockQuote.get_extent, from_text, __str__, and text."""

import unittest

import mdformat

from biz.dfch.specmgr.models.md import (
    MarkdownBlockQuote,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
)


class _IntroField(MarkdownParagraph):
    """A leaf paragraph field, standing in for a quote's declared "intro" field."""


class _BodyField(MarkdownParagraph):
    """A leaf paragraph field, standing in for a quote's declared "body" field."""


class _QuoteWithTwoParagraphs(MarkdownBlockQuote):
    """A composite quote whose body is split across two declared paragraph fields."""

    intro: _IntroField
    body: _BodyField


class _InnerQuote(MarkdownBlockQuote):
    """A leaf block quote, used as a nested field's declared type."""


class _OuterQuoteWithNestedField(MarkdownBlockQuote):
    """A composite quote with one declared paragraph field and one nested quote field."""

    intro: _IntroField
    inner: _InnerQuote


class TestMarkdownBlockQuoteGetExtent(unittest.TestCase):
    """Tests for MarkdownBlockQuote.get_extent."""

    def test_no_extent_when_first_token_is_not_a_blockquote(self) -> None:
        """A text not starting with a block quote has no extent."""
        text = mdformat.text("Just a paragraph.\n")
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, 0)

    def test_leaf_extent_covers_a_single_line_quote(self) -> None:
        """A single-line quote's extent covers exactly that one line."""
        text = mdformat.text("> This is a quote.\n")
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_leaf_extent_covers_a_multi_line_quote(self) -> None:
        """A quote spanning several physical lines of one paragraph is a single block."""
        text = mdformat.text("> Line one.\n> Line two.\n")
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_leaf_extent_covers_a_loose_quote_with_multiple_paragraphs(self) -> None:
        """Internal blank '>' continuation lines don't split the quote -- every
        consecutive '>' line belongs to the same instance."""
        text = mdformat.text("> Para one.\n>\n> Para two.\n")
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_extent_does_not_extend_past_a_real_blank_line(self) -> None:
        """Content after a real (non-'>') blank line is not consumed."""
        text = mdformat.text("> Quoted.\n\nAfter quote.\n")
        own_span = mdformat.text("> Quoted.\n").splitlines()
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(own_span))

    def test_extent_treats_two_blank_line_separated_quotes_as_separate_instances(self) -> None:
        """Two quotes separated by a real blank line are two instances, not one."""
        text = mdformat.text("> Quote A.\n\n> Quote B.\n")
        own_span = mdformat.text("> Quote A.\n").splitlines()
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(own_span))

    def test_extent_includes_a_nested_deeper_quote(self) -> None:
        """A more deeply nested quote ('> > ...') is included in the outer extent."""
        text = mdformat.text("> Outer.\n>\n> > Inner.\n")
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))

    def test_extent_includes_a_heading_and_a_list_inside_the_quote(self) -> None:
        """A quote's content can be any block type, not just a paragraph."""
        text = mdformat.text("> ## Quoted Heading\n>\n> - item one\n> - item two\n")
        result = MarkdownBlockQuote.get_extent(text)
        self.assertEqual(result, len(text.splitlines()))


class TestMarkdownBlockQuoteLeafFromTextAndStr(unittest.TestCase):
    """Tests for MarkdownBlockQuote.from_text/__str__/text -- leaf (no declared fields) case."""

    def test_leaf_quote_round_trips_verbatim(self) -> None:
        """A leaf MarkdownBlockQuote stores and re-emits its complete extent verbatim."""
        text = mdformat.text("> This is a quote.\n")
        instance = MarkdownBlockQuote.from_text(text)
        self.assertEqual(instance._value, text)
        self.assertEqual(str(instance), text)

    def test_leaf_quote_preserves_inline_formatting(self) -> None:
        """Inline markdown markup inside a quote round-trips verbatim."""
        text = mdformat.text("> A quote with *emphasis* and **strong** text.\n")
        instance = MarkdownBlockQuote.from_text(text)
        self.assertEqual(str(instance), text)

    def test_leaf_loose_quote_with_multiple_paragraphs_round_trips(self) -> None:
        """A loose quote (internal blank '>' line, several paragraphs) round-trips exactly."""
        text = mdformat.text("> Para one.\n>\n> Para two.\n")
        instance = MarkdownBlockQuote.from_text(text)
        self.assertEqual(str(instance), text)

    def test_leaf_quote_rejects_text_not_starting_with_a_blockquote(self) -> None:
        """from_text fails loudly when text doesn't start with a blockquote_open token."""
        text = mdformat.text("Just a paragraph.\n")
        with self.assertRaises(AssertionError):
            MarkdownBlockQuote.from_text(text)

    def test_leaf_text_strips_the_marker_from_a_single_line_quote(self) -> None:
        """text returns the quote's content with its '>' marker stripped."""
        text = mdformat.text("> This is a quote.\n")
        instance = MarkdownBlockQuote.from_text(text)
        self.assertEqual(instance.text, "This is a quote.")

    def test_leaf_text_strips_the_marker_from_every_line_of_a_loose_quote(self) -> None:
        """text dedents every line, including the blank continuation line."""
        text = mdformat.text("> Para one.\n>\n> Para two.\n")
        instance = MarkdownBlockQuote.from_text(text)
        self.assertEqual(instance.text, "Para one.\n\nPara two.")

    def test_leaf_text_preserves_nested_markdown_syntax_as_is(self) -> None:
        """text does not render inline markup down to plain text, only strips the marker."""
        text = mdformat.text("> A quote with *emphasis*.\n")
        instance = MarkdownBlockQuote.from_text(text)
        self.assertEqual(instance.text, "A quote with *emphasis*.")


class TestMarkdownBlockQuoteCompositeFromTextAndStr(unittest.TestCase):
    """Tests for MarkdownBlockQuote.from_text/__str__/text -- composite (declared fields) case."""

    def test_composite_quote_splits_into_declared_paragraph_fields(self) -> None:
        """Every line of the extent is dedented and delegated -- there is no separate
        'own text' kept back, unlike MarkdownSection/MarkdownParagraph."""
        text = mdformat.text("> Intro sentence.\n>\n> Body content.\n")
        instance = _QuoteWithTwoParagraphs.from_text(text)
        self.assertEqual(instance._value, "")
        self.assertEqual(str(instance.intro), mdformat.text("Intro sentence.\n"))
        self.assertEqual(str(instance.body), mdformat.text("Body content.\n"))

    def test_composite_quote_round_trips_exactly(self) -> None:
        """str(instance) reproduces the exact source text, byte-exact."""
        text = mdformat.text("> Intro sentence.\n>\n> Body content.\n")
        instance = _QuoteWithTwoParagraphs.from_text(text)
        self.assertEqual(str(instance), text)

    def test_composite_quote_text_is_the_dedented_body(self) -> None:
        """text returns the same marker-free markdown that was delegated to the fields."""
        text = mdformat.text("> Intro sentence.\n>\n> Body content.\n")
        instance = _QuoteWithTwoParagraphs.from_text(text)
        self.assertEqual(instance.text, mdformat.text("Intro sentence.\n\nBody content.\n"))

    def test_composite_quote_with_a_nested_quote_field_round_trips(self) -> None:
        """A nested MarkdownBlockQuote field inside a composite quote works via one
        level of dedenting -- the inner line still starts with its own '>' marker."""
        text = mdformat.text("> Outer intro.\n>\n> > Inner quote.\n")
        instance = _OuterQuoteWithNestedField.from_text(text)
        self.assertEqual(str(instance.intro), mdformat.text("Outer intro.\n"))
        self.assertEqual(str(instance.inner), mdformat.text("> Inner quote.\n"))
        self.assertEqual(str(instance), text)

    def test_composite_quote_leaves_a_following_heading_for_a_sibling_field(self) -> None:
        """When a composite quote is one field among several in a larger document,
        its own consumption stops before the next heading."""

        class Document(MarkdownSection1):
            class Quote(_QuoteWithTwoParagraphs): ...

            class Section2(MarkdownSection2): ...

            quote: Quote
            section2: Section2

        text = mdformat.text("""# Document

> Intro sentence.
>
> Body content.

## Section 2

This is a section 2.

""")
        instance = Document.from_text(text)
        self.assertEqual(str(instance), text)
        self.assertEqual(str(instance.quote), mdformat.text("> Intro sentence.\n>\n> Body content.\n"))


if __name__ == "__main__":
    unittest.main()
