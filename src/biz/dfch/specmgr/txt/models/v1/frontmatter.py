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

"""Free-Form Text (TXT) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `vcr/models/v1/frontmatter.py::VcrFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["txt"]`` and narrows the free-form ``status`` to TXT's own closed
three-value set ``draft``/``progress``/``done`` (REQ-005) -- deliberately
lighter than VCR's four-value verification lifecycle, suited to an
unstructured catch-all document. See `.specmgr/feat/feat-229-txt/README.md`
Decisions Made (2026-10-28 11:30).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.frontmatter import DEFAULT_STATUS

#: Fixed, closed set of accepted ``status`` values for free-form text
#: documents: ``draft`` (not started), ``progress`` (in work), ``done``
#: (finished). Deliberately lighter than VCR's four-value verification
#: lifecycle -- an unstructured catch-all document has no separate
#: sign-off outcome.
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "progress",
        "done",
    }
)


class TxtFrontmatter(MarkdownFrontmatter):
    """Free-Form Text (TXT) frontmatter: `MarkdownFrontmatter` narrowed for the ``txt`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"txt"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["txt"] = "txt"``, so a document
        omitting ``type`` entirely still parses as a free-form text document.
    status:
        One of ``"draft"``, ``"progress"``, ``"done"``. Narrows the base's
        free-form ``str = "draft"`` default to this closed three-value set.
        Blank/absent still defaults to ``"draft"`` (inherited from the base's
        ``_default_blank_status_to_draft`` validator, which runs before this
        one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``,
    ``classification``) are inherited unchanged from
    :class:`MarkdownFrontmatter`.
    """

    type: Literal["txt"] = "txt"  # type: ignore

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
