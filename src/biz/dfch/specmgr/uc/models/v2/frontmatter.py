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

"""Use-case frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Replaces `uc/models/v1/use_case_frontmatter.py`'s standalone `UseCaseFrontmatter`,
which re-declared `id`/`version`/`created`/`updated`/`status` from scratch. Here,
only `type` and `status` are narrowed beyond the base's free-form defaults --
`id`'s `uc-NNN` pattern is deliberately *not* ported forward: per
`MarkdownFrontmatter.id`'s own docstring, `id` is a specmgr-assigned identifier
(the same convention `models.adr.v1.AdrFrontmatter.id` already uses), not a
hand-authored `uc-NNN` sequence number -- mirroring `AdrFrontmatter`'s own
`id: str | None = None`, not `UseCaseFrontmatter`'s stricter, now-superseded
`Field(..., pattern=r"^uc-[0-9]+$")`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.frontmatter import DEFAULT_STATUS

#: Fixed, closed set of accepted `status` values, ported forward from
#: `uc/models/v1/use_case_frontmatter.py::UseCaseFrontmatter`'s own set --
#: unlike `AdrFrontmatter.status`, there is no `"superseded by <anything>"`
#: freeform shape for a use case (that concept is ADR-specific).
_ALLOWED_STATUSES = frozenset({"draft", "proposed", "accepted", "deprecated", "superseded"})


class UcFrontmatter(MarkdownFrontmatter):
    """Use-case frontmatter: `MarkdownFrontmatter` narrowed for the `uc` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always `"uc"`. Narrows the base's mandatory,
        default-less `str` field to a `Literal["uc"] = "uc"`, so a document
        omitting `type` entirely still parses as a use case.
    status:
        One of `"draft"`, `"proposed"`, `"accepted"`, `"deprecated"`,
        `"superseded"`. Narrows the base's free-form `str = "draft"` default
        to this closed five-value set, matching `uc/models/v1`'s own
        vocabulary. Blank/absent still defaults to `"draft"` (inherited from
        the base's `_default_blank_status_to_draft` validator, which runs
        before this one).

    All other fields (`id`, `created`, `updated`, `version`) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["uc"] = "uc"

    # feat-189 Phase 120 (C13): redeclare the inherited `status` field (the
    # only way to attach `json_schema_extra` to it) so the generated JSON
    # Schema carries this same closed set as an `enum` key -- schema-level
    # documentation only, in the `MarkdownFrontmatter.created`/`.updated`
    # `pattern`-metadata precedent: pydantic-core never enforces it, and
    # `_validate_status` below remains the sole enforcement point. The
    # default stays the base's own `"draft"`.
    status: str = Field(default=DEFAULT_STATUS, json_schema_extra={"enum": sorted(_ALLOWED_STATUSES)})

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
