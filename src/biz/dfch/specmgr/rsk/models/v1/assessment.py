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

"""The 5x5 risk-matrix assessment models: probability/impact H3 leaves and the H2 assessment section.

Each assessment (`## Initial Assessment` / `## Residual Assessment`) is one
cell of a 5x5 risk matrix: two integer coordinates carried by exactly two
mandatory leaf H3 sections -- `### Probability {1..5}` and `### Impact
{1..5}` -- with the value in the heading itself. The range is baked into each
leaf's regex `@alias`, enforced eagerly by `match_alias` (`re.fullmatch`) at
parse time (same family as `tsk`'s free-form `### ` `UpdateEntry` and
`uc`'s numbered `### Extension N.`/`### Step N:` headings) -- so a missing
value digit, an out-of-range digit (`### Probability 6`), a misspelled
heading word, or a wrong H3 order all fail the parse at parse time. There is
deliberately no `tsk.Task`-style eager-validation `model_validator` here
(`.specmgr/feat/feat-15-add-artifact-type-risk/README.md` Decisions Made):
every tool path parses, so there is no silent-construction gap.

`level` (the matrix zone) is a computed field derived from the probability
x impact product (`level_from_product`) -- always computed, never stored in
the markdown. The same zone thresholds are documented in the packaged
domain-knowledge resource `specmgr://rsk/risk-matrix` (a Phase 3 test guards
the two against drift).
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field

from ....models.md import MarkdownSection2, MarkdownSection3, alias, AliasType

#: Matches a `### Probability {1..5}` heading line as retained in a leaf
#: `MarkdownSection3`'s `.text` (first line), capturing the 1..5 value digit
#: (group 1). Mirrors `Probability`'s own `@alias`, which sees the heading
#: text without the `###` marker.
_PROBABILITY_HEADING_PATTERN = re.compile(r"### Probability ([1-5])")

#: Same as `_PROBABILITY_HEADING_PATTERN` for the `Impact` leaf.
_IMPACT_HEADING_PATTERN = re.compile(r"### Impact ([1-5])")

# Zone names, in ascending severity order.
LEVEL_LOW = "low"
LEVEL_MEDIUM = "medium"
LEVEL_HIGH = "high"
LEVEL_VERY_HIGH = "very high"

# Upper product bounds (inclusive) on the probability x impact product (1..25)
# for the three lower zones; the remainder of the range (above
# `HIGH_PRODUCT_MAX`, i.e. 15..25) is `very high`.
LOW_PRODUCT_MAX = 4
MEDIUM_PRODUCT_MAX = 9
HIGH_PRODUCT_MAX = 14


def level_from_product(product: int) -> str:
    """Map a probability x impact product (1..25) to its 5x5 matrix zone.

    Zone thresholds: 1-4 `low`, 5-9 `medium`, 10-14 `high`, 15-25
    `very high`. This function is the single source of truth for
    `Assessment.level`; the identical thresholds are documented in the
    packaged domain-knowledge resource `specmgr://rsk/risk-matrix`.

    Args:
        product: The probability x impact product, 1..25.

    Returns:
        One of `LEVEL_LOW`/`LEVEL_MEDIUM`/`LEVEL_HIGH`/`LEVEL_VERY_HIGH`.

    Raises:
        AssertionError: `product` is outside 1..25.
    """
    assert 1 <= product <= 25, f"product must be 1..25, got {product}"
    if product <= LOW_PRODUCT_MAX:
        result: str = LEVEL_LOW
    elif product <= MEDIUM_PRODUCT_MAX:
        result = LEVEL_MEDIUM
    elif product <= HIGH_PRODUCT_MAX:
        result = LEVEL_HIGH
    else:
        result = LEVEL_VERY_HIGH
    return result


@alias(value=r"^Probability [1-5]$", type=AliasType.REGEX)
class Probability(MarkdownSection3):
    """`### Probability {1..5}` under `## Initial/Residual Assessment` -- the probability coordinate of the 5x5 matrix.

    A leaf H3 section: the value lives in the heading itself (e.g.
    `### Probability 4`), constrained by the regex `@alias` above and
    enforced by `match_alias` (`re.fullmatch`) at parse time -- a missing
    value digit (`### Probability`), an out-of-range digit
    (`### Probability 6`), or a misspelled heading word all fail the parse
    eagerly. Any body text under the heading is absorbed into the leaf like
    every other leaf `MarkdownSection` (it is not part of the value).

    Parameters
    ----------
    value:
        Computed. The 1..5 probability value carried by the heading (e.g.
        `4` for `### Probability 4`). Never stored separately -- derived
        from the retained heading text.
    """

    @computed_field  # type: ignore
    @property
    def value(self) -> int:
        """The 1..5 probability value carried by this heading (e.g. `4` for `### Probability 4`).

        Returns:
            The integer value parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `Probability`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _PROBABILITY_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"Probability: expected heading '### Probability 1..5', got {heading_line!r}"
        result: int = int(match.group(1))
        return result


