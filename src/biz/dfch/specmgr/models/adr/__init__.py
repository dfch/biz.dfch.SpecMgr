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

See ``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md`` §3-§6 for the design this package implements:

- :class:`AdrFrontmatter` -- the YAML frontmatter block (plan §3), including
  the specmgr schema version (``version``, a specmgr-only extension key,
  not part of the MADR 4.0.0 standard).
- :class:`AdrBody` -- the whole-section body fields (plan §4) plus the
  dynamic :class:`AdrOption` collection (plan §5).
- :class:`AdrOption` -- one ``### Option N: {title}`` sub-section.
- :class:`Adr` -- a full ADR document (frontmatter + body).
- :func:`parse_adr` -- parses an on-disk ``.md`` file's text into an
  :class:`Adr` (plan §7/§10 item 2); :class:`AdrParseError` is its
  structural-error type (see ``v1.parser`` for the full parse-error split).
- :func:`render_adr` -- renders an :class:`Adr` back into the canonical
  on-disk ``.md`` text (plan §7/§10 item 2, the other half of the
  parse/render pipeline).

The MCP tool wrappers (plan §10 item 3) are a separate, later step.

**Schema versioning (plan §6):** every model class lives under a ``vN``
sibling package (currently only :mod:`.v1`), one per *major* schema
version -- see :data:`SCHEMA_MAJOR_VERSION`/``CURRENT_SCHEMA_VERSION`` in
``v1._util``, and ``AdrFrontmatter.version`` in ``v1.frontmatter``. The
names re-exported here always point at the current
version's classes, so ``from biz.dfch.specmgr.models.adr import Adr``
tracks whichever ``vN`` is current without callers needing to know the
version number -- callers that specifically need an older version's
classes (e.g. a migration step) import ``biz.dfch.specmgr.models.adr.v1``
directly instead.
"""

from .v1 import (
    CURRENT_SCHEMA_VERSION,
    SCHEMA_MAJOR_VERSION,
    Adr,
    AdrBody,
    AdrFrontmatter,
    AdrOption,
    AdrOptionNotFoundError,
    AdrParseError,
    AdrSectionError,
    AdrSummary,
    option_create,
    option_delete,
    option_list,
    option_read,
    option_update,
    parse_adr,
    render_adr,
    set_status,
    update_section,
)

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
    "AdrOptionNotFoundError",
    "AdrParseError",
    "AdrSectionError",
    "AdrSummary",
    "option_create",
    "option_delete",
    "option_list",
    "option_read",
    "option_update",
    "parse_adr",
    "render_adr",
    "set_status",
    "update_section",
]
