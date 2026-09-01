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

"""feat-27-validation Task 1.0/1.8: pin the exact exception type and message of every cataloged
`models/md` error surface, so every later message-enrichment task's diff to this file is the
reviewable record of every intentional message change (the plan's "pin-then-enrich" instruction).

Cataloged surfaces (feature README Task 1.0):

- "text left over after processing all fields", for a scalar field and for a `list[...]` field.
- "expected ..., found no match", for a scalar field and for a `list[...]` field.
- raw-HTML rejection, for an inline and a block token.
- "text is not in 'mdformat'." for non-normalized input.
- heading alias mismatch.
- frontmatter `yaml.YAMLError`, via `parse_tsk` on malformed YAML.
- `pydantic.ValidationError`, via a closed-vocabulary frontmatter value.

Every fixture below is deliberately minimal (short, non-truncated snippets) so the pinned
message is a short, stable, exact string rather than a snippet-truncated one. Exception
*types* are asserted first and must never change (REQ-006/ACC-004); message *content* is
asserted second and is exactly what a later task's diff to this file will show changing.
"""

from __future__ import annotations

import unittest
from typing import ClassVar

import mdformat
import yaml
import yaml.parser
from pydantic import ValidationError

from biz.dfch.specmgr.models.md import AliasType, MarkdownSection2, MarkdownStr, alias
from biz.dfch.specmgr.models.md._markdown import format_text, parse
from biz.dfch.specmgr.tsk.models.v1 import parse_tsk

# ---------------------------------------------------------------------------
# Minimal, self-contained fixtures (deliberately independent of
# `test_markdown_str.py`'s own fixtures, which may evolve for unrelated
# reasons -- this file's fixtures exist solely to keep the pinned messages
# below reproducible).
# ---------------------------------------------------------------------------


class _OneLineField(MarkdownStr):
    """A leaf field that always claims exactly one leading line, if any remain."""

    @classmethod
    def get_extent(cls, text: str) -> int:
        return min(1, len(text.splitlines()))


class _MarkerItemField(MarkdownStr):
    """A leaf field that claims exactly one line if it starts with a fixed marker, else none."""

    _MARKER: ClassVar[str] = "item: "

    @classmethod
    def get_extent(cls, text: str) -> int:
        lines = text.splitlines()
        if not lines or not lines[0].startswith(cls._MARKER):
            return 0
        return 1


class _ScalarLeftoverContainer(MarkdownStr):
    """A single mandatory scalar field that never consumes all of its own text."""

    only: _OneLineField


class _ListLeftoverContainer(MarkdownStr):
    """A single mandatory `list[...]` field that stops matching before the text ends."""

    items: list[_MarkerItemField]


class _ScalarMissingContainer(MarkdownStr):
    """A single mandatory scalar field with no possible match in the given text."""

    only: _MarkerItemField


class _ListMissingContainer(MarkdownStr):
    """A single mandatory `list[...]` field with zero possible matches in the given text."""

    items: list[_MarkerItemField]


@alias(value="Expected Heading", type=AliasType.LITERAL)
class _LiterallyAliasedSection(MarkdownSection2):
    """An `h2` section pinned to a fixed heading text via a `LITERAL` `@alias`."""


class TestLeftoverTextBaseline(unittest.TestCase):
    """Pins "text left over after processing all fields" (a field, and a list)."""

    def test_scalar_field_leaves_text_unconsumed(self) -> None:
        text = mdformat.text("line0\nline1")

        with self.assertRaises(AssertionError) as ctx:
            _ScalarLeftoverContainer.from_text(text)

        self.assertEqual(
            str(ctx.exception),
            "_ScalarLeftoverContainer: text left over after processing all fields, "
            "starting at line 2 of the normalized body:\nline1",
        )

    def test_list_field_leaves_a_stray_list_marker_line_unconsumed(self) -> None:
        """The known trigger (feat-7 Task 0.29/GitHub issue #27): a `+`-prefixed continuation
        line becomes a brand-new CommonMark list (mdformat renormalizes its marker to `-`),
        which the container has no further field to consume."""
        text = mdformat.text("item: one\n\n+ stray line")
        self.assertEqual(text, "item: one\n\n- stray line\n")

        with self.assertRaises(AssertionError) as ctx:
            _ListLeftoverContainer.from_text(text)

        self.assertEqual(
            str(ctx.exception),
            "_ListLeftoverContainer: text left over after processing all fields, "
            "starting at line 3 of the normalized body:\n"
            "- stray line likely cause: a line starting with '-', '*', or '+' begins a new "
            "CommonMark list, which the declared fields have nothing left to consume; if this "
            "was meant to continue the previous paragraph, remove the marker or indent the line "
            "so it belongs to the preceding block instead.",
        )


