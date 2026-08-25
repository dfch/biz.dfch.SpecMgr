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

"""Problem Statement (PRB) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `tsk/models/v1/frontmatter.py::TskFrontmatter`/
`qa/models/v2/frontmatter.py::QaFrontmatter`: a subtype of `MarkdownFrontmatter`
that restricts `type` to a fixed ``Literal["prb"]`` and narrows the free-form
``status`` to a closed vocabulary matching a problem statement's own
lifecycle (still being filled in, current state captured, future state
reached, or abandoned) -- see `.specmgr/feat/feat-16-problem-statement/README.md`
Design Notes.
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter

#: Fixed, closed set of accepted ``status`` values for `prb` documents --
#: ``draft`` (still being filled in), ``active`` (current state captured,
#: gap/future state being refined), ``resolved`` (future state reached), or
#: ``cancelled`` (abandoned). Reuses TSK/QA's 4-value pattern/wording
#: convention, with PRB-specific semantics (see the feature README's Design
#: Notes/Decisions Made).
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "active",
        "resolved",
        "cancelled",
    }
)


class PrbFrontmatter(MarkdownFrontmatter):
    """Problem Statement (PRB) frontmatter: `MarkdownFrontmatter` narrowed for the ``prb`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"prb"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["prb"] = "prb"``, so a document
        omitting ``type`` entirely still parses as a problem statement document.
    status:
        One of ``"draft"``, ``"active"``, ``"resolved"``, ``"cancelled"``.
        Narrows the base's free-form ``str = "draft"`` default to this
        closed four-value set. Blank/absent still defaults to ``"draft"``
        (inherited from the base's ``_default_blank_status_to_draft``
        validator, which runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["prb"] = "prb"  # type: ignore

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
