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

"""Tests for :func:`parse_txt`: the `TxtDocument`-level entry point.

Covers the ACC-003 matrix from `.specmgr/feat/feat-229-txt/README.md`
(document-level round-trip and `model_dump` surfacing the body text,
frontmatter closed-status enforcement through the full parser) plus the
document-level views of the ACC-001/ACC-002 structural and entry violations.
Note: any future `list_txt` paging-clamp behavior is a Phase 110 tool test
(`tests/txt/tools/`), not covered here.
"""

from __future__ import annotations

import textwrap
import unittest

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.txt.models.v1 import TxtDocument
from biz.dfch.specmgr.txt.models.v1.parser import parse_txt
from biz.dfch.specmgr.models.md._markdown import format_text

# The minimal valid document: frontmatter, a single H1, an opaque free-form
# body, and the mandatory `## Updates` section with exactly one entry --
# nothing else. This is the shape a freshly created `txt` document may
# legitimately have.
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: txt-001
    type: txt
    version: 1.0.0
    status: draft
    created: '2026-08-31T00:00:00.000Z'
    updated: '2026-08-31T00:00:00.000Z'
    ---

    # Ad-hoc review notes

    Some free-form prose about what was reviewed.

    ## Updates

    ### 2026-08-31 00:00:00.000Z - Created

    Initial draft of the review notes.
    """
)

# Every feature present: a free-form body with free H2/H3 headings, a bullet
# list, and a fenced `## Updates` (which must stay in the body), plus the
# mandatory `## Updates` section with its leading "newest first" anchor
# comment and two newest-first entries.
_FULL_DOC = textwrap.dedent(
    """\
    ---
    id: txt-001
    type: txt
    version: 1.0.0
    status: done
    created: '2026-08-31T00:00:00.000Z'
    updated: '2026-08-31T00:00:00.000Z'
    ---

    # Ad-hoc review notes

    ## Findings

    Some prose about what was found.

    - item one

    - item two

    ### Detail

    More prose under a free H3.

    ```
    ## Updates
    ```

    ## Updates

    <!-- Newest entry first -- prepend new entries directly below this comment. -->

    ### 2026-08-27 00:00:00.000Z : Reviewed

    The findings were reviewed.

    ### 2026-08-26 00:00:00.000Z - Created

    Initial draft of the review notes.
    """
)


class TestParseTxt(unittest.TestCase):
    """`parse_txt` on valid documents (ACC-003 round-trip and `model_dump`)."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a TxtDocument with the expected shape."""
        document = parse_txt(_MINIMAL_DOC)

        self.assertIsInstance(document, TxtDocument)
        self.assertEqual(document.frontmatter.id, "txt-001")
        self.assertEqual(document.frontmatter.type, "txt")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.created, "2026-08-31T00:00:00.000Z")
        self.assertEqual(document.body.text, "Ad-hoc review notes")
        self.assertEqual(document.body.body.text, "Some free-form prose about what was reviewed.\n")
        self.assertEqual(len(document.body.updates.updates), 1)
        self.assertEqual(document.body.updates.updates[0].title, "Created")

    def test_parses_full_document(self) -> None:
        """A document with a free-form body (free H2/H3, lists, a fenced `## Updates`) parses."""
        document = parse_txt(_FULL_DOC)

        self.assertEqual(document.frontmatter.id, "txt-001")
        self.assertEqual(document.frontmatter.status, "done")
        self.assertEqual(document.body.text, "Ad-hoc review notes")

        self.assertEqual(
            document.body.body.text,
            "## Findings\n\nSome prose about what was found.\n\n- item one\n\n- item two\n\n"
            "### Detail\n\nMore prose under a free H3.\n\n```\n## Updates\n```\n",
        )

        updates = document.body.updates
        self.assertIsNotNone(updates.comment)
        self.assertEqual(len(updates.updates), 2)
        self.assertEqual(updates.updates[0].timestamp, "2026-08-27 00:00:00.000Z")
        self.assertEqual(updates.updates[0].title, "Reviewed")
        self.assertEqual(updates.updates[0].content.text, "The findings were reviewed.\n")
        self.assertEqual(updates.updates[1].timestamp, "2026-08-26 00:00:00.000Z")
        self.assertEqual(updates.updates[1].title, "Created")
        self.assertEqual(updates.updates[1].content.text, "Initial draft of the review notes.\n")

    def test_full_document_round_trips(self) -> None:
        """The body of the full document round-trips byte-exact through `parse_txt` (ACC-003)."""
        text = _FULL_DOC

        document = parse_txt(text)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_parse_render_reparse_is_byte_stable(self) -> None:
        """parse -> render -> re-parse is byte-stable for the full document (ACC-003, REQ-006).

        The rendered body (the engine's `MarkdownStr.__str__` re-emission)
        re-parses to an identical rendering, and the re-composed full
        document (frontmatter re-serialized + rendered body) re-parses to
        equal frontmatter and body.
        """
        document = parse_txt(_FULL_DOC)
        rendered = str(document.body)
        re_parsed_body = parse_txt(rendered).body

        self.assertEqual(str(re_parsed_body), rendered)

        re_composed = frontmatter.dumps(
            frontmatter.Post(content=rendered, **document.frontmatter.model_dump(exclude_none=True))
        )
        document2 = parse_txt(re_composed)

        self.assertEqual(document2.frontmatter, document.frontmatter)
        self.assertEqual(str(document2.body), rendered)

    def test_model_dump_surfaces_body_text(self) -> None:
        """A parsed document's `model_dump()` carries the opaque body text (ACC-003, REQ-006)."""
        document = parse_txt(_FULL_DOC)

        dump = document.model_dump(mode="json")

        self.assertEqual(
            dump["body"]["body"]["text"],
            "## Findings\n\nSome prose about what was found.\n\n- item one\n\n- item two\n\n"
            "### Detail\n\nMore prose under a free H3.\n\n```\n## Updates\n```\n",
        )
        self.assertEqual(
            dump["body"]["updates"]["updates"][0]["content"]["text"],
            "The findings were reviewed.\n",
        )

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying TxtFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_txt(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "txt")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.version, "1.0.0")


