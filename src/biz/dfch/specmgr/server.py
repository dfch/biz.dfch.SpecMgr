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

Registers the following resources and tools so far (plan §8, §9a):

Resources
---------
specmgr://version -- Installed version number of the ``biz-dfch-specmgr`` package.
specmgr://adr/list -- Ids/titles/statuses/filenames of every ADR (``doc/adr-tool-plan.md``).

Tools
-----
ADR tools (``tools/adr/``): ``get_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``set_status``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.

Prompts
-------
ADR prompts (``prompts/adr/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (``doc/adr-tool-plan.md``
§11).

Add further tool/resource modules (mirroring the ``tools/`` / ``resources/``
package layout used by sibling projects) and import them at the bottom of
this module, next to the existing ``resources``/``tools`` import, so their
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
# Resource/tool registration (side-effect: registers all resources/tools on
# mcp). Every sub-package here must be imported for its @mcp.tool()/
# @mcp.resource() decorators to actually run.
# ---------------------------------------------------------------------------

from . import prompts, resources, tools  # noqa: E402, F401
