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

"""``@mcp.tool()`` wrapper: get_prb (Task 3.8).

Mirrors ``tsk.tools.get_tsk``/``qa.tools.get_qa`` -- a thin file-I/O/id-lookup
adapter that re-reads and re-parses the current on-disk state on every call;
there is no in-memory cache of a parsed :class:`PrbDocument`: the ``.md``
file itself is always the source of truth.

Implemented as a tool, not a resource, from the start -- id-based single-
document reads for PRB never had a ``specmgr://prb/{id}`` resource in the
first place (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614: "Expose id-based
document reads as a tool, not a resource").
"""

from __future__ import annotations

from ...server import mcp
from ..models.v1 import PrbDocument
from ._io import load_by_id
from ._paths import prb_base_dir


@mcp.tool(
    name="get_prb",
    title="Get problem statement",
    description="Read, parse, and return a full problem statement document (frontmatter and body) by its id.",
)
def get_prb(id: str) -> PrbDocument:
    """Read and return the problem statement identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    PrbDocument
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`._paths.PrbNotFoundError` if no problem statement has
        this id.
    """
    base_dir = prb_base_dir()
    _, doc = load_by_id(base_dir, id)
    return doc
