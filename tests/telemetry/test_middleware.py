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

"""Tests for ``telemetry/middleware.py`` (feat-139-logging-telemetry, Phase 3, Tasks 3.4/3.7).

Exercises the ``SpecmgrTelemetryMiddleware`` directly against a fake
``call_next`` (no live server, no transport): the enablement gate (a pure
pass-through when both features are off -- no correlation ID, no record, no
exception conversion, ACC-008/ACC-001), the ACC-013 method filter (the three
invocation methods observed; ``initialize``/``*/list``/``ping``/
``notifications/*`` unobserved), the per-method identity extraction
(``name`` for tools/prompts, ``uri`` for resources), the per-channel error
behavior (a ``tools/call`` ``isError: true`` result vs. a raised
``MCPError``/``ValidationError``/raw exception), the correlation-ID
attachment (``_meta`` for tool error results, ``error.data`` for JSON-RPC
errors, never a success result), the ``set_status`` status value, and
``server.py``'s Task 3.2 startup append (including its broken-contract
guard).

Covers VCR ``0a1c2f63-9576-4463-bf40-8f771f14fefb``'s acceptance criteria
AC-002 (every invocation logged, not tools only) and AC-004 (correlation ID
on error responses only).

Requires the ``mcp`` extra (the SDK's context/models/dispatcher symbols),
same as ``telemetry/middleware.py`` itself.
"""

import asyncio
import importlib
import inspect
import logging
import os
import sys
import unittest
from unittest import mock

from mcp.server import MCPServer
from mcp.server._otel import OpenTelemetryMiddleware
from mcp.server.context import ServerRequestContext
from mcp.server.request_state import RequestStateBoundary
from mcp.server.runner import modern_error_data
from mcp.shared.exceptions import MCPError
from mcp.shared.jsonrpc_dispatcher import handler_exception_to_error_data
from mcp_types import INTERNAL_ERROR, INVALID_PARAMS, CallToolResult, InputRequiredResult, TextContent
from pydantic import BaseModel, ValidationError

from biz.dfch.specmgr.telemetry.config import (
    ENV_LOG_ENABLED,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_LOG_FORMAT,
    ENV_LOG_LEVEL,
    ENV_OTEL_ENABLED,
    ENV_OTEL_ENDPOINT,
    ENV_OTEL_EXPORTER,
    TelemetryConfig,
)
from biz.dfch.specmgr.telemetry.middleware import (
    INTERNAL_ERROR_MESSAGE,
    INVALID_PARAMS_MESSAGE,
    SpecmgrTelemetryMiddleware,
    middleware_contract_compatible,
    new_correlation_id,
)

#: All eight telemetry env vars, removed from the env by the server
#: re-import tests so they pin exactly the environment they assert on.
_ALL_TELEMETRY_ENV_VARS = (
    ENV_LOG_ENABLED,
    ENV_LOG_LEVEL,
    ENV_LOG_FORMAT,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_OTEL_ENABLED,
    ENV_OTEL_EXPORTER,
    ENV_OTEL_ENDPOINT,
)

#: The protocol version every test context carries (the middleware never reads it).
_PROTOCOL_VERSION = "2025-03-26"

#: A sentinel session: the middleware must never touch ``ctx.session``.
_SESSION = object()


def _config(**overrides: object) -> TelemetryConfig:
    """Build a default (disabled) ``TelemetryConfig`` with the given overrides applied."""
    base: dict[str, object] = {
        "log_enabled": False,
        "log_level": "INFO",
        "log_format": "rich",
        "log_file_enabled": False,
        "log_file_path": None,
        "otel_enabled": False,
        "otel_exporter": "console",
        "otel_endpoint": None,
    }
    base.update(overrides)
    return TelemetryConfig(**base)


def _make_ctx(method: str, params: dict[str, object] | None = None, request_id: int | None = 1) -> ServerRequestContext:
    """Build a real ``ServerRequestContext`` for the given method/params."""
    result = ServerRequestContext(
        session=_SESSION,
        lifespan_context={},
        protocol_version=_PROTOCOL_VERSION,
        method=method,
        params=params,
        request_id=request_id,
    )
    return result


