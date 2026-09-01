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

"""Tests for the `Vcr` body model (ACC-001/ACC-002/ACC-003/ACC-004).

Covers the alias acceptance/rejection of every heading class, `Verifies`'
regex-enforced `value`/mandatory `notes`, `Coverage`'s closed 3-value set,
the `AcceptanceCriterion` heading regex (number/method/title) and its
computed `number`/`method` fields, the independently-optional
`description`/`TestSteps` presence/absence (all four combinations,
mirroring `.specmgr/feat/feat-33-vcr/example.md`'s empirically-validated
shape), `AcceptanceCriteria`'s zero-entry rejection, `Vcr`'s section
optional/misordering behavior, and the duplicate-AC-number after-validator
(the `ValidationError` channel).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.vcr.models.v1.body import (
    AcceptanceCriteria,
    AcceptanceCriterion,
    Coverage,
    MoreInformation,
    TestSteps,
    UpdateEntry,
    Updates,
    Vcr,
    Verifies,
)
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias

# The full reference body (frontmatter stripped), exercising every field:
# `Verifies` with its optional leading comment, `Coverage`, `Acceptance
# Criteria` with three entries covering all four `description`/`test_steps`
# combinations (a number gap: AC-001 has both a description paragraph and
# `Test Steps`, AC-003 has a description paragraph but no `Test Steps`,
# AC-004 has neither -- heading only), `More Information`, and `Updates`
# (with its own leading "newest first" anchor comment) with two entries.
# Mirrors the shape empirically validated against
# `.specmgr/feat/feat-33-vcr/example.md` (AC-001/002/004 carry a
# description paragraph, AC-003 has none; AC-001 is the only one with
# `Test Steps` in that draft).
_REFERENCE_TEXT = format_text(
    """\
# API Key Revocation Latency Verification

## Verifies

<!-- Cross-referenced during the feat-32-sysrs gap-analysis review. -->

REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action

Confirms that a support agent revoking a compromised partner API key
closes the exposure window fast enough to meet the 1-second performance
requirement.

## Coverage

partial

## Acceptance Criteria

### AC-001 (Test): The revoke endpoint returns 204 within 1s under nominal load

95th-percentile latency from revoke request to `204 No Content` response
stays below 1000 ms, measured under a simulated background load.

#### Test Steps

1. Issue a new API key via `POST /keys`.

2. Submit `POST /keys/{id}/revoke` and start a timer.

3. Record the wall-clock time to the `204 No Content` response.

### AC-003 (Inspection): The revoke handler has a well-formed not-found error path

A static review of the `revoke_key` handler source confirms a well-formed
not-found branch.

### AC-004 (Special): The revocation audit-log format is compliance-certified

## More Information

Verification performed against the staging gateway (build 2026.08.30-rc3).

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-08-27 : Confirmed

AC-001 and AC-003 executed against staging.

### 2026-08-26 - Created

Initial verification case drafted.
"""
)


def _verifies() -> Verifies:
    return Verifies.from_text(
        format_text("## Verifies\n\nREQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Some title\n\nSome paraphrase.\n")
    )


def _coverage() -> Coverage:
    return Coverage.from_text(format_text("## Coverage\n\nfull\n"))


def _acceptance_criteria() -> AcceptanceCriteria:
    return AcceptanceCriteria.from_text(format_text("## Acceptance Criteria\n\n### AC-001 (Test): Some criterion\n"))


def _minimal_vcr_kwargs() -> dict:
    return {
        "verifies": _verifies(),
        "coverage": _coverage(),
        "acceptance_criteria": _acceptance_criteria(),
    }


class TestVcrHeadingAlias(unittest.TestCase):
    """`Vcr`'s H1 alias is the free-form `.+` REGEX: any non-empty title matches."""

    def test_vcr_matches_any_nonempty_h1_text(self) -> None:
        for heading in ("API Key Revocation Latency Verification", "A VCR", "x"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Vcr, heading))

    def test_vcr_rejects_empty_h1_text(self) -> None:
        self.assertFalse(match_alias(Vcr, ""))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Vcr._metadata.get("type"), "heading_open")
        self.assertEqual(Vcr._metadata.get("tag"), "h1")