@alias(value=r"^Impact [1-5]$", type=AliasType.REGEX)
class Impact(MarkdownSection3):
    """`### Impact {1..5}` under `## Initial/Residual Assessment` -- the impact coordinate of the 5x5 matrix.

    A leaf H3 section: the value lives in the heading itself (e.g.
    `### Impact 3`), constrained by the regex `@alias` above and enforced by
    `match_alias` (`re.fullmatch`) at parse time -- a missing value digit
    (`### Impact`), an out-of-range digit (`### Impact 6`), or a misspelled
    heading word all fail the parse eagerly. Any body text under the heading
    is absorbed into the leaf like every other leaf `MarkdownSection` (it is
    not part of the value).

    Parameters
    ----------
    value:
        Computed. The 1..5 impact value carried by the heading (e.g. `3`
        for `### Impact 3`). Never stored separately -- derived from the
        retained heading text.
    """

    @computed_field  # type: ignore
    @property
    def value(self) -> int:
        """The 1..5 impact value carried by this heading (e.g. `3` for `### Impact 3`).

        Returns:
            The integer value parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `Impact`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _IMPACT_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"Impact: expected heading '### Impact 1..5', got {heading_line!r}"
        result: int = int(match.group(1))
        return result


@alias(value=r"^(Initial|Residual) Assessment$", type=AliasType.REGEX)
class Assessment(MarkdownSection2):
    """`## Initial Assessment`/`## Residual Assessment` -- one 5x5 risk-matrix cell.

    Two mandatory leaf H3 children in fixed order: `### Probability {1..5}`
    first, then `### Impact {1..5}` (field declaration order, enforced by
    `models.md`'s `process_field` extent matching -- a `### Impact` heading
    where a `### Probability` one is expected fails the parse). Use the
    thin subclasses `InitialAssessment`/`ResidualAssessment` (below) as the
    field types on `Risk`, which pin each H2 heading by LITERAL alias and
    additionally enforce the initial-before-residual order.

    Parameters
    ----------
    probability:
        `### Probability {1..5}` leaf section (value in the heading).
        Mandatory.
    impact:
        `### Impact {1..5}` leaf section (value in the heading). Mandatory.
    level:
        Computed. The zone (`low`/`medium`/`high`/`very high`) of the
        probability x impact product -- see `level_from_product`. Always
        computed, never stored in the markdown.
    """

    probability: Probability = Field(
        description="`### Probability {1..5}` leaf section (value in the heading). Mandatory."
    )
    impact: Impact = Field(description="`### Impact {1..5}` leaf section (value in the heading). Mandatory.")

    @computed_field  # type: ignore
    @property
    def level(self) -> str:
        """The derived 5x5 zone of this cell: `probability.value x impact.value` mapped by `level_from_product`.

        Returns:
            One of `LEVEL_LOW`/`LEVEL_MEDIUM`/`LEVEL_HIGH`/`LEVEL_VERY_HIGH`.
        """
        product: int = self.probability.value * self.impact.value
        result: str = level_from_product(product)
        return result


@alias(value="Initial Assessment", type=AliasType.LITERAL)
class InitialAssessment(Assessment):
    """`## Initial Assessment` -- the 5x5 assessment BEFORE mitigation.

    A thin `Assessment` subclass pinning the H2 heading to `Initial
    Assessment` (LITERAL `@alias`), so `Risk`'s field order (initial before
    residual) is enforced at parse time: a document carrying the two
    assessment sections in the wrong order fails `match_alias` instead of
    being silently swapped.
    """


@alias(value="Residual Assessment", type=AliasType.LITERAL)
class ResidualAssessment(Assessment):
    """`## Residual Assessment` -- the 5x5 assessment AFTER mitigation.

    A thin `Assessment` subclass pinning the H2 heading to `Residual
    Assessment` (LITERAL `@alias`); see `InitialAssessment` for the
    order-enforcement rationale.
    """
