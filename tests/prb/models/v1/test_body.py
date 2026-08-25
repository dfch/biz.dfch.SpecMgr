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

"""Tests for the `Prb`/`CurrentState`/`Question{N}` body models (ACC-002).

Covers the reference document from
`.specmgr/feat/feat-16-problem-statement/prb_reference.md` (all 7 5W2H
questions answered, `Impact`/`References`/`More Information` all present),
plus explicit coverage of each mandatory-vs-optional field combination:
each of the 7 questions individually absent/present, and
`Impact`/`References`/`More Information` absent/present.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias
from biz.dfch.specmgr.prb.models.v1.body import (
    CurrentState,
    FutureState,
    Gap,
    Impact,
    MoreInformation,
    Prb,
    Question1,
    Question2,
    Question3,
    Question4,
    Question5,
    Question6,
    Question7,
    References,
    Summary,
)

# Every `Question{N}` class alongside the exact canonical heading text it
# must -- and only it must -- match (verbatim from the iSixSigma 5W2H list,
# see the feature README's Design Notes).
_QUESTION_CLASSES_AND_HEADINGS = [
    (Question1, "What Is the Problem?"),
    (Question2, "Why Is It a Problem?"),
    (Question3, "Where Is the Problem Observed?"),
    (Question4, "Who Is Impacted?"),
    (Question5, "When Was the Problem First Observed?"),
    (Question6, "How Is the Problem Observed?"),
    (Question7, "How Often Is the Problem Observed?"),
]

# The reference document's body (`prb_reference.md`, frontmatter stripped),
# exercising every field: all 7 5W2H questions answered, `Impact`/
# `References`/`More Information` all present.
_REFERENCE_TEXT = format_text(
    """\
# Widget Registry Migration Rollback Failures

<!-- Captured during the platform team's weekly incident review. -->

## Current State

### Summary

Widget migrations from WidgetRegistryV1 to WidgetRegistryV2 occasionally
leave a widget in a half-migrated state when the migration tool fails
partway through, because the tool has no rollback step. This has happened
three times in the last two weeks, each time requiring a platform engineer
to manually restore the widget's registration by hand from a backup.

### What Is the Problem?

The migration tool does not roll back a widget's registration if any step
of the migration to WidgetRegistryV2 fails, leaving the widget registered
in neither registry cleanly.

### Why Is It a Problem?

A half-migrated widget is invisible to both registries' health checks,
which silently drops traffic for that widget until an engineer notices and
intervenes manually.

### Where Is the Problem Observed?

In the `widget-migrate` CLI tool's `migrate_one_widget` step, specifically
when the WidgetRegistryV2 write succeeds but the subsequent
WidgetRegistryV1 de-registration call fails.

### Who Is Impacted?

The on-call platform engineer (who has to perform the manual restore), and
any consumer service that depends on the affected widget's registration
during the outage window.

### When Was the Problem First Observed?

First observed on 2026-08-11, during the initial production rollout of the
migration tool.

### How Is the Problem Observed?

Via a PagerDuty alert firing on the "widget registration missing" health
check, followed by a platform engineer confirming the widget is absent from
both WidgetRegistryV1 and WidgetRegistryV2 simultaneously.

### How Often Is the Problem Observed?

Three times in the two weeks since rollout, roughly once every four to five
migration batches.

## Gap

The migration tool currently completes a partial migration with no
rollback step in 100% of cases where the de-registration call fails
(3 of roughly 60 widgets migrated so far); the expected behavior is zero
widgets left in a half-migrated state, regardless of where a migration
step fails.

## Impact

Each incident costs the on-call engineer 30-45 minutes of manual recovery
time and causes a brief registration outage for the affected widget,
visible to at least one downstream consumer service in every occurrence so
far.

## Future State

The migration tool automatically rolls back a widget to its original
WidgetRegistryV1 registration if any step of its migration to
WidgetRegistryV2 fails, so no widget is ever left in an inconsistent,
half-migrated state, and no manual recovery is required.

## References

- `tsk_reference.md`: "Migrate Widgets to the New Registry" task list.
- `qa_reference.md`: the original requirements-elicitation interview,
  which already anticipated this failure mode in its "Functional
  Suitability" section.

## More Information

This problem statement was drafted after the third rollback incident, once
a clear pattern across all three occurrences had emerged. No root cause
analysis is included here by design; a separate root-cause investigation is
tracked internally and will be linked from `References` once complete.
"""
)


def _minimal_current_state() -> CurrentState:
    text = format_text(
        """\