class TestVerifiesValueValidation(unittest.TestCase):
    """`Verifies.value` is regex-enforced against `_VERIFIES_PATTERN` (REQ-001)."""

    def test_accepts_req_reference(self) -> None:
        sut = Verifies.from_text(
            format_text("## Verifies\n\nREQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\nA paraphrase.\n")
        )

        self.assertEqual(sut.value.text, "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title")
        self.assertEqual(sut.notes.text, "A paraphrase.")

    def test_accepts_uc_reference(self) -> None:
        sut = Verifies.from_text(
            format_text("## Verifies\n\nUC 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\nA paraphrase.\n")
        )

        self.assertEqual(sut.value.text, "UC 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title")

    def test_rejects_unknown_type_tag(self) -> None:
        with self.assertRaises(ValidationError):
            Verifies.from_text(
                format_text("## Verifies\n\nDEC 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\nA paraphrase.\n")
            )

    def test_rejects_malformed_uuid(self) -> None:
        with self.assertRaises(ValidationError):
            Verifies.from_text(format_text("## Verifies\n\nREQ not-a-uuid: A title\n\nA paraphrase.\n"))

    def test_rejects_missing_title(self) -> None:
        with self.assertRaises(ValidationError):
            Verifies.from_text(
                format_text("## Verifies\n\nREQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d:\n\nA paraphrase.\n")
            )

    def test_missing_notes_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Verifies.from_text(format_text("## Verifies\n\nREQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n"))

    def test_optional_comment_present(self) -> None:
        sut = Verifies.from_text(
            format_text(
                "## Verifies\n\n<!-- Some context comment. -->\n\n"
                "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\nA paraphrase.\n"
            )
        )

        self.assertIsNotNone(sut.comment)
        self.assertEqual(sut.value.text, "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title")

    def test_optional_comment_absent(self) -> None:
        sut = _verifies()

        self.assertIsNone(sut.comment)

    def test_metadata_is_heading_open_h2(self) -> None:
        self.assertEqual(Verifies._metadata.get("type"), "heading_open")
        self.assertEqual(Verifies._metadata.get("tag"), "h2")


