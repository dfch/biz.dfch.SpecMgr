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

"""Shared base classes for whole-section fields that recur, byte-identically, across domains.

Extracted during feat-29-dec-source-roles (GitHub issue #29) when `dec` needed
the same `## Source` shape `req` already had, and the same RASCI
(`## Roles and Responsibilities`) shape `sop` already had. Rather than a third
(or, for RASCI, a second) independent copy of these field/validator
definitions, each domain now declares its own thin concrete subclass of the
base classes below, keeping domain-first ownership (every domain still
declares and imports its own class in its own package -- see
`.specmgr/feat/feat-29-dec-source-roles/README.md`'s "Decisions Made" log for
the full rationale) while sharing the actual field declarations.

`@alias` and inheritance: `@alias(...)` sets `cls._alias_metadata` as a plain
Python class attribute at decoration time; `match_alias()`
(`alias_match.py`) reads it via `getattr(cls, "_alias_metadata", None)`,
which follows normal MRO-based attribute lookup. A subclass that never
redeclares `_alias_metadata` therefore inherits it from whichever ancestor
declared it (verified empirically during feat-29's planning). Consequently
`RolesAndResponsibilitiesBase` below carries the one `@alias` override this
family needs (its class name would otherwise derive a wrong default heading,
"Roles And Responsibilities" with a capital "And"); every domain's own
`RolesAndResponsibilities` subclass inherits that override automatically and
must not redeclare it. `SourceBase`/`AccountableBase`/`ResponsibleBase`/
`SupportBase`/`ConsultedBase`/`InformedBase` need no `@alias` at all, since
their default `SPACE_SEPARATED`-derived heading text (computed from the
*actual* runtime class's own `__name__` at match time, not at decoration
time) already equals the desired heading text once a domain's own
single-word-named concrete subclass (`Source`, `Accountable`, ...) is used
as the actual field type -- see the field-narrowing note below.

Field-narrowing pattern: `RolesAndResponsibilitiesBase` types its
`accountable`/`responsible`/`support`/`consulted`/`informed` fields to the
*Base leaf classes declared here, but every domain's own concrete
`RolesAndResponsibilities` subclass re-declares those same fields narrowed to
that domain's own concrete `Accountable`/`Responsible`/`Support`/`Consulted`/
`Informed` subclasses (verified with a standalone Pydantic v2 test during
planning: a subclass may narrow an inherited field's type to a subtype, and
Pydantic validates against the narrowed type, not the parent's declared
type). This is what makes `cls.__name__` resolve to the domain's own class
name (e.g. "Accountable", not "AccountableBase") at parse time, which is
required for the default `SPACE_SEPARATED` alias match to succeed.
"""

from __future__ import annotations

from pydantic import Field

from .alias import alias
from .alias_type import AliasType
from .markdown_list_item import MarkdownListItem
from .markdown_paragraph import MarkdownParagraph
from .markdown_section2 import MarkdownSection2
from .markdown_section3 import MarkdownSection3


class SourceBase(MarkdownSection2):
    """`## Source` -- single-line value naming the origin/authority of this document. Mandatory.

    Shared base for every domain's own `Source` (currently `req`, `dec`).
    Domain subclasses are thin pass-throughs (`class Source(SourceBase): ...`)
    with a domain-specific docstring only -- the default `SPACE_SEPARATED`
    alias already matches `"## Source"` for a subclass named `Source`, so no
    `@alias` override is needed here or in any subclass.

    Parameters
    ----------
    value:
        Single-line value naming the origin/authority of this document. Mandatory.
    """

    # Intentionally domain-neutral ("this document", not "this requirement"/"this decision"):
    # every domain-specific subclass (`req.Source`, `dec.Source`, ...) inherits this exact
    # `Field(description=...)` verbatim into its own generated JSON Schema, so wording specific
    # to one domain here would be misleading for every other domain that reuses this base
    # (feat-29-dec-source-roles, REQ-016). Domain-specific wording belongs on the concrete
    # subclass's own class-level docstring instead (see `req.Source`/`dec.Source`), not here.
    value: MarkdownParagraph = Field(description="Single-line value naming the origin/authority of this document.")


class AccountableBase(MarkdownSection3):
    """`### Accountable` under `## Roles and Responsibilities` -- the single owner
    ultimately answerable for this document. Mandatory once the container is present.

    A single mandatory paragraph (never a bullet list): exactly one owner,
    structurally discouraging multiple owners. See the general
    `specmgr://rasci` resource for RASCI role definitions. Shared base for
    every domain's own `Accountable` (currently `sop`, `dec`).

    Parameters
    ----------
    value:
        The single paragraph naming the accountable party. Mandatory; never a bullet list.
    """

    value: MarkdownParagraph = Field(
        description="The single paragraph naming the accountable party. Mandatory; never a bullet list."
    )


