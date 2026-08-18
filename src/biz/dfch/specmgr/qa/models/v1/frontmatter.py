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

"""Question and Answer (QA) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `tsk/models/v1/frontmatter.py::TskFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["qa"]`` and narrows the free-form ``status`` to TSK's own closed
vocabulary (reused verbatim -- a Q&A document's lifecycle doesn't map
naturally to REQ's larger, ADR-like proposed/accepted/rejected/implemented
set, see the feature README's Design Notes/Decisions Made).
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter

#: Fixed, closed set of accepted ``status`` values for `qa` documents --
#: reused verbatim from TSK's own set (`tsk/models/v1/frontmatter.py`), not
#: REQ's larger set, since a Q&A interview's lifecycle (start it, conduct
#: it, close it out, or drop it) matches TSK's shape, not REQ's.
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "active",
        "done",
        "cancelled",
    }
)


class QaFrontmatter(MarkdownFrontmatter):
    """Question and Answer (QA) frontmatter: `MarkdownFrontmatter` narrowed for the ``qa`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"qa"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["qa"] = "qa"``, so a document
        omitting ``type`` entirely still parses as a Q&A document.
    status:
        One of ``"draft"``, ``"active"``, ``"done"``, ``"cancelled"``. Narrows
        the base's free-form ``str = "draft"`` default to this closed
        four-value set (reused from TSK). Blank/absent still defaults to
        ``"draft"`` (inherited from the base's ``_default_blank_status_to_draft``
        validator, which runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["qa"] = "qa"  # type: ignore

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
