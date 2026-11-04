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

"""Pydantic model for one line of SET listing output (``list_set``).

Mirrors :class:`~biz.dfch.specmgr.txt.models.v1.summary.TxtSummary`
field-for-field, for the paged ``list_set`` tool -- a paged MCP tool from
day one per ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so SET has no
``specmgr://set/list`` resource. Subclasses
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary` for its
``id``/``title``/``status``/``ref``/``path``/``error`` fields, with no
extra fields (the plan does not call for exposing anything of the set body
in the listing -- a set is a convenience bundle, the items remain the
source of truth, and a listing row that duplicated the bundle's contents
would be a cache of second-hand facts).
"""

from __future__ import annotations

from ....general.models.summary import DocSummary

__all__ = ["SetSummary"]


class SetSummary(DocSummary):
    """One line of ``list_set`` output.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key).
    title:
        The set document's ``# {title}`` H1.
    status:
        The set document's ``frontmatter.status`` value, verbatim (one of
        the closed four-value set ``draft``/``progress``/``done``/
        ``review``).
    ref:
        The document's extensionless base name (e.g.
        ``"set-<uuid>-a-title"``), deliberately *not* a filename or path --
        callers must not read this off disk themselves, only pass it to
        ``get_set`` alongside (or instead of) ``id``. Named ``ref`` rather
        than ``filename`` precisely to avoid inviting direct filesystem
        access (mirrors
        :class:`~biz.dfch.specmgr.txt.models.v1.summary.TxtSummary`).
    """
