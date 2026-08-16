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

"""Resource: specmgr://tsk/list (Task 3.10).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``req.resources.req_list``/``specmgr://req/list``.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...server import mcp
from ..models.v1 import TskSummary
from ..tools._io import read_tsk
from ..tools._paths import iter_tsk_paths


@mcp.resource(
    "specmgr://tsk/list",
    name="tsk_list",
    title="TSK List",
    description=(
        "Ids, titles, statuses, and refs of every task list in the configured "
        "task list base directory, for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from "
        "disk -- for documents that have no assigned id; use it with the get_tsk tool "
        "instead."
    ),
    mime_type="application/json",
)
def tsk_list() -> list[TskSummary]:
    """Return a one-line summary of every task list in the configured base directory.

    A file that fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.tsk.models.v1.parse_tsk` raises) is silently
    skipped -- a single malformed file must not break listing every other
    valid one (mirrors ``tsk.tools._paths.find_tsk_path``'s own
    skip-on-parse-failure rule).

    Returns
    -------
    list[TskSummary]
        One entry per successfully-parsed ``*.md`` file, in filename-sorted
        order. Empty if the base directory does not exist or holds no
        task lists.
    """
    summaries: list[TskSummary] = []
    for path in iter_tsk_paths():
        try:
            doc = read_tsk(path)
        except (AssertionError, ValidationError):
            continue
        summaries.append(
            TskSummary(
                id=doc.frontmatter.id,
                title=doc.body.text,
                status=doc.frontmatter.status,
                ref=path.stem,
            )
        )
    return summaries
