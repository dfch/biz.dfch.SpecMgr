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

"""Tests for :func:`parse_sop`: the `SopDocument`-level `from_text` entry point.

Covers the ACC-001 (structural violations -> engine `AssertionError`) and
ACC-002 (model-level violations -> `pydantic.ValidationError`) matrices from
`.specmgr/feat/feat-30-sop/README.md`. Note: ACC-002's `list_sop` paging-clamp
part is a Phase 2 tool test (`tests/sop/tools/`), not covered here.
"""

from __future__ import annotations

import textwrap
import unittest

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.sop.models.v1 import SopDocument
from biz.dfch.specmgr.sop.models.v1.parser import parse_sop

# Zero optional sections: the H1, the mandatory `## Purpose`, and the
# mandatory `## Procedure` (with one step) -- nothing else. This is the shape
# a freshly created `sop` document may legitimately have (ACC-002: every
# optional section defaults to `None` end to end through the full parser).
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: sop-001
    type: sop
    version: 1.0.0
    status: draft
    created: '2026-08-30 00:00:00.000Z'
    updated: '2026-08-30 00:00:00.000Z'
    ---

    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)

# Every section present: Scope, Definitions, RASCI with `Support` deliberately
# empty (present-with-zero-items), Safety and Precautions, 5 `Step`s (with a
# number gap), `Related Artifacts` with all five sub-lists including `Sops`,
# `More Information`, and one `## Updates` entry with a well-formed ISO8601
# timestamp (the leading-zero step number below is part of ACC-002's
# computed-field matrix).
_FULL_DOC = textwrap.dedent(
    """\
    ---
    id: sop-001
    type: sop
    version: 1.0.0
    status: active
    created: '2026-08-30 00:00:00.000Z'
    updated: '2026-08-30 00:00:00.000Z'
    ---

    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Scope

    All new hires.

    ## Definitions

    - SSO: Single Sign-On.

    ## Roles and Responsibilities

    ### Accountable

    The IT Manager.

    ### Responsible

    - Helpdesk Lead

    ### Support

    ### Consulted

    - HR Business Partner

    ### Informed

    - The new hire

    ## Safety and Precautions

    Verify identity first.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.

    ### Step 2: Verify identity

    The service desk verifies identity.

    ## Related Artifacts

    ### Requirements

    - REQ-0001: Onboarding

    ### Decisions

    - DEC-0001: SSO choice

    ### Goals

    - GOL-0001: Fast onboarding

    ### Acceptance Criteria

    - ACC-0001: Account works

    ### Sops

    - SOP-0042: Account deprovisioning

    ## More Information

    See the IT wiki.

    ## Updates

    ### 2026-08-30 14:30:00.000+02:00 - Approved

    Signed off.
    """
)


