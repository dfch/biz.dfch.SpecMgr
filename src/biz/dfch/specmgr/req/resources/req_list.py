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

"""Resource: specmgr://req/list (Task 3.18).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``adr.resources.adr_list``/``specmgr://adr/list``. Deliberately unfiltered
-- characteristics/tags filtering (ACC-002) was explicitly deferred during
Task 3.9's design discussion.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...server import mcp
from ..models.v1 import ReqSummary
from ..tools._io import read_req
from ..tools._paths import iter_req_paths


@mcp.resource(
    "specmgr://req/list",
    name="req_list",
    title="Requirement List",
    description=(
        "Ids, titles, statuses, and filenames of every requirement in the configured "
        "requirement base directory, for context before addressing one by id."
    ),
    mime_type="application/json",
)
def req_list() -> list[ReqSummary]:
    """Return a one-line summary of every requirement in the configured base directory.

    A file that fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.req.models.v1.parse_req` raises) is silently
    skipped -- a single malformed file must not break listing every other
    valid one (mirrors ``req.tools._paths.find_req_path``'s own
    skip-on-parse-failure rule).

    Returns
    -------
    list[ReqSummary]
        One entry per successfully-parsed ``*.md`` file, in filename-sorted
        order. Empty if the base directory does not exist or holds no
        requirements.
    """
    summaries: list[ReqSummary] = []
    for path in iter_req_paths():
        try:
            doc = read_req(path)
        except (AssertionError, ValidationError):
            continue
        summaries.append(
            ReqSummary(
                id=doc.frontmatter.id,
                title=doc.body.text,
                status=doc.frontmatter.status,
                filename=path.name,
            )
        )
    return summaries
