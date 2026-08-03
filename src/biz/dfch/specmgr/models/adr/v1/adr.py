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

"""Pydantic model for a full ADR document (frontmatter + body).

Deliberately holds no file/id/path information -- the file/directory
naming and id-assignment scheme is still an open backlog item (plan §9)
and is out of scope for this schema.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, field_validator

from .body import AdrBody
from .frontmatter import AdrFrontmatter

#: The schema major version this module implements. Matches this package's
#: ``vN`` folder name (plan §6) and is the value every ``Adr.version`` in
#: this module must share the major component with -- an ``Adr`` built from
#: ``models.adr.v1`` can never legitimately carry a ``"2.x.x"`` version.
SCHEMA_MAJOR_VERSION = 1

#: The current, default schema version for newly created v1 documents.
#: Bump the minor/patch component here for non-breaking schema evolutions
#: that don't warrant a new ``vN`` package (plan §6); only a breaking change
#: gets a new major version, hence a new sibling package.
CURRENT_SCHEMA_VERSION = f"{SCHEMA_MAJOR_VERSION}.0.0"

_SEMVER_PATTERN = re.compile(r"^(?P<major>\d+)\.\d+\.\d+$")


class Adr(BaseModel):
    """A full ADR document: schema version, YAML frontmatter, and body.

    This is the structured object the future parser produces from an
    on-disk ``.md`` file and the renderer consumes to produce one, and the
    shape ``get_adr``/``create_adr`` (plan §8) are expected to exchange
    with the LLM instead of raw markdown text.

    Parameters
    ----------
    version:
        The ``major.minor.patch`` schema version this document was created
        with. Not part of the ADR's own content (frontmatter/body); it is
        metadata about *our* schema, letting a future parser dispatch an
        on-disk document to the ``models/adr/vN/`` package that understands
        it, and a future migration step recognize a document still on an
        older major version. Defaults to :data:`CURRENT_SCHEMA_VERSION`.
        Must share ``vN``'s major component -- ``models.adr.v1.Adr`` never
        accepts a ``"2.x.x"`` value.
    frontmatter:
        The YAML frontmatter block. See :class:`AdrFrontmatter`.
    body:
        The parsed body sections and options. See :class:`AdrBody`.
    """

    version: str = CURRENT_SCHEMA_VERSION
    frontmatter: AdrFrontmatter
    body: AdrBody

    @field_validator("version")
    @classmethod
    def _validate_version(cls, value: str) -> str:
        match = _SEMVER_PATTERN.match(value)
        if not match:
            raise ValueError(f"version must be 'major.minor.patch', got {value!r}")
        major = int(match.group("major"))
        if major != SCHEMA_MAJOR_VERSION:
            raise ValueError(
                f"version {value!r} has major component {major}, "
                f"but models.adr.v1.Adr only accepts major version {SCHEMA_MAJOR_VERSION}"
            )
        return value
