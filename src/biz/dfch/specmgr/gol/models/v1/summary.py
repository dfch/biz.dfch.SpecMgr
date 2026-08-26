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

"""Pydantic model for one line of GOL listing output (Phase 2, Task 2.3).

Mirrors :class:`~biz.dfch.specmgr.req.models.v1.summary.ReqSummary`/
:class:`~biz.dfch.specmgr.prb.models.v1.summary.PrbSummary` field-for-field,
for the (Phase-3, not-yet-built) ``list_gol`` tool -- a paged MCP tool from
day one per ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so GOL has no
``specmgr://gol/list`` resource. Subclasses
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary` for its
``id``/``title``/``status``/``ref`` fields (feat-13 Task 1.3, REQ-003).
"""

from __future__ import annotations

from ....general.models.summary import DocSummary

__all__ = ["GolSummary"]


class GolSummary(DocSummary):
    """One line of ``list_gol`` output.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key).
    title:
        The goal's ``# {title}`` H1.
    status:
        The goal's ``frontmatter.status`` value, verbatim.
    ref:
        The document's extensionless base name (e.g.
        ``"gol-<uuid>-a-title"``), deliberately *not* a filename or path --
        callers must not read this off disk themselves, only pass it to
        ``get_gol`` alongside (or instead of) ``id``. Named ``ref`` rather
        than ``filename`` precisely to avoid inviting direct filesystem
        access (mirrors
        :class:`~biz.dfch.specmgr.req.models.v1.summary.ReqSummary`).
    """
