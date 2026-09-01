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

"""Tests for :func:`parse_feat`: the `FeatDocument`-level `from_text` entry point.

Covers the ACC-001 (structural violations -> engine `AssertionError`;
value violations -> `pydantic.ValidationError`) matrix from
`.specmgr/feat/feat-31-feature/README.md`, plus the reference document's
byte-exact round-trip (seeded from
`.specmgr/feat/feat-31-feature/example.md`, see
`tests/feat/models/v1/data/feat_reference.md`).
"""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.models.v1.parser import parse_feat
from biz.dfch.specmgr.models.md._markdown import format_text

_DATA_DIR = Path(__file__).parent / "data"

# The mandatory-sections-only shape: H1, `## Plan` (Overview/Requirements/
# Acceptance Criteria/Scope/Task List, no optional Dependencies/Design
# Notes/Related Decisions), `## Progress` (Current Status/Updates, no
# optional Blockers/Decisions Made/Related PRs/More Information).
_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: feat-1-widget
    type: feat
    version: 1.0.0
    status: planning
    created: '2026-08-26 00:00:00.000Z'
    updated: '2026-08-26 00:00:00.000Z'
    ---

    # Feature: A Widget

    ## Plan

    ### Overview

    Some overview text.

    ### Requirements

    - REQ-001: Some requirement.

    ### Acceptance Criteria

    - [ ] ACC-001: Some criterion.

    ### Scope

    #### Included

    - A thing.

    #### Explicitly Out Of Scope

    - Another thing.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Set up

    ## Progress

    ### Current Status

    Some status text.

    ### Updates

    #### 2026-08-26 09:00:00.000Z - Created

    Initial draft.
    """
)


def _full_doc_text() -> str:
    return (_DATA_DIR / "feat_reference.md").read_text(encoding="utf-8")


class TestParseFeat(unittest.TestCase):
    """`parse_feat` on valid documents (ACC-001 round-trip)."""

    def test_parses_minimal_document(self) -> None:
        document = parse_feat(_MINIMAL_DOC)

        self.assertIsInstance(document, FeatDocument)
        self.assertEqual(document.frontmatter.id, "feat-1-widget")
        self.assertEqual(document.frontmatter.type, "feat")
        self.assertEqual(document.frontmatter.status, "planning")
        self.assertEqual(document.frontmatter.created, "2026-08-26 00:00:00.000Z")
        self.assertEqual(document.body.text, "Feature: A Widget")
        self.assertIsNone(document.body.plan.dependencies)
        self.assertIsNone(document.body.plan.design_notes)
        self.assertIsNone(document.body.plan.related_decisions)
        self.assertIsNone(document.body.progress.blockers)
        self.assertIsNone(document.body.progress.decisions_made)
        self.assertIsNone(document.body.progress.related_prs_commits)
        self.assertIsNone(document.body.progress.more_information)

    def test_parses_full_reference_document(self) -> None:
        document = parse_feat(_full_doc_text())

        self.assertEqual(document.frontmatter.status, "progress")
        self.assertEqual(document.body.text, "Feature: Example Widget")

        phases = document.body.plan.task_list.phases
        self.assertGreaterEqual(len(phases), 2)
        for phase in phases:
            with self.subTest(phase=phase.number):
                self.assertGreaterEqual(len(phase.items), 1)

        updates = document.body.progress.updates.updates
        self.assertGreaterEqual(len(updates), 2)

        decisions_made = document.body.progress.decisions_made
        self.assertIsNotNone(decisions_made)
        self.assertGreaterEqual(len(decisions_made.decisions), 2)

    def test_full_reference_document_body_round_trips(self) -> None:
        text = _full_doc_text()

        document = parse_feat(text)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_defaults_frontmatter_when_absent(self) -> None:
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_feat(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "feat")
        self.assertEqual(document.frontmatter.status, "planning")
        self.assertEqual(document.frontmatter.version, "1.0.0")


class TestParseFeatValueViolations(unittest.TestCase):
    """Model-level violations raise `pydantic.ValidationError` (ACC-001)."""

    def test_status_outside_closed_set_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace("status: planning", "status: draft")

        with self.assertRaises(ValidationError):
            parse_feat(text)

    def test_hyphenated_status_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace("status: planning", "status: in-progress")

        with self.assertRaises(ValidationError):
            parse_feat(text)

    def test_type_other_than_feat_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace("type: feat", "type: dec")

        with self.assertRaises(ValidationError):
            parse_feat(text)

    def test_malformed_requirement_item_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace("- REQ-001: Some requirement.", "- Not a requirement.")

        with self.assertRaises(ValidationError):
            parse_feat(text)

    def test_malformed_acceptance_criterion_item_raises_validation_error(self) -> None:
        text = _MINIMAL_DOC.replace("- [ ] ACC-001: Some criterion.", "- [ ] Not a criterion.")

        with self.assertRaises(ValidationError):
            parse_feat(text)

    def test_out_of_order_updates_entry_raises_validation_error(self) -> None:
        text = textwrap.dedent(
            """\
            # Feature: A Widget

            ## Plan

            ### Overview

            Some overview text.

            ### Requirements

            - REQ-001: Some requirement.

            ### Acceptance Criteria

            - [ ] ACC-001: Some criterion.

            ### Scope

            #### Included

            - A thing.

            #### Explicitly Out Of Scope

            - Another thing.

            ### Task List

            #### Phase 0: Scaffolding

            - [x] Task 0.1: Set up

            ## Progress

            ### Current Status

            Some status text.

            ### Updates

            #### 2026-08-26 09:00:00.000Z - Created

            Initial draft.

            #### 2026-08-27 09:00:00.000Z - Later

            A later update, out of order.
            """
        )

        with self.assertRaises(ValidationError):
            parse_feat(text)


class TestParseFeatStructuralViolations(unittest.TestCase):
    """Structural violations raise the engine's `AssertionError` (ACC-001)."""

    def test_unknown_h2_raises_assertion_error(self) -> None:
        text = textwrap.dedent(
            """\
            # Feature: A Widget

            ## Plan

            ### Overview

            Some overview text.

            ### Requirements

            - REQ-001: Some requirement.

            ### Acceptance Criteria

            - [ ] ACC-001: Some criterion.

            ### Scope

            #### Included

            - A thing.

            #### Explicitly Out Of Scope

            - Another thing.

            ### Task List

            #### Phase 0: Scaffolding

            - [x] Task 0.1: Set up

            ## Unknown Section

            Some unknown prose.

            ## Progress

            ### Current Status

            Some status text.

            ### Updates

            #### 2026-08-26 09:00:00.000Z - Created

            Initial draft.
            """
        )

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_missing_requirements_raises_assertion_error(self) -> None:
        text = textwrap.dedent(
            """\
            # Feature: A Widget

            ## Plan

            ### Overview

            Some overview text.

            ### Acceptance Criteria

            - [ ] ACC-001: Some criterion.

            ### Scope

            #### Included

            - A thing.

            #### Explicitly Out Of Scope

            - Another thing.

            ### Task List

            #### Phase 0: Scaffolding

            - [x] Task 0.1: Set up

            ## Progress

            ### Current Status

            Some status text.

            ### Updates

            #### 2026-08-26 09:00:00.000Z - Created

            Initial draft.
            """
        )

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_malformed_phase_heading_raises_assertion_error(self) -> None:
        text = _MINIMAL_DOC.replace("#### Phase 0: Scaffolding", "#### Phase Zero: Scaffolding")

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_malformed_update_entry_heading_raises_assertion_error(self) -> None:
        text = _MINIMAL_DOC.replace("#### 2026-08-26 09:00:00.000Z - Created", "#### Not A Timestamp - Created")

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_update_entry_with_em_dash_separator_raises_assertion_error(self) -> None:
        """ACC-001: an em-dash-separated `### Updates` entry heading is a structural failure."""
        text = _MINIMAL_DOC.replace(
            "#### 2026-08-26 09:00:00.000Z - Created", "#### 2026-08-26 09:00:00.000Z — Created"
        )

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_task_list_with_zero_phases_raises_assertion_error(self) -> None:
        text = textwrap.dedent(
            """\
            # Feature: A Widget

            ## Plan

            ### Overview

            Some overview text.

            ### Requirements

            - REQ-001: Some requirement.

            ### Acceptance Criteria

            - [ ] ACC-001: Some criterion.

            ### Scope

            #### Included

            - A thing.

            #### Explicitly Out Of Scope

            - Another thing.

            ### Task List

            ## Progress

            ### Current Status

            Some status text.

            ### Updates

            #### 2026-08-26 09:00:00.000Z - Created

            Initial draft.
            """
        )

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
        text = textwrap.dedent(
            """\
            # Feature: A Widget

            ## Plan

            ### Overview

            Some overview text.

            ### Requirements

            - REQ-001: Some requirement.

            ### Acceptance Criteria

            - [ ] ACC-001: Some criterion.

            ### Scope

            #### Included

            - A thing.

            #### Explicitly Out Of Scope

            - Another thing.

            ### Task List

            #### Phase 0: Scaffolding

            - [x] Task 0.1: Set up

            ## Progress

            ### Current Status

            Some status text.

            ### Updates
            """
        )

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
        text = _MINIMAL_DOC.replace("# Feature: A Widget\n", "Some leading prose.\n\n# Feature: A Widget\n")

        with self.assertRaises(AssertionError):
            parse_feat(text)

    def test_second_h1_raises_assertion_error(self) -> None:
        text = _MINIMAL_DOC + "\n# Second Title\n"

        with self.assertRaises(AssertionError):
            parse_feat(text)


if __name__ == "__main__":
    unittest.main()
