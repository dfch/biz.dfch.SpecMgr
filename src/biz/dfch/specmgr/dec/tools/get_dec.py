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

"""``@mcp.tool()`` wrapper: get_dec (Task 2.2).

Mirrors ``gol.tools.get_gol`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`DecDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for DEC: there is no
``specmgr://dec/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as GOL/REQ/UC/TSK/QA/PRB's own ``get_*`` tools).
"""

from __future__ import annotations

from ...server import mcp
from ..models.v1 import DecDocument
from ._io import load_by_id
from ._paths import dec_base_dir


@mcp.tool(
    name="get_dec",
    title="Get decision",
    description="Read, parse, and return a full decision document (frontmatter and body) by its id.",
)
def get_dec(id: str) -> DecDocument:
    """Read and return the decision identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    DecDocument
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`._paths.DecNotFoundError` if no decision has this id.
    """
    base_dir = dec_base_dir()
    _, doc = load_by_id(base_dir, id)
    return doc
