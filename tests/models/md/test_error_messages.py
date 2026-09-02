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

"""feat-27-validation Task 1.8: unit tests for every message shape Phase 1 (Tasks 1.2-1.7) adds.

Complements `test_validation_error_baseline.py` (which pins one canonical, exact string per
cataloged surface) with tests that instead probe the *mechanics* behind those messages: field-
path composition across multiple nesting levels (REQ-001), 1-based line references relative to
the normalized body (REQ-002), and the expected/fix detail each message states (REQ-003).
"""

from __future__ import annotations

import unittest

import mdformat

from biz.dfch.specmgr.models.md import (
    AliasType,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    alias,
)
from biz.dfch.specmgr.models.md._markdown import format_text, not_in_mdformat_message, parse
from biz.dfch.specmgr.models.md.alias_match import describe_alias
from biz.dfch.specmgr.models.md.markdown_str import _child_path, _field_label


# ---------------------------------------------------------------------------
# `_field_label`/`_child_path` (the document-relative path mechanics, REQ-001)
# ---------------------------------------------------------------------------


class _DomainNamedSection(MarkdownSection3):
    """A `MarkdownSection` subclass with its own name -- carries domain identity."""


class TestFieldLabel(unittest.TestCase):
    """Tests for `markdown_str._field_label`."""

    def test_generic_engine_type_used_directly_yields_the_field_name(self) -> None:
        """`MarkdownParagraph` used directly (not subclassed) carries no identity of its
        own -- the same generic type is reused verbatim across many unrelated fields -- so
        the field's own attribute name is what actually identifies it."""
        result = _field_label("content", MarkdownParagraph)
        self.assertEqual(result, "content")

    def test_domain_named_type_yields_its_own_class_name(self) -> None:
        """A subclass with its own name (e.g. a heading-bearing section) carries independent
        domain identity -- exactly what a reader sees in the document -- so it is preferred
        over the field's own (often near-identical, just differently cased) attribute name."""
        result = _field_label("some_field", _DomainNamedSection)
        self.assertEqual(result, "_DomainNamedSection")


class TestChildPath(unittest.TestCase):
    """Tests for `markdown_str._child_path`."""

    def test_empty_path_returns_the_label_alone(self) -> None:
        result = _child_path("", "Task")
        self.assertEqual(result, "Task")

    def test_non_empty_path_appends_the_label(self) -> None:
        result = _child_path("Task > RecentUpdates", "UpdateEntry")
        self.assertEqual(result, "Task > RecentUpdates > UpdateEntry")


# ---------------------------------------------------------------------------
# `describe_alias` (the expected heading text/pattern, REQ-003)
# ---------------------------------------------------------------------------


class NoAliasSection(MarkdownSection3):
    """No `@alias` at all -- defaults to the implicit `SPACE_SEPARATED` derivation.

    Deliberately not leading-underscore-prefixed (see
    `alias_match.space_separated_name`'s own docstring note): a leading underscore would
    derive to the slightly odd `"_ No Alias Section"`, irrelevant noise for what this
    fixture demonstrates.
    """


@alias(type=AliasType.SPACE_SEPARATED)
class ExplicitSpaceSeparatedSection(MarkdownSection3): ...


@alias(value="Exact Title", type=AliasType.LITERAL)
class _LiteralSection(MarkdownSection3): ...


@alias(value=r"^Option \d+: .+$", type=AliasType.REGEX)
class _RegexSection(MarkdownSection3): ...


class TestDescribeAlias(unittest.TestCase):
    """Tests for `alias_match.describe_alias`."""

    def test_no_alias_describes_the_space_separated_class_name(self) -> None:
        result = describe_alias(NoAliasSection)
        self.assertEqual(result, "heading 'No Alias Section'")

    def test_explicit_space_separated_describes_the_same_way_as_no_alias(self) -> None:
        result = describe_alias(ExplicitSpaceSeparatedSection)
        self.assertEqual(result, "heading 'Explicit Space Separated Section'")

    def test_literal_describes_the_declared_value_verbatim(self) -> None:
        result = describe_alias(_LiteralSection)
        self.assertEqual(result, "heading 'Exact Title'")

    def test_regex_describes_the_pattern_not_a_literal_heading(self) -> None:
        result = describe_alias(_RegexSection)
        self.assertEqual(result, "heading matching regex '^Option \\\\d+: .+$'")


# ---------------------------------------------------------------------------
# End-to-end field-path composition (REQ-001's own worked example) and line
# references across multiple nesting levels (REQ-002).
# ---------------------------------------------------------------------------


@alias(value=".+", type=AliasType.REGEX)
class UpdateEntry(MarkdownSection3):
    """`### {free-form title}` -- mirrors `tsk.UpdateEntry`'s shape exactly."""

    content: MarkdownParagraph


class RecentUpdates(MarkdownSection2):
    """`## Recent Updates` -- mirrors `tsk.RecentUpdates`'s shape exactly."""

    updates: list[UpdateEntry]


