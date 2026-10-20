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

"""Wire-level regression tests for the MCP tool error contract
(feat-221-mcp-220-error-contract, Phase 100, REQ-004 / ACC-002).

Since ``mcp`` v2.1.0 (upstream #3314), a tool handler's raised exception is
wrapped by the SDK in ``UnexpectedToolError("Error executing tool <name>")``
before it reaches the client: the handler's own message text is swallowed.
``server.SpecMgrServer`` (the ``mcp`` singleton's class) restores the 2.0.0
caller-visible error text at the single ``call_tool`` seam by re-raising
``UnexpectedToolError.__cause__`` (the original exception); the SDK's own
``_handle_call_tool`` catch then stringifies that original exception into the
``is_error=True`` ``CallToolResult`` the client receives -- the 2.0.0 wire
shape minus the ``Error executing tool <name>: `` prefix (deliberately not
re-prepended).

These tests pin that restored contract at the wire level, in-process and
transport-free (no stdio/sse/http): each scenario drives a real
``mcp.client.session.ClientSession`` over anyio memory streams against the
live ``mcp`` singleton (the SDK's own test-suite pattern), so the assertion
covers the full ``tools/call`` path -- request framing, the registered
handler, the ``SpecMgrServer.call_tool`` override, and the SDK's
``_handle_call_tool`` result construction. The public ``call_tool`` itself
raises the original exception post-shim and never returns an ``is_error``
result; the ``is_error`` result is produced one layer up, which is exactly
the boundary the session exercises.

The three pinned cases (all over the ``req`` domain, the canonical
raise-based usage-error family):

(a) a malformed id (``get_req`` with ``id="not-a-uuid"``) reaches the client
    as ``is_error=True`` with the content text equal to the original
    ``_path_safety`` ``ValueError`` message -- NOT the bare
    ``Error executing tool get_req`` an unpatched ``mcp`` >= 2.1.0 would
    send;
(b) a well-formed-but-absent id reaches the client as ``is_error=True`` with
    the content text equal to the domain's own ``ReqNotFoundError`` message;
(c) a healthy call reaches the client with the success shape unchanged
    (``is_error`` false, the payload identical to the direct Python call's
    return value).

This test -- not the locked ``mcp`` version number -- is the behavioral
guard for future 2.x bumps (the plan's Design Notes, "Version drift"):
``uv.lock`` may resolve ``mcp`` > 2.2.0, and any 2.x release that changes
the exception-to-``CallToolResult`` conversion again must land here as a
failure, not as a silently stripped error message.
"""

from __future__ import annotations

import asyncio
import json
import logging
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.client.session import ClientSession
from mcp.types import CallToolResult, TextContent

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
from biz.dfch.specmgr.req.tools.get_req import get_req
from biz.dfch.specmgr.req.tools.get_req_example import get_req_example
from biz.dfch.specmgr.req.tools.list_req import list_req
from biz.dfch.specmgr.server import SpecMgrServer, mcp

#: A malformed id: fails the ``_path_safety`` canonical-UUID check for every
#: UUID domain (the case whose 2.1.0+ unpatched wire text is the bare
#: ``Error executing tool <name>``).
_MALFORMED_ID = "not-a-uuid"

#: A well-formed but absent canonical UUID (reaches the domain's own
#: not-found error past the id-validation guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: Per-scenario wall-clock guard (a healthy scenario completes in milliseconds;
#: this only bounds a regression that deadlocks the in-process session).
_SCENARIO_TIMEOUT_SECONDS = 30

#: The SDK's own request handler logger (``mcp.server.mcpserver.server``):
#: its ``_handle_call_tool`` catch logs the re-raised original exception with
#: ``logger.exception`` (logging is retained by design -- the shim must not
#: silence it), which would otherwise print a full rich traceback into the
#: test output for every error scenario.
_SDK_SERVER_LOGGER = logging.getLogger("mcp.server.mcpserver.server")


def _wire_text(result: CallToolResult) -> str:
    """The single ``TextContent``'s text of a wire-level tool result.

    Raises:
        AssertionError: The result carries no content or more than one item,
            or its sole item is not a ``TextContent`` (a shape regression this
            module's assertions depend on).
    """
    assert isinstance(result.content, list) and len(result.content) == 1, result.content
    assert isinstance(result.content[0], TextContent), result.content[0]
    return result.content[0].text