class TestParseSop(unittest.TestCase):
    """`parse_sop` on valid documents (ACC-001/ACC-002 round-trip)."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document (zero optional sections) parses into a SopDocument with the expected shape."""
        document = parse_sop(_MINIMAL_DOC)

        self.assertIsInstance(document, SopDocument)
        self.assertEqual(document.frontmatter.id, "sop-001")
        self.assertEqual(document.frontmatter.type, "sop")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.created, "2026-08-30 00:00:00.000Z")
        self.assertEqual(document.body.text, "New Employee IT Account Provisioning")
        self.assertIn("Provision accounts for new hires", document.body.purpose.text)
        self.assertEqual([(s.number, s.name) for s in document.body.procedure.steps], [(1, "Submit request")])
        self.assertIsNone(document.body.scope)
        self.assertIsNone(document.body.definitions)
        self.assertIsNone(document.body.roles_and_responsibilities)
        self.assertIsNone(document.body.safety_and_precautions)
        self.assertIsNone(document.body.related_artifacts)
        self.assertIsNone(document.body.more_information)
        self.assertIsNone(document.body.updates)

    def test_parses_full_document(self) -> None:
        """A document with every section present parses, with the computed fields correct (ACC-002)."""
        document = parse_sop(_FULL_DOC)

        self.assertEqual(document.frontmatter.id, "sop-001")
        self.assertEqual(document.frontmatter.status, "active")
        self.assertEqual(document.body.text, "New Employee IT Account Provisioning")
        self.assertIsNotNone(document.body.scope)
        self.assertIn("All new hires", document.body.scope.text)
        self.assertIsNotNone(document.body.definitions)
        self.assertIsNotNone(document.body.safety_and_precautions)

        rasci = document.body.roles_and_responsibilities
        self.assertIsNotNone(rasci)
        self.assertEqual(rasci.accountable.value.text, "The IT Manager.")
        self.assertEqual([item.text for item in rasci.responsible.items], ["Helpdesk Lead"])
        # Support is present but empty (present-with-zero-items).
        self.assertIsNotNone(rasci.support)
        self.assertIsNone(rasci.support.items)
        self.assertEqual([item.text for item in rasci.consulted.items], ["HR Business Partner"])
        self.assertEqual([item.text for item in rasci.informed.items], ["The new hire"])

        self.assertEqual(
            [(s.number, s.name) for s in document.body.procedure.steps],
            [(1, "Submit request"), (2, "Verify identity")],
        )

    def test_full_document_round_trips(self) -> None:
        """The body of the full document round-trips byte-exact through `parse_sop`."""
        text = _FULL_DOC

        document = parse_sop(text)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying SopFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_sop(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "sop")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.version, "1.0.0")

    def test_related_artifacts_sub_lists_independently_optional(self) -> None:
        """Each of the five sub-lists can be present/absent independently (ACC-002)."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Related Artifacts

            ### Sops

            - SOP-0042: Account deprovisioning
            """
        )

        document = parse_sop(text)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertIsNone(related_artifacts.requirements)
        self.assertIsNone(related_artifacts.decisions)
        self.assertIsNone(related_artifacts.goals)
        self.assertIsNone(related_artifacts.acceptance_criteria)
        self.assertEqual(
            [item.text for item in related_artifacts.sops.items],
            ["SOP-0042: Account deprovisioning"],
        )

    def test_related_artifacts_with_zero_sub_lists_parses(self) -> None:
        """A `## Related Artifacts` H2 with none of the five sub-lists is valid (all children optional)."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Related Artifacts
            """
        )

        document = parse_sop(text)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertIsNone(related_artifacts.requirements)
        self.assertIsNone(related_artifacts.decisions)
        self.assertIsNone(related_artifacts.goals)
        self.assertIsNone(related_artifacts.acceptance_criteria)
        self.assertIsNone(related_artifacts.sops)


