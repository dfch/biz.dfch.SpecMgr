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

"""Problem Statement (PRB) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1WithComment`/
`MarkdownSection2`/`MarkdownSection3`/`@alias` engine, applying the same
"one class per heading" shape already used by `req/models/v1/body.py`/
`tsk/models/v1/body.py`/`qa/models/v2/body.py`. `Prb` is the top-level H1
container:

```
# {H1 title}                                    Prb (free-form title)
<!-- optional leading comment -->               comment: MarkdownComment | None (inherited)

## Current State                                current_state: CurrentState
### Summary                                     summary: Summary
### What Is the Problem?                        question_1: Question1 | None
### Why Is It a Problem?                         question_2: Question2 | None
### Where Is the Problem Observed?               question_3: Question3 | None
### Who Is Impacted?                             question_4: Question4 | None
### When Was the Problem First Observed?         question_5: Question5 | None
### How Is the Problem Observed?                 question_6: Question6 | None
### How Often Is the Problem Observed?           question_7: Question7 | None

## Gap                                           gap: Gap
## Impact                                        impact: Impact | None
## Future State                                  future_state: FutureState
## References                                    references: References | None
## More Information                              more_information: MoreInformation | None
```

Field declaration order on `Prb`/`CurrentState` enforces markdown order
(title -> optional comment (inherited) -> `current_state` -> `gap` ->
`impact` -> `future_state` -> `references` -> `more_information`, and within
`CurrentState`: `summary` -> `question_1` .. `question_7`), since
`models.md`'s `MarkdownStr.from_text` distributes text among declared
fields in that same order.

Every `Question{N}`/`Summary`/`Gap`/`Impact`/`FutureState`/`References`/
`MoreInformation` class is a bare leaf subclass with no further declared
fields -- the same "opaque, captures any remaining markdown verbatim"
pattern already used by REQ's `MoreInformation`/`Notes` and QA's
`RawRequirements`/`MoreInformation`.

**No `Root Cause` section** -- a deliberate, Six-Sigma-discipline-driven
omission, not an oversight (see the feature README's Scope/Design Notes).
"""

from __future__ import annotations

from pydantic import Field

from ....models.md import (
    MarkdownSection1WithComment,
    MarkdownSection2,
    MarkdownSection3,
    alias,
    AliasType,
)

# --------------------------------------------------------------------------
# `## Current State`
# --------------------------------------------------------------------------


class Summary(MarkdownSection3):
    """`### Summary` under `## Current State` -- free-form synthesis of the current state. Mandatory.

    Leaf class (no declared fields), mirroring `MoreInformation`/`Notes`:
    captures whatever markdown text follows the heading verbatim, with no
    further structure imposed. Must always carry *some* text (even a short
    placeholder at creation time), even if all 7 5W2H questions below are
    still unanswered.
    """


@alias(value=r"What Is the Problem\?", type=AliasType.REGEX)
class Question1(MarkdownSection3):
    """`### What Is the Problem?` under `## Current State` -- the 1st 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


@alias(value=r"Why Is It a Problem\?", type=AliasType.REGEX)
class Question2(MarkdownSection3):
    """`### Why Is It a Problem?` under `## Current State` -- the 2nd 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


@alias(value=r"Where Is the Problem Observed\?", type=AliasType.REGEX)
class Question3(MarkdownSection3):
    """`### Where Is the Problem Observed?` under `## Current State` -- the 3rd 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


@alias(value=r"Who Is Impacted\?", type=AliasType.REGEX)
class Question4(MarkdownSection3):
    """`### Who Is Impacted?` under `## Current State` -- the 4th 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


@alias(value=r"When Was the Problem First Observed\?", type=AliasType.REGEX)
class Question5(MarkdownSection3):
    """`### When Was the Problem First Observed?` under `## Current State` -- the 5th 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


@alias(value=r"How Is the Problem Observed\?", type=AliasType.REGEX)
class Question6(MarkdownSection3):
    """`### How Is the Problem Observed?` under `## Current State` -- the 6th 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


@alias(value=r"How Often Is the Problem Observed\?", type=AliasType.REGEX)
class Question7(MarkdownSection3):
    """`### How Often Is the Problem Observed?` under `## Current State` -- the 7th 5W2H question. Optional.

    Leaf class (no declared fields) -- captures the answer text verbatim.
    """


