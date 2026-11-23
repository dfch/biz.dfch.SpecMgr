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

"""feat-253-md-line-offset: regression suite for the `models/md` line-offset hand-off (GitHub issue #253).

Synthetic engine tests for the 1-based line references that the shared
`models/md` engine reports in its actionable error messages and stores as
every parsed child's `_line` (feat-27-validation REQ-002). Both hand-off
mechanisms the plan names are covered:

- the scalar-field hand-off of `MarkdownStr.from_text` (ACC-001, ACC-002,
  ACC-003's engine part, and the REQ-003 empty-remainder rule), and
- the own-block hand-off of `MarkdownSection.from_text`,
  `MarkdownParagraph.from_text`, and `MarkdownListItem.from_text` (ACC-008).

Every expected line is computed from the mdformat-normalized text that is
handed to the outermost `from_text` call (`format_text`), never hard-coded,
so a test states only which line it means, not where that line is.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md import (
    AliasType,
    MarkdownBlockQuote,
    MarkdownListItemWithNotes,
    MarkdownParagraph,
    MarkdownSection2,
    MarkdownSection3,
    alias,
)
from biz.dfch.specmgr.models.md._markdown import format_text


def _line_of(body: str, line_text: str) -> int:
    """Return the 1-based line number of the one line of `body` that equals `line_text`.

    Args:
        body: The mdformat-normalized text handed to the outermost `from_text` call.
        line_text: The exact text of the line to find.

    Returns:
        The 1-based line number of that line.

    Raises:
        AssertionError: `line_text` does not occur exactly once in `body`.
    """
    matches = [index for index, line in enumerate(body.splitlines(), start=1) if line == line_text]
    assert len(matches) == 1, f"{line_text!r} occurs {len(matches)} time(s) in the body, expected once."
    result = matches[0]
    return result


def _line_after_last(body: str) -> int:
    """Return the 1-based line directly after the last line of `body` (REQ-003 empty-remainder rule).

    Args:
        body: The mdformat-normalized text handed to the outermost `from_text` call.

    Returns:
        The number of lines of `body` plus one.
    """
    result = len(body.splitlines()) + 1
    return result


# ---------------------------------------------------------------------------
# Synthetic models
# ---------------------------------------------------------------------------


@alias(value="X", type=AliasType.LITERAL)
class _TwoScalars(MarkdownSection2):
    """`## X` with two consumed scalar paragraph fields and nothing else."""

    first: MarkdownParagraph
    second: MarkdownParagraph


@alias(value="X", type=AliasType.LITERAL)
class _ThreeScalars(MarkdownSection2):
    """`## X` with two scalar paragraph fields and a mandatory third block-quote field."""

    first: MarkdownParagraph
    second: MarkdownParagraph
    third: MarkdownBlockQuote


@alias(value="Y", type=AliasType.LITERAL)
class _Inner(MarkdownSection3):
    """`### Y` with one paragraph field."""

    body: MarkdownParagraph


@alias(value="X", type=AliasType.LITERAL)
class _Outer(MarkdownSection2):
    """`## X` with a paragraph field followed by a nested `### Y` section (the plan's Overview shape)."""

    lead: MarkdownParagraph
    inner: _Inner


class _LeadWithQuote(MarkdownParagraph):
    """A paragraph with a nested block-quote field (the composite `MarkdownParagraph` path)."""

    quote: MarkdownBlockQuote


# ---------------------------------------------------------------------------
# Scalar-field hand-off (ACC-001, ACC-002, ACC-003 engine part, REQ-003)
# ---------------------------------------------------------------------------


class TestScalarFieldHandOffLineReferences(unittest.TestCase):
    """The line references after two consumed scalar fields of a multi-field section."""

    def test_text_left_over_reports_the_line_of_the_unconsumed_block(self) -> None:
        text = format_text("## X\n\nFirst.\n\nSecond.\n\n> Left over.\n")
        expected = f"starting at line {_line_of(text, '> Left over.')} of the normalized body"

        with self.assertRaises(AssertionError) as ctx:
            _TwoScalars.from_text(text)

        message = str(ctx.exception)
        self.assertTrue(message.startswith("_TwoScalars: text left over after processing all fields"), message)
        self.assertIn(expected, message)

    def test_found_no_match_reports_the_line_where_the_remainder_starts(self) -> None:
        text = format_text("## X\n\nFirst.\n\nSecond.\n\nThird.\n")
        expected = f"remaining text starts at line {_line_of(text, 'Third.')} of the normalized body"

        with self.assertRaises(AssertionError) as ctx:
            _ThreeScalars.from_text(text)

        message = str(ctx.exception)
        self.assertTrue(message.startswith("_ThreeScalars > third: expected MarkdownBlockQuote, found no match"))
        self.assertIn(expected, message)

    def test_found_no_match_with_an_empty_remainder_reports_the_line_after_the_last_line(self) -> None:
        text = format_text("## X\n\nFirst.\n\nSecond.\n")
        expected = f"remaining text starts at line {_line_after_last(text)} of the normalized body (0 line(s))"

        with self.assertRaises(AssertionError) as ctx:
            _ThreeScalars.from_text(text)

        message = str(ctx.exception)
        self.assertTrue(message.startswith("_ThreeScalars > third: expected MarkdownBlockQuote, found no match"))
        self.assertIn(expected, message)

    def test_child_line_after_two_scalar_fields_is_its_normalized_body_line(self) -> None:
        text = format_text("## X\n\nFirst.\n\nSecond.\n\n> Third.\n")
        expected = (_line_of(text, "First."), _line_of(text, "Second."), _line_of(text, "> Third."))

        sut = _ThreeScalars.from_text(text)

        result = (sut.first._line, sut.second._line, sut.third._line)
        self.assertEqual(result, expected)


# ---------------------------------------------------------------------------
# Own-block hand-off (ACC-008)
# ---------------------------------------------------------------------------


class TestOwnBlockHandOffLineReferences(unittest.TestCase):
    """The `_line` of a child that follows its parent's own heading, paragraph, or item paragraph."""

    def test_section_child_after_the_heading_is_on_its_normalized_body_line(self) -> None:
        text = format_text("### Y\n\nBody.\n")
        expected = _line_of(text, "Body.")

        sut = _Inner.from_text(text)

        self.assertEqual(sut.body._line, expected)

    def test_nested_section_children_are_on_their_normalized_body_lines(self) -> None:
        text = format_text("## X\n\nA.\n\n### Y\n\nB.\n")
        expected = (_line_of(text, "A."), _line_of(text, "### Y"), _line_of(text, "B."))

        sut = _Outer.from_text(text)

        result = (sut.lead._line, sut.inner._line, sut.inner.body._line)
        self.assertEqual(result, expected)

    def test_list_item_note_after_a_blank_line_is_on_its_normalized_body_line(self) -> None:
        text = format_text("- One item.\n\n  A note.\n")
        expected = _line_of(text, "  A note.")

        sut = MarkdownListItemWithNotes.from_text(text)

        self.assertIsNotNone(sut.notes)
        self.assertEqual([note._line for note in sut.notes], [expected])

    def test_paragraph_child_after_the_paragraph_is_on_its_normalized_body_line(self) -> None:
        text = format_text("Lead.\n\n> A quote.\n")
        expected = _line_of(text, "> A quote.")

        sut = _LeadWithQuote.from_text(text)

        self.assertEqual(sut.quote._line, expected)


if __name__ == "__main__":
    unittest.main()
