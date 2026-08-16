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
specmgr://adr/list --   Ids/titles/statuses/refs of every ADR
                        (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/req_schema.json``) so it works from a
                        real, non-editable install.
specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
specmgr://req/template -- A requirement template (every field present, placeholder text)
                          as raw markdown.
specmgr://req/list --   Ids/titles/statuses/refs of every requirement.
specmgr://uc/schema --  The generated UC JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/uc_schema.json``) so it works from a
                        real, non-editable install.
specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
specmgr://uc/template -- A use-case template (every field present, placeholder text)
                          as raw markdown.
specmgr://uc/list --    Ids/titles/statuses/refs of every use case.
specmgr://tsk/schema -- The generated TSK JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/tsk_schema.json``) so it works from a
                        real, non-editable install.
specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
specmgr://tsk/template -- A task list template (every field present, placeholder text)
                          as raw markdown.
specmgr://tsk/list --   Ids/titles/statuses/refs of every task list.
specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
                        characteristics (and sub-characteristics), each with a description.

REQ has no ``specmgr://req/{id}`` resource, unlike ADR -- id-based reads go
through the ``get_req`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
UC has no ``specmgr://uc/{id}`` resource either, for the same reason -- id-based
reads go through the ``get_uc`` tool only. TSK has no ``specmgr://tsk/{id}``
resource either -- id-based reads go through the ``get_tsk`` tool only, and
there never was such a resource to remove in the first place.

Tools
-----
ADR tools (``adr/tools/``): ``get_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``set_status``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc``, ``get_uc_example``,
``get_uc_template``, ``create_uc``, ``update_uc``, ``set_status_uc``, ``delete_uc``
(stub, not yet implemented), ``validate_uc``.
Requirement tools (``req/tools/``): ``parse_req``, ``get_req``, ``get_req_example``,
``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``, ``delete_req``
(stub, not yet implemented), ``validate_req``.
Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk``, ``get_tsk_example``,
``get_tsk_template``, ``create_tsk``, ``update_tsk``, ``set_status_tsk``, ``delete_tsk``
(stub, not yet implemented), ``validate_tsk``.
General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
preserving YAML frontmatter blocks.

Prompts
-------
ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
§11).
Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).
Task list prompts (``tsk/prompts/``): ``create_task``, ``update_task`` -- instructional
text guiding an LLM through the TSK tool sequence above, plus ``implement_task`` --
reads an existing task list via ``get_tsk``, builds a ``TodoWrite`` list from its
items, and uses the ``question`` tool to resolve ambiguity before proceeding.

Modules are grouped domain-first
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
document-type domain"): each document
domain (``adr``, ``uc``, ``req``, ``tsk``, and later ``ac``) is a top-level package
with its own ``tools``/``prompts``/``resources`` sub-packages, self-
registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
tools/resources (e.g. ``specmgr://version``/``specmgr://iso25010`` resources
or the ``mdformat`` tool) stay under the top-level ``general`` package
instead (``general.tools``/``general.resources``). Add a new domain by
creating its top-level package and importing it at the bottom of this
module, next to the existing ``adr``/``general``/``req``/``tsk``/``uc``
imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
decorators actually run. ``req`` and ``tsk`` each register ``tools``,
``resources``, and ``prompts``; ``uc`` registers ``tools`` and ``resources``
-- it has no ``prompts`` sub-package yet.
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
# mcp). Every domain package here (including the cross-cutting `general`
# package, which in turn imports its own `resources`/`tools` sub-packages)
# must be imported for its @mcp.tool()/@mcp.prompt()/@mcp.resource()
# decorators to actually run.
# ---------------------------------------------------------------------------

from . import adr, general, req, tsk, uc  # noqa: E402, F401
