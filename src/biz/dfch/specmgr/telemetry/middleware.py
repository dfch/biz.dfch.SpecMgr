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

"""The specmgr ``ServerMiddleware``: correlation IDs and call logging (feat-139-logging-telemetry, Phase 3, Task 3.1).

The single instrumentation point this feature adds to the MCP server: an
``mcp.server.context.ServerMiddleware`` implementation that
``server.py``'s module scope appends to ``mcp.middleware`` (Task 3.2), so it
runs innermost in the SDK's own chain -- inside the SDK's built-in
``OpenTelemetryMiddleware`` (whose request span is therefore already active
by the time this middleware runs) and inside the SDK's request-state
boundary.

Enablement gating (the Design Notes' "Middleware enablement gating" bullet):
when neither ``SPECMGR_LOG_ENABLED`` nor ``SPECMGR_OTEL_ENABLED`` is
``true`` (the default), :meth:`SpecmgrTelemetryMiddleware.__call__` passes
every method -- including the three invocations -- straight to
``call_next(ctx)`` unmodified: no correlation ID, no log record, no
exception conversion, no attachment. The default configuration is therefore
a byte-for-byte no-op over the SDK's own behavior (ACC-001/ACC-008).

Method filter (ACC-013): the ``ServerMiddleware`` chain wraps every inbound
JSON-RPC request and notification (``initialize``, ``tools/list``,
``resources/list``, ``prompts/get``'s sibling ``prompts/list``, ``ping``,
``notifications/*`` included), not only item invocations. This middleware
observes only the three invocation methods -- ``tools/call``,
``resources/read``, and ``prompts/get`` -- and passes every other method
through unobserved.

For an observed invocation it:

- extracts the invoked item's identity from the correct per-method raw
  params key (``ctx.params["name"]`` for ``tools/call``/``prompts/get``,
  ``ctx.params["uri"]`` for ``resources/read`` -- the Design Notes'
  "Per-method target extraction" bullet);
- generates the per-invocation correlation ID via
  :func:`new_correlation_id` (the active span's trace ID when a recording
  span is current -- which Phase 4's ``SPECMGR_OTEL_ENABLED`` makes the
  SDK's built-in middleware true -- else a fresh ``uuid4().hex``; Phase 3
  always takes the ``uuid4()`` branch);
- logs a start record (before ``call_next``) and a completion or error
  record (after), carrying, for a ``set_status`` tool call, the new status
  value (REQ ``bc356fc9-964a-4274-93ec-4627c5aeb2e5``). The record messages
  carry id/type-only identity (no arguments, no body, no paths, no titles);
  the structured fields ride in ``extra=`` and the ``telemetry/logging.py``
  formatters emit only what is present.

Error detection is per-method (the Design Notes' "Per-method error channels"
bullet):

- ``tools/call`` failures arrive as a *result*, not an exception -- the SDK
  converts every non-``MCPError`` tool exception into a
  ``CallToolResult``/wire dict with ``isError: true`` before the middleware
  sees it -- so the middleware inspects the post-``call_next`` result for
  that shape (both the model and the plain dict, per ``HandlerResult``) in
  addition to the exception path.
- ``resources/read``/``prompts/get`` failures (and ``tools/call``'s
  ``MCPError`` passthrough) arrive as raised exceptions: an ``MCPError``
  (kept, with the correlation ID merged into ``e.error.data`` -- channel
  (b)), a pydantic ``ValidationError``, or any other raw exception (both
  converted to the wire-identical ``MCPError`` the dispatcher would
  otherwise produce -- channel (c) -- and re-raised).

Correlation-ID attachment (Task 3.3) happens on error responses only, never
on a successful result: (a) a ``tools/call`` error result gets
``"_meta": {"correlationId": ...}`` merged into it (preserving any
pre-existing ``_meta``), (b) an ``MCPError`` gets the ID merged into
``e.error.data`` (preserving the SDK's own ``uri`` entry where present),
and (c) a converted error carries the ID in its ``data``.

This phase creates and increments no OTel counter/histogram: no
``MeterProvider`` exists until Phase 4, and the metrics are Task 5.2/5.3's
responsibility (the Design Notes' "Phase 3/Phase 5 division of labor"
bullet).

Like ``telemetry/logging.py``, this module imports ``mcp``/``mcp_types``/
``opentelemetry`` symbols and is only imported from ``server.py`` (which
already requires the ``mcp`` extra) and its tests -- it is not
base-library-safe.

The ``ServerMiddleware`` contract is a provisional API (the ADR's flagged
risk). This middleware therefore never asserts on the SDK-provided
``ctx``/``call_next`` inside ``__call__`` -- a future contract change must
degrade (Task 4.3's fail-open policy), not raise on every request; the
input validation the repo convention requires lives in ``__init__``
instead. Task 4.3's policy has two surfaces, one warning per episode via
the ``biz.dfch.specmgr.telemetry`` logger:

- *startup* -- :func:`middleware_contract_compatible` checks the installed
  SDK's ``Server.middleware`` list type and the
  ``ServerMiddleware.__call__`` signature against this middleware's own
  implementation before ``server.py`` appends it; an incompatible
  contract (or an append that raises) logs one warning and the server
  continues operating without call observability, rather than failing to
  start (this upgrades Task 3.2's minimal append guard -- same mechanism,
  not a second, independent one);
- *call time* -- ``__call__`` guards the middleware-contract surfaces
  (the pre-call ``ctx`` reads, the post-call result processing) and, on
  the first ``AttributeError``/``TypeError`` there, logs one warning,
  disables observability for the rest of the process, and still completes
  the request unmodified -- never double-executing ``call_next``.
"""

