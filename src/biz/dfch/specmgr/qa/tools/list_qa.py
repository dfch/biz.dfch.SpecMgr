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

"""``@mcp.tool()`` wrapper: list_qa (feat-13-list-paging Task 2.5).

Replaces the earlier ``specmgr://qa/list`` resource (``qa.resources.qa_list``).
Converted from a resource to a tool because MCP resources cannot take
arbitrary parameters (only URI-template path segments), and
``max_results``/``offset`` paging needs exactly that -- the same
resource->tool reasoning already applied to ``get_req``
(ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Deliberately unfiltered --
characteristics/tags filtering was explicitly deferred for REQ's own
equivalent, and the same deferral applies here. See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
contract shared by every ``list_<domain>`` tool.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...general.models import PagedResult
from ...general.tools._paging import normalize_paging, paginate
from ...server import mcp
from ..models.v1 import QaSummary
from ._io import read_qa
from ._paths import iter_qa_paths


@mcp.tool(
    name="list_qa",
    title="List QA documents",
    description=(
        "Ids, titles, statuses, and refs of QA documents in the configured QA base "
        "directory, one page at a time, for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- "
        "for documents that have no assigned id; use it with the get_qa tool instead. "
        "max_results/offset control paging (default page size 25, capped at 100); "
        "out-of-range values are clamped, not errored."
    ),
)
def list_qa(max_results: int | None = None, offset: int | None = None) -> PagedResult[QaSummary]:
    """Return one page of one-line QA document summaries from the configured base directory.

    A file that fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.qa.models.v2.parse_qa` raises) is silently
    skipped -- a single malformed file must not break listing every other
    valid one (mirrors ``qa.tools._paths.find_qa_path``'s own
    skip-on-parse-failure rule). The complete, skip-broken-file-filtered
    list is materialized first, then paginated in memory, so the returned
    ``total`` always reflects the count of parseable documents only,
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
    PagedResult[QaSummary]
        One entry per successfully-parsed ``*.md`` file within the
        requested page, in filename-sorted order. ``results`` is empty if
        the base directory does not exist, holds no QA documents, or
        ``offset`` is past the end of the full list.
    """
    summaries: list[QaSummary] = []
    for path in iter_qa_paths():
        try:
            doc = read_qa(path)
        except (AssertionError, ValidationError):
            continue
        summaries.append(
            QaSummary(
                id=doc.frontmatter.id,
                title=doc.body.text,
                status=doc.frontmatter.status,
                ref=path.stem,
            )
        )
    return paginate(summaries, *normalize_paging(max_results, offset))
