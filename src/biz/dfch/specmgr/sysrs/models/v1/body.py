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

"""System Requirements Specification (SYSRS) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownSection2WithComment`/`MarkdownSection3`/`MarkdownParagraph`/
`MarkdownListItem`/`MarkdownListItemWithNotes` engine: each class below
models one markdown heading (`## `/`### `) or list, and `Sysrs` is the
top-level H1 container. A `sysrs` document aggregates already-existing
specmgr artifacts (`gol`, `prb`, `qa`, `uc`, `req`, `rsk`, `dec`/`adr`,
`vcr`) into one coherent, navigable specification via per-section
cross-reference lists, rather than duplicating their content -- see
`.specmgr/feat/feat-32-sysrs/README.md` Design Notes for the full
rationale and the "Phase 1 outcome record" for the exact engine mechanics
this module implements (no `models/md` engine changes).

Field declaration order on `Sysrs` enforces the markdown order (the
approved `example.v7.md` outline, 18 H2s in binding order):

```
System Purpose (M, leaf)
System Scope (M, leaf)
Business Context and Goals (M, container)
    Business Context (O, leaf)
    Goals (M, GOL list)
    Problem Statement (O, PRB list)
Stakeholder Needs and Elicitation (O, QA list)
Operational Concept and Scenarios (O, UC list)
Decisions (O, DEC|ADR list)
Risks (O, RSK list)
Assumptions and Dependencies (O, leaf)
System Overview (M, container)
    System Context (M, leaf)
    System Functions (M, leaf)
    User Characteristics (O, leaf)
    System Integration (O, leaf)
System Modes and States (O, leaf)
Requirements (M, container, >=1 of 9 H3s)
    Functional Suitability / Performance Efficiency / Compatibility /
    Interaction Capability / Reliability / Security / Maintainability /
    Flexibility / Safety (each O, REQ list)
Other Characteristics (O, umbrella, no >=1-of-N check)
    Physical Characteristics / Environmental Conditions /
    Information Management / Policy and Regulation /
    System Life Cycle Sustainment /
    Packaging, Handling, Shipping and Transportation (each O, REQ list)
Verification (O, VCR list)
References (O, plain bullet list, no type-tag regex)
More Information (O, leaf)
Appendix (O, leaf)
Definitions and Acronyms (O, leaf)
Updates (O, last, dynamic timestamp-led H3 entries)
```

since `models.md`'s `MarkdownStr.from_text` distributes text among declared
fields in that same order.
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, field_validator, model_validator

from ....models.md import (
    MarkdownListItem,
    MarkdownListItemWithNotes,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection2WithComment,
    MarkdownSection3,
    alias,
    AliasType,
)
from ....models.md._ordering import validate_newest_first

#: The standard lowercase 8-4-4-4-12 hex UUID shape, shared by every
#: cross-reference section's item-text pattern below -- the same
#: uuid-fragment style as the shipped `vcr` precedent
#: (`vcr.models.v1.body._VERIFIES_PATTERN`).
_UUID_PATTERN = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def _validate_cross_reference_items(
    items: list[MarkdownListItemWithNotes], pattern: str
) -> list[MarkdownListItemWithNotes]:
    """Enforce `pattern` against every item's `.text` (shared by every cross-reference list class below).

    `re.DOTALL` is required: an item's `.text` keeps the embedded newline of
    a soft-wrapped bullet line (`mdformat` does not reflow), and `.` would
    not otherwise match it -- confirmed empirically in Phase 1 (Task 1.1).
    The pattern itself is otherwise a plain `re.fullmatch` against the exact
    `<ALLOWED-TYPE-TAG(S)> <uuid>: <title>` shape.

    Args:
        items: The list's already-list-level-validated items (e.g.
            `Field(min_length=1)` has already run).
        pattern: The calling class's own module-level pattern constant.

    Returns:
        `items`, unchanged, once every item matches.

    Raises:
        ValueError: some item's `.text` does not fullmatch `pattern` --
            channeled by Pydantic into `pydantic.ValidationError`.
    """
    for item in items:
        if not re.fullmatch(pattern, item.text, re.DOTALL):
            raise ValueError(f"item must match pattern {pattern!r}, got {item.text!r}")
    return items


class SystemPurpose(MarkdownSection2):
    """`## System Purpose` -- the reason the system is being developed or
    modified (29148 §9.5.2). Mandatory, free-form prose (DEC's `Context`/
    SOP's `Purpose` precedent: opaque free text, no declared nested
    fields).
    """


class SystemScope(MarkdownSection2):
    """`## System Scope` -- what the system will and will not do; results of
    the earlier needs analysis (29148 §9.5.3). Mandatory, free-form prose.
    """


class BusinessContext(MarkdownSection3):
    """`### Business Context` under `## Business Context and Goals` --
    free-form prose describing the business situation driving this
    specification (BRS §9.3.2/9.3.7; StRS §9.4.2/9.4.7). Optional; may not
    exist at creation time.
    """


#: Matches `### Goals`' bullet item text: `GOL <uuid>: <title>` (REQ-006).
_GOALS_PATTERN = rf"^GOL {_UUID_PATTERN}: .+$"


class Goals(MarkdownSection3):
    """`### Goals` under `## Business Context and Goals` -- cross-reference
    list to `gol`. Mandatory once the container is present, at least one
    item.

    Parameters
    ----------
    items:
        Bullet list of `GOL <uuid>: <title>` cross-references, each
        optionally followed by an indented notes paragraph (the
        `MarkdownListItemWithNotes` shape, REQ-003). Must contain at least
        one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `GOL <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _GOALS_PATTERN)


#: Matches `### Problem Statement`'s bullet item text: `PRB <uuid>: <title>`.
_PROBLEM_STATEMENT_PATTERN = rf"^PRB {_UUID_PATTERN}: .+$"


