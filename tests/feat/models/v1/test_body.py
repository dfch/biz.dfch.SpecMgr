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

"""Tests for the `Feature` body model (ACC-001).

Covers the alias acceptance/rejection of every heading class, the computed
`RequirementItem.description`/`AcceptanceCriterionItem.criterion_description`/
`Phase.number`/`Phase.title`/`UpdateEntry.timestamp`/`UpdateEntry.title`/
`DecisionEntry.timestamp`/`DecisionEntry.title` fields, the
`Scope`/`Dependencies`/`TaskList`/`Updates`/`DecisionsMade` composite shapes,
`Feature`'s mandatory/optional section behavior, the newest-first ordering
after-validator on `Updates`/`DecisionsMade`, and the full reference
document's round-trip (seeded from
`.specmgr/feat/feat-31-feature/example.md`, see
`tests/feat/models/v1/data/feat_reference.md`).
"""

from __future__ import annotations

import unittest
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.feat.models.v1.body import (
    AcceptanceCriteria,
    AcceptanceCriterionItem,
    Blockers,
    Blocks,
    CurrentStatus,
    DecisionEntry,
    DecisionsMade,
    Dependencies,
    DependsOn,
    DesignNotes,
    ExplicitlyOutOfScope,
    Feature,
    Included,
    MoreInformation,
    Overview,
    Phase,
    Plan,
    Progress,
    RelatedDecisions,
    RelatedPrsCommits,
    RequirementItem,
    Requirements,
    Scope,
    TaskList,
    UpdateEntry,
    Updates,
)
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias

_DATA_DIR = Path(__file__).parent / "data"


def _reference_body_text() -> str:
    text = (_DATA_DIR / "feat_reference.md").read_text(encoding="utf-8")
    post = frontmatter.loads(text)
    result: str = format_text(post.content)
    return result


class TestFeatureHeadingAlias(unittest.TestCase):
    """`Feature`'s H1 alias requires the `"Feature: {title}"` prefix."""

    def test_accepts_titled_headings(self) -> None:
        for heading in ("Feature: A Widget", "Feature: x", "Feature: A: B"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Feature, heading))

    def test_rejects_headings_without_prefix(self) -> None:
        for heading in ("A Widget", "feature: A Widget", "Feature:", "Feature: "):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Feature, heading))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Feature._metadata.get("type"), "heading_open")
        self.assertEqual(Feature._metadata.get("tag"), "h1")


class TestImplicitHeadingAliases(unittest.TestCase):
    """Every implicit-`SPACE_SEPARATED` heading class derives its canonical heading and rejects others."""

    def test_leaf_and_composite_sections_match_their_canonical_headings(self) -> None:
        for cls, heading in (
            (Plan, "Plan"),
            (Overview, "Overview"),
            (Requirements, "Requirements"),
            (AcceptanceCriteria, "Acceptance Criteria"),
            (Scope, "Scope"),
            (Included, "Included"),
            (ExplicitlyOutOfScope, "Explicitly Out Of Scope"),
            (Dependencies, "Dependencies"),
            (DependsOn, "Depends On"),
            (Blocks, "Blocks"),
            (DesignNotes, "Design Notes"),
            (RelatedDecisions, "Related Decisions"),
            (TaskList, "Task List"),
            (Progress, "Progress"),
            (CurrentStatus, "Current Status"),
            (Blockers, "Blockers"),
            (Updates, "Updates"),
            (DecisionsMade, "Decisions Made"),
            (MoreInformation, "More Information"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))

    def test_leaf_and_composite_sections_reject_foreign_headings(self) -> None:
        for cls, foreign in (
            (Overview, "Overviews"),
            (Requirements, "Requirement"),
            (AcceptanceCriteria, "AcceptanceCriteria"),
            (Included, "Includeds"),
            (ExplicitlyOutOfScope, "Explicitly out of scope"),
            (DependsOn, "Depends on"),
            (Blocks, "Block"),
            (DesignNotes, "Design Note"),
            (RelatedDecisions, "Related ADRs"),
            (TaskList, "Tasklist"),
            (CurrentStatus, "Status"),
            (Updates, "Update"),
            (DecisionsMade, "Decisions"),
            (MoreInformation, "More Information "),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(match_alias(cls, foreign))


class TestRelatedPrsCommitsLiteralAlias(unittest.TestCase):
    """`RelatedPrsCommits` pins its heading LITERAL to "Related PRs / Commits" (slash/mixed-case)."""

    def test_accepts_canonical_heading(self) -> None:
        self.assertTrue(match_alias(RelatedPrsCommits, "Related PRs / Commits"))

    def test_rejects_space_separated_derivation(self) -> None:
        # The plain `SPACE_SEPARATED` derivation of the class name ("Related Prs Commits")
        # is deliberately not accepted -- this is why a `LITERAL` override is needed at all.
        self.assertFalse(match_alias(RelatedPrsCommits, "Related Prs Commits"))

    def test_rejects_other_wording(self) -> None:
        for heading in ("Related PRs/Commits", "related prs / commits", "Related PRs"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(RelatedPrsCommits, heading))


class TestPhaseHeadingAlias(unittest.TestCase):
    """`Phase`'s regex alias requires `Phase {N}: {title}` -- title mandatory, unpadded number."""

    def test_accepts_numbered_titled_headings(self) -> None:
        for heading in ("Phase 0: Scaffolding", "Phase 1: Models", "Phase 12: A: B"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Phase, heading))

    def test_rejects_headings_without_title(self) -> None:
        for heading in ("Phase 1", "Phase 1:", "Phase 1: "):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Phase, heading))

    def test_rejects_nonnumeric_and_malformed_numbers(self) -> None:
        for heading in ("Phase one: X", "phase 1: X", "Phases 1: X", "Phase1: X"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Phase, heading))

    def test_metadata_is_heading_open_h4(self) -> None:
        self.assertEqual(Phase._metadata.get("type"), "heading_open")
        self.assertEqual(Phase._metadata.get("tag"), "h4")


