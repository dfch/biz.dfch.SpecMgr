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

"""Verification Case Record (VCR) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `dec/models/v1/frontmatter.py::DecFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["vcr"]`` and narrows the free-form ``status`` to VCR's own closed
four-value set -- a hyphen-free rewording of INCOSE's Guide for Writing
Requirements Attribute A26 ("Need or Requirement Verification Status": "not
started, in work, complete, and approved"), see
`.specmgr/feat/feat-33-vcr/README.md` REQ-004. No separate pass/fail/waived
outcome field exists anywhere in this domain -- `## Coverage` is the only
outcome signal.
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter

#: Fixed, closed set of accepted ``status`` values for verification case
#: records: ``draft`` (not started), ``progress`` (in work), ``complete``
#: (verification activity finished), ``approved`` (result signed off).
#: Deliberately hyphen-free (unlike INCOSE A26's own "not started"/"in
#: work" wording) and with no separate pass/fail/waived outcome value --
#: see REQ-004/Design Notes.
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "progress",
        "complete",
        "approved",
    }
)


class VcrFrontmatter(MarkdownFrontmatter):
    """Verification Case Record (VCR) frontmatter: `MarkdownFrontmatter` narrowed for the ``vcr`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"vcr"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["vcr"] = "vcr"``, so a document
        omitting ``type`` entirely still parses as a verification case record.
    status:
        One of ``"draft"``, ``"progress"``, ``"complete"``, ``"approved"``.
        Narrows the base's free-form ``str = "draft"`` default to this closed
        four-value set. Blank/absent still defaults to ``"draft"`` (inherited
        from the base's ``_default_blank_status_to_draft`` validator, which
        runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["vcr"] = "vcr"  # type: ignore

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
