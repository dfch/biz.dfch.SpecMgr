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

"""``@mcp.tool()`` wrapper: list_tsk (feat-13-list-paging Task 2.4).

Replaces the earlier ``specmgr://tsk/list`` resource
(``tsk.resources.tsk_list``). Converted from a resource to a tool because
MCP resources cannot take arbitrary parameters (only URI-template path
segments), and ``max_results``/``offset`` paging needs exactly that -- the
same resource->tool reasoning already applied to ``get_req``
(ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
contract shared by every ``list_<domain>`` tool.

feat-81-83-validation Phase 3 (REQ-006/REQ-007) routed this tool through
the shared ``general.tools._listing.build_summaries`` helper: a file that
fails to parse now appears inline in ``results`` as a failed entry (marker
``title``/``status``, ``ref``, ``path``, and ``error``) and contributes to
both ``total`` and the new ``error_count``, instead of being silently
skipped.
"""

from __future__ import annotations

from pathlib import Path

from ...general.models import PagedResult
from ...general.tools._listing import build_summaries, default_failed_summary
from ...general.tools._paging import normalize_paging, paginate
from ...server import mcp
from ..models.v1 import TskDocument, TskSummary
from ._io import read_tsk
from ._paths import iter_tsk_paths


def _to_summary(doc: TskDocument, path: Path) -> TskSummary:
    result = TskSummary(
        id=doc.frontmatter.id,
        title=doc.body.text,
        status=doc.frontmatter.status,
        ref=path.stem,
        path=str(path.resolve()),
    )
    return result


def _to_failed_summary(path: Path, error: Exception) -> TskSummary:
    result = default_failed_summary(TskSummary, path, error)
    return result


@mcp.tool(
    name="list_tsk",
    title="List task lists",
    description=(
        "Ids, titles, statuses, and refs of task lists in the configured task list base "
        "directory, one page at a time, for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- "
        "for documents that have no assigned id; use it with the get_tsk tool instead. "
        "max_results/offset control paging (default page size 25, capped at 100); "
        "out-of-range values are clamped, not errored."
    ),
)
def list_tsk(max_results: int | None = None, offset: int | None = None) -> PagedResult[TskSummary]:
    """Return one page of one-line task-list summaries from the configured base directory.

    A file that fails to parse (``AssertionError``, ``pydantic.ValidationError``,
    or ``yaml.YAMLError`` -- the same channels
    :func:`~biz.dfch.specmgr.tsk.models.v1.parse_tsk` raises) appears inline
    in ``results`` as its own failed entry (``id=None``, ``title``/``status``
    both the fixed marker ``"<failed to parse>"``, ``ref``/``path``
    populated the same way as a successful entry, and ``error`` carrying the
    exception's message) rather than being silently skipped
    (feat-81-83-validation Phase 3, REQ-006) -- a single malformed file must
    not break listing every other valid one. The complete list (successes
    and failures both) is materialized first, then paginated in memory, so
    the returned ``total``/``error_count`` always reflect the whole
    directory, independent of paging.

    Parameters
    ----------
    max_results:
        Maximum number of summaries to return in this page. Defaults to
        ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);
        otherwise clamped into range (see
        :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
    offset:
        Zero-based index of the first summary to include in this page.
        Defaults to ``0`` when not given (``None``); negative values are
        floored to ``0``.

    Returns
    -------
    PagedResult[TskSummary]
        One entry per ``*.md`` file within the requested page (successes
        and failures both), in filename-sorted order. ``results`` is empty
        if the base directory does not exist, holds no task lists, or
        ``offset`` is past the end of the full list.
    """
    summaries, error_count = build_summaries(iter_tsk_paths(), read_tsk, _to_summary, _to_failed_summary)
    return paginate(summaries, *normalize_paging(max_results, offset), error_count=error_count)