class TestFoundNoMatchBaseline(unittest.TestCase):
    """Pins "expected ..., found no match" (a field, and a list)."""

    def test_scalar_field_finds_no_match(self) -> None:
        text = mdformat.text("no marker here")

        with self.assertRaises(AssertionError) as ctx:
            _ScalarMissingContainer.from_text(text)

        self.assertEqual(
            str(ctx.exception),
            "_ScalarMissingContainer > _MarkerItemField: expected _MarkerItemField, found no "
            "match; remaining text starts at line 1 of the normalized body (1 line(s)) and "
            "begins with:\nno marker here",
        )

    def test_list_field_finds_no_match(self) -> None:
        text = mdformat.text("no marker here")

        with self.assertRaises(AssertionError) as ctx:
            _ListMissingContainer.from_text(text)

        self.assertEqual(
            str(ctx.exception),
            "_ListMissingContainer > _MarkerItemField: expected list[_MarkerItemField], found "
            "no match; remaining text starts at line 1 of the normalized body (1 line(s)) and "
            "begins with:\nno marker here",
        )


class TestRawHtmlRejectionBaseline(unittest.TestCase):
    """Pins the raw-HTML rejection message (an inline token, and a block token)."""

    def test_inline_html_tag_is_rejected(self) -> None:
        text = format_text("Some <b>bold</b> text.\n")

        with self.assertRaises(AssertionError) as ctx:
            parse(text)

        self.assertEqual(
            str(ctx.exception),
            "raw HTML is not permitted in a parsed document at line 1 (relative to this text's "
            "own numbering): html_inline '<b>'; fix: wrap it in a code span (e.g. `<b>`) or "
            "write it as an HTML comment (e.g. `<!-- <b> -->`) instead",
        )

    def test_block_html_tag_is_rejected(self) -> None:
        text = format_text("<div>raw html</div>\n")

        with self.assertRaises(AssertionError) as ctx:
            parse(text)

        self.assertEqual(
            str(ctx.exception),
            "raw HTML is not permitted in a parsed document at line 1 (relative to this text's "
            "own numbering): html_block '<div>raw html</div>'; fix: wrap it in a code span "
            "(e.g. `<div>raw html</div>`) or write it as an HTML comment "
            "(e.g. `<!-- <div>raw html</div> -->`) instead",
        )


class TestNotInMdformatBaseline(unittest.TestCase):
    """Pins "text is not in 'mdformat'." for non-normalized input."""

    def test_non_normalized_heading_spacing_is_rejected(self) -> None:
        text = "#  Title\ncontent\n"

        with self.assertRaises(AssertionError) as ctx:
            MarkdownStr.get_extent(text)

        self.assertEqual(
            str(ctx.exception),
            "text is not in 'mdformat' -- first difference at line 1 (relative to this text's "
            "own numbering): got '#  Title', mdformat produces '# Title'",
        )


class TestAliasMismatchBaseline(unittest.TestCase):
    """Pins the heading alias-mismatch message."""

    def test_wrong_heading_text_is_rejected(self) -> None:
        text = mdformat.text("## Wrong Heading\n\nSome body.\n")

        with self.assertRaises(AssertionError) as ctx:
            _LiterallyAliasedSection.from_text(text)

        self.assertEqual(
            str(ctx.exception),
            "_LiterallyAliasedSection (line 1): expected heading 'Expected Heading', got heading 'Wrong Heading'",
        )


# A minimal but complete `tsk` document body, reused by both frontmatter fixtures below --
# only the frontmatter block differs between the two tests.
_TSK_BODY = """\
# Title

- [ ] item

## Recent Updates

### Entry

Some update text.
"""


class TestFrontmatterYamlErrorBaseline(unittest.TestCase):
    """Pins `yaml.YAMLError`, raised via `parse_tsk` on malformed YAML frontmatter."""

    def test_malformed_yaml_raises_yaml_error(self) -> None:
        text = f"---\nid: tsk-1\nstatus: [unterminated\n---\n{_TSK_BODY}"

        with self.assertRaises(yaml.YAMLError) as ctx:
            parse_tsk(text)

        self.assertIsInstance(ctx.exception, yaml.parser.ParserError)
        self.assertEqual(
            str(ctx.exception),
            'while parsing a flow sequence\n  in "the frontmatter block", line 3, column 9\n'
            "did not find expected ',' or ']'\n"
            '  in "the frontmatter block", line 4, column 1',
        )


class TestFrontmatterValidationErrorBaseline(unittest.TestCase):
    """Pins `pydantic.ValidationError`, raised via `parse_tsk` on a closed-vocabulary
    frontmatter value (`status`)."""

    def test_out_of_vocabulary_status_raises_validation_error(self) -> None:
        text = "---\nid: tsk-1\nstatus: not-a-real-status\n---\n" + _TSK_BODY

        with self.assertRaises(ValidationError) as ctx:
            parse_tsk(text)

        # The exact message includes pydantic's own version-coupled documentation URL
        # (e.g. "https://errors.pydantic.dev/2.13/v/value_error") -- asserting the stable,
        # project-owned part of the message rather than the whole string keeps this pin
        # from failing on an unrelated pydantic version bump.
        self.assertIn(
            "status must be one of ['active', 'cancelled', 'done', 'draft'], got 'not-a-real-status'",
            str(ctx.exception),
        )


if __name__ == "__main__":
    unittest.main()
