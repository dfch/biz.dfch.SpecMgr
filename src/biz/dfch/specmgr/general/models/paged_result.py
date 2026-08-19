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

"""Generic paged-result wrapper shared by every ``list_<domain>`` MCP tool (feat-13 Task 1.1).

Shape is taken verbatim from this project's ``asdste100`` MCP tools (e.g.
``word_list``, ``rules_examples``), whose live output is
``{ total, offset, max_results, truncated, results: [...] }`` -- reused
rather than invented so the contract stays consistent across d-fens MCP
servers (see ``.specmgr/feat/feat-13-list-paging/README.md`` Design Notes).
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

__all__ = ["PagedResult"]

#: Element type held by a :class:`PagedResult`'s ``results`` list.
T = TypeVar("T")


class PagedResult(BaseModel, Generic[T]):
    """One page of results plus the paging metadata needed to fetch the next page.

    Every ``list_<domain>`` MCP tool (``list_adr``, ``list_req``, ``list_uc``,
    ``list_tsk``, ``list_qa``) returns this same shape, parameterized by that
    domain's own summary model (e.g. ``PagedResult[ReqSummary]``), so callers
    learn one paging contract instead of five.

    Parameters
    ----------
    total:
        The total number of items available across all pages (e.g. every
        parseable document in a domain's directory), independent of
        ``offset``/``max_results``.
    offset:
        The zero-based index of the first item included in ``results``, as
        actually applied (already normalized -- see
        ``general.tools._paging.normalize_paging``).
    max_results:
        The maximum number of items requested for this page, as actually
        applied (already normalized).
    truncated:
        ``True`` if further items exist beyond this page (i.e.
        ``offset + max_results < total``); ``False`` otherwise, including
        when ``offset`` is past the end of the full item list.
    results:
        The page's items, i.e. ``items[offset : offset + max_results]`` of
        the full, materialized item list.
    """

    total: int
    offset: int
    max_results: int
    truncated: bool
    results: list[T]
