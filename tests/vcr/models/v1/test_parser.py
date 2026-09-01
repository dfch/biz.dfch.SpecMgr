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

"""Tests for :func:`parse_vcr`: the `VcrDocument`-level `from_text` entry point.

Covers the ACC-001..004 structural (engine `AssertionError`) and model-level
(`pydantic.ValidationError`) matrices from
`.specmgr/feat/feat-33-vcr/README.md`. Note: any future `list_vcr`
paging-clamp behavior is a Phase 2 tool test (`tests/vcr/tools/`), not
covered here.
"""

from __future__ import annotations

import textwrap
import unittest

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.vcr.models.v1 import VcrDocument
from biz.dfch.specmgr.vcr.models.v1.parser import parse_vcr
from biz.dfch.specmgr.models.md._markdown import format_text

# Zero optional sections: the H1, and the three mandatory `## Verifies` /
# `## Coverage` / `## Acceptance Criteria` sections -- nothing else. This is
# the shape a freshly created `vcr` document may legitimately have (every
# optional section defaults to `None` end to end through the full parser).
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: vcr-001
    type: vcr
    version: 1.0.0
    status: draft
    created: 2026-08-31
    updated: 2026-08-31
    ---

    # API Key Revocation Latency Verification

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

    Confirms that a support agent revoking a compromised partner API key
    closes the exposure window fast enough.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The revoke endpoint returns 204 within 1s
    """
)

# Every section present: `Verifies` with its optional comment, three
# `Acceptance Criteria` entries covering all four independently-optional
# `description`/`Test Steps` combinations (a number gap: AC-001 has both a
# description paragraph and `Test Steps`, AC-003 has a description
# paragraph but no `Test Steps`, AC-004 has neither -- heading only),
# `More Information`, and two `Updates` entries. Mirrors the shape
# empirically validated against `.specmgr/feat/feat-33-vcr/example.md`.
_FULL_DOC = textwrap.dedent(
    """\
    ---
    id: vcr-001
    type: vcr
    version: 1.0.0
    status: complete
    created: 2026-08-31
    updated: 2026-08-31
    ---

    # API Key Revocation Latency Verification

    ## Verifies

    <!-- Cross-referenced during the feat-32-sysrs gap-analysis review. -->

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

    Confirms that a support agent revoking a compromised partner API key
    closes the exposure window fast enough.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The revoke endpoint returns 204 within 1s

    95th-percentile latency stays below 1000 ms under a simulated background load.

    #### Test Steps

    1. Issue a new API key.

    2. Submit the revoke request.

    ### AC-003 (Inspection): The revoke handler has a well-formed not-found error path

    A static review of the handler source confirms a well-formed not-found branch.

    ### AC-004 (Special): The revocation audit-log format is compliance-certified

    ## More Information

    Verification performed against the staging gateway.

    ## Updates

    ### 2026-08-27 : Confirmed

    AC-001 and AC-003 executed against staging.

    ### 2026-08-26 - Created

    Initial verification case drafted.
    """
)


class TestParseVcr(unittest.TestCase):
    """`parse_vcr` on valid documents (ACC-001..004 round-trip)."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document (zero optional sections) parses into a VcrDocument with the expected shape."""
        document = parse_vcr(_MINIMAL_DOC)

        self.assertIsInstance(document, VcrDocument)
        self.assertEqual(document.frontmatter.id, "vcr-001")
        self.assertEqual(document.frontmatter.type, "vcr")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.created, "2026-08-31")
        self.assertEqual(document.body.text, "API Key Revocation Latency Verification")
        self.assertIn("closes the exposure window", document.body.verifies.notes.text)
        self.assertEqual(document.body.coverage.value.text, "partial")
        self.assertEqual(len(document.body.acceptance_criteria.criteria), 1)
        self.assertIsNone(document.body.more_information)
        self.assertIsNone(document.body.updates)

    def test_parses_full_document(self) -> None:
        """A document with every section present parses, with the computed fields correct."""
        document = parse_vcr(_FULL_DOC)

        self.assertEqual(document.frontmatter.id, "vcr-001")
        self.assertEqual(document.frontmatter.status, "complete")
        self.assertEqual(document.body.text, "API Key Revocation Latency Verification")

        verifies = document.body.verifies
        self.assertIsNotNone(verifies.comment)
        self.assertEqual(
            verifies.value.text, "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action"
        )

        criteria = document.body.acceptance_criteria.criteria
        self.assertEqual([(c.number, c.method) for c in criteria], [(1, "Test"), (3, "Inspection"), (4, "Special")])
        # AC-001: both a description paragraph and `Test Steps`.
        self.assertIsNotNone(criteria[0].description)
        self.assertIsNotNone(criteria[0].test_steps)
        self.assertEqual(len(criteria[0].test_steps.items), 2)
        # AC-003: a description paragraph but no `Test Steps`.
        self.assertIsNotNone(criteria[1].description)
        self.assertIsNone(criteria[1].test_steps)
        # AC-004: neither a description paragraph nor `Test Steps`.
        self.assertIsNone(criteria[2].description)
        self.assertIsNone(criteria[2].test_steps)

        self.assertIsNotNone(document.body.more_information)
        self.assertIn("staging gateway", document.body.more_information.text)

        updates = document.body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 2)
        self.assertEqual(updates.updates[0].content.text, "AC-001 and AC-003 executed against staging.")
        self.assertEqual(updates.updates[1].content.text, "Initial verification case drafted.")

    def test_full_document_round_trips(self) -> None:
        """The body of the full document round-trips byte-exact through `parse_vcr`."""
        text = _FULL_DOC

        document = parse_vcr(text)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying VcrFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_vcr(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "vcr")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.version, "1.0.0")


