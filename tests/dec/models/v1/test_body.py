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

"""Tests for the `Decision` body model (ACC-001/ACC-002).

Covers the alias acceptance/rejection of every heading class, the computed
`Option.number`/`Option.name` fields, the `DecisionOutcome` composite shape,
the `ProsAndCons`/`Updates` containers' zero-entry rejection, the
`RelatedArtifacts` sub-list independence, `Decision`'s section
optional/misordering behavior, and the duplicate-option-number
after-validator (the `ValidationError` channel).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1.body import (
    AcceptanceCriteria,
    Confirmation,
    Consequences,
    ConsideredOptions,
    Context,
    Decision,
    DecisionDrivers,
    DecisionOutcome,
    Decisions,
    Goals,
    MoreInformation,
    Option,
    ProsAndCons,
    RelatedArtifacts,
    Requirements,
    UpdateEntry,
    Updates,
)
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias

# Every `RelatedArtifacts` sub-list class alongside the exact canonical
# heading text it must -- and only it must -- match. The headings derive
# from the class names via the `AliasType.SPACE_SEPARATED` convention (no
# explicit `@alias`), including the multi-word `AcceptanceCriteria` ->
# "Acceptance Criteria" derivation.
_SUB_LIST_CLASSES_AND_HEADINGS = [
    (Requirements, "Requirements"),
    (Decisions, "Decisions"),
    (Goals, "Goals"),
    (AcceptanceCriteria, "Acceptance Criteria"),
]

# The full reference body (frontmatter stripped), exercising every field:
# all optional sections present, `Decision Outcome` with both H3s,
# `Related Artifacts` with all four sub-lists, `Pros and Cons` with two
# options (number gap), and `Updates` with two entries.
_REFERENCE_TEXT = format_text(
    """\
# Choose a Document Store for the Order Service

## Context and Problem Statement

The order service currently persists orders in a relational database that
was chosen for the reporting needs of 2023. The service now needs fast reads
for the customer dashboard, and the relational store cannot serve that
workload within the latency budget.

## Decision Drivers

- Latency: the dashboard read path must stay under 100 ms at p95.

- Cost: the storage budget for the order service is unchanged.

## Considered Options

We weighed a key-value store, a document store, and keeping the relational
database with a read replica.

## Decision Outcome

We chose the document store because it meets the latency budget with the
lowest operational cost, and the team already runs it for two other
services.

### Consequences

The reporting team loses a single source of truth for orders and must read
from the nightly export instead.

### Confirmation

A two-week load test of the dashboard read path against the document store
confirms the p95 latency target.

## Related Artifacts

### Requirements

- REQ-9687: Order dashboard read latency

- REQ-9688: Order history retention

### Decisions

- DEC-2703: Nightly order export to the data warehouse

### Goals

- GOL-0007: Cost-neutral platform migration

### Acceptance Criteria

- ACC-1234: Dashboard p95 latency under 100 ms

## Pros and Cons

### Option 1: Document Store

Meets the latency budget; lowest operational cost. Cons: no transactional
writes across documents.

### Option 3: Key-Value Store

Even faster reads. Cons: the team has no operational experience with it,
and the migration cost exceeds the budget.

## More Information

The load-test harness configuration is stored in the platform repository
under `load-tests/orders/`.

## Updates

### 2026-08-26 — Created

Initial decision record drafted after the 2026-08-25 platform review.

### 2026-08-27 — Confirmed

Load test passed; the decision is confirmed and the migration task list
opened.
"""
)


def _context() -> Context:
    return Context.from_text(format_text("## Context and Problem Statement\n\nSome context prose.\n"))


def _outcome() -> DecisionOutcome:
    return DecisionOutcome.from_text(format_text("## Decision Outcome\n\nSome outcome prose.\n"))


def _minimal_decision_kwargs() -> dict:
    return {
        "context": _context(),
        "outcome": _outcome(),
    }


class TestDecisionHeadingAlias(unittest.TestCase):
    """`Decision`'s H1 alias is the free-form `.+` REGEX: any non-empty title matches."""

    def test_decision_matches_any_nonempty_h1_text(self) -> None:
        for heading in ("Choose a Document Store", "A Decision", "x"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Decision, heading))

    def test_decision_rejects_empty_h1_text(self) -> None:
        self.assertFalse(match_alias(Decision, ""))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Decision._metadata.get("type"), "heading_open")
        self.assertEqual(Decision._metadata.get("tag"), "h1")


