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

"""Goal (GOL) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `req/models/v1/frontmatter.py::ReqFrontmatter`/
`prb/models/v1/frontmatter.py::PrbFrontmatter`: a subtype of `MarkdownFrontmatter`
that restricts `type` to a fixed ``Literal["gol"]`` and narrows the free-form
``status`` to REQ's exact seven-value set -- goals are business-level
requirements, so requirement-lifecycle semantics apply (see
`.specmgr/feat/feat-18-goal/README.md` Design Notes).
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter

#: Fixed, closed set of accepted ``status`` values for goals -- REQ's exact
#: seven-value set: ``draft`` (still being written), ``proposed`` (under
#: consideration), ``accepted`` (agreed to be pursued), ``implemented`` (the
#: goal has genuinely been reached), ``superseded`` (replaced by another
#: goal), ``deprecated`` (no longer pursued, kept for reference), or
#: ``rejected`` (considered and not pursued).
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


class GolFrontmatter(MarkdownFrontmatter):
    """Goal (GOL) frontmatter: `MarkdownFrontmatter` narrowed for the ``gol`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"gol"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["gol"] = "gol"``, so a document
        omitting ``type`` entirely still parses as a goal document.
    status:
        One of ``"draft"``, ``"proposed"``, ``"accepted"``, ``"superseded"``,
        ``"deprecated"``, ``"rejected"``, ``"implemented"``. Narrows the base's
        free-form ``str = "draft"`` default to this closed seven-value set
        (REQ's exact set -- goals are business-level requirements, so
        requirement-lifecycle semantics apply). Blank/absent still defaults
        to ``"draft"`` (inherited from the base's
        ``_default_blank_status_to_draft`` validator, which runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["gol"] = "gol"  # type: ignore

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