class TestParseTxtValueViolations(unittest.TestCase):
    """Model-level violations raise `pydantic.ValidationError` (ACC-003, REQ-005)."""

    def test_status_outside_closed_set_raises_validation_error(self) -> None:
        """A frontmatter `status` outside TxtFrontmatter's closed three-set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: in-review")

        with self.assertRaises(ValidationError):
            parse_txt(text)

    def test_vcr_only_complete_status_raises_validation_error(self) -> None:
        """`complete` belongs to VCR's four-value lifecycle, not TXT's three."""
        text = _MINIMAL_DOC.replace("status: draft", "status: complete")

        with self.assertRaises(ValidationError):
            parse_txt(text)

    def test_type_other_than_txt_raises_validation_error(self) -> None:
        """A frontmatter `type` other than `txt` fails validation."""
        text = _MINIMAL_DOC.replace("type: txt", "type: vcr")

        with self.assertRaises(ValidationError):
            parse_txt(text)

    def test_out_of_order_update_entries_raise_validation_error(self) -> None:
        """Newer entries below older ones fail the shared newest-first check (REQ-004)."""
        text = _MINIMAL_DOC.replace(
            "### 2026-08-31 00:00:00.000Z - Created\n\nInitial draft of the review notes.",
            "### 2026-08-30 00:00:00.000Z - Older\n\nAn older entry.\n\n"
            "### 2026-08-31 00:00:00.000Z - Created\n\nA newer entry below it.",
        )

        with self.assertRaises(ValidationError):
            parse_txt(text)


class TestParseTxtStructuralViolations(unittest.TestCase):
    """Structural violations raise the engine's `AssertionError` (ACC-001/ACC-002 document level)."""

    def _body_only(self, body: str) -> str:
        # No `textwrap.dedent` here: the `body` argument is already column-0
        # (it may itself contain multi-line content, e.g. a fenced code
        # block), and dedenting a template into which such a body is
        # interpolated would mis-indent the H1 and the fence lines.
        return f"# Ad-hoc review notes\n\n{body}\n"

    def test_missing_updates_raises_assertion_error(self) -> None:
        """A document without `## Updates` at all is a structural failure (REQ-003/REQ-004)."""
        with self.assertRaises(AssertionError):
            parse_txt(self._body_only("Some free-form prose."))

    def test_empty_body_raises_assertion_error(self) -> None:
        """H1 followed directly by `## Updates` is a structural failure (REQ-002)."""
        with self.assertRaises(AssertionError):
            parse_txt(self._body_only("## Updates\n\n### 2026-08-31 00:00:00.000Z - Created\n\nSome text."))

    def test_duplicate_updates_raises_assertion_error(self) -> None:
        """A second top-level `## Updates` is a structural failure (REQ-003)."""
        with self.assertRaises(AssertionError):
            parse_txt(
                self._body_only(
                    "Some prose.\n\n"
                    "## Updates\n\n### 2026-08-31 00:00:00.000Z - Created\n\nSome text.\n\n"
                    "## Updates\n\n### 2026-08-30 00:00:00.000Z - Older\n\nMore text."
                )
            )

    def test_h2_after_updates_raises_assertion_error(self) -> None:
        """Any other top-level H2 after `## Updates` is a structural failure (REQ-003)."""
        with self.assertRaises(AssertionError):
            parse_txt(
                self._body_only(
                    "Some prose.\n\n"
                    "## Updates\n\n### 2026-08-31 00:00:00.000Z - Created\n\nSome text.\n\n"
                    "## Notes\n\nSome notes text."
                )
            )

    def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
        """A `## Updates` H2 present with zero entries is a structural failure (REQ-004)."""
        with self.assertRaises(AssertionError):
            parse_txt(self._body_only("Some prose.\n\n## Updates"))

    def test_update_entry_with_blank_content_raises_assertion_error(self) -> None:
        """An entry heading with no body content is a structural failure (REQ-004)."""
        with self.assertRaises(AssertionError):
            parse_txt(self._body_only("Some prose.\n\n## Updates\n\n### 2026-08-31 00:00:00.000Z - Created"))

    def test_bad_update_entry_heading_raises_assertion_error(self) -> None:
        """A non-timestamp-led entry heading fails the entry alias at parse time (REQ-004)."""
        with self.assertRaises(AssertionError):
            parse_txt(self._body_only("Some prose.\n\n## Updates\n\n### 2026-08-31 - Created\n\nSome text."))

    def test_fenced_updates_in_body_is_not_structural(self) -> None:
        """A `## Updates` line inside a code fence is body content, not a section (REQ-002/REQ-003)."""
        document = parse_txt(
            self._body_only(
                "```\n## Updates\n```\n\nSome prose.\n\n"
                "## Updates\n\n### 2026-08-31 00:00:00.000Z - Created\n\nSome text."
            )
        )

        self.assertIn("```\n## Updates\n```\n", document.body.body.text)


