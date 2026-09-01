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

"""Tests for :func:`parse_dec`: the `DecDocument`-level `from_text` entry point.

Covers the ACC-001 (structural violations -> engine `AssertionError`) and
ACC-002 (model-level violations -> `pydantic.ValidationError`) matrices from
`.specmgr/feat/feat-21-decision/README.md`. Note: ACC-002's `list_dec`
paging-clamp part is a Phase 2 tool test (`tests/dec/tools/`), not covered
here.
"""

from __future__ import annotations

import textwrap
import unittest

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1 import DecDocument
from biz.dfch.specmgr.dec.models.v1.parser import parse_dec
from biz.dfch.specmgr.models.md._markdown import format_text

# Zero optional sections: the H1, the mandatory `## Context and Problem
# Statement`, and the mandatory `## Decision Outcome` (with its lead
# paragraph) -- nothing else. This is the shape a freshly created `dec`
# document may legitimately have (ACC-002: every optional section defaults
# to `None` end to end through the full parser).
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: dec-001
    type: dec
    version: 1.0.0
    status: draft
    created: 2026-08-26
    updated: 2026-08-26
    ---

    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)

# Every section present: both outcome H3s, `Related Artifacts` with two
# sub-lists, `Pros and Cons` with two options (a number gap), `More
# Information`, and two `Updates` entries (the leading-zero option number
# below is part of ACC-002's computed-field matrix).
_FULL_DOC = textwrap.dedent(
    """\
    ---
    id: dec-001
    type: dec
    version: 1.0.0
    status: accepted
    created: 2026-08-26
    updated: 2026-08-27
    ---

    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Drivers

    - Latency under 100 ms at p95.

    ## Considered Options

    We weighed a key-value store and a document store.

    ## Decision Outcome

    We chose the document store.

    ### Consequences

    Reporting reads from the nightly export.

    ### Confirmation

    A two-week load test.

    ## Related Artifacts

    ### Requirements

    - REQ-9687: Order dashboard read latency

    ### Goals

    - GOL-0007: Cost-neutral platform migration

    ## Pros and Cons

    ### Option 1: Document Store

    Meets the latency budget.

    ### Option 03: Key-Value Store

    Even faster reads.

    ## More Information

    Harness config in the platform repository.

    ## Updates

    ### 2026-08-26 - Created

    Initial decision record drafted.

    ### 2026-08-27 : Confirmed

    Load test passed.
    """
)


