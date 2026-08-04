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

"""Resource: specmgr://adr/{id} (plan §8, §9a).

Implemented as an MCP resource rather than an ``@mcp.tool()`` (plan §9a),
matching this repo's existing ``specmgr://version`` convention.
"""

from __future__ import annotations

from ...models.adr import Adr
from ...server import mcp
from ..tools._io import load_by_id
from ..tools._paths import adr_base_dir


@mcp.resource(
    "specmgr://adr/{id}",
    name="adr_get",
    title="Get ADR",
    description=(
        "Full ADR document (frontmatter and body) for the given id, as structured JSON -- "
        "a resource-based, read-only counterpart of the get_adr tool for plain context "
        "retrieval without a tool round-trip."
    ),
    mime_type="application/json",
)
def adr_get(id: str) -> Adr:  # noqa: A002 -- "id" matches the plan's tool/resource parameter name throughout
    """Return the ADR identified by ``id`` as a template resource.

    Same id-resolution and no-cache, re-read-per-call design as
    ``adr.tools.get_adr.get_adr`` (plan §7, §9a) -- this is simply that same
    read exposed as an MCP resource (``specmgr://adr/{id}``) instead of a
    ``@mcp.tool()``, for a host that wants to address a specific ADR as
    context without an explicit tool call.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier (plan §9a).

    Returns
    -------
    Adr
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`~biz.dfch.specmgr.adr.tools._paths.AdrNotFoundError`
        if no ADR has this id.
    """
    base_dir = adr_base_dir()
    _, adr = load_by_id(base_dir, id)
    return adr