class TestUpdateEntryAndDecisionEntryHeadingAlias(unittest.TestCase):
    """`UpdateEntry`/`DecisionEntry` share the identical ISO8601-timestamp `@alias` regex."""

    def test_accepts_well_formed_headings(self) -> None:
        for cls in (UpdateEntry, DecisionEntry):
            for heading in (
                "2026-08-30 16:47:59.981Z - Paused for review",
                "2026-08-30 14:02:11.123+02:00 - Initial scaffolding",
                "2026-08-30 09:15:00.000-05:00 - x",
                "2026-08-30 16:47:59.981Z : Paused for review",
                "2026-08-30 14:02:11.123+02:00 : Initial scaffolding",
                "2026-08-30 09:15:00.000-05:00 : x",
            ):
                with self.subTest(cls=cls.__name__, heading=heading):
                    self.assertTrue(match_alias(cls, heading))

    def test_rejects_malformed_headings(self) -> None:
        for cls in (UpdateEntry, DecisionEntry):
            for heading in (
                "2026-08-30 16:47:59Z - Missing milliseconds",
                "2026-08-30 16:47:59.981 - Missing offset",
                "2026-08-30T16:47:59.981Z - Wrong timestamp separator",
                "Anything Goes",
                "2026-08-30 16:47:59.981Z",
                "2026-08-30 16:47:59.981Z - ",
                "2026-08-30 16:47:59.981Z : ",
            ):
                with self.subTest(cls=cls.__name__, heading=heading):
                    self.assertFalse(match_alias(cls, heading))

    def test_rejects_em_dash_separator(self) -> None:
        """ACC-001: the em-dash separator is rejected -- only ` - `/` : ` are accepted."""
        for cls in (UpdateEntry, DecisionEntry):
            for heading in (
                "2026-08-30 16:47:59.981Z — Paused for review",
                "2026-08-30 14:02:11.123+02:00 — Initial scaffolding",
                "2026-08-30 09:15:00.000-05:00 — x",
            ):
                with self.subTest(cls=cls.__name__, heading=heading):
                    self.assertFalse(match_alias(cls, heading))

    def test_metadata_is_heading_open_h4(self) -> None:
        for cls in (UpdateEntry, DecisionEntry):
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls._metadata.get("type"), "heading_open")
                self.assertEqual(cls._metadata.get("tag"), "h4")


