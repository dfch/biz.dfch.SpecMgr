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

"""Question and Answer (QA) v2 body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownSection2WithComment`/`MarkdownSection3`/`MarkdownSection3WithComment`
engine, mirroring `qa/models/v1/body.py`'s "one class per heading" shape --
with `questions: list[QaQuestionAnswer] | None` (adjacent Q&A pairs, no
heading of their own) replacing v1's `items: list[QaSection] | None`
(one `### {free-form heading}` per pair). `Qa` is the top-level H1 container:

```
# {H1 title}                                   Qa (free-form title)

## General                                     general: General
### Introduction                                introduction: Introduction
<!-- optional comment -->
{intro paragraphs}
### Raw Requirements                            raw_requirements: RawRequirements
{opaque raw text}

## Elicitation Context                          elicitation_context: ElicitationContext
<!-- optional comment -->                       questions: list[QaQuestionAnswer] | None
> {question}
{opaque answer prose}
...

## Functional Suitability                       functional_suitability: FunctionalSuitability
<!-- optional comment -->                       questions: list[QaQuestionAnswer] | None
> {question}
{opaque answer prose}
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
-> `elicitation_context` -> the 9 ISO/IEC 25010:2023 characteristics, in
their canonical order -> `more_information`), since `models.md`'s
`MarkdownStr.from_text` distributes text among declared fields in that same
order.

**`General`/`Introduction`/`RawRequirements`/`MoreInformation` are duplicated
verbatim from `qa/models/v1/body.py`**, not imported -- v2 has zero
dependency on v1 beyond the shared, unchanged `QaFrontmatter` (see the
feature README's Design Notes/Decisions Made), so v1 can eventually be
deleted with no lingering dependency from v2.

**`## Elicitation Context` is a 10th `_QaCategory`-shaped section, not one of
the 9 ISO/IEC 25010:2023 characteristics** -- it will not appear in, and is
not derived from, the `specmgr://iso25010` resource; it is QA-schema-
specific. It sits between `General` and `FunctionalSuitability` in both
markdown document order and `Qa`'s field declaration order.

**The 10 `_QaCategory`-shaped classes (`ElicitationContext`,
`FunctionalSuitability`, ..., `Safety`) share one private intermediate base,
`_QaCategory`**, declaring `questions` once, rather than each independently
redeclaring it -- mirrors v1's own `_QaCategory` pattern exactly (see the
feature README's Design Notes for the empirically-verified rationale: each
final subclass's own `__name__`, not `_QaCategory`'s, is what `@markdown`'s
inherited `_metadata` and the implicit `AliasType.SPACE_SEPARATED` alias
derivation key off, so sharing the base does not risk any heading-detection
ambiguity between the siblings).
"""

from __future__ import annotations

from pydantic import Field

from ....models.md import (
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection2WithComment,
    MarkdownSection3,
    MarkdownSection3WithComment,
    alias,
    AliasType,
)
from .question_answer import QaQuestionAnswer

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
# `## Elicitation Context` and the 9 ISO/IEC 25010:2023 quality-characteristic categories
# --------------------------------------------------------------------------


class _QaCategory(MarkdownSection2):
    """Private, non-instantiable-in-practice intermediate base for the 10 `_QaCategory`-shaped H2 sections.

    Declares `questions` exactly once; each final subclass below relies on
    the implicit `AliasType.SPACE_SEPARATED` derivation of its own class name
    (e.g. `FunctionalSuitability` -> ``"Functional Suitability"``) for its
    heading match, with no field redeclaration and no per-subclass
    `@alias`/`@markdown` re-application needed -- `@markdown`'s
    `heading_open`/`h2` metadata and `_get_field_names()`'s field
    introspection are both inherited correctly through this extra level
    (empirically verified by v1's own `_QaCategory`; see the feature
    README's Design Notes for the "dynamic, not hardcoded" heading-level
    stop-condition rationale).

    Applies no `@markdown` decorator of its own: it inherits
    `_metadata = {"type": "heading_open", "tag": "h2"}` from
    `MarkdownSection2` through ordinary Python class-attribute inheritance.
    """

    questions: list[QaQuestionAnswer] | None = Field(
        default=None, description="Repeating adjacent Q&A pairs for this category. May be empty/absent."
    )


class ElicitationContext(_QaCategory):
    """`## Elicitation Context` -- a 10th `_QaCategory`-shaped section. Always present.

    Not one of the 9 ISO/IEC 25010:2023 characteristics -- it does not
    appear in, and is not derived from, the `specmgr://iso25010` resource;
    it is QA-schema-specific. Positioned between `General` and
    `FunctionalSuitability` in both markdown document order and `Qa`'s field
    declaration order.
    """


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
    elicitation_context:
        `## Elicitation Context`. Mandatory (always present; `questions` may be empty).
    functional_suitability:
        `## Functional Suitability`. Mandatory (always present; `questions` may be empty).
    performance_efficiency:
        `## Performance Efficiency`. Mandatory (always present; `questions` may be empty).
    compatibility:
        `## Compatibility`. Mandatory (always present; `questions` may be empty).
    interaction_capability:
        `## Interaction Capability`. Mandatory (always present; `questions` may be empty).
    reliability:
        `## Reliability`. Mandatory (always present; `questions` may be empty).
    security:
        `## Security`. Mandatory (always present; `questions` may be empty).
    maintainability:
        `## Maintainability`. Mandatory (always present; `questions` may be empty).
    flexibility:
        `## Flexibility`. Mandatory (always present; `questions` may be empty).
    safety:
        `## Safety`. Mandatory (always present; `questions` may be empty).
    more_information:
        `## More Information`. Optional.
    """

    general: General = Field(description="`## General` section. Mandatory.")
    elicitation_context: ElicitationContext = Field(description="`## Elicitation Context` section. Mandatory.")
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
