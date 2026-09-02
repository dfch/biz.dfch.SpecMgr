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

"""Tests for the `Sysrs` body model (ACC-004/ACC-005).

Covers the alias acceptance/rejection of every heading class (incl. the
8-class LITERAL pin set), the per-section cross-reference item-text regex
matrix (REQ-006), the `BusinessContextAndGoals`/`SystemOverview` composite
containers, the `Requirements` >=1-of-9 after-validator (the
`ValidationError` channel per the 2026-09-02 decision), the
`OtherCharacteristics` no-validator umbrella, the `References`/
cross-reference lists' zero-item rejection, the `Updates` timestamp-led
alias + newest-first ordering check, the Task 1.3(e) empty-mandatory-leaf
acceptance pin, and `Sysrs`'s misordering/structural-violation matrix.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias
from biz.dfch.specmgr.sysrs.models.v1.body import (
    Appendix,
    AssumptionsAndDependencies,
    BusinessContext,
    BusinessContextAndGoals,
    Compatibility,
    Decisions,
    DefinitionsAndAcronyms,
    EnvironmentalConditions,
    Flexibility,
    FunctionalSuitability,
    Goals,
    InformationManagement,
    InteractionCapability,
    Maintainability,
    MoreInformation,
    OperationalConceptAndScenarios,
    OtherCharacteristics,
    PackagingHandlingShippingAndTransportation,
    PerformanceEfficiency,
    PhysicalCharacteristics,
    PolicyAndRegulation,
    ProblemStatement,
    References,
    Reliability,
    Requirements,
    Risks,
    Safety,
    Security,
    StakeholderNeedsAndElicitation,
    SystemContext,
    SystemFunctions,
    SystemIntegration,
    SystemLifeCycleSustainment,
    SystemModesAndStates,
    SystemOverview,
    SystemPurpose,
    SystemScope,
    Sysrs,
    UpdateEntry,
    Updates,
    UserCharacteristics,
    Verification,
)

# Fixture UUIDs (lowercase 8-4-4-4-12 hex), borrowed from
# `.specmgr/feat/feat-32-sysrs/sysrs-example.md` for realism.
_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_PRB_ID = "7166b565-ddb2-4a91-924c-d36d0e02d7aa"
_QA_ID = "c79bc330-6795-4dd3-9b79-c0936d4ae7f9"
_UC_ID = "88ed67cd-0b3b-4846-a827-530c12695936"
_DEC_ID = "60b1e331-4fe4-4d41-8c50-d0bd6227c472"
_ADR_ID = "365bcab7-b086-4205-84f9-eb1654ff8410"
_RSK_ID = "c1b33b41-d976-4191-a2c5-6f3c09441eb3"
_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"
_VCR_ID = "ee8672f3-af06-4f53-bc2a-80b5a581399b"

# Every LITERAL-pinned class alongside its canonical heading text and the
# (wrong) SPACE_SEPARATED-derived text the implicit alias would produce.
_LITERAL_CLASSES = [
    (BusinessContextAndGoals, "Business Context and Goals", "Business Context And Goals"),
    (StakeholderNeedsAndElicitation, "Stakeholder Needs and Elicitation", "Stakeholder Needs And Elicitation"),
    (OperationalConceptAndScenarios, "Operational Concept and Scenarios", "Operational Concept And Scenarios"),
    (AssumptionsAndDependencies, "Assumptions and Dependencies", "Assumptions And Dependencies"),
    (SystemModesAndStates, "System Modes and States", "System Modes And States"),
    (DefinitionsAndAcronyms, "Definitions and Acronyms", "Definitions And Acronyms"),
    (PolicyAndRegulation, "Policy and Regulation", "Policy And Regulation"),
    (
        PackagingHandlingShippingAndTransportation,
        "Packaging, Handling, Shipping and Transportation",
        "Packaging Handling Shipping And Transportation",
    ),
]

# Every cross-reference list class alongside its allowed type tag(s) (a
# tuple, since `Decisions` allows two) and whether it is H2- or H3-level.
_CROSS_REF_CLASSES = [
    (Goals, ("GOL",)),
    (ProblemStatement, ("PRB",)),
    (StakeholderNeedsAndElicitation, ("QA",)),
    (OperationalConceptAndScenarios, ("UC",)),
    (Decisions, ("DEC", "ADR")),
    (Risks, ("RSK",)),
    (FunctionalSuitability, ("REQ",)),
    (PerformanceEfficiency, ("REQ",)),
    (Compatibility, ("REQ",)),
    (InteractionCapability, ("REQ",)),
    (Reliability, ("REQ",)),
    (Security, ("REQ",)),
    (Maintainability, ("REQ",)),
    (Flexibility, ("REQ",)),
    (Safety, ("REQ",)),
    (PhysicalCharacteristics, ("REQ",)),
    (EnvironmentalConditions, ("REQ",)),
    (InformationManagement, ("REQ",)),
    (PolicyAndRegulation, ("REQ",)),
    (SystemLifeCycleSustainment, ("REQ",)),
    (PackagingHandlingShippingAndTransportation, ("REQ",)),
    (Verification, ("VCR",)),
]


def _system_purpose() -> SystemPurpose:
    return SystemPurpose.from_text(format_text("## System Purpose\n\nSome purpose prose.\n"))


def _system_scope() -> SystemScope:
    return SystemScope.from_text(format_text("## System Scope\n\nSome scope prose.\n"))


def _business_context_and_goals() -> BusinessContextAndGoals:
    return BusinessContextAndGoals.from_text(
        format_text(f"## Business Context and Goals\n\n### Goals\n\n- GOL {_GOL_ID}: A goal\n")
    )


def _system_overview() -> SystemOverview:
    return SystemOverview.from_text(
        format_text("## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n")
    )


def _requirements() -> Requirements:
    return Requirements.from_text(
        format_text(f"## Requirements\n\n### Functional Suitability\n\n- REQ {_REQ_ID}: A req\n")
    )


def _minimal_sysrs_kwargs() -> dict:
    return {
        "system_purpose": _system_purpose(),
        "system_scope": _system_scope(),
        "business_context_and_goals": _business_context_and_goals(),
        "system_overview": _system_overview(),
        "requirements": _requirements(),
    }


class TestSysrsHeadingAlias(unittest.TestCase):
    """`Sysrs`'s H1 alias mandates the `System Requirements Specification: ` prefix."""

    def test_accepts_valid_prefix(self) -> None:
        for heading in (
            "System Requirements Specification: Example Widget Platform",
            "System Requirements Specification: x",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Sysrs, heading))

    def test_rejects_missing_or_wrong_prefix(self) -> None:
        for heading in (
            "System Specification: Example Widget Platform",
            "system requirements specification: Example Widget Platform",
            "Example Widget Platform",
            "System Requirements Specification:",
            "System Requirements Specification: ",
        ):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Sysrs, heading))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Sysrs._metadata.get("type"), "heading_open")
        self.assertEqual(Sysrs._metadata.get("tag"), "h1")


