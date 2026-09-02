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

"""Tests for `models.md._markdown.format_markdown_document`.

This is the single shared formatting implementation behind both the
`mdformat` MCP tool (`general.tools.mdformat`) and the `mdformat` CLI command
(`commands.mdformat`) -- see their own test suites for the file-I/O and
exit-code behavior each builds on top of this pure, disk-free helper.
"""

from __future__ import annotations

import textwrap
import unittest

from biz.dfch.specmgr.models.md._markdown import format_markdown_document, format_text


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
            type: adr
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
            type: adr
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


if __name__ == "__main__":
    unittest.main()
