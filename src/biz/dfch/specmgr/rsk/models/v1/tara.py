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

"""Pydantic schema and parser for the TARA risk-response-strategy guidance
document (``rsk/data/rsk_tara.md``), feat-92-resources REQ-003.

Per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("Expose cross-cutting
reference resources as raw markdown with model-backed drift-guard tests,
not structured JSON"), this model is parsed purely to fail fast on
structural drift -- ``specmgr://rsk/tara`` (``rsk/resources/tara.py``)
still returns the packaged file's raw markdown text unchanged, discarding
the parsed result. Placed under ``rsk/models/v1/`` (not
``general/models/``, unlike :mod:`biz.dfch.specmgr.general.models.dtais`)
since it is RSK-owned domain knowledge, mirroring this same package's
``Strategy``/``level_from_product`` placement (``body.py``/
``assessment.py``).

Mirrors :mod:`biz.dfch.specmgr.general.models.dtais`'s shape closely: an
H1-rooted document (:class:`Tara`, a `MarkdownSection1` subclass) with a
leading `list[MarkdownListItem]` field directly under the H1, followed by
further `MarkdownSection2` children. Closed-vocabulary bullets are modeled
as `MarkdownListItem` subclasses with a `@computed_field` regex-extracting
the leading TARA strategy word, reusing `feat.RequirementItem`/
`tsk.TaskItem`'s established precedent (ADR 356d8781-e446-4c26-917a-
eda85648ce9d's Decision Drivers) rather than inventing a new shared
`models/md` primitive. All four regexes use `re.DOTALL` except
`_STRATEGY_ITEM_PATTERN` (the intro list's bullets are always a single
line): a soft-wrapped bullet's `.text` keeps the embedded newline of its
continuation lines (`mdformat` does not reflow), mirroring
`sysrs.models.v1.body._validate_cross_reference_items`'s established
reasoning.

The real document's own TARA strategy word appears, in order, in **three
different lists**, and -- unlike DTAIS's two 5-word lists, which happen to
share the same order -- the order genuinely differs across all three:
``transfer``/``accept``/``reduce``/``avoid`` (the intro list),
``transfer``/``avoid``/``reduce``/``accept`` (the "When to apply each
strategy" quadrant list), and ``reduce``/``transfer``/``avoid``/``accept``
(the "Interaction with `## Mitigation`" list). `Tara._validate_strategies`
therefore pins the intro list's *exact order* as the one canonical,
fixed 4-value vocabulary (`["transfer", "accept", "reduce", "avoid"]`),
while `Tara._validate_quadrant_matches_strategies`/
`Tara._validate_mitigation_matches_strategies` compare the quadrant/
mitigation lists against that canonical list as *sets*, not ordered
lists -- REQ-003's "matching" cross-check read as "names the same four
words", not "in the same order" (see this feature's Decisions Made log).
The independent, unrelated 6-value frontmatter `status` lifecycle list is
pinned as an exact ordered vocabulary by
`StatusInteraction._validate_status_values`, mirroring
`general.models.dtais.CoverageRelationship._validate_coverage_values`'s
strict-reading precedent -- no cross-check against the strategy words is
needed or meaningful, since `status` and `strategy` are explicitly
documented as independent fields.
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

__all__ = [
    "MitigationInteraction",
    "MitigationItem",
    "QuadrantItem",
    "StatusInteraction",
    "StatusItem",
    "StrategyItem",
    "Tara",
    "WhenToApply",
    "parse_tara",
]

#: Matches the intro list's bare `` `word` `` bullet text (see
#: `StrategyItem.strategy`). Always a single line -- no `re.DOTALL` needed.
_STRATEGY_ITEM_PATTERN = re.compile(r"^`(?P<strategy>[a-z]+)`$")

#: Matches the "When to apply each strategy" quadrant list's bolded
#: ``**{quadrant description} → `word`**\n{explanation}`` bullet text (see
#: `QuadrantItem.strategy`). `re.DOTALL` is required: a soft-wrapped
#: bullet's `.text` keeps the embedded newline of its continuation lines
#: (`mdformat` does not reflow), the same reasoning as
#: `sysrs.models.v1.body._validate_cross_reference_items`.
_QUADRANT_ITEM_PATTERN = re.compile(r"^\*\*.+ → `(?P<strategy>[a-z]+)`\*\*\n.+$", re.DOTALL)

#: Matches the "Interaction with `## Mitigation`" list's `` `word`:
#: {explanation} `` bullet text (see `MitigationItem.strategy`) -- same
#: multi-line reasoning as `_QUADRANT_ITEM_PATTERN`.
_MITIGATION_ITEM_PATTERN = re.compile(r"^`(?P<strategy>[a-z]+)`: .+$", re.DOTALL)

#: Matches the "Interaction with the frontmatter `status`" list's
#: `` `word` — {explanation} `` bullet text (see `StatusItem.status`) --
#: same multi-line reasoning as `_QUADRANT_ITEM_PATTERN`, using an em dash
#: (`—`, not a hyphen) as the separator, exactly as authored in
#: `rsk/data/rsk_tara.md`.
_STATUS_ITEM_PATTERN = re.compile(r"^`(?P<status>[a-z]+)` — .+$", re.DOTALL)


class StrategyItem(MarkdownListItem):
    """`` - `word` `` -- one bullet of the intro, bare 4-item TARA strategy-word list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the computed property below): the strategy
    word is the item's entire own text (e.g. `` "`transfer`" ``), recovered
    by `@computed_field` at access time, never stored separately.

    Parameters
    ----------
    strategy:
        Computed. This item's own backticked TARA strategy word, e.g.
        `"transfer"`. Raises `AssertionError` if `.text` does not match
        `` `word` `` exactly (see `_STRATEGY_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def strategy(self) -> str:
        """This item's own backticked TARA strategy word (e.g. `"transfer"`).

        Returns:
            The strategy word extracted from this item's own backticked
            text.

        Raises:
            AssertionError: `.text` does not match `` `word` `` exactly
                (see `_STRATEGY_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _STRATEGY_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`word`', got {self.text!r}"
        result: str = match.group("strategy")
        return result


class QuadrantItem(MarkdownListItem):
    """`` - **{quadrant description} → `word`**\\n{explanation} `` -- one bullet of the 4-item quadrant list.

    Parameters
    ----------
    strategy:
        Computed. This item's own backticked TARA strategy word, e.g.
        `"transfer"`. Raises `AssertionError` if `.text` does not match
        `` **{description} → `word`**\\n{explanation} `` (see
        `_QUADRANT_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def strategy(self) -> str:
        """This item's own backticked TARA strategy word (e.g. `"transfer"`).

        Returns:
            The strategy word extracted from the bolded quadrant heading
            line.

        Raises:
            AssertionError: `.text` does not match
                `` **{description} → `word`**\\n{explanation} `` (see
                `_QUADRANT_ITEM_PATTERN`). The message names this item's
                own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _QUADRANT_ITEM_PATTERN.fullmatch(self.text)
        assert match, (
            f"{self._path} (line {self._line}): expected '**{{description}} \u2192 `word`**\\n...', got {self.text!r}"
        )
        result: str = match.group("strategy")
        return result


class MitigationItem(MarkdownListItem):
    """`` - `word`: {explanation} `` -- one bullet of the 4-item mitigation-interaction list.

    Parameters
    ----------
    strategy:
        Computed. This item's own backticked TARA strategy word, e.g.
        `"reduce"`. Raises `AssertionError` if `.text` does not match
        `` `word`: {explanation} `` (see `_MITIGATION_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def strategy(self) -> str:
        """This item's own backticked TARA strategy word (e.g. `"reduce"`).

        Returns:
            The strategy word extracted from the leading backticked token.

        Raises:
            AssertionError: `.text` does not match
                `` `word`: {explanation} `` (see
                `_MITIGATION_ITEM_PATTERN`). The message names this item's
                own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _MITIGATION_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`word`: ...', got {self.text!r}"
        result: str = match.group("strategy")
        return result


class StatusItem(MarkdownListItem):
    """`` - `word` — {explanation} `` -- one bullet of the closed 6-value frontmatter `status` list.

    Parameters
    ----------
    status:
        Computed. This item's own backticked status value, e.g.
        `"open"`. Raises `AssertionError` if `.text` does not match
        `` `word` — {explanation} `` (see `_STATUS_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def status(self) -> str:
        """This item's own backticked status value (e.g. `"open"`).

        Returns:
            The status value extracted from the leading backticked token.

        Raises:
            AssertionError: `.text` does not match `` `word` — {explanation} ``
                (see `_STATUS_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _STATUS_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '`word` \u2014 ...', got {self.text!r}"
        result: str = match.group("status")
        return result


@alias(value="When to apply each strategy", type=AliasType.LITERAL)
class WhenToApply(MarkdownSection2):
    """`## When to apply each strategy` -- the quadrant-coordinate 4-item strategy list.

    Parameters
    ----------
    intro:
        Lead paragraph pointing at `## Initial Assessment`'s matrix
        coordinates. Mandatory.
    items:
        The `` **{quadrant} → `word`**\\n{explanation} `` entries, in
        document order. Exactly 4, one per TARA strategy -- their *set* of
        strategy words must match the intro list's (see
        `Tara._validate_quadrant_matches_strategies`); their *order* need
        not.
    closing:
        Closing paragraph noting the quadrants are a guideline, not a
        rule. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph pointing at `## Initial Assessment`'s matrix coordinates. Mandatory."
    )
    items: list[QuadrantItem] = Field(
        min_length=4,
        max_length=4,
        description="Bullet list of `**{quadrant} -> `word`**\\n{explanation}` entries; exactly 4.",
    )
    closing: MarkdownParagraph = Field(
        description="Closing paragraph noting the quadrants are a guideline, not a rule. Mandatory."
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> WhenToApply:
        """Force every item's `.strategy` computed field to evaluate eagerly, not lazily.

        Mirrors `general.models.dtais.WhenToApply._validate_items_eagerly`:
        without this, a malformed item would parse silently and only
        raise, if ever, whenever something later happens to read
        `.strategy`.
        """
        for item in self.items:
            _ = item.strategy
        return self


@alias(value="Interaction with `## Mitigation`", type=AliasType.LITERAL)
class MitigationInteraction(MarkdownSection2):
    """`` ## Interaction with `## Mitigation` `` -- how each strategy shapes the `## Mitigation` text.

    Parameters
    ----------
    intro:
        Lead paragraph introducing `## Mitigation` as the treatment
        section bridging the two assessments. Mandatory.
    items:
        The `` `word`: {explanation} `` entries, in document order.
        Exactly 4, one per TARA strategy -- their *set* of strategy words
        must match the intro list's (see
        `Tara._validate_mitigation_matches_strategies`); their *order*
        need not. There is deliberately no `closing` paragraph on this
        section -- unlike `WhenToApply`/`StatusInteraction`, the real
        document's `` ## Interaction with `## Mitigation` `` section ends
        directly after this bullet list, immediately followed by the next
        `##` heading.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing `## Mitigation` as the treatment section. Mandatory."
    )
    items: list[MitigationItem] = Field(
        min_length=4,
        max_length=4,
        description="Bullet list of `` `word`: {explanation} `` entries; exactly 4.",
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> MitigationInteraction:
        """Force every item's `.strategy` computed field to evaluate eagerly, not lazily.

        Mirrors `WhenToApply._validate_items_eagerly` above.
        """
        for item in self.items:
            _ = item.strategy
        return self


#: The closed, ordered 6-value frontmatter `status` vocabulary (REQ-003's
#: "6-value status list", validated as actual values, not just a count) --
#: independent of the TARA strategy words above (`status` tracks the
#: lifecycle state of a `rsk` entry, `strategy` tracks its chosen
#: response; the real document explicitly documents them as independent
#: fields).
_STATUS_VALUES = ["open", "mitigating", "accepted", "occurred", "closed", "dropped"]


@alias(value="Interaction with the frontmatter `status`", type=AliasType.LITERAL)
class StatusInteraction(MarkdownSection2):
    """`` ## Interaction with the frontmatter `status` `` -- the closed 6-value `status` lifecycle list.

    Parameters
    ----------
    intro:
        Lead paragraph introducing the six-value `status` lifecycle.
        Mandatory.
    items:
        The `` `word` — {explanation} `` entries, in document order.
        Exactly 6, and exactly `_STATUS_VALUES` in that order (see
        `_validate_status_values`).
    closing:
        Closing paragraph explaining that `status` and `strategy` are
        independent fields. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing the six-value `status` lifecycle. Mandatory."
    )
    items: list[StatusItem] = Field(
        min_length=6,
        max_length=6,
        description="Bullet list of `` `word` -- {explanation} `` entries; exactly 6.",
    )
    closing: MarkdownParagraph = Field(
        description="Closing paragraph explaining `status`/`strategy` are independent fields. Mandatory."
    )

    @model_validator(mode="after")
    def _validate_status_values(self) -> StatusInteraction:
        """Force eager evaluation of every item's `.status`, and pin the closed 6-value vocabulary.

        Mirrors `general.models.dtais.CoverageRelationship.
        _validate_coverage_values`'s stricter reading (REQ-003's "6-value
        status list"): `items`' `.status`es must be exactly
        `_STATUS_VALUES`, in that order -- not merely 6 items of any
        wording.

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.status`, see `StatusItem.status`), or `items`' values are
                not exactly `_STATUS_VALUES` in order.
        """
        values = [item.status for item in self.items]
        assert values == _STATUS_VALUES, (
            f"StatusInteraction: expected status values {_STATUS_VALUES!r} in order, got {values!r}"
        )
        return self


