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

"""Common base for every domain's one-line listing summary (feat-13 Task 1.3, REQ-003/ACC-001).

``ReqSummary``, ``UcSummary``, ``TskSummary``, and ``QaSummary`` each
subclass :class:`DocSummary` instead of independently redeclaring the same
four fields.

**ADR is a deliberate exception.** ``biz.dfch.specmgr.models.adr.v1.summary.
AdrSummary`` does *not* subclass :class:`DocSummary`: that module is part of
the dependency-free base library (``models/adr`` has no dependency on
``mcp``/``tools``/``resources``/``prompts`` -- see ``AGENTS.md``'s "models
location" note), whereas this ``general`` package's own ``__init__.py``
unconditionally imports its ``tools``/``resources``/``prompts``
sub-packages, which in turn import ``server.mcp`` -- so importing anything
under ``general`` (this module included) already requires the ``mcp``
extra to be installed. Making ``AdrSummary`` subclass :class:`DocSummary`
would therefore silently add a new, previously-absent ``mcp`` dependency to
the base library. ``AdrSummary`` instead keeps its own, field-identical
declaration; a structural (not inheritance-based) test asserts the two
stay in sync. See ``.specmgr/feat/feat-13-list-paging/README.md``'s
Decisions Made log for the full rationale.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["DocSummary"]


class DocSummary(BaseModel):
    """Common ``id``/``title``/``status``/``ref`` fields shared by every domain's summary model.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key).
    title:
        The document's ``# {title}`` H1.
    status:
        The document's ``frontmatter.status`` value, verbatim.
    ref:
        The document's extensionless base name (e.g.
        ``"req-<uuid>-a-title"``), deliberately *not* a filename or path --
        callers must not read this off disk themselves, only pass it to
        the matching domain's ``get_<domain>`` tool alongside (or instead
        of) ``id``. Named ``ref`` rather than ``filename`` precisely to
        avoid inviting direct filesystem access.
    """

    id: str | None
    title: str
    status: str
    ref: str
