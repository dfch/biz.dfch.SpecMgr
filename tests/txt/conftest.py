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

"""Collection-time MCP-registration isolation for every ``tests/txt`` test (feat-229-txt Phase 110).

The ``txt`` package is **not** imported by ``server.py``'s own bottom-of-file
domain-import line yet (that registration is this feature's Phase 160). Every
tool module under ``txt/tools/`` still follows the vcr precedent of importing
the shared ``mcp`` application instance from ``...server`` and decorating its
functions with ``@mcp.tool()`` -- so merely *importing* the ``txt.tools``
package registers its seven tools on the process-wide singleton for the rest
of the worker process.

Importing ``txt.tools`` is easy to trigger indirectly: ``txt/__init__.py``
follows the vcr/qa/sysrs precedent of ``from . import prompts, resources,
tools``, so any import of **any** ``biz.dfch.specmgr.txt`` sub-package (the
``tests/txt/models`` test modules import ``biz.dfch.specmgr.txt.models.v1``)
runs the package ``__init__`` and pulls in ``txt.tools`` -- at pytest
collection time, before any test of this directory has run.

Left alone, that import-time registration would inflate the live server
surface from the 115 tools the ``server.py`` import line registers to
122, and ``tests/test_schema_surface_registration.py`` -- which pins exactly
that total (``test_tool_total_is_115``) against the live singleton -- would
fail in every xdist worker that collects anything under ``tests/txt`` (even
one that only runs the model tests), despite the server itself never loading
``txt`` in this phase.

The fix, applied here at conftest-import time: pytest imports this file
before any test module under ``tests/txt`` is collected, so it pre-imports
the ``txt.tools`` package with ``server.mcp`` temporarily swapped for a
throwaway ``MCPServer`` instance -- every ``@mcp.tool()`` decorator of the
seven tool modules binds the throwaway instead of the shared singleton, and
any later import of a ``biz.dfch.specmgr.txt`` sub-package (the model tests'
``import biz.dfch.specmgr.txt.models.v1``) finds ``txt.tools`` already in
``sys.modules`` and re-runs no decorator. The swap is restored immediately
(``try``/``finally``), so the real singleton -- and every test that imports
``biz.dfch.specmgr.server`` -- sees the unchanged 115-tool surface. The
imported tool functions remain plain callables for the tests (the mcp SDK's
``tool()`` decorator registers and returns the function unchanged), exactly
as ``tests/vcr/tools/`` calls its own tools.

Phase 120 (resources/prompts) will extend this same pre-import under the
swap to ``txt.resources``/``txt.prompts`` when those sub-packages first
register ``@mcp.resource()``/``@mcp.prompt()`` decorators -- the
``specmgr://txt/*`` URIs and the two prompts would otherwise inflate the
pinned resource/prompt totals the same way.

**Phase 160 removal mandate.** Once Phase 160 registers ``txt`` on
``server.py``'s own bottom-of-file domain-import line, **THIS ENTIRE FILE
MUST BE DELETED** in that same phase. The throwaway pre-import would then be
not just unnecessary but actively wrong: in every xdist worker the top-level
``tests/test_*.py`` modules (which import ``biz.dfch.specmgr.server``) are
collected before the ``tests/txt/`` subdirectory, so ``txt.tools`` is
already in ``sys.modules`` -- correctly bound to the REAL singleton -- by
the time this conftest runs, and the pre-import under the throwaway swap
would rebind the tool modules to a dead instance, keeping ``txt``'s seven
tools off the real server surface in whichever workers collected
``tests/txt`` first. The ``sys.modules`` guard assert above is therefore a
*deliberate loud tripwire* for exactly that moment: a collection-time
``AssertionError`` from this file in a Phase 160 run means this file was
not removed -- it is not a runtime bug to debug around. No future phase may
"fix" that assert by weakening it (e.g. relaxing the ``sys.modules`` check)
instead of deleting the file; the only correct resolution is the Phase 160
deletion (the same mandate is recorded in the feature plan's Decisions Made
so the Phase 160 implementer sees it there too).
"""

from __future__ import annotations

import asyncio
import sys

from mcp.server import MCPServer

import biz.dfch.specmgr.server as _server_module

# Guard: this pre-import is only effective before any txt TOOL module has been
# imported (its @mcp.tool() decorators would already have run against the real
# singleton). Nothing outside tests/txt imports the txt package in this phase
# (verified by grep: no src/ module and no other test directory touches
# biz.dfch.specmgr.txt), so a violation here is a collection-ordering or
# future-drift bug, not a runtime state.
assert not any(
    name == "biz.dfch.specmgr.txt.tools" or name.startswith("biz.dfch.specmgr.txt.tools.") for name in sys.modules
), (
    "a biz.dfch.specmgr.txt.tools module was imported before this conftest's throwaway-mcp "
    "pre-import; the @mcp.tool() registration isolation no longer applies"
)

#: The throwaway registration target for the txt tool modules. Kept
#: module-level so the instance (and its tool manager) stays alive for the
#: session; it is never exposed to any test -- tests import the tool functions
#: themselves, which the decorators return unchanged.
_throwaway_mcp = MCPServer()

_real_mcp = _server_module.mcp
_server_module.mcp = _throwaway_mcp
try:
    import biz.dfch.specmgr.txt.tools  # noqa: E402, F401  (registers the seven tools on the throwaway)
finally:
    _server_module.mcp = _real_mcp

# Postcondition: the real singleton is untouched (the pre-import registered
# every tool on the throwaway only).
assert _server_module.mcp is _real_mcp
_expected_tool_names = {
    "create_txt",
    "get_txt",
    "get_txt_example",
    "get_txt_schema",
    "get_txt_template",
    "list_txt",
    "parse_txt",
}
_throwaway_names = {tool.name for tool in asyncio.run(_throwaway_mcp.list_tools())}
assert _throwaway_names == _expected_tool_names, _throwaway_names
_real_names = {tool.name for tool in asyncio.run(_real_mcp.list_tools())}
assert not (_real_names & _expected_tool_names), _real_names & _expected_tool_names
