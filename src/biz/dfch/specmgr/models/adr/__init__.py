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

"""Pydantic models for MADR 4.0.0-based Architecture Decision Records.

See ``doc/adr-tool-plan.md`` §3-§6 for the design this package implements:

- :class:`AdrFrontmatter` -- the YAML frontmatter block (plan §3).
- :class:`AdrBody` -- the whole-section body fields (plan §4) plus the
  dynamic :class:`AdrOption` collection (plan §5).
- :class:`AdrOption` -- one ``### Option N: {title}`` sub-section.
- :class:`Adr` -- a full ADR document (schema version + frontmatter + body).

This subpackage holds only the schema itself; the parser/renderer and the
MCP tool wrappers are separate, later steps (plan §10, items 2-3).

**Schema versioning (plan §6):** every model class lives under a ``vN``
sibling package (currently only :mod:`.v1`), one per *major* schema
version -- see :data:`SCHEMA_MAJOR_VERSION`/``CURRENT_SCHEMA_VERSION`` in
``v1.adr``. The names re-exported here always point at the current
version's classes, so ``from biz.dfch.specmgr.models.adr import Adr``
tracks whichever ``vN`` is current without callers needing to know the
version number -- callers that specifically need an older version's
classes (e.g. a migration step) import ``biz.dfch.specmgr.models.adr.v1``
directly instead.
"""

from .v1 import CURRENT_SCHEMA_VERSION, SCHEMA_MAJOR_VERSION, Adr, AdrBody, AdrFrontmatter, AdrOption

# NOTE: mirrors v1.__all__ verbatim (this package always re-exports
# "current"); pylint flags this as duplicate-code (R0801), but a literal
# list is required for ruff's static __all__/F401 check to recognize these
# names as exported -- a derived `list(v1.__all__)` fails that check instead.
__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "SCHEMA_MAJOR_VERSION",
    "Adr",
    "AdrBody",
    "AdrFrontmatter",
    "AdrOption",
]