def _returns(value: object):
    """Build a fake ``call_next`` returning ``value`` for any context."""

    async def call_next(context: ServerRequestContext) -> object:
        return value

    return call_next


def _raises(exc: BaseException):
    """Build a fake ``call_next`` raising ``exc`` for any context."""

    async def call_next(context: ServerRequestContext) -> object:
        raise exc

    return call_next


def _invoke(sut: SpecmgrTelemetryMiddleware, ctx: ServerRequestContext, call_next) -> object:
    """Run one middleware invocation in a fresh event loop."""
    result = asyncio.run(sut(ctx, call_next))
    return result


class _Capture(logging.Handler):
    """A ``logging.Handler`` that keeps every record it receives."""

    def __init__(self) -> None:
        """Initialize the capture with an empty record list."""
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Keep the record."""
        self.records.append(record)


class _MiddlewareTestCase(unittest.TestCase):
    """Save/restore the root logger and capture the middleware's own logger."""

    def setUp(self) -> None:
        self.root = logging.getLogger()
        self.saved_root_handlers = list(self.root.handlers)
        self.saved_root_level = self.root.level
        # Detach (without closing) whatever handlers exist so SDK-side
        # incidental logging (e.g. modern_error_data's logger.exception)
        # cannot leak into the test output; tearDown restores the set.
        self.root.handlers.clear()
        self._logger = logging.getLogger("biz.dfch.specmgr.telemetry")
        self._capture = _Capture()
        self._saved_logger_level = self._logger.level
        self._saved_logger_propagate = self._logger.propagate
        self._logger.addHandler(self._capture)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

    def tearDown(self) -> None:
        for handler in list(self.root.handlers):
            if handler not in self.saved_root_handlers:
                self.root.removeHandler(handler)
                handler.close()
        self.root.handlers = self.saved_root_handlers
        self.root.level = self.saved_root_level
        self._logger.removeHandler(self._capture)
        self._logger.setLevel(self._saved_logger_level)
        self._logger.propagate = self._saved_logger_propagate

    @property
    def records(self) -> list[logging.LogRecord]:
        """The records the middleware's logger emitted during the test."""
        result = self._capture.records
        return result


