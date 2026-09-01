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

"""Tests for the `Sop` body model (ACC-001/ACC-002).

Covers the alias acceptance/rejection of every heading class, the RASCI
`RolesAndResponsibilities` composite (mandatory `Accountable`/`Responsible`,
the three-way `Support`/`Consulted`/`Informed` states), the computed
`Step.number`/`Step.name` and `UpdateEntry.timestamp`/`UpdateEntry.title`
fields, the `Procedure`/`Updates` containers' zero-entry rejection, the
`RelatedArtifacts` sub-list independence (incl. the new `Sops` self-reference),
`Sop`'s section optional/misordering behavior, and the duplicate-step-number
after-validator (the `ValidationError` channel).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias
from biz.dfch.specmgr.sop.models.v1.body import (
    AcceptanceCriteria,
    Accountable,
    Consulted,
    Decisions,
    Definitions,
    Goals,
    Informed,
    MoreInformation,
    Procedure,
    Purpose,
    RelatedArtifacts,
    Requirements,
    Responsible,
    RolesAndResponsibilities,
    SafetyAndPrecautions,
    Scope,
    Sop,
    Sops,
    Step,
    Support,
    UpdateEntry,
    Updates,
)

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
    (Sops, "Sops"),
]

# The full reference body (frontmatter stripped), exercising every field:
# all optional sections present, RASCI with `Support` deliberately empty
# (present-with-zero-items) and `Consulted`/`Informed` populated, 5 numbered
# `Step`s (with a number gap), `Related Artifacts` with all five sub-lists
# including `Sops`, and `Updates` with one ISO8601-timestamped entry.
_REFERENCE_TEXT = format_text(
    """\
# New Employee IT Account Provisioning

## Purpose

Provision all IT accounts a new hire needs on day one, so they can work
without waiting on manual ticket handling.

## Scope

All new hires across every business unit. Contractors are out of scope
(see the contractor onboarding SOP).

## Definitions

- SSO: Single Sign-On, the corporate identity provider.

- Service Desk: The IT support team handling access requests.

## Roles and Responsibilities

### Accountable

The IT Manager owns this procedure end to end.

### Responsible

- Helpdesk Lead

- Identity Administrator

### Support

### Consulted

- HR Business Partner

- Information Security Officer

### Informed

- The new hire

- The hiring manager

## Safety and Precautions

Verify the new hire's identity against HR records before provisioning any
account. Never provision accounts for a start date that has not been
confirmed by HR.

## Procedure

### Step 1: Submit request

HR submits the onboarding request via the service desk portal.

### Step 2: Verify identity

The service desk verifies the new hire's identity against HR records.

### Step 4: Provision accounts

The identity administrator provisions SSO, email, and role-specific
accounts.

## Related Artifacts

### Requirements

- REQ-0001: Day-one account readiness

### Decisions

- DEC-0001: SSO provider selection

### Goals

- GOL-0001: Four-hour onboarding

### Acceptance Criteria

- ACC-0001: New hire can sign in on day one

### Sops

- SOP-0042: IT Account Deprovisioning

## More Information

The full account matrix is stored in the IT wiki under `onboarding/accounts/`.

## Updates

### 2026-08-30 14:30:00.000+02:00 - Approved

The IT Manager signed off on the procedure after the pilot run.
"""
)


def _purpose() -> Purpose:
    return Purpose.from_text(format_text("## Purpose\n\nSome purpose prose.\n"))


def _procedure() -> Procedure:
    return Procedure.from_text(format_text("## Procedure\n\n### Step 1: Do something\n\nSome step body.\n"))


def _minimal_sop_kwargs() -> dict:
    return {
        "purpose": _purpose(),
        "procedure": _procedure(),
    }


def _roles(
    *,
    accountable: str = "The IT Manager.",
    responsible: str = "- Helpdesk Lead\n",
    support: str | None = None,
    consulted: str | None = None,
    informed: str | None = None,
) -> str:
    """Build a `## Roles and Responsibilities` body with the given sub-sections.

    Each of `support`/`consulted`/`informed` is omitted entirely when ``None``
    (heading absent); when a string, that string is inserted verbatim under
    the heading (use the empty string for a present-with-zero-items heading).
    """
    parts = [
        "## Roles and Responsibilities\n",
        f"\n### Accountable\n\n{accountable}\n",
        f"\n### Responsible\n\n{responsible}\n",
    ]
    if support is not None:
        parts.append(f"\n### Support\n\n{support}")
    if consulted is not None:
        parts.append(f"\n### Consulted\n\n{consulted}")
    if informed is not None:
        parts.append(f"\n### Informed\n\n{informed}")
    return "".join(parts)


class TestSopHeadingAlias(unittest.TestCase):
    """`Sop`'s H1 alias is the free-form `.+` REGEX: any non-empty title matches."""

    def test_sop_matches_any_nonempty_h1_text(self) -> None:
        for heading in ("New Employee IT Account Provisioning", "An SOP", "x"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Sop, heading))

    def test_sop_rejects_empty_h1_text(self) -> None:
        self.assertFalse(match_alias(Sop, ""))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Sop._metadata.get("type"), "heading_open")
        self.assertEqual(Sop._metadata.get("tag"), "h1")