@alias(value=".+", type=AliasType.REGEX)
class Task(MarkdownSection1):
    """`# {title}` -- mirrors `tsk.Task`'s shape (minus the checklist/comment) exactly."""

    recent_updates: RecentUpdates


class TestNestedFieldPathComposition(unittest.TestCase):
    """Reproduces REQ-001's own worked example (`Task > RecentUpdates > UpdateEntry > content`)
    end to end, using a local fixture tree shaped exactly like `tsk`'s real one (so this test
    stays independent of the `tsk` domain package's own evolution)."""

    def test_missing_leaf_paragraph_reports_the_full_path_chain(self) -> None:
        text = mdformat.text("# Task Title\n\n## Recent Updates\n\n### My Update\n")

        with self.assertRaises(AssertionError) as ctx:
            Task.from_text(text)

        message = str(ctx.exception)
        self.assertTrue(message.startswith("Task > RecentUpdates > UpdateEntry > content: "))
        self.assertIn("expected MarkdownParagraph, found no match", message)

    def test_missing_leaf_paragraph_line_reference_points_at_the_entry_heading(self) -> None:
        """The `### My Update` heading itself is line 4 of the normalized body; the missing
        `content` paragraph is reported as starting right after it, also line 4 (there is no
        body line of its own to point to)."""
        text = mdformat.text("# Task Title\n\n## Recent Updates\n\n### My Update\n")

        with self.assertRaises(AssertionError) as ctx:
            Task.from_text(text)

        self.assertIn("remaining text starts at line 4 of the normalized body", str(ctx.exception))

    def test_a_second_entry_reports_a_deeper_line_reference(self) -> None:
        """A second `### ` entry, several lines further down, reports a correspondingly
        higher line number -- the running offset accumulates correctly across a mandatory
        `list[...]` field's own already-matched items (REQ-002)."""
        text = mdformat.text(
            "# Task Title\n\n## Recent Updates\n\n### First Update\n\nFirst update text.\n\n### Second Update\n"
        )

        with self.assertRaises(AssertionError) as ctx:
            Task.from_text(text)

        message = str(ctx.exception)
        self.assertTrue(message.startswith("Task > RecentUpdates > UpdateEntry > content: "))
        self.assertIn("remaining text starts at line 8 of the normalized body", message)


# ---------------------------------------------------------------------------
# Raw-HTML rejection: the fix hint names both documented remedies (REQ-003),
# and is present for both a block and a nested inline token missing its own
# `.map` (the fallback-to-ancestor-map mechanics).
# ---------------------------------------------------------------------------


class TestRawHtmlFixHint(unittest.TestCase):
    """Tests for the raw-HTML rejection message's fix hint and line reference."""

    def test_fix_hint_names_both_documented_remedies(self) -> None:
        text = format_text("<div>raw</div>\n")

        with self.assertRaises(AssertionError) as ctx:
            parse(text)

        message = str(ctx.exception)
        self.assertIn("wrap it in a code span", message)
        self.assertIn("write it as an HTML comment", message)

    def test_html_comment_is_never_rejected_regardless_of_position(self) -> None:
        """An HTML comment (`<!-- ... -->`), block or inline, is the documented escape hatch
        itself -- it must never trigger the rejection this message describes."""
        text = format_text("A line with an inline comment <!-- note --> in it.\n")

        tokens = parse(text)  # must not raise

        self.assertTrue(tokens)

    def test_inline_tag_without_its_own_map_still_gets_a_line_reference(self) -> None:
        """An `html_inline` token nested inside an `inline` token's `.children` never carries
        a `.map` of its own -- the message must still carry a line reference, falling back to
        the enclosing (block-level) `inline` token's own `.map`."""
        text = format_text("Line one.\n\nSome <b>bold</b> text on line three.\n")

        with self.assertRaises(AssertionError) as ctx:
            parse(text)

        self.assertIn("at line 3", str(ctx.exception))


# ---------------------------------------------------------------------------
# "text is not in 'mdformat'." -- both the line-content-differs case and the
# trailing-newline-only edge case (Task 1.5).
# ---------------------------------------------------------------------------


class TestNotInMdformatMessage(unittest.TestCase):
    """Tests for `_markdown.not_in_mdformat_message`."""

    def test_reports_the_first_differing_line_content(self) -> None:
        message = not_in_mdformat_message("Title\n===\n\ncontent\n")

        self.assertIn("first difference at line", message)

    def test_trailing_newline_only_difference_gets_a_dedicated_message(self) -> None:
        """`splitlines()` never turns a missing/extra trailing newline into an extra empty
        line, so a text differing from `format_text(text)` only in that respect would
        otherwise report a nonsensical "line 0" -- this case gets its own, honest wording
        instead."""
        message = not_in_mdformat_message("# Title\n\ncontent")

        self.assertIn("every line matches", message)
        self.assertNotIn("line 0", message)


if __name__ == "__main__":
    unittest.main()