class TestParseSopValueViolations(unittest.TestCase):
    """Model-level violations raise `pydantic.ValidationError` (ACC-002)."""

    def test_status_outside_closed_set_raises_validation_error(self) -> None:
        """A frontmatter `status` outside SopFrontmatter's closed five-set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: in-review")

        with self.assertRaises(ValidationError):
            parse_sop(text)

    def test_dec_only_proposed_status_raises_validation_error(self) -> None:
        """`proposed` belongs to DEC/GOL's set, not SOP's five-value set."""
        text = _MINIMAL_DOC.replace("status: draft", "status: proposed")

        with self.assertRaises(ValidationError):
            parse_sop(text)

    def test_type_other_than_sop_raises_validation_error(self) -> None:
        """A frontmatter `type` other than `sop` fails validation."""
        text = _MINIMAL_DOC.replace("type: sop", "type: gol")

        with self.assertRaises(ValidationError):
            parse_sop(text)

    def test_duplicate_step_number_raises_validation_error(self) -> None:
        """Two `### Step 1:` headings fail the `Sop` after-validator."""
        text = _FULL_DOC.replace("### Step 2: Verify identity", "### Step 1: Verify identity")

        with self.assertRaises(ValidationError):
            parse_sop(text)

    def test_duplicate_step_number_via_leading_zero_raises_validation_error(self) -> None:
        """`### Step 1:` and `### Step 01:` are the same number -- a duplicate."""
        text = _FULL_DOC.replace("### Step 2: Verify identity", "### Step 01: Verify identity")

        with self.assertRaises(ValidationError):
            parse_sop(text)

    def test_step_number_and_name_computed(self) -> None:
        """`Step.number`/`Step.name` are computed from the heading (ACC-002)."""
        document = parse_sop(_FULL_DOC)

        self.assertEqual(
            [(s.number, s.name) for s in document.body.procedure.steps],
            [(1, "Submit request"), (2, "Verify identity")],
        )

    def test_update_entry_timestamp_and_title_computed(self) -> None:
        """`UpdateEntry.timestamp`/`UpdateEntry.title` are computed from the heading (ACC-002)."""
        document = parse_sop(_FULL_DOC)

        updates = document.body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 1)
        self.assertEqual(updates.updates[0].timestamp, "2026-08-30 14:30:00.000+02:00")
        self.assertEqual(updates.updates[0].title, "Approved")


class TestParseSopStructuralViolations(unittest.TestCase):
    """Structural violations raise the engine's `AssertionError` (ACC-001)."""

    def test_unknown_h2_raises_assertion_error(self) -> None:
        """An H2 heading no field claims is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Unknown Section

            Some unknown prose.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_missing_purpose_raises_assertion_error(self) -> None:
        """A missing mandatory `## Purpose` is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_missing_procedure_raises_assertion_error(self) -> None:
        """A missing mandatory `## Procedure` is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_procedure_with_zero_steps_raises_assertion_error(self) -> None:
        """A `## Procedure` H2 present with zero steps is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_step_heading_without_title_raises_assertion_error(self) -> None:
        """`### Step 1` without `: title` fails the step alias at parse time."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_roles_without_accountable_raises_assertion_error(self) -> None:
        """`## Roles and Responsibilities` without `### Accountable` is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Roles and Responsibilities

            ### Responsible

            - Helpdesk Lead

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_roles_without_responsible_raises_assertion_error(self) -> None:
        """`## Roles and Responsibilities` without `### Responsible` is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Roles and Responsibilities

            ### Accountable

            The IT Manager.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_accountable_as_bullet_list_raises_assertion_error(self) -> None:
        """`### Accountable` written as a bullet list instead of a single paragraph is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Roles and Responsibilities

            ### Accountable

            - The IT Manager

            ### Responsible

            - Helpdesk Lead

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_responsible_empty_raises_assertion_error(self) -> None:
        """`### Responsible` present but empty is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Roles and Responsibilities

            ### Accountable

            The IT Manager.

            ### Responsible

            ### Consulted

            - HR

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_related_artifacts_sub_list_with_zero_items_raises_assertion_error(self) -> None:
        """A `## Related Artifacts` sub-list present with zero items is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Related Artifacts

            ### Requirements
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_malformed_updates_entry_heading_raises_assertion_error(self) -> None:
        """A `## Updates` entry with a malformed timestamp (no offset) is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Updates

            ### 2026-08-30 14:30:00.000 - Approved

            Signed off.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_updates_entry_with_em_dash_separator_raises_assertion_error(self) -> None:
        """ACC-001: a `## Updates` entry heading using the em-dash separator is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Updates

            ### 2026-08-30 14:30:00.000+02:00 — Approved

            Signed off.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_malformed_updates_entry_missing_title_raises_assertion_error(self) -> None:
        """A `## Updates` entry heading missing the ` - `/` : ` + `title` is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Updates

            ### 2026-08-30 14:30:00.000+02:00

            Signed off.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
        """A `## Updates` H2 present with zero entries is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Updates
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_updates_before_more_information_raises_assertion_error(self) -> None:
        """Misordering: `## Updates` must come after `## More Information`."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Updates

            ### 2026-08-30 14:30:00.000+02:00 - Created

            Some update text.

            ## More Information

            Some more information text.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_safety_and_precautions_after_procedure_raises_assertion_error(self) -> None:
        """Misordering: `## Safety and Precautions` must come before `## Procedure`."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            ## Safety and Precautions

            Verify identity first.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        """A duplicated `## Purpose` H2 is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            First purpose.

            ## Purpose

            Second purpose.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
        """Non-blank content before the H1 is a structural failure."""
        text = textwrap.dedent(
            """\
            Some leading prose.

            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)

    def test_second_h1_raises_assertion_error(self) -> None:
        """A second H1 is a structural failure."""
        text = textwrap.dedent(
            """\
            # New Employee IT Account Provisioning

            ## Purpose

            Provision accounts for new hires.

            ## Procedure

            ### Step 1: Submit request

            HR submits the request.

            # Second Title
            """
        )

        with self.assertRaises(AssertionError):
            parse_sop(text)


if __name__ == "__main__":
    unittest.main()