class TestLiteralAliasClasses(unittest.TestCase):
    """The 8-class LITERAL pin set (lowercase "and" / commas) -- Phase 1-confirmed exhaustive list."""

    def test_each_accepts_its_canonical_heading(self) -> None:
        for cls, canonical, _wrong in _LITERAL_CLASSES:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, canonical))

    def test_each_rejects_the_space_separated_derivation(self) -> None:
        for cls, _canonical, wrong in _LITERAL_CLASSES:
            with self.subTest(cls=cls.__name__):
                self.assertFalse(match_alias(cls, wrong))


class TestImplicitHeadingAliases(unittest.TestCase):
    """Every other section class derives its heading from its class name (SPACE_SEPARATED)."""

    def test_leaf_and_container_sections_match_their_canonical_headings(self) -> None:
        for cls, heading in (
            (SystemPurpose, "System Purpose"),
            (SystemScope, "System Scope"),
            (BusinessContext, "Business Context"),
            (Goals, "Goals"),
            (ProblemStatement, "Problem Statement"),
            (Decisions, "Decisions"),
            (Risks, "Risks"),
            (SystemOverview, "System Overview"),
            (SystemContext, "System Context"),
            (SystemFunctions, "System Functions"),
            (UserCharacteristics, "User Characteristics"),
            (SystemIntegration, "System Integration"),
            (Requirements, "Requirements"),
            (FunctionalSuitability, "Functional Suitability"),
            (PerformanceEfficiency, "Performance Efficiency"),
            (Compatibility, "Compatibility"),
            (InteractionCapability, "Interaction Capability"),
            (Reliability, "Reliability"),
            (Security, "Security"),
            (Maintainability, "Maintainability"),
            (Flexibility, "Flexibility"),
            (Safety, "Safety"),
            (OtherCharacteristics, "Other Characteristics"),
            (PhysicalCharacteristics, "Physical Characteristics"),
            (EnvironmentalConditions, "Environmental Conditions"),
            (InformationManagement, "Information Management"),
            (SystemLifeCycleSustainment, "System Life Cycle Sustainment"),
            (Verification, "Verification"),
            (References, "References"),
            (MoreInformation, "More Information"),
            (Appendix, "Appendix"),
            (Updates, "Updates"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))

    def test_reject_foreign_headings(self) -> None:
        for cls, foreign in (
            (SystemPurpose, "System Purposes"),
            (Goals, "Goal"),
            (Requirements, "Requirement"),
            (References, "Reference"),
            (Updates, "Update"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(match_alias(cls, foreign))


class TestCrossReferenceItemPatterns(unittest.TestCase):
    """Every cross-reference list class's per-item type-tag regex (REQ-006)."""

    def test_goals_accepts_correct_tag_and_rejects_wrong_tag(self) -> None:
        Goals.from_text(format_text(f"### Goals\n\n- GOL {_GOL_ID}: A goal\n"))
        with self.assertRaises(ValidationError):
            Goals.from_text(format_text(f"### Goals\n\n- PRB {_GOL_ID}: A goal\n"))

    def test_problem_statement_accepts_correct_tag_and_rejects_wrong_tag(self) -> None:
        ProblemStatement.from_text(format_text(f"### Problem Statement\n\n- PRB {_PRB_ID}: A problem\n"))
        with self.assertRaises(ValidationError):
            ProblemStatement.from_text(format_text(f"### Problem Statement\n\n- GOL {_PRB_ID}: A problem\n"))

    def test_stakeholder_needs_accepts_qa_and_rejects_others(self) -> None:
        StakeholderNeedsAndElicitation.from_text(
            format_text(f"## Stakeholder Needs and Elicitation\n\n- QA {_QA_ID}: An interview\n")
        )
        with self.assertRaises(ValidationError):
            StakeholderNeedsAndElicitation.from_text(
                format_text(f"## Stakeholder Needs and Elicitation\n\n- UC {_QA_ID}: An interview\n")
            )

    def test_operational_concept_accepts_uc_and_rejects_others(self) -> None:
        OperationalConceptAndScenarios.from_text(
            format_text(f"## Operational Concept and Scenarios\n\n- UC {_UC_ID}: A scenario\n")
        )
        with self.assertRaises(ValidationError):
            OperationalConceptAndScenarios.from_text(
                format_text(f"## Operational Concept and Scenarios\n\n- QA {_UC_ID}: A scenario\n")
            )

    def test_decisions_accepts_both_dec_and_adr(self) -> None:
        Decisions.from_text(format_text(f"## Decisions\n\n- DEC {_DEC_ID}: A decision\n"))
        Decisions.from_text(format_text(f"## Decisions\n\n- ADR {_ADR_ID}: An architecture decision\n"))

    def test_decisions_rejects_req(self) -> None:
        with self.assertRaises(ValidationError):
            Decisions.from_text(format_text(f"## Decisions\n\n- REQ {_DEC_ID}: A decision\n"))

    def test_risks_accepts_rsk_and_rejects_others(self) -> None:
        Risks.from_text(format_text(f"## Risks\n\n- RSK {_RSK_ID}: A risk\n"))
        with self.assertRaises(ValidationError):
            Risks.from_text(format_text(f"## Risks\n\n- REQ {_RSK_ID}: A risk\n"))

    def test_requirements_children_accept_req_and_reject_others(self) -> None:
        for cls in (
            FunctionalSuitability,
            PerformanceEfficiency,
            Compatibility,
            InteractionCapability,
            Reliability,
            Security,
            Maintainability,
            Flexibility,
            Safety,
            PhysicalCharacteristics,
            EnvironmentalConditions,
            InformationManagement,
            SystemLifeCycleSustainment,
        ):
            with self.subTest(cls=cls.__name__):
                heading_text = _heading_for(cls)
                cls.from_text(format_text(f"{heading_text}\n\n- REQ {_REQ_ID}: A req\n"))
                with self.assertRaises(ValidationError):
                    cls.from_text(format_text(f"{heading_text}\n\n- GOL {_REQ_ID}: A req\n"))

    def test_every_cross_reference_class_in_the_table_accepts_its_allowed_tags(self) -> None:
        """Regression-style coverage exercising `_CROSS_REF_CLASSES` end to end (REQ-006)."""
        for cls, tags in _CROSS_REF_CLASSES:
            heading_text = _heading_for(cls)
            for tag in tags:
                with self.subTest(cls=cls.__name__, tag=tag):
                    sut = cls.from_text(format_text(f"{heading_text}\n\n- {tag} {_GOL_ID}: A title\n"))
                    self.assertEqual(len(sut.items), 1)

    def test_policy_and_regulation_accepts_req_and_rejects_others(self) -> None:
        PolicyAndRegulation.from_text(format_text(f"### Policy and Regulation\n\n- REQ {_REQ_ID}: A req\n"))
        with self.assertRaises(ValidationError):
            PolicyAndRegulation.from_text(format_text(f"### Policy and Regulation\n\n- GOL {_REQ_ID}: A req\n"))

    def test_packaging_handling_accepts_req_and_rejects_others(self) -> None:
        heading = "### Packaging, Handling, Shipping and Transportation"
        PackagingHandlingShippingAndTransportation.from_text(format_text(f"{heading}\n\n- REQ {_REQ_ID}: A req\n"))
        with self.assertRaises(ValidationError):
            PackagingHandlingShippingAndTransportation.from_text(format_text(f"{heading}\n\n- GOL {_REQ_ID}: A req\n"))

    def test_verification_accepts_vcr_and_rejects_others(self) -> None:
        Verification.from_text(format_text(f"## Verification\n\n- VCR {_VCR_ID}: A verification\n"))
        with self.assertRaises(ValidationError):
            Verification.from_text(format_text(f"## Verification\n\n- REQ {_VCR_ID}: A verification\n"))

    def test_malformed_uuid_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Goals.from_text(format_text("### Goals\n\n- GOL not-a-uuid: A goal\n"))

    def test_uppercase_uuid_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Goals.from_text(format_text(f"### Goals\n\n- GOL {_GOL_ID.upper()}: A goal\n"))

    def test_missing_title_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Goals.from_text(format_text(f"### Goals\n\n- GOL {_GOL_ID}\n"))
        with self.assertRaises(ValidationError):
            Goals.from_text(format_text(f"### Goals\n\n- GOL {_GOL_ID}:\n"))

    def test_bare_bullet_without_notes_accepted(self) -> None:
        sut = Goals.from_text(format_text(f"### Goals\n\n- GOL {_GOL_ID}: A goal\n"))

        self.assertEqual(len(sut.items), 1)
        self.assertIsNone(sut.items[0].notes)

    def test_bullet_with_notes_accepted(self) -> None:
        sut = Goals.from_text(format_text(f"### Goals\n\n- GOL {_GOL_ID}: A goal\n\n  A paraphrase note.\n"))

        self.assertEqual(len(sut.items), 1)
        self.assertIsNotNone(sut.items[0].notes)
        self.assertEqual(sut.items[0].notes[0].text, "A paraphrase note.")


def _heading_for(cls: type) -> str:
    """Return the `## `/`### ` heading line for a cross-reference list class used in the parametrized tests above."""
    names = {
        Goals: "### Goals",
        ProblemStatement: "### Problem Statement",
        StakeholderNeedsAndElicitation: "## Stakeholder Needs and Elicitation",
        OperationalConceptAndScenarios: "## Operational Concept and Scenarios",
        Decisions: "## Decisions",
        Risks: "## Risks",
        FunctionalSuitability: "### Functional Suitability",
        PerformanceEfficiency: "### Performance Efficiency",
        Compatibility: "### Compatibility",
        InteractionCapability: "### Interaction Capability",
        Reliability: "### Reliability",
        Security: "### Security",
        Maintainability: "### Maintainability",
        Flexibility: "### Flexibility",
        Safety: "### Safety",
        PhysicalCharacteristics: "### Physical Characteristics",
        EnvironmentalConditions: "### Environmental Conditions",
        InformationManagement: "### Information Management",
        PolicyAndRegulation: "### Policy and Regulation",
        SystemLifeCycleSustainment: "### System Life Cycle Sustainment",
        PackagingHandlingShippingAndTransportation: "### Packaging, Handling, Shipping and Transportation",
        Verification: "## Verification",
    }
    return names[cls]


class TestCrossReferenceListZeroItems(unittest.TestCase):
    """A cross-reference list section present with zero items is a structural error (ACC-004)."""

    def test_from_text_with_zero_items_raises_assertion_error(self) -> None:
        for cls, heading in (
            (Goals, "### Goals"),
            (ProblemStatement, "### Problem Statement"),
            (StakeholderNeedsAndElicitation, "## Stakeholder Needs and Elicitation"),
            (OperationalConceptAndScenarios, "## Operational Concept and Scenarios"),
            (Decisions, "## Decisions"),
            (Risks, "## Risks"),
            (FunctionalSuitability, "### Functional Suitability"),
            (Verification, "## Verification"),
        ):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(AssertionError):
                    cls.from_text(format_text(f"{heading}\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        for cls in (Goals, ProblemStatement, Decisions, Risks, FunctionalSuitability, Verification):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(ValidationError):
                    cls(items=[])


class TestMandatorySections(unittest.TestCase):
    """`Sysrs`'s five mandatory sections -- absent raises (two channels, mirroring SOP's own split)."""

    def test_missing_each_mandatory_field_raises_validation_error_on_construction(self) -> None:
        for field in (
            "system_purpose",
            "system_scope",
            "business_context_and_goals",
            "system_overview",
            "requirements",
        ):
            with self.subTest(field=field):
                kwargs = _minimal_sysrs_kwargs()
                del kwargs[field]

                with self.assertRaises(ValidationError):
                    Sysrs(**kwargs)

    def test_from_text_missing_system_purpose_raises_assertion_error(self) -> None:
        text = format_text(
            "# System Requirements Specification: X\n\n"
            "## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n- GOL "
            f"{_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n- REQ "
            f"{_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_from_text_missing_requirements_raises_assertion_error(self) -> None:
        text = format_text(
            "# System Requirements Specification: X\n\n"
            "## System Purpose\n\np\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n- GOL "
            f"{_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_from_text_rejects_lead_paragraph_under_h1(self) -> None:
        text = format_text(
            "# System Requirements Specification: X\n\nSome lead prose.\n\n"
            "## System Purpose\n\np\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n- GOL "
            f"{_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n- REQ "
            f"{_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)


class TestOptionalSectionsIndividuallyOptional(unittest.TestCase):
    """Every optional `Sysrs` H2 defaults to `None`/independently settable (ACC-004/005)."""

    def test_all_optional_sections_default_to_none_when_absent(self) -> None:
        sut = Sysrs(**_minimal_sysrs_kwargs())

        self.assertIsNone(sut.stakeholder_needs_and_elicitation)
        self.assertIsNone(sut.operational_concept_and_scenarios)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.risks)
        self.assertIsNone(sut.assumptions_and_dependencies)
        self.assertIsNone(sut.system_modes_and_states)
        self.assertIsNone(sut.other_characteristics)
        self.assertIsNone(sut.verification)
        self.assertIsNone(sut.references)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.appendix)
        self.assertIsNone(sut.definitions_and_acronyms)
        self.assertIsNone(sut.updates)

    def test_verification_present(self) -> None:
        kwargs = _minimal_sysrs_kwargs()
        kwargs["verification"] = Verification.from_text(format_text(f"## Verification\n\n- VCR {_VCR_ID}: A vcr\n"))

        sut = Sysrs(**kwargs)

        self.assertIsNotNone(sut.verification)

    def test_references_present(self) -> None:
        kwargs = _minimal_sysrs_kwargs()
        kwargs["references"] = References.from_text(format_text("## References\n\n- Some external standard.\n"))

        sut = Sysrs(**kwargs)

        self.assertIsNotNone(sut.references)


class TestBusinessContextAndGoalsComposite(unittest.TestCase):
    """`BusinessContextAndGoals`: mandatory `Goals`, optional `BusinessContext`/`ProblemStatement`."""

    def test_missing_goals_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            BusinessContextAndGoals.from_text(format_text("## Business Context and Goals\n"))

    def test_missing_goals_raises_validation_error_on_construction(self) -> None:
        with self.assertRaises(ValidationError):
            BusinessContextAndGoals()

    def test_business_context_and_problem_statement_optional(self) -> None:
        sut = BusinessContextAndGoals.from_text(
            format_text(f"## Business Context and Goals\n\n### Goals\n\n- GOL {_GOL_ID}: A goal\n")
        )

        self.assertIsNone(sut.business_context)
        self.assertIsNone(sut.problem_statement)

    def test_all_three_children_present(self) -> None:
        sut = BusinessContextAndGoals.from_text(
            format_text(
                "## Business Context and Goals\n\n### Business Context\n\nContext prose.\n\n"
                f"### Goals\n\n- GOL {_GOL_ID}: A goal\n\n"
                f"### Problem Statement\n\n- PRB {_PRB_ID}: A problem\n"
            )
        )

        self.assertIsNotNone(sut.business_context)
        self.assertEqual([item.text for item in sut.goals.items], [f"GOL {_GOL_ID}: A goal"])
        self.assertEqual([item.text for item in sut.problem_statement.items], [f"PRB {_PRB_ID}: A problem"])


class TestSystemOverviewComposite(unittest.TestCase):
    """`SystemOverview`: mandatory `SystemContext`/`SystemFunctions`, optional `UserCharacteristics`/`SystemIntegration`."""

    def test_missing_system_context_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            SystemOverview.from_text(format_text("## System Overview\n\n### System Functions\n\nf\n"))

    def test_missing_system_functions_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            SystemOverview.from_text(format_text("## System Overview\n\n### System Context\n\nc\n"))

    def test_optional_children_default_to_none(self) -> None:
        sut = SystemOverview.from_text(
            format_text("## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n")
        )

        self.assertIsNone(sut.user_characteristics)
        self.assertIsNone(sut.system_integration)

    def test_all_four_children_present(self) -> None:
        sut = SystemOverview.from_text(
            format_text(
                "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
                "### User Characteristics\n\nu\n\n### System Integration\n\ni\n"
            )
        )

        self.assertIsNotNone(sut.user_characteristics)
        self.assertIsNotNone(sut.system_integration)


class TestRequirementsAtLeastOnePresent(unittest.TestCase):
    """`Requirements`: >=1 of the nine H3s -- the `ValidationError` channel (2026-09-02 decision)."""

    def test_zero_children_raises_validation_error_on_construction(self) -> None:
        with self.assertRaises(ValidationError):
            Requirements()

    def test_one_child_present_parses(self) -> None:
        sut = Requirements.from_text(format_text(f"## Requirements\n\n### Safety\n\n- REQ {_REQ_ID}: A safety req\n"))

        self.assertIsNotNone(sut.safety)
        self.assertIsNone(sut.functional_suitability)

    def test_all_nine_children_present_in_canonical_order(self) -> None:
        text = format_text(
            "## Requirements\n\n"
            f"### Functional Suitability\n\n- REQ {_REQ_ID}: a\n\n"
            f"### Performance Efficiency\n\n- REQ {_REQ_ID}: b\n\n"
            f"### Compatibility\n\n- REQ {_REQ_ID}: c\n\n"
            f"### Interaction Capability\n\n- REQ {_REQ_ID}: d\n\n"
            f"### Reliability\n\n- REQ {_REQ_ID}: e\n\n"
            f"### Security\n\n- REQ {_REQ_ID}: f\n\n"
            f"### Maintainability\n\n- REQ {_REQ_ID}: g\n\n"
            f"### Flexibility\n\n- REQ {_REQ_ID}: h\n\n"
            f"### Safety\n\n- REQ {_REQ_ID}: i\n"
        )

        sut = Requirements.from_text(text)

        self.assertIsNotNone(sut.functional_suitability)
        self.assertIsNotNone(sut.performance_efficiency)
        self.assertIsNotNone(sut.compatibility)
        self.assertIsNotNone(sut.interaction_capability)
        self.assertIsNotNone(sut.reliability)
        self.assertIsNotNone(sut.security)
        self.assertIsNotNone(sut.maintainability)
        self.assertIsNotNone(sut.flexibility)
        self.assertIsNotNone(sut.safety)
        self.assertEqual(str(sut), text)

    def test_out_of_canonical_order_raises_assertion_error(self) -> None:
        text = format_text(
            "## Requirements\n\n"
            f"### Performance Efficiency\n\n- REQ {_REQ_ID}: b\n\n"
            f"### Functional Suitability\n\n- REQ {_REQ_ID}: a\n"
        )

        with self.assertRaises(AssertionError):
            Requirements.from_text(text)


class TestOtherCharacteristicsUmbrella(unittest.TestCase):
    """`OtherCharacteristics`: optional umbrella, NO >=1-of-N validator (unlike `Requirements`)."""

    def test_zero_children_present_is_accepted(self) -> None:
        sut = OtherCharacteristics()

        self.assertIsNone(sut.physical_characteristics)
        self.assertIsNone(sut.environmental_conditions)
        self.assertIsNone(sut.information_management)
        self.assertIsNone(sut.policy_and_regulation)
        self.assertIsNone(sut.system_life_cycle_sustainment)
        self.assertIsNone(sut.packaging_handling_shipping_and_transportation)

    def test_empty_container_parses(self) -> None:
        sut = OtherCharacteristics.from_text(format_text("## Other Characteristics\n"))

        self.assertIsNone(sut.physical_characteristics)

    def test_one_child_present(self) -> None:
        sut = OtherCharacteristics.from_text(
            format_text(f"## Other Characteristics\n\n### Physical Characteristics\n\n- REQ {_REQ_ID}: A req\n")
        )

        self.assertIsNotNone(sut.physical_characteristics)
        self.assertIsNone(sut.environmental_conditions)


class TestReferencesList(unittest.TestCase):
    """`References` -- plain bullet list (no notes, no type-tag regex); present implies >=1 item."""

    def test_parses_plain_bullets(self) -> None:
        sut = References.from_text(format_text("## References\n\n- Some external standard.\n- Another one.\n"))

        self.assertEqual([item.text for item in sut.items], ["Some external standard.", "Another one."])

    def test_items_have_no_notes_attribute_type_conflict(self) -> None:
        # A plain MarkdownListItem has no `notes` attribute at all.
        sut = References.from_text(format_text("## References\n\n- Some external standard.\n"))

        self.assertFalse(hasattr(sut.items[0], "notes"))

    def test_zero_items_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            References.from_text(format_text("## References\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            References(items=[])


class TestUpdateEntryHeadingAlias(unittest.TestCase):
    """`UpdateEntry`'s regex alias -- date-only or date+time lead, ` - `/` : ` separator."""

    def test_accepts_date_only_lead(self) -> None:
        for heading in ("2026-08-30 - Created", "2026-08-30 : Created"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_accepts_full_date_time_lead(self) -> None:
        for heading in (
            "2026-08-30 14:30:00.000+02:00 - Approved",
            "2026-08-30 14:30:00.000Z - Approved",
            "2026-08-30 14:30:00.000+02:00 : Approved",
            "2026-08-30 14:30:00.000Z : Approved",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_rejects_em_dash_separator(self) -> None:
        for heading in ("2026-08-30 — Approved", "2026-08-30 14:30:00.000Z — Approved"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_rejects_missing_title(self) -> None:
        for heading in ("2026-08-30", "2026-08-30 - ", "2026-08-30 -", "2026-08-30 :"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(UpdateEntry._metadata.get("type"), "heading_open")
        self.assertEqual(UpdateEntry._metadata.get("tag"), "h3")


class TestUpdatesContainer(unittest.TestCase):
    """`Updates` -- dynamic newest-first collection of timestamp-led entries."""

    def test_parses_date_only_entries_newest_first(self) -> None:
        text = format_text(
            "## Updates\n\n### 2026-09-14 - Added Security Requirements\n\nSome text.\n\n"
            "### 2026-08-30 - Initial draft created\n\nSome other text.\n"
        )

        sut = Updates.from_text(text)

        self.assertEqual([entry.timestamp for entry in sut.updates], ["2026-09-14", "2026-08-30"])
        self.assertEqual(str(sut), text)

    def test_parses_date_time_entries_with_colon_separator(self) -> None:
        text = format_text("## Updates\n\n### 2026-08-30 14:30:00.000+02:00 : Approved\n\nSigned off.\n")

        sut = Updates.from_text(text)

        self.assertEqual(sut.updates[0].timestamp, "2026-08-30 14:30:00.000+02:00")
        self.assertEqual(sut.updates[0].title, "Approved")

    def test_out_of_order_entries_raise_validation_error(self) -> None:
        text = format_text("## Updates\n\n### 2026-08-30 - Older\n\nx\n\n### 2026-09-14 - Newer\n\ny\n")

        with self.assertRaises(ValidationError):
            Updates.from_text(text)

    def test_equal_timestamps_are_allowed(self) -> None:
        text = format_text("## Updates\n\n### 2026-08-30 - First\n\nx\n\n### 2026-08-30 - Second\n\ny\n")

        sut = Updates.from_text(text)

        self.assertEqual(len(sut.updates), 2)

    def test_zero_entries_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Updates.from_text(format_text("## Updates\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Updates(updates=[])

    def test_comment_is_optional(self) -> None:
        text = format_text(
            "## Updates\n\n<!-- Newest entry first -- prepend below. -->\n\n### 2026-08-30 - Created\n\nx\n"
        )

        sut = Updates.from_text(text)

        self.assertIsNotNone(sut.comment)


class TestEmptyMandatoryLeafAccepted(unittest.TestCase):
    """Task 1.3(e) pin: a mandatory free-text leaf present with zero body content is ACCEPTED."""

    def test_system_purpose_with_zero_body_is_accepted(self) -> None:
        text = format_text("## System Purpose\n")

        sut = SystemPurpose.from_text(text)

        self.assertEqual(sut.text, text)
        self.assertEqual(str(sut), text)

    def test_system_context_with_zero_body_is_accepted(self) -> None:
        text = format_text("### System Context\n")

        sut = SystemContext.from_text(text)

        self.assertEqual(sut.text, text)

    def test_sysrs_with_empty_mandatory_leaves_round_trips(self) -> None:
        text = format_text(
            "# System Requirements Specification: X\n\n"
            "## System Purpose\n\n"
            "## System Scope\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\n### System Functions\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n"
        )

        sut = Sysrs.from_text(text)

        self.assertEqual(sut.system_purpose.text, "## System Purpose\n")
        self.assertEqual(str(sut), text)


class TestSysrsMisordering(unittest.TestCase):
    """H2 sections out of declaration order / unknown headings / structural violations (ACC-004)."""

    def _wrap(self, middle: str) -> str:
        return format_text(f"# System Requirements Specification: X\n\n{middle}")

    def test_unknown_h2_raises_assertion_error(self) -> None:
        text = self._wrap(
            "## System Purpose\n\np\n\n## Unknown Section\n\nx\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_system_scope_before_system_purpose_raises_assertion_error(self) -> None:
        text = self._wrap(
            "## System Scope\n\ns\n\n## System Purpose\n\np\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_optional_section_misordering_raises_assertion_error(self) -> None:
        # `## Risks` must come before `## Assumptions and Dependencies`.
        text = self._wrap(
            "## System Purpose\n\np\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## Assumptions and Dependencies\n\na\n\n"
            f"## Risks\n\n- RSK {_RSK_ID}: A risk\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        text = self._wrap(
            "## System Purpose\n\nFirst.\n\n## System Purpose\n\nSecond.\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
        text = format_text(
            "Some leading prose.\n\n# System Requirements Specification: X\n\n"
            "## System Purpose\n\np\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)

    def test_second_h1_raises_assertion_error(self) -> None:
        text = self._wrap(
            "## System Purpose\n\np\n\n## System Scope\n\ns\n\n"
            "## Business Context and Goals\n\n### Goals\n\n"
            f"- GOL {_GOL_ID}: A goal\n\n"
            "## System Overview\n\n### System Context\n\nc\n\n### System Functions\n\nf\n\n"
            "## Requirements\n\n### Functional Suitability\n\n"
            f"- REQ {_REQ_ID}: A req\n\n# Second Title\n"
        )

        with self.assertRaises(AssertionError):
            Sysrs.from_text(text)


if __name__ == "__main__":
    unittest.main()
