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

"""Resource: specmgr://req/{id} (Task 3.17).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``adr.resources.adr_get``/``specmgr://adr/{id}``. Per Task 3.9's design
discussion, id-based single-document read is a resource only, everywhere in
the REQ lifecycle surface -- there is no ``get_req`` tool.
"""

from __future__ import annotations

from ...server import mcp
from ..models.v1 import ReqDocument
from ..tools._io import load_by_id
from ..tools._paths import req_base_dir


@mcp.resource(
    "specmgr://req/{id}",
    name="req_get",
    title="Get requirement",
    description=(
        "Full requirement document (frontmatter and body) for the given id, as structured "
        "JSON -- a resource-based, read-only single-document lookup, mirroring specmgr://adr/{id}."
    ),
    mime_type="application/json",
)
def req_get(id: str) -> ReqDocument:  # noqa: A002 -- "id" matches this surface's parameter name throughout
    """Return the requirement identified by ``id`` as a template resource.

    Same id-resolution and no-cache, re-read-per-call design as every other
    REQ tool/resource -- the ``.md`` file on disk is always re-read and
    re-parsed, never cached in memory.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    ReqDocument
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`~biz.dfch.specmgr.req.tools._paths.ReqNotFoundError`
        if no requirement has this id.
    """
    base_dir = req_base_dir()
    _, doc = load_by_id(base_dir, id)
    return doc
