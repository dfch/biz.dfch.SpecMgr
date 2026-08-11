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

"""Confirms that a heading's own token span can be sliced out of a flat
``markdown-it-py`` token stream.

The generic heading-mapped parser sketched in
``tests/feat-5-md-model-parser/req_parser.py`` recursively slices a
field's tokens from its own ``heading_open`` up to (not including) the next
same-or-shallower-level heading. These tests pin down that slicing on a
minimal, two-section document: one ``h2`` heading with two paragraphs,
followed by a second ``h2`` heading with one paragraph.
"""

import unittest

from markdown_it import MarkdownIt
from markdown_it.token import Token

MARKDOWN_TEXT = """\
## First Section

Paragraph one text.

Paragraph two text.

## Second Section

Other paragraph text.
"""

HEADING_TAG = "h2"


def _slice_first_heading_section(tokens: list[Token], tag: str) -> list[Token]:
    """Slice the first ``tag``-level heading's own span out of ``tokens``.

    The span starts at the first ``heading_open`` token matching ``tag`` and
    ends right before the next ``heading_open`` token matching ``tag`` (or at
    the end of ``tokens`` if there is none), i.e. it includes the heading's
    own ``heading_open``/``inline``/``heading_close`` triple plus everything
    nested beneath it.

    Args:
        tokens: The flat token stream to slice.
        tag: The heading tag to match, e.g. ``"h2"``.

    Returns:
        The sliced list of tokens belonging to the first matching heading.
    """
    assert isinstance(tokens, list), type(tokens)
    assert isinstance(tag, str) and tag, tag

    start = next(i for i, token in enumerate(tokens) if token.type == "heading_open" and token.tag == tag)
    end = next(
        (i for i in range(start + 1, len(tokens)) if tokens[i].type == "heading_open" and tokens[i].tag == tag),
        len(tokens),
    )

    result = tokens[start:end]
    return result


class TestParseHeading(unittest.TestCase):
    def setUp(self):
        md = MarkdownIt("commonmark")
        self.tokens = md.parse(MARKDOWN_TEXT)

    def test_first_h2_section_has_expected_token_types(self):
        expected_types = [
            "heading_open",
            "inline",
            "heading_close",
            "paragraph_open",
            "inline",
            "paragraph_close",
            "paragraph_open",
            "inline",
            "paragraph_close",
        ]

        sut = _slice_first_heading_section(self.tokens, HEADING_TAG)

        result = [token.type for token in sut]

        self.assertEqual(result, expected_types)

    def test_first_h2_section_contains_own_heading_and_paragraph_text(self):
        sut = _slice_first_heading_section(self.tokens, HEADING_TAG)

        self.assertEqual(sut[0].tag, HEADING_TAG)
        self.assertEqual(sut[1].content, "First Section")
        self.assertEqual(sut[4].content, "Paragraph one text.")
        self.assertEqual(sut[7].content, "Paragraph two text.")

    def test_first_h2_section_excludes_second_section_content(self):
        sut = _slice_first_heading_section(self.tokens, HEADING_TAG)

        inline_texts = [token.content for token in sut if token.type == "inline"]
        heading_opens = [token for token in sut if token.type == "heading_open"]

        self.assertNotIn("Second Section", inline_texts)
        self.assertNotIn("Other paragraph text.", inline_texts)
        self.assertEqual(len(heading_opens), 1)


if __name__ == "__main__":
    unittest.main()
