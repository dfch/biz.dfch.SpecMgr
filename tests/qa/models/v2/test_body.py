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

"""Tests for the QA v2 `Qa`/`General`/`_QaCategory`-shaped body models (ACC-002).

Covers the reference document from the feature README's Design Notes: a
full document with `## Elicitation Context` before `## Functional
Suitability`, one category (`Functional Suitability`) with several adjacent
Q&A pairs (including a multi-paragraph answer embedding an ordered list),
and several categories with zero pairs (`Performance Efficiency`,
`Compatibility`, ...). Also verifies the 9-category class-sharing decision
made in v1 and carried over to v2: each of the 10 `_QaCategory`-shaped
classes shares a private `_QaCategory` intermediate base, and this file
explicitly verifies each still resolves its own, distinct heading alias
correctly (not an accidentally-shared one).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias
from biz.dfch.specmgr.qa.models.v2.body import (
    Compatibility,
    ElicitationContext,
    Flexibility,
    FunctionalSuitability,
    General,
    InteractionCapability,
    Introduction,
    Maintainability,
    MoreInformation,
    PerformanceEfficiency,
    Qa,
    RawRequirements,
    Reliability,
    Safety,
    Security,
)
from biz.dfch.specmgr.qa.models.v2.question_answer import QaQuestionAnswer

# Every `_QaCategory`-shaped class alongside the exact canonical heading text
# it must -- and only it must -- match. `ElicitationContext` is included
# here even though it is not one of the 9 ISO/IEC 25010:2023 characteristics
# (see the feature README's Design Notes).
_CATEGORY_CLASSES_AND_HEADINGS = [
    (ElicitationContext, "Elicitation Context"),
    (FunctionalSuitability, "Functional Suitability"),
    (PerformanceEfficiency, "Performance Efficiency"),
    (Compatibility, "Compatibility"),
    (InteractionCapability, "Interaction Capability"),
    (Reliability, "Reliability"),
    (Security, "Security"),
    (Maintainability, "Maintainability"),
    (Flexibility, "Flexibility"),
    (Safety, "Safety"),
]

# The reference example from the feature README's Design Notes, adapted
# verbatim: `## Elicitation Context` before `## Functional Suitability`,
# `Functional Suitability` with several adjacent Q&A pairs (including a
# multi-paragraph answer with an embedded ordered list), and every other
# category left empty (zero pairs).
_REFERENCE_TEXT = format_text(
    """\
# Widget Frobnicator Q&A

## General

### Introduction

<!-- filled in during the kickoff interview -->

This document captures the requirements interview for the Widget Frobnicator.

### Raw Requirements

The frobnicator must handle at least 500 widgets/minute.

## Elicitation Context

> Who are the primary stakeholders for this system?

Product management and the on-call SRE team.

## Functional Suitability

<!-- comment belongs to the question right after it -->

> What happens when the input queue is empty?

The frobnicator idles and polls every 100ms.

That polling interval is configurable via `poll_interval_ms`.

> How should malformed widgets be handled?

Malformed widgets are rejected and logged. The rejection flow is:

1. Validate the widget schema.
2. Log the failure with the widget's id.
3. Increment the `rejected_total` counter.

No retry is attempted for malformed input.

## Performance Efficiency

## Compatibility

## Interaction Capability

## Reliability

## Security

## Maintainability

## Flexibility

## Safety

## More Information

See the original ticket for background on throughput targets.
"""
)


def _minimal_general() -> General:
    text = format_text(
        """\
## General

### Introduction

Some intro text.

### Raw Requirements

Some raw requirements text.
"""
    )
    return General.from_text(text)


class TestQaCategoryAliasesAreDistinct(unittest.TestCase):
    """Each of the 10 `_QaCategory`-shaped classes resolves its own, correct, distinct heading alias.

    Regression test for the shared-`_QaCategory`-base decision (carried over
    from v1): since all 10 classes inherit from the same private
    intermediate base, this confirms `match_alias`'s
    `AliasType.SPACE_SEPARATED` default keys off each final subclass's own
    `__name__`, not the shared base's, so no two categories accidentally
    match the same (or the wrong) heading text.
    """

    def test_each_category_matches_its_own_canonical_heading_and_no_other(self) -> None:
        for cls, heading in _CATEGORY_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))
                for other_cls, other_heading in _CATEGORY_CLASSES_AND_HEADINGS:
                    if other_heading == heading:
                        continue
                    self.assertFalse(
                        match_alias(cls, other_heading),
                        f"{cls.__name__} incorrectly matched {other_heading!r}",
                    )

    def test_metadata_is_heading_open_h2_for_every_category(self) -> None:
        for cls, _heading in _CATEGORY_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls._metadata.get("type"), "heading_open")
                self.assertEqual(cls._metadata.get("tag"), "h2")

    def test_category_parses_and_round_trips_when_empty(self) -> None:
        for cls, heading in _CATEGORY_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"## {heading}\n")
                sut = cls.from_text(text)
                self.assertIsNone(sut.questions)
                self.assertEqual(str(sut), text)


class TestQaCategoryQuestionsOptional(unittest.TestCase):
    """`_QaCategory.questions` is optional -- both present and absent are valid (ACC-002)."""

    def test_direct_construction_without_questions_defaults_to_none(self) -> None:
        sut = Compatibility()

        self.assertIsNone(sut.questions)

    def test_direct_construction_with_questions(self) -> None:
        pair = QaQuestionAnswer()

        sut = FunctionalSuitability(questions=[pair])

        self.assertIsNotNone(sut.questions)
        self.assertEqual(len(sut.questions), 1)


class TestGeneralIntroductionRawRequirements(unittest.TestCase):
    """`General`/`Introduction`/`RawRequirements` parse and round-trip (ACC-002)."""

    def test_parses_and_round_trips(self) -> None:
        sut = _minimal_general()

        self.assertIsNone(sut.comment)
        self.assertEqual(sut.introduction.body[0].text, "Some intro text.")
        self.assertIn("Some raw requirements text.", sut.raw_requirements.text)

    def test_introduction_and_raw_requirements_keep_implicit_alias_derivation(self) -> None:
        """No explicit `@alias` on `Introduction`/`RawRequirements` -- per v1's own established precedent."""
        self.assertTrue(match_alias(Introduction, "Introduction"))
        self.assertTrue(match_alias(RawRequirements, "Raw Requirements"))


