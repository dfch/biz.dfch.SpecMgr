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

"""Pydantic schema and parser for the EARS requirement-phrasing-templates guidance
document (``general/data/general_ears.md``), feat-92-resources REQ-006.

Per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("Expose cross-cutting
reference resources as raw markdown with model-backed drift-guard tests,
not structured JSON"), this model is parsed purely to fail fast on
structural drift -- ``specmgr://ears`` (``general/resources/ears.py``)
still returns the packaged file's raw markdown text unchanged, discarding
the parsed result. Placed under ``general/models/`` (not a domain-specific
package), since it is cross-cutting domain knowledge, not owned by any
single document-type domain -- mirroring ``general/models/dtais.py``/
``rasci.py``'s own placement rationale.

The five pattern names and their order (``Ubiquitous requirements``,
``Event-driven requirements``, ``Unwanted behaviours``, ``State-driven
requirements``, ``Optional features``) match the source paper's own
terminology exactly (Mavin et al., "Easy Approach to Requirements
Syntax (EARS)", RE'09, sections 4.1-4.6 -- feat-92-resources Phase 8).

Unlike ``dtais``/``tara`` (both reverse-engineered from a pre-existing
packaged file with inconsistent per-list ordering), ``general/data/
general_ears.md`` was authored from scratch alongside this model, so its
two closed-vocabulary lists ("The five requirement patterns" and "When to
use each pattern") were deliberately kept in the SAME pattern-name order
-- the cross-check between them
(:meth:`Ears._validate_when_to_use_matches_patterns`) is therefore a
simple, strict ordered-list equality, not the set-based comparison
``rsk.models.v1.tara.Tara._validate_quadrant_matches_strategies``/
``_validate_mitigation_matches_strategies`` needed for a document whose
lists disagree on order.

Mirrors :mod:`biz.dfch.specmgr.general.models.dtais`'s shape closely: an
H1-rooted document (:class:`Ears`, a `MarkdownSection1` subclass) with a
leading `MarkdownParagraph` intro, followed by three `MarkdownSection2`
children. Unlike `Dtais.methods` (a bare `list[MethodItem]` field
directly under the H1, no heading of its own), `general/data/
general_ears.md`'s first closed-vocabulary list lives under its own ``##
The five requirement patterns`` heading, so it is wrapped in a composite
:class:`Patterns` section (mirroring `WhenToUse`'s shape below) rather
than declared as a bare list field on `Ears` itself. Closed-vocabulary
bullets are modeled as `MarkdownListItem` subclasses with
`@computed_field`s regex-extracting the leading keyword, reusing
`feat.RequirementItem`/`tsk.TaskItem`'s established precedent (ADR
356d8781-e446-4c26-917a-eda85648ce9d's Decision Drivers) rather than
inventing a new shared `models/md` primitive. `` ## Combining patterns ``
is out of REQ-006's narrow scope (which only asks for the five templates
and when to use each), so it is modeled as a **leaf** `MarkdownSection2`
subclass (no nested fields of its own), mirroring
`rsk.models.v1.risk_matrix`'s leaf-section precedent.
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
    "CombiningPatterns",
    "Ears",
    "PatternItem",
    "Patterns",
    "WhenToUse",
    "WhenToUseItem",
    "parse_ears",
]

#: A pattern name is multiple words, possibly with an internal hyphen
#: (``Event-driven requirements``, ``State-driven requirements``) or a
#: plain space-separated multi-word name (``Ubiquitous requirements``,
#: ``Unwanted behaviours``, ``Optional features``).
_NAME = r"[A-Za-z]+(?:[- ][A-Za-z]+)*"

#: Matches "The five requirement patterns" list's `` **Name** --
#: `template` {explanation} `` bullet text (see `PatternItem.name`/
#: `.template`) -- the pattern name is bolded plain text (not backticked),
#: while the template itself IS backticked. `re.DOTALL` is required: a
#: soft-wrapped bullet's `.text` keeps the embedded newline of its
#: continuation lines (`mdformat` does not reflow across an inline code
#: span), and `.` would not otherwise match it -- the same reasoning as
#: `general.models.dtais._METHOD_ITEM_PATTERN`.
_PATTERN_ITEM_PATTERN = re.compile(
    r"^\*\*(?P<name>" + _NAME + r")\*\* -- (?P<template>`[^`]+`).*$",
    re.DOTALL,
)

#: Matches "When to use each pattern" list's `` **`Name`** -- {guidance} ``
#: bullet text (see `WhenToUseItem.name`) -- bolded AND backticked, unlike
#: `_PATTERN_ITEM_PATTERN`'s bolded-only name.
_WHEN_TO_USE_ITEM_PATTERN = re.compile(
    r"^\*\*`(?P<name>" + _NAME + r")`\*\* -- .+$",
    re.DOTALL,
)

#: The closed, ordered 5-value EARS pattern-name vocabulary (REQ-006's "five
#: requirement-phrasing templates", validated as actual values, not just a
#: count) -- the source paper's own terminology and order (Mavin et al.,
#: RE'09, sections 4.1-4.6).
_PATTERN_NAMES = [
    "Ubiquitous requirements",
    "Event-driven requirements",
    "Unwanted behaviours",
    "State-driven requirements",
    "Optional features",
]


class PatternItem(MarkdownListItem):
    """`` - **Name** -- `template` {explanation} `` -- one bullet of "The five requirement patterns" list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the two computed properties below): the
    pattern name and its template both live in the item's own text (e.g.
    `` "**Ubiquitous requirements** -- `The <system name> shall <system
    response>.` A requirement ..." ``), recovered by `@computed_field` at
    access time, never stored separately.

    Parameters
    ----------
    name:
        Computed. This item's own bolded pattern name, e.g.
        `"Ubiquitous requirements"`, `"Event-driven requirements"`, or
        `"Unwanted behaviours"`. Raises `AssertionError` if `.text` does
        not match `` **Name** -- `template` ... `` (see
        `_PATTERN_ITEM_PATTERN`).
    template:
        Computed. This item's own backticked sentence template, e.g.
        `` "`The <system name> shall <system response>.`" ``. Same
        validation as `name`.
    """

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        """This item's own bolded pattern name (e.g. `"Ubiquitous requirements"`).

        Returns:
            The pattern name extracted from the leading bolded token.

        Raises:
            AssertionError: `.text` does not match `` **Name** --
                `template` ... `` (see `_PATTERN_ITEM_PATTERN`). The
                message names this item's own path and 1-based line
                (REQ-001/REQ-006, via `self._path`/`self._line`, threaded
                in by `models.md`'s `MarkdownListItem.from_text`).
        """
        match = _PATTERN_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**Name** -- `template` ...', got {self.text!r}"
        result: str = match.group("name")
        return result

    @computed_field  # type: ignore
    @property
    def template(self) -> str:
        """This item's own backticked sentence template.

        Returns:
            The template extracted from the backticked token following the
            bolded pattern name, e.g.
            `` "`The <system name> shall <system response>.`" ``.

        Raises:
            AssertionError: `.text` does not match `` **Name** --
                `template` ... `` (see `_PATTERN_ITEM_PATTERN`). The
                message names this item's own path and 1-based line
                (REQ-001/REQ-006, via `self._path`/`self._line`, threaded
                in by `models.md`'s `MarkdownListItem.from_text`).
        """
        match = _PATTERN_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**Name** -- `template` ...', got {self.text!r}"
        result: str = match.group("template")
        return result


class WhenToUseItem(MarkdownListItem):
    """`` - **`Name`** -- {guidance} `` -- one bullet of the "When to use each pattern" 5-item list.

    Same leaf shape as `PatternItem`, just extracted from the
    bolded-AND-backticked variant of the pattern name (`` **`Name`** ``,
    not `` **Name** ``).

    Parameters
    ----------
    name:
        Computed. This item's own bolded, backticked pattern name, e.g.
        `"Ubiquitous requirements"`. Raises `AssertionError` if `.text` does
        not match `` **`Name`** -- ... `` (see `_WHEN_TO_USE_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        """This item's own bolded, backticked pattern name (e.g. `"Ubiquitous requirements"`).

        Returns:
            The pattern name extracted from the leading bolded, backticked
            token.

        Raises:
            AssertionError: `.text` does not match `` **`Name`** -- ... ``
                (see `_WHEN_TO_USE_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-006, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _WHEN_TO_USE_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**`Name`** -- ...', got {self.text!r}"
        result: str = match.group("name")
        return result


@alias(value="The five requirement patterns", type=AliasType.LITERAL)
class Patterns(MarkdownSection2):
    """`## The five requirement patterns` -- the closed, ordered 5-item pattern list.

    Parameters
    ----------
    items:
        The `` **Name** -- `template` {explanation} `` entries, in
        document order. Exactly 5, and exactly the closed, ordered
        `["Ubiquitous requirements", "Event-driven requirements",
        "Unwanted behaviours", "State-driven requirements", "Optional
        features"]` vocabulary (see `_validate_patterns`).
    """

    items: list[PatternItem] = Field(
        min_length=5,
        max_length=5,
        description="Bullet list of `` **Name** -- `template` {explanation} `` entries; exactly 5.",
    )

    @model_validator(mode="after")
    def _validate_patterns(self) -> Patterns:
        """Force eager evaluation of every item's `.name`/`.template`, and pin the closed 5-value vocabulary.

        Mirrors `general.models.rasci.Roles._validate_roles`'s
        strict-reading precedent: `items`' `.name`s must be exactly
        `_PATTERN_NAMES`, in that order -- not merely 5 items of any
        wording (REQ-006's "five requirement-phrasing templates" read
        strictly).

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.name`/`.template`, see `PatternItem`), or `items`'
                names are not exactly `_PATTERN_NAMES` in order.
        """
        names = [item.name for item in self.items]
        for item in self.items:
            _ = item.template
        assert names == _PATTERN_NAMES, f"Patterns: expected pattern names {_PATTERN_NAMES!r} in order, got {names!r}"
        return self


@alias(value="When to use each pattern", type=AliasType.LITERAL)
class WhenToUse(MarkdownSection2):
    """`## When to use each pattern` -- the second, bolded-and-backticked 5-item pattern-name list.

    Parameters
    ----------
    items:
        The `` **`Name`** -- {guidance} `` entries, in document order.
        Exactly 5, one per EARS pattern.
    """

    items: list[WhenToUseItem] = Field(
        min_length=5,
        max_length=5,
        description="Bullet list of `**`Name`** -- {guidance}` entries; exactly 5, one per EARS pattern.",
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> WhenToUse:
        """Force every item's `.name` computed field to evaluate eagerly, not lazily.

        Mirrors `general.models.dtais.WhenToApply._validate_items_eagerly`:
        without this, a malformed item would parse silently and only
        raise, if ever, whenever something later happens to read `.name`.
        """
        for item in self.items:
            _ = item.name
        return self


@alias(value="Combining patterns", type=AliasType.LITERAL)
class CombiningPatterns(MarkdownSection2):
    """`## Combining patterns` -- how a "complex" EARS sentence combines multiple templates, left unmodeled.

    A leaf `MarkdownSection2` subclass (declares no nested `MarkdownStr`
    fields of its own): the comparison/combination prose is stored
    verbatim as this section's entire extent -- REQ-006 only calls for
    modeling the five templates and when to use each, not this
    combination guidance, mirroring `rsk.models.v1.risk_matrix.
    ScaleAnchors`/`general.models.rasci.RasciVsRaci`'s leaf-section
    precedent for an out-of-scope section.
    """


@alias(value=".+", type=AliasType.REGEX)
class Ears(MarkdownSection1):
    """The EARS requirement-phrasing-templates guidance document (`general/data/general_ears.md`).

    Parameters
    ----------
    intro:
        The lead paragraph introducing the five requirement patterns.
        Mandatory.
    patterns:
        `## The five requirement patterns`. Mandatory.
    when_to_use:
        `## When to use each pattern`. Mandatory.
    combining_patterns:
        `## Combining patterns`. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing the five EARS requirement patterns. Mandatory."
    )
    patterns: Patterns = Field(description="`## The five requirement patterns` section. Mandatory.")
    when_to_use: WhenToUse = Field(description="`## When to use each pattern` section. Mandatory.")
    combining_patterns: CombiningPatterns = Field(description="`## Combining patterns` section. Mandatory.")

    @model_validator(mode="after")
    def _validate_when_to_use_matches_patterns(self) -> Ears:
        """Enforce REQ-006's "matching" cross-check, as a strict, ordered-list equality.

        The `## The five requirement patterns` 5-item list (`patterns.
        items`) and the `## When to use each pattern` 5-item list
        (`when_to_use.items`) must name the same 5 words, in the same
        order -- a simple ordered-list equality since `general/data/
        general_ears.md` was authored from scratch with both lists
        deliberately kept in the same order (unlike
        `rsk.models.v1.tara.Tara`'s set-based cross-checks, needed for a
        pre-existing file whose lists disagree on order).

        Raises:
            AssertionError: some item's `.text` is malformed (via `.name`,
                see `PatternItem.name`/`WhenToUseItem.name`), or the two
                lists' pattern names do not match, in order.
        """
        pattern_names = [item.name for item in self.patterns.items]
        when_to_use_names = [item.name for item in self.when_to_use.items]
        assert pattern_names == when_to_use_names, (
            f"Ears: 'When to use each pattern' names {when_to_use_names!r} must match the "
            f"'The five requirement patterns' names {pattern_names!r}, in the same order"
        )
        return self


def parse_ears(text: str) -> Ears:
    """Parse the packaged EARS guidance markdown text into an :class:`Ears`.

    Thin `format_text` + `Ears.from_text` wrapper -- unlike `parse_adr`/
    `parse_req`, there is no YAML frontmatter to split off first, since
    this is a plain packaged data file, not a user-authored document
    (mirrors `biz.dfch.specmgr.general.models.dtais.parse_dtais`'s exact
    shape).

    Parameters
    ----------
    text:
        The complete markdown file content, exactly as read from disk (e.g.
        via `general.tools._packaged_data.read_packaged_text`).

    Returns
    -------
    Ears
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation.
    """
    result = Ears.from_text(format_text(text))
    assert isinstance(result, Ears), type(result)
    return result