class TestMcpErrorContract(unittest.TestCase):
    """REQ-004: the in-process client session sees the original exception text, not the SDK wrapper."""

    def setUp(self) -> None:
        self.sut = mcp
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        # The server lifespan's startup warmup must stay a no-op in-process:
        # both presence flags set means no warmup thread starts at all.
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {
                    "SPECMGR_FEAT_WARMUP_DISABLED": "1",
                    "SPECMGR_SIMILARITY_DISABLED": "1",
                },
            )
        )
        # Keep the SDK's retained ``logger.exception`` of the re-raised original
        # out of the test output (see ``_SDK_SERVER_LOGGER``).
        self.enterContext(mock.patch.object(_SDK_SERVER_LOGGER, "level", logging.CRITICAL))

    async def _run_server(
        self, read_stream: MemoryObjectReceiveStream[Any], write_stream: MemoryObjectSendStream[Any]
    ) -> None:
        """Serve the live ``mcp`` singleton over in-memory streams (``run_stdio_async``'s in-process twin)."""
        sut = self.sut
        init_options = sut._lowlevel_server.create_initialization_options()
        await sut._lowlevel_server.run(read_stream, write_stream, init_options)

    def _scenario(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Drive one ``tools/call`` for ``name``/``arguments`` over an in-process client session."""
        to_server_send, to_server_receive = anyio.create_memory_object_stream(16)
        from_server_send, from_server_receive = anyio.create_memory_object_stream(16)

        async def run_session() -> CallToolResult:
            async with anyio.create_task_group() as tg:
                tg.start_soon(self._run_server, to_server_receive, from_server_send)
                async with ClientSession(from_server_receive, to_server_send) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)
                    return result

        result = asyncio.run(asyncio.wait_for(run_session(), timeout=_SCENARIO_TIMEOUT_SECONDS))
        return result

    def test_singleton_is_the_spec_mgr_server_subclass(self) -> None:
        """REQ-002: the registered server object is the ``SpecMgrServer`` seam, not a plain ``MCPServer``."""
        self.assertIsInstance(self.sut, SpecMgrServer)
        self.assertEqual(type(self.sut).call_tool.__qualname__, "SpecMgrServer.call_tool")

    def test_malformed_id_wire_carries_original_value_error_message(self) -> None:
        """(a) A malformed id must reach the client as ``is_error=True`` with the original ``ValueError`` text (no ``Error executing tool`` prefix)."""
        with self.assertRaises(ValueError) as direct:
            get_req(_MALFORMED_ID)

        result = self._scenario("get_req", {"id": _MALFORMED_ID})

        self.assertTrue(result.is_error)
        self.assertEqual(_wire_text(result), str(direct.exception))
        self.assertFalse(_wire_text(result).startswith("Error executing tool"))

    def test_absent_id_wire_carries_original_not_found_message(self) -> None:
        """(b) A well-formed-but-absent id must reach the client as ``is_error=True`` with the domain's ``ReqNotFoundError`` text."""
        with self.assertRaises(ReqNotFoundError) as direct:
            get_req(_MISSING_UUID)

        result = self._scenario("get_req", {"id": _MISSING_UUID})

        self.assertTrue(result.is_error)
        self.assertEqual(_wire_text(result), str(direct.exception))
        self.assertFalse(_wire_text(result).startswith("Error executing tool"))

    def test_healthy_call_wire_shape_unchanged(self) -> None:
        """(c) A healthy call must reach the client with ``is_error`` false and the payload identical to the direct Python call's return value."""
        expected_example = get_req_example()
        expected_listing = list_req().model_dump(mode="json")

        example_result = self._scenario("get_req_example", {})
        listing_result = self._scenario("list_req", {})

        self.assertFalse(example_result.is_error)
        self.assertEqual(_wire_text(example_result), expected_example)
        self.assertFalse(listing_result.is_error)
        self.assertEqual(json.loads(_wire_text(listing_result)), expected_listing)


if __name__ == "__main__":
    unittest.main()