from __future__ import annotations

import inspect
import logging
import threading
import time
import traceback
import uuid
from collections.abc import Mapping
from typing import Any

from mcp.server.context import CallNext, HandlerResult, ServerMiddleware, ServerRequestContext
from mcp.shared.exceptions import MCPError
from mcp_types import CallToolResult, INTERNAL_ERROR, INVALID_PARAMS
from opentelemetry import trace
from pydantic import ValidationError

from .config import TelemetryConfig

#: The logger this middleware emits its start/completion/error records on
#: (under the ``biz.dfch.specmgr`` namespace; ``server.py``'s Task 3.2 guard
#: uses it for its single startup warning too).
logger = logging.getLogger("biz.dfch.specmgr.telemetry")

# ---------------------------------------------------------------------------
# Method/item-type/params-key constants (comparison values per the repo
# convention; the per-method mapping is the Design Notes' "Per-method target
# extraction" bullet)
# ---------------------------------------------------------------------------

#: The JSON-RPC method that invokes a tool.
METH_TOOLS_CALL = "tools/call"
#: The JSON-RPC method that reads a resource.
METH_RESOURCES_READ = "resources/read"
#: The JSON-RPC method that invokes a prompt.
METH_PROMPTS_GET = "prompts/get"

#: The item type logged/counted for a ``tools/call`` invocation.
ITEM_TYPE_TOOL = "tool"
#: The item type logged/counted for a ``resources/read`` invocation.
ITEM_TYPE_RESOURCE = "resource"
#: The item type logged/counted for a ``prompts/get`` invocation.
ITEM_TYPE_PROMPT = "prompt"

#: The raw params key carrying the tool/prompt name.
PARAMS_KEY_NAME = "name"
#: The raw params key carrying the resource uri.
PARAMS_KEY_URI = "uri"
#: The raw params key carrying a tool call's arguments.
PARAMS_KEY_ARGUMENTS = "arguments"
#: The ``set_status`` tool's argument carrying the new status value.
PARAMS_KEY_STATUS = "status"

#: The tool name whose invocations additionally log the new status value.
SET_STATUS_TOOL = "set_status"

# ---------------------------------------------------------------------------
# Wire-shape keys and the per-channel error values
# ---------------------------------------------------------------------------

