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

"""Pydantic model for the ADR YAML frontmatter block (plan §3)."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._util import CURRENT_SCHEMA_VERSION, blank_to_none, validate_schema_version

#: Fixed, closed set of accepted ``status`` values.
_FIXED_STATUSES = frozenset({"draft", "proposed", "rejected", "accepted", "deprecated", "superseded"})

#: Additional accepted ``status`` shape: ``"superseded by <anything>"``.
_SUPERSEDED_PATTERN = re.compile(r"^superseded by .+$")


class AdrFrontmatter(BaseModel):
    """The ADR YAML frontmatter block.

    Update contract: whole object, full replace only (plan §3) -- there is
    no partial-update or deletion-sentinel mechanism for frontmatter; omit a
    key from the submitted object to drop it.

    Parameters
    ----------
    version:
        The specmgr schema major.minor.patch version this document was
        written with (plan §6). This is a specmgr-only extension key, not
        part of the MADR 4.0.0 standard -- it is kept alongside the
        MADR-defined keys below purely so it round-trips through the
        parse/render pipeline (plan §7) and lets a future parser dispatch
        an on-disk file to the ``models/adr/vN`` package that understands
        it, or recognize a document still on an older major version.
        Defaults to :data:`CURRENT_SCHEMA_VERSION`. Must share this
        package's major component -- ``models.adr.v1.AdrFrontmatter`` never
        accepts a ``"2.x.x"`` value.
    status:
        Either one of ``"proposed"``, ``"rejected"``, ``"accepted"``,
        ``"deprecated"``, or a string matching ``^superseded by .+$``.
        Mandatory.
    date:
        Free-form date the decision was last updated (MADR uses
        ``YYYY-MM-DD``, not enforced here since the ``.md`` file is the
        source of truth). Optional.
    decision_makers:
        Free-form list of everyone involved in the decision, as written in
        the frontmatter (YAML key ``decision-makers``). Optional.
    consulted:
        Free-form list of subject-matter experts consulted. Optional.
    informed:
        Free-form list of people kept up to date on progress. Optional.
    """

    model_config = ConfigDict(populate_by_name=True)

    version: str = CURRENT_SCHEMA_VERSION
    status: str
    date: str | None = None
    decision_makers: str | None = Field(default=None, alias="decision-makers")
    consulted: str | None = None
    informed: str | None = None

    @field_validator("version")
    @classmethod
    def _validate_version(cls, value: str) -> str:
        return validate_schema_version(value)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value in _FIXED_STATUSES or _SUPERSEDED_PATTERN.match(value):
            return value
        raise ValueError(
            f"status must be one of {sorted(_FIXED_STATUSES)} or match '^superseded by .+$', got {value!r}"
        )

    @field_validator("date", "decision_makers", "consulted", "informed", mode="before")
    @classmethod
    def _optional_blank_to_none(cls, value: str | None) -> str | None:
        return blank_to_none(value)
