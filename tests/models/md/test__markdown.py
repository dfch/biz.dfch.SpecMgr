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

"""Tests for `models.md._markdown.format_markdown_document` and `consume_leading_lines`.

`format_markdown_document` is the single shared formatting implementation
behind both the `mdformat` MCP tool (`general.tools.mdformat`) and the
`mdformat` CLI command (`commands.mdformat`) -- see their own test suites for
the file-I/O and exit-code behavior each builds on top of this pure,
disk-free helper.

`consume_leading_lines` is the shared hand-off step of the `models/md` engine
(feat-253): it slices consumed lines off a text, re-normalizes the rest, and
returns the line count that the caller's offset must advance by.
"""

from __future__ import annotations

import textwrap
import unittest

from biz.dfch.specmgr.models.md._markdown import consume_leading_lines, format_markdown_document, format_text


class TestFormatMarkdownDocument(unittest.TestCase):
    """Tests for `format_markdown_document()`."""

    def test_unformatted_body_reports_changed_and_formats(self) -> None:
        unformatted = textwrap.dedent(
            """\
            # Title

            Some   text   with    extra  spacing.
            """
        )

        changed, formatted_text = format_markdown_document(unformatted)

        self.assertTrue(changed)
        self.assertIn("Some text with extra spacing.", formatted_text)
        self.assertTrue(formatted_text.endswith("\n"))

    def test_already_formatted_reports_unchanged(self) -> None:
        formatted = "# Title\n\nSome text.\n"

        changed, formatted_text = format_markdown_document(formatted)

        self.assertFalse(changed)
        self.assertEqual(formatted_text, formatted)

    def test_frontmatter_preserved_body_reformatted(self) -> None:
        unformatted = textwrap.dedent(
            """\
            ---
            id: uc-001
            type: uc
            status: draft
            ---

            # Use Case Title

            Some   text   with    spacing.

            1) first item
            2) second item
            """
        )

        changed, formatted_text = format_markdown_document(unformatted)

        self.assertTrue(changed)
        self.assertIn("id: uc-001", formatted_text)
        self.assertIn("type: uc", formatted_text)
        self.assertIn("Some text with spacing.", formatted_text)
        self.assertIn("1. first item", formatted_text)
        self.assertIn("2. second item", formatted_text)
        self.assertTrue(formatted_text.endswith("\n"))

    def test_no_frontmatter_still_works(self) -> None:
        unformatted = textwrap.dedent(
            """\
            # Title

            Some   text   with    extra   spaces.
            """
        )

        changed, formatted_text = format_markdown_document(unformatted)

        self.assertTrue(changed)
        self.assertIn("Some text with extra spaces.", formatted_text)

    def test_trailing_newline_enforced(self) -> None:
        no_newline = "# Title\n\nText."

        changed, formatted_text = format_markdown_document(no_newline)

        self.assertTrue(changed)
        self.assertTrue(formatted_text.endswith("\n"))

    def test_idempotent(self) -> None:
        unformatted = textwrap.dedent(
            """\
            ---
            id: test
            type: req
            ---

            # Title

            Some   text   with    spacing.
            """
        )

        changed1, formatted_text = format_markdown_document(unformatted)
        self.assertTrue(changed1)

        changed2, formatted_text2 = format_markdown_document(formatted_text)
        self.assertFalse(changed2)
        self.assertEqual(formatted_text, formatted_text2)

    def test_does_not_modify_input_argument(self) -> None:
        original = "# Title\n\nSome   text.\n"
        original_copy = original

        format_markdown_document(original)

        self.assertEqual(original, original_copy)

    def test_thematic_break_dashes_rendered_as_dashes(self) -> None:
        unformatted = "Text\n\n---\n\nMore text.\n"

        formatted_text = format_text(unformatted)

        self.assertIn("\n---\n", formatted_text)
        self.assertNotIn("_" * 70, formatted_text)

    def test_thematic_break_asterisks_rendered_as_dashes(self) -> None:
        unformatted = "Text\n\n***\n\nMore text.\n"

        formatted_text = format_text(unformatted)

        self.assertIn("\n---\n", formatted_text)
        self.assertNotIn("_" * 70, formatted_text)

    def test_thematic_break_underscores_rendered_as_dashes(self) -> None:
        unformatted = "Text\n\n___\n\nMore text.\n"

        formatted_text = format_text(unformatted)

        self.assertIn("\n---\n", formatted_text)
        self.assertNotIn("_" * 70, formatted_text)

    def test_document_thematic_break_rendered_as_dashes(self) -> None:
        unformatted = textwrap.dedent(
            """\
            ---
            id: test
            type: req
            ---

            # Title

            Some text.

            ***

            More text.
            """
        )

        changed, formatted_text = format_markdown_document(unformatted)

        self.assertTrue(changed)
        self.assertIn("\n---\n", formatted_text)
        self.assertNotIn("_" * 70, formatted_text)


class TestConsumeLeadingLines(unittest.TestCase):
    """Tests for `consume_leading_lines()` (feat-253)."""

    #: An `mdformat`-normalized 3-line text: paragraph, blank separator, paragraph.
    TEXT = "A.\n\nB.\n"

    def test_text_is_normalized(self) -> None:
        self.assertEqual(self.TEXT, format_text(self.TEXT))

    def test_count_zero_returns_the_whole_text_and_consumes_nothing(self) -> None:
        rest, consumed = consume_leading_lines(self.TEXT, 0)

        self.assertEqual(rest, self.TEXT)
        self.assertEqual(consumed, 0)

    def test_removed_leading_blank_separator_line_is_counted_as_consumed(self) -> None:
        rest, consumed = consume_leading_lines(self.TEXT, 1)

        self.assertEqual(rest, "B.\n")
        # The sliced-off line `A.` plus the blank separator line that the
        # re-normalization of the rest removes.
        self.assertEqual(consumed, 2)

    def test_count_at_the_end_returns_an_empty_rest_and_consumes_every_line(self) -> None:
        rest, consumed = consume_leading_lines(self.TEXT, 3)

        self.assertEqual(rest, "")
        self.assertEqual(consumed, len(self.TEXT.splitlines()))

    def test_count_past_the_end_returns_an_empty_rest_and_consumes_every_line(self) -> None:
        # REQ-003: for an empty rest the consumed count is the line count of
        # the whole text, never `count`.
        rest, consumed = consume_leading_lines(self.TEXT, 10)

        self.assertEqual(rest, "")
        self.assertEqual(consumed, len(self.TEXT.splitlines()))

    def test_empty_text_returns_an_empty_rest_and_consumes_nothing(self) -> None:
        for count in (0, 1):
            with self.subTest(count=count):
                rest, consumed = consume_leading_lines("", count)

                self.assertEqual(rest, "")
                self.assertEqual(consumed, 0)

    def test_negative_count_is_rejected(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            consume_leading_lines(self.TEXT, -1)

        self.assertIn("must not be negative", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