class TestParseVcrValueViolations(unittest.TestCase):
    """Model-level violations raise `pydantic.ValidationError`."""

    def test_status_outside_closed_set_raises_validation_error(self) -> None:
        """A frontmatter `status` outside VcrFrontmatter's closed four-set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: in-review")

        with self.assertRaises(ValidationError):
            parse_vcr(text)

    def test_dec_only_accepted_status_raises_validation_error(self) -> None:
        """`accepted` belongs to DEC's six-value set, not VCR's four."""
        text = _MINIMAL_DOC.replace("status: draft", "status: accepted")

        with self.assertRaises(ValidationError):
            parse_vcr(text)

    def test_type_other_than_vcr_raises_validation_error(self) -> None:
        """A frontmatter `type` other than `vcr` fails validation."""
        text = _MINIMAL_DOC.replace("type: vcr", "type: dec")

        with self.assertRaises(ValidationError):
            parse_vcr(text)

    def test_coverage_outside_closed_set_raises_validation_error(self) -> None:
        """A `## Coverage` value outside `full`/`partial`/`none` fails validation."""
        text = _MINIMAL_DOC.replace("partial", "unknown")

        with self.assertRaises(ValidationError):
            parse_vcr(text)

    def test_verifies_value_with_unknown_type_tag_raises_validation_error(self) -> None:
        """A `## Verifies` value tagged with something other than `REQ`/`UC` fails validation."""
        text = _MINIMAL_DOC.replace(
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action",
            "DEC 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action",
        )

        with self.assertRaises(ValidationError):
            parse_vcr(text)

    def test_duplicate_ac_number_raises_validation_error(self) -> None:
        """Two `### AC-001` headings fail the `Vcr` after-validator."""
        text = _FULL_DOC.replace(
            "### AC-003 (Inspection): The revoke handler has a well-formed not-found error path",
            "### AC-001 (Inspection): The revoke handler has a well-formed not-found error path",
        )

        with self.assertRaises(ValidationError):
            parse_vcr(text)

    def test_ac_number_and_method_computed(self) -> None:
        """`AcceptanceCriterion.number`/`.method` are computed from the heading."""
        document = parse_vcr(_FULL_DOC)

        criteria = document.body.acceptance_criteria.criteria
        first, second, third = criteria

        self.assertEqual(first.number, 1)
        self.assertEqual(first.method, "Test")
        self.assertEqual(second.number, 3)
        self.assertEqual(second.method, "Inspection")
        self.assertEqual(third.number, 4)
        self.assertEqual(third.method, "Special")


class TestParseVcrStructuralViolations(unittest.TestCase):
    """Structural violations raise the engine's `AssertionError`."""

    def test_unknown_h2_raises_assertion_error(self) -> None:
        """An H2 heading no field claims is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Unknown Section

            Some unknown prose.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_missing_verifies_raises_assertion_error(self) -> None:
        """A missing mandatory `## Verifies` is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_missing_coverage_raises_assertion_error(self) -> None:
        """A missing mandatory `## Coverage` is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_missing_acceptance_criteria_raises_assertion_error(self) -> None:
        """A missing mandatory `## Acceptance Criteria` is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_acceptance_criteria_with_zero_criteria_raises_assertion_error(self) -> None:
        """A `## Acceptance Criteria` H2 present with zero criteria is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_acceptance_criterion_heading_without_title_raises_assertion_error(self) -> None:
        """`### AC-001 (Test):` without criterion text fails the AC alias at parse time."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test):
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_acceptance_criterion_heading_with_unknown_method_raises_assertion_error(self) -> None:
        """`### AC-001 (Certification): ...` fails the AC alias at parse time (not a DTAIS word)."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Certification): Some criterion
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_test_steps_with_zero_items_raises_assertion_error(self) -> None:
        """A `#### Test Steps` present with zero items is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion

            #### Test Steps
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_updates_before_more_information_raises_assertion_error(self) -> None:
        """Misordering: `## Updates` must come after `## More Information`."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion

            ## Updates

            ### 2026-08-26 - Created

            Some update text.

            ## More Information

            Some more information text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        """A duplicated `## Coverage` H2 is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Coverage

            full

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
        """Non-blank content before the H1 is a structural failure."""
        text = textwrap.dedent(
            """\
            Some leading prose.

            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)

    def test_second_h1_raises_assertion_error(self) -> None:
        """A second H1 is a structural failure."""
        text = textwrap.dedent(
            """\
            # API Key Revocation Latency Verification

            ## Verifies

            REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

            Confirms that revocation is fast enough.

            ## Coverage

            partial

            ## Acceptance Criteria

            ### AC-001 (Test): Some criterion

            # Second Title
            """
        )

        with self.assertRaises(AssertionError):
            parse_vcr(text)


if __name__ == "__main__":
    unittest.main()
