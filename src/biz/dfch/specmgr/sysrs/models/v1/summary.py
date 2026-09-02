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

"""Pydantic model for one line of SYSRS listing output (Phase 2, Task 2.4).

Mirrors :class:`~biz.dfch.specmgr.sop.models.v1.summary.SopSummary`
field-for-field, for the (Phase-3, not-yet-built) ``list_sysrs`` tool -- a
paged MCP tool from day one per ADR ec9f5262-9912-49d0-903f-fcfb54f28c13,
so SYSRS has no ``specmgr://sysrs/list`` resource. Subclasses
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary` for its
``id``/``title``/``status``/``ref`` fields (feat-13 Task 1.3, REQ-003) --
plain, no extras, same as SOP's own summary.
"""

from __future__ import annotations

from ....general.models.summary import DocSummary

__all__ = ["SysrsSummary"]


class SysrsSummary(DocSummary):
    """One line of ``list_sysrs`` output.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key).
    title:
        The SYSRS document's ``# System Requirements Specification: {title}`` H1.
    status:
        The SYSRS document's ``frontmatter.status`` value, verbatim.
    ref:
        The document's extensionless base name (e.g.
        ``"sysrs-<uuid>-a-title"``), deliberately *not* a filename or path --
        callers must not read this off disk themselves, only pass it to
        ``get_sysrs`` alongside (or instead of) ``id``. Named ``ref`` rather
        than ``filename`` precisely to avoid inviting direct filesystem
        access (mirrors
        :class:`~biz.dfch.specmgr.sop.models.v1.summary.SopSummary`).
    """
