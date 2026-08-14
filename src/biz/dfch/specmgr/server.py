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
specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
specmgr://adr/list --   Ids/titles/statuses/filenames of every ADR
                        (``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md``).
specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md``).
specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/req_schema.json``) so it works from a
                        real, non-editable install.
specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
specmgr://req/template -- A requirement template (every field present, placeholder text)
                          as raw markdown.
specmgr://req/{id} --   Full requirement document for a given id.
specmgr://req/list --   Ids/titles/statuses/filenames of every requirement.

Tools
-----
ADR tools (``adr/tools/``): ``get_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``set_status``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
Use-case tools (``uc/tools/``): ``parse_uc``.
Requirement tools (``req/tools/``): ``parse_req``, ``get_req_example``, ``get_req_template``,
``create_req``, ``update_req``, ``set_status_req``, ``delete_req`` (stub, not yet
implemented), ``validate_req``.
General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
preserving YAML frontmatter blocks.

Prompts
-------
ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md``
§11).
Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).

Modules are grouped domain-first
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
document-type domain"): each document
domain (``adr``, ``uc``, ``req``, and later ``ac``) is a top-level package
with its own ``tools``/``prompts``/``resources`` sub-packages, self-
registered via the domain package's own ``__init__.py``. ``req`` registers
``tools``, ``resources``, and ``prompts``; ``uc`` currently only registers
``tools`` -- it has no ``prompts`` sub-package yet. Cross-cutting, non-domain-specific
tools/resources (e.g.
``specmgr://version`` resource or ``mdformat`` tool) stay under the
top-level ``general`` (for tools) or ``resources`` (for resources) packages
instead. Add a new domain by creating its top-level package and importing
it at the bottom of this module, next to the existing ``adr``/``general``/
``req``/``resources``/``uc`` imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` /
``@mcp.resource()`` decorators actually run.
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
# Resource/tool/prompt registration (side-effect: registers everything on
# mcp). Every domain package (and the cross-cutting `resources` package)
# here must be imported for its @mcp.tool()/@mcp.prompt()/@mcp.resource()
# decorators to actually run.
# ---------------------------------------------------------------------------

from . import adr, general, req, resources, uc  # noqa: E402, F401
