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

"""Pydantic model for the ADR body -- whole-section fields plus options
(plan §4, §5).
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from ._util import blank_to_none
from .option import AdrOption

__all__ = ["MANDATORY_SECTION_FIELDS", "OPTIONAL_SECTION_FIELDS", "AdrBody"]

#: Whole-section :class:`AdrBody` fields that must be non-blank (plan §4).
#: Shared with ``mutations.update_section`` so the deletion-sentinel
#: rejection rule for mandatory sections cannot drift from this model's own
#: validators.
MANDATORY_SECTION_FIELDS = ("title", "context_and_problem_statement", "considered_options", "decision_outcome")

#: Whole-section :class:`AdrBody` fields that normalize blank to ``None``
#: (plan §4). Shared with ``mutations.update_section`` for the same reason
#: as :data:`MANDATORY_SECTION_FIELDS`.
OPTIONAL_SECTION_FIELDS = ("decision_drivers", "consequences", "confirmation", "more_information")


class AdrBody(BaseModel):
    """The ADR body: whole-section fields (plan §4) plus the dynamic
    ``Option`` collection that backs the derived ``## Pros and Cons of the
    Options`` section (plan §5).

    Each whole-section field maps 1:1 to the ``key`` values the future
    ``update_section(key, value)`` MCP tool accepts (plan §4's table),
    using this model's snake_case attribute names rather than the table's
    camelCase key strings -- the tool layer, not this model, is responsible
    for translating between the two.

    Mandatory fields (``title``, ``context_and_problem_statement``,
    ``considered_options``, ``decision_outcome``) must be non-blank; this
    mirrors plan §4's rule that ``update_section`` must reject a deletion
    sentinel targeting a mandatory section rather than write it. Optional
    fields (``decision_drivers``, ``consequences``, ``confirmation``,
    ``more_information``) normalize a blank/whitespace-only value to
    ``None``, i.e. "absent", consistent with the render-time rule that an
    absent optional section omits its heading entirely.

    Parameters
    ----------
    title:
        The ``# {title}`` H1. Mandatory.
    context_and_problem_statement:
        ``## Context and Problem Statement``. Mandatory.
    decision_drivers:
        ``## Decision Drivers``. Optional.
    considered_options:
        ``## Considered Options``. Mandatory. Kept fully independent from
        ``options`` below -- no consistency check is enforced between them
        (plan §4).
    decision_outcome:
        ``## Decision Outcome`` text before any H3. Mandatory.
    consequences:
        ``### Consequences`` under Decision Outcome. Optional.
    confirmation:
        ``### Confirmation`` under Decision Outcome. Optional.
    options:
        The dynamic ``### Option N: {title}`` collection. Backs the derived
        ``## Pros and Cons of the Options`` section, which is rendered iff
        this list is non-empty (plan §5). Defaults to an empty list.
    more_information:
        ``## More Information``, always last. Optional.
    """

    title: str
    context_and_problem_statement: str
    decision_drivers: str | None = None
    considered_options: str
    decision_outcome: str
    consequences: str | None = None
    confirmation: str | None = None
    options: list[AdrOption] = Field(default_factory=list)
    more_information: str | None = None

    @field_validator(*MANDATORY_SECTION_FIELDS)
    @classmethod
    def _required_non_blank(cls, value: str, info: ValidationInfo) -> str:
        if not value or not value.strip():
            raise ValueError(f"{info.field_name} is mandatory and must not be blank")
        return value

    @field_validator(*OPTIONAL_SECTION_FIELDS, mode="before")
    @classmethod
    def _optional_blank_to_none(cls, value: str | None) -> str | None:
        return blank_to_none(value)
