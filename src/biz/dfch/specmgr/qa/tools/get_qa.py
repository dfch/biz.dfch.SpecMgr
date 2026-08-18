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

"""``@mcp.tool()`` wrapper: get_qa (Phase 4, Task 4.1).

Mirrors ``adr.tools.get_adr``/``req.tools.get_req`` -- a thin
file-I/O/id-lookup adapter that re-reads and re-parses the current on-disk
state on every call; there is no in-memory cache of a parsed
:class:`QaDocument`: the ``.md`` file itself is always the source of truth.

There is no ``specmgr://qa/{id}`` resource -- id-based reads go through
this tool only, mirroring REQ's own choice; see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource") for the full rationale.
"""

from __future__ import annotations

from ...server import mcp
from ..models.v1 import QaDocument
from ._io import load_by_id
from ._paths import qa_base_dir


@mcp.tool(
    name="get_qa",
    title="Get QA document",
    description="Read, parse, and return a full QA document (frontmatter and body) by its id.",
)
def get_qa(id: str) -> QaDocument:
    """Read and return the Question and Answer (QA) document identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    QaDocument
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`._paths.QaNotFoundError` if no QA document has this id.
    """
    base_dir = qa_base_dir()
    _, doc = load_by_id(base_dir, id)
    return doc
