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

"""Tests for :func:`parse_set`: the `SetDocument`-level entry point.

Covers the document-level round-trip, the four-value status enforcement
through the full parser, the mixed-tag `## Items` acceptance, the duplicate
`(tag, id)` rejection, the missing/empty `## Items` and missing `## Description`
structural rejections, and the opaque `## Description` round-trip (a fenced
code block plus nested H3s stay verbatim).
"""

from __future__ import annotations

import textwrap
import unittest

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.set.models.v1 import SetDocument
from biz.dfch.specmgr.set.models.v1.parser import parse_set, parse_set_body

# The minimal valid document: frontmatter, a single H1, an opaque
# `## Description`, and the mandatory `## Items` section with exactly one
# bullet -- nothing else.
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: set-001
    type: set
    version: 1.0.0
    status: draft
    created: '2026-08-31T00:00:00.000Z'
    updated: '2026-08-31T00:00:00.000Z'
    ---

    # Ad-hoc review set

    ## Description

    Some prose about what the set bundles and why the items belong together.

    ## Items

    - REQ 00000000-0000-4000-8000-000000000001: Sample Requirement
    """
)

# Every feature present: an opaque description with a nested H3, a bullet
# list, and a fenced `## Items` (which must stay in the description), plus
# the mandatory `## Items` section with a mixed-tag loose list and
# per-bullet notes.
_FULL_DOC = textwrap.dedent(
    """\
    ---
    id: set-001
    type: set
    version: 1.0.0
    status: review
    created: '2026-08-31T00:00:00.000Z'
    updated: '2026-08-31T00:00:00.000Z'
    ---

    # Ad-hoc review set

    ## Description

    ### Why this grouping

    Some prose about what the set bundles.

    - item one

    - item two

    ```
    ## Items
    ```

    ## Items

    - GOL 00000000-0000-4000-8000-000000000001: A Goal

      A notes paragraph for the goal.

    - REQ 00000000-0000-4000-8000-000000000002: A Requirement

    - FEAT feat-42-thermal-management: A Feature
    """
)


class TestParseSet(unittest.TestCase):
    """The document-level happy paths: parse, round-trip, model_dump."""

    def test_parses_minimal_document(self) -> None:
        result = parse_set(_MINIMAL_DOC)

        self.assertIsInstance(result, SetDocument)
        self.assertEqual(result.frontmatter.id, "set-001")
        self.assertEqual(result.frontmatter.type, "set")
        self.assertEqual(result.frontmatter.status, "draft")
        self.assertEqual(result.body.text, "Ad-hoc review set")
        self.assertEqual(len(result.body.items.items), 1)

    def test_parses_full_document(self) -> None:
        result = parse_set(_FULL_DOC)

        self.assertIsInstance(result, SetDocument)
        self.assertEqual(result.frontmatter.status, "review")
        self.assertEqual(result.body.text, "Ad-hoc review set")
        description = str(result.body.description)
        self.assertIn("### Why this grouping", description)
        self.assertIn("```\n## Items\n```", description)  # fenced heading stays in the opaque section
        items = result.body.items.items
        self.assertEqual(len(items), 3)
        self.assertIn("GOL 00000000-0000-4000-8000-000000000001: A Goal", items[0].text)
        self.assertEqual(len(items[0].notes or []), 1)
        self.assertIn("A notes paragraph for the goal.", items[0].notes[0].text)  # type: ignore[union-attr]
        self.assertIsNone(items[1].notes)
        self.assertIn("FEAT feat-42-thermal-management: A Feature", items[2].text)

    def test_full_document_round_trips(self) -> None:
        result = parse_set(_FULL_DOC)

        rendered = frontmatter_round_trip(result)
        reparsed = parse_set(rendered)

        self.assertEqual(reparsed.model_dump(mode="json"), result.model_dump(mode="json"))

    def test_parse_render_reparse_is_byte_stable(self) -> None:
        result = parse_set(_FULL_DOC)
        first = frontmatter_round_trip(result)
        second = frontmatter_round_trip(parse_set(first))

        self.assertEqual(first, second)

    def test_model_dump_surfaces_description_and_items(self) -> None:
        result = parse_set(_MINIMAL_DOC)
        dump = result.model_dump(mode="json")

        self.assertEqual(dump["body"]["text"], "Ad-hoc review set")
        self.assertIn(
            "## Description",
            dump["body"]["description"]["text"],
        )
        self.assertEqual(
            dump["body"]["items"]["items"][0]["text"], "REQ 00000000-0000-4000-8000-000000000001: Sample Requirement"
        )

    def test_parse_set_body_is_the_frontmatter_free_half(self) -> None:
        # a body without any frontmatter block: parse_set_body is the body-only half
        body = textwrap.dedent(
            """\
            # Ad-hoc review set

            ## Description

            Prose.

            ## Items

            - REQ 00000000-0000-4000-8000-000000000001: A
            """
        )
        result = parse_set_body(body)

        self.assertEqual(result.text, "Ad-hoc review set")


def frontmatter_round_trip(doc: SetDocument) -> str:
    """Re-compose the full file text from a parsed document (frontmatter + rendered body)."""
    post = frontmatter.Post(content=str(doc.body), **doc.frontmatter.model_dump())
    text = frontmatter.dumps(post)
    return text if text.endswith("\n") else text + "\n"


class TestParseSetValueViolations(unittest.TestCase):
    """Value/cross-field failures: the frontmatter closed status set, the
    duplicate (tag, id) guard, the bullet shape."""

    def test_accepts_each_of_the_four_statuses(self) -> None:
        for status in ("draft", "progress", "done", "review"):
            with self.subTest(status=status):
                text = _MINIMAL_DOC.replace("status: draft", f"status: {status}")
                self.assertEqual(parse_set(text).frontmatter.status, status)

    def test_fifth_status_is_rejected(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_set(_MINIMAL_DOC.replace("status: draft", "status: in-review"))
        self.assertIn("draft", str(ctx.exception))
        self.assertIn("review", str(ctx.exception))

    def test_type_other_than_set_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            parse_set(_MINIMAL_DOC.replace("type: set", "type: txt"))

    def test_duplicate_tag_id_pair_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace(
            "- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement",
            "- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement\n\n"
            "- REQ 00000000-0000-4000-8000-000000000001: Again",
        )
        with self.assertRaises(ValidationError) as ctx:
            parse_set(text)
        self.assertIn("used by more than one", str(ctx.exception))

    def test_mixed_tags_are_accepted(self) -> None:
        text = _MINIMAL_DOC.replace(
            "- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement",
            "- REQ 00000000-0000-4000-8000-000000000001: A\n\n"
            "- UC 00000000-0000-4000-8000-000000000002: B\n\n"
            "- FEAT feat-42: C",
        )
        result = parse_set(text)

        self.assertEqual(len(result.body.items.items), 3)

    def test_malformed_bullet_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace(
            "- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement",
            "- SOP 00000000-0000-4000-8000-000000000001: Not a reference tag",
        )
        with self.assertRaises(ValidationError):
            parse_set(text)


class TestParseSetStructuralViolations(unittest.TestCase):
    """Structural failures: missing/empty sections, the binding order, the
    trailing-completeness rule for any further H2."""

    def _body(self, body: str) -> str:
        fm = _MINIMAL_DOC.split("---\n")[1]
        return f"---\n{fm}---\n\n{body}"

    def test_missing_description_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            parse_set_body(format_text("# T\n\n## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n"))

    def test_missing_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            parse_set_body(format_text("# T\n\n## Description\n\nProse.\n"))

    def test_empty_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            parse_set_body(format_text("# T\n\n## Description\n\nProse.\n\n## Items\n"))

    def test_h2_after_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            parse_set_body(
                format_text(
                    "# T\n\n## Description\n\nProse.\n\n## Items\n\n"
                    "- REQ 00000000-0000-4000-8000-000000000001: A\n\n## Source\n\nLeft over.\n"
                )
            )

    def test_items_before_description_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            parse_set_body(
                format_text(
                    "# T\n\n## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n\n## Description\n\nProse.\n"
                )
            )

    def test_fenced_items_in_description_is_not_structural(self) -> None:
        # a fenced `## Items` line is code, not a heading: the opaque
        # description keeps it and the real `## Items` section still binds
        result = parse_set_body(
            format_text(
                "# T\n\n## Description\n\n```\n## Items\n```\n\nProse.\n\n"
                "## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n"
            )
        )

        self.assertIn("```\n## Items\n```", str(result.description))
        self.assertEqual(len(result.items.items), 1)

    def test_minimal_document_frontmatter_still_parses_through_parse_set(self) -> None:
        # the _body helper composes a full file from the minimal doc's frontmatter
        result = parse_set(
            self._body("# T\n\n## Description\n\nProse.\n\n## Items\n\n- REQ 00000000-0000-4000-8000-000000000001: A\n")
        )

        self.assertIsInstance(result, SetDocument)


if __name__ == "__main__":
    unittest.main()
