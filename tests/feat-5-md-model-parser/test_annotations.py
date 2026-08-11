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

"""Confirms a simple depth-first walker over a ``markdown-it-py`` token tree.

``MarkdownIt.parse()`` returns a flat ``list[Token]``, but ``inline`` tokens
each carry their own nested formatting tokens (``text``/``strong_open``/
``em_open``/...) in ``.children``, so the real shape is a shallow tree, not a
flat sequence. ``walk_token_tree`` yields every token depth-first, descending
into ``.children`` whenever present, so callers (e.g. alias plain-text
extraction, per ``req_parser.py``'s design notes) can visit every token
without special-casing ``inline`` tokens themselves.
"""

import unittest
from collections.abc import Iterator

from markdown_it import MarkdownIt
from markdown_it.token import Token

MARKDOWN_TEXT = "## Hello **World**\n\nSome *text* here.\n"

H2_TEXT = """## _First_ level **2** heading

This is a paragraph with **strong** text.

### This is a level 3 heading

And here is some more text.

## _Second_ level **2** heading

This is a paragraph with *emph* text.

"""


def walk_token_tree(tokens: list[Token]) -> Iterator[Token]:
    """Depth-first walk over ``tokens``, descending into ``.children``.

    Args:
        tokens: The token list to walk, e.g. from ``MarkdownIt.parse()``.

    Yields:
        Each token in ``tokens``, followed immediately by the recursive
        walk of its ``.children`` (if any), before moving to the next
        sibling token.
    """
    assert isinstance(tokens, list), type(tokens)

    for token in tokens:
        yield token
        if token.children:
            yield from walk_token_tree(token.children)


_HEADING_LEVEL_BY_TAG = {f"h{level}": level for level in range(1, 7)}


def _heading_level(token: Token) -> int | None:
    """The numeric heading level of ``token`` (``h1`` -> 1, ..., ``h6`` -> 6).

    Args:
        token: The token to inspect.

    Returns:
        The heading level, or ``None`` if ``token`` is not a ``heading_open``.
    """
    if token.type != "heading_open":
        return None
    return _HEADING_LEVEL_BY_TAG.get(token.tag)


def get_section(token: Token, tokens: list[Token]) -> list[Token]:
    """Slice ``token``'s own section out of ``tokens``.

    The section starts at ``token`` itself (included) and extends up to,
    but not including, the next terminating token:

    - When ``token`` is a ``heading_open`` (e.g. ``h2``), the section ends at
      the next ``heading_open`` at the *same or a shallower* level (e.g. an
      ``h1`` or another ``h2`` both terminate an ``h2`` section, but a nested
      ``h3`` does not).
    - Otherwise, the section ends at the next token with the same
      ``(type, tag)`` as ``token``.

    Runs to the end of ``tokens`` if no terminator is found.

    Args:
        token: The section's own starting token. Matched by identity, not
            equality, since two structurally identical headings (e.g. same
            tag and, after slicing, no distinguishing ``map``) would
            otherwise collapse to the same index.
        tokens: The full flat token stream to slice from.

    Returns:
        The slice of ``tokens`` from ``token`` (inclusive) up to the next
        terminating token (exclusive).
    """
    assert isinstance(token, Token), type(token)
    assert isinstance(tokens, list), type(tokens)

    start = next(i for i, t in enumerate(tokens) if t is token)
    own_level = _heading_level(token)

    def _is_terminator(candidate: Token) -> bool:
        if own_level is not None:
            candidate_level = _heading_level(candidate)
            return candidate_level is not None and candidate_level <= own_level
        return candidate.type == token.type and candidate.tag == token.tag

    end = next((i for i in range(start + 1, len(tokens)) if _is_terminator(tokens[i])), len(tokens))

    result = tokens[start:end]
    return result


