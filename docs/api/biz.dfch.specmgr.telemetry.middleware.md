# `biz.dfch.specmgr.telemetry.middleware`

The specmgr ``ServerMiddleware``: correlation IDs and call logging (feat-139-logging-telemetry, Phase 3, Task 3.1).

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
degrade (Task 4.2's guard / Task 4.3's fail-open policy), not raise on
every request; the input validation the repo convention requires lives in
``__init__`` instead, where Task 3.2's startup guard already wraps the call.

## Classes

### `SpecmgrTelemetryMiddleware`

The specmgr ``ServerMiddleware``: correlation IDs + start/completion/error logging.

Appended to ``mcp.middleware`` by ``server.py``'s module scope (Task
3.2), it is the innermost context-tier middleware: it observes the
dispatcher's already-serialized wire dict for a success and the raised
exception for a failure. See the module docstring for the enablement
gating, the ACC-013 method filter, the per-method identity extraction,
and the three per-channel error behaviors.

Attributes:
    config: The parsed, validated telemetry configuration the
        middleware was built with (``server.py`` passes its own
        module-scope ``telemetry_config``).


## Functions

### `_attach_correlation_id_to_mcp_error(error: 'MCPError', correlation_id: 'str') -> 'None'`

Channel (b): merge the correlation ID into an ``MCPError``'s ``error.data``.

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


### `_attach_correlation_id_to_result(result: 'HandlerResult', correlation_id: 'str') -> 'None'`

Channel (a): merge the correlation ID into a ``tools/call`` error result's ``_meta``.

For the wire dict, the ``"_meta"`` key is merged (preserving any
pre-existing meta, e.g. the dispatcher's ``serverInfo`` stamp); for the
model, ``CallToolResult.meta`` (which dumps as ``_meta``) is merged
the same way. Only error results reach this function (channel (a)'s
callers gate on :func:`_is_tool_error_result`), so a successful result
never receives the ID.

Args:
    result: The error result to annotate (mutated in place).
    correlation_id: The invocation's correlation ID.


### `_converted_mcp_error(exc: 'Exception', correlation_id: 'str') -> 'MCPError'`

Channel (c): build the wire-identical ``MCPError`` a raw exception is converted to.

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


### `_duration_ms(start: 'float') -> 'float'`

Return the elapsed milliseconds since a ``time.monotonic()`` mark.


### `_first_text_content(result: 'object') -> 'str'`

Return the first text content block's text from an error result.

For the ``tools/call`` error record's ``message`` (the SDK's own
``str(e)`` of the tool's exception, the ``CallToolResult`` content
entry). Returns ``""`` when the result carries no text content block.

Args:
    result: The error result (a wire dict or a ``CallToolResult``).

Returns:
    The first text content's text, or ``""``.


### `_is_tool_error_result(result: 'HandlerResult') -> 'bool'`

Whether a post-``call_next`` ``tools/call`` result is an error result.

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


### `_raised_exception_field(exc: 'BaseException') -> 'dict[str, object]'`

Build the error record's ``exception`` field from a raised exception.

Channel (b)/(c) shape (the Design Notes' pin): the exception's
qualified type name, its ``str()``, and the formatted traceback.

Args:
    exc: The raised exception (an ``MCPError``, a
        ``ValidationError``, or any raw exception).

Returns:
    The ``{"type": ..., "message": ..., "traceback": ...}`` mapping.


### `_set_status_value(method: 'str', item_name: 'str | None', params: 'Mapping[str, Any] | None') -> 'str | None'`

Return the new status value of a ``set_status`` invocation, else ``None``.

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


### `_tool_error_field(result: 'HandlerResult') -> 'dict[str, object]'`

Build the error record's ``exception`` field for a ``tools/call`` error result.

Channel (a) shape: no exception object exists at the middleware layer
for a tool error, so the field carries the SDK's own ``tool_error``
type signal and the error text from the result's content, and no
``traceback`` key.

Args:
    result: The ``isError: true`` result (a wire dict or a
        ``CallToolResult``).

Returns:
    The ``{"type": "tool_error", "message": ...}`` mapping.


### `new_correlation_id() -> 'str'`

Generate the correlation ID for one invocation.

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