class TestContextHeadingAlias(unittest.TestCase):
    """`Context` pins its heading LITERAL to "Context and Problem Statement"."""

    def test_accepts_canonical_heading(self) -> None:
        self.assertTrue(match_alias(Context, "Context and Problem Statement"))

    def test_rejects_other_wording(self) -> None:
        for heading in ("Context", "context and problem statement", "Context and Problem"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Context, heading))

    def test_metadata_is_heading_open_h2(self) -> None:
        self.assertEqual(Context._metadata.get("type"), "heading_open")
        self.assertEqual(Context._metadata.get("tag"), "h2")


class TestProsAndConsHeadingAlias(unittest.TestCase):
    """`ProsAndCons` pins its heading LITERAL to "Pros and Cons"."""

    def test_accepts_canonical_heading(self) -> None:
        self.assertTrue(match_alias(ProsAndCons, "Pros and Cons"))

    def test_rejects_old_adr_heading(self) -> None:
        self.assertFalse(match_alias(ProsAndCons, "Pros and Cons of the Options"))

    def test_rejects_other_wording(self) -> None:
        for heading in ("Pros And Cons", "pros and cons", "Options"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(ProsAndCons, heading))


class TestOptionHeadingAlias(unittest.TestCase):
    """`Option`'s regex alias requires `Option {N}: {name}` -- title mandatory."""

    def test_accepts_numbered_titled_headings(self) -> None:
        for heading in ("Option 1: Use PostgreSQL", "Option 01: X", "Option 12: A: B", "Option 99: y"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Option, heading))

    def test_rejects_headings_without_title(self) -> None:
        for heading in ("Option 1", "Option 1:", "Option 1: "):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Option, heading))

    def test_rejects_nonnumeric_and_malformed_numbers(self) -> None:
        for heading in ("Option one: X", "Option : X", "Option 1:X", "option 1: x", "Options 1: X"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Option, heading))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(Option._metadata.get("type"), "heading_open")
        self.assertEqual(Option._metadata.get("tag"), "h3")


class TestUpdateEntryHeadingAlias(unittest.TestCase):
    """`UpdateEntry`'s H3 alias is the free-form `.+` REGEX (date-led titles are convention)."""

    def test_update_entry_matches_any_nonempty_h3_text(self) -> None:
        for heading in ("2026-08-26 — Created", "A Note", "x"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_update_entry_rejects_empty_h3_text(self) -> None:
        self.assertFalse(match_alias(UpdateEntry, ""))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(UpdateEntry._metadata.get("type"), "heading_open")
        self.assertEqual(UpdateEntry._metadata.get("tag"), "h3")


class TestSubListHeadingAliases(unittest.TestCase):
    """Each `RelatedArtifacts` sub-list class resolves its own, correct, distinct heading alias.

    Regression-style coverage mirroring GOL's `RelatedArtifacts` sub-list
    alias test: since the four sub-list headings are all short, single- (or
    double-) word title-case names, this confirms each class's
    `SPACE_SEPARATED`-derived alias matches its own exact wording and no
    other sub-list's -- in particular that `AcceptanceCriteria` derives
    "Acceptance Criteria" (space inserted) from its class name.
    """

    def test_each_sub_list_matches_its_own_canonical_heading_and_no_other(self) -> None:
        for cls, heading in _SUB_LIST_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))
                for other_cls, other_heading in _SUB_LIST_CLASSES_AND_HEADINGS:
                    if other_heading == heading:
                        continue
                    self.assertFalse(
                        match_alias(cls, other_heading),
                        f"{cls.__name__} incorrectly matched {other_heading!r}",
                    )

    def test_metadata_is_heading_open_h3_for_every_sub_list(self) -> None:
        for cls, _heading in _SUB_LIST_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls._metadata.get("type"), "heading_open")
                self.assertEqual(cls._metadata.get("tag"), "h3")

    def test_acceptance_criteria_rejects_unsplit_class_name(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriteria, "AcceptanceCriteria"))


