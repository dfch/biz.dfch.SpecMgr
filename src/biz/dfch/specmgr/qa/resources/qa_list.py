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

"""Resource: specmgr://qa/list (Phase 4, Task 4.2).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``adr.resources.adr_list``/``req.resources.req_list``. Deliberately
unfiltered -- characteristics/tags filtering was explicitly deferred for
REQ's own equivalent, and the same deferral applies here.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...server import mcp
from ..models.v1 import QaSummary
from ..tools._io import read_qa
from ..tools._paths import iter_qa_paths


@mcp.resource(
    "specmgr://qa/list",
    name="qa_list",
    title="QA Document List",
    description=(
        "Ids, titles, statuses, and refs of every QA document in the configured "
        "QA base directory, for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from "
        "disk -- for documents that have no assigned id; use it with the get_qa tool "
        "instead."
    ),
    mime_type="application/json",
)
def qa_list() -> list[QaSummary]:
    """Return a one-line summary of every QA document in the configured base directory.

    A file that fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.qa.models.v1.parse_qa` raises) is silently
    skipped -- a single malformed file must not break listing every other
    valid one (mirrors ``qa.tools._paths.find_qa_path``'s own
    skip-on-parse-failure rule).

    Returns
    -------
    list[QaSummary]
        One entry per successfully-parsed ``*.md`` file, in filename-sorted
        order. Empty if the base directory does not exist or holds no QA
        documents.
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
    return summaries
