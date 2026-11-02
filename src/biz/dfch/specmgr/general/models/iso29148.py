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

"""Pydantic schema and parser for the ISO/IEC/IEEE 29148:2018 requirement-
specifications guidance document (``general/data/general_iso29148.md``),
feat-173-req-iso29148-level-set Phase 130 (REQ-003/ACC-003).

Per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("Expose cross-cutting
reference resources as raw markdown with model-backed drift-guard tests,
not structured JSON"), this model is parsed purely to fail fast on
structural drift -- ``specmgr://iso29148`` (``general/resources/iso29148.
py``) still returns the packaged file's raw markdown text unchanged,
discarding the parsed result. Placed under ``general/models/`` (not the
top-level ``models/`` package), since it is cross-cutting domain
knowledge, not owned by any single document-type domain: the four ISO
29148 kinds are referenced by ``req``'s ``## Level`` field, but the
knowledge is not owned by the ``req`` schema. Top-level ``models/
iso25010.py`` (backing ``specmgr://iso25010``) is the one legacy placement
exception, not the precedent to follow -- mirroring ``general/models/
ears.py``/``dtais.py``'s own placement rationale.

The four abbreviations (``BRS``, ``StRS``, ``SyRS``, ``SRS``) and their
order match the standard's own §3.2 "Abbreviated terms" exactly. The
standard's clause references carried by this document: §3.2 (the
abbreviations), §5.4 (the mapping sentence, reproduced verbatim),
§6.2-6.4 (the processes: business or mission analysis; stakeholder needs
and requirements definition; system [software] requirements definition),
§8.2-8.5 (the example outlines), §9.3-9.6 (the normative content clauses),
and §5.2.6 (the "Characteristics of a set of requirements" list).

Mirrors :mod:`biz.dfch.specmgr.general.models.ears`'s shape closely: an
H1-rooted document (:class:`Iso29148`, a `MarkdownSection1` subclass)
with a leading `MarkdownParagraph` intro, followed by five
`MarkdownSection2` children in the standard's own order. The five `##`
sections are pinned by declaration order -- removing, renaming, or
reordering any of them fails the parse (a same-level heading where the
next declared section's heading is expected yields a no-match error, and
a trailing section yields a leftover-text error). Closed-vocabulary
bullets are modeled as `MarkdownListItem` subclasses with
`@computed_field`s regex-extracting the leading keyword, reusing
`feat.RequirementItem`/`tsk.TaskItem`'s established precedent (ADR
356d8781-e446-4c26-917a-eda85648ce9d's Decision Drivers) rather than
inventing a new shared `models/md` primitive. ``general/data/
general_iso29148.md`` was authored from scratch alongside this model, so
its two closed 4-item lists ("The four requirement specifications" and
"When to use each") are deliberately kept in the SAME abbreviation order
-- the cross-check between them
(:meth:`Iso29148._validate_when_to_use_matches_patterns`) is therefore a
simple, strict ordered-list equality, exactly the same-order rule
`Ears._validate_when_to_use_matches_patterns` implements. The standard's
§5.4 mapping sentence is the ``## The four requirement specifications``
section's own intro paragraph, pinned verbatim by
`RequirementSpecifications._validate_patterns` (a whitespace-normalized
containment check; the source's mixed dash typography -- `BRS –` en dash,
`StRS -`/`SyRS -`/`SRS -` hyphens -- is part of the pinned text). The two
prose sections (``## Mapping to specmgr document types``, ``##
Requirement obligation``) are leaf `MarkdownSection2` subclasses (no
nested fields of their own), mirroring `Ears.CombiningPatterns`'s
leaf-section precedent for an unmodeled prose section -- the ``##
Requirement obligation`` section's position pin is what structurally owns
REQ-002's "obligation is carried by the requirement statement's
phrasing" half (ACC-003). The three validators share their method names
with the `ears.py`/`dtais.py` counterparts of the same kind (the
`whitelist.py` entries are name-based, per that file's own design), so no
new whitelist entry is needed for them.
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
    "Characteristics",
    "CharacteristicItem",
    "DocumentTypeMapping",
    "Iso29148",
    "RequirementObligation",
    "RequirementSpecifications",
    "SpecificationItem",
    "WhenToUseEach",
    "WhenToUseEachItem",
    "parse_iso29148",
]

#: An ISO 29148 §3.2 abbreviation is a plain letter token (``BRS``,
#: ``StRS``, ``SyRS``, ``SRS`` -- the standard's own mixed-case spellings,
#: all `[A-Za-z]+`).
_ABBREVIATION = r"[A-Za-z]+"

#: A §5.2.6 characteristic name is space-separated words (``Complete``,
#: ``Able to be validated``).
_CHARACTERISTIC_NAME = r"[A-Za-z]+(?: [A-Za-z]+)*"

#: Matches "The four requirement specifications" list's `` **BRS** --
#: {full name, clause references, summary} `` bullet text (see
#: `SpecificationItem.abbreviation`) -- the abbreviation is bolded plain
#: text (not backticked). `re.DOTALL` is required: a soft-wrapped bullet's
#: `.text` keeps the embedded newline of its continuation lines
#: (`mdformat` does not reflow), and `.` would not otherwise match it --
#: the same reasoning as `general.models.ears._PATTERN_ITEM_PATTERN`.
_KIND_ITEM_PATTERN = re.compile(
    r"^\*\*(?P<abbreviation>" + _ABBREVIATION + r")\*\* -- .+$",
    re.DOTALL,
)

#: Matches "When to use each" list's `` **`BRS`** -- {guidance} `` bullet
#: text (see `WhenToUseEachItem.abbreviation`) -- bolded AND backticked,
#: unlike `_KIND_ITEM_PATTERN`'s bolded-only abbreviation.
_WHEN_TO_USE_ITEM_PATTERN = re.compile(
    r"^\*\*`(?P<abbreviation>" + _ABBREVIATION + r")`\*\* -- .+$",
    re.DOTALL,
)

#: Matches "Characteristics of a set of requirements" list's
#: `` **`Complete`** -- {description} `` bullet text (see
#: `CharacteristicItem.characteristic`) -- bolded AND backticked, with a
#: possibly multi-word name.
_CHARACTERISTIC_ITEM_PATTERN = re.compile(
    r"^\*\*`(?P<characteristic>" + _CHARACTERISTIC_NAME + r")`\*\* -- .+$",
    re.DOTALL,
)

#: The closed, ordered 4-value ISO 29148 §3.2 abbreviation vocabulary
#: (validated as actual values, not just a count) -- the standard's own
#: spellings and order.
_ABBREVIATIONS = ["BRS", "StRS", "SyRS", "SRS"]

#: The closed, ordered 5-value ISO 29148 §5.2.6 characteristic-name
#: vocabulary (validated as actual values, not just a count).
_CHARACTERISTICS = ["Complete", "Consistent", "Feasible", "Comprehensible", "Able to be validated"]

#: The standard's own §5.4 mapping sentence, verbatim (the source's mixed
#: dash typography -- `BRS –` en dash, `StRS -`/`SyRS -`/`SRS -` hyphens --
#: is part of the pinned text). `RequirementSpecifications._validate_
#: patterns` asserts it is present in the section's intro paragraph,
#: whitespace-normalized.
_MAPPING_SENTENCE = (
    "The business requirements specification (BRS), the stakeholder requirements specification (StRS), "
    "the system requirements specification (SyRS) and the software requirements specification (SRS) are "
    "intended to represent different sets of requirement information items. The specifications correspond "
    "to the requirements in Figure 3 as follows: BRS – Business Requirement (business management level); "
    "StRS - Stakeholder Requirement (business operational level); SyRS - System Requirements; and SRS - "
    "Software Requirements."
)


class SpecificationItem(MarkdownListItem):
    """`` - **BRS** -- {full name, clause references, summary} `` -- one bullet of "The four requirement
    specifications" list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the computed property below): the
    abbreviation lives in the item's own text (e.g. `` "**BRS** --
    Business Requirements Specification. Process §6.2 ..." ``), recovered
    by `@computed_field` at access time, never stored separately.

    Parameters
    ----------
    abbreviation:
        Computed. This item's own bolded ISO 29148 §3.2 abbreviation,
        e.g. `"BRS"`, `"StRS"`, `"SyRS"`, or `"SRS"`. Raises
        `AssertionError` if `.text` does not match ``
        **Abbreviation** -- ... `` (see `_KIND_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def abbreviation(self) -> str:
        """This item's own bolded abbreviation (e.g. `"BRS"`).

        Returns:
            The abbreviation extracted from the leading bolded token.

        Raises:
            AssertionError: `.text` does not match `` **Abbreviation** --
                ... `` (see `_KIND_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-003, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _KIND_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**Abbreviation** -- ...', got {self.text!r}"
        result: str = match.group("abbreviation")
        return result


class WhenToUseEachItem(MarkdownListItem):
    """`` - **`BRS`** -- {guidance} `` -- one bullet of the "When to use each" 4-item list.

    Same leaf shape as `SpecificationItem`, just extracted from the
    bolded-AND-backticked variant of the abbreviation (`` **`BRS`** ``,
    not `` **BRS** ``).

    Parameters
    ----------
    abbreviation:
        Computed. This item's own bolded, backticked abbreviation, e.g.
        `"BRS"`. Raises `AssertionError` if `.text` does not match
        `` **`Abbreviation`** -- ... `` (see `_WHEN_TO_USE_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def abbreviation(self) -> str:
        """This item's own bolded, backticked abbreviation (e.g. `"BRS"`).

        Returns:
            The abbreviation extracted from the leading bolded, backticked
            token.

        Raises:
            AssertionError: `.text` does not match ``
                **`Abbreviation`** -- ... `` (see
                `_WHEN_TO_USE_ITEM_PATTERN`). The message names this
                item's own path and 1-based line (REQ-003, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _WHEN_TO_USE_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**`Abbreviation`** -- ...', got {self.text!r}"
        result: str = match.group("abbreviation")
        return result


class CharacteristicItem(MarkdownListItem):
    """`` - **`Complete`** -- {description} `` -- one bullet of the "Characteristics of a set of requirements"
    5-item list.

    Same leaf shape as `WhenToUseEachItem`, just for the §5.2.6
    characteristic names (possibly multi-word, e.g. `"Able to be
    validated"`) rather than the §3.2 abbreviations.

    Parameters
    ----------
    characteristic:
        Computed. This item's own bolded, backticked characteristic name,
        e.g. `"Complete"`. Raises `AssertionError` if `.text` does not
        match `` **`Name`** -- ... `` (see `_CHARACTERISTIC_ITEM_PATTERN`).
    """

    @computed_field  # type: ignore
    @property
    def characteristic(self) -> str:
        """This item's own bolded, backticked characteristic name (e.g. `"Complete"`).

        Returns:
            The characteristic name extracted from the leading bolded,
            backticked token.

        Raises:
            AssertionError: `.text` does not match `` **`Name`** -- ... ``
                (see `_CHARACTERISTIC_ITEM_PATTERN`). The message names
                this item's own path and 1-based line (REQ-003, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        match = _CHARACTERISTIC_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**`Name`** -- ...', got {self.text!r}"
        result: str = match.group("characteristic")
        return result


@alias(value="The four requirement specifications", type=AliasType.LITERAL)
class RequirementSpecifications(MarkdownSection2):
    """`## The four requirement specifications` -- the closed, ordered 4-item abbreviation list, preceded by the
    standard's own §5.4 mapping sentence as the section's intro paragraph.

    Parameters
    ----------
    intro:
        The standard's §5.4 mapping sentence, verbatim. Mandatory; pinned
        by `_validate_patterns` (whitespace-normalized containment).
    items:
        The `` **Abbreviation** -- {full name, clause references,
        summary} `` entries, in document order. Exactly 4, and exactly
        the closed, ordered `["BRS", "StRS", "SyRS", "SRS"]` vocabulary
        (see `_validate_patterns`).
    """

    intro: MarkdownParagraph = Field(description="The standard's §5.4 mapping sentence, verbatim. Mandatory.")
    items: list[SpecificationItem] = Field(
        min_length=4,
        max_length=4,
        description="Bullet list of `` **Abbreviation** -- ... `` entries; exactly 4.",
    )

    @model_validator(mode="after")
    def _validate_patterns(self) -> RequirementSpecifications:
        """Force eager evaluation of every item's `.abbreviation`, pin the closed 4-value vocabulary, and pin the §5.4
        mapping sentence.

        Mirrors `general.models.ears.Patterns._validate_patterns`'s
        strict-reading precedent (the name is shared; the `whitelist.py`
        entry is name-based): `items`' `.abbreviation`s must be exactly
        `_ABBREVIATIONS`, in that order -- not merely 4 items of any
        wording (REQ-003's "four requirement specifications" read
        strictly). `intro.text` must contain `_MAPPING_SENTENCE`
        whitespace-normalized -- the §5.4 sentence's position in this
        section is pinned, and its mixed dash typography is part of the
        pinned text.

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.abbreviation`, see `SpecificationItem.abbreviation`),
                or `items`' abbreviations are not exactly `_ABBREVIATIONS`
                in order, or `intro` does not contain the §5.4 mapping
                sentence.
        """
        abbreviations = [item.abbreviation for item in self.items]
        assert abbreviations == _ABBREVIATIONS, (
            f"RequirementSpecifications: expected abbreviations {_ABBREVIATIONS!r} in order, got {abbreviations!r}"
        )
        normalized = re.sub(r"\s+", " ", self.intro.text)
        assert _MAPPING_SENTENCE in normalized, (
            f"RequirementSpecifications: intro must contain the standard's §5.4 mapping sentence "
            f"(verbatim, whitespace-normalized); got {self.intro.text!r}"
        )
        return self


@alias(value="When to use each", type=AliasType.LITERAL)
class WhenToUseEach(MarkdownSection2):
    """`## When to use each` -- the second, bolded-and-backticked 4-item abbreviation list.

    Parameters
    ----------
    items:
        The `` **`Abbreviation`** -- {guidance} `` entries, in document
        order. Exactly 4, one per ISO 29148 requirement specification.
        Must match `RequirementSpecifications.items`' abbreviations in
        the same order (see
        `Iso29148._validate_when_to_use_matches_patterns`).
    """

    items: list[WhenToUseEachItem] = Field(
        min_length=4,
        max_length=4,
        description=(
            "Bullet list of `` **`Abbreviation`** -- {guidance} `` entries; exactly 4, "
            "one per requirement specification."
        ),
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> WhenToUseEach:
        """Force every item's `.abbreviation` computed field to evaluate eagerly, not lazily.

        Mirrors `general.models.ears.WhenToUse._validate_items_eagerly`
        (the name is shared; the `whitelist.py` entry is name-based):
        without this, a malformed item would parse silently and only
        raise, if ever, whenever something later happens to read
        `.abbreviation`.
        """
        for item in self.items:
            _ = item.abbreviation
        return self


@alias(value="Mapping to specmgr document types", type=AliasType.LITERAL)
class DocumentTypeMapping(MarkdownSection2):
    """`## Mapping to specmgr document types` -- how the four requirement specifications map onto specmgr document
    types, left unmodeled.

    A leaf `MarkdownSection2` subclass (declares no nested `MarkdownStr`
    fields of its own): the mapping prose (StRS to the `qa`
    requirements-elicitation documents, SyRS to the `sysrs` aggregator,
    SRS to plain `req` software requirements, BRS to the `gol`-adjacent
    business level) is stored verbatim as this section's entire extent --
    its presence and position are pinned by the declaration order alone,
    mirroring `Ears.CombiningPatterns`'s leaf-section precedent for an
    out-of-scope prose section.
    """


@alias(value="Requirement obligation", type=AliasType.LITERAL)
class RequirementObligation(MarkdownSection2):
    """`## Requirement obligation` -- where a requirement's obligation lives (the statement's phrasing, not a
    field), left unmodeled.

    A leaf `MarkdownSection2` subclass (declares no nested `MarkdownStr`
    fields of its own): the obligation prose (the EARS pointer to
    `specmgr://ears`, the ISO "shall" convention) is stored verbatim as
    this section's entire extent -- its presence and position are pinned
    by the declaration order alone, mirroring `Ears.CombiningPatterns`'s
    leaf-section precedent. That position pin is what structurally owns
    REQ-002's "obligation is carried by the requirement statement's
    phrasing" half (ACC-003).
    """


@alias(value="Characteristics of a set of requirements", type=AliasType.LITERAL)
class Characteristics(MarkdownSection2):
    """`## Characteristics of a set of requirements` -- the closed, ordered 5-item §5.2.6 characteristic-name list.

    Parameters
    ----------
    intro:
        The note that the standard's §5.2.6 lists the characteristics a
        set of requirements must exhibit, and that the list below
        reproduces them. Mandatory.
    items:
        The `` **`Name`** -- {description} `` entries, in document order.
        Exactly 5, and exactly the closed, ordered
        `["Complete", "Consistent", "Feasible", "Comprehensible", "Able to
        be validated"]` vocabulary (see `_validate_patterns`).
    """

    intro: MarkdownParagraph = Field(
        description="Note that the list reproduces the §5.2.6 characteristics of a set of requirements. Mandatory."
    )
    items: list[CharacteristicItem] = Field(
        min_length=5,
        max_length=5,
        description="Bullet list of `` **`Name`** -- {description} `` entries; exactly 5 (§5.2.6).",
    )

    @model_validator(mode="after")
    def _validate_patterns(self) -> Characteristics:
        """Force eager evaluation of every item's `.characteristic`, and pin the closed 5-value vocabulary.

        Extends `WhenToUseEach._validate_items_eagerly`'s
        eager-evaluation pattern with an actual-value check (REQ-003's
        stricter reading of the §5.2.6 list): `items`' `.characteristic`s
        must be exactly `_CHARACTERISTICS`, in that order -- not merely 5
        items of any wording. (Shares its name with
        `general.models.ears.Patterns._validate_patterns`; the
        `whitelist.py` entry is name-based.)

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.characteristic`, see `CharacteristicItem.characteristic`),
                or `items`' names are not exactly `_CHARACTERISTICS` in
                order.
        """
        names = [item.characteristic for item in self.items]
        assert names == _CHARACTERISTICS, (
            f"Characteristics: expected characteristic names {_CHARACTERISTICS!r} in order, got {names!r}"
        )
        return self


@alias(value=".+", type=AliasType.REGEX)
class Iso29148(MarkdownSection1):
    """The ISO/IEC/IEEE 29148:2018 requirement-specifications guidance document (`general/data/general_iso29148.
    md`).

    The five `##` sections are pinned in the standard's own order by the
    declaration order -- removing, renaming, or reordering any of them
    fails the parse (see the module docstring).

    Parameters
    ----------
    intro:
        The lead paragraph introducing the four requirement
        specifications and specmgr's `## Level` field. Mandatory.
    specifications:
        `## The four requirement specifications`. Mandatory.
    when_to_use:
        `## When to use each`. Mandatory.
    mapping:
        `## Mapping to specmgr document types`. Mandatory.
    obligation:
        `## Requirement obligation`. Mandatory.
    characteristics:
        `## Characteristics of a set of requirements`. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing the four ISO 29148 requirement specifications. Mandatory."
    )
    specifications: RequirementSpecifications = Field(
        description="`## The four requirement specifications` section. Mandatory."
    )
    when_to_use: WhenToUseEach = Field(description="`## When to use each` section. Mandatory.")
    mapping: DocumentTypeMapping = Field(description="`## Mapping to specmgr document types` section. Mandatory.")
    obligation: RequirementObligation = Field(description="`## Requirement obligation` section. Mandatory.")
    characteristics: Characteristics = Field(
        description="`## Characteristics of a set of requirements` section. Mandatory."
    )

    @model_validator(mode="after")
    def _validate_when_to_use_matches_patterns(self) -> Iso29148:
        """Enforce the strict ordered cross-check between the two 4-item abbreviation lists.

        The `## The four requirement specifications` 4-item list
        (`specifications.items`) and the `## When to use each` 4-item list
        (`when_to_use.items`) must name the same 4 abbreviations, in the
        same order -- the same-order rule
        `Ears._validate_when_to_use_matches_patterns` implements (the name
        is shared; the `whitelist.py` entry is name-based).

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.abbreviation`, see `SpecificationItem.abbreviation`/
                `WhenToUseEachItem.abbreviation`), or the two lists'
                abbreviations do not match, in order.
        """
        specification_abbreviations = [item.abbreviation for item in self.specifications.items]
        when_to_use_abbreviations = [item.abbreviation for item in self.when_to_use.items]
        assert specification_abbreviations == when_to_use_abbreviations, (
            f"Iso29148: 'When to use each' abbreviations {when_to_use_abbreviations!r} must match the "
            f"'The four requirement specifications' abbreviations {specification_abbreviations!r}, "
            "in the same order"
        )
        return self


def parse_iso29148(text: str) -> Iso29148:
    """Parse the packaged ISO/IEC/IEEE 29148:2018 guidance markdown text into an :class:`Iso29148`.

    Thin `format_text` + `Iso29148.from_text` wrapper -- unlike
    `parse_adr`/`parse_req`, there is no YAML frontmatter to split off
    first, since this is a plain packaged data file, not a user-authored
    document (mirrors `biz.dfch.specmgr.general.models.ears.parse_ears`'s
    exact shape).

    Parameters
    ----------
    text:
        The complete markdown file content, exactly as read from disk (e.g.
        via `general.tools._packaged_data.read_packaged_text`).

    Returns
    -------
    Iso29148
        The structured document. Raises ``AssertionError`` for a
        malformed heading/list structure, or ``pydantic.ValidationError``
        for a structurally-sound document whose field values fail schema
        validation.
    """
    result = Iso29148.from_text(format_text(text))
    assert isinstance(result, Iso29148), type(result)
    return result