#: The ``_meta`` key on a dumped result (``CallToolResult.meta``'s alias).
META_KEY = "_meta"
#: The correlation ID's key inside ``_meta`` and inside a JSON-RPC error's
#: ``data`` (the client-visible error-response field, ACC-008).
CORRELATION_ID_KEY = "correlationId"
#: The camelCase wire key for ``CallToolResult.is_error``.
WIRE_IS_ERROR_KEY = "isError"
#: The result's content-list key (wire and model field share it).
CONTENT_KEY = "content"
#: The content block's type key/field (wire and model share it).
BLOCK_KEY_TYPE = "type"
#: The text content block's text key/field (wire and model share it).
BLOCK_KEY_TEXT = "text"
#: The content-block type value identifying a text block.
BLOCK_TYPE_TEXT = "text"

#: The per-channel error-type signal for a ``tools/call`` ``isError: true``
#: result (the SDK's own value, matching the ``mcp.server._otel`` built-in
#: middleware and Task 5.3's error-type counter).
TOOL_ERROR_TYPE = "tool_error"

#: The JSON-RPC error message the dispatcher's catch-all uses for a raw
#: (non-``MCPError``, non-``ValidationError``) exception (``mcp/server/
#: runner.py``'s ``modern_error_data``) -- channel (c) replicates it
#: wire-identically.
INTERNAL_ERROR_MESSAGE = "Internal server error"
#: The JSON-RPC error message the dispatcher's ladder uses for a pydantic
#: ``ValidationError`` (``mcp/shared/jsonrpc_dispatcher.py``'s
#: ``handler_exception_to_error_data``) -- channel (c) replicates it
#: wire-identically.
INVALID_PARAMS_MESSAGE = "Invalid request parameters"

#: The record phases (the message's trailing word).
_PHASE_START = "start"
_PHASE_COMPLETED = "completed"
_PHASE_FAILED = "failed"

#: The duration's millisecond precision.
_DURATION_MS_PRECISION = 3
#: The hex width of a trace ID (128 bits).
_TRACE_ID_HEX_WIDTH = "032x"

#: Which item type an observed method's invocation is (ACC-013's scope).
_METHOD_ITEM_TYPE = {
    METH_TOOLS_CALL: ITEM_TYPE_TOOL,
    METH_RESOURCES_READ: ITEM_TYPE_RESOURCE,
    METH_PROMPTS_GET: ITEM_TYPE_PROMPT,
}
#: Which raw params key carries the invoked item's identity, per method.
_METHOD_PARAMS_KEY = {
    METH_TOOLS_CALL: PARAMS_KEY_NAME,
    METH_RESOURCES_READ: PARAMS_KEY_URI,
    METH_PROMPTS_GET: PARAMS_KEY_NAME,
}


def new_correlation_id() -> str:
    """Generate the correlation ID for one invocation.

    The shared helper the Design Notes' "Correlation ID exposure" bullet
    pins: when a recording OpenTelemetry span is current (Phase 4's
    ``SPECMGR_OTEL_ENABLED`` makes the SDK's built-in
    ``OpenTelemetryMiddleware`` -- which runs outside this middleware --
    true by the time this helper runs), the correlation ID *is* that span's
    trace ID (hex-formatted), so ACC-003's "the correlation ID matches the
    trace ID of the span" holds by construction; otherwise it is a freshly
    generated ``uuid4().hex``. In Phase 3 no ``TracerProvider`` exists yet,
    so the ``uuid4()`` branch is the one that engages.

    Returns:
        A 32-character lowercase hex string (a trace ID or a UUIDv4).
    """
    span = trace.get_current_span()
    if span.is_recording():
        span_context = span.get_span_context()
        if span_context is not None and span_context.trace_id:
            result = format(span_context.trace_id, _TRACE_ID_HEX_WIDTH)
            return result
    result = uuid.uuid4().hex
    return result