class TestSafetyAndPrecautionsHeadingAlias(unittest.TestCase):
    """`SafetyAndPrecautions` pins its heading LITERAL to "Safety and Precautions"."""

    def test_accepts_canonical_heading(self) -> None:
        self.assertTrue(match_alias(SafetyAndPrecautions, "Safety and Precautions"))

    def test_rejects_space_separated_derivation(self) -> None:
        # The implicit SPACE_SEPARATED alias would expect "Safety And Precautions"
        # (capitalized "And"); the LITERAL alias uses lowercase "and".
        self.assertFalse(match_alias(SafetyAndPrecautions, "Safety And Precautions"))

    def test_rejects_other_wording(self) -> None:
        for heading in ("Safety", "safety and precautions", "Safety & Precautions"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(SafetyAndPrecautions, heading))

    def test_metadata_is_heading_open_h2(self) -> None:
        self.assertEqual(SafetyAndPrecautions._metadata.get("type"), "heading_open")
        self.assertEqual(SafetyAndPrecautions._metadata.get("tag"), "h2")


class TestRolesAndResponsibilitiesHeadingAlias(unittest.TestCase):
    """`RolesAndResponsibilities` pins its heading LITERAL to "Roles and Responsibilities"."""

    def test_accepts_canonical_heading(self) -> None:
        self.assertTrue(match_alias(RolesAndResponsibilities, "Roles and Responsibilities"))

    def test_rejects_space_separated_derivation(self) -> None:
        self.assertFalse(match_alias(RolesAndResponsibilities, "Roles And Responsibilities"))

    def test_metadata_is_heading_open_h2(self) -> None:
        self.assertEqual(RolesAndResponsibilities._metadata.get("type"), "heading_open")
        self.assertEqual(RolesAndResponsibilities._metadata.get("tag"), "h2")


class TestStepHeadingAlias(unittest.TestCase):
    """`Step`'s regex alias requires `Step {N}: {name}` -- title mandatory."""

    def test_accepts_numbered_titled_headings(self) -> None:
        for heading in ("Step 1: Do something", "Step 01: X", "Step 12: A: B", "Step 99: y"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Step, heading))

    def test_rejects_headings_without_title(self) -> None:
        for heading in ("Step 1", "Step 1:", "Step 1: "):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Step, heading))

    def test_rejects_nonnumeric_and_malformed_numbers(self) -> None:
        for heading in ("Step one: X", "Step : X", "Step 1:X", "step 1: x", "Steps 1: X"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(Step, heading))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(Step._metadata.get("type"), "heading_open")
        self.assertEqual(Step._metadata.get("tag"), "h3")


