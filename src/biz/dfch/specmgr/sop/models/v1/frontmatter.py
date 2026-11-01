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

"""Standard Operating Procedure (SOP) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `gol/models/v1/frontmatter.py::GolFrontmatter`/
`dec/models/v1/frontmatter.py::DecFrontmatter`: a subtype of `MarkdownFrontmatter`
that restricts `type` to a fixed ``Literal["sop"]`` and narrows the free-form
``status`` to SOP's own closed five-value approval/effectivity lifecycle set
(``draft`` -> ``review`` -> ``approved`` -> ``active`` -> ``retired``) -- see
`.specmgr/feat/feat-30-sop/README.md` Design Notes. ``approved`` and ``active``
are kept distinct per explicit user decision: this system does not model an
effective-date/rollout gap, so the transition from ``approved`` to ``active``
is a manual ``set_status`` call, not automatic.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.frontmatter import DEFAULT_STATUS

#: Fixed, closed set of accepted ``status`` values for SOPs -- a five-value
#: approval/effectivity lifecycle: ``draft`` (still being written), ``review``
#: (under review by the responsible authority), ``approved`` (signed off, not
#: yet in force), ``active`` (currently in force, staff must follow it), or
#: ``retired`` (no longer in force, kept for reference).
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "review",
        "approved",
        "active",
        "retired",
    }
)


class SopFrontmatter(MarkdownFrontmatter):
    """Standard Operating Procedure (SOP) frontmatter: `MarkdownFrontmatter` narrowed for the ``sop`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"sop"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["sop"] = "sop"``, so a document
        omitting ``type`` entirely still parses as an SOP document.
    status:
        One of ``"draft"``, ``"review"``, ``"approved"``, ``"active"``,
        ``"retired"``. Narrows the base's free-form ``str = "draft"`` default
        to this closed five-value set. Blank/absent still defaults to
        ``"draft"`` (inherited from the base's ``_default_blank_status_to_draft``
        validator, which runs before this one). ``approved`` (signed off) and
        ``active`` (currently in force) are distinct: the transition between
        them is a manual ``set_status`` call, not automatic.
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["sop"] = "sop"  # type: ignore

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
