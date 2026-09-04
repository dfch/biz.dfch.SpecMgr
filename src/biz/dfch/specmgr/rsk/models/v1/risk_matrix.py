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

"""Pydantic schema and parser for the 5x5 risk-matrix guidance document
(``rsk/data/rsk_risk_matrix.md``), feat-92-resources REQ-004.

Per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("Expose cross-cutting
reference resources as raw markdown with model-backed drift-guard tests,
not structured JSON"), this model is parsed purely to fail fast on
structural drift -- ``specmgr://rsk/risk-matrix`` (``rsk/resources/
risk_matrix.py``) still returns the packaged file's raw markdown text
unchanged, discarding the parsed result. Placed under ``rsk/models/v1/``
(not ``general/models/``), same reasoning as
:mod:`biz.dfch.specmgr.rsk.models.v1.tara`: RSK-owned domain knowledge,
alongside ``Strategy``/``level_from_product`` (``body.py``/
``assessment.py``).

REQ-004 reads narrowly: only the "Product thresholds" 4-item list is
modeled (:class:`ProductThresholds`, :class:`ThresholdItem`); the visual
5x5 zone table (`## Zone table`) and the two closed-vocabulary,
probability/impact scale-anchor lists under `## Scale anchors` encode the
same information but are deliberately left unmodeled -- this feature's own
Design Notes accept a small residual drift risk on the table itself rather
than adding a general-purpose markdown-table-parsing primitive to
`models/md` for this single, narrow use. `## Scale anchors`, `## Zone
table`, and `## Reading initial and residual together` are therefore each
modeled as a **leaf** `MarkdownSection2` subclass (`ScaleAnchors`,
`ZoneTable`, `ReadingTogether`): a leaf declares no nested `MarkdownStr`
fields of its own, so `models/md`'s engine stores each leaf's entire
extent (heading + full body, verbatim) without attempting to parse its
internal bullets/table/paragraphs into any further structure -- this
still satisfies the parser's requirement that every line of the document
be consumed by some declared field, honoring REQ-004's narrow scope
without leaving any part of the document unaccounted for.

`ThresholdItem` recovers a bullet's low/high bound and zone name via three
separate `@computed_field`s (`low: int`, `high: int`, `zone: str`), reusing
`feat.RequirementItem`/`tsk.TaskItem`'s established `MarkdownListItem` +
regex precedent (ADR 356d8781-e446-4c26-917a-eda85648ce9d's Decision
Drivers) rather than inventing a new shared `models/md` primitive. The
zone name can contain a space (`"very high"`), so the regex's zone group
allows an internal space.

`ProductThresholds._validate_thresholds` gives REQ-004's drift-guard real
teeth by cross-checking the packaged prose against
`rsk.models.v1.assessment.level_from_product`'s own executable
zone-derivation logic (this module's own Decisions Made entry, feature
README): beyond `Field(min_length=4, max_length=4)`, it also pins the 4
zone names' exact order (`["low", "medium", "high", "very high"]`),
asserts the 4 bands are contiguous and span 1..25 exactly, and asserts
`level_from_product(low) == zone`/`level_from_product(high) == zone` for
every band.
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, model_validator

from ....models.md import (
    AliasType,
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    alias,
)
from ....models.md._markdown import format_text
from .assessment import level_from_product

__all__ = [
    "ProductThresholds",
    "ReadingTogether",
    "RiskMatrix",
    "ScaleAnchors",
    "ThresholdItem",
    "ZoneTable",
    "parse_risk_matrix",
]

#: Matches a "Product thresholds" bullet's `` `low-high` → `zone` `` text
#: (see `ThresholdItem.low`/`.high`/`.zone`), e.g. `` `1-4` → `low` `` or
#: `` `15-25` → `very high` ``. The zone group allows an internal space
#: (`"very high"`), and always a single line -- no `re.DOTALL` needed.
_THRESHOLD_ITEM_PATTERN = re.compile(r"^`(?P<low>\d+)-(?P<high>\d+)`\s*\u2192\s*`(?P<zone>[a-z]+(?: [a-z]+)*)`$")

#: The closed, ordered 4-value zone vocabulary (REQ-004's "4 entries",
#: validated as actual values, not just a count), mirroring
#: `general.models.dtais.CoverageRelationship`'s
#: `_COVERAGE_VALUES`/`_validate_coverage_values` strict-reading
#: precedent.
_EXPECTED_ZONES = ["low", "medium", "high", "very high"]

#: The 5x5 matrix's product range (`p x i`, both 1..5): 1..25 inclusive.
_MIN_PRODUCT = 1
_MAX_PRODUCT = 25


class ThresholdItem(MarkdownListItem):
    """`` - `low-high` → `zone` `` -- one bullet of the 4-item "Product thresholds" list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the computed properties below): the band's low
    bound, high bound, and zone name all live in the item's own text (e.g.
    `` "`1-4` → `low`" ``), recovered by `@computed_field` at access time,
    never stored separately.

    Parameters
    ----------
    low:
        Computed. This band's low (inclusive) product bound, e.g. `1` for
        `` `1-4` → `low` ``. Raises `AssertionError` if `.text` does not
        match `` `low-high` → `zone` `` (see `_THRESHOLD_ITEM_PATTERN`).
    high:
        Computed. This band's high (inclusive) product bound, e.g. `4` for
        `` `1-4` → `low` ``. Same validation as `low`.
    zone:
        Computed. This band's zone name, e.g. `"low"` or `"very high"`
        (the zone name may contain a space). Same validation as `low`.
    """

    @computed_field  # type: ignore
    @property
    def low(self) -> int:
        """This band's low (inclusive) product bound (e.g. `1` for `` `1-4` → `low` ``).

        Returns:
            The low bound parsed from this item's own backticked range.

        Raises:
            AssertionError: `.text` does not match `` `low-high` → `zone` ``
                (see `_THRESHOLD_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _THRESHOLD_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`low-high` \u2192 `zone`', got {self.text!r}"
        result: int = int(match.group("low"))
        return result

    @computed_field  # type: ignore
    @property
    def high(self) -> int:
        """This band's high (inclusive) product bound (e.g. `4` for `` `1-4` → `low` ``).

        Returns:
            The high bound parsed from this item's own backticked range.

        Raises:
            AssertionError: `.text` does not match `` `low-high` → `zone` ``
                (see `_THRESHOLD_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _THRESHOLD_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`low-high` \u2192 `zone`', got {self.text!r}"
        result: int = int(match.group("high"))
        return result

    @computed_field  # type: ignore
    @property
    def zone(self) -> str:
        """This band's zone name (e.g. `"low"` or `"very high"`).

        Returns:
            The zone name parsed from this item's own backticked text.

        Raises:
            AssertionError: `.text` does not match `` `low-high` → `zone` ``
                (see `_THRESHOLD_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _THRESHOLD_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`low-high` \u2192 `zone`', got {self.text!r}"
        result: str = match.group("zone")
        return result


@alias(value="Scale anchors", type=AliasType.LITERAL)
class ScaleAnchors(MarkdownSection2):
    """`## Scale anchors` -- the probability/impact 1..5 scale anchors, left unmodeled.

    A leaf `MarkdownSection2` subclass (declares no nested `MarkdownStr`
    fields of its own): the probability (`1` = rare .. `5` = almost
    certain) and impact (`1` = negligible .. `5` = severe) anchor lists,
    and the intervening/closing prose, are stored verbatim as this
    section's entire extent -- REQ-004 only calls for modeling the
    "Product thresholds" list, not this section's own two 2-item lists.
    """


@alias(value="Zone table", type=AliasType.LITERAL)
class ZoneTable(MarkdownSection2):
    """`## Zone table` -- the visual 5x5 probability x impact zone table, left unmodeled.

    A leaf `MarkdownSection2` subclass, same reasoning as `ScaleAnchors`:
    the pipe table's rows/columns are deliberately not parsed into any
    structure (this feature's Design Notes: "`risk_matrix` avoids table
    parsing entirely"); this section's entire extent is stored verbatim.
    """


@alias(value="Reading initial and residual together", type=AliasType.LITERAL)
class ReadingTogether(MarkdownSection2):
    """`## Reading initial and residual together` -- how the two 5x5 assessments relate, left unmodeled.

    A leaf `MarkdownSection2` subclass, same reasoning as `ScaleAnchors`:
    the 4-item Initial Assessment/Strategy/Mitigation/Residual Assessment
    list and the closing prose are stored verbatim as this section's
    entire extent -- REQ-004 only calls for modeling the "Product
    thresholds" list.
    """


@alias(value="Product thresholds", type=AliasType.LITERAL)
class ProductThresholds(MarkdownSection2):
    """`## Product thresholds` -- the 4-item product-to-zone band list REQ-004 calls out to model.

    Parameters
    ----------
    intro:
        Lead paragraph introducing the product `p x i` range (1..25).
        Mandatory.
    items:
        The `` `low-high` → `zone` `` entries, in document order. Exactly
        4, and validated by `_validate_thresholds` to name the closed,
        ordered `["low", "medium", "high", "very high"]` vocabulary with
        contiguous bounds spanning 1..25, cross-checked against
        `level_from_product`.
    closing:
        Closing paragraph noting these are the same thresholds the schema
        derives. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing the product `p x i` range (1..25). Mandatory."
    )
    items: list[ThresholdItem] = Field(
        min_length=4,
        max_length=4,
        description="Bullet list of `` `low-high` → `zone` `` entries; exactly 4.",
    )
    closing: MarkdownParagraph = Field(
        description="Closing paragraph noting these are the same thresholds the schema derives. Mandatory."
    )

    @model_validator(mode="after")
    def _validate_thresholds(self) -> ProductThresholds:
        """Force eager evaluation, pin the closed 4-band vocabulary, and cross-check `level_from_product`.

        Beyond `items`' `Field(min_length=4, max_length=4)` count
        constraint, this asserts: the 4 zone names are exactly
        `_EXPECTED_ZONES`, in that order; the 4 bands' bounds are
        contiguous, starting at 1 and ending at 25 (each band's low bound
        is the previous band's high bound + 1); and, for every band,
        `level_from_product(low) == zone` and `level_from_product(high) ==
        zone` -- tying the packaged prose directly to the actual
        executable zone-derivation logic it describes (this module's own
        docstring, this feature's Decisions Made log).

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.low`/`.high`/`.zone`, see `ThresholdItem`), the zone
                names are not exactly `_EXPECTED_ZONES` in order, the
                bounds are not contiguous and spanning 1..25, or some
                band's bounds do not match what `level_from_product` would
                actually derive for them.
        """
        zones = [item.zone for item in self.items]
        assert zones == _EXPECTED_ZONES, (
            f"ProductThresholds: expected zones {_EXPECTED_ZONES!r} in order, got {zones!r}"
        )

        bounds = [(item.low, item.high) for item in self.items]
        assert bounds[0][0] == _MIN_PRODUCT, (
            f"ProductThresholds: expected the first band to start at {_MIN_PRODUCT}, got {bounds[0][0]}"
        )
        assert bounds[-1][1] == _MAX_PRODUCT, (
            f"ProductThresholds: expected the last band to end at {_MAX_PRODUCT}, got {bounds[-1][1]}"
        )
        for previous, current in zip(bounds, bounds[1:]):
            assert current[0] == previous[1] + 1, (
                f"ProductThresholds: expected contiguous bands, got {previous!r} followed by {current!r}"
            )

        for item in self.items:
            assert level_from_product(item.low) == item.zone, (
                f"ProductThresholds: level_from_product({item.low}) == {level_from_product(item.low)!r}, "
                f"expected {item.zone!r}"
            )
            assert level_from_product(item.high) == item.zone, (
                f"ProductThresholds: level_from_product({item.high}) == {level_from_product(item.high)!r}, "
                f"expected {item.zone!r}"
            )
        return self


@alias(value=".+", type=AliasType.REGEX)
class RiskMatrix(MarkdownSection1):
    """The 5x5 risk-matrix guidance document (`rsk/data/rsk_risk_matrix.md`).

    Parameters
    ----------
    intro:
        The lead paragraph introducing the two 5x5 assessments and their
        probability/impact coordinates. Mandatory.
    scale_anchors:
        `## Scale anchors`. Leaf section, left unmodeled. Mandatory.
    zone_table:
        `## Zone table`. Leaf section, left unmodeled. Mandatory.
    product_thresholds:
        `## Product thresholds`. Mandatory -- REQ-004's modeled section.
    reading_together:
        `## Reading initial and residual together`. Leaf section, left
        unmodeled. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing the two 5x5 assessments and their coordinates. Mandatory."
    )
    scale_anchors: ScaleAnchors = Field(description="`## Scale anchors` section (leaf, unmodeled). Mandatory.")
    zone_table: ZoneTable = Field(description="`## Zone table` section (leaf, unmodeled). Mandatory.")
    product_thresholds: ProductThresholds = Field(description="`## Product thresholds` section. Mandatory.")
    reading_together: ReadingTogether = Field(
        description="`## Reading initial and residual together` section (leaf, unmodeled). Mandatory."
    )


def parse_risk_matrix(text: str) -> RiskMatrix:
    """Parse the packaged risk-matrix guidance markdown text into a :class:`RiskMatrix`.

    Thin `format_text` + `RiskMatrix.from_text` wrapper -- unlike
    `parse_adr`/`parse_rsk`, there is no YAML frontmatter to split off
    first, since this is a plain packaged data file, not a user-authored
    document (mirrors `biz.dfch.specmgr.rsk.models.v1.tara.parse_tara`'s
    exact shape).

    Parameters
    ----------
    text:
        The complete markdown file content, exactly as read from disk (e.g.
        via `general.tools._packaged_data.read_packaged_text`).

    Returns
    -------
    RiskMatrix
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation.
    """
    result = RiskMatrix.from_text(format_text(text))
    assert isinstance(result, RiskMatrix), type(result)
    return result