#: The provisional ``ServerMiddleware`` contract this middleware implements:
#: an async ``__call__`` taking exactly the two positional parameters
#: ``(ctx, call_next)`` (besides ``self``). Task 4.4's canary test pins the
#: installed SDK's side of this shape.
_MW_PARAM_CTX = "ctx"
_MW_PARAM_CALL_NEXT = "call_next"
_MIDDLEWARE_CONTRACT_PARAMS = (_MW_PARAM_CTX, _MW_PARAM_CALL_NEXT)


def _callable_contract_params(callable_object: object) -> tuple[str, ...] | None:
    """Return a callable's positional parameter names (besides ``self``), if it fits the contract shape.

    ``None`` when the object is not a coroutine function or its signature
    cannot be inspected (a contract that no longer looks like the pinned
    async two-argument shape).

    Args:
        callable_object: A ``__call__`` implementation to inspect (the
            SDK's ``ServerMiddleware.__call__`` protocol method or this
            middleware's own ``__call__``).

    Returns:
        The positional parameter names (besides ``self``), or ``None``.
    """
    if not inspect.iscoroutinefunction(callable_object):
        return None
    try:
        parameters = list(inspect.signature(callable_object).parameters.values())
    except (TypeError, ValueError):
        return None
    positional = [
        parameter.name
        for parameter in parameters
        if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if not positional or positional[0] != "self":
        return None
    result = tuple(positional[1:])
    return result


def middleware_contract_compatible(server: object) -> bool:
    """Whether the installed SDK's provisional ``Server.middleware`` contract still fits (Task 4.3).

    The startup half of the Task 4.3 fail-open policy, evaluated by
    ``server.py``'s module scope before the middleware is appended. Checks,
    without mutating anything: (1) the server's ``middleware`` chain is a
    ``list`` (the appendable shape this feature relies on), and (2) both
    the SDK's ``ServerMiddleware.__call__`` protocol and this middleware's
    own ``__call__`` are async two-argument callables taking exactly
    ``(ctx, call_next)``. A ``False`` result (or an exception raised while
    checking -- e.g. the ``middleware`` attribute itself is gone) means the
    contract changed underneath us: the caller logs one warning and
    continues operating without call observability, rather than failing to
    start (ACC-010).

    Args:
        server: The constructed ``MCPServer`` whose ``middleware`` chain is
            checked (any object exposing the SDK's ``middleware`` list).

    Returns:
        ``True`` when appending :class:`SpecmgrTelemetryMiddleware` is
        contract-compatible with the installed SDK.
    """
    chain = server.middleware
    if not isinstance(chain, list):
        return False
    if _callable_contract_params(ServerMiddleware.__call__) != _MIDDLEWARE_CONTRACT_PARAMS:
        return False
    result = _callable_contract_params(SpecmgrTelemetryMiddleware.__call__) == _MIDDLEWARE_CONTRACT_PARAMS
    return result


def _is_tool_error_result(result: HandlerResult) -> bool:
    """Whether a post-``call_next`` ``tools/call`` result is an error result.

    A ``tools/call`` failure arrives as a *result*, not an exception (the
    SDK's ``_handle_call_tool`` converts every non-``MCPError`` tool
    exception into an ``isError: true`` result). Both shapes are checked,
    per ``HandlerResult``: the dumped wire dict (the form the dispatcher's
    inner chain actually returns) and the ``CallToolResult`` model. An
    ``InputRequiredResult`` (the second possible ``tools/call`` shape)
    carries no ``isError``/``is_error`` and is therefore a success here.

    Args:
        result: The ``call_next`` return value.

    Returns:
        ``True`` when the result is a failing tool call.
    """
    if isinstance(result, dict):
        return result.get(WIRE_IS_ERROR_KEY) is True
    if isinstance(result, CallToolResult):
        return result.is_error is True
    return False


def _first_text_content(result: object) -> str:
    """Return the first text content block's text from an error result.

    For the ``tools/call`` error record's ``message`` (the SDK's own
    ``str(e)`` of the tool's exception, the ``CallToolResult`` content
    entry). Returns ``""`` when the result carries no text content block.

    Args:
        result: The error result (a wire dict or a ``CallToolResult``).

    Returns:
        The first text content's text, or ``""``.
    """
    content: object
    if isinstance(result, dict):
        content = result.get(CONTENT_KEY)
    elif isinstance(result, CallToolResult):
        content = result.content
    else:
        content = None
    if not isinstance(content, list):
        result_text = ""
        return result_text
    for block in content:
        if isinstance(block, dict):
            block_type: object = block.get(BLOCK_KEY_TYPE)
            block_text: object = block.get(BLOCK_KEY_TEXT)
        else:
            block_type = getattr(block, BLOCK_KEY_TYPE, None)
            block_text = getattr(block, BLOCK_KEY_TEXT, None)
        if block_type == BLOCK_TYPE_TEXT and isinstance(block_text, str):
            result_text = block_text
            return result_text
    result_text = ""
    return result_text


def _raised_exception_field(exc: BaseException) -> dict[str, object]:
    """Build the error record's ``exception`` field from a raised exception.

    Channel (b)/(c) shape (the Design Notes' pin): the exception's
    qualified type name, its ``str()``, and the formatted traceback.

    Args:
        exc: The raised exception (an ``MCPError``, a
            ``ValidationError``, or any raw exception).

    Returns:
        The ``{"type": ..., "message": ..., "traceback": ...}`` mapping.
    """
    result: dict[str, object] = {
        "type": type(exc).__qualname__,
        "message": str(exc),
        "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    }
    return result


def _tool_error_field(result: HandlerResult) -> dict[str, object]:
    """Build the error record's ``exception`` field for a ``tools/call`` error result.

    Channel (a) shape: no exception object exists at the middleware layer
    for a tool error, so the field carries the SDK's own ``tool_error``
    type signal and the error text from the result's content, and no
    ``traceback`` key.

    Args:
        result: The ``isError: true`` result (a wire dict or a
            ``CallToolResult``).

    Returns:
        The ``{"type": "tool_error", "message": ...}`` mapping.
    """
    result_dict: dict[str, object] = {"type": TOOL_ERROR_TYPE, "message": _first_text_content(result)}
    return result_dict


def _attach_correlation_id_to_result(result: HandlerResult, correlation_id: str) -> None:
    """Channel (a): merge the correlation ID into a ``tools/call`` error result's ``_meta``.

    For the wire dict, the ``"_meta"`` key is merged (preserving any
    pre-existing meta, e.g. the dispatcher's ``serverInfo`` stamp); for the
    model, ``CallToolResult.meta`` (which dumps as ``_meta``) is merged
    the same way. Only error results reach this function (channel (a)'s
    callers gate on :func:`_is_tool_error_result`), so a successful result
    never receives the ID.

    Args:
        result: The error result to annotate (mutated in place).
        correlation_id: The invocation's correlation ID.
    """
    if isinstance(result, dict):
        meta = result.get(META_KEY)
        merged = dict(meta) if isinstance(meta, Mapping) else {}
        merged[CORRELATION_ID_KEY] = correlation_id
        result[META_KEY] = merged
    elif isinstance(result, CallToolResult):
        meta = result.meta
        merged = dict(meta) if isinstance(meta, Mapping) else {}
        merged[CORRELATION_ID_KEY] = correlation_id
        result.meta = merged


def _attach_correlation_id_to_mcp_error(error: MCPError, correlation_id: str) -> None:
    """Channel (b): merge the correlation ID into an ``MCPError``'s ``error.data``.

    Preserves the SDK's own ``data`` entries where present (a
    ``resources/read`` failure carries ``data={"uri": ...}``); a ``None``
    data starts a fresh mapping. (A non-mapping data payload cannot hold an
    extra key and is replaced by the correlation-ID mapping -- an
    unobserved shape for the three invocation methods, whose SDK-produced
    ``MCPError``s carry either a ``uri`` mapping or no data at all.)

    Args:
        error: The raised ``MCPError`` (mutated in place and re-raised by
            the caller unchanged otherwise).
        correlation_id: The invocation's correlation ID.
    """
    data = error.error.data
    merged = dict(data) if isinstance(data, Mapping) else {}
    merged[CORRELATION_ID_KEY] = correlation_id
    error.error.data = merged


def _converted_mcp_error(exc: Exception, correlation_id: str) -> MCPError:
    """Channel (c): build the wire-identical ``MCPError`` a raw exception is converted to.

    Replicates the dispatcher's own error mapping (``mcp/server/runner.py``
    ``modern_error_data`` + ``mcp/shared/jsonrpc_dispatcher.py``
    ``handler_exception_to_error_data``), plus the ``data`` carrying the
    correlation ID: a pydantic ``ValidationError`` becomes the ladder's
    ``INVALID_PARAMS``/"Invalid request parameters", any other exception
    the catch-all's ``INTERNAL_ERROR``/"Internal server error". The caller
    raises the result with ``from exc``.

    Args:
        exc: The raised exception being converted.
        correlation_id: The invocation's correlation ID.

    Returns:
        The converted ``MCPError``.
    """
    data = {CORRELATION_ID_KEY: correlation_id}
    if isinstance(exc, ValidationError):
        result = MCPError(code=INVALID_PARAMS, message=INVALID_PARAMS_MESSAGE, data=data)
        return result
    result = MCPError(code=INTERNAL_ERROR, message=INTERNAL_ERROR_MESSAGE, data=data)
    return result


def _duration_ms(start: float) -> float:
    """Return the elapsed milliseconds since a ``time.monotonic()`` mark."""
    result = round((time.monotonic() - start) * 1000.0, _DURATION_MS_PRECISION)
    return result


def _set_status_value(method: str, item_name: str | None, params: Mapping[str, Any] | None) -> str | None:
    """Return the new status value of a ``set_status`` invocation, else ``None``.

    REQ ``bc356fc9-964a-4274-93ec-4627c5aeb2e5``: a ``set_status`` call's
    log records additionally carry the new status value. The value is read
    from the raw params' ``arguments`` mapping (``ctx.params["arguments"][
    "status"]``); anything missing, non-string, or blank returns ``None``
    (the field is simply absent from the records).

    Args:
        method: The invocation's JSON-RPC method.
        item_name: The extracted item identity (``None`` when absent).
        params: The raw, pre-validation params mapping (``None`` allowed).

    Returns:
        The new status value, or ``None``.
    """
    if method != METH_TOOLS_CALL or item_name != SET_STATUS_TOOL or params is None:
        return None
    arguments = params.get(PARAMS_KEY_ARGUMENTS)
    if not isinstance(arguments, Mapping):
        return None
    status = arguments.get(PARAMS_KEY_STATUS)
    if isinstance(status, str) and status.strip():
        result: str | None = status
        return result
    result = None
    return result


class SpecmgrTelemetryMiddleware:
    """The specmgr ``ServerMiddleware``: correlation IDs + start/completion/error logging.

    Appended to ``mcp.middleware`` by ``server.py``'s module scope (Task
    3.2), it is the innermost context-tier middleware: it observes the
    dispatcher's already-serialized wire dict for a success and the raised
    exception for a failure. See the module docstring for the enablement
    gating, the ACC-013 method filter, the per-method identity extraction,
    the three per-channel error behaviors, and the Task 4.3 call-time
    fail-open guard.

    Attributes:
        config: The parsed, validated telemetry configuration the
            middleware was built with (``server.py`` passes its own
            module-scope ``telemetry_config``).
    """

    config: TelemetryConfig

    def __init__(self, config: TelemetryConfig) -> None:
        """Build the middleware for the given configuration.

        Args:
            config: The parsed, validated telemetry configuration
                (``telemetry/config.py``).
        """
        assert isinstance(config, TelemetryConfig), type(config)
        self.config = config
        self._enabled = config.log_enabled or config.otel_enabled
        self._disabled = False
        self._disable_lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        """Whether observability engages (at least one feature enabled, not yet failed open).

        ``False`` makes :meth:`__call__` a pure pass-through for every
        method; ``server.py``'s startup guard, the Phase 3 unit tests, and
        anything else reading the effective observability state read it.
        It turns ``False`` -- and stays ``False`` for the rest of the
        process -- once the Task 4.3 call-time fail-open guard has
        disabled observability after a first contract violation.
        """
        result = self._enabled and not self._disabled
        return result

    async def __call__(
        self,
        ctx: ServerRequestContext[Any, Any],
        call_next: CallNext,
    ) -> HandlerResult:
        """Run one inbound request/notification through the middleware.

        When :attr:`enabled` is ``False`` (both features off, the default,
        or the Task 4.3 call-time guard has failed open), the request is
        passed straight to ``call_next(ctx)`` unmodified and unobserved.
        When ``ctx.method`` is not one of the three invocation methods,
        the request is passed straight through unobserved (ACC-013).
        Otherwise the invocation is observed per the module docstring
        (identity extraction, correlation ID, start/completion/error
        records, per-channel error attachment/conversion).

        The middleware-contract surfaces (the ``ctx.method`` read here,
        the pre-call extraction and post-call result processing in
        :meth:`_observe`) are guarded per the Task 4.3 fail-open policy:
        a first ``AttributeError``/``TypeError`` there -- a future SDK
        whose provisional contract no longer matches this implementation
        -- logs one warning, disables observability for the rest of the
        process, and still completes the request unmodified (``call_next``
        is never called twice).

        Args:
            ctx: The per-request context (``ctx.method``/``ctx.params``
                are the identity source; ``ctx.session`` is never touched).
            call_next: The rest of the middleware chain.

        Returns:
            The (possibly annotated) result of ``call_next``.
        """
        if not self.enabled:
            return await call_next(ctx)
        try:
            method = ctx.method
        except (AttributeError, TypeError) as e:
            self._fail_open_once(e)
            return await call_next(ctx)
        if method not in _METHOD_ITEM_TYPE:
            return await call_next(ctx)
        return await self._observe(ctx, call_next, method)

    async def _observe(
        self,
        ctx: ServerRequestContext[Any, Any],
        call_next: CallNext,
        method: str,
    ) -> HandlerResult:
        """Observe one invocation of one of the three methods (see :meth:`__call__`).

        Args:
            ctx: The per-request context.
            call_next: The rest of the middleware chain.
            method: The already-extracted ``ctx.method`` (one of the three
                invocation methods; ``__call__``'s guarded read).

        Returns:
            The (possibly annotated) result of ``call_next``.

        Raises:
            MCPError: For a raised ``MCPError`` (channel (b), the error's
                ``data`` annotated in place) or a raised
                ``ValidationError``/other raw exception (channel (c), the
                converted, wire-identical error).
        """
        try:
            item_type = _METHOD_ITEM_TYPE[method]
            params: Mapping[str, Any] | None = ctx.params if isinstance(ctx.params, Mapping) else None
            raw_item = params.get(_METHOD_PARAMS_KEY[method]) if params is not None else None
            item_name: str | None = raw_item if isinstance(raw_item, str) else None
            status = _set_status_value(method, item_name, params)
            correlation_id = new_correlation_id()
            started = time.monotonic()
            self._log(_PHASE_START, logging.INFO, method, item_type, item_name, correlation_id, status=status)
        except (AttributeError, TypeError) as e:
            self._fail_open_once(e)
            return await call_next(ctx)
        try:
            result = await call_next(ctx)
        except MCPError as e:
            self._log(
                _PHASE_FAILED,
                logging.ERROR,
                method,
                item_type,
                item_name,
                correlation_id,
                status=status,
                duration_ms=_duration_ms(started),
                exception=_raised_exception_field(e),
            )
            _attach_correlation_id_to_mcp_error(e, correlation_id)
            raise
        except ValidationError as e:
            self._log(
                _PHASE_FAILED,
                logging.ERROR,
                method,
                item_type,
                item_name,
                correlation_id,
                status=status,
                duration_ms=_duration_ms(started),
                exception=_raised_exception_field(e),
            )
            raise _converted_mcp_error(e, correlation_id) from e
        except Exception as e:
            self._log(
                _PHASE_FAILED,
                logging.ERROR,
                method,
                item_type,
                item_name,
                correlation_id,
                status=status,
                duration_ms=_duration_ms(started),
                exception=_raised_exception_field(e),
            )
            raise _converted_mcp_error(e, correlation_id) from e
        try:
            duration_ms = _duration_ms(started)
            if method == METH_TOOLS_CALL and _is_tool_error_result(result):
                self._log(
                    _PHASE_FAILED,
                    logging.ERROR,
                    method,
                    item_type,
                    item_name,
                    correlation_id,
                    status=status,
                    duration_ms=duration_ms,
                    exception=_tool_error_field(result),
                )
                _attach_correlation_id_to_result(result, correlation_id)
                return result
            self._log(
                _PHASE_COMPLETED,
                logging.INFO,
                method,
                item_type,
                item_name,
                correlation_id,
                status=status,
                duration_ms=duration_ms,
            )
            return result
        except (AttributeError, TypeError) as e:
            # Post-call contract surface (the SDK-returned result shape):
            # fail open once and return the result the chain produced,
            # unannotated -- the request itself already succeeded.
            self._fail_open_once(e)
            return result

    def _fail_open_once(self, exc: Exception) -> None:
        """The Task 4.3 call-time fail-open: one warning, then observability off.

        On the first middleware-contract violation at call time (an
        ``AttributeError``/``TypeError`` from one of the guarded
        contract surfaces), log exactly one warning via the
        ``biz.dfch.specmgr.telemetry`` logger and disable observability
        for the rest of the process: every later request is a pure
        pass-through (no records, no IDs, no attachment, no conversion).
        The server keeps operating normally -- the request that hit the
        violation still completes (see the guarded call sites).

        Args:
            exc: The contract-violation exception (named in the warning).
        """
        with self._disable_lock:
            if self._disabled:
                return
            self._disabled = True
        logger.warning(
            "the installed MCP SDK's Server.middleware contract is incompatible with the "
            "specmgr telemetry middleware at call time (%s: %s); call observability is "
            "disabled for the rest of this process (one message per episode)",
            type(exc).__name__,
            exc,
        )

    def _log(
        self,
        phase: str,
        level: int,
        method: str,
        item_type: str,
        item_name: str | None,
        correlation_id: str,
        *,
        status: str | None = None,
        duration_ms: float | None = None,
        exception: dict[str, object] | None = None,
    ) -> None:
        """Emit one start/completion/error record for the invocation.

        The message carries id/type-only identity (``"{item_type}
        {item_name} {phase}"`, the item name omitted when it could not be
        extracted from the raw params) -- no arguments, no body, no paths,
        no titles (ACC-004); the structured fields ride in ``extra=`` and
        ``telemetry/logging.py``'s formatters emit only what is present.

        Args:
            phase: The record's phase (``start``/``completed``/``failed``).
            level: The logging level (INFO for start/completed, ERROR for
                failed).
            method: The JSON-RPC method (``tools/call``/``resources/read``/
                ``prompts/get``).
            item_type: The item type (``tool``/``resource``/``prompt``).
            item_name: The invoked item's identity, or ``None``.
            correlation_id: The invocation's correlation ID.
            status: The new status value (``set_status`` invocations only).
            duration_ms: The measured duration in milliseconds
                (completion/error records only; absent on the start record).
            exception: The error record's ``exception`` field (error
                records only).
        """
        identity = f"{item_type} {item_name}" if item_name is not None else item_type
        message = f"{identity} {phase}"
        extra: dict[str, object] = {
            "correlation_id": correlation_id,
            "method": method,
            "item_type": item_type,
        }
        if item_name is not None:
            extra["item_name"] = item_name
        if status is not None:
            extra["status"] = status
        if duration_ms is not None:
            extra["duration_ms"] = duration_ms
        if exception is not None:
            extra["exception"] = exception
        logger.log(level, message, extra=extra)