class ProblemStatement(MarkdownSection3):
    """`### Problem Statement` under `## Business Context and Goals` --
    cross-reference list to `prb`. Optional as a whole (not every system
    has a formal problem statement); at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `PRB <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `PRB <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _PROBLEM_STATEMENT_PATTERN)


@alias(value="Business Context and Goals", type=AliasType.LITERAL)
class BusinessContextAndGoals(MarkdownSection2):
    """`## Business Context and Goals` -- umbrella for the BRS/StRS content
    borrowed into this document (BRS §9.3.2/9.3.7; StRS §9.4.2/9.4.7).
    Mandatory.

    The class name `BusinessContextAndGoals` does not match the heading's
    exact wording (lowercase "and"), so the alias is pinned LITERAL (the
    implicit `SPACE_SEPARATED` alias would expect "Business Context And
    Goals").

    Parameters
    ----------
    business_context:
        `### Business Context` sub-section (free-form prose). Optional.
    goals:
        `### Goals` sub-section (cross-reference list to `gol`, >=1 item).
        Mandatory once this container is present.
    problem_statement:
        `### Problem Statement` sub-section (cross-reference list to
        `prb`, >=1 item when present). Optional.
    """

    business_context: BusinessContext | None = Field(
        default=None, description="`### Business Context` sub-section. Optional."
    )
    goals: Goals = Field(
        description="`### Goals` sub-section (cross-reference list to `gol`, >=1 item). "
        "Mandatory once this container is present."
    )
    problem_statement: ProblemStatement | None = Field(
        default=None,
        description="`### Problem Statement` sub-section (cross-reference list to `prb`, >=1 item when present). "
        "Optional.",
    )


#: Matches `## Stakeholder Needs and Elicitation`'s bullet item text: `QA <uuid>: <title>`.
_STAKEHOLDER_NEEDS_PATTERN = rf"^QA {_UUID_PATTERN}: .+$"


@alias(value="Stakeholder Needs and Elicitation", type=AliasType.LITERAL)
class StakeholderNeedsAndElicitation(MarkdownSection2):
    """`## Stakeholder Needs and Elicitation` -- cross-reference list to
    `qa` (StRS §9.4.5/9.4.15). Optional as a whole (elicitation artifacts
    may not exist yet at first drafting); at least one item when present.

    The class name's implicit `SPACE_SEPARATED` derivation would expect
    "Stakeholder Needs And Elicitation" (capitalized "And"), so the alias
    is pinned LITERAL to the lowercase "and" the heading actually uses.

    Parameters
    ----------
    items:
        Bullet list of `QA <uuid>: <title>` cross-references. Must contain
        at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `QA <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _STAKEHOLDER_NEEDS_PATTERN)


#: Matches `## Operational Concept and Scenarios`'s bullet item text: `UC <uuid>: <title>`.
_OPERATIONAL_CONCEPT_PATTERN = rf"^UC {_UUID_PATTERN}: .+$"


@alias(value="Operational Concept and Scenarios", type=AliasType.LITERAL)
class OperationalConceptAndScenarios(MarkdownSection2):
    """`## Operational Concept and Scenarios` -- cross-reference list to
    `uc` (StRS §9.4.16/9.4.17; ConOps/OpsCon §5.4/Annex A). Optional as a
    whole; at least one item when present.

    The class name's implicit `SPACE_SEPARATED` derivation would expect
    "Operational Concept And Scenarios" (capitalized "And"), so the alias
    is pinned LITERAL to the lowercase "and" the heading actually uses.

    Parameters
    ----------
    items:
        Bullet list of `UC <uuid>: <title>` cross-references. Must contain
        at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `UC <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _OPERATIONAL_CONCEPT_PATTERN)


#: Matches `## Decisions`'s bullet item text: `DEC <uuid>: <title>` OR `ADR <uuid>: <title>`
#: (real `sysrs` documents may cross-reference either `dec` or `adr` ids, decided 2026-08-30).
_DECISIONS_PATTERN = rf"^(DEC|ADR) {_UUID_PATTERN}: .+$"


class Decisions(MarkdownSection2):
    """`## Decisions` -- cross-reference list to `dec`/`adr` -- architecture/
    design choices made in service of the requirements below. Optional as
    a whole; at least one item when present. No 29148 clause (specmgr
    addition).

    Parameters
    ----------
    items:
        Bullet list of `DEC <uuid>: <title>` or `ADR <uuid>: <title>`
        cross-references. Must contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `DEC <uuid>: <title>` or `ADR <uuid>: <title>` cross-references; "
        "must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _DECISIONS_PATTERN)


#: Matches `## Risks`'s bullet item text: `RSK <uuid>: <title>`.
_RISKS_PATTERN = rf"^RSK {_UUID_PATTERN}: .+$"


class Risks(MarkdownSection2):
    """`## Risks` -- cross-reference list to `rsk`. Optional as a whole; at
    least one item when present. No 29148 clause.

    Parameters
    ----------
    items:
        Bullet list of `RSK <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `RSK <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _RISKS_PATTERN)


@alias(value="Assumptions and Dependencies", type=AliasType.LITERAL)
class AssumptionsAndDependencies(MarkdownSection2):
    """`## Assumptions and Dependencies` -- assumptions/dependencies to take
    into account when allocating and deriving lower-level requirements
    (29148 §9.5.19). Optional, free-form prose (may mix paragraphs and
    bullets).

    The class name's implicit `SPACE_SEPARATED` derivation would expect
    "Assumptions And Dependencies" (capitalized "And"), so the alias is
    pinned LITERAL to the lowercase "and" the heading actually uses.
    """


class SystemContext(MarkdownSection3):
    """`### System Context` under `## System Overview` -- major elements
    incl. human elements and all significant interfaces crossing the
    system boundary (29148 §9.5.4.1). Mandatory, free-form prose (diagram
    recommended; fenced code blocks, e.g. ```mermaid, are accepted
    verbatim).
    """


class SystemFunctions(MarkdownSection3):
    """`### System Functions` under `## System Overview` -- major system
    capabilities, conditions, constraints (29148 §9.5.4.2). Mandatory,
    free-form prose.
    """


class UserCharacteristics(MarkdownSection3):
    """`### User Characteristics` under `## System Overview` -- roles /
    user-operator-maintainer classes, numbers, nature of use (29148
    §9.5.4.3). Optional, free-form prose.
    """


class SystemIntegration(MarkdownSection3):
    """`### System Integration` under `## System Overview` -- integration
    sequence/dependencies across subsystems, interface control points.
    Optional, free-form prose. No 29148 clause (specmgr addition).
    """


class SystemOverview(MarkdownSection2):
    """`## System Overview` -- umbrella for the system's context, functions,
    users, and integration (29148 §9.5.4). Mandatory.

    Parameters
    ----------
    system_context:
        `### System Context` sub-section. Mandatory once this container
        is present.
    system_functions:
        `### System Functions` sub-section. Mandatory once this container
        is present.
    user_characteristics:
        `### User Characteristics` sub-section. Optional.
    system_integration:
        `### System Integration` sub-section. Optional.
    """

    system_context: SystemContext = Field(
        description="`### System Context` sub-section. Mandatory once this container is present."
    )
    system_functions: SystemFunctions = Field(
        description="`### System Functions` sub-section. Mandatory once this container is present."
    )
    user_characteristics: UserCharacteristics | None = Field(
        default=None, description="`### User Characteristics` sub-section. Optional."
    )
    system_integration: SystemIntegration | None = Field(
        default=None, description="`### System Integration` sub-section. Optional."
    )


@alias(value="System Modes and States", type=AliasType.LITERAL)
class SystemModesAndStates(MarkdownSection2):
    """`## System Modes and States` -- the standard itself is conditional:
    "if the system can exist in various operational modes or states,
    define these" (29148 §9.5.10). Optional, free-form prose.

    The class name's implicit `SPACE_SEPARATED` derivation would expect
    "System Modes And States" (capitalized "And"), so the alias is pinned
    LITERAL to the lowercase "and" the heading actually uses.
    """


#: Matches every `## Requirements`/`## Other Characteristics` H3's bullet item
#: text: `REQ <uuid>: <title>` (REQ-006).
_REQ_PATTERN = rf"^REQ {_UUID_PATTERN}: .+$"


class FunctionalSuitability(MarkdownSection3):
    """`### Functional Suitability` under `## Requirements` -- cross-reference
    list to `req` (29148 §9.5.5 functional). Optional; at least one item
    when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class PerformanceEfficiency(MarkdownSection3):
    """`### Performance Efficiency` under `## Requirements` -- cross-reference
    list to `req` (29148 §9.5.7). Optional; at least one item when
    present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Compatibility(MarkdownSection3):
    """`### Compatibility` under `## Requirements` -- cross-reference list to
    `req` (29148 §9.5.8 interfaces -> Interoperability; §9.5.9.4 other
    quality). Optional; at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class InteractionCapability(MarkdownSection3):
    """`### Interaction Capability` under `## Requirements` -- cross-reference
    list to `req` (29148 §9.5.6 usability; §9.5.9.1 human system
    integration). Optional; at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Reliability(MarkdownSection3):
    """`### Reliability` under `## Requirements` -- cross-reference list to
    `req` (29148 §9.5.9.3). Optional; at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Security(MarkdownSection3):
    """`### Security` under `## Requirements` -- cross-reference list to
    `req` (29148 §9.5.13). Optional; at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Maintainability(MarkdownSection3):
    """`### Maintainability` under `## Requirements` -- cross-reference list
    to `req` (29148 §9.5.9.2). Optional; at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Flexibility(MarkdownSection3):
    """`### Flexibility` under `## Requirements` -- cross-reference list to
    `req` (29148 §9.5.9.4; the 25010:2023 rename of Portability). Optional;
    at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Safety(MarkdownSection3):
    """`### Safety` under `## Requirements` -- cross-reference list to `req`
    (no 29148 §9.5 clause; 25010:2023 addition). Optional; at least one
    item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class Requirements(MarkdownSection2):
    """`## Requirements` -- the document's reason for existing: the nine
    ISO/IEC 25010:2023 product-quality characteristics in canonical model
    order, each a cross-reference list to `req`, grouped by the REQ's
    first `## Characteristics` item (the placement rule, see
    `example.v7.md`'s header comment). Mandatory as a whole; at least one
    of the nine H3s must be present.

    Parameters
    ----------
    functional_suitability, performance_efficiency, compatibility,
    interaction_capability, reliability, security, maintainability,
    flexibility, safety:
        The nine canonical ISO/IEC 25010:2023 characteristic sub-sections,
        in that fixed (parse-enforced) order. Each independently optional,
        but at least one of the nine must be present (`_validate_at_least_one_present`).
    """

    functional_suitability: FunctionalSuitability | None = Field(
        default=None, description="`### Functional Suitability` sub-section. Optional."
    )
    performance_efficiency: PerformanceEfficiency | None = Field(
        default=None, description="`### Performance Efficiency` sub-section. Optional."
    )
    compatibility: Compatibility | None = Field(default=None, description="`### Compatibility` sub-section. Optional.")
    interaction_capability: InteractionCapability | None = Field(
        default=None, description="`### Interaction Capability` sub-section. Optional."
    )
    reliability: Reliability | None = Field(default=None, description="`### Reliability` sub-section. Optional.")
    security: Security | None = Field(default=None, description="`### Security` sub-section. Optional.")
    maintainability: Maintainability | None = Field(
        default=None, description="`### Maintainability` sub-section. Optional."
    )
    flexibility: Flexibility | None = Field(default=None, description="`### Flexibility` sub-section. Optional.")
    safety: Safety | None = Field(default=None, description="`### Safety` sub-section. Optional.")

    @model_validator(mode="after")
    def _validate_at_least_one_present(self) -> Requirements:
        """Reject a `## Requirements` container with none of the nine H3s present.

        Decided 2026-09-02 (see `.specmgr/feat/feat-32-sysrs/README.md`
        Decisions Made): this `assert`-based `model_validator(mode="after")`
        surfaces as `pydantic.ValidationError` (Pydantic wraps a validator's
        `AssertionError`) -- `sysrs` matches every other domain's identical-
        shape check (e.g. SOP/DEC/VCR/TSK's own `Updates` ordering checks)
        rather than special-casing itself via a `from_text`-override
        `AssertionError`.
        """
        assert any(
            (
                self.functional_suitability,
                self.performance_efficiency,
                self.compatibility,
                self.interaction_capability,
                self.reliability,
                self.security,
                self.maintainability,
                self.flexibility,
                self.safety,
            )
        ), "Requirements: at least one of the nine characteristic sub-sections must be present"
        return self


class PhysicalCharacteristics(MarkdownSection3):
    """`### Physical Characteristics` under `## Other Characteristics` --
    cross-reference list to `req` (29148 §9.5.11). Optional; at least one
    item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class EnvironmentalConditions(MarkdownSection3):
    """`### Environmental Conditions` under `## Other Characteristics` --
    cross-reference list to `req` (29148 §9.5.12). Optional; at least one
    item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class InformationManagement(MarkdownSection3):
    """`### Information Management` under `## Other Characteristics` --
    cross-reference list to `req` (29148 §9.5.14). Optional; at least one
    item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


@alias(value="Policy and Regulation", type=AliasType.LITERAL)
class PolicyAndRegulation(MarkdownSection3):
    """`### Policy and Regulation` under `## Other Characteristics` --
    cross-reference list to `req` (29148 §9.5.15). Optional; at least one
    item when present.

    The class name's implicit `SPACE_SEPARATED` derivation would expect
    "Policy And Regulation" (capitalized "And"), so the alias is pinned
    LITERAL to the lowercase "and" the heading actually uses.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class SystemLifeCycleSustainment(MarkdownSection3):
    """`### System Life Cycle Sustainment` under `## Other Characteristics` --
    cross-reference list to `req` (29148 §9.5.16). Optional; at least one
    item when present.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


@alias(value="Packaging, Handling, Shipping and Transportation", type=AliasType.LITERAL)
class PackagingHandlingShippingAndTransportation(MarkdownSection3):
    """`### Packaging, Handling, Shipping and Transportation` under `##
    Other Characteristics` -- cross-reference list to `req` (29148
    §9.5.17). Optional; at least one item when present.

    The class name's implicit `SPACE_SEPARATED` derivation would produce
    "Packaging Handling Shipping And Transportation" (no commas,
    capitalized "And"), so the alias is pinned LITERAL to the heading's
    actual comma-separated, lowercase-"and" wording.

    Parameters
    ----------
    items:
        Bullet list of `REQ <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `REQ <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _REQ_PATTERN)


class OtherCharacteristics(MarkdownSection2):
    """`## Other Characteristics` -- umbrella for 29148 §9.5.11-9.5.17 -- the
    requirement categories that are NOT 25010 characteristics. Optional as
    a whole (omit if none of the six apply, e.g. no packaging for
    cloud-hosted software); **no** >=1-of-N validator, unlike
    `Requirements` -- the whole umbrella is optional.

    Parameters
    ----------
    physical_characteristics, environmental_conditions,
    information_management, policy_and_regulation,
    system_life_cycle_sustainment,
    packaging_handling_shipping_and_transportation:
        The six sub-sections, in that fixed (parse-enforced) order. Each
        independently optional.
    """

    physical_characteristics: PhysicalCharacteristics | None = Field(
        default=None, description="`### Physical Characteristics` sub-section. Optional."
    )
    environmental_conditions: EnvironmentalConditions | None = Field(
        default=None, description="`### Environmental Conditions` sub-section. Optional."
    )
    information_management: InformationManagement | None = Field(
        default=None, description="`### Information Management` sub-section. Optional."
    )
    policy_and_regulation: PolicyAndRegulation | None = Field(
        default=None, description="`### Policy and Regulation` sub-section. Optional."
    )
    system_life_cycle_sustainment: SystemLifeCycleSustainment | None = Field(
        default=None, description="`### System Life Cycle Sustainment` sub-section. Optional."
    )
    packaging_handling_shipping_and_transportation: PackagingHandlingShippingAndTransportation | None = Field(
        default=None,
        description="`### Packaging, Handling, Shipping and Transportation` sub-section. Optional.",
    )


#: Matches `## Verification`'s bullet item text: `VCR <uuid>: <title>`.
_VERIFICATION_PATTERN = rf"^VCR {_UUID_PATTERN}: .+$"


class Verification(MarkdownSection2):
    """`## Verification` -- cross-reference list to `vcr` (Verification
    Case Records). Optional as a whole (an early document may legitimately
    have no VCRs yet); at least one item when present.

    Parameters
    ----------
    items:
        Bullet list of `VCR <uuid>: <title>` cross-references. Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `VCR <uuid>: <title>` cross-references; must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        return _validate_cross_reference_items(items, _VERIFICATION_PATTERN)


class References(MarkdownSection2):
    """`## References` -- free-form bullet list of external standards/
    documents (no specmgr ids, no per-item type-tag regex) -- mirrors
    29148's own "5 References". Optional as a whole; present implies at
    least one item (user-confirmed 2026-09-01: a bare heading with zero
    bullets is a structural error, consistent with every other list
    section in the codebase).

    Parameters
    ----------
    items:
        Plain bullet list of external references (the no-notes
        `MarkdownListItem` variant, unlike every cross-reference list
        above). Must contain at least one item.
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Plain bullet list of external references; must contain at least one item.",
    )


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no
    fixed format. Optional. Mirrors `dec`/`sop`/`vcr`'s own `## More
    Information`.
    """


class Appendix(MarkdownSection2):
    """`## Appendix` -- supplementary material that does not belong in any
    other section, e.g. large diagrams, worked examples, extended
    interface descriptions. Optional, free-form prose (fenced code
    blocks, e.g. ```mermaid, are accepted verbatim). No 29148 clause
    (user addition).
    """


@alias(value="Definitions and Acronyms", type=AliasType.LITERAL)
class DefinitionsAndAcronyms(MarkdownSection2):
    """`## Definitions and Acronyms` -- list of abbreviations used in this
    document (e.g. API, MVP, SLA). Optional, free-form prose. No 29148
    clause (user addition).

    The class name's implicit `SPACE_SEPARATED` derivation would expect
    "Definitions And Acronyms" (capitalized "And"), so the alias is pinned
    LITERAL to the lowercase "and" the heading actually uses.
    """


#: Matches a `{yyyy-MM-dd or full date+time} ( - | : ) {title}` heading line
#: as retained in a composite `MarkdownSection3`'s `.text` (the heading's
#: inline content, no `###` marker), capturing the timestamp (named group
#: `timestamp`) and the title (named group `title`). Mirrors
#: `vcr.models.v1.body._UPDATE_ENTRY_HEADING_PATTERN`/
#: `dec.models.v1.body._UPDATE_ENTRY_HEADING_PATTERN` exactly -- the locked
#: post-sibling `## Updates` shape (feat-38-39-41-43-44 D2/D3), adopted by
#: `sysrs` from day one.
_UPDATE_ENTRY_HEADING_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))?)(?: - | : )(?P<title>.+)"
)


@alias(
    value=r"^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))?(?: - | : ).+$",
    type=AliasType.REGEX,
)
class UpdateEntry(MarkdownSection3):
    """`### {timestamp} ( - | : ) {title}` under `## Updates` -- one update
    entry (a change to the `sysrs` document itself, not to the system it
    specifies).

    The H3 heading text carries a timestamp and a title, joined by either
    ``" - "`` (space, hyphen, space) or ``" : "`` (space, colon, space):
    e.g. `### 2026-08-31 - Created` or
    `### 2026-08-31 07:40:12.500+02:00 : Created`. The em-dash separator is
    rejected. The timestamp is either a bare ``yyyy-MM-dd`` date or the
    full ``yyyy-MM-dd HH:mm:ss.fff`` + explicit UTC offset (``+02:00``,
    ``-05:00``) or ``Z`` for UTC variant. Mirrors DEC's/VCR's `UpdateEntry`
    shape exactly (feat-38-39-41-43-44 D2/D3, adopted from day one).

    Parameters
    ----------
    content:
        The lead paragraph right after the H3 heading -- this entry's own
        update text. Mandatory.
    timestamp:
        Computed. The timestamp carried by the heading, verbatim. Never
        stored separately -- derived from the retained heading text.
    title:
        Computed. The title carried by the heading (the text after
        ``" - "``/``" : "``). Never stored separately -- derived from the
        retained heading text.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The timestamp carried by this heading (e.g. `2026-08-31` or `2026-08-31 07:40:12.500+02:00`).

        Returns:
            The timestamp string parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The title carried by this heading (e.g. `Created` for `### 2026-08-31 - Created`).

        Returns:
            The title parsed from the retained heading text (the text
            after ``" - "``/``" : "``).

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("title")
        return result


class Updates(MarkdownSection2WithComment):
    """`## Updates` -- a dynamic, newest-first list of timestamp-led `### `
    update entries. Optional as a whole, and the last section of the
    document if present. May be preceded by an explanatory HTML comment
    (e.g. an ordering hint).

    Mirrors `dec`/`sop`/`vcr`'s `Updates` container shape exactly: no
    dedicated per-entry tools -- entries are prepended (newest-first) by
    editing the whole body.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`), e.g.
        `<!-- Newest entry first -- prepend new entries directly below
        this comment. -->`. Inherited from `MarkdownSection2WithComment`.
    updates:
        The dynamic collection of `### ` entries, in document order,
        newest-first (enforced, see `_validate_newest_first`). Requires
        at least one entry (``min_length=1``) -- an H2 with zero entries
        is a structural error.
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `### {timestamp} ( - | : ) {title}` entries, in document order, "
        "newest-first. Must contain at least one entry.",
    )

    @model_validator(mode="after")
    def _validate_newest_first(self) -> Updates:
        """Reject entries that are not in newest-first order.

        Delegates to the shared `models.md._ordering.validate_newest_first`
        helper (mixed date-only/date+time day-granularity rule, equal
        values allowed) -- mirrors `sop`/`dec`/`vcr`'s own
        `Updates._validate_newest_first` without duplicating its logic.
        The `assert` inside that helper surfaces as `pydantic.ValidationError`
        here (a `model_validator(mode="after")` `assert`, per the 2026-09-02
        decision -- see this class's module docstring and
        `Requirements._validate_at_least_one_present`). Raises on the first
        out-of-order pair.
        """
        validate_newest_first([update.timestamp for update in self.updates], "Updates")
        return self


@alias(value=r"^System Requirements Specification: .+$", type=AliasType.REGEX)
class Sysrs(MarkdownSection1):
    """The `sysrs` body: a single H1 section with the fields below.

    The H1 heading text is mandated to start with `System Requirements
    Specification: ` (unlike every other domain's free-form H1) --
    REQ-005.

    Parameters
    ----------
    system_purpose:
        `## System Purpose`. Mandatory.
    system_scope:
        `## System Scope`. Mandatory.
    business_context_and_goals:
        `## Business Context and Goals`. Mandatory.
    stakeholder_needs_and_elicitation:
        `## Stakeholder Needs and Elicitation`. Optional.
    operational_concept_and_scenarios:
        `## Operational Concept and Scenarios`. Optional.
    decisions:
        `## Decisions`. Optional.
    risks:
        `## Risks`. Optional.
    assumptions_and_dependencies:
        `## Assumptions and Dependencies`. Optional.
    system_overview:
        `## System Overview`. Mandatory.
    system_modes_and_states:
        `## System Modes and States`. Optional.
    requirements:
        `## Requirements` (>=1 of 9 characteristic sub-sections).
        Mandatory.
    other_characteristics:
        `## Other Characteristics`. Optional.
    verification:
        `## Verification`. Optional.
    references:
        `## References`. Optional.
    more_information:
        `## More Information`. Optional.
    appendix:
        `## Appendix`. Optional.
    definitions_and_acronyms:
        `## Definitions and Acronyms`. Optional.
    updates:
        `## Updates` (>=1 entry if present). Optional; last section.
    """

    system_purpose: SystemPurpose = Field(description="`## System Purpose` section. Mandatory.")
    system_scope: SystemScope = Field(description="`## System Scope` section. Mandatory.")
    business_context_and_goals: BusinessContextAndGoals = Field(
        description="`## Business Context and Goals` section. Mandatory."
    )
    stakeholder_needs_and_elicitation: StakeholderNeedsAndElicitation | None = Field(
        default=None, description="`## Stakeholder Needs and Elicitation` section. Optional."
    )
    operational_concept_and_scenarios: OperationalConceptAndScenarios | None = Field(
        default=None, description="`## Operational Concept and Scenarios` section. Optional."
    )
    decisions: Decisions | None = Field(default=None, description="`## Decisions` section. Optional.")
    risks: Risks | None = Field(default=None, description="`## Risks` section. Optional.")
    assumptions_and_dependencies: AssumptionsAndDependencies | None = Field(
        default=None, description="`## Assumptions and Dependencies` section. Optional."
    )
    system_overview: SystemOverview = Field(description="`## System Overview` section. Mandatory.")
    system_modes_and_states: SystemModesAndStates | None = Field(
        default=None, description="`## System Modes and States` section. Optional."
    )
    requirements: Requirements = Field(description="`## Requirements` section (>=1 of 9 sub-sections). Mandatory.")
    other_characteristics: OtherCharacteristics | None = Field(
        default=None, description="`## Other Characteristics` section. Optional."
    )
    verification: Verification | None = Field(default=None, description="`## Verification` section. Optional.")
    references: References | None = Field(default=None, description="`## References` section. Optional.")
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
    appendix: Appendix | None = Field(default=None, description="`## Appendix` section. Optional.")
    definitions_and_acronyms: DefinitionsAndAcronyms | None = Field(
        default=None, description="`## Definitions and Acronyms` section. Optional."
    )
    updates: Updates | None = Field(default=None, description="`## Updates` section. Optional; last.")