class TestCoverageValueValidation(unittest.TestCase):
    """`Coverage.value` is regex-enforced against the closed 3-value set (REQ-002)."""

    def test_accepts_all_three_values(self) -> None:
        for value in ("full", "partial", "none"):
            with self.subTest(value=value):
                sut = Coverage.from_text(format_text(f"## Coverage\n\n{value}\n"))
                self.assertEqual(sut.value.text, value)

    def test_rejects_unknown_value(self) -> None:
        with self.assertRaises(ValidationError):
            Coverage.from_text(format_text("## Coverage\n\nunknown\n"))

    def test_rejects_tara_words(self) -> None:
        # "transfer"/"accept"/"reduce"/"avoid" belong to RSK's `## Strategy`, not VCR's `## Coverage`.
        for value in ("transfer", "accept", "reduce", "avoid"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    Coverage.from_text(format_text(f"## Coverage\n\n{value}\n"))

    def test_metadata_is_heading_open_h2(self) -> None:
        self.assertEqual(Coverage._metadata.get("type"), "heading_open")
        self.assertEqual(Coverage._metadata.get("tag"), "h2")


class TestAcceptanceCriterionHeadingAlias(unittest.TestCase):
    """`AcceptanceCriterion`'s regex alias requires `AC-NNN (Method): <text>` -- 3-digit number, DTAIS method."""

    def test_accepts_all_five_dtais_methods(self) -> None:
        for method in ("Demonstration", "Test", "Analysis", "Inspection", "Special"):
            with self.subTest(method=method):
                self.assertTrue(match_alias(AcceptanceCriterion, f"AC-001 ({method}): Some criterion text"))

    def test_accepts_boundary_number(self) -> None:
        self.assertTrue(match_alias(AcceptanceCriterion, "AC-999 (Test): Some criterion text"))

    def test_rejects_two_digit_number(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-01 (Test): Some criterion text"))

    def test_rejects_four_digit_number(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-0001 (Test): Some criterion text"))

    def test_rejects_unknown_method_word(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-001 (Certification): Some criterion text"))

    def test_rejects_missing_parentheses(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-001 Test: Some criterion text"))

    def test_rejects_missing_colon(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-001 (Test) Some criterion text"))

    def test_rejects_missing_criterion_text(self) -> None:
        for heading in ("AC-001 (Test):", "AC-001 (Test): "):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(AcceptanceCriterion, heading))

    def test_rejects_nonnumeric_number(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-abc (Test): Some criterion text"))

    def test_rejects_wrong_case_method(self) -> None:
        self.assertFalse(match_alias(AcceptanceCriterion, "AC-001 (test): Some criterion text"))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(AcceptanceCriterion._metadata.get("type"), "heading_open")
        self.assertEqual(AcceptanceCriterion._metadata.get("tag"), "h3")


class TestAcceptanceCriterionDescriptionAndTestSteps(unittest.TestCase):
    """`AcceptanceCriterion.description`/`.test_steps` are independently optional (ACC-003).

    Covers all four combinations empirically demonstrated by
    `.specmgr/feat/feat-33-vcr/example.md`: a description paragraph with no
    `Test Steps` (AC-002/AC-004 there), `Test Steps` with no description
    (not in that draft, but structurally symmetric and covered here), both
    together (AC-001 there), and neither (heading only).
    """

    def test_description_only_no_test_steps(self) -> None:
        text = format_text("### AC-002 (Analysis): Some criterion text\n\nSome description prose.\n")

        sut = AcceptanceCriterion.from_text(text)

        self.assertIsNotNone(sut.description)
        self.assertEqual(sut.description.text, "Some description prose.")
        self.assertIsNone(sut.test_steps)
        self.assertEqual(str(sut), text)

    def test_test_steps_only_no_description(self) -> None:
        text = format_text(
            "### AC-003 (Inspection): Some criterion text\n\n#### Test Steps\n\n1. Do the first thing.\n\n"
            "2. Do the second thing.\n"
        )

        sut = AcceptanceCriterion.from_text(text)

        self.assertIsNone(sut.description)
        self.assertIsNotNone(sut.test_steps)
        self.assertEqual(len(sut.test_steps.items), 2)
        self.assertEqual(str(sut), text)

    def test_both_description_and_test_steps(self) -> None:
        text = format_text(
            "### AC-001 (Test): Some criterion text\n\nSome description prose.\n\n#### Test Steps\n\n"
            "1. Do the first thing.\n\n2. Do the second thing.\n"
        )

        sut = AcceptanceCriterion.from_text(text)

        self.assertIsNotNone(sut.description)
        self.assertEqual(sut.description.text, "Some description prose.")
        self.assertIsNotNone(sut.test_steps)
        self.assertEqual(len(sut.test_steps.items), 2)
        self.assertEqual(str(sut), text)

    def test_neither_description_nor_test_steps(self) -> None:
        text = format_text("### AC-004 (Special): Some criterion text\n")

        sut = AcceptanceCriterion.from_text(text)

        self.assertIsNone(sut.description)
        self.assertIsNone(sut.test_steps)
        self.assertEqual(str(sut), text)


class TestAcceptanceCriterionComputedFields(unittest.TestCase):
    """`AcceptanceCriterion.number`/`.method` are computed from the heading (ACC-003)."""

    def test_parses_number_and_method(self) -> None:
        sut = AcceptanceCriterion.from_text(format_text("### AC-001 (Test): Some criterion text\n"))

        self.assertEqual(sut.number, 1)
        self.assertEqual(sut.method, "Test")

    def test_method_is_not_normalized(self) -> None:
        sut = AcceptanceCriterion.from_text(format_text("### AC-002 (Special): Some criterion text\n"))

        self.assertEqual(sut.method, "Special")

    def test_accepts_multi_digit_and_gap_numbers(self) -> None:
        sut = AcceptanceCriterion.from_text(format_text("### AC-012 (Analysis): Some criterion text\n"))

        self.assertEqual(sut.number, 12)

    def test_keeps_colons_inside_criterion_text(self) -> None:
        sut = AcceptanceCriterion.from_text(format_text("### AC-003 (Inspection): A: B\n"))

        self.assertEqual(sut.number, 3)
        self.assertEqual(sut.method, "Inspection")

    def test_rejects_heading_without_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            AcceptanceCriterion.from_text(format_text("### AC-001 (Test):\n"))

    def test_test_steps_absent_by_default(self) -> None:
        sut = AcceptanceCriterion.from_text(format_text("### AC-001 (Test): Some criterion text\n"))

        self.assertIsNone(sut.test_steps)

    def test_test_steps_present(self) -> None:
        text = format_text(
            "### AC-001 (Test): Some criterion text\n\n#### Test Steps\n\n1. Do the first thing.\n\n"
            "2. Do the second thing.\n"
        )

        sut = AcceptanceCriterion.from_text(text)

        self.assertIsNotNone(sut.test_steps)
        self.assertEqual(len(sut.test_steps.items), 2)
        self.assertEqual(str(sut), text)


class TestTestStepsZeroItems(unittest.TestCase):
    """`TestSteps` requires >=1 item: H4 present with zero steps is a structural error."""

    def test_from_text_with_zero_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            TestSteps.from_text(format_text("#### Test Steps\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            TestSteps(items=[])

    def test_metadata_is_heading_open_h4(self) -> None:
        self.assertEqual(TestSteps._metadata.get("type"), "heading_open")
        self.assertEqual(TestSteps._metadata.get("tag"), "h4")


class TestAcceptanceCriteriaHeadingAlias(unittest.TestCase):
    """`AcceptanceCriteria` pins its heading LITERAL to "Acceptance Criteria"."""

    def test_accepts_canonical_heading(self) -> None:
        self.assertTrue(match_alias(AcceptanceCriteria, "Acceptance Criteria"))

    def test_rejects_other_wording(self) -> None:
        for heading in ("AcceptanceCriteria", "acceptance criteria", "Acceptance Criterion"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(AcceptanceCriteria, heading))

    def test_metadata_is_heading_open_h2(self) -> None:
        self.assertEqual(AcceptanceCriteria._metadata.get("type"), "heading_open")
        self.assertEqual(AcceptanceCriteria._metadata.get("tag"), "h2")


class TestAcceptanceCriteriaZeroEntries(unittest.TestCase):
    """`AcceptanceCriteria` requires >=1 criterion: H2 present with zero entries is a structural error."""

    def test_from_text_with_zero_criteria_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            AcceptanceCriteria.from_text(format_text("## Acceptance Criteria\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            AcceptanceCriteria(criteria=[])


class TestUpdateEntryHeadingAlias(unittest.TestCase):
    """`UpdateEntry`'s regex alias requires a `yyyy-MM-dd` (or full date+time) timestamp + ` - `/` : ` + `title`."""

    def test_accepts_date_only_and_date_time_headings(self) -> None:
        for heading in (
            "2026-08-26 - Created",
            "2026-08-26 : Created",
            "2026-08-26 14:30:00.000+02:00 - Confirmed",
            "2026-08-26 14:30:00.000Z : Confirmed",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_rejects_non_timestamp_led_headings(self) -> None:
        for heading in ("A Note", "x", "2026-8-26 - Created", "Created"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_update_entry_rejects_empty_h3_text(self) -> None:
        self.assertFalse(match_alias(UpdateEntry, ""))


class TestImplicitHeadingAliases(unittest.TestCase):
    """The remaining leaf sections derive their heading from their class name (SPACE_SEPARATED)."""

    def test_leaf_sections_match_their_canonical_headings(self) -> None:
        for cls, heading in (
            (MoreInformation, "More Information"),
            (Updates, "Updates"),
            (TestSteps, "Test Steps"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))

    def test_leaf_sections_reject_foreign_headings(self) -> None:
        for cls, foreign in (
            (MoreInformation, "More Information "),
            (Updates, "Update"),
            (TestSteps, "Test Step"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(match_alias(cls, foreign))


class TestMandatorySections(unittest.TestCase):
    """`Vcr.verifies`/`.coverage`/`.acceptance_criteria` are mandatory -- absent raises.

    Two distinct channels, mirroring the engine's own split: direct
    construction without a mandatory field raises `pydantic.ValidationError`
    (the field is simply missing from the constructor call), while
    `Vcr.from_text` on a markdown document that lacks the section raises
    `AssertionError` (the engine found no match for a mandatory field).
    """

    def test_missing_verifies_raises_validation_error(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        del kwargs["verifies"]

        with self.assertRaises(ValidationError):
            Vcr(**kwargs)

    def test_missing_coverage_raises_validation_error(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        del kwargs["coverage"]

        with self.assertRaises(ValidationError):
            Vcr(**kwargs)

    def test_missing_acceptance_criteria_raises_validation_error(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        del kwargs["acceptance_criteria"]

        with self.assertRaises(ValidationError):
            Vcr(**kwargs)

    def test_from_text_missing_verifies_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n## Coverage\n\nfull\n\n## Acceptance Criteria\n\n### AC-001 (Test): Some criterion\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)

    def test_from_text_missing_coverage_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n## Verifies\n\nREQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\nA paraphrase.\n\n"
            "## Acceptance Criteria\n\n### AC-001 (Test): Some criterion\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)

    def test_from_text_missing_acceptance_criteria_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n## Verifies\n\nREQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\nA paraphrase.\n\n"
            "## Coverage\n\nfull\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)


class TestOptionalSectionsIndividuallyOptional(unittest.TestCase):
    """Each optional section is independently optional (ACC-004)."""

    def test_both_optional_sections_default_to_none_when_absent(self) -> None:
        sut = Vcr(**_minimal_vcr_kwargs())

        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_more_information_present(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        kwargs["more_information"] = MoreInformation.from_text(
            format_text("## More Information\n\nSome more information text.\n")
        )

        sut = Vcr(**kwargs)

        self.assertIsNotNone(sut.more_information)
        self.assertIn("Some more information text.", sut.more_information.text)
        self.assertIsNone(sut.updates)

    def test_updates_present(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        kwargs["updates"] = Updates.from_text(format_text("## Updates\n\n### 2026-08-26 - Created\n\nSome text.\n"))

        sut = Vcr(**kwargs)

        self.assertIsNotNone(sut.updates)
        self.assertEqual(len(sut.updates.updates), 1)
        self.assertIsNone(sut.more_information)

    def test_updates_with_leading_comment(self) -> None:
        # `Updates` is `MarkdownSection2WithComment` (unlike DEC's plain
        # `MarkdownSection2`) -- `.specmgr/feat/feat-33-vcr/example.md`/
        # `template.md` both carry a permanent "newest first" anchor comment
        # directly under this heading (Design Notes' persisted candidate
        # outline), mirroring `feat`'s own `Updates(MarkdownSection3WithComment)`.
        text = format_text(
            "## Updates\n\n<!-- Newest entry first -- prepend new entries directly below this comment. -->\n\n"
            "### 2026-08-26 - Created\n\nSome text.\n"
        )

        sut = Updates.from_text(text)

        self.assertIsNotNone(sut.comment)
        self.assertEqual(len(sut.updates), 1)
        self.assertEqual(str(sut), text)


class TestDuplicateAcNumbers(unittest.TestCase):
    """`Vcr` rejects duplicate AC numbers (ACC-003, the `ValidationError` channel)."""

    def _acceptance_criteria(self, heading_a: str, heading_b: str) -> AcceptanceCriteria:
        return AcceptanceCriteria.from_text(
            format_text(f"## Acceptance Criteria\n\n### {heading_a}\n\n### {heading_b}\n")
        )

    def test_duplicate_identical_numbers_raise_validation_error(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        kwargs["acceptance_criteria"] = self._acceptance_criteria("AC-001 (Test): First", "AC-001 (Analysis): Second")

        with self.assertRaises(ValidationError):
            Vcr(**kwargs)

    def test_gaps_are_allowed(self) -> None:
        kwargs = _minimal_vcr_kwargs()
        kwargs["acceptance_criteria"] = self._acceptance_criteria("AC-001 (Test): First", "AC-003 (Analysis): Second")

        sut = Vcr(**kwargs)

        self.assertEqual([criterion.number for criterion in sut.acceptance_criteria.criteria], [1, 3])


class TestVcrMisordering(unittest.TestCase):
    """H2/H3 sections out of declaration order leave text over: structural failure."""

    def test_updates_before_more_information_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n"
            "## Verifies\n\n"
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\n"
            "A paraphrase.\n\n"
            "## Coverage\n\n"
            "full\n\n"
            "## Acceptance Criteria\n\n"
            "### AC-001 (Test): Some criterion\n\n"
            "## Updates\n\n"
            "### 2026-08-26 - Created\n\n"
            "Some update text.\n\n"
            "## More Information\n\n"
            "Some more information text.\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)

    def test_coverage_before_verifies_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n"
            "## Coverage\n\n"
            "full\n\n"
            "## Verifies\n\n"
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\n"
            "A paraphrase.\n\n"
            "## Acceptance Criteria\n\n"
            "### AC-001 (Test): Some criterion\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)

    def test_unknown_h2_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n"
            "## Verifies\n\n"
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\n"
            "A paraphrase.\n\n"
            "## Unknown Section\n\n"
            "Some unknown prose.\n\n"
            "## Coverage\n\n"
            "full\n\n"
            "## Acceptance Criteria\n\n"
            "### AC-001 (Test): Some criterion\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        text = format_text(
            "# A VCR\n\n"
            "## Verifies\n\n"
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: A title\n\n"
            "A paraphrase.\n\n"
            "## Coverage\n\n"
            "full\n\n"
            "## Coverage\n\n"
            "partial\n\n"
            "## Acceptance Criteria\n\n"
            "### AC-001 (Test): Some criterion\n"
        )

        with self.assertRaises(AssertionError):
            Vcr.from_text(text)


class TestVcrReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference body parses, exposes its computed fields, and round-trips (ACC-001..004)."""

    def test_round_trips(self) -> None:
        sut = Vcr.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_title(self) -> None:
        sut = Vcr.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.text, "API Key Revocation Latency Verification")

    def test_verifies(self) -> None:
        sut = Vcr.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.verifies.comment)
        self.assertEqual(
            sut.verifies.value.text,
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of agent action",
        )
        self.assertIn("closes the exposure window", sut.verifies.notes.text)

    def test_coverage(self) -> None:
        sut = Vcr.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.coverage.value.text, "partial")

    def test_acceptance_criteria(self) -> None:
        sut = Vcr.from_text(_REFERENCE_TEXT)

        criteria = sut.acceptance_criteria.criteria
        self.assertEqual([(c.number, c.method) for c in criteria], [(1, "Test"), (3, "Inspection"), (4, "Special")])

        # AC-001: both a description paragraph and `Test Steps`.
        self.assertIsNotNone(criteria[0].description)
        self.assertIn("95th-percentile latency", criteria[0].description.text)
        self.assertIsNotNone(criteria[0].test_steps)
        self.assertEqual(len(criteria[0].test_steps.items), 3)

        # AC-003: a description paragraph but no `Test Steps`.
        self.assertIsNotNone(criteria[1].description)
        self.assertIn("well-formed", criteria[1].description.text)
        self.assertIsNone(criteria[1].test_steps)

        # AC-004: neither a description paragraph nor `Test Steps` (heading only).
        self.assertIsNone(criteria[2].description)
        self.assertIsNone(criteria[2].test_steps)

    def test_more_information_and_updates(self) -> None:
        sut = Vcr.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.more_information)
        self.assertIn("staging gateway", sut.more_information.text)

        updates = sut.updates
        self.assertIsNotNone(updates)
        self.assertIsNotNone(updates.comment)
        self.assertEqual(len(updates.updates), 2)
        self.assertEqual(updates.updates[0].content.text, "AC-001 and AC-003 executed against staging.")
        self.assertEqual(updates.updates[1].content.text, "Initial verification case drafted.")


if __name__ == "__main__":
    unittest.main()
