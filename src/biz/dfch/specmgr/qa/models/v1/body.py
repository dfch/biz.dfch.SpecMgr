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

"""Question and Answer (QA) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownSection2WithComment`/`MarkdownSection3`/`MarkdownSection3WithComment`/
`MarkdownSection4`/`MarkdownBlockQuote`/`MarkdownParagraph`/`MarkdownStr`
engine, mirroring `req/models/v1/body.py`'s "one class per heading" shape.
`Qa` is the top-level H1 container:

```
# {H1 title}                                   Qa (free-form title)

## General                                     general: General
### Introduction                                introduction: Introduction
<!-- optional comment -->
{intro paragraphs}
### Raw Requirements                            raw_requirements: RawRequirements
{opaque raw text}

## Functional Suitability                       functional_suitability: FunctionalSuitability
### {free-form Q&A heading}                     items: list[QaSection] | None
<!-- optional comment -->
#### Requirement                                requirement: Requirement | None
{opaque agent-authored content}
> {question}                                    question: MarkdownBlockQuote | None
{opaque answer prose}                           answer: QaAnswer | None
...

## Performance Efficiency                        performance_efficiency: PerformanceEfficiency
## Compatibility                                 compatibility: Compatibility
## Interaction Capability                        interaction_capability: InteractionCapability
## Reliability                                   reliability: Reliability
## Security                                      security: Security
## Maintainability                               maintainability: Maintainability
## Flexibility                                   flexibility: Flexibility
## Safety                                        safety: Safety

## More Information                             more_information: MoreInformation | None
{opaque raw text}
```

Field declaration order on `Qa` enforces markdown order (title -> `general`
-> the 9 ISO/IEC 25010:2023 characteristics, in their canonical order ->
`more_information`), since `models.md`'s `MarkdownStr.from_text` distributes
text among declared fields in that same order.

**The 9 `<QaCategory>` classes (`FunctionalSuitability`, ..., `Safety`) share
one private intermediate base, `_QaCategory`**, declaring `items` once,
rather than each independently redeclaring it -- see the feature README's
Decisions Made for the empirically-verified rationale (each final subclass's
own `__name__`, not `_QaCategory`'s, is what `@markdown`'s inherited
`_metadata` and the implicit `AliasType.SPACE_SEPARATED` alias derivation
key off, so sharing the base does not risk any heading-detection ambiguity
between the 9 siblings).
"""

from __future__ import annotations

from pydantic import Field, computed_field

from ....models.md import (
    MarkdownBlockQuote,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection2WithComment,
    MarkdownSection3,
    MarkdownSection3WithComment,
    MarkdownSection4,
    MarkdownStr,
    alias,
    AliasType,
    markdown,
)

# --------------------------------------------------------------------------
# `## General`
# --------------------------------------------------------------------------


class Introduction(MarkdownSection3WithComment):
    """`### Introduction` under `## General` -- free-form prose framing the interview. Mandatory.

    `comment` is inherited from `MarkdownSection3WithComment` -- not redeclared
    here, per this project's established "inherit rather than redeclare"
    idiom (see e.g. TSK's `Task`, REQ's `Level`/`Priority`).
    """

    body: list[MarkdownParagraph] | None = Field(
        default=None, description="Free-form introductory prose paragraphs. Optional."
    )


class RawRequirements(MarkdownSection3):
    """`### Raw Requirements` under `## General` -- free-form, pre-existing raw requirement notes.

    Leaf class (no declared fields), mirroring `MoreInformation`/`Notes`:
    captures whatever markdown text follows the heading verbatim, with no
    further structure imposed.
    """


class General(MarkdownSection2WithComment):
    """`## General` -- introductory framing for the interview. Mandatory (always present).

    `comment` is inherited from `MarkdownSection2WithComment` -- not
    redeclared here.

    Parameters
    ----------
    introduction:
        `### Introduction`. Mandatory.
    raw_requirements:
        `### Raw Requirements`. Mandatory.
    """

    introduction: Introduction = Field(description="`### Introduction` section. Mandatory.")
    raw_requirements: RawRequirements = Field(description="`### Raw Requirements` section. Mandatory.")


# --------------------------------------------------------------------------
# Repeating `QaSection` (`### {free-form heading}`) Q&A pairs
# --------------------------------------------------------------------------


@markdown(end_marker=MarkdownBlockQuote)
class Requirement(MarkdownSection4):
    """`#### Requirement` -- an optional callout promoting a Q&A pair's answer to a concrete requirement.

    Leaf class (no declared fields): its content is deliberately
    unspecified/arbitrary agent-authored data, not shaped like REQ's own
    `Requirement` fields (`statement`/`characteristics`/`level`/...) and not
    a placeholder for future structure -- see the feature README's Design
    Notes.

    The heading text is fixed (``"Requirement"``, matching the implicit
    `AliasType.SPACE_SEPARATED` derivation of this class's own name), not
    free-form -- confirmed against `qa_reference.md`'s literal ``#### Requirement``
    heading.

    Decorated `@markdown(end_marker=MarkdownBlockQuote)` (Phase 1's new
    mechanism, merging into `MarkdownSection4`'s already-inherited
    `_metadata` rather than replacing it -- `type`/`tag` do not need to be
    re-passed here): since `requirement` is declared *before* `question` on
    `QaSection` below, `Requirement.get_extent` must stop at the next
    depth-0 block quote, not just the next heading, or it would silently
    absorb `question`'s own block quote into its own content.
    """


