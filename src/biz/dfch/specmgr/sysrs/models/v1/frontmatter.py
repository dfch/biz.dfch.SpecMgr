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

"""System Requirements Specification (SYSRS) frontmatter, narrowing `feat-5-md-model-parser`'s generic
`MarkdownFrontmatter`.

Mirrors the pattern established by `sop/models/v1/frontmatter.py::SopFrontmatter`
(and, further back, `gol/models/v1/frontmatter.py::GolFrontmatter`/
`dec/models/v1/frontmatter.py::DecFrontmatter`): a subtype of
`MarkdownFrontmatter` that restricts `type` to a fixed ``Literal["sysrs"]``
and narrows the free-form ``status`` to `sysrs`'s own closed five-value
lifecycle set (``draft`` -> ``review`` -> ``approved`` -> ``active`` ->
``retired``) -- see `.specmgr/feat/feat-32-sysrs/README.md` Design Notes
("Confirmed frontmatter shape", decided 2026-09-01, mirroring `sop`'s
shipped set verbatim, including its GOL/DEC error-message pattern).
``approved`` and ``active`` are kept distinct, same rationale as `sop`:
this system does not model an effective-date/rollout gap, so the
transition from ``approved`` to ``active`` is a manual ``set_status``
call, not automatic.
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter

#: Fixed, closed set of accepted ``status`` values for SYSRS documents -- a
#: five-value lifecycle: ``draft`` (still being written), ``review`` (under
#: review by the responsible authority), ``approved`` (signed off, not yet
#: in force), ``active`` (currently in force -- the specification of record
#: for the system), or ``retired`` (no longer in force, kept for reference).
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "review",
        "approved",
        "active",
        "retired",
    }
)


class SysrsFrontmatter(MarkdownFrontmatter):
    """System Requirements Specification (SYSRS) frontmatter: `MarkdownFrontmatter` narrowed for the ``sysrs``
    document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"sysrs"``. Narrows the base's
        mandatory, default-less ``str`` field to a ``Literal["sysrs"] =
        "sysrs"``, so a document omitting ``type`` entirely still parses
        as a SYSRS document.
    status:
        One of ``"draft"``, ``"review"``, ``"approved"``, ``"active"``,
        ``"retired"``. Narrows the base's free-form ``str = "draft"``
        default to this closed five-value set. Blank/absent still defaults
        to ``"draft"`` (inherited from the base's
        `_default_blank_status_to_draft` validator, which runs before this
        one). ``approved`` (signed off) and ``active`` (currently in
        force) are distinct: the transition between them is a manual
        ``set_status`` call, not automatic.
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``,
    ``classification``) are inherited unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["sysrs"] = "sysrs"  # type: ignore

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