class TestUnquotedTimestampNormalization(unittest.TestCase):
    """The `_stringify_metadata` datetime-coercion branch (feat-146 REQ-006/REQ-003).

    An unquoted frontmatter `created`/`updated` timestamp is coerced by PyYAML to a
    `datetime` before this domain's own `_stringify_metadata` runs -- such a value
    must parse and converge to the `T`-canonical form, and an unquoted date-only
    value must still be rejected by the frontmatter's own date+time pattern.
    """

    def test_unquoted_timestamps_converge_to_t_canonical_form(self) -> None:
        """Unquoted `T`- and space-separated timestamps parse and converge to the `T`-canonical
        form; an unquoted date-only value still fails the frontmatter pattern."""
        text = _MINIMAL_DOC.replace("created: '2026-08-31T00:00:00.000Z'", "created: 2026-08-31T00:00:00.000Z").replace(
            "updated: '2026-08-31T00:00:00.000Z'", "updated: 2026-08-31 00:00:00.000Z"
        )
        document = parse_txt(text)
        self.assertEqual(document.frontmatter.created, "2026-08-31T00:00:00.000Z")
        self.assertEqual(document.frontmatter.updated, "2026-08-31T00:00:00.000Z")

        with self.assertRaises(ValidationError):
            parse_txt(text.replace("created: 2026-08-31T00:00:00.000Z", "created: 2026-08-31"))


if __name__ == "__main__":
    unittest.main()
