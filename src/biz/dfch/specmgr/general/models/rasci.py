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

"""Pydantic schema and parser for the RASCI responsibility-assignment guidance
document (``general/data/general_rasci.md``), feat-92-resources REQ-005.

Per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("Expose cross-cutting
reference resources as raw markdown with model-backed drift-guard tests,
not structured JSON"), this model is parsed purely to fail fast on
structural drift -- ``specmgr://rasci`` (``general/resources/rasci.py``)
still returns the packaged file's raw markdown text unchanged, discarding
the parsed result. Placed under ``general/models/`` (not ``rsk/models/v1/``
or a domain-specific package), since it is cross-cutting domain knowledge,
not owned by any single document-type domain -- mirroring
``general/models/dtais.py``'s own placement rationale.

Mirrors :mod:`biz.dfch.specmgr.general.models.dtais`'s shape closely: an
H1-rooted document (:class:`Rasci`, a `MarkdownSection1` subclass) with a
leading `MarkdownParagraph` intro, followed by further `MarkdownSection2`
children. The 5-item role list is modeled as a `MarkdownListItem` subclass
with two `@computed_field`s (`role`/`description`), reusing
`feat.RequirementItem`/`tsk.TaskItem`'s established precedent (ADR
356d8781-e446-4c26-917a-eda85648ce9d's Decision Drivers) rather than
inventing a new shared `models/md` primitive -- the two-computed-field
shape (as opposed to `dtais`'s single-computed-field `MethodItem`/
`WhenToApplyItem`/`CoverageItem`) mirrors `tsk.models.v1.task_item.TaskItem`'s
`checked`/`description` precedent instead, since REQ-005 explicitly asks
for "the 5 RASCI roles **and their descriptions**", not just the role
words.

`## RASCI vs. plain RACI` is out of REQ-005's narrow scope (which only asks
for "the 5 RASCI roles and their descriptions"), so it is modeled as a
**leaf** `MarkdownSection2` subclass (:class:`RasciVsRaci`, no nested
fields of its own): `models/md`'s engine stores its entire extent (heading
+ full body, verbatim) without attempting to parse its internal prose into
any further structure -- this still satisfies the parser's requirement
that every line of the document be consumed by some declared field,
mirroring `rsk.models.v1.risk_matrix`'s `ScaleAnchors`/`ZoneTable`/
`ReadingTogether` leaf-section precedent for an out-of-scope section.
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
    "Rasci",
    "RasciVsRaci",
    "RoleItem",
    "Roles",
    "parse_rasci",
]

#: Matches the "The five roles" list's ``- **Role** -- {description}`` bullet
#: text (see `RoleItem.role`/`.description`). `re.DOTALL` is required: a
#: soft-wrapped bullet's `.text` keeps the embedded newline of its
#: continuation lines (`mdformat` does not reflow), and `.` would not
#: otherwise match it -- the same reasoning as
#: `general.models.dtais._METHOD_ITEM_PATTERN`. Unlike DTAIS/TARA's
#: backticked ``` `Word` ``` style, RASCI's role names are bolded plain text
#: (``**Responsible**``), not backticked.
_ROLE_ITEM_PATTERN = re.compile(r"^\*\*(?P<role>[A-Za-z]+)\*\* -- (?P<description>.+)$", re.DOTALL)

#: The closed, ordered 5-value RASCI role vocabulary (REQ-005's "5 RASCI
#: roles", validated as actual values, not just a count), mirroring
#: `general.models.dtais.CoverageRelationship`'s
#: `_COVERAGE_VALUES`/`_validate_coverage_values` strict-reading precedent.
_EXPECTED_ROLES = ["Responsible", "Accountable", "Support", "Consulted", "Informed"]


class RoleItem(MarkdownListItem):
    """`` - **Role** -- {description} `` -- one bullet of the 5-item RASCI role list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the two computed properties below): the role
    name and its description both live in the item's own text (e.g.
    `` "**Responsible** -- the people who do the work. ..." ``), recovered
    by `@computed_field` at access time, never stored separately -- mirrors
    `tsk.models.v1.task_item.TaskItem`'s `checked`/`description`
    two-computed-field precedent, since REQ-005 asks for both the role word
    and its description, not just the word.

    Parameters
    ----------
    role:
        Computed. This item's own bolded role name, e.g. `"Responsible"`.
        Raises `AssertionError` if `.text` does not match
        `` **Role** -- {description} `` (see `_ROLE_ITEM_PATTERN`).
    description:
        Computed. This item's own description text following the bolded
        role name, e.g. `"the people who do the work. ..."`. Same
        validation as `role`.
    """

    @computed_field  # type: ignore
    @property
    def role(self) -> str:
        """This item's own bolded role name (e.g. `"Responsible"`).

        Returns:
            The role name extracted from the leading bolded token.

        Raises:
            AssertionError: `.text` does not match `` **Role** --
                {description} `` (see `_ROLE_ITEM_PATTERN`). The message
                names this item's own path and 1-based line (REQ-001/
                REQ-005, via `self._path`/`self._line`, threaded in by
                `models.md`'s `MarkdownListItem.from_text`).
        """
        match = _ROLE_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**Role** -- ...', got {self.text!r}"
        result: str = match.group("role")
        return result

    @computed_field  # type: ignore
    @property
    def description(self) -> str:
        """This item's own description text following the bolded role name.

        Returns:
            The description text extracted after the leading bolded role
            name.

        Raises:
            AssertionError: `.text` does not match `` **Role** --
                {description} `` (see `_ROLE_ITEM_PATTERN`). The message
                names this item's own path and 1-based line (REQ-001/
                REQ-005, via `self._path`/`self._line`, threaded in by
                `models.md`'s `MarkdownListItem.from_text`).
        """
        match = _ROLE_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"{self._path} (line {self._line}): expected '**Role** -- ...', got {self.text!r}"
        result: str = match.group("description")
        return result


@alias(value="The five roles", type=AliasType.LITERAL)
class Roles(MarkdownSection2):
    """`## The five roles` -- the closed, ordered 5-item RASCI role list.

    Parameters
    ----------
    items:
        The `` **Role** -- {description} `` entries, in document order.
        Exactly 5, and validated by `_validate_roles` to name the closed,
        ordered `["Responsible", "Accountable", "Support", "Consulted",
        "Informed"]` vocabulary.
    """

    items: list[RoleItem] = Field(
        min_length=5,
        max_length=5,
        description="Bullet list of `**Role** -- {description}` entries; exactly 5, one per RASCI role.",
    )

    @model_validator(mode="after")
    def _validate_roles(self) -> Roles:
        """Force eager evaluation of every item's `.role`/`.description`, and pin the closed 5-role vocabulary.

        Extends `general.models.dtais.WhenToApply._validate_items_eagerly`'s
        eager-evaluation pattern with an actual-value check (REQ-005's
        stricter reading of "5 RASCI roles"): `items`' `.role`s must be
        exactly `["Responsible", "Accountable", "Support", "Consulted",
        "Informed"]`, in that order -- not merely 5 items of any wording.

        Raises:
            AssertionError: some item's `.text` is malformed (via
                `.role`/`.description`, see `RoleItem`), or `items`' role
                names are not exactly `_EXPECTED_ROLES` in order.
        """
        roles = [item.role for item in self.items]
        for item in self.items:
            _ = item.description
        assert roles == _EXPECTED_ROLES, f"Roles: expected roles {_EXPECTED_ROLES!r} in order, got {roles!r}"
        return self


@alias(value="RASCI vs. plain RACI", type=AliasType.LITERAL)
class RasciVsRaci(MarkdownSection2):
    """`## RASCI vs. plain RACI` -- how RASCI differs from plain RACI, left unmodeled.

    A leaf `MarkdownSection2` subclass (declares no nested `MarkdownStr`
    fields of its own): the comparison prose is stored verbatim as this
    section's entire extent -- REQ-005 only calls for modeling "the 5 RASCI
    roles and their descriptions", not this comparison section, mirroring
    `rsk.models.v1.risk_matrix.ScaleAnchors`'s leaf-section precedent for an
    out-of-scope section.
    """


@alias(value=".+", type=AliasType.REGEX)
class Rasci(MarkdownSection1):
    """The RASCI responsibility-assignment guidance document (`general/data/general_rasci.md`).

    Parameters
    ----------
    intro:
        The lead paragraph introducing RASCI and its relationship to plain
        RACI. Mandatory.
    roles:
        `## The five roles`. Mandatory -- REQ-005's modeled section.
    rasci_vs_raci:
        `## RASCI vs. plain RACI`. Leaf section, left unmodeled. Mandatory.
    """

    intro: MarkdownParagraph = Field(
        description="Lead paragraph introducing RASCI and its relationship to plain RACI. Mandatory."
    )
    roles: Roles = Field(description="`## The five roles` section. Mandatory.")
    rasci_vs_raci: RasciVsRaci = Field(description="`## RASCI vs. plain RACI` section (leaf, unmodeled). Mandatory.")


def parse_rasci(text: str) -> Rasci:
    """Parse the packaged RASCI guidance markdown text into a :class:`Rasci`.

    Thin `format_text` + `Rasci.from_text` wrapper -- unlike `parse_adr`/
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
    Rasci
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation.
    """
    result = Rasci.from_text(format_text(text))
    assert isinstance(result, Rasci), type(result)
    return result
