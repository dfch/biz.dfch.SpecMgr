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

"""Risk (RSK) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1WithComment`/
`MarkdownSection2` engine, mirroring `req/models/v1/body.py`'s "one class per
heading" shape and `tsk/models/v1/body.py`'s free-form-H1 +
optional-leading-comment pattern. `Risk` is the top-level H1 container:

```
# {H1 title}
<!-- optional leading comment -->        comment: MarkdownComment | None

## Cause                                 cause: Cause
{root condition}
## Trigger                               trigger: Trigger
{what sets the risk event in motion}
## Consequence                           consequence: Consequence
{what happens if the risk event occurs}
## Scope                                 scope: Scope (>=1 item)
- {affected system / component}
## Initial Assessment                    initial_assessment: InitialAssessment
### Probability {1..5}
### Impact {1..5}
## Strategy                              strategy: Strategy (TARA word)
{transfer | accept | reduce | avoid}
## Mitigation                            mitigation: Mitigation
{treatment measures}
## Residual Assessment                   residual_assessment: ResidualAssessment
### Probability {1..5}
### Impact {1..5}
## Owner                                 owner: Owner | None
{responsible person / role}
## Tags                                  tags: Tags | None
- {tag}
## More Information                      more_information: MoreInformation | None
{free-form}
```

Field declaration order on `Risk` enforces the markdown order (title ->
optional comment (inherited) -> Cause -> Trigger -> Consequence -> Scope ->
Initial Assessment -> Strategy -> Mitigation -> Residual Assessment ->
optional Owner -> optional Tags -> optional More Information), since
`models.md`'s `MarkdownStr.from_text` distributes text among declared fields
in that same order.
"""

from __future__ import annotations

import re

from pydantic import Field, field_validator

from ....models.md import (
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1WithComment,
    MarkdownSection2,
    alias,
    AliasType,
)
from .assessment import InitialAssessment, ResidualAssessment


class Cause(MarkdownSection2):
    """`## Cause` -- why the risk exists (the root condition). Mandatory, free-form prose."""


class Trigger(MarkdownSection2):
    """`## Trigger` -- what sets the risk event in motion. Mandatory, free-form prose."""


class Consequence(MarkdownSection2):
    """`## Consequence` -- what happens if the risk event occurs. Mandatory, free-form prose."""


class Scope(MarkdownSection2):
    """`## Scope` -- bullet list of affected systems/components. Mandatory, at least one entry."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of affected systems/components; must contain at least one item.",
    )


#: The TARA 4-value closed set (`## Strategy`'s single-line value) --
#: Transfer, Accept, Reduce, Avoid (the TARA framework's risk-response
#: strategies, `.specmgr/feat/feat-15-add-artifact-type-risk/README.md`
#: Design Notes). Only these four words are accepted; anything else (e.g. the
#: TARRA-era words `tolerate`/`assign`/`recover`) is a validation error.
_TARA_PATTERN = r"^(transfer|accept|reduce|avoid)$"


class Strategy(MarkdownSection2):
    """`## Strategy` -- single-line TARA response strategy. Mandatory.

    One of the four TARA words: `transfer`, `accept`, `reduce`, `avoid`.
    """

    value: MarkdownParagraph = Field(
        description="Single-line TARA response strategy. One of `transfer`, `accept`, `reduce`, `avoid`."
    )

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
        """Enforce the TARA closed 4-value set against `value.text`.

        `value` is a `MarkdownParagraph` (a model, not a `str`), so a
        `Field(pattern=...)` string constraint cannot be applied directly --
        pydantic only applies `pattern` to string-typed schemas. This
        validator re-implements the same check against `value.text`, the
        paragraph's own inline text (mirroring `req`'s `Level`/`Priority`).
        """
        if not re.fullmatch(_TARA_PATTERN, value.text):
            raise ValueError(f"value must match pattern {_TARA_PATTERN!r}, got {value.text!r}")
        return value


class Mitigation(MarkdownSection2):
    """`## Mitigation` -- the treatment measures bridging the two assessments. Mandatory, free-form prose.

    `"none"` is a valid value when the strategy is `accept` (no measures
    taken).
    """


class Owner(MarkdownSection2):
    """`## Owner` -- single-line value naming the responsible person/role. Optional."""

    value: MarkdownParagraph = Field(description="Single-line value naming the responsible person or role.")


class Tags(MarkdownSection2):
    """`## Tags` -- bullet list of free-form labels for grouping/filtering risks. Optional."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of free-form labels for grouping/filtering risks; must contain at least one item.",
    )


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no fixed format. Optional."""


@alias(value=".+", type=AliasType.REGEX)
class Risk(MarkdownSection1WithComment):
    """The `rsk` body: a single H1 section with the fields below.

    The H1 heading text is free-form. `comment` is inherited from
    `MarkdownSection1WithComment` (see its own docstring) -- not redeclared
    here.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`) preceding `cause`.
        Inherited from `MarkdownSection1WithComment`.
    cause:
        `## Cause`. Mandatory.
    trigger:
        `## Trigger`. Mandatory.
    consequence:
        `## Consequence`. Mandatory.
    scope:
        `## Scope`. Mandatory, at least one entry.
    initial_assessment:
        `## Initial Assessment` (5x5, before mitigation). Mandatory.
    strategy:
        `## Strategy` (TARA 4-value closed set). Mandatory.
    mitigation:
        `## Mitigation`. Mandatory.
    residual_assessment:
        `## Residual Assessment` (5x5, after mitigation). Mandatory.
    owner:
        `## Owner`. Optional.
    tags:
        `## Tags`. Optional.
    more_information:
        `## More Information`. Optional.
    """

    cause: Cause = Field(description="`## Cause` section. Mandatory.")
    trigger: Trigger = Field(description="`## Trigger` section. Mandatory.")
    consequence: Consequence = Field(description="`## Consequence` section. Mandatory.")
    scope: Scope = Field(description="`## Scope` section (>=1 affected system/component). Mandatory.")
    initial_assessment: InitialAssessment = Field(
        description="`## Initial Assessment` section (5x5, before mitigation). Mandatory."
    )
    strategy: Strategy = Field(description="`## Strategy` section (TARA 4-value closed set). Mandatory.")
    mitigation: Mitigation = Field(description="`## Mitigation` section. Mandatory.")
    residual_assessment: ResidualAssessment = Field(
        description="`## Residual Assessment` section (5x5, after mitigation). Mandatory."
    )
    owner: Owner | None = Field(default=None, description="`## Owner` section. Optional.")
    tags: Tags | None = Field(default=None, description="`## Tags` section. Optional.")
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