class TestUpdateEntryHeadingAlias(unittest.TestCase):
    """`UpdateEntry`'s regex alias requires an ISO8601 timestamp + ` - `/` : ` + `title`."""

    def test_accepts_well_formed_offset_timestamps(self) -> None:
        for heading in (
            "2026-08-30 14:30:00.000+02:00 - Approved",
            "2026-08-30 14:30:00.000-05:00 - Approved",
            "2026-08-30 14:30:00.000Z - Approved",
            "2026-01-02 03:04:05.678+00:00 - Created",
            "2026-08-30 14:30:00.000+02:00 : Approved",
            "2026-08-30 14:30:00.000-05:00 : Approved",
            "2026-08-30 14:30:00.000Z : Approved",
            "2026-01-02 03:04:05.678+00:00 : Created",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_rejects_em_dash_separator(self) -> None:
        """ACC-001: the em-dash separator is rejected -- only ` - `/` : ` are accepted."""
        for heading in (
            "2026-08-30 14:30:00.000+02:00 — Approved",
            "2026-08-30 14:30:00.000-05:00 — Approved",
            "2026-08-30 14:30:00.000Z — Approved",
        ):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_rejects_missing_title(self) -> None:
        for heading in (
            "2026-08-30 14:30:00.000+02:00",
            "2026-08-30 14:30:00.000+02:00 - ",
            "2026-08-30 14:30:00.000+02:00 -",
            "2026-08-30 14:30:00.000+02:00 : ",
            "2026-08-30 14:30:00.000+02:00 :",
        ):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_rejects_missing_offset(self) -> None:
        for heading in (
            "2026-08-30 14:30:00.000 - Approved",
            "2026-08-30 14:30:00 - Approved",
            "2026-08-30 14:30 - Approved",
        ):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_rejects_wrong_timestamp_format(self) -> None:
        for heading in (
            "2026-8-30 14:30:00.000+02:00 - Approved",
            "2026-08-30 14:30:00+02:00 - Approved",
            "2026-08-30T14:30:00.000+02:00 - Approved",
            "bad - Approved",
        ):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(UpdateEntry._metadata.get("type"), "heading_open")
        self.assertEqual(UpdateEntry._metadata.get("tag"), "h3")


class TestSubListHeadingAliases(unittest.TestCase):
    """Each `RelatedArtifacts` sub-list class resolves its own, correct, distinct heading alias.

    Regression-style coverage mirroring DEC's `RelatedArtifacts` sub-list
    alias test: since the five sub-list headings are short, single- (or
    double-) word title-case names, this confirms each class's
    `SPACE_SEPARATED`-derived alias matches its own exact wording and no
    other sub-list's.
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
    """The remaining leaf sections derive their heading from their class name (SPACE_SEPARATED)."""

    def test_leaf_sections_match_their_canonical_headings(self) -> None:
        for cls, heading in (
            (Purpose, "Purpose"),
            (Scope, "Scope"),
            (Definitions, "Definitions"),
            (MoreInformation, "More Information"),
            (Procedure, "Procedure"),
            (Updates, "Updates"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))

    def test_leaf_sections_reject_foreign_headings(self) -> None:
        for cls, foreign in (
            (Scope, "Scopes"),
            (Definitions, "Definition"),
            (MoreInformation, "More Information "),
            (Purpose, "Purposes"),
            (Procedure, "Procedures"),
            (Updates, "Update"),
        ):
            with self.subTest(cls=cls.__name__):
                self.assertFalse(match_alias(cls, foreign))


class TestMandatorySections(unittest.TestCase):
    """`Sop.purpose`/`Sop.procedure` are mandatory -- absent raises.

    Two distinct channels, mirroring the engine's own split: direct
    construction without a mandatory field raises `pydantic.ValidationError`,
    while `Sop.from_text` on a markdown document that lacks the section raises
    `AssertionError`.
    """

    def test_missing_purpose_raises_validation_error(self) -> None:
        kwargs = _minimal_sop_kwargs()
        del kwargs["purpose"]

        with self.assertRaises(ValidationError):
            Sop(**kwargs)

    def test_missing_procedure_raises_validation_error(self) -> None:
        kwargs = _minimal_sop_kwargs()
        del kwargs["procedure"]

        with self.assertRaises(ValidationError):
            Sop(**kwargs)

    def test_from_text_missing_purpose_raises_assertion_error(self) -> None:
        text = format_text("# An SOP\n\n## Procedure\n\n### Step 1: Do something\n\nSome step body.\n")

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_from_text_missing_procedure_raises_assertion_error(self) -> None:
        text = format_text("# An SOP\n\n## Purpose\n\nSome purpose prose.\n")

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_from_text_rejects_lead_paragraph_under_h1(self) -> None:
        # SOP has no lead paragraph under the H1 (unlike GOL): the first field
        # is the mandatory `## Purpose`.
        text = format_text(
            "# An SOP\n\nSome lead prose.\n\n## Purpose\n\nSome purpose prose.\n"
            "## Procedure\n\n### Step 1: Do something\n\nSome step body.\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)


class TestOptionalSectionsIndividuallyOptional(unittest.TestCase):
    """Each optional section is independently optional (ACC-002).

    Covers all seven optional sections absent at once (a freshly created `sop`
    document carries only `purpose` + `procedure`) and each section present
    one at a time.
    """

    def test_all_seven_optional_sections_default_to_none_when_absent(self) -> None:
        sut = Sop(**_minimal_sop_kwargs())

        self.assertIsNone(sut.scope)
        self.assertIsNone(sut.definitions)
        self.assertIsNone(sut.roles_and_responsibilities)
        self.assertIsNone(sut.safety_and_precautions)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.updates)

    def test_scope_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["scope"] = Scope.from_text(format_text("## Scope\n\nSome scope.\n"))

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.scope)
        self.assertIn("Some scope.", sut.scope.text)

    def test_definitions_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["definitions"] = Definitions.from_text(format_text("## Definitions\n\nSome definitions.\n"))

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.definitions)

    def test_roles_and_responsibilities_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["roles_and_responsibilities"] = RolesAndResponsibilities.from_text(format_text(_roles()))

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.roles_and_responsibilities)

    def test_safety_and_precautions_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["safety_and_precautions"] = SafetyAndPrecautions.from_text(
            format_text("## Safety and Precautions\n\nBe careful.\n")
        )

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.safety_and_precautions)
        self.assertIn("Be careful.", sut.safety_and_precautions.text)

    def test_related_artifacts_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["related_artifacts"] = RelatedArtifacts.from_text(
            format_text("## Related Artifacts\n\n### Decisions\n\n- DEC-0001: Some decision.\n")
        )

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.related_artifacts)

    def test_more_information_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["more_information"] = MoreInformation.from_text(format_text("## More Information\n\nSome more info.\n"))

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.more_information)

    def test_updates_present(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["updates"] = Updates.from_text(
            format_text("## Updates\n\n### 2026-08-30 14:30:00.000+02:00 - Created\n\nSome update text.\n")
        )

        sut = Sop(**kwargs)

        self.assertIsNotNone(sut.updates)
        self.assertEqual(len(sut.updates.updates), 1)


class TestRasciComposite(unittest.TestCase):
    """`RolesAndResponsibilities`: mandatory `Accountable`/`Responsible`, optional `Support`/`Consulted`/`Informed`."""

    def test_parses_accountable_and_responsible_only(self) -> None:
        sut = RolesAndResponsibilities.from_text(format_text(_roles()))

        self.assertEqual(sut.accountable.value.text, "The IT Manager.")
        self.assertEqual([item.text for item in sut.responsible.items], ["Helpdesk Lead"])
        self.assertIsNone(sut.support)
        self.assertIsNone(sut.consulted)
        self.assertIsNone(sut.informed)

    def test_missing_accountable_raises_assertion_error(self) -> None:
        text = format_text("## Roles and Responsibilities\n\n### Responsible\n\n- Helpdesk Lead\n")

        with self.assertRaises(AssertionError):
            RolesAndResponsibilities.from_text(text)

    def test_missing_responsible_raises_assertion_error(self) -> None:
        text = format_text("## Roles and Responsibilities\n\n### Accountable\n\nThe IT Manager.\n")

        with self.assertRaises(AssertionError):
            RolesAndResponsibilities.from_text(text)

    def test_missing_accountable_raises_validation_error_on_construction(self) -> None:
        with self.assertRaises(ValidationError):
            RolesAndResponsibilities(responsible=Responsible.from_text(format_text("### Responsible\n\n- x\n")))

    def test_missing_responsible_raises_validation_error_on_construction(self) -> None:
        with self.assertRaises(ValidationError):
            RolesAndResponsibilities(accountable=Accountable.from_text(format_text("### Accountable\n\nx\n")))

    def test_accountable_rejects_bullet_list(self) -> None:
        # `Accountable` is a single `MarkdownParagraph`, never a bullet list.
        text = format_text(
            "## Roles and Responsibilities\n\n### Accountable\n\n- The IT Manager\n\n### Responsible\n\n- Helpdesk Lead\n"
        )

        with self.assertRaises(AssertionError):
            RolesAndResponsibilities.from_text(text)

    def test_responsible_rejects_empty_body(self) -> None:
        # `Responsible` is a mandatory list (>=1 item): an empty body is a structural error.
        text = format_text(
            "## Roles and Responsibilities\n\n### Accountable\n\nThe IT Manager.\n\n### Responsible\n\n### Consulted\n\n- HR\n"
        )

        with self.assertRaises(AssertionError):
            RolesAndResponsibilities.from_text(text)

    def test_responsible_empty_list_raises_validation_error_on_construction(self) -> None:
        with self.assertRaises(ValidationError):
            Responsible(items=[])


class TestSupportConsultedInformedThreeStates(unittest.TestCase):
    """`Support`/`Consulted`/`Informed` each have three independently testable states (ACC-002).

    (a) heading absent entirely (`X is None`);
    (b) heading present with zero items (`X is not None`, `X.items is None`) --
        tested both mid-section (followed by a sibling H3) and at end-of-section;
    (c) heading present with N items (`X.items` populated).
    """

    def test_support_absent_when_heading_missing(self) -> None:
        sut = RolesAndResponsibilities.from_text(format_text(_roles()))

        self.assertIsNone(sut.support)

    def test_support_present_empty_mid_section(self) -> None:
        # `### Support` present with zero items, followed by `### Consulted`.
        sut = RolesAndResponsibilities.from_text(format_text(_roles(support="", consulted="- HR\n")))

        self.assertIsNotNone(sut.support)
        self.assertIsNone(sut.support.items)
        self.assertIsNotNone(sut.consulted)

    def test_support_present_empty_at_end_of_section(self) -> None:
        # `### Support` present with zero items as the last H3 (followed by the
        # next H2 `## Procedure` at the document level).
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Roles and Responsibilities\n\n"
            "### Accountable\n\nA\n\n### Responsible\n\n- R\n\n### Support\n\n"
            "## Procedure\n\n### Step 1: x\n\ny\n"
        )

        sut = Sop.from_text(text)

        rasci = sut.roles_and_responsibilities
        self.assertIsNotNone(rasci.support)
        self.assertIsNone(rasci.support.items)

    def test_support_present_with_items(self) -> None:
        sut = RolesAndResponsibilities.from_text(format_text(_roles(support="- Platform Team\n")))

        self.assertIsNotNone(sut.support)
        self.assertIsNotNone(sut.support.items)
        self.assertEqual([item.text for item in sut.support.items], ["Platform Team"])

    def test_consulted_present_empty_mid_section(self) -> None:
        sut = RolesAndResponsibilities.from_text(format_text(_roles(consulted="", informed="- HR\n")))

        self.assertIsNotNone(sut.consulted)
        self.assertIsNone(sut.consulted.items)
        self.assertIsNotNone(sut.informed)

    def test_informed_present_empty_at_end_of_section(self) -> None:
        # `### Informed` present with zero items as the last H3 in the section.
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Roles and Responsibilities\n\n"
            "### Accountable\n\nA\n\n### Responsible\n\n- R\n\n### Informed\n\n"
            "## Procedure\n\n### Step 1: x\n\ny\n"
        )

        sut = Sop.from_text(text)

        rasci = sut.roles_and_responsibilities
        self.assertIsNotNone(rasci.informed)
        self.assertIsNone(rasci.informed.items)

    def test_all_three_optional_h3s_in_different_states_in_one_document(self) -> None:
        # Support absent; Consulted present-empty mid-section; Informed present-with-N.
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Roles and Responsibilities\n\n"
            "### Accountable\n\nA\n\n### Responsible\n\n- R\n\n"
            "### Consulted\n\n### Informed\n\n- The new hire\n\n"
            "## Procedure\n\n### Step 1: x\n\ny\n"
        )

        sut = Sop.from_text(text)

        rasci = sut.roles_and_responsibilities
        self.assertIsNone(rasci.support)
        self.assertIsNotNone(rasci.consulted)
        self.assertIsNone(rasci.consulted.items)
        self.assertIsNotNone(rasci.informed)
        self.assertIsNotNone(rasci.informed.items)
        self.assertEqual([item.text for item in rasci.informed.items], ["The new hire"])

    def test_optional_h3_empty_list_field_accepts_none(self) -> None:
        # Direct construction: `items` defaults to `None` (the present-empty state)
        # for each of the three optional RASCI H3 leaves.
        for cls in (Support, Consulted, Informed):
            with self.subTest(cls=cls.__name__):
                sut = cls()

                self.assertIsNone(sut.items)


class TestStepComputedFields(unittest.TestCase):
    """`Step.number`/`Step.name` are computed from the heading (ACC-002)."""

    def test_parses_number_and_name(self) -> None:
        text = format_text("### Step 1: Provision the account\n\nSome step body.\n")

        sut = Step.from_text(text)

        self.assertEqual(sut.number, 1)
        self.assertEqual(sut.name, "Provision the account")
        self.assertEqual(str(sut), text)

    def test_accepts_leading_zero_number(self) -> None:
        sut = Step.from_text(format_text("### Step 01: X\n\nSome step body.\n"))

        self.assertEqual(sut.number, 1)
        self.assertEqual(sut.name, "X")

    def test_accepts_multi_digit_and_gap_numbers(self) -> None:
        sut = Step.from_text(format_text("### Step 12: X\n\nSome step body.\n"))

        self.assertEqual(sut.number, 12)
        self.assertEqual(sut.name, "X")

    def test_keeps_colons_inside_the_name(self) -> None:
        sut = Step.from_text(format_text("### Step 2: A: B\n\nSome step body.\n"))

        self.assertEqual(sut.number, 2)
        self.assertEqual(sut.name, "A: B")

    def test_rejects_heading_without_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Step.from_text(format_text("### Step 1\n\nSome step body.\n"))

    def test_rejects_heading_with_empty_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Step.from_text(format_text("### Step 1:\n\nSome step body.\n"))

    def test_rejects_nonnumeric_number_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            Step.from_text(format_text("### Step one: X\n\nSome step body.\n"))


class TestDuplicateStepNumbers(unittest.TestCase):
    """`Sop` rejects duplicate step numbers (ACC-002, the `ValidationError` channel)."""

    def _procedure(self, heading_a: str, heading_b: str) -> Procedure:
        return Procedure.from_text(
            format_text(f"## Procedure\n\n### {heading_a}\n\nBody A.\n\n### {heading_b}\n\nBody B.\n")
        )

    def test_duplicate_identical_numbers_raise_validation_error(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["procedure"] = self._procedure("Step 1: A", "Step 1: B")

        with self.assertRaises(ValidationError):
            Sop(**kwargs)

    def test_duplicate_via_leading_zero_raise_validation_error(self) -> None:
        # "01" normalizes to the same integer as "1" -- a duplicate.
        kwargs = _minimal_sop_kwargs()
        kwargs["procedure"] = self._procedure("Step 1: A", "Step 01: B")

        with self.assertRaises(ValidationError):
            Sop(**kwargs)

    def test_gaps_are_allowed(self) -> None:
        kwargs = _minimal_sop_kwargs()
        kwargs["procedure"] = self._procedure("Step 1: A", "Step 3: B")

        sut = Sop(**kwargs)

        self.assertEqual([step.number for step in sut.procedure.steps], [1, 3])


class TestProcedureZeroSteps(unittest.TestCase):
    """`Procedure` requires >=1 step: H2 present with zero steps is a structural error."""

    def test_from_text_with_zero_steps_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Procedure.from_text(format_text("## Procedure\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Procedure(steps=[])


class TestRelatedArtifactsSubListsIndividuallyOptional(unittest.TestCase):
    """Each of the five `RelatedArtifacts` sub-lists is independently optional (ACC-002)."""

    def test_all_five_sub_lists_default_to_none_when_absent(self) -> None:
        sut = RelatedArtifacts()

        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)
        self.assertIsNone(sut.sops)

    def test_empty_related_artifacts_container_parses(self) -> None:
        sut = RelatedArtifacts.from_text(format_text("## Related Artifacts\n"))

        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)
        self.assertIsNone(sut.sops)

    def test_requirements_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text("## Related Artifacts\n\n### Requirements\n\n- REQ-0001: Some requirement.\n")
        )

        self.assertIsNotNone(sut.requirements)
        self.assertEqual([item.text for item in sut.requirements.items], ["REQ-0001: Some requirement."])
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)
        self.assertIsNone(sut.sops)

    def test_sops_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(format_text("## Related Artifacts\n\n### Sops\n\n- SOP-0042: Some SOP.\n"))

        self.assertIsNotNone(sut.sops)
        self.assertEqual([item.text for item in sut.sops.items], ["SOP-0042: Some SOP."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.acceptance_criteria)

    def test_sub_list_present_without_any_bullet_raises_assertion_error(self) -> None:
        for heading in ("Requirements", "Decisions", "Goals", "Acceptance Criteria", "Sops"):
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
        with self.assertRaises(ValidationError):
            Sops(items=[])


class TestUpdateEntryComputedFields(unittest.TestCase):
    """`UpdateEntry.timestamp`/`UpdateEntry.title` are computed from the heading (ACC-002)."""

    def test_parses_timestamp_and_title_with_offset(self) -> None:
        text = format_text("### 2026-08-30 14:30:00.000+02:00 - Approved\n\nSigned off.\n")

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.timestamp, "2026-08-30 14:30:00.000+02:00")
        self.assertEqual(sut.title, "Approved")
        self.assertEqual(sut.content.text, "Signed off.")
        self.assertEqual(str(sut), text)

    def test_parses_timestamp_and_title_with_z(self) -> None:
        sut = UpdateEntry.from_text(format_text("### 2026-08-30 14:30:00.000Z - Created\n\nInitial draft.\n"))

        self.assertEqual(sut.timestamp, "2026-08-30 14:30:00.000Z")
        self.assertEqual(sut.title, "Created")

    def test_keeps_separator_inside_the_title(self) -> None:
        sut = UpdateEntry.from_text(format_text("### 2026-08-30 14:30:00.000+02:00 - A - B\n\nBody.\n"))

        self.assertEqual(sut.title, "A - B")

    def test_rejects_heading_without_title_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            UpdateEntry.from_text(format_text("### 2026-08-30 14:30:00.000+02:00\n\nBody.\n"))

    def test_rejects_heading_without_offset_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            UpdateEntry.from_text(format_text("### 2026-08-30 14:30:00.000 - Approved\n\nBody.\n"))

    def test_rejects_heading_with_wrong_timestamp_format_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            UpdateEntry.from_text(format_text("### 2026-8-30 14:30:00.000+02:00 - Approved\n\nBody.\n"))

    def test_rejects_heading_without_milliseconds_at_parse_time(self) -> None:
        with self.assertRaises(AssertionError):
            UpdateEntry.from_text(format_text("### 2026-08-30 14:30:00+02:00 - Approved\n\nBody.\n"))

    def test_entry_without_lead_paragraph_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            UpdateEntry.from_text(format_text("### 2026-08-30 14:30:00.000+02:00 - Approved\n"))

    def test_missing_content_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            UpdateEntry()


class TestUpdatesContainer(unittest.TestCase):
    """`Updates` mirrors DEC/TSK's `Updates`/`RecentUpdates` container shape."""

    def test_parses_multiple_entries_in_document_order(self) -> None:
        text = format_text(
            "## Updates\n\n"
            "### 2026-08-26 09:00:00.000+02:00 - Created\n\n"
            "First entry text.\n\n"
            "### 2026-08-27 10:00:00.000+02:00 - Confirmed\n\n"
            "Second entry text.\n"
        )

        sut = Updates.from_text(text)

        self.assertEqual(len(sut.updates), 2)
        self.assertEqual(sut.updates[0].content.text, "First entry text.")
        self.assertEqual(sut.updates[0].title, "Created")
        self.assertEqual(sut.updates[1].content.text, "Second entry text.")
        self.assertEqual(sut.updates[1].title, "Confirmed")
        self.assertEqual(str(sut), text)

    def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Updates.from_text(format_text("## Updates\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Updates(updates=[])


class TestSopMisordering(unittest.TestCase):
    """H2/H3 sections out of declaration order leave text over: structural failure."""

    def test_procedure_before_purpose_raises_assertion_error(self) -> None:
        text = format_text("# An SOP\n\n## Procedure\n\n### Step 1: x\n\ny\n\n## Purpose\n\np\n")

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_updates_before_more_information_raises_assertion_error(self) -> None:
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n\n"
            "## Updates\n\n### 2026-08-30 14:30:00.000+02:00 - Created\n\nSome update.\n\n"
            "## More Information\n\nSome more info.\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_related_artifacts_after_more_information_raises_assertion_error(self) -> None:
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n\n"
            "## More Information\n\nSome more info.\n\n## Related Artifacts\n\n### Requirements\n\n- REQ-0001: x\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_safety_and_precautions_after_procedure_raises_assertion_error(self) -> None:
        # Safety and Precautions must come before Procedure (read warnings before acting).
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n\n"
            "## Safety and Precautions\n\nBe careful.\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_unknown_h2_raises_assertion_error(self) -> None:
        text = format_text(
            "# An SOP\n\n## Purpose\n\np\n\n## Unknown Section\n\nSome unknown prose.\n\n"
            "## Procedure\n\n### Step 1: x\n\ny\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_duplicate_h2_raises_assertion_error(self) -> None:
        text = format_text(
            "# An SOP\n\n## Purpose\n\nFirst purpose.\n\n## Purpose\n\nSecond purpose.\n\n"
            "## Procedure\n\n### Step 1: x\n\ny\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_step_outside_procedure_raises_assertion_error(self) -> None:
        text = format_text("# An SOP\n\n### Step 1: x\n\ny\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n")

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_accountable_outside_roles_raises_assertion_error(self) -> None:
        text = format_text(
            "# An SOP\n\n### Accountable\n\nA\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n"
        )

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
        text = format_text("Some leading prose.\n\n# An SOP\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n")

        with self.assertRaises(AssertionError):
            Sop.from_text(text)

    def test_second_h1_raises_assertion_error(self) -> None:
        text = format_text("# An SOP\n\n## Purpose\n\np\n\n## Procedure\n\n### Step 1: x\n\ny\n\n# Second Title\n")

        with self.assertRaises(AssertionError):
            Sop.from_text(text)


class TestSopReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference body parses, exposes its computed fields, and round-trips (ACC-001/ACC-002)."""

    def test_round_trips(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_title(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.text, "New Employee IT Account Provisioning")

    def test_all_sections_present(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.purpose)
        self.assertIn("Provision all IT accounts", sut.purpose.text)
        self.assertIsNotNone(sut.scope)
        self.assertIn("Contractors are out of scope", sut.scope.text)
        self.assertIsNotNone(sut.definitions)
        self.assertIsNotNone(sut.safety_and_precautions)
        self.assertIn("Verify the new hire's identity", sut.safety_and_precautions.text)
        self.assertIsNotNone(sut.more_information)
        self.assertIn("IT wiki", sut.more_information.text)

    def test_rasci_fields(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        rasci = sut.roles_and_responsibilities
        self.assertIsNotNone(rasci)
        self.assertEqual(rasci.accountable.value.text, "The IT Manager owns this procedure end to end.")
        self.assertEqual([item.text for item in rasci.responsible.items], ["Helpdesk Lead", "Identity Administrator"])
        # Support is present but empty (the demonstrated present-with-zero-items shape).
        self.assertIsNotNone(rasci.support)
        self.assertIsNone(rasci.support.items)
        self.assertEqual(
            [item.text for item in rasci.consulted.items], ["HR Business Partner", "Information Security Officer"]
        )
        self.assertEqual([item.text for item in rasci.informed.items], ["The new hire", "The hiring manager"])

    def test_steps_number_and_name_computed(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        self.assertEqual(
            [(step.number, step.name) for step in sut.procedure.steps],
            [(1, "Submit request"), (2, "Verify identity"), (4, "Provision accounts")],
        )

    def test_related_artifacts_sub_lists_present(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        related_artifacts = sut.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertEqual(
            [item.text for item in related_artifacts.requirements.items], ["REQ-0001: Day-one account readiness"]
        )
        self.assertEqual(
            [item.text for item in related_artifacts.decisions.items], ["DEC-0001: SSO provider selection"]
        )
        self.assertEqual([item.text for item in related_artifacts.goals.items], ["GOL-0001: Four-hour onboarding"])
        self.assertEqual(
            [item.text for item in related_artifacts.acceptance_criteria.items],
            ["ACC-0001: New hire can sign in on day one"],
        )
        self.assertEqual([item.text for item in related_artifacts.sops.items], ["SOP-0042: IT Account Deprovisioning"])

    def test_updates_entry_computed_fields(self) -> None:
        sut = Sop.from_text(_REFERENCE_TEXT)

        updates = sut.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 1)
        entry = updates.updates[0]
        self.assertEqual(entry.timestamp, "2026-08-30 14:30:00.000+02:00")
        self.assertEqual(entry.title, "Approved")
        self.assertIn("The IT Manager signed off", entry.content.text)


if __name__ == "__main__":
    unittest.main()