class TestParseDec(unittest.TestCase):
    """`parse_dec` on valid documents (ACC-001/ACC-002 round-trip)."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document (zero optional sections) parses into a DecDocument with the expected shape."""
        document = parse_dec(_MINIMAL_DOC)

        self.assertIsInstance(document, DecDocument)
        self.assertEqual(document.frontmatter.id, "dec-001")
        self.assertEqual(document.frontmatter.type, "dec")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.created, "2026-08-26")
        self.assertEqual(document.body.text, "Choose a Document Store")
        self.assertIn("cannot serve the dashboard read path", document.body.context.text)
        self.assertEqual(document.body.outcome.statement.text, "We chose the document store.")
        self.assertIsNone(document.body.outcome.consequences)
        self.assertIsNone(document.body.outcome.confirmation)
        self.assertIsNone(document.body.drivers)
        self.assertIsNone(document.body.considered)
        self.assertIsNone(document.body.related_artifacts)
        self.assertIsNone(document.body.pros_and_cons)
        self.assertIsNone(document.body.more_information)
        self.assertIsNone(document.body.updates)

    def test_parses_full_document(self) -> None:
        """A document with every section present parses, with the computed fields correct (ACC-002)."""
        document = parse_dec(_FULL_DOC)

        self.assertEqual(document.frontmatter.id, "dec-001")
        self.assertEqual(document.frontmatter.status, "accepted")
        self.assertEqual(document.body.text, "Choose a Document Store")
        self.assertIsNotNone(document.body.drivers)
        self.assertIsNotNone(document.body.considered)

        outcome = document.body.outcome
        self.assertEqual(outcome.statement.text, "We chose the document store.")
        self.assertIsNotNone(outcome.consequences)
        self.assertIn("nightly export", outcome.consequences.text)
        self.assertIsNotNone(outcome.confirmation)
        self.assertIn("two-week load test", outcome.confirmation.text)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertEqual(
            [item.text for item in related_artifacts.requirements.items],
            ["REQ-9687: Order dashboard read latency"],
        )
        self.assertIsNone(related_artifacts.decisions)
        self.assertEqual(
            [item.text for item in related_artifacts.goals.items], ["GOL-0007: Cost-neutral platform migration"]
        )
        self.assertIsNone(related_artifacts.acceptance_criteria)

        pros_and_cons = document.body.pros_and_cons
        self.assertIsNotNone(pros_and_cons)
        # "Option 03" normalizes to the integer 3; the 1 -> 3 gap is allowed.
        self.assertEqual(
            [(option.number, option.name) for option in pros_and_cons.options],
            [(1, "Document Store"), (3, "Key-Value Store")],
        )

        self.assertIsNotNone(document.body.more_information)
        self.assertIn("Harness config", document.body.more_information.text)

        updates = document.body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 2)
        self.assertEqual(updates.updates[0].content.text, "Initial decision record drafted.")
        self.assertEqual(updates.updates[1].content.text, "Load test passed.")

    def test_full_document_round_trips(self) -> None:
        """The body of the full document round-trips byte-exact through `parse_dec`."""
        text = _FULL_DOC

        document = parse_dec(text)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying DecFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_dec(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "dec")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.version, "1.0.0")

    def test_related_artifacts_sub_lists_independently_optional(self) -> None:
        """Each of the four sub-lists can be present/absent independently (ACC-002)."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Related Artifacts

            ### Decisions

            - DEC-2703: Nightly order export
            """
        )

        document = parse_dec(text)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertIsNone(related_artifacts.requirements)
        self.assertEqual([item.text for item in related_artifacts.decisions.items], ["DEC-2703: Nightly order export"])
        self.assertIsNone(related_artifacts.goals)
        self.assertIsNone(related_artifacts.acceptance_criteria)

    def test_related_artifacts_with_zero_sub_lists_parses(self) -> None:
        """A `## Related Artifacts` H2 with none of the four sub-lists is valid (all children optional)."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Related Artifacts
            """
        )

        document = parse_dec(text)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertIsNone(related_artifacts.requirements)
        self.assertIsNone(related_artifacts.decisions)
        self.assertIsNone(related_artifacts.goals)
        self.assertIsNone(related_artifacts.acceptance_criteria)


