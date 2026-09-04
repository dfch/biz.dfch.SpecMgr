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

"""Pydantic schema and parser for the DTAIS verification-methods guidance
document (``general/data/general_dtais.md``), feat-92-resources REQ-002.

Per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("Expose cross-cutting
reference resources as raw markdown with model-backed drift-guard tests,
not structured JSON"), this model is parsed purely to fail fast on
structural drift -- ``specmgr://dtais`` (``general/resources/dtais.py``)
still returns the packaged file's raw markdown text unchanged, discarding
the parsed result. Placed under ``general/models/`` (not a top-level
``models/`` module, unlike :mod:`biz.dfch.specmgr.models.iso25010`) since
it is cross-cutting domain knowledge, not owned by any single document-type
domain -- mirroring ``general/models/paged_result.py``/``summary.py``'s own
placement.

Mirrors :mod:`biz.dfch.specmgr.models.iso25010`'s shape closely: an
H1-rooted document (:class:`Dtais`, a `MarkdownSection1` subclass) with a
leading `list[MarkdownListItem]` field directly under the H1, followed by
further `MarkdownSection2` children. Closed-vocabulary bullets are modeled
as `MarkdownListItem` subclasses with a `@computed_field` regex-extracting
the leading backticked keyword, reusing `feat.RequirementItem`/
`tsk.TaskItem`'s established precedent (ADR 356d8781-e446-4c26-917a-
eda85648ce9d's Decision Drivers) rather than inventing a new shared
`models/md` primitive.

Two eager-computed-field-validation `model_validator`s extend
`tsk.models.v1.body.Task._validate_items_eagerly`'s pattern beyond that
package's own precedent set: `WhenToApply._validate_items_eagerly` forces
every `WhenToApplyItem`'s `.method` computed field to evaluate during
construction, and `CoverageRelationship._validate_coverage_values` does
the same for `CoverageItem.value` while additionally pinning the closed
3-value `full`/`partial`/`none` vocabulary (REQ-002's "3-value coverage
list", the stricter of the two readings -- validating the actual values,
not just the count). `Dtais._validate_when_to_apply_matches_methods` is the
"matching" cross-check REQ-002 explicitly calls for: the intro 5-item
method-word list and the second, bolded "when to apply" 5-item list must
name the same 5 words in the same order.
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, model_validator

from ...models.md import (
    AliasType,
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    alias,
)
from ...models.md._markdown import format_text

__all__ = [
    "CoverageItem",
    "CoverageRelationship",
    "Dtais",
    "MethodItem",
    "WhenToApply",
    "WhenToApplyItem",
    "parse_dtais",
]

#: Matches the intro list's un-bolded ``- `Word` -- {definition}`` bullet
#: text (see `MethodItem.method`). `re.DOTALL` is required: a soft-wrapped
#: bullet's `.text` keeps the embedded newline of its continuation lines
#: (`mdformat` does not reflow), and `.` would not otherwise match it --
#: the same reasoning as `sysrs.models.v1.body._validate_cross_reference_items`.
_METHOD_ITEM_PATTERN = re.compile(r"^`(?P<method>[A-Za-z]+)` -- .+$", re.DOTALL)

#: Matches the "When to apply each method"/"Relationship to `## Coverage`"
#: lists' bolded-and-backticked ``- **`Word`** -- {definition}`` bullet
#: text (see `WhenToApplyItem.method`) -- the same shape as
#: `_METHOD_ITEM_PATTERN` above, plus the surrounding `**...**` bold markup.
_WHEN_TO_APPLY_ITEM_PATTERN = re.compile(r"^\*\*`(?P<method>[A-Za-z]+)`\*\* -- .+$", re.DOTALL)

#: Matches the coverage list's bolded-and-backticked ``- **`value`** --
#: {definition}`` bullet text (see `CoverageItem.value`) -- identical shape
#: to `_WHEN_TO_APPLY_ITEM_PATTERN`, kept as a separate constant/computed
#: field name (`value`, not `method`) since it is a semantically distinct
#: closed vocabulary (`full`/`partial`/`none`, not a DTAIS method word).
_COVERAGE_ITEM_PATTERN = re.compile(r"^\*\*`(?P<value>[a-z]+)`\*\* -- .+$", re.DOTALL)


class MethodItem(MarkdownListItem):
    """`` - `Word` -- {definition} `` -- one bullet of the intro, un-bolded 5-item method-word list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the computed property below): the method word
    lives in the item's own text (e.g. `` "`Demonstration` -- observing the
    system ..." ``), recovered by `@computed_field` at access time, never
    stored separately.

    Parameters
    ----------
    method:
        Computed. This item's own backticked method word, e.g.
        `"Demonstration"`. Raises `AssertionError` if `.text` does not
        match `` `Word` -- ... `` (see `_METHOD_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def method(self) -> str:
        """This item's own backticked method word (e.g. `"Demonstration"`).

        Returns:
            The method word extracted from the leading backticked token.

        Raises:
            AssertionError: `.text` does not match `` `Word` -- ... `` (see
                `_METHOD_ITEM_PATTERN`). The message names this item's own
                path and 1-based line (REQ-001/REQ-002, via `self._path`/
                `self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _METHOD_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`Word` -- ...', got {self.text!r}"
        result: str = match.group("method")
        return result


class WhenToApplyItem(MarkdownListItem):
    """`` - **`Word`** -- {guidance} `` -- one bullet of the "When to apply each method" 5-item list.

    Same leaf shape as `MethodItem`, just extracted from the bolded-and-
    backticked variant of the marker (`` **`Word`** ``, not `` `Word` ``).

    Parameters
    ----------
    method:
        Computed. This item's own backticked method word, e.g.
        `"Demonstration"`. Raises `AssertionError` if `.text` does not
        match `` **`Word`** -- ... `` (see `_WHEN_TO_APPLY_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def method(self) -> str:
        """This item's own backticked method word (e.g. `"Demonstration"`).

        Returns:
            The method word extracted from the leading bolded, backticked
            token.

        Raises:
            AssertionError: `.text` does not match `` **`Word`** -- ... ``
                (see `_WHEN_TO_APPLY_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _WHEN_TO_APPLY_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**`Word`** -- ...', got {self.text!r}"
        result: str = match.group("method")
        return result


class CoverageItem(MarkdownListItem):
    """`` - **`value`** -- {meaning} `` -- one bullet of the closed 3-value `## Coverage` list.

    Same leaf shape as `WhenToApplyItem`, just for the lowercase
    `full`/`partial`/`none` coverage vocabulary rather than a DTAIS method
    word.

    Parameters
    ----------
    value:
        Computed. This item's own backticked coverage value, e.g.
        `"full"`. Raises `AssertionError` if `.text` does not match
        `` **`value`** -- ... `` (see `_COVERAGE_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def value(self) -> str:
        """This item's own backticked coverage value (e.g. `"full"`).

        Returns:
            The coverage value extracted from the leading bolded, backticked
            token.

        Raises:
            AssertionError: `.text` does not match `` **`value`** -- ... ``
                (see `_COVERAGE_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _COVERAGE_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**`value`** -- ...', got {self.text!r}"
        result: str = match.group("value")
        return result


@alias(value="When to apply each method", type=AliasType.LITERAL)
class WhenToApply(MarkdownSection2):
    """`## When to apply each method` -- the second, bolded 5-item method-word list.

    Parameters
    ----------
    items:
        The `` **`Word`** -- {guidance} `` entries, in document order.
        Exactly 5, one per DTAIS method.
    """

    items: list[WhenToApplyItem] = Field(
        min_length=5,
        max_length=5,
        description="Bullet list of `**`Word`** -- {guidance}` entries; exactly 5, one per DTAIS method.",
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> WhenToApply:
        """Force every item's `.method` computed field to evaluate eagerly, not lazily.

        Mirrors `feat.models.v1.body.Requirements._validate_items_eagerly`/
        `tsk.models.v1.body.Task._validate_items_eagerly`: without this, a
        malformed item would parse silently and only raise, if ever,
        whenever something later happens to read `.method`.
        """
        for item in self.items:
            _ = item.method
        return self


#: The closed, ordered 3-value `## Coverage` vocabulary (REQ-002's "3-value
#: coverage list", validated as actual values, not just a count).
_COVERAGE_VALUES = ["full", "partial", "none"]


@alias(value="Relationship to `## Coverage`", type=AliasType.LITERAL)
class CoverageRelationship(MarkdownSection2):
    """`` ## Relationship to `## Coverage` `` -- how the chosen method interacts with the document-level
    `## Coverage` roll-up, closed to the 3-value `full`/`partial`/`none` vocabulary.

    Parameters
    ----------
    intro:
        The lead paragraph introducing the `## Coverage` roll-up. Mandatory.
    items:
        The `` **`value`** -- {meaning} `` entries, in document order.
        Exactly 3, and exactly `["full", "partial", "none"]` in that order
        (see `_validate_coverage_values`).
    closing:
        The closing paragraph explaining how the least-verified criterion
        drives the roll-up. Mandatory.
    """

    intro: MarkdownParagraph = Field(description="Lead paragraph introducing the `## Coverage` roll-up. Mandatory.")
    items: list[CoverageItem] = Field(
        min_length=3,
        max_length=3,
        description="Bullet list of `**`value`** -- {meaning}` entries; exactly 3 (`full`/`partial`/`none`).",
    )
    closing: MarkdownParagraph = Field(
        description="Closing paragraph explaining the least-verified-criterion roll-up rule. Mandatory."
    )

    @model_validator(mode="after")
    def _validate_coverage_values(self) -> CoverageRelationship:
        """Force eager evaluation of every item's `.value`, and pin the closed 3-value vocabulary.

        Extends `WhenToApply._validate_items_eagerly`'s eager-evaluation
        pattern with an actual-value check (REQ-002's stricter reading of
        "3-value coverage list"): `items`' `.value`s must be exactly
        `["full", "partial", "none"]`, in that order -- not merely 3 items
        of any wording.

        Raises:
            AssertionError: some item's `.text` is malformed (via `.value`,
                see `CoverageItem.value`), or `items`' values are not
                exactly `["full", "partial", "none"]` in order.
        """
        values = [item.value for item in self.items]
        assert values == _COVERAGE_VALUES, (
            f"CoverageRelationship: expected coverage values {_COVERAGE_VALUES!r} in order, got {values!r}"
        )
        return self


@alias(value=".+", type=AliasType.REGEX)
class Dtais(MarkdownSection1):
    """The DTAIS verification-methods guidance document (`general/data/general_dtais.md`).

    Parameters
    ----------
    intro:
        The lead paragraph introducing the five method words. Mandatory.
    methods:
        The intro, un-bolded `` `Word` -- {definition} `` bullet list.
        Exactly 5.
    when_to_apply:
        `## When to apply each method`. Mandatory.
    coverage:
        `` ## Relationship to `## Coverage` ``. Mandatory.
    """

    intro: MarkdownParagraph = Field(description="Lead paragraph introducing the five DTAIS method words. Mandatory.")
    methods: list[MethodItem] = Field(
        min_length=5,
        max_length=5,
        description="Intro bullet list of `` `Word` -- {definition} `` entries; exactly 5.",
    )
    when_to_apply: WhenToApply = Field(description="`## When to apply each method` section. Mandatory.")
    coverage: CoverageRelationship = Field(description="`## Relationship to `## Coverage`` section. Mandatory.")

    @model_validator(mode="after")
    def _validate_when_to_apply_matches_methods(self) -> Dtais:
        """Force eager evaluation, and enforce REQ-002's "matching" cross-check.

        The intro 5-item method-word list (`methods`) and the second,
        bolded "When to apply each method" 5-item list
        (`when_to_apply.items`) must name the same 5 words, in the same
        order -- REQ-002's "matching 'when to apply' list" guarantee.

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.method`, see `MethodItem.method`/`WhenToApplyItem.method`),
                or the two lists' method words do not match, in order.
        """
        method_words = [item.method for item in self.methods]
        when_to_apply_words = [item.method for item in self.when_to_apply.items]
        assert method_words == when_to_apply_words, (
            f"Dtais: 'When to apply each method' words {when_to_apply_words!r} must match the intro method "
            f"words {method_words!r}, in the same order"
        )
        return self


def parse_dtais(text: str) -> Dtais:
    """Parse the packaged DTAIS guidance markdown text into a :class:`Dtais`.

    Thin `format_text` + `Dtais.from_text` wrapper -- unlike `parse_adr`/
    `parse_req`, there is no YAML frontmatter to split off first, since
    this is a plain packaged data file, not a user-authored document
    (mirrors `biz.dfch.specmgr.models.iso25010.parse_iso25010`'s exact
    shape).

    Parameters
    ----------
    text:
        The complete markdown file content, exactly as read from disk (e.g.
        via `general.tools._packaged_data.read_packaged_text`).

    Returns
    -------
    Dtais
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation.
    """
    result = Dtais.from_text(format_text(text))
    assert isinstance(result, Dtais), type(result)
    return result