## Current State

### Summary

A short placeholder summary.
"""
    )
    return CurrentState.from_text(text)


def _minimal_prb_kwargs() -> dict:
    return {
        "current_state": _minimal_current_state(),
        "gap": Gap.from_text(format_text("## Gap\n\nSome gap text.\n")),
        "future_state": FutureState.from_text(format_text("## Future State\n\nSome future state text.\n")),
    }


class TestQuestionHeadingAliases(unittest.TestCase):
    """Each `Question{N}` class resolves its own, correct, distinct heading alias.

    Regression-style coverage mirroring QA v2's `_QaCategory`-shaped alias
    test: since the 7 5W2H question headings all follow a similar shape
    ("... the Problem ...?"), this confirms each class's explicit `@alias`
    matches its own exact wording and no other question's.
    """

    def test_each_question_matches_its_own_canonical_heading_and_no_other(self) -> None:
        for cls, heading in _QUESTION_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))
                for other_cls, other_heading in _QUESTION_CLASSES_AND_HEADINGS:
                    if other_heading == heading:
                        continue
                    self.assertFalse(
                        match_alias(cls, other_heading),
                        f"{cls.__name__} incorrectly matched {other_heading!r}",
                    )

    def test_metadata_is_heading_open_h3_for_every_question(self) -> None:
        for cls, _heading in _QUESTION_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls._metadata.get("type"), "heading_open")
                self.assertEqual(cls._metadata.get("tag"), "h3")


class TestSummaryMandatory(unittest.TestCase):
    """`CurrentState.summary` is mandatory -- absent raises, present parses."""

    def test_missing_summary_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            CurrentState()

    def test_present_summary_parses(self) -> None:
        sut = _minimal_current_state()

        self.assertIn("A short placeholder summary.", sut.summary.text)


class TestCurrentStateQuestionsIndividuallyOptional(unittest.TestCase):
    """Each of the 7 5W2H questions is independently optional (ACC-002).

    Covers each question absent (direct construction defaults to `None`)
    and each question present (direct construction with a value), one
    question at a time, matching the plan's explicit coverage requirement.
    """

    def _summary(self) -> Summary:
        return Summary.from_text(format_text("### Summary\n\nA short placeholder summary.\n"))

    def test_all_seven_questions_default_to_none_when_absent(self) -> None:
        sut = CurrentState(summary=self._summary())

        self.assertIsNone(sut.question_1)
        self.assertIsNone(sut.question_2)
        self.assertIsNone(sut.question_3)
        self.assertIsNone(sut.question_4)
        self.assertIsNone(sut.question_5)
        self.assertIsNone(sut.question_6)
        self.assertIsNone(sut.question_7)

    def test_question_1_present(self) -> None:
        text = format_text(
            "## Current State\n\n### Summary\n\nA summary.\n\n### What Is the Problem?\n\nSome answer.\n"
        )
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_1)
        self.assertIn("Some answer.", sut.question_1.text)
        self.assertIsNone(sut.question_2)

    def test_question_2_present(self) -> None:
        text = format_text(
            "## Current State\n\n### Summary\n\nA summary.\n\n### Why Is It a Problem?\n\nSome answer.\n"
        )
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_2)
        self.assertIn("Some answer.", sut.question_2.text)
        self.assertIsNone(sut.question_1)

    def test_question_3_present(self) -> None:
        text = format_text(
            "## Current State\n\n### Summary\n\nA summary.\n\n### Where Is the Problem Observed?\n\nSome answer.\n"
        )
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_3)
        self.assertIn("Some answer.", sut.question_3.text)

    def test_question_4_present(self) -> None:
        text = format_text("## Current State\n\n### Summary\n\nA summary.\n\n### Who Is Impacted?\n\nSome answer.\n")
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_4)
        self.assertIn("Some answer.", sut.question_4.text)

    def test_question_5_present(self) -> None:
        text = format_text(
            "## Current State\n\n### Summary\n\nA summary.\n\n"
            "### When Was the Problem First Observed?\n\nSome answer.\n"
        )
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_5)
        self.assertIn("Some answer.", sut.question_5.text)

    def test_question_6_present(self) -> None:
        text = format_text(
            "## Current State\n\n### Summary\n\nA summary.\n\n### How Is the Problem Observed?\n\nSome answer.\n"
        )
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_6)
        self.assertIn("Some answer.", sut.question_6.text)

    def test_question_7_present(self) -> None:
        text = format_text(
            "## Current State\n\n### Summary\n\nA summary.\n\n### How Often Is the Problem Observed?\n\nSome answer.\n"
        )
        sut = CurrentState.from_text(text)

        self.assertIsNotNone(sut.question_7)
        self.assertIn("Some answer.", sut.question_7.text)


class TestGapFutureStateMandatory(unittest.TestCase):
    """`Prb.gap`/`Prb.future_state` are mandatory -- absent raises."""

    def test_missing_gap_raises_validation_error(self) -> None:
        kwargs = _minimal_prb_kwargs()
        del kwargs["gap"]

        with self.assertRaises(ValidationError):
            Prb(**kwargs)

    def test_missing_future_state_raises_validation_error(self) -> None:
        kwargs = _minimal_prb_kwargs()
        del kwargs["future_state"]

        with self.assertRaises(ValidationError):
            Prb(**kwargs)

    def test_missing_current_state_raises_validation_error(self) -> None:
        kwargs = _minimal_prb_kwargs()
        del kwargs["current_state"]

        with self.assertRaises(ValidationError):
            Prb(**kwargs)


class TestImpactReferencesMoreInformationOptional(unittest.TestCase):
    """`Prb.impact`/`references`/`more_information` are independently optional (ACC-002)."""

    def test_all_three_default_to_none_when_absent(self) -> None:
        sut = Prb(**_minimal_prb_kwargs())

        self.assertIsNone(sut.impact)
        self.assertIsNone(sut.references)
        self.assertIsNone(sut.more_information)

    def test_impact_present(self) -> None:
        kwargs = _minimal_prb_kwargs()
        kwargs["impact"] = Impact.from_text(format_text("## Impact\n\nSome impact text.\n"))

        sut = Prb(**kwargs)

        self.assertIsNotNone(sut.impact)
        self.assertIsNone(sut.references)
        self.assertIsNone(sut.more_information)

    def test_references_present(self) -> None:
        kwargs = _minimal_prb_kwargs()
        kwargs["references"] = References.from_text(format_text("## References\n\nSome reference text.\n"))

        sut = Prb(**kwargs)

        self.assertIsNone(sut.impact)
        self.assertIsNotNone(sut.references)
        self.assertIsNone(sut.more_information)

    def test_more_information_present(self) -> None:
        kwargs = _minimal_prb_kwargs()
        kwargs["more_information"] = MoreInformation.from_text(
            format_text("## More Information\n\nSome more information text.\n")
        )

        sut = Prb(**kwargs)

        self.assertIsNone(sut.impact)
        self.assertIsNone(sut.references)
        self.assertIsNotNone(sut.more_information)


class TestPrbReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference document (`prb_reference.md`'s body) parses and round-trips (ACC-001/ACC-002)."""

    def test_round_trips(self) -> None:
        sut = Prb.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_title_and_comment(self) -> None:
        sut = Prb.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.text, "Widget Registry Migration Rollback Failures")
        self.assertIsNotNone(sut.comment)
        self.assertIn("Captured during the platform team's weekly incident review.", sut.comment.text)

    def test_all_seven_questions_are_present(self) -> None:
        sut = Prb.from_text(_REFERENCE_TEXT)

        cs = sut.current_state
        self.assertIsNotNone(cs.summary)
        self.assertIsNotNone(cs.question_1)
        self.assertIsNotNone(cs.question_2)
        self.assertIsNotNone(cs.question_3)
        self.assertIsNotNone(cs.question_4)
        self.assertIsNotNone(cs.question_5)
        self.assertIsNotNone(cs.question_6)
        self.assertIsNotNone(cs.question_7)

    def test_gap_impact_future_state_references_more_information_present(self) -> None:
        sut = Prb.from_text(_REFERENCE_TEXT)

        self.assertIn("The migration tool currently completes a partial migration", sut.gap.text)
        self.assertIsNotNone(sut.impact)
        self.assertIn("Each incident costs the on-call engineer", sut.impact.text)
        self.assertIn("The migration tool automatically rolls back a widget", sut.future_state.text)
        self.assertIsNotNone(sut.references)
        self.assertIn("Migrate Widgets to the New Registry", sut.references.text)
        self.assertIsNotNone(sut.more_information)
        self.assertIn("This problem statement was drafted", sut.more_information.text)


if __name__ == "__main__":
    unittest.main()
