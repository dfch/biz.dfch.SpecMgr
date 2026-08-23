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

"""Pydantic model for one line of QA listing output.

Mirrors :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary`
field-for-field, for the ``list_qa`` tool. Subclasses
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary` for its
``id``/``title``/``status``/``ref`` fields (feat-13 Task 1.3, REQ-003).

Lives directly in `qa/models/v2/` alongside `QaFrontmatter` -- both are
body-schema-independent DTOs, so neither needs its own `v1`/`v2` split
(feat-14 Phase 8: `qa/models/v1/` was removed once v2 became the domain's
only tool-reachable schema).
"""

from __future__ import annotations

from ....general.models.summary import DocSummary

__all__ = ["QaSummary"]


class QaSummary(DocSummary):
    """One line of ``specmgr://qa/list`` output.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key).
    title:
        The Q&A document's ``# {title}`` H1.
    status:
        The Q&A document's ``frontmatter.status`` value, verbatim.
    ref:
        The document's extensionless base name (e.g.
        ``"qa-<uuid>-a-title"``), deliberately *not* a filename or path --
        callers must not read this off disk themselves, only pass it to
        ``get_qa`` alongside (or instead of) ``id``. Named ``ref`` rather
        than ``filename`` precisely to avoid inviting direct filesystem
        access (mirrors
        :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary`).
    """