class QaAnswer(MarkdownStr):
    """One `QaSection`'s free-form prose answer.

    Deliberately **not** heading-anchored, unlike `RawRequirements`/
    `MoreInformation` (which each own a fixed `##`/`###` heading of their
    own): in the schema, `answer` is simply the trailing prose that follows
    `question`'s block quote within the same `QaSection`, with no heading of
    its own (verified against `qa_reference.md` -- no `#### Answer`/similar
    heading appears anywhere). A bare `MarkdownStr` subclass with no
    `@markdown` metadata already captures "everything remaining" verbatim in
    `_value` via the base class's own `get_extent` (no heading-level stop
    condition applies), exactly the leaf behavior this field needs.

    Adds a `text` computed property (mirroring `MarkdownParagraph.text`/
    `MarkdownSection.text`/`MarkdownCodeBlock.text`'s established pattern) so
    this otherwise-private `_value` is reachable through `model_dump()`/
    `model_dump_json()` -- the same serialization path an MCP tool's return
    value goes through.
    """

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Return this answer's raw markdown text verbatim (or ``""`` if unset)."""
        return self._value


@alias(value=".+", type=AliasType.REGEX)
class QaSection(MarkdownSection3WithComment):
    """`### {free-form heading}` -- one question/answer pair. Free-form H3 heading.

    `comment` is inherited from `MarkdownSection3WithComment` -- not
    redeclared here. All four fields (`comment`, `requirement`, `question`,
    `answer`) are fully optional.

    Parameters
    ----------
    requirement:
        `#### Requirement` callout. Optional.
    question:
        The interviewer's question, as a block quote. Optional.
    answer:
        The interviewee's free-form prose answer. Optional.
    """

    requirement: Requirement | None = Field(default=None, description="`#### Requirement` callout. Optional.")
    question: MarkdownBlockQuote | None = Field(
        default=None, description="The interviewer's question, as a block quote. Optional."
    )
    answer: QaAnswer | None = Field(default=None, description="Free-form prose answer. Optional.")


# --------------------------------------------------------------------------
# The 9 ISO/IEC 25010:2023 quality-characteristic categories
# --------------------------------------------------------------------------


class _QaCategory(MarkdownSection2):
    """Private, non-instantiable-in-practice intermediate base for the 9 `<QaCategory>` H2 sections.

    Declares `items` exactly once; each of the 9 final subclasses below
    relies on the implicit `AliasType.SPACE_SEPARATED` derivation of its own
    class name (e.g. `FunctionalSuitability` -> ``"Functional Suitability"``)
    for its heading match, with no field redeclaration and no per-subclass
    `@alias`/`@markdown` re-application needed -- `@markdown`'s
    `heading_open`/`h2` metadata and `_get_field_names()`'s field
    introspection are both inherited correctly through this extra level
    (empirically verified; see the feature README's Decisions Made for the
    9-category class-sharing rationale).
    """

    items: list[QaSection] | None = Field(
        default=None, description="Repeating Q&A pairs for this category. May be empty/absent."
    )


class FunctionalSuitability(_QaCategory):
    """`## Functional Suitability` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class PerformanceEfficiency(_QaCategory):
    """`## Performance Efficiency` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class Compatibility(_QaCategory):
    """`## Compatibility` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class InteractionCapability(_QaCategory):
    """`## Interaction Capability` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class Reliability(_QaCategory):
    """`## Reliability` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class Security(_QaCategory):
    """`## Security` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class Maintainability(_QaCategory):
    """`## Maintainability` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class Flexibility(_QaCategory):
    """`## Flexibility` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


class Safety(_QaCategory):
    """`## Safety` -- one of the 9 ISO/IEC 25010:2023 quality characteristics. Always present."""


# --------------------------------------------------------------------------
# `## More Information`
# --------------------------------------------------------------------------


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no fixed format. Optional."""


# --------------------------------------------------------------------------
# `Qa`: the top-level H1 container
# --------------------------------------------------------------------------


@alias(value=".+", type=AliasType.REGEX)
class Qa(MarkdownSection1):
    """The `qa` body: a single H1 section with the fields below.

    The H1 heading text is free-form.

    Parameters
    ----------
    general:
        `## General`. Mandatory (always present).
    functional_suitability:
        `## Functional Suitability`. Mandatory (always present; `items` may be empty).
    performance_efficiency:
        `## Performance Efficiency`. Mandatory (always present; `items` may be empty).
    compatibility:
        `## Compatibility`. Mandatory (always present; `items` may be empty).
    interaction_capability:
        `## Interaction Capability`. Mandatory (always present; `items` may be empty).
    reliability:
        `## Reliability`. Mandatory (always present; `items` may be empty).
    security:
        `## Security`. Mandatory (always present; `items` may be empty).
    maintainability:
        `## Maintainability`. Mandatory (always present; `items` may be empty).
    flexibility:
        `## Flexibility`. Mandatory (always present; `items` may be empty).
    safety:
        `## Safety`. Mandatory (always present; `items` may be empty).
    more_information:
        `## More Information`. Optional.
    """

    general: General = Field(description="`## General` section. Mandatory.")
    functional_suitability: FunctionalSuitability = Field(description="`## Functional Suitability` section.")
    performance_efficiency: PerformanceEfficiency = Field(description="`## Performance Efficiency` section.")
    compatibility: Compatibility = Field(description="`## Compatibility` section.")
    interaction_capability: InteractionCapability = Field(description="`## Interaction Capability` section.")
    reliability: Reliability = Field(description="`## Reliability` section.")
    security: Security = Field(description="`## Security` section.")
    maintainability: Maintainability = Field(description="`## Maintainability` section.")
    flexibility: Flexibility = Field(description="`## Flexibility` section.")
    safety: Safety = Field(description="`## Safety` section.")
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
