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

"""Set (SET) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `txt/models/v1/frontmatter.py::TxtFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["set"]`` and narrows the free-form ``status`` to SET's own closed
four-value set ``draft``/``progress``/``done``/``review`` -- the SET-specific
lifecycle (a bundle under review is a distinct state from one in work, unlike
the deliberately lighter TXT three-value set). See
`.specmgr/feat/feat-173-req-iso29148-level-set/README.md` (the 2026-11-01
Decisions Made entry) for the full rationale.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.frontmatter import DEFAULT_STATUS

#: Fixed, closed set of accepted ``status`` values for set documents:
#: ``draft`` (not started), ``progress`` (in work), ``done`` (finished),
#: ``review`` (under review). SET-specific: a convenience bundle has a
#: distinct review state (someone checking the bundled items), unlike the
#: deliberately lighter TXT three-value set.
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "progress",
        "done",
        "review",
    }
)


class SetFrontmatter(MarkdownFrontmatter):
    """Set (SET) frontmatter: `MarkdownFrontmatter` narrowed for the ``set`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"set"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["set"] = "set"``, so a document
        omitting ``type`` entirely still parses as a set document.
    status:
        One of ``"draft"``, ``"progress"``, ``"done"``, ``"review"``. Narrows
        the base's free-form ``str = "draft"`` default to this closed
        four-value set. Blank/absent still defaults to ``"draft"`` (inherited
        from the base's ``_default_blank_status_to_draft`` validator, which
        runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``,
    ``classification``) are inherited unchanged from
    :class:`MarkdownFrontmatter`.
    """

    type: Literal["set"] = "set"  # type: ignore

    # feat-189 Phase 120 (C13) precedent: redeclare the inherited `status`
    # field (the only way to attach `json_schema_extra` to it) so the
    # generated JSON Schema carries this same closed set as an `enum` key --
    # schema-level documentation only: pydantic-core never enforces it, and
    # `_validate_status` below remains the sole enforcement point. The
    # default stays the base's own `"draft"`.
    status: str = Field(default=DEFAULT_STATUS, json_schema_extra={"enum": sorted(_ALLOWED_STATUSES)})

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
