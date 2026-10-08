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

"""``@mcp.tool()`` wrapper: list_gol (Task 3.9).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13: "Expose ``list_<domain>`` as a paged
MCP tool, not a resource") -- unlike REQ/UC/TSK/QA/PRB (which launched as a
``specmgr://<domain>/list`` resource and were converted later in
feat-13-list-paging), GOL is a new domain built after that ADR was accepted,
so it must not repeat that resource-then-convert history. See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging contract
shared by every ``list_<domain>`` tool.

feat-81-83-validation Phase 3 (REQ-006/REQ-007) routed this tool through
the shared ``general.tools._listing.build_summaries`` helper: a file that
fails to parse now appears inline in ``results`` as a failed entry (marker
``title``/``status``, ``ref``, ``path``, and ``error``) and contributes to
both ``total`` and the new ``error_count``, instead of being silently
skipped.

**feat-200-list (GitHub issue #200), Task 110.100: the optional ``glob``
parameter.** This tool now takes an optional, case-insensitive ``glob``
pattern matched against each document's own id (a UUID; REQ-002/REQ-004):
the shared ``general.tools._listing.filter_summaries_by_glob`` helper runs
on the materialized row list, between this tool's own row build and the
``total``/paging step, so it never re-scans the filesystem on its own. A
failed-to-parse row carries ``id=None`` and therefore never matches, so a
glob-given result has no failed rows and ``error_count = 0`` by
construction (REQ-003); ``total`` is the match count and
``offset``/``max_results`` paging keeps its existing meaning on that
smaller set (ACC-004). ``glob=None`` (the default) leaves every outcome
byte-identical to the pre-glob behaviour (REQ-005), and an empty string is
a pattern, not an off-switch (it matches no id and yields a zero-row
result).
"""

from __future__ import annotations

from pathlib import Path

from ...general.models import PagedResult
from ...general.tools._listing import build_summaries, default_failed_summary, filter_summaries_by_glob
from ...general.tools._paging import normalize_paging, paginate
from ...server import mcp
from ..models.v1 import GolDocument, GolSummary
from ._cache import reconcile_gol_cache
from ._io import read_gol
from ._paths import iter_gol_paths


def _to_summary(doc: GolDocument, path: Path) -> GolSummary:
    result = GolSummary(
        id=doc.frontmatter.id,
        title=doc.body.text,
        status=doc.frontmatter.status,
        ref=path.stem,
        path=str(path.resolve()),
    )
    return result


def _to_failed_summary(path: Path, error: Exception) -> GolSummary:
    result = default_failed_summary(GolSummary, path, error)
    return result


@mcp.tool(
    name="list_gol",
    title="List goals",
    description=(
        "Ids, titles, statuses, and refs of goals in the configured goal base directory, "
        "one page at a time, for context before addressing one by id. 'ref' is an opaque, "
        "extensionless identifier -- not a filename to read from disk -- for documents that "
        "have no assigned id; use it with the get_gol tool instead. "
        "An optional glob pattern (e.g. 'dead*') filters the listing to the goals "
        "whose id matches it, case-insensitively; glob=None (the default) lists everything, "
        "and an empty string matches nothing. max_results/offset control "
        "paging (default page size 25, capped at 100); out-of-range values are clamped, not errored."
    ),
)
def list_gol(
    max_results: int | None = None,
    offset: int | None = None,
    glob: str | None = None,
) -> PagedResult[GolSummary]:
    """Return one page of one-line goal summaries from the configured base directory.

    A file that fails to parse (``AssertionError``, ``pydantic.ValidationError``,
    or ``yaml.YAMLError`` -- the same channels
    :func:`~biz.dfch.specmgr.gol.models.v1.parse_gol` raises) appears inline
    in ``results`` as its own failed entry (``id=None``, ``title``/``status``
    both the fixed marker ``"<failed to parse>"``, ``ref``/``path``
    populated the same way as a successful entry, and ``error`` carrying the
    exception's message) rather than being silently skipped
    (feat-81-83-validation Phase 3, REQ-006) -- a single malformed file must
    not break listing every other valid one. The complete list (successes
    and failures both) is materialized first, then -- when ``glob`` is given
    -- filtered to the rows whose ``id`` matches it (the shared
    ``general.tools._listing.filter_summaries_by_glob`` helper, applied
    between the row build and the ``total``/paging step), then paginated in
    memory, so the returned ``total``/``error_count`` always reflect the
    whole directory (or that filtered subset), independent of paging.

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
    glob:
        Optional glob pattern matched, case-insensitively, against each
        document's own id (a UUID) -- e.g. ``"dead*"`` (feat-200-list,
        GitHub issue #200, REQ-002/REQ-004). Defaults to ``None`` (no
        filtering: the complete directory is listed, exactly as before --
        REQ-005). An empty string is a pattern, not an off-switch: it
        matches no id (ids are never empty) and yields a zero-row result.
        Failed-to-parse rows carry ``id=None`` and therefore never match
        any pattern, so a glob-given result has no failed rows and
        ``error_count = 0`` by construction (REQ-003); ``total`` is the
        match count and ``offset``/``max_results`` paging keeps its existing
        meaning on that smaller set.

    Returns
    -------
    PagedResult[GolSummary]
        One entry per ``*.md`` file within the requested page (successes
        and failures both -- only entries whose ``id`` matches ``glob`` when
        it is given), in filename-sorted order. ``results`` is empty if the
        base directory does not exist, holds no goals, ``offset`` is past
        the end of the full list, or no id matches ``glob``.
    """
    paths = list(iter_gol_paths())
    reconcile_gol_cache(paths)  # feat-107-doc-cache Phase 4, REQ-005
    summaries, error_count = build_summaries(paths, read_gol, _to_summary, _to_failed_summary)

    # feat-200-list, Task 110.100 (REQ-002/REQ-003): the id-glob filter runs between the row build
    # above and the total/paging step below -- never a filesystem re-scan.
    if glob is not None:
        summaries, error_count = filter_summaries_by_glob(summaries, glob)

    return paginate(summaries, *normalize_paging(max_results, offset), error_count=error_count)
