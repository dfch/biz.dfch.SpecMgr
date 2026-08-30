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

"""``@mcp.tool()`` wrapper: list_feat (Task 2.3).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). Mirrors ``dec.tools.list_dec``'s
overall shape, with two feat-only differences: (1) it scans
``<base>/*/README.md`` via :func:`~biz.dfch.specmgr.feat.tools._paths.iter_feat_paths`,
not ``<base>/*.md``; (2) each :class:`~biz.dfch.specmgr.feat.models.v1.FeatSummary`
also carries the real filesystem ``path`` (REQ-004's Addressing section) and
uses ``ref = path.parent.name`` (the containing folder's own name, which by
convention already equals ``id`` for a healthy document) rather than
``path.stem`` (which would just be the fixed, uninformative ``"README"``).
"""

from __future__ import annotations

from pydantic import ValidationError

from ...general.models import PagedResult
from ...general.tools._paging import normalize_paging, paginate
from ...server import mcp
from ..models.v1 import FeatSummary
from ._io import read_feat
from ._paths import feat_base_dir, feature_title, iter_feat_paths


@mcp.tool(
    name="list_feat",
    title="List features",
    description=(
        "Ids, titles, statuses, and refs of features in the configured feature base directory, "
        "one page at a time, for context before addressing one by id. 'ref' is an opaque, "
        "extensionless identifier -- not a filename to read from disk -- for documents that "
        "have no assigned id; use it with the get_feat tool instead. max_results/offset control "
        "paging (default page size 25, capped at 100); out-of-range values are clamped, not errored."
    ),
)
def list_feat(max_results: int | None = None, offset: int | None = None) -> PagedResult[FeatSummary]:
    """Return one page of one-line feature summaries from the configured base directory.

    A folder whose ``README.md`` fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.feat.models.v1.parse_feat` raises) is silently
    skipped -- a single malformed document must not break listing every
    other valid one. This includes every one of the 17 pre-existing,
    hand-authored feature folders that predate this schema (out of scope
    for this feature, see its own README's Scope section) -- they are
    simply invisible to this tool until migrated. The complete,
    skip-broken-folder-filtered list is materialized first, then paginated
    in memory, so the returned ``total`` always reflects the count of
    parseable documents only, independent of paging.

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
    PagedResult[FeatSummary]
        One entry per successfully-parsed ``README.md`` file within the
        requested page, in folder-name-sorted order. ``results`` is empty
        if the base directory does not exist, holds no parseable feature
        documents, or ``offset`` is past the end of the full list.
    """
    summaries: list[FeatSummary] = []
    for path in iter_feat_paths(feat_base_dir()):
        try:
            doc = read_feat(path)
        except (AssertionError, ValidationError):
            continue
        summaries.append(
            FeatSummary(
                id=doc.frontmatter.id,
                title=feature_title(doc.body.text),
                status=doc.frontmatter.status,
                ref=path.parent.name,
                path=str(path),
            )
        )
    return paginate(summaries, *normalize_paging(max_results, offset))