class TestRequirementItem(unittest.TestCase):
    """`RequirementItem.description` re-matches `REQ-\\d{3}: .+` against `.text`."""

    def test_parses_description(self) -> None:
        sut = RequirementItem.from_text(format_text("- REQ-001: The widget must render within 200ms.\n"))

        self.assertEqual(sut.description, "The widget must render within 200ms.")

    def test_malformed_item_raises_assertion_error_on_access(self) -> None:
        sut = RequirementItem.from_text(format_text("- Not a requirement at all.\n"))

        with self.assertRaises(AssertionError):
            _ = sut.description

    def test_requirements_rejects_malformed_item_eagerly(self) -> None:
        text = format_text("### Requirements\n\n- Not a requirement at all.\n")

        with self.assertRaises(ValidationError):
            Requirements.from_text(text)

    def test_requirements_with_zero_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Requirements.from_text(format_text("### Requirements\n"))

    def test_requirements_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Requirements(items=[])


class TestAcceptanceCriterionItem(unittest.TestCase):
    """`AcceptanceCriterionItem.criterion_description` re-matches `ACC-\\d{3}: .+` against `.description`."""

    def test_parses_checked_and_criterion_description(self) -> None:
        sut = AcceptanceCriterionItem.from_text(format_text("- [x] ACC-002: All elements reachable.\n"))

        self.assertTrue(sut.checked)
        self.assertEqual(sut.criterion_description, "All elements reachable.")

    def test_parses_unchecked(self) -> None:
        sut = AcceptanceCriterionItem.from_text(format_text("- [ ] ACC-001: Render under budget.\n"))

        self.assertFalse(sut.checked)
        self.assertEqual(sut.criterion_description, "Render under budget.")

    def test_malformed_item_raises_assertion_error_on_access(self) -> None:
        sut = AcceptanceCriterionItem.from_text(format_text("- [ ] Not an acceptance criterion.\n"))

        with self.assertRaises(AssertionError):
            _ = sut.criterion_description

    def test_acceptance_criteria_rejects_malformed_item_eagerly(self) -> None:
        text = format_text("### Acceptance Criteria\n\n- [ ] Not an acceptance criterion.\n")

        with self.assertRaises(ValidationError):
            AcceptanceCriteria.from_text(text)

    def test_acceptance_criteria_rejects_malformed_marker_eagerly(self) -> None:
        text = format_text("### Acceptance Criteria\n\n- [z] ACC-001: Bad marker.\n")

        with self.assertRaises(ValidationError):
            AcceptanceCriteria.from_text(text)

    def test_acceptance_criteria_with_zero_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            AcceptanceCriteria.from_text(format_text("### Acceptance Criteria\n"))


class TestScopeComposite(unittest.TestCase):
    """`Scope` requires both `Included`/`ExplicitlyOutOfScope`; neither has any own text."""

    def test_parses_both_children(self) -> None:
        text = format_text(
            "### Scope\n\n#### Included\n\n- A thing.\n\n#### Explicitly Out Of Scope\n\n- Another thing.\n"
        )

        sut = Scope.from_text(text)

        self.assertIn("A thing.", sut.included.text)
        self.assertIn("Another thing.", sut.explicitly_out_of_scope.text)
        self.assertEqual(str(sut), text)

    def test_missing_included_raises_assertion_error(self) -> None:
        text = format_text("### Scope\n\n#### Explicitly Out Of Scope\n\n- Another thing.\n")

        with self.assertRaises(AssertionError):
            Scope.from_text(text)

    def test_missing_explicitly_out_of_scope_raises_assertion_error(self) -> None:
        text = format_text("### Scope\n\n#### Included\n\n- A thing.\n")

        with self.assertRaises(AssertionError):
            Scope.from_text(text)


class TestDependenciesComposite(unittest.TestCase):
    """`Dependencies`'s `depends_on`/`blocks` children are each independently optional."""

    def test_both_children_absent(self) -> None:
        sut = Dependencies()

        self.assertIsNone(sut.depends_on)
        self.assertIsNone(sut.blocks)

    def test_depends_on_present(self) -> None:
        sut = Dependencies.from_text(format_text("### Dependencies\n\n#### Depends On\n\n- Some dependency.\n"))

        self.assertIsNotNone(sut.depends_on)
        self.assertIsNone(sut.blocks)

    def test_blocks_present(self) -> None:
        sut = Dependencies.from_text(format_text("### Dependencies\n\n#### Blocks\n\n- Some blocked feature.\n"))

        self.assertIsNone(sut.depends_on)
        self.assertIsNotNone(sut.blocks)