class TestQaRequiredVsOptionalFields(unittest.TestCase):
    """`Qa`'s `general`/`elicitation_context`/9 `_QaCategory` fields are mandatory; `more_information` is optional."""

    def _build_minimal_kwargs(self) -> dict:
        return {
            "general": _minimal_general(),
            "elicitation_context": ElicitationContext(),
            "functional_suitability": FunctionalSuitability(),
            "performance_efficiency": PerformanceEfficiency(),
            "compatibility": Compatibility(),
            "interaction_capability": InteractionCapability(),
            "reliability": Reliability(),
            "security": Security(),
            "maintainability": Maintainability(),
            "flexibility": Flexibility(),
            "safety": Safety(),
        }

    def test_construction_without_more_information_defaults_to_none(self) -> None:
        sut = Qa(**self._build_minimal_kwargs())

        self.assertIsNone(sut.more_information)

    def test_construction_with_more_information(self) -> None:
        kwargs = self._build_minimal_kwargs()
        kwargs["more_information"] = MoreInformation()

        sut = Qa(**kwargs)

        self.assertIsNotNone(sut.more_information)

    def test_missing_mandatory_general_raises_validation_error(self) -> None:
        kwargs = self._build_minimal_kwargs()
        del kwargs["general"]

        with self.assertRaises(ValidationError):
            Qa(**kwargs)

    def test_missing_mandatory_elicitation_context_raises_validation_error(self) -> None:
        kwargs = self._build_minimal_kwargs()
        del kwargs["elicitation_context"]

        with self.assertRaises(ValidationError):
            Qa(**kwargs)

    def test_missing_mandatory_category_raises_validation_error(self) -> None:
        kwargs = self._build_minimal_kwargs()
        del kwargs["safety"]

        with self.assertRaises(ValidationError):
            Qa(**kwargs)


class TestQaReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference document (README Design Notes) parses and round-trips (ACC-002)."""

    def test_round_trips(self) -> None:
        sut = Qa.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_all_ten_category_shaped_fields_are_always_present(self) -> None:
        sut = Qa.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.elicitation_context)
        self.assertIsNotNone(sut.functional_suitability)
        self.assertIsNotNone(sut.performance_efficiency)
        self.assertIsNotNone(sut.compatibility)
        self.assertIsNotNone(sut.interaction_capability)
        self.assertIsNotNone(sut.reliability)
        self.assertIsNotNone(sut.security)
        self.assertIsNotNone(sut.maintainability)
        self.assertIsNotNone(sut.flexibility)
        self.assertIsNotNone(sut.safety)

    def test_elicitation_context_has_at_least_one_question(self) -> None:
        sut = Qa.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.elicitation_context.questions)
        self.assertGreaterEqual(len(sut.elicitation_context.questions), 1)
        pair = sut.elicitation_context.questions[0]
        self.assertEqual(pair.question.text, "Who are the primary stakeholders for this system?")
        self.assertEqual(pair.answer.text.strip(), "Product management and the on-call SRE team.")

    def test_categories_with_zero_pairs_have_questions_none(self) -> None:
        sut = Qa.from_text(_REFERENCE_TEXT)

        self.assertIsNone(sut.performance_efficiency.questions)
        self.assertIsNone(sut.compatibility.questions)
        self.assertIsNone(sut.interaction_capability.questions)
        self.assertIsNone(sut.reliability.questions)
        self.assertIsNone(sut.security.questions)
        self.assertIsNone(sut.maintainability.questions)
        self.assertIsNone(sut.flexibility.questions)
        self.assertIsNone(sut.safety.questions)

    def test_functional_suitability_has_two_adjacent_pairs(self) -> None:
        sut = Qa.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.functional_suitability.questions)
        self.assertEqual(len(sut.functional_suitability.questions), 2)

        first, second = sut.functional_suitability.questions

        self.assertIsNotNone(first.comment)
        self.assertEqual(first.question.text, "What happens when the input queue is empty?")
        self.assertIn("The frobnicator idles and polls every 100ms.", first.answer.text)
        self.assertIn("poll_interval_ms", first.answer.text)

        self.assertIsNone(second.comment)
        self.assertEqual(second.question.text, "How should malformed widgets be handled?")
        self.assertIn("Validate the widget schema.", second.answer.text)
        self.assertIn("Log the failure with the widget's id.", second.answer.text)
        self.assertIn("Increment the `rejected_total` counter.", second.answer.text)
        self.assertIn("No retry is attempted for malformed input.", second.answer.text)

    def test_more_information_is_present_and_captures_free_form_text(self) -> None:
        sut = Qa.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.more_information)
        self.assertIn("See the original ticket for background on throughput targets.", sut.more_information.text)


if __name__ == "__main__":
    unittest.main()
