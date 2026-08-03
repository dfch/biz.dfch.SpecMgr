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

"""MCP server for ``biz-dfch-specmgr``.

Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).

This is still a placeholder skeleton: no domain tools exist yet. It
registers one resource so far:

Resources
---------
specmgr://version -- Installed version number of the ``biz-dfch-specmgr`` package.

Once a domain model exists, add tool modules (mirroring the ``tools/`` /
``resources/`` package layout used by sibling projects) and import them
at the bottom of this module, next to the ``resources`` import, so their
``@mcp.tool()`` / ``@mcp.resource()`` decorators actually run.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp.server import MCPServer


@asynccontextmanager
async def _lifespan(_server: MCPServer) -> AsyncGenerator[None, None]:
    """Placeholder lifespan: no shared state to initialise yet."""
    yield


mcp = MCPServer(
    name="specmgr",
    instructions="An artifact manager for system specifications.",
    lifespan=_lifespan,
)

# ---------------------------------------------------------------------------
# Resource registration (side-effect: registers all resources on mcp).
# Import tool modules here too once a domain model exists, e.g.:
#   from . import resources, tools
# ---------------------------------------------------------------------------

from . import resources  # noqa: E402, F401