class TestPhaseComputedFields(unittest.TestCase):
    """`Phase.number`/`Phase.title` are computed from the heading."""

    def test_parses_number_and_title(self) -> None:
        text = format_text("#### Phase 1: Implementation\n\n- [ ] Task 1.1: Do the thing\n")

        sut = Phase.from_text(text)

        self.assertEqual(sut.number, 1)
        self.assertEqual(sut.title, "Implementation")
        self.assertEqual(str(sut), text)

    def test_keeps_colons_inside_the_title(self) -> None:
        sut = Phase.from_text(format_text("#### Phase 2: A: B\n\n- [ ] Task 2.1: X\n"))

        self.assertEqual(sut.number, 2)
        self.assertEqual(sut.title, "A: B")

    def test_rejects_heading_without_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Phase.from_text(format_text("#### Phase 1\n\n- [ ] Task 1.1: X\n"))

    def test_with_zero_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Phase.from_text(format_text("#### Phase 1: Implementation\n"))

    def test_rejects_malformed_marker_eagerly(self) -> None:
        text = format_text("#### Phase 1: Implementation\n\n- [z] Task 1.1: Bad marker\n")

        with self.assertRaises(ValidationError):
            Phase.from_text(text)


class TestTaskListComposite(unittest.TestCase):
    """`TaskList.phases` holds >=1 `Phase` entries, in document order, no own text."""

    def test_parses_multiple_phases(self) -> None:
        text = format_text(
            "### Task List\n\n"
            "#### Phase 0: Scaffolding\n\n"
            "- [x] Task 0.1: Set up\n\n"
            "#### Phase 1: Implementation\n\n"
            "- [ ] Task 1.1: Build it\n"
        )

        sut = TaskList.from_text(text)

        self.assertEqual([p.number for p in sut.phases], [0, 1])
        self.assertEqual(str(sut), text)

    def test_with_zero_phases_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            TaskList.from_text(format_text("### Task List\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            TaskList(phases=[])


class TestUpdateEntryAndDecisionEntry(unittest.TestCase):
    """`UpdateEntry`/`DecisionEntry` parse `content`/`timestamp`/`title` identically."""

    def test_update_entry_parses_content_and_computed_fields(self) -> None:
        text = format_text("#### 2026-08-30 16:47:59.981Z - Paused for review\n\nSome update text.\n")

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.content.text, "Some update text.")
        self.assertEqual(sut.timestamp, "2026-08-30 16:47:59.981Z")
        self.assertEqual(sut.title, "Paused for review")
        self.assertEqual(str(sut), text)

    def test_decision_entry_parses_content_and_computed_fields(self) -> None:
        text = format_text("#### 2026-08-30 17:10:00.000Z - Deferred mobile gestures\n\nSome decision text.\n")

        sut = DecisionEntry.from_text(text)

        self.assertEqual(sut.content.text, "Some decision text.")
        self.assertEqual(sut.timestamp, "2026-08-30 17:10:00.000Z")
        self.assertEqual(sut.title, "Deferred mobile gestures")
        self.assertEqual(str(sut), text)

    def test_entry_without_lead_paragraph_raises_assertion_error(self) -> None:
        for cls in (UpdateEntry, DecisionEntry):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(AssertionError):
                    cls.from_text(format_text("#### 2026-08-30 16:47:59.981Z - Paused for review\n"))

    def test_missing_content_raises_validation_error(self) -> None:
        for cls in (UpdateEntry, DecisionEntry):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(ValidationError):
                    cls()


class TestUpdatesOrdering(unittest.TestCase):
    """`Updates` enforces newest-first ordering across its `updates` entries."""

    def test_parses_newest_first_entries(self) -> None:
        text = format_text(
            "### Updates\n\n"
            "#### 2026-08-30 16:47:59.981Z - Paused for review\n\n"
            "First entry text.\n\n"
            "#### 2026-08-30 14:02:11.123+02:00 - Initial scaffolding\n\n"
            "Second entry text.\n"
        )

        sut = Updates.from_text(text)

        self.assertEqual(len(sut.updates), 2)
        self.assertEqual(str(sut), text)

    def test_out_of_order_entries_raise_validation_error(self) -> None:
        text = format_text(
            "### Updates\n\n"
            "#### 2026-08-30 14:02:11.123+02:00 - Initial scaffolding\n\n"
            "First entry text.\n\n"
            "#### 2026-08-30 16:47:59.981Z - Paused for review\n\n"
            "Second entry text.\n"
        )

        with self.assertRaises(ValidationError):
            Updates.from_text(text)

    def test_equal_timestamps_are_allowed(self) -> None:
        text = format_text(
            "### Updates\n\n"
            "#### 2026-08-30 16:47:59.981Z - First\n\n"
            "First entry text.\n\n"
            "#### 2026-08-30 16:47:59.981Z - Second\n\n"
            "Second entry text.\n"
        )

        sut = Updates.from_text(text)

        self.assertEqual(len(sut.updates), 2)

    def test_zero_entries_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Updates.from_text(format_text("### Updates\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Updates(updates=[])

    def test_comment_is_optional(self) -> None:
        text = format_text(
            "### Updates\n\n"
            "<!-- Newest entry first -->\n\n"
            "#### 2026-08-30 16:47:59.981Z - Paused for review\n\n"
            "Some update text.\n"
        )

        sut = Updates.from_text(text)

        self.assertIsNotNone(sut.comment)
        self.assertEqual(len(sut.updates), 1)


class TestDecisionsMadeOrdering(unittest.TestCase):
    """`DecisionsMade` enforces newest-first ordering across its `decisions` entries (mirrors `Updates`)."""

    def test_parses_newest_first_entries(self) -> None:
        text = format_text(
            "### Decisions Made\n\n"
            "#### 2026-08-30 17:10:00.000Z - Deferred mobile gestures\n\n"
            "First entry text.\n\n"
            "#### 2026-08-30 09:15:00.000+02:00 - Chose composite-based library\n\n"
            "Second entry text.\n"
        )

        sut = DecisionsMade.from_text(text)

        self.assertEqual(len(sut.decisions), 2)
        self.assertEqual(str(sut), text)

    def test_out_of_order_entries_raise_validation_error(self) -> None:
        text = format_text(
            "### Decisions Made\n\n"
            "#### 2026-08-30 09:15:00.000+02:00 - Chose composite-based library\n\n"
            "First entry text.\n\n"
            "#### 2026-08-30 17:10:00.000Z - Deferred mobile gestures\n\n"
            "Second entry text.\n"
        )

        with self.assertRaises(ValidationError):
            DecisionsMade.from_text(text)

    def test_zero_entries_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            DecisionsMade.from_text(format_text("### Decisions Made\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            DecisionsMade(decisions=[])


def _minimal_scope() -> Scope:
    return Scope.from_text(
        format_text("### Scope\n\n#### Included\n\n- A thing.\n\n#### Explicitly Out Of Scope\n\n- Another.\n")
    )


def _minimal_plan() -> Plan:
    return Plan.from_text(
        format_text(
            "## Plan\n\n"
            "### Overview\n\n"
            "Some overview.\n\n"
            "### Requirements\n\n"
            "- REQ-001: Some requirement.\n\n"
            "### Acceptance Criteria\n\n"
            "- [ ] ACC-001: Some criterion.\n\n"
            "### Scope\n\n"
            "#### Included\n\n"
            "- A thing.\n\n"
            "#### Explicitly Out Of Scope\n\n"
            "- Another.\n\n"
            "### Task List\n\n"
            "#### Phase 0: Scaffolding\n\n"
            "- [x] Task 0.1: Set up\n"
        )
    )


def _minimal_progress() -> Progress:
    return Progress.from_text(
        format_text(
            "## Progress\n\n"
            "### Current Status\n\n"
            "Some status.\n\n"
            "### Updates\n\n"
            "#### 2026-08-30 16:47:59.981Z - Created\n\n"
            "Some update text.\n"
        )
    )


class TestPlanMandatoryAndOptionalSections(unittest.TestCase):
    """`Plan`'s four optional sections (`dependencies`/`design_notes`/`related_decisions`) default to None."""

    def test_minimal_plan_optional_sections_absent(self) -> None:
        sut = _minimal_plan()

        self.assertIsNone(sut.dependencies)
        self.assertIsNone(sut.design_notes)
        self.assertIsNone(sut.related_decisions)

    def test_missing_overview_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Plan(
                requirements=None,  # type: ignore[arg-type]
                acceptance_criteria=None,  # type: ignore[arg-type]
                scope=_minimal_scope(),
                task_list=None,  # type: ignore[arg-type]
            )

    def test_from_text_missing_task_list_raises_assertion_error(self) -> None:
        text = format_text(
            "## Plan\n\n"
            "### Overview\n\n"
            "Some overview.\n\n"
            "### Requirements\n\n"
            "- REQ-001: Some requirement.\n\n"
            "### Acceptance Criteria\n\n"
            "- [ ] ACC-001: Some criterion.\n\n"
            "### Scope\n\n"
            "#### Included\n\n"
            "- A thing.\n\n"
            "#### Explicitly Out Of Scope\n\n"
            "- Another.\n"
        )

        with self.assertRaises(AssertionError):
            Plan.from_text(text)


class TestProgressMandatoryAndOptionalSections(unittest.TestCase):
    """`Progress`'s four optional sections default to None; `current_status`/`updates` are mandatory."""

    def test_minimal_progress_optional_sections_absent(self) -> None:
        sut = _minimal_progress()

        self.assertIsNone(sut.blockers)
        self.assertIsNone(sut.decisions_made)
        self.assertIsNone(sut.related_prs_commits)
        self.assertIsNone(sut.more_information)

    def test_from_text_missing_updates_raises_assertion_error(self) -> None:
        text = format_text("## Progress\n\n### Current Status\n\nSome status.\n")

        with self.assertRaises(AssertionError):
            Progress.from_text(text)


class TestFeatureHeadingAndSections(unittest.TestCase):
    """`Feature` requires both `plan`/`progress`."""

    def test_parses_minimal_document(self) -> None:
        text = format_text(f"# Feature: A Widget\n\n{_minimal_plan()}\n\n{_minimal_progress()}\n")

        sut = Feature.from_text(text)

        self.assertEqual(sut.text, "Feature: A Widget")
        self.assertEqual(str(sut), text)

    def test_missing_plan_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Feature(progress=_minimal_progress())  # type: ignore[call-arg]

    def test_missing_progress_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Feature(plan=_minimal_plan())  # type: ignore[call-arg]

    def test_from_text_missing_progress_raises_assertion_error(self) -> None:
        text = format_text(f"# Feature: A Widget\n\n{_minimal_plan()}\n")

        with self.assertRaises(AssertionError):
            Feature.from_text(text)


class TestFeatureReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference body (seeded from `example.md`) parses, exposes computed fields, and round-trips."""

    def test_round_trips(self) -> None:
        text = _reference_body_text()

        sut = Feature.from_text(text)

        self.assertEqual(str(sut), text)

    def test_title(self) -> None:
        sut = Feature.from_text(_reference_body_text())

        self.assertEqual(sut.text, "Feature: Example Widget")

    def test_requirements_at_least_one(self) -> None:
        sut = Feature.from_text(_reference_body_text())

        self.assertGreaterEqual(len(sut.plan.requirements.items), 1)

    def test_task_list_has_at_least_two_phases_each_with_at_least_one_item(self) -> None:
        sut = Feature.from_text(_reference_body_text())

        phases = sut.plan.task_list.phases
        self.assertGreaterEqual(len(phases), 2)
        for phase in phases:
            with self.subTest(phase=phase.number):
                self.assertGreaterEqual(len(phase.items), 1)

    def test_updates_has_at_least_two_entries_newest_first(self) -> None:
        sut = Feature.from_text(_reference_body_text())

        updates = sut.progress.updates.updates
        self.assertGreaterEqual(len(updates), 2)
        self.assertGreaterEqual(updates[0].timestamp, updates[1].timestamp)

    def test_decisions_made_has_at_least_two_entries_newest_first(self) -> None:
        sut = Feature.from_text(_reference_body_text())

        decisions_made = sut.progress.decisions_made
        self.assertIsNotNone(decisions_made)
        self.assertGreaterEqual(len(decisions_made.decisions), 2)
        self.assertGreaterEqual(decisions_made.decisions[0].timestamp, decisions_made.decisions[1].timestamp)

    def test_all_optional_sections_present(self) -> None:
        sut = Feature.from_text(_reference_body_text())

        self.assertIsNotNone(sut.plan.dependencies)
        self.assertIsNotNone(sut.plan.design_notes)
        self.assertIsNotNone(sut.plan.related_decisions)
        self.assertIsNotNone(sut.progress.blockers)
        self.assertIsNotNone(sut.progress.decisions_made)
        self.assertIsNotNone(sut.progress.related_prs_commits)
        self.assertIsNotNone(sut.progress.more_information)


if __name__ == "__main__":
    unittest.main()
