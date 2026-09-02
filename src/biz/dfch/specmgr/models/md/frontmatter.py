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

"""Generic base frontmatter model shared by every markdown-backed document type.

Per ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (REQ-006/Task 4.1 of
``feat-5-md-model-parser``): this is a *base* frontmatter model carrying only
the handful of fields every document type shares. A concrete document type
(e.g. a future ``uc``/``req``) defines its own frontmatter model that
subclasses :class:`MarkdownFrontmatter` and adds its own fields, narrowing
``type`` to a fixed ``Literal[...]`` value, e.g.::

    from typing import Literal

    class UcFrontmatter(MarkdownFrontmatter):
        type: Literal["uc"] = "uc"
        # ... uc-specific fields ...

This model is deliberately independent of ``models.adr.v1.AdrFrontmatter``:
no shared base class, no shared validator module. ``AdrFrontmatter`` is left
exactly as-is (see the ADR's Decision Outcome/Consequences) -- a possible
future convergence is noted there but not decided.

This module has no import dependency on ``models.adr.v1`` or any other
document-type package, consistent with ``models.md``'s existing
no-dependency invariant (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae).
"""

from __future__ import annotations

import re

from pydantic import BaseModel, field_validator

from ._util import CURRENT_SCHEMA_VERSION, blank_to_none, default_if_blank, validate_schema_version

#: Default ``status`` value when omitted or blank/``None``.
DEFAULT_STATUS = "draft"

#: The canonical date+time variant (D4/D5/D7,
#: ``.specmgr/feat/feat-38-39-41-43-44/README.md`` Design Notes):
#: space-separated ``yyyy-MM-dd HH:mm:ss.fff``, followed by either ``Z``
#: (UTC) or a signed ``±HH:mm`` offset. Date-only, ``T``-separated,
#: microsecond, and timezone-less values all fail this pattern -- ``created``/
#: ``updated`` are the two fields that are strictly date+time-only (D5); a
#: date-only value is legitimate elsewhere (e.g. a DEC/VCR/TSK ``UpdateEntry``
#: heading) but never here.
_DATE_TIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$")


class MarkdownFrontmatter(BaseModel):
    """The core YAML frontmatter fields shared by every markdown document type.

    Parameters
    ----------
    id:
        The specmgr-assigned document identifier (a server-generated
        identifier string), used to resolve ``id -> file path``. Optional,
        defaults to ``None`` so existing/hand-authored files without one
        still parse; they are just not addressable via id-based tools until
        one is assigned.
    type:
        The document-type discriminator (e.g. ``"uc"``, ``"req"``).
        Mandatory with no default on this base model -- every concrete
        document type must supply its own fixed value, typically by
        overriding this field as ``Literal["..."] = "..."`` in its own
        frontmatter subclass. This lets a generic loader read ``type``
        alone from a raw frontmatter block to decide which concrete
        subclass to validate the rest of the block against, without
        needing to know that beforehand. Must not be blank.
    created:
        Free-form date/timestamp the document was first created. Optional.
    updated:
        Free-form date/timestamp the document was last updated. Optional.
    status:
        Free-form lifecycle status. Defaults to ``"draft"`` -- both when
        the key is absent entirely and when it is present but blank (e.g. a
        template shipping a placeholder ``status:`` with nothing after the
        colon, which YAML parses as ``None``, not an absent key).
        Deliberately not restricted to a fixed set of values here (unlike
        ``AdrFrontmatter.status``'s closed six-value enum): different
        document types may have different valid status vocabularies, and a
        subclass is free to add its own stricter validator.
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. Defaults to
        :data:`biz.dfch.specmgr.models.md._util.CURRENT_SCHEMA_VERSION`.
        Must share this package's major component -- a
        ``MarkdownFrontmatter`` (or subclass) never accepts a ``"2.x.x"``
        value while ``models.md``'s
        :data:`biz.dfch.specmgr.models.md._util.SCHEMA_MAJOR_VERSION` is
        ``1``.
    classification:
        Free-text classification label for the document -- e.g. a security
        classification, a business-confidentiality level, or a
        project-specific taxonomy. Optional, defaults to ``None`` so every
        existing document without this key keeps parsing unchanged.
        Deliberately not restricted to a fixed set of values -- specmgr
        imposes no single classification scheme; blank/whitespace-only
        input normalizes to ``None``, same as ``created``/``updated``.
    """

    id: str | None = None
    type: str
    created: str | None = None
    updated: str | None = None
    status: str = DEFAULT_STATUS
    version: str = CURRENT_SCHEMA_VERSION
    classification: str | None = None

    @field_validator("type")
    @classmethod
    def _validate_type_non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("type must not be blank")
        return value

    @field_validator("version")
    @classmethod
    def _validate_version(cls, value: str) -> str:
        return validate_schema_version(value)

    @field_validator("status", mode="before")
    @classmethod
    def _default_blank_status_to_draft(cls, value: object) -> object:
        return default_if_blank(value, DEFAULT_STATUS)

    @field_validator("created", "updated", "classification", mode="before")
    @classmethod
    def _optional_blank_to_none(cls, value: str | None) -> str | None:
        return blank_to_none(value)

    @field_validator("created", "updated", mode="after")
    @classmethod
    def _validate_date_time_format(cls, value: str | None) -> str | None:
        """Reject any non-``None`` ``created``/``updated`` value that isn't the date+time variant (D5).

        Runs after :meth:`_optional_blank_to_none` (mode="before" validators
        on a class run before mode="after" validators on the same class),
        so this validator only ever sees ``None`` or an already-non-blank
        string. ``None`` passes through unchanged; any other value must
        :func:`re.fullmatch` :data:`_DATE_TIME_PATTERN` -- date-only,
        ``T``-separated, microsecond, and timezone-less values are all
        rejected here.
        """
        if value is None:
            return value
        if not _DATE_TIME_PATTERN.fullmatch(value):
            raise ValueError(
                f"created/updated {value!r} must be the date+time variant "
                f"'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset"
            )
        return value
