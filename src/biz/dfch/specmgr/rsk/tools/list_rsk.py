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

"""``@mcp.tool()`` wrapper: list_rsk (Task 3.14).

Per feat-13 / ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, listing is a paged
``@mcp.tool()`` rather than a ``specmgr://rsk/list`` resource: MCP resources
cannot take arbitrary parameters (only URI-template path segments), and
``max_results``/``offset`` paging needs exactly that -- the same resource->
tool reasoning already applied to ``get_req`` (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614) and ``list_tsk``. Mirrors
``tsk.tools.list_tsk`` line-for-line in mechanism, with one deliberate
difference: each summary line is built by
:meth:`~biz.dfch.specmgr.rsk.models.v1.RskSummary.from_document` (a
model-layer factory) instead of inline construction, because ``RskSummary``
carries six risk-specific derived fields (the zone levels, the TARA word,
the first ``## Scope`` entry, and the residual-risk coordinates) that the
factory derives from the parsed assessments in one place -- see the feature
README's Decisions Made.

feat-81-83-validation Phase 3 (REQ-006/REQ-007) routed this tool through the
shared ``general.tools._listing.build_summaries`` helper: a file that fails
to parse now appears inline in ``results`` as a failed entry rather than
being silently skipped. ``RskSummary``'s own extra risk-specific fields (not
part of the shared ``DocSummary`` base) cannot be represented by the
generic ``general.tools._listing.default_failed_summary`` builder every
other domain uses, so a failed row is instead built by
``rsk.tools._sentinel.build_failed_rsk_summary`` from a fixed, valid,
deliberately worst-case-severity sentinel document -- see that module's own
docstring and the feature README's Design Notes ("``RskSummary``'s extra
fields -- sentinel-document design") for the full rationale.
"""

from __future__ import annotations

from pathlib import Path

from ...general.models import PagedResult
from ...general.tools._listing import build_summaries
from ...general.tools._paging import normalize_paging, paginate
from ...server import mcp
from ..models.v1 import RskDocument, RskSummary
from ._io import read_rsk
from ._paths import iter_rsk_paths
from ._sentinel import build_failed_rsk_summary


def _to_summary(doc: RskDocument, path: Path) -> RskSummary:
    result = RskSummary.from_document(doc, ref=path.stem, path=str(path.resolve()))
    return result


@mcp.tool(
    name="list_rsk",
    title="List risks",
    description=(
        "Ids, titles, statuses, and refs of risks in the configured risk base directory, "
        "one page at a time, for context before addressing one by id. Each line also carries "
        "the initial/residual 5x5 zone levels, the TARA strategy word, the first `## Scope` "
        "entry, and the residual-risk coordinates (residual_probability/residual_impact/"
        "residual_product). 'ref' is an opaque, extensionless identifier -- not a filename to "
        "read from disk -- for documents that have no assigned id; use it with the get_rsk "
        "tool instead. max_results/offset control paging (default page size 25, capped at "
        "100); out-of-range values are clamped, not errored."
    ),
)
def list_rsk(max_results: int | None = None, offset: int | None = None) -> PagedResult[RskSummary]:
    """Return one page of one-line risk summaries from the configured base directory.

    A file that fails to parse (``AssertionError``, ``pydantic.ValidationError``,
    or ``yaml.YAMLError`` -- the same channels
    :func:`~biz.dfch.specmgr.rsk.models.v1.parse_rsk` raises) appears inline
    in ``results`` as its own failed entry (``id=None``, ``title``/``status``
    both the fixed marker ``"<failed to parse>"`` (overridden onto a
    genuinely-parsed sentinel document -- see ``rsk.tools._sentinel``'s own
    docstring for why ``title`` cannot be read off that document's real H1
    the way every other domain's failed entry reads it off its own
    ``path.stem``-adjacent marker), ``ref``/``path`` populated the same way
    as a successful entry, and ``error`` carrying the exception's message)
    rather than being silently skipped (feat-81-83-validation Phase 3,
    REQ-006) -- a single malformed file must not break listing every other
    valid one. The complete list (successes and failures both) is
    materialized first, then paginated in memory, so the returned
    ``total``/``error_count`` always reflect the whole directory,
    independent of paging.

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
    PagedResult[RskSummary]
        One entry per ``*.md`` file within the requested page (successes
        and failures both), in filename-sorted order. ``results`` is empty
        if the base directory does not exist, holds no risks, or ``offset``
        is past the end of the full list.
    """
    summaries, error_count = build_summaries(iter_rsk_paths(), read_rsk, _to_summary, build_failed_rsk_summary)
    return paginate(summaries, *normalize_paging(max_results, offset), error_count=error_count)