class CurrentState(MarkdownSection2):
    """`## Current State` -- the factual, evidence-led description of the current state. Mandatory.

    Structured around the classic 5W2H ("What/Why/Where/Who/When/How/How
    Often") interview questions, each under its own fixed, optional H3
    heading, plus a mandatory `### Summary` synthesizing whichever answers
    are actually present.

    Parameters
    ----------
    summary:
        `### Summary`. Mandatory -- a freshly created `prb` document may
        have zero questions answered yet, but must always carry *some*
        `Summary` text.
    question_1:
        `### What Is the Problem?`. Optional.
    question_2:
        `### Why Is It a Problem?`. Optional.
    question_3:
        `### Where Is the Problem Observed?`. Optional.
    question_4:
        `### Who Is Impacted?`. Optional.
    question_5:
        `### When Was the Problem First Observed?`. Optional.
    question_6:
        `### How Is the Problem Observed?`. Optional.
    question_7:
        `### How Often Is the Problem Observed?`. Optional.
    """

    summary: Summary = Field(description="`### Summary` section. Mandatory.")
    question_1: Question1 | None = Field(default=None, description="`### What Is the Problem?` section. Optional.")
    question_2: Question2 | None = Field(default=None, description="`### Why Is It a Problem?` section. Optional.")
    question_3: Question3 | None = Field(
        default=None, description="`### Where Is the Problem Observed?` section. Optional."
    )
    question_4: Question4 | None = Field(default=None, description="`### Who Is Impacted?` section. Optional.")
    question_5: Question5 | None = Field(
        default=None, description="`### When Was the Problem First Observed?` section. Optional."
    )
    question_6: Question6 | None = Field(
        default=None, description="`### How Is the Problem Observed?` section. Optional."
    )
    question_7: Question7 | None = Field(
        default=None, description="`### How Often Is the Problem Observed?` section. Optional."
    )


# --------------------------------------------------------------------------
# `## Gap` / `## Impact` / `## Future State` / `## References` / `## More Information`
# --------------------------------------------------------------------------


class Gap(MarkdownSection2):
    """`## Gap` -- the measurable, actual-vs-expected difference between current and future state. Mandatory.

    Leaf class (no declared fields), mirroring `MoreInformation`/`Notes`:
    captures whatever markdown text follows the heading verbatim, with no
    further structure imposed. Kept a pure measurement, deliberately not
    conflated with `Impact` (the consequence of the gap).
    """


class Impact(MarkdownSection2):
    """`## Impact` -- the business/cost/safety consequence of the gap. Optional.

    Leaf class (no declared fields) -- captures the text verbatim. Placed
    between `Gap` and `Future State` (current state -> gap -> why it
    matters -> target state).
    """


class FutureState(MarkdownSection2):
    """`## Future State` -- the desired/target condition once the problem is resolved. Mandatory.

    Leaf class (no declared fields) -- captures the text verbatim.
    """


class References(MarkdownSection2):
    """`## References` -- free-form cross-references to other artifacts/tickets. Optional.

    Leaf class (no declared fields) -- opaque free text for v1, matching
    `MoreInformation`/`Notes` elsewhere (no structured cross-referencing,
    see the feature README's Scope).
    """


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no fixed format. Optional."""


# --------------------------------------------------------------------------
# `Prb`: the top-level H1 container
# --------------------------------------------------------------------------


@alias(value=".+", type=AliasType.REGEX)
class Prb(MarkdownSection1WithComment):
    """The `prb` body: a single H1 section with the fields below.

    The H1 heading text is free-form. `comment` is inherited from
    `MarkdownSection1WithComment` (see its own docstring) -- not
    redeclared here.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`) preceding
        `current_state`. Inherited from `MarkdownSection1WithComment`.
    current_state:
        `## Current State`. Mandatory.
    gap:
        `## Gap`. Mandatory.
    impact:
        `## Impact`. Optional.
    future_state:
        `## Future State`. Mandatory.
    references:
        `## References`. Optional.
    more_information:
        `## More Information`. Optional.
    """

    current_state: CurrentState = Field(description="`## Current State` section. Mandatory.")
    gap: Gap = Field(description="`## Gap` section. Mandatory.")
    impact: Impact | None = Field(default=None, description="`## Impact` section. Optional.")
    future_state: FutureState = Field(description="`## Future State` section. Mandatory.")
    references: References | None = Field(default=None, description="`## References` section. Optional.")
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