class TestParseDecValueViolations(unittest.TestCase):
    """Model-level violations raise `pydantic.ValidationError` (ACC-002)."""

    def test_status_outside_closed_set_raises_validation_error(self) -> None:
        """A frontmatter `status` outside DecFrontmatter's closed six-set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: in-review")

        with self.assertRaises(ValidationError):
            parse_dec(text)

    def test_gol_only_implemented_status_raises_validation_error(self) -> None:
        """`implemented` belongs to GOL's seven-value set, not DEC's six."""
        text = _MINIMAL_DOC.replace("status: draft", "status: implemented")

        with self.assertRaises(ValidationError):
            parse_dec(text)

    def test_type_other_than_dec_raises_validation_error(self) -> None:
        """A frontmatter `type` other than `dec` fails validation."""
        text = _MINIMAL_DOC.replace("type: dec", "type: gol")

        with self.assertRaises(ValidationError):
            parse_dec(text)

    def test_duplicate_option_number_raises_validation_error(self) -> None:
        """Two `### Option 1:` headings fail the `Decision` after-validator."""
        text = _FULL_DOC.replace("### Option 03: Key-Value Store", "### Option 1: Key-Value Store")

        with self.assertRaises(ValidationError):
            parse_dec(text)

    def test_duplicate_option_number_via_leading_zero_raises_validation_error(self) -> None:
        """`### Option 1:` and `### Option 01:` are the same number -- a duplicate."""
        text = _FULL_DOC.replace("### Option 03: Key-Value Store", "### Option 01: Key-Value Store")

        with self.assertRaises(ValidationError):
            parse_dec(text)

    def test_option_number_and_name_computed(self) -> None:
        """`Option.number`/`Option.name` are computed from the heading (ACC-002)."""
        document = parse_dec(_FULL_DOC)

        pros_and_cons = document.body.pros_and_cons
        self.assertIsNotNone(pros_and_cons)
        first, second = pros_and_cons.options

        self.assertEqual(first.number, 1)
        self.assertEqual(first.name, "Document Store")
        # Leading zeros are accepted: "03" computes to the integer 3.
        self.assertEqual(second.number, 3)
        self.assertEqual(second.name, "Key-Value Store")


class TestParseDecStructuralViolations(unittest.TestCase):
    """Structural violations raise the engine's `AssertionError` (ACC-001)."""

    def test_unknown_h2_raises_assertion_error(self) -> None:
        """An H2 heading no field claims is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Unknown Section

            Some unknown prose.

            ## Decision Outcome

            We chose the document store.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_missing_context_raises_assertion_error(self) -> None:
        """A missing mandatory `## Context and Problem Statement` is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Decision Outcome

            We chose the document store.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_missing_decision_outcome_raises_assertion_error(self) -> None:
        """A missing mandatory `## Decision Outcome` is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_outcome_without_lead_prose_raises_assertion_error(self) -> None:
        """`## Decision Outcome` with a bare list in place of the lead paragraph is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            - a list item
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_pros_and_cons_with_zero_options_raises_assertion_error(self) -> None:
        """A `## Pros and Cons` H2 present with zero options is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Pros and Cons
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_option_heading_without_title_raises_assertion_error(self) -> None:
        """`### Option 1` without `: title` fails the option alias at parse time."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Pros and Cons

            ### Option 1
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
        """A `## Updates` H2 present with zero entries is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Updates
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_updates_entry_without_lead_paragraph_raises_assertion_error(self) -> None:
        """An `## Updates` entry whose heading carries no lead paragraph is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Updates

            ### 2026-08-26 - Created
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_updates_before_more_information_raises_assertion_error(self) -> None:
        """Misordering: `## Updates` must come after `## More Information`."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Updates

            ### 2026-08-26 - Created

            Some update text.

            ## More Information

            Some more information text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_related_artifacts_after_pros_and_cons_raises_assertion_error(self) -> None:
        """Misordering: `## Related Artifacts` must come before `## Pros and Cons`."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            ## Pros and Cons

            ### Option 1: Document Store

            Meets the latency budget.

            ## Related Artifacts

            ### Requirements

            - REQ-9687: Order dashboard read latency
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_consequences_outside_decision_outcome_raises_assertion_error(self) -> None:
        """Misordering: `### Consequences` only belongs under `## Decision Outcome`."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ### Consequences

            Some consequence prose.

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_confirmation_outside_decision_outcome_raises_assertion_error(self) -> None:
        """Misordering: `### Confirmation` only belongs under `## Decision Outcome`."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ### Confirmation

            Some confirmation prose.

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_old_adr_pros_and_cons_heading_raises_assertion_error(self) -> None:
        """The old ADR heading `## Pros and Cons of the Options` is rejected (LITERAL alias)."""
        text = _FULL_DOC.replace("## Pros and Cons", "## Pros and Cons of the Options")

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        """A duplicated `## Context and Problem Statement` H2 is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            First context prose.

            ## Context and Problem Statement

            Second context prose.

            ## Decision Outcome

            We chose the document store.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
        """Non-blank content before the H1 is a structural failure."""
        text = textwrap.dedent(
            """\
            Some leading prose.

            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)

    def test_second_h1_raises_assertion_error(self) -> None:
        """A second H1 is a structural failure."""
        text = textwrap.dedent(
            """\
            # Choose a Document Store

            ## Context and Problem Statement

            The current store cannot serve the dashboard read path.

            ## Decision Outcome

            We chose the document store.

            # Second Title
            """
        )

        with self.assertRaises(AssertionError):
            parse_dec(text)


if __name__ == "__main__":
    unittest.main()
