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

"""``@mcp.tool()`` wrapper: get_uc (Task 3.1.5).

Mirrors ``req.tools.get_req`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`UcDocument`: the ``.md`` file itself is
always the source of truth. The sole id-based read path for UC.
"""

from __future__ import annotations

from ...server import mcp
from ..models.v2 import UcDocument
from ._io import load_by_id
from ._paths import uc_base_dir


@mcp.tool(
    name="get_uc",
    title="Get use case",
    description="Read, parse, and return a full use-case document (frontmatter and body) by its id.",
)
def get_uc(id: str) -> UcDocument:
    """Read and return the use case identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    UcDocument
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`._paths.UcNotFoundError` if no use case has this id.
    """
    base_dir = uc_base_dir()
    _, doc = load_by_id(base_dir, id)
    return doc
