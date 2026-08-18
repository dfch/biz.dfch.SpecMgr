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

"""Tests for the `Qa`/`General`/`<QaCategory>`/`QaSection`/`Requirement`/`QaAnswer` body models.

Covers ACC-003 (required vs. optional field validation) and the 9-category
class-sharing decision made during this phase (Task 3.1): each of the 9
`<QaCategory>` classes shares a private `_QaCategory` intermediate base, and
this file explicitly verifies each still resolves its own, distinct heading
alias correctly (not an accidentally-shared one).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias
from biz.dfch.specmgr.models.md.markdown_block_quote import MarkdownBlockQuote
from biz.dfch.specmgr.qa.models.v1.body import (
    Compatibility,
    Flexibility,
    FunctionalSuitability,
    General,
    InteractionCapability,
    Introduction,
    Maintainability,
    MoreInformation,
    PerformanceEfficiency,
    Qa,
    QaAnswer,
    QaSection,
    RawRequirements,
    Reliability,
    Requirement,
    Safety,
    Security,
)

# Every `<QaCategory>` class alongside the exact canonical ISO/IEC 25010:2023
# heading text it must -- and only it must -- match.
_CATEGORY_CLASSES_AND_HEADINGS = [
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
    """Each of the 9 `<QaCategory>` classes resolves its own, correct, distinct heading alias.

    Regression test for the shared-`_QaCategory`-base decision (Task 3.1):
    since all 9 classes inherit from the same private intermediate base,
    this confirms `match_alias`'s `AliasType.SPACE_SEPARATED` default keys
    off each final subclass's own `__name__`, not the shared base's, so no
    two categories accidentally match the same (or the wrong) heading text.
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
                self.assertIsNone(sut.items)
                self.assertEqual(str(sut), text)


class TestQaCategoryItemsOptional(unittest.TestCase):
    """`<QaCategory>.items` is optional -- both present and absent are valid (ACC-003)."""

    def test_direct_construction_without_items_defaults_to_none(self) -> None:
        sut = Compatibility()

        self.assertIsNone(sut.items)

    def test_direct_construction_with_items(self) -> None:
        section = QaSection()

        sut = FunctionalSuitability(items=[section])

        self.assertIsNotNone(sut.items)
        self.assertEqual(len(sut.items), 1)


class TestQaSectionAllFieldsOptional(unittest.TestCase):
    """`QaSection`'s `comment`/`requirement`/`question`/`answer` are all optional (ACC-003)."""

    def test_direct_construction_with_no_fields_set(self) -> None:
        sut = QaSection()

        self.assertIsNone(sut.comment)
        self.assertIsNone(sut.requirement)
        self.assertIsNone(sut.question)
        self.assertIsNone(sut.answer)

    def test_free_form_heading_accepts_arbitrary_title(self) -> None:
        text = format_text(
            """\
### Anything Goes Here?

Some answer prose.
"""
        )

        sut = QaSection.from_text(text)

        self.assertEqual(sut.text, "Anything Goes Here?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "Some answer prose.")

    def test_parses_with_only_question_and_answer(self) -> None:
        text = format_text(
            """\
### How should X be handled?

> Should X halt or continue?

X should continue with a warning.
"""
        )

        sut = QaSection.from_text(text)

        self.assertIsNone(sut.comment)
        self.assertIsNone(sut.requirement)
        self.assertIsNotNone(sut.question)
        self.assertEqual(sut.question.text, "Should X halt or continue?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "X should continue with a warning.")
        self.assertEqual(str(sut), text)


class TestRequirementEndMarkerWiring(unittest.TestCase):
    """`Requirement` declares `@markdown(end_marker=MarkdownBlockQuote)`, merged into `MarkdownSection4`'s metadata.

    Regression test for Task 1.3/1.4's mechanism actually being wired up for
    `qa`'s own `Requirement` class (not just Phase 1's own synthetic
    fixture).
    """

    def test_end_marker_is_markdown_block_quote(self) -> None:
        self.assertIs(Requirement._metadata.get("end_marker"), MarkdownBlockQuote)

    def test_inherited_type_and_tag_are_preserved(self) -> None:
        """`@markdown(end_marker=...)` merges into `MarkdownSection4`'s inherited `type`/`tag`, not replacing them."""
        self.assertEqual(Requirement._metadata.get("type"), "heading_open")
        self.assertEqual(Requirement._metadata.get("tag"), "h4")

    def test_fixed_heading_text_is_requirement(self) -> None:
        """`Requirement`'s heading is fixed (`"Requirement"`), not free-form, per `qa_reference.md`."""
        self.assertTrue(match_alias(Requirement, "Requirement"))
        self.assertFalse(match_alias(Requirement, "Something Else"))

    def test_does_not_absorb_a_following_depth_zero_block_quote(self) -> None:
        text = format_text(
            """\
### A Q&A pair

#### Requirement

The system must do the thing.

> Is this acceptable?

Yes, it is acceptable.
"""
        )

        sut = QaSection.from_text(text)

        self.assertIsNotNone(sut.requirement)
        self.assertNotIn("Is this acceptable?", sut.requirement.text)
        self.assertIsNotNone(sut.question)
        self.assertEqual(sut.question.text, "Is this acceptable?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "Yes, it is acceptable.")


class TestQaAnswerIsHeadingFree(unittest.TestCase):
    """`QaAnswer` has no heading of its own -- it is the trailing prose within a `QaSection`."""

    def test_text_computed_property_exposes_value(self) -> None:
        sut = QaAnswer.from_text(format_text("Some prose.\n"))

        self.assertEqual(sut.text, "Some prose.\n")

    def test_multi_paragraph_answer_round_trips(self) -> None:
        text = format_text(
            """\
### A question?

> The question itself.

First paragraph of the answer.

Second paragraph of the answer.
"""
        )

        sut = QaSection.from_text(text)

        self.assertIn("First paragraph", sut.answer.text)
        self.assertIn("Second paragraph", sut.answer.text)
        self.assertEqual(str(sut), text)


class TestGeneralIntroductionRawRequirements(unittest.TestCase):
    """`General`/`Introduction`/`RawRequirements` parse and round-trip (ACC-002/ACC-003)."""

    def test_parses_and_round_trips(self) -> None:
        sut = _minimal_general()

        self.assertIsNone(sut.comment)
        self.assertEqual(sut.introduction.body[0].text, "Some intro text.")
        self.assertIn("Some raw requirements text.", sut.raw_requirements.text)

    def test_introduction_and_raw_requirements_keep_implicit_alias_derivation(self) -> None:
        """No explicit `@alias` on `Introduction`/`RawRequirements` -- per the plan's direct instruction."""
        self.assertTrue(match_alias(Introduction, "Introduction"))
        self.assertTrue(match_alias(RawRequirements, "Raw Requirements"))


class TestQaRequiredVsOptionalFields(unittest.TestCase):
    """`Qa`'s 9 `<QaCategory>` fields plus `general` are mandatory; `more_information` is optional (ACC-003)."""

    def _build_minimal_kwargs(self) -> dict:
        return {
            "general": _minimal_general(),
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

    def test_missing_mandatory_category_raises_validation_error(self) -> None:
        kwargs = self._build_minimal_kwargs()
        del kwargs["safety"]

        with self.assertRaises(ValidationError):
            Qa(**kwargs)


if __name__ == "__main__":
    unittest.main()