class TestWalkTokenTree(unittest.TestCase):
    def setUp(self):
        md = MarkdownIt("commonmark")
        self.tokens = md.parse(MARKDOWN_TEXT)

    def test_walk_visits_every_top_level_token(self):
        expected_types = [
            "heading_open",
            "inline",
            "heading_close",
            "paragraph_open",
            "inline",
            "paragraph_close",
        ]

        sut = list(walk_token_tree(self.tokens))

        result = [token.type for token in sut if token in self.tokens]
        self.assertEqual(result, expected_types)

    def test_walk_descends_into_inline_children(self):
        sut = list(walk_token_tree(self.tokens))

        result = [token.type for token in sut]

        self.assertIn("strong_open", result)
        self.assertIn("em_open", result)

    def test_walk_yields_children_immediately_after_their_parent(self):
        sut = list(walk_token_tree(self.tokens))

        heading_inline_index = next(
            i for i, token in enumerate(sut) if token.type == "inline" and token.content == "Hello **World**"
        )

        self.assertEqual(sut[heading_inline_index + 1].type, "text")
        self.assertEqual(sut[heading_inline_index + 2].type, "strong_open")
        self.assertEqual(sut[heading_inline_index + 3].type, "text")
        self.assertEqual(sut[heading_inline_index + 3].content, "World")
        self.assertEqual(sut[heading_inline_index + 4].type, "strong_close")

    def test_walk_empty_token_list_yields_nothing(self):
        sut = list(walk_token_tree([]))

        self.assertEqual(sut, [])


H1_TERMINATES_H2_TEXT = """## Section Two

Some content in section two.

# Back to top level

More text after the h1.
"""


class TestGetSection(unittest.TestCase):
    def setUp(self):
        md = MarkdownIt("commonmark")
        self.tokens = md.parse(H2_TEXT)
        self.h2_headings = [t for t in self.tokens if t.type == "heading_open" and t.tag == "h2"]

    def test_get_section_for_first_h2_includes_own_heading_and_nested_h3(self):
        sut = get_section(self.h2_headings[0], self.tokens)

        result_types = [t.type for t in sut]
        self.assertEqual(sut[0], self.h2_headings[0])
        self.assertIn("heading_open", result_types)
        self.assertTrue(any(t.type == "heading_open" and t.tag == "h3" for t in sut))

    def test_get_section_for_first_h2_excludes_second_h2_content(self):
        sut = get_section(self.h2_headings[0], self.tokens)

        inline_texts = [t.content for t in sut if t.type == "inline"]
        self.assertNotIn("_Second_ level **2** heading", inline_texts)
        self.assertNotIn("This is a paragraph with *emph* text.", inline_texts)

    def test_get_section_for_second_h2_runs_to_end_of_document(self):
        sut = get_section(self.h2_headings[1], self.tokens)

        self.assertEqual(sut[0], self.h2_headings[1])
        self.assertEqual(sut, self.tokens[self.tokens.index(self.h2_headings[1]) :])

    def test_get_section_does_not_collapse_structurally_identical_headings(self):
        identical_heading_a = Token("heading_open", "h2", 1)
        identical_heading_b = Token("heading_open", "h2", 1)
        tokens = [identical_heading_a, Token("inline", "", 0), identical_heading_b, Token("inline", "", 0)]

        sut = get_section(identical_heading_b, tokens)

        self.assertEqual(sut, tokens[2:])

    def test_get_section_for_h2_is_terminated_by_a_following_h1(self):
        md = MarkdownIt("commonmark")
        tokens = md.parse(H1_TERMINATES_H2_TEXT)
        h2_heading = next(t for t in tokens if t.type == "heading_open" and t.tag == "h2")

        sut = get_section(h2_heading, tokens)

        inline_texts = [t.content for t in sut if t.type == "inline"]
        self.assertNotIn("Back to top level", inline_texts)
        self.assertNotIn("More text after the h1.", inline_texts)
        self.assertFalse(any(t.type == "heading_open" and t.tag == "h1" for t in sut))


if __name__ == "__main__":
    unittest.main()