@alias(value=".+", type=AliasType.REGEX)
class Tara(MarkdownSection1):
    """The TARA risk-response-strategy guidance document (`rsk/data/rsk_tara.md`).

    Parameters
    ----------
    intro:
        The lead paragraph introducing the TARA framework and the four
        strategy words. Mandatory.
    strategies:
        The intro, bare `` `word` `` bullet list. Exactly 4, and exactly
        `["transfer", "accept", "reduce", "avoid"]` in that order -- the
        one canonical, fixed-order vocabulary every other list's *set* of
        words is checked against (see `_validate_strategies`).
    when_to_apply:
        `## When to apply each strategy`. Mandatory.
    mitigation:
        `` ## Interaction with `## Mitigation` ``. Mandatory.
    status:
        `` ## Interaction with the frontmatter `status` ``. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing the TARA framework and the four strategy words. Mandatory."
    )
    strategies: list[StrategyItem] = Field(
        min_length=4,
        max_length=4,
        description="Intro bullet list of `` `word` `` entries; exactly 4.",
    )
    when_to_apply: WhenToApply = Field(description="`## When to apply each strategy` section. Mandatory.")
    mitigation: MitigationInteraction = Field(
        description="`` ## Interaction with `## Mitigation` `` section. Mandatory."
    )
    status: StatusInteraction = Field(
        description="`` ## Interaction with the frontmatter `status` `` section. Mandatory."
    )

    @model_validator(mode="after")
    def _validate_strategies(self) -> Tara:
        """Force eager evaluation, and pin the canonical, ordered 4-value TARA vocabulary.

        The intro list is the single source of truth for the strategy
        words' canonical order: exactly `["transfer", "accept", "reduce",
        "avoid"]`, in that order.

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.strategy`, see `StrategyItem.strategy`), or `strategies`'
                words are not exactly `["transfer", "accept", "reduce",
                "avoid"]` in order.
        """
        words = [item.strategy for item in self.strategies]
        assert words == ["transfer", "accept", "reduce", "avoid"], (
            f"Tara: expected strategy words ['transfer', 'accept', 'reduce', 'avoid'] in order, got {words!r}"
        )
        return self

    @model_validator(mode="after")
    def _validate_quadrant_matches_strategies(self) -> Tara:
        """Enforce REQ-003's "matching" cross-check for the quadrant list, by set, not order.

        The real document's quadrant list orders its four bullets by
        matrix quadrant (`transfer`/`avoid`/`reduce`/`accept`), not by the
        intro list's own canonical order (`transfer`/`accept`/`reduce`/
        `avoid`) -- so this compares the two lists' strategy words as
        *sets*, deliberately not as ordered lists (see this module's own
        docstring, and this feature's Decisions Made log).

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.strategy`, see `QuadrantItem.strategy`), or the
                quadrant list's strategy words, as a set, do not equal the
                intro list's strategy words, as a set.
        """
        strategy_words = {item.strategy for item in self.strategies}
        quadrant_words = {item.strategy for item in self.when_to_apply.items}
        assert strategy_words == quadrant_words, (
            f"Tara: 'When to apply each strategy' words {quadrant_words!r} must name the same strategies "
            f"as the intro list {strategy_words!r} (as a set; order may differ)"
        )
        return self

    @model_validator(mode="after")
    def _validate_mitigation_matches_strategies(self) -> Tara:
        """Enforce REQ-003's "matching" cross-check for the mitigation list, by set, not order.

        Same reasoning as `_validate_quadrant_matches_strategies`: the real
        document's mitigation list orders its four bullets
        (`reduce`/`transfer`/`avoid`/`accept`), differently again from
        both the intro list and the quadrant list -- so this, too,
        compares strategy words as *sets*.

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.strategy`, see `MitigationItem.strategy`), or the
                mitigation list's strategy words, as a set, do not equal
                the intro list's strategy words, as a set.
        """
        strategy_words = {item.strategy for item in self.strategies}
        mitigation_words = {item.strategy for item in self.mitigation.items}
        assert strategy_words == mitigation_words, (
            f"Tara: 'Interaction with `## Mitigation`' words {mitigation_words!r} must name the same "
            f"strategies as the intro list {strategy_words!r} (as a set; order may differ)"
        )
        return self


def parse_tara(text: str) -> Tara:
    """Parse the packaged TARA guidance markdown text into a :class:`Tara`.

    Thin `format_text` + `Tara.from_text` wrapper -- unlike `parse_adr`/
    `parse_rsk`, there is no YAML frontmatter to split off first, since
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
    Tara
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation.
    """
    result = Tara.from_text(format_text(text))
    assert isinstance(result, Tara), type(result)
    return result
