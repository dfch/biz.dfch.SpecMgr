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

"""Requirement frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `uc/models/v2/frontmatter.py::UcFrontmatter`:
subtype of `MarkdownFrontmatter` that restricts `type` to a fixed ``Literal["req"]``
and narrows the free-form ``status`` to an appropriate closed vocabulary for requirements.
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter

#: Fixed, closed set of accepted ``status`` values for requirements -- ADR's six plus
#: ``"implemented"``, since requirements track implementation beyond acceptance.
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "proposed",
        "accepted",
        "superseded",
        "deprecated",
        "rejected",
        "implemented",
    }
)


class ReqFrontmatter(MarkdownFrontmatter):
    """Requirement frontmatter: `MarkdownFrontmatter` narrowed for the ``req`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"req"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["req"] = "req"``, so a document
        omitting ``type`` entirely still parses as a requirement document.
    status:
        One of ``"draft"``, ``"proposed"``, ``"accepted"``, ``"superseded"``,
        ``"deprecated"``, ``"rejected"``, ``"implemented"``. Narrows the base's
        free-form ``str = "draft"`` default to this closed seven-value set.
        Blank/absent still defaults to ``"draft"`` (inherited from the base's
        ``_default_blank_status_to_draft`` validator, which runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["req"] = "req"  # type: ignore

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