class TestImplicitHeadingAliases(unittest.TestCase):
    """The remaining leaf sections derive their heading from their class name (SPACE_SEPARATED).

    No explicit `@alias`: each heading must equal the class name converted
    via `space_separated_name` (e.g. `DecisionDrivers` -> "Decision
    Drivers"), and no leaf must accept a sibling leaf's heading.
    """

    def test_leaf_sections_match_their_canonical_headings(self) -> None:
        for cls, heading in (
            (DecisionDrivers, "Decision Drivers"),
            (ConsideredOptions, "Considered Options"),
            (Consequences, "Consequences"),
            (Confirmation, "Confirmation"),
            (MoreInformation, "More Information"),
            (Updates, "Updates"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))

    def test_leaf_sections_reject_foreign_headings(self) -> None:
        for cls, foreign in (
            (Consequences, "Confirmation"),
            (Confirmation, "Consequences"),
            (DecisionDrivers, "Decision Driver"),
            (ConsideredOptions, "Considered Option"),
            (MoreInformation, "More Information "),
            (Updates, "Update"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(match_alias(cls, foreign))


class TestMandatorySections(unittest.TestCase):
    """`Decision.context`/`Decision.outcome` are mandatory -- absent raises.

    Two distinct channels, mirroring the engine's own split: direct
    construction without a mandatory field raises
    `pydantic.ValidationError` (the field is simply missing from the
    constructor call), while `Decision.from_text` on a markdown document
    that lacks the section raises `AssertionError` (the engine found no
    match for a mandatory field).
    """

    def test_missing_context_raises_validation_error(self) -> None:
        kwargs = _minimal_decision_kwargs()
        del kwargs["context"]

        with self.assertRaises(ValidationError):
            Decision(**kwargs)

    def test_missing_outcome_raises_validation_error(self) -> None:
        kwargs = _minimal_decision_kwargs()
        del kwargs["outcome"]

        with self.assertRaises(ValidationError):
            Decision(**kwargs)

    def test_from_text_missing_context_raises_assertion_error(self) -> None:
        text = format_text("# A Decision\n\n## Decision Outcome\n\nSome outcome prose.\n")

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_from_text_missing_outcome_raises_assertion_error(self) -> None:
        text = format_text("# A Decision\n\n## Context and Problem Statement\n\nSome context prose.\n")

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_from_text_rejects_lead_paragraph_under_h1(self) -> None:
        # DEC has no `statement` lead paragraph under the H1 (unlike GOL):
        # the first field is the mandatory `## Context and Problem Statement`.
        text = format_text(
            "# A Decision\n\nSome lead prose.\n\n## Context and Problem Statement\n\nSome context prose.\n"
            "## Decision Outcome\n\nSome outcome prose.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)


class TestOptionalSectionsIndividuallyOptional(unittest.TestCase):
    """Each optional section is independently optional (ACC-002).

    Covers all six sections absent at once (a freshly created `dec`
    document carries only `context` + `outcome`) and each section present
    one at a time.
    """

    def test_all_six_optional_sections_default_to_none_when_absent(self) -> None:
        sut = Decision(**_minimal_decision_kwargs())

        self.assertIsNone(sut.drivers)
        self.assertIsNone(sut.considered)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.pros_and_cons)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_drivers_present(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["drivers"] = DecisionDrivers.from_text(format_text("## Decision Drivers\n\nSome drivers.\n"))

        sut = Decision(**kwargs)

        self.assertIsNotNone(sut.drivers)
        self.assertIn("Some drivers.", sut.drivers.text)
        self.assertIsNone(sut.considered)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.pros_and_cons)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_considered_present(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["considered"] = ConsideredOptions.from_text(
            format_text("## Considered Options\n\nSome considered options.\n")
        )

        sut = Decision(**kwargs)

        self.assertIsNotNone(sut.considered)
        self.assertIn("Some considered options.", sut.considered.text)
        self.assertIsNone(sut.drivers)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.pros_and_cons)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_related_artifacts_present(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["related_artifacts"] = RelatedArtifacts.from_text(
            format_text("## Related Artifacts\n\n### Decisions\n\n- DEC-0001: Some decision.\n")
        )

        sut = Decision(**kwargs)

        self.assertIsNotNone(sut.related_artifacts)
        self.assertIsNone(sut.drivers)
        self.assertIsNone(sut.considered)
        self.assertIsNone(sut.pros_and_cons)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_pros_and_cons_present(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["pros_and_cons"] = ProsAndCons.from_text(
            format_text("## Pros and Cons\n\n### Option 1: Some option\n\nSome option body.\n")
        )

        sut = Decision(**kwargs)

        self.assertIsNotNone(sut.pros_and_cons)
        self.assertEqual(len(sut.pros_and_cons.options), 1)
        self.assertIsNone(sut.drivers)
        self.assertIsNone(sut.considered)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_more_information_present(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["more_information"] = MoreInformation.from_text(
            format_text("## More Information\n\nSome more information text.\n")
        )

        sut = Decision(**kwargs)

        self.assertIsNotNone(sut.more_information)
        self.assertIn("Some more information text.", sut.more_information.text)
        self.assertIsNone(sut.drivers)
        self.assertIsNone(sut.considered)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.pros_and_cons)
        self.assertIsNone(sut.updates)

    def test_updates_present(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["updates"] = Updates.from_text(
            format_text("## Updates\n\n### 2026-08-26 — Created\n\nSome update text.\n")
        )

        sut = Decision(**kwargs)

        self.assertIsNotNone(sut.updates)
        self.assertEqual(len(sut.updates.updates), 1)
        self.assertIsNone(sut.drivers)
        self.assertIsNone(sut.considered)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.pros_and_cons)
        self.assertIsNone(sut.more_information)


class TestDecisionOutcomeComposite(unittest.TestCase):
    """`DecisionOutcome` requires a lead paragraph; the H3s are optional leaves."""

    def test_parses_lead_plus_both_h3s(self) -> None:
        text = format_text(
            "## Decision Outcome\n\n"
            "Some outcome prose.\n\n"
            "### Consequences\n\n"
            "Some consequence prose.\n\n"
            "### Confirmation\n\n"
            "Some confirmation prose.\n"
        )

        sut = DecisionOutcome.from_text(text)

        self.assertEqual(sut.statement.text, "Some outcome prose.")
        self.assertIsNotNone(sut.consequences)
        self.assertIn("Some consequence prose.", sut.consequences.text)
        self.assertIsNotNone(sut.confirmation)
        self.assertIn("Some confirmation prose.", sut.confirmation.text)
        self.assertEqual(str(sut), text)

    def test_both_h3s_absent(self) -> None:
        sut = DecisionOutcome.from_text(format_text("## Decision Outcome\n\nSome outcome prose.\n"))

        self.assertEqual(sut.statement.text, "Some outcome prose.")
        self.assertIsNone(sut.consequences)
        self.assertIsNone(sut.confirmation)

    def test_missing_lead_paragraph_raises_assertion_error(self) -> None:
        text = format_text("## Decision Outcome\n\n### Consequences\n\nSome consequence prose.\n")

        with self.assertRaises(AssertionError):
            DecisionOutcome.from_text(text)

    def test_bare_list_in_place_of_lead_paragraph_raises_assertion_error(self) -> None:
        text = format_text("## Decision Outcome\n\n- a list item\n")

        with self.assertRaises(AssertionError):
            DecisionOutcome.from_text(text)

    def test_reversed_h3_order_raises_assertion_error(self) -> None:
        text = format_text(
            "## Decision Outcome\n\n"
            "Some outcome prose.\n\n"
            "### Confirmation\n\n"
            "Some confirmation prose.\n\n"
            "### Consequences\n\n"
            "Some consequence prose.\n"
        )

        with self.assertRaises(AssertionError):
            DecisionOutcome.from_text(text)

    def test_unknown_h3_raises_assertion_error(self) -> None:
        text = format_text("## Decision Outcome\n\nSome outcome prose.\n\n### Something Else\n\nSome prose.\n")

        with self.assertRaises(AssertionError):
            DecisionOutcome.from_text(text)

    def test_missing_statement_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            DecisionOutcome()


class TestOptionComputedFields(unittest.TestCase):
    """`Option.number`/`Option.name` are computed from the heading (ACC-002)."""

    def test_parses_number_and_name(self) -> None:
        text = format_text("### Option 1: Some Option Name\n\nSome option body.\n")

        sut = Option.from_text(text)

        self.assertEqual(sut.number, 1)
        self.assertEqual(sut.name, "Some Option Name")
        self.assertEqual(str(sut), text)

    def test_accepts_leading_zero_number(self) -> None:
        sut = Option.from_text(format_text("### Option 01: X\n\nSome option body.\n"))

        self.assertEqual(sut.number, 1)
        self.assertEqual(sut.name, "X")

    def test_accepts_multi_digit_and_gap_numbers(self) -> None:
        sut = Option.from_text(format_text("### Option 12: X\n\nSome option body.\n"))

        self.assertEqual(sut.number, 12)
        self.assertEqual(sut.name, "X")

    def test_keeps_colons_inside_the_name(self) -> None:
        sut = Option.from_text(format_text("### Option 2: A: B\n\nSome option body.\n"))

        self.assertEqual(sut.number, 2)
        self.assertEqual(sut.name, "A: B")

    def test_rejects_heading_without_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Option.from_text(format_text("### Option 1\n\nSome option body.\n"))

    def test_rejects_heading_with_empty_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Option.from_text(format_text("### Option 1:\n\nSome option body.\n"))

    def test_rejects_nonnumeric_number_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Option.from_text(format_text("### Option one: X\n\nSome option body.\n"))


class TestDuplicateOptionNumbers(unittest.TestCase):
    """`Decision` rejects duplicate option numbers (ACC-002, the `ValidationError` channel)."""

    def _pros_and_cons(self, heading_a: str, heading_b: str) -> ProsAndCons:
        return ProsAndCons.from_text(
            format_text(f"## Pros and Cons\n\n### {heading_a}\n\nBody A.\n\n### {heading_b}\n\nBody B.\n")
        )

    def test_duplicate_identical_numbers_raise_validation_error(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["pros_and_cons"] = self._pros_and_cons("Option 1: A", "Option 1: B")

        with self.assertRaises(ValidationError):
            Decision(**kwargs)

    def test_duplicate_via_leading_zero_raise_validation_error(self) -> None:
        # "01" normalizes to the same integer as "1" -- a duplicate.
        kwargs = _minimal_decision_kwargs()
        kwargs["pros_and_cons"] = self._pros_and_cons("Option 1: A", "Option 01: B")

        with self.assertRaises(ValidationError):
            Decision(**kwargs)

    def test_gaps_are_allowed(self) -> None:
        kwargs = _minimal_decision_kwargs()
        kwargs["pros_and_cons"] = self._pros_and_cons("Option 1: A", "Option 3: B")

        sut = Decision(**kwargs)

        self.assertEqual([option.number for option in sut.pros_and_cons.options], [1, 3])

    def test_no_pros_and_cons_is_fine(self) -> None:
        sut = Decision(**_minimal_decision_kwargs())

        self.assertIsNone(sut.pros_and_cons)


class TestProsAndConsZeroOptions(unittest.TestCase):
    """`ProsAndCons` requires >=1 option: H2 present with zero options is a structural error."""

    def test_from_text_with_zero_options_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            ProsAndCons.from_text(format_text("## Pros and Cons\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            ProsAndCons(options=[])


class TestRelatedArtifactsSubListsIndividuallyOptional(unittest.TestCase):
    """Each of the four `RelatedArtifacts` sub-lists is independently optional (ACC-002)."""

    def test_all_four_sub_lists_default_to_none_when_absent(self) -> None:
        sut = RelatedArtifacts()

        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)

    def test_empty_related_artifacts_container_parses(self) -> None:
        sut = RelatedArtifacts.from_text(format_text("## Related Artifacts\n"))

        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)

    def test_requirements_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text("## Related Artifacts\n\n### Requirements\n\n- REQ-0001: Some requirement.\n")
        )

        self.assertIsNotNone(sut.requirements)
        self.assertEqual([item.text for item in sut.requirements.items], ["REQ-0001: Some requirement."])
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)

    def test_decisions_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text("## Related Artifacts\n\n### Decisions\n\n- DEC-0001: Some decision.\n")
        )

        self.assertIsNotNone(sut.decisions)
        self.assertEqual([item.text for item in sut.decisions.items], ["DEC-0001: Some decision."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)

    def test_goals_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(format_text("## Related Artifacts\n\n### Goals\n\n- GOL-0001: Some goal.\n"))

        self.assertIsNotNone(sut.goals)
        self.assertEqual([item.text for item in sut.goals.items], ["GOL-0001: Some goal."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.acceptance_criteria)

    def test_acceptance_criteria_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text("## Related Artifacts\n\n### Acceptance Criteria\n\n- ACC-0001: Some criterion.\n")
        )

        self.assertIsNotNone(sut.acceptance_criteria)
        self.assertEqual([item.text for item in sut.acceptance_criteria.items], ["ACC-0001: Some criterion."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)

    def test_sub_list_present_without_any_bullet_raises_assertion_error(self) -> None:
        for heading in ("Requirements", "Decisions", "Goals", "Acceptance Criteria"):
            with self.subTest(heading=heading):
                with self.assertRaises(AssertionError):
                    RelatedArtifacts.from_text(format_text(f"## Related Artifacts\n\n### {heading}\n"))

    def test_empty_sub_list_items_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Requirements(items=[])
        with self.assertRaises(ValidationError):
            Decisions(items=[])
        with self.assertRaises(ValidationError):
            Goals(items=[])
        with self.assertRaises(ValidationError):
            AcceptanceCriteria(items=[])


class TestUpdatesEntryShape(unittest.TestCase):
    """`Updates`/`UpdateEntry` mirror TSK's `RecentUpdates`/`UpdateEntry` shape."""

    def test_parses_entry_with_content(self) -> None:
        text = format_text("### 2026-08-26 — Created\n\nSome update text.\n")

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.content.text, "Some update text.")
        self.assertEqual(str(sut), text)

    def test_entry_title_is_free_form(self) -> None:
        sut = UpdateEntry.from_text(format_text("### Anything Goes\n\nSome update text.\n"))

        self.assertEqual(sut.content.text, "Some update text.")

    def test_entry_without_lead_paragraph_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            UpdateEntry.from_text(format_text("### 2026-08-26 — Created\n"))

    def test_missing_content_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            UpdateEntry()

    def test_parses_multiple_entries_in_document_order(self) -> None:
        text = format_text(
            "## Updates\n\n"
            "### 2026-08-26 — Created\n\n"
            "First entry text.\n\n"
            "### 2026-08-27 — Confirmed\n\n"
            "Second entry text.\n"
        )

        sut = Updates.from_text(text)

        self.assertEqual(len(sut.updates), 2)
        self.assertEqual(sut.updates[0].content.text, "First entry text.")
        self.assertEqual(sut.updates[1].content.text, "Second entry text.")
        self.assertEqual(str(sut), text)

    def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Updates.from_text(format_text("## Updates\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Updates(updates=[])


class TestDecisionMisordering(unittest.TestCase):
    """H2/H3 sections out of declaration order leave text over: structural failure."""

    def test_updates_before_more_information_raises_assertion_error(self) -> None:
        text = format_text(
            "# A Decision\n\n"
            "## Context and Problem Statement\n\n"
            "Some context prose.\n\n"
            "## Decision Outcome\n\n"
            "Some outcome prose.\n\n"
            "## Updates\n\n"
            "### 2026-08-26 — Created\n\n"
            "Some update text.\n\n"
            "## More Information\n\n"
            "Some more information text.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_related_artifacts_after_pros_and_cons_raises_assertion_error(self) -> None:
        text = format_text(
            "# A Decision\n\n"
            "## Context and Problem Statement\n\n"
            "Some context prose.\n\n"
            "## Decision Outcome\n\n"
            "Some outcome prose.\n\n"
            "## Pros and Cons\n\n"
            "### Option 1: Some option\n\n"
            "Some option body.\n\n"
            "## Related Artifacts\n\n"
            "### Requirements\n\n"
            "- REQ-0001: Some requirement.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_consequences_under_h1_outside_outcome_raises_assertion_error(self) -> None:
        text = format_text(
            "# A Decision\n\n"
            "### Consequences\n\n"
            "Some consequence prose.\n\n"
            "## Context and Problem Statement\n\n"
            "Some context prose.\n\n"
            "## Decision Outcome\n\n"
            "Some outcome prose.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_confirmation_under_h1_outside_outcome_raises_assertion_error(self) -> None:
        text = format_text(
            "# A Decision\n\n"
            "### Confirmation\n\n"
            "Some confirmation prose.\n\n"
            "## Context and Problem Statement\n\n"
            "Some context prose.\n\n"
            "## Decision Outcome\n\n"
            "Some outcome prose.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_unknown_h2_raises_assertion_error(self) -> None:
        text = format_text(
            "# A Decision\n\n"
            "## Context and Problem Statement\n\n"
            "Some context prose.\n\n"
            "## Unknown Section\n\n"
            "Some unknown prose.\n\n"
            "## Decision Outcome\n\n"
            "Some outcome prose.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        text = format_text(
            "# A Decision\n\n"
            "## Context and Problem Statement\n\n"
            "First context prose.\n\n"
            "## Context and Problem Statement\n\n"
            "Second context prose.\n\n"
            "## Decision Outcome\n\n"
            "Some outcome prose.\n"
        )

        with self.assertRaises(AssertionError):
            Decision.from_text(text)


class TestDecisionReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference body parses, exposes its computed fields, and round-trips (ACC-001/ACC-002)."""

    def test_round_trips(self) -> None:
        sut = Decision.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_title(self) -> None:
        sut = Decision.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.text, "Choose a Document Store for the Order Service")

    def test_all_sections_present(self) -> None:
        sut = Decision.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.context)
        self.assertIn("relational store cannot serve", sut.context.text)
        self.assertIsNotNone(sut.drivers)
        self.assertIn("must stay under 100 ms", sut.drivers.text)
        self.assertIsNotNone(sut.considered)
        self.assertIn("key-value store", sut.considered.text)
        self.assertIsNotNone(sut.outcome)
        self.assertIn("We chose the document store", sut.outcome.statement.text)
        self.assertIsNotNone(sut.outcome.consequences)
        self.assertIsNotNone(sut.outcome.confirmation)
        self.assertIsNotNone(sut.more_information)
        self.assertIn("load-test harness configuration", sut.more_information.text)

    def test_related_artifacts_sub_lists_present(self) -> None:
        sut = Decision.from_text(_REFERENCE_TEXT)

        related_artifacts = sut.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertEqual(
            [item.text for item in related_artifacts.requirements.items],
            ["REQ-9687: Order dashboard read latency", "REQ-9688: Order history retention"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.decisions.items],
            ["DEC-2703: Nightly order export to the data warehouse"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.goals.items],
            ["GOL-0007: Cost-neutral platform migration"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.acceptance_criteria.items],
            ["ACC-1234: Dashboard p95 latency under 100 ms"],
        )

    def test_options_number_and_name_computed(self) -> None:
        sut = Decision.from_text(_REFERENCE_TEXT)

        pros_and_cons = sut.pros_and_cons
        self.assertIsNotNone(pros_and_cons)
        self.assertEqual(
            [(option.number, option.name) for option in pros_and_cons.options],
            [(1, "Document Store"), (3, "Key-Value Store")],
        )

    def test_updates_entries(self) -> None:
        sut = Decision.from_text(_REFERENCE_TEXT)

        updates = sut.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 2)
        self.assertEqual(
            updates.updates[0].content.text, "Initial decision record drafted after the 2026-08-25 platform review."
        )
        # `.text` retains embedded line breaks exactly as authored, so the
        # wrapped reference paragraph is checked with `assertIn`; the
        # byte-exact structure is guarded by `test_round_trips` above.
        self.assertIn("Load test passed; the decision is confirmed", updates.updates[1].content.text)
        self.assertIn("migration task list", updates.updates[1].content.text)
