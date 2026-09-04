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

"""``@mcp.tool()`` wrapper: list_prb (Task 3.9).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13: "Expose ``list_<domain>`` as a paged
MCP tool, not a resource") -- unlike REQ/TSK/QA (which launched as a
``specmgr://<domain>/list`` resource and were converted later in
feat-13-list-paging), PRB is a new domain built after that ADR was accepted,
so it must not repeat that resource-then-convert history. See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging contract
shared by every ``list_<domain>`` tool.

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
from ..models.v1 import PrbDocument, PrbSummary
from ._io import read_prb
from ._paths import iter_prb_paths


def _to_summary(doc: PrbDocument, path: Path) -> PrbSummary:
    result = PrbSummary(
        id=doc.frontmatter.id,
        title=doc.body.text,
        status=doc.frontmatter.status,
        ref=path.stem,
        path=str(path.resolve()),
    )
    return result


def _to_failed_summary(path: Path, error: Exception) -> PrbSummary:
    result = default_failed_summary(PrbSummary, path, error)
    return result


@mcp.tool(
    name="list_prb",
    title="List problem statements",
    description=(
        "Ids, titles, statuses, and refs of problem statements in the configured problem "
        "statement base directory, one page at a time, for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- "
        "for documents that have no assigned id; use it with the get_prb tool instead. "
        "max_results/offset control paging (default page size 25, capped at 100); "
        "out-of-range values are clamped, not errored."
    ),
)
def list_prb(max_results: int | None = None, offset: int | None = None) -> PagedResult[PrbSummary]:
    """Return one page of one-line problem-statement summaries from the configured base directory.

    A file that fails to parse (``AssertionError``, ``pydantic.ValidationError``,
    or ``yaml.YAMLError`` -- the same channels
    :func:`~biz.dfch.specmgr.prb.models.v1.parse_prb` raises) appears inline
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
    PagedResult[PrbSummary]
        One entry per ``*.md`` file within the requested page (successes
        and failures both), in filename-sorted order. ``results`` is empty
        if the base directory does not exist, holds no problem statements,
        or ``offset`` is past the end of the full list.
    """
    summaries, error_count = build_summaries(iter_prb_paths(), read_prb, _to_summary, _to_failed_summary)
    return paginate(summaries, *normalize_paging(max_results, offset), error_count=error_count)
