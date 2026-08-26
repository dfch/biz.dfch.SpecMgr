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

"""Risk (RSK) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `tsk/models/v1/frontmatter.py::TskFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["rsk"]`` and narrows the free-form ``status`` to a purpose-fit
closed risk-lifecycle vocabulary.

One deliberate deviation from the other domain frontmatters (REQ/TSK/QA all
keep the base's ``"draft"`` default): a risk lifecycle starts at ``"open"``,
which is not part of the base's default and would fail this class's own
closed-set validator. So `status` is redeclared with a ``"open"`` default and
this class adds a `mode="before"` validator (``_default_blank_status_to_open``)
that maps absent/blank values to ``"open"``. It runs *before* the base's
inherited ``_default_blank_status_to_draft`` (Pydantic applies child-class
``mode="before"`` validators first), so by the time the base's validator sees
the value it is already ``"open"`` and passes it through unchanged.
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md._util import default_if_blank

#: Fixed, closed set of accepted ``status`` values for risks -- a purpose-fit
#: risk lifecycle (identified/monitored, treatment in progress, residual risk
#: accepted, event materialized, resolved/expired, or dropped from the
#: register), rather than reusing REQ's larger, ADR-like set (
#: `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` Design Notes).
_ALLOWED_STATUSES = frozenset(
    {
        "open",
        "mitigating",
        "accepted",
        "occurred",
        "closed",
        "dropped",
    }
)

#: Default ``status`` value when the key is absent or blank -- the starting
#: state of a risk lifecycle. The base `MarkdownFrontmatter`'s own default is
#: ``"draft"``, which is not part of the rsk set.
DEFAULT_RSK_STATUS = "open"


class RskFrontmatter(MarkdownFrontmatter):
    """Risk frontmatter: `MarkdownFrontmatter` narrowed for the ``rsk`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"rsk"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["rsk"] = "rsk"``, so a document
        omitting ``type`` entirely still parses as a risk document.
    status:
        One of ``"open"``, ``"mitigating"``, ``"accepted"``, ``"occurred"``,
        ``"closed"``, ``"dropped"``. Narrows the base's free-form ``str``
        field to this closed six-value set; absent/blank defaults to
        ``"open"`` (``_default_blank_status_to_open`` below, which runs
        before the base's ``_default_blank_status_to_draft``).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["rsk"] = "rsk"  # type: ignore
    status: str = DEFAULT_RSK_STATUS

    @field_validator("status", mode="before")
    @classmethod
    def _default_blank_status_to_open(cls, value: object) -> object:
        """Map an absent/blank ``status`` to ``"open"`` (not the base's ``"draft"``).

        Runs before the base's inherited ``_default_blank_status_to_draft``
        (Pydantic applies child-class ``mode="before"`` validators first), so
        by the time the base's validator sees the value it is already
        ``"open"`` and passes it through unchanged.
        """
        return default_if_blank(value, DEFAULT_RSK_STATUS)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