class ResponsibleBase(MarkdownSection3):
    """`### Responsible` under `## Roles and Responsibilities` -- those who do
    the work this document describes. Mandatory once the container is present.

    A mandatory bullet list (>=1 entry). See the general `specmgr://rasci`
    resource for RASCI role definitions. Shared base for every domain's own
    `Responsible` (currently `sop`, `dec`).

    Parameters
    ----------
    items:
        Bullet list naming the responsible parties; must contain at least one item.
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list naming the responsible parties; must contain at least one item.",
    )


class SupportBase(MarkdownSection3):
    """`### Support` under `## Roles and Responsibilities` -- those who
    provide resources or assistance to the responsible parties. Optional.

    An optional bullet list that MAY be present with zero list items (an
    intentional "considered, currently empty" placeholder distinct from
    omitting the heading entirely). See the general `specmgr://rasci`
    resource for RASCI role definitions. Shared base for every domain's own
    `Support` (currently `sop`, `dec`).

    Parameters
    ----------
    items:
        Bullet list naming the support parties, or ``None`` when the heading
        is present with no items. Optional as a whole.
    """

    items: list[MarkdownListItem] | None = Field(
        default=None,
        description="Bullet list naming the support parties, or ``None`` when the heading is present "
        "with no items. Optional; the heading MAY appear with zero items.",
    )


class ConsultedBase(MarkdownSection3):
    """`### Consulted` under `## Roles and Responsibilities` -- those whose
    opinions are sought before or during the work. Optional.

    An optional bullet list that MAY be present with zero list items (an
    intentional "considered, currently empty" placeholder distinct from
    omitting the heading entirely). See the general `specmgr://rasci`
    resource for RASCI role definitions. Shared base for every domain's own
    `Consulted` (currently `sop`, `dec`).

    Parameters
    ----------
    items:
        Bullet list naming the consulted parties, or ``None`` when the heading
        is present with no items. Optional as a whole.
    """

    items: list[MarkdownListItem] | None = Field(
        default=None,
        description="Bullet list naming the consulted parties, or ``None`` when the heading is present "
        "with no items. Optional; the heading MAY appear with zero items.",
    )


class InformedBase(MarkdownSection3):
    """`### Informed` under `## Roles and Responsibilities` -- those who are
    kept up to date on progress or outcomes. Optional.

    An optional bullet list that MAY be present with zero list items (an
    intentional "considered, currently empty" placeholder distinct from
    omitting the heading entirely). See the general `specmgr://rasci`
    resource for RASCI role definitions. Shared base for every domain's own
    `Informed` (currently `sop`, `dec`).

    Parameters
    ----------
    items:
        Bullet list naming the informed parties, or ``None`` when the heading
        is present with no items. Optional as a whole.
    """

    items: list[MarkdownListItem] | None = Field(
        default=None,
        description="Bullet list naming the informed parties, or ``None`` when the heading is present "
        "with no items. Optional; the heading MAY appear with zero items.",
    )


@alias(value="Roles and Responsibilities", type=AliasType.LITERAL)
class RolesAndResponsibilitiesBase(MarkdownSection2):
    """`## Roles and Responsibilities` -- the RASCI responsibility assignment
    for this document. `### Accountable` and `### Responsible` are both
    mandatory (strict-RACI "always has an owner and a doer") once this
    container itself is present, while `### Support`/`### Consulted`/
    `### Informed` stay independently optional and MAY each be present with
    zero list items. See the general `specmgr://rasci` resource for RASCI
    role definitions.

    Shared base for every domain's own `RolesAndResponsibilities` (currently
    `sop`, `dec`). Carries the one `@alias` override this family needs
    (see this module's own docstring) -- domain subclasses inherit it
    automatically and must not redeclare `@alias` themselves. Whether the
    container itself is optional (`sop`) or mandatory (`dec`) on the parent
    document is decided by each domain's own top-level body field
    declaration, not by this shared class.

    Every domain's own concrete subclass re-declares the five fields below,
    narrowed to that domain's own concrete `Accountable`/`Responsible`/
    `Support`/`Consulted`/`Informed` subclasses (see this module's own
    docstring for why the narrowing is required, not just cosmetic).

    Parameters
    ----------
    accountable:
        `### Accountable` sub-section (single paragraph). Mandatory once this container is present.
    responsible:
        `### Responsible` sub-section (bullet list, >=1 item). Mandatory once
        this container is present.
    support:
        `### Support` sub-section (bullet list, MAY be empty). Optional.
    consulted:
        `### Consulted` sub-section (bullet list, MAY be empty). Optional.
    informed:
        `### Informed` sub-section (bullet list, MAY be empty). Optional.
    """

    accountable: AccountableBase = Field(
        description="`### Accountable` sub-section (single paragraph). Mandatory once this container is present."
    )
    responsible: ResponsibleBase = Field(
        description="`### Responsible` sub-section (bullet list, >=1 item). Mandatory once this container is present."
    )
    support: SupportBase | None = Field(default=None, description="`### Support` sub-section. Optional; MAY be empty.")
    consulted: ConsultedBase | None = Field(
        default=None, description="`### Consulted` sub-section. Optional; MAY be empty."
    )
    informed: InformedBase | None = Field(
        default=None, description="`### Informed` sub-section. Optional; MAY be empty."
    )