class TestEnablementGate(_MiddlewareTestCase):
    """The middleware is a pure pass-through when both features are off (Task 3.4)."""

    def test_both_off_passes_a_raw_exception_through_unconverted(self):
        sut = SpecmgrTelemetryMiddleware(_config())
        ctx = _make_ctx("resources/read", {"uri": "specmgr://req/schema"})
        original = RuntimeError("boom")

        with self.assertRaises(RuntimeError) as cm:
            _invoke(sut, ctx, _raises(original))

        self.assertIs(cm.exception, original)
        self.assertEqual(self.records, [])

    def test_both_off_passes_a_tool_error_result_through_untouched(self):
        sut = SpecmgrTelemetryMiddleware(_config())
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        wire = {"content": [{"type": "text", "text": "boom"}], "isError": True, "resultType": "complete"}

        result = _invoke(sut, ctx, _returns(wire))

        self.assertIs(result, wire)
        self.assertNotIn("_meta", wire)
        self.assertEqual(self.records, [])

    def test_both_off_passes_a_non_invocation_method_through(self):
        sut = SpecmgrTelemetryMiddleware(_config())
        ctx = _make_ctx("ping", {})
        sentinel = {"pong": True}

        result = _invoke(sut, ctx, _returns(sentinel))

        self.assertIs(result, sentinel)
        self.assertEqual(self.records, [])

    def test_logging_only_engages_the_observability_path(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        self.assertTrue(sut.enabled)
        _invoke(sut, ctx, _returns({"content": [], "resultType": "complete"}))

        self.assertEqual(
            [record.getMessage() for record in self.records], ["tool get_req start", "tool get_req completed"]
        )

    def test_otel_only_engages_the_observability_path(self):
        sut = SpecmgrTelemetryMiddleware(_config(otel_enabled=True))
        ctx = _make_ctx("prompts/get", {"name": "create_req"})

        self.assertTrue(sut.enabled)
        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(
            [record.getMessage() for record in self.records], ["prompt create_req start", "prompt create_req completed"]
        )


class TestMethodFilter(_MiddlewareTestCase):
    """The ACC-013 method-name filter: only the three invocations are observed (Task 3.7)."""

    _NON_INVOCATION_CASES = (
        (
            "initialize",
            {"protocolVersion": _PROTOCOL_VERSION, "capabilities": {}, "clientInfo": {"name": "c", "version": "1"}},
            1,
        ),
        ("tools/list", {}, 2),
        ("resources/list", {}, 3),
        ("prompts/list", {}, 4),
        ("ping", {}, 5),
        ("notifications/cancelled", {"requestId": 1, "reason": "canceled"}, None),
    )

    def test_non_invocation_methods_produce_no_record_and_no_attachment(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))

        for method, params, request_id in self._NON_INVOCATION_CASES:
            self.records.clear()
            ctx = _make_ctx(method, params, request_id=request_id)
            sentinel = {"method": method}

            result = _invoke(sut, ctx, _returns(sentinel))

            self.assertIs(result, sentinel, method)
            self.assertNotIn("_meta", sentinel, method)
            self.assertEqual(self.records, [], method)

    def test_a_raising_non_invocation_method_passes_the_exception_through_unconverted(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/list", {})
        original = RuntimeError("boom")

        with self.assertRaises(RuntimeError) as cm:
            _invoke(sut, ctx, _raises(original))

        self.assertIs(cm.exception, original)
        self.assertEqual(self.records, [])

    def test_the_three_invocation_methods_produce_start_and_completion_records(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        cases = (
            ("tools/call", {"name": "get_req", "arguments": {"id": "x"}}, "tool", "get_req"),
            ("resources/read", {"uri": "specmgr://req/schema"}, "resource", "specmgr://req/schema"),
            ("prompts/get", {"name": "create_req"}, "prompt", "create_req"),
        )

        for method, params, item_type, item_name in cases:
            self.records.clear()
            ctx = _make_ctx(method, params)

            _invoke(sut, ctx, _returns({"resultType": "complete"}))

            self.assertEqual(len(self.records), 2, method)
            start, completion = self.records
            self.assertEqual(start.getMessage(), f"{item_type} {item_name} start", method)
            self.assertEqual(completion.getMessage(), f"{item_type} {item_name} completed", method)
            for record in self.records:
                self.assertEqual(record.method, method, method)
                self.assertEqual(record.item_type, item_type, method)
                self.assertEqual(record.item_name, item_name, method)
            self.assertEqual(start.correlation_id, completion.correlation_id, method)

    def test_a_notification_produces_no_record_and_returns_none(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("notifications/initialized", {}, request_id=None)

        result = _invoke(sut, ctx, _returns(None))

        self.assertIsNone(result)
        self.assertEqual(self.records, [])


class TestIdentityExtraction(_MiddlewareTestCase):
    """The per-method identity key: ``name`` for tools/prompts, ``uri`` for resources (Task 3.7)."""

    def test_tool_call_identity_comes_from_the_name_param(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "uri": "must-not-be-used", "arguments": {"id": "x"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(self.records[0].item_name, "get_req")
        self.assertEqual(self.records[0].item_type, "tool")

    def test_prompt_get_identity_comes_from_the_name_param(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("prompts/get", {"name": "create_req", "uri": "must-not-be-used"})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(self.records[0].item_name, "create_req")
        self.assertEqual(self.records[0].item_type, "prompt")

    def test_resource_read_identity_comes_from_the_uri_param(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("resources/read", {"uri": "specmgr://req/schema"})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        self.assertEqual(self.records[0].item_name, "specmgr://req/schema")
        self.assertEqual(self.records[0].item_type, "resource")

    def test_resource_read_does_not_fall_back_to_a_name_key(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("resources/read", {"name": "not-a-uri"})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        self.assertFalse(hasattr(self.records[0], "item_name"))
        self.assertNotIn("not-a-uri", self.records[0].getMessage())

    def test_missing_params_still_log_the_record_without_an_item_name(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", None)

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        record = self.records[0]
        self.assertFalse(hasattr(record, "item_name"))
        self.assertEqual(record.getMessage(), "tool start")
        self.assertRegex(record.correlation_id, r"^[0-9a-f]{32}$")


class TestToolErrorChannel(_MiddlewareTestCase):
    """The tools/call error result: ``isError: true`` detected post-call_next, channel (a)."""

    def test_an_is_error_dict_result_is_logged_and_gets_the_correlation_id_in__meta(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        wire = {"content": [{"type": "text", "text": "boom"}], "isError": True, "resultType": "complete"}

        result = _invoke(sut, ctx, _returns(wire))

        self.assertIs(result, wire)
        start, error = self.records
        self.assertEqual(start.getMessage(), "tool get_req start")
        self.assertEqual(error.levelno, logging.ERROR)
        self.assertEqual(error.getMessage(), "tool get_req failed")
        self.assertEqual(error.exception, {"type": "tool_error", "message": "boom"})
        self.assertNotIn("traceback", error.exception)
        self.assertEqual(wire["_meta"], {"correlationId": error.correlation_id})
        self.assertEqual(wire["_meta"]["correlationId"], start.correlation_id)

    def test_an_is_error_dict_result_preserves_a_preexisting__meta(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        preexisting = {"io.modelcontextprotocol/serverInfo": {"name": "specmgr"}}
        wire = {"_meta": preexisting, "content": [{"type": "text", "text": "boom"}], "isError": True}

        result = _invoke(sut, ctx, _returns(wire))

        self.assertEqual(result["_meta"]["io.modelcontextprotocol/serverInfo"], {"name": "specmgr"})
        self.assertEqual(result["_meta"]["correlationId"], self.records[1].correlation_id)

    def test_an_is_error_call_tool_result_model_is_logged_and_annotated(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        model = CallToolResult(content=[TextContent(type="text", text="boom")], is_error=True, meta={"pre": 1})

        result = _invoke(sut, ctx, _returns(model))

        self.assertIs(result, model)
        self.assertEqual(model.meta, {"pre": 1, "correlationId": self.records[1].correlation_id})
        self.assertEqual(self.records[1].exception, {"type": "tool_error", "message": "boom"})

    def test_an_is_error_model_without_text_content_logs_an_empty_message(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        model = CallToolResult(content=[], is_error=True)

        _invoke(sut, ctx, _returns(model))

        self.assertEqual(self.records[1].exception, {"type": "tool_error", "message": ""})

    def test_an_is_error_dict_result_with_non_list_content_logs_an_empty_message(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "bad"}})
        wire = {"content": "not-a-list", "isError": True}

        result = _invoke(sut, ctx, _returns(wire))

        self.assertIs(result, wire)
        self.assertEqual(self.records[1].exception, {"type": "tool_error", "message": ""})

    def test_a_non_error_dict_result_never_gets_the_correlation_id(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})
        wire = {
            "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "specmgr"}},
            "content": [{"type": "text", "text": "ok"}],
            "resultType": "complete",
        }

        result = _invoke(sut, ctx, _returns(wire))

        self.assertIs(result, wire)
        self.assertNotIn("correlationId", wire["_meta"])
        self.assertEqual([record.levelno for record in self.records], [logging.INFO, logging.INFO])

    def test_a_non_error_model_result_never_gets_the_correlation_id(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})
        model = CallToolResult(content=[TextContent(type="text", text="ok")], meta={"pre": 1})

        result = _invoke(sut, ctx, _returns(model))

        self.assertIs(result, model)
        self.assertEqual(model.meta, {"pre": 1})

    def test_an_input_required_result_is_a_success_never_an_error(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})
        model = InputRequiredResult(request_state="opaque")
        wire = {"resultType": "input_required", "requestState": "opaque"}

        first = _invoke(sut, ctx, _returns(model))
        self.assertIs(first, model)
        self.assertIsNone(model.meta)
        self.records.clear()
        second = _invoke(sut, ctx, _returns(wire))
        self.assertIs(second, wire)
        self.assertNotIn("_meta", wire)
        self.assertEqual(
            [record.getMessage() for record in self.records], ["tool get_req start", "tool get_req completed"]
        )


class TestMcpErrorChannel(_MiddlewareTestCase):
    """The raised-MCPError channel (b): the ID is merged into ``error.data``."""

    def test_a_mcp_error_gets_the_correlation_id_merged_into_its_data_preserving_the_uri(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("resources/read", {"uri": "specmgr://nope"})
        error = MCPError(code=INVALID_PARAMS, message="not found", data={"uri": "specmgr://nope"})

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(error))

        self.assertIs(cm.exception, error)
        self.assertEqual(error.error.data, {"uri": "specmgr://nope", "correlationId": self.records[1].correlation_id})
        self.assertEqual(error.error.code, INVALID_PARAMS)
        self.assertEqual(error.error.message, "not found")
        self.assertEqual(self.records[1].exception["type"], "MCPError")
        self.assertEqual(self.records[1].exception["message"], "not found")
        self.assertIn("Traceback", self.records[1].exception["traceback"])

    def test_a_mcp_error_with_no_data_gets_a_fresh_data_mapping(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("resources/read", {"uri": "specmgr://req/schema"})
        error = MCPError(code=INTERNAL_ERROR, message="oops")

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(error))

        self.assertIs(cm.exception, error)
        self.assertEqual(error.error.data, {"correlationId": self.records[1].correlation_id})

    def test_a_mcp_error_on_a_tool_call_is_handled_by_the_same_channel(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "delete", "arguments": {"id": "x", "type": "req"}})
        error = MCPError(code=INTERNAL_ERROR, message="nope")

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(error))

        self.assertIs(cm.exception, error)
        self.assertEqual(error.error.data, {"correlationId": self.records[1].correlation_id})
        self.assertEqual(self.records[1].getMessage(), "tool delete failed")


class TestRawExceptionChannel(_MiddlewareTestCase):
    """The raised-raw-exception channel (c): converted to the dispatcher's wire-identical error."""

    def test_a_raw_exception_is_converted_to_the_dispatcher_internal_error_wire_identically(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("resources/read", {"uri": "specmgr://req/schema"})
        original = RuntimeError("boom")

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(original))

        converted = cm.exception
        expected = modern_error_data(original)
        self.assertEqual(converted.error.code, expected.code)
        self.assertEqual(converted.error.message, expected.message)
        self.assertEqual(converted.error.code, INTERNAL_ERROR)
        self.assertEqual(converted.error.message, INTERNAL_ERROR_MESSAGE)
        self.assertEqual(converted.error.data, {"correlationId": self.records[1].correlation_id})
        self.assertIs(converted.__cause__, original)
        self.assertEqual(self.records[1].exception["type"], "RuntimeError")
        self.assertEqual(self.records[1].exception["message"], "boom")
        self.assertIn("RuntimeError: boom", self.records[1].exception["traceback"])

    def test_a_raw_exception_on_prompts_get_is_converted_the_same_way(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("prompts/get", {"name": "create_req"})
        original = ValueError("nope")

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(original))

        self.assertEqual(cm.exception.error.code, INTERNAL_ERROR)
        self.assertEqual(cm.exception.error.message, INTERNAL_ERROR_MESSAGE)
        self.assertEqual(cm.exception.error.data, {"correlationId": self.records[1].correlation_id})
        self.assertEqual(self.records[1].getMessage(), "prompt create_req failed")

    def test_a_validation_error_is_converted_to_the_dispatcher_invalid_params_wire_identically(self):
        class _Params(BaseModel):
            name: str

        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("prompts/get", {"name": 3})
        with self.assertRaises(ValidationError) as validation_cm:
            _Params.model_validate({"name": 3})
        original = validation_cm.exception

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(original))

        converted = cm.exception
        expected = handler_exception_to_error_data(original)
        self.assertEqual(converted.error.code, expected.code)
        self.assertEqual(converted.error.message, expected.message)
        self.assertEqual(converted.error.code, INVALID_PARAMS)
        self.assertEqual(converted.error.message, INVALID_PARAMS_MESSAGE)
        self.assertEqual(converted.error.data, {"correlationId": self.records[1].correlation_id})
        self.assertIs(converted.__cause__, original)
        self.assertEqual(self.records[1].exception["type"], "ValidationError")


class TestLogRecordShape(_MiddlewareTestCase):
    """The pinned record shape: extras only, id/type-only messages, set_status's status."""

    def test_start_and_completion_records_share_the_uuid4_correlation_id_in_phase_3(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        start, completion = self.records
        self.assertEqual(start.correlation_id, completion.correlation_id)
        self.assertRegex(start.correlation_id, r"^[0-9a-f]{32}$")

    def test_completion_and_error_records_carry_a_numeric_duration_ms(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))
        self.assertIsInstance(self.records[1].duration_ms, (int, float))
        self.assertGreaterEqual(self.records[1].duration_ms, 0.0)
        self.records.clear()
        _invoke(sut, ctx, _returns({"content": [{"type": "text", "text": "boom"}], "isError": True}))
        self.assertIsInstance(self.records[1].duration_ms, (int, float))
        self.assertGreaterEqual(self.records[1].duration_ms, 0.0)

    def test_the_start_record_carries_no_duration_ms(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        self.assertFalse(hasattr(self.records[0], "duration_ms"))

    def test_error_records_carry_nothing_but_the_pinned_fields(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        _invoke(sut, ctx, _returns({"content": [{"type": "text", "text": "boom"}], "isError": True}))

        error = self.records[1]
        for absent in ("item_name",):
            self.assertTrue(hasattr(error, absent))
        self.assertEqual(getattr(error, "domain", "absent"), "absent")

    def test_a_set_status_call_records_the_new_status_value(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx(
            "tools/call",
            {
                "name": "set_status",
                "arguments": {"id": "0f6f3c8e-0000-4000-8000-000000000000", "type": "req", "status": "accepted"},
            },
        )

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        for record in self.records:
            self.assertEqual(record.status, "accepted")
            self.assertNotIn("accepted", record.getMessage())
            self.assertEqual(record.item_name, "set_status")

    def test_a_set_status_call_without_a_status_argument_carries_no_status_extra(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "set_status", "arguments": {"id": "x", "type": "req"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        for record in self.records:
            self.assertFalse(hasattr(record, "status"))

    def test_a_set_status_call_without_an_arguments_mapping_carries_no_status_extra(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "set_status"})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        for record in self.records:
            self.assertFalse(hasattr(record, "status"))
            self.assertEqual(record.item_name, "set_status")

    def test_other_tool_calls_carry_no_status_extra(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x", "status": "accepted"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        for record in self.records:
            self.assertFalse(hasattr(record, "status"))

    def test_a_prompt_invocation_with_a_status_argument_carries_no_status_extra(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("prompts/get", {"name": "create_req", "arguments": {"status": "accepted"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        for record in self.records:
            self.assertFalse(hasattr(record, "status"))

    def test_record_messages_carry_id_and_type_only(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x", "content": "the secret body"}})

        _invoke(sut, ctx, _returns({"resultType": "complete"}))

        for record in self.records:
            self.assertNotIn("the secret body", record.getMessage())
            self.assertNotIn("the secret body", str(vars(record)))


class TestCorrelationIdHelper(_MiddlewareTestCase):
    """The shared correlation-ID helper (span branch + uuid4 fallback)."""

    def test_without_an_active_span_the_helper_returns_a_fresh_uuid4_hex(self):
        first = new_correlation_id()
        second = new_correlation_id()

        self.assertRegex(first, r"^[0-9a-f]{32}$")
        self.assertNotEqual(first, second)

    def test_with_an_active_recording_span_the_helper_returns_the_trace_id_hex(self):
        from opentelemetry import trace as otel_trace
        from opentelemetry.sdk.trace import TracerProvider

        previous = otel_trace.get_tracer_provider()
        provider = TracerProvider()
        otel_trace.set_tracer_provider(provider)
        try:
            tracer = otel_trace.get_tracer("test")
            with tracer.start_as_current_span("span") as span:
                result = new_correlation_id()
        finally:
            provider.shutdown()
            otel_trace.set_tracer_provider(previous)

        self.assertEqual(result, format(span.get_span_context().trace_id, "032x"))


class TestServerWiring(_MiddlewareTestCase):
    """Task 3.2: server.py appends the middleware at module scope, guarded."""

    def _fresh_import_server(self, env: dict[str, str]) -> object:
        clean = {name: value for name, value in os.environ.items() if name not in _ALL_TELEMETRY_ENV_VARS}
        clean.update(env)
        saved = sys.modules.pop("biz.dfch.specmgr.server", None)
        try:
            with mock.patch.dict(os.environ, clean, clear=True):
                module = importlib.import_module("biz.dfch.specmgr.server")
            return module
        finally:
            if saved is not None:
                sys.modules["biz.dfch.specmgr.server"] = saved

    def test_fresh_import_appends_the_middleware_innermost(self):
        module = self._fresh_import_server({ENV_LOG_ENABLED: "true"})
        chain = module.mcp.middleware

        self.assertEqual(len(chain), 3)
        self.assertIsInstance(chain[0], OpenTelemetryMiddleware)
        self.assertIsInstance(chain[1], RequestStateBoundary)
        self.assertIsInstance(chain[2], SpecmgrTelemetryMiddleware)
        self.assertTrue(chain[2].enabled)

    def test_fresh_import_with_the_default_config_appends_a_disabled_middleware(self):
        module = self._fresh_import_server({})
        chain = module.mcp.middleware

        self.assertIsInstance(chain[-1], SpecmgrTelemetryMiddleware)
        self.assertFalse(chain[-1].enabled)

    def test_a_broken_middleware_contract_logs_one_warning_and_keeps_starting(self):
        def _broken_middleware(_inner: object) -> None:
            raise AttributeError("the Server.middleware contract is incompatible")

        with mock.patch.object(MCPServer, "middleware", new=property(_broken_middleware)):
            module = self._fresh_import_server({ENV_LOG_ENABLED: "true"})

        lowlevel_chain = module.mcp._lowlevel_server.middleware
        self.assertFalse(any(isinstance(entry, SpecmgrTelemetryMiddleware) for entry in lowlevel_chain))
        warnings = [record for record in self.records if record.levelno == logging.WARNING]
        self.assertEqual(len(warnings), 1)
        self.assertIn("could not append the specmgr telemetry middleware", warnings[0].getMessage())
        self.assertEqual(len(self.records), 1)

    def test_an_incompatible_sdk_contract_fails_open_at_startup_with_one_warning(self):
        # Task 4.4(b): simulate a future SDK whose ``ServerMiddleware.__call__``
        # contract changed (a renamed parameter) and assert the Task 4.3
        # fail-open policy engages through ``server.py``'s real startup path:
        # one warning, no middleware appended, the server still constructed
        # and operating.
        from mcp.server.context import ServerMiddleware

        async def _incompatible(self: object, context: object) -> object:
            return None

        with mock.patch.object(ServerMiddleware, "__call__", new=_incompatible):
            module = self._fresh_import_server({ENV_LOG_ENABLED: "true"})

        self.assertIsInstance(module.mcp, MCPServer)
        lowlevel_chain = module.mcp._lowlevel_server.middleware
        self.assertFalse(any(isinstance(entry, SpecmgrTelemetryMiddleware) for entry in lowlevel_chain))
        warnings = [record for record in self.records if record.levelno == logging.WARNING]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Server.middleware contract is incompatible", warnings[0].getMessage())
        self.assertEqual(len(self.records), 1)


class TestMiddlewareContractCanary(_MiddlewareTestCase):
    """Task 4.4(a): pin the installed SDK's provisional ``Server.middleware`` contract.

    A future ``mcp`` upgrade that changes the ``middleware`` list type or
    the ``ServerMiddleware.__call__`` signature trips these canaries in CI
    before the runtime fail-open policy ever needs to engage (the ADR's
    flagged risk).
    """

    def test_the_installed_sdk_middleware_chain_is_a_list(self):
        server = MCPServer(name="canary", instructions="canary")

        self.assertIs(type(server.middleware), list)

    def test_the_installed_sdk_servermiddleware_call_signature_is_the_pinned_shape(self):
        from mcp.server.context import ServerMiddleware

        self.assertTrue(inspect.iscoroutinefunction(ServerMiddleware.__call__))
        parameters = list(inspect.signature(ServerMiddleware.__call__).parameters.values())
        positional = [
            parameter.name
            for parameter in parameters
            if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]

        self.assertEqual(positional, ["self", "ctx", "call_next"])

    def test_the_contract_check_passes_on_the_installed_sdk(self):
        server = MCPServer(name="canary", instructions="canary")

        self.assertTrue(middleware_contract_compatible(server))

    def test_the_contract_check_rejects_a_non_list_chain(self):
        class _TupleChain:
            middleware = (object(),)

        self.assertFalse(middleware_contract_compatible(_TupleChain()))

    def test_the_contract_check_rejects_a_renamed_protocol_param(self):
        from mcp.server.context import ServerMiddleware

        server = MCPServer(name="canary", instructions="canary")

        async def _renamed(self: object, context: object) -> object:
            return None

        with mock.patch.object(ServerMiddleware, "__call__", new=_renamed):
            self.assertFalse(middleware_contract_compatible(server))

    def test_the_contract_check_rejects_a_sync_protocol(self):
        from mcp.server.context import ServerMiddleware

        server = MCPServer(name="canary", instructions="canary")

        def _sync(self: object, ctx: object, call_next: object) -> object:
            return None

        with mock.patch.object(ServerMiddleware, "__call__", new=_sync):
            self.assertFalse(middleware_contract_compatible(server))


class TestCallTimeFailOpen(_MiddlewareTestCase):
    """Task 4.3's call-time half: a first contract violation at request time fails open once (ACC-010)."""

    def _fail_open_count(self) -> int:
        return len(
            [
                record
                for record in self.records
                if "incompatible with the specmgr telemetry middleware at call time" in record.getMessage()
            ]
        )

    def test_a_broken_ctx_method_at_call_time_fails_open_with_one_warning_and_completes_the_request(self):
        class _BrokenMethodCtx:
            """A ctx double whose ``method`` read raises (a future SDK contract change)."""

            params = None

            @property
            def method(self) -> str:
                raise AttributeError("the method attribute is gone")

        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        sentinel = {"result": True}
        ctx = _BrokenMethodCtx()

        first = _invoke(sut, ctx, _returns(sentinel))
        second = _invoke(sut, ctx, _returns(sentinel))

        self.assertIs(first, sentinel)
        self.assertIs(second, sentinel)
        self.assertEqual(self._fail_open_count(), 1)
        self.assertFalse(sut.enabled)

    def test_a_broken_ctx_params_at_call_time_fails_open_with_one_warning(self):
        class _BrokenParamsCtx:
            method = "tools/call"

            @property
            def params(self) -> object:
                raise AttributeError("the params attribute is gone")

        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        sentinel = {"result": True}

        result = _invoke(sut, _BrokenParamsCtx(), _returns(sentinel))

        self.assertIs(result, sentinel)
        self.assertEqual(self._fail_open_count(), 1)
        self.assertFalse(sut.enabled)
        # No start/completion records: observability is off.
        self.assertEqual([record for record in self.records if record.levelno in (logging.INFO,)], [])

    def test_a_broken_result_shape_after_call_next_returns_the_result_and_fails_open(self):
        class _BrokenResult(dict):
            def get(self, *args: object, **kwargs: object) -> object:
                raise TypeError("the result contract changed")

        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})
        broken = _BrokenResult()

        result = _invoke(sut, ctx, _returns(broken))

        self.assertIs(result, broken)
        self.assertEqual(self._fail_open_count(), 1)
        self.assertFalse(sut.enabled)

    def test_an_app_exception_is_not_misread_as_a_contract_violation(self):
        sut = SpecmgrTelemetryMiddleware(_config(log_enabled=True))
        ctx = _make_ctx("tools/call", {"name": "get_req", "arguments": {"id": "x"}})

        with self.assertRaises(MCPError) as cm:
            _invoke(sut, ctx, _raises(RuntimeError("boom")))

        self.assertEqual(cm.exception.error.code, INTERNAL_ERROR)
        self.assertEqual(self._fail_open_count(), 0)
        self.assertTrue(sut.enabled)
        self.assertEqual(
            [record.getMessage() for record in self.records], ["tool get_req start", "tool get_req failed"]
        )


if __name__ == "__main__":
    unittest.main()
