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

"""Pydantic model for one line of ADR listing output (plan §8, §9a).

**Deliberately does not subclass**
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary`, unlike
``ReqSummary``/``UcSummary``/``TskSummary``/``QaSummary`` (feat-13 Task
1.3, REQ-003): this module is part of the dependency-free base library
(``models/adr`` has no dependency on ``mcp``/``tools``/``resources``/
``prompts``), but importing anything under ``general`` (including
``general.models``) transitively imports ``general.tools``, which imports
``server.mcp`` -- an ``mcp``-extra-only dependency. Subclassing would
therefore silently add a new ``mcp`` dependency to the base library.
:class:`AdrSummary` keeps its own field-identical declaration instead; see
``.specmgr/feat/feat-13-list-paging/README.md``'s Decisions Made log and
``tests/general/models/test_summary.py`` for the structural (not
inheritance-based) equivalence check.
"""

from __future__ import annotations

from pydantic import BaseModel


class AdrSummary(BaseModel):
    """One line of ``list_adr`` tool output (plan §8, §9a).

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key -- plan §9a).
    title:
        The ADR's ``# {title}`` H1.
    status:
        The ADR's ``frontmatter.status`` value, verbatim.
    ref:
        The document's extensionless base name (e.g.
        ``"<uuid>-a-title"``), deliberately *not* a filename or path --
        callers must not read this off disk themselves, only pass it to
        ``get_adr``/``specmgr://adr/{id}`` alongside (or instead of) ``id``.
        Named ``ref`` rather than ``filename`` precisely to avoid inviting
        direct filesystem access.
    """

    id: str | None
    title: str
    status: str
    ref: str
