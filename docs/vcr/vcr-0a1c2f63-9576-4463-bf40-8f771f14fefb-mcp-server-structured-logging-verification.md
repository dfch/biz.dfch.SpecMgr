---
classification: null
created: '2026-09-19 13:18:34.380+02:00'
id: 0a1c2f63-9576-4463-bf40-8f771f14fefb
status: draft
type: vcr
updated: '2026-09-21 22:25:40.952+02:00'
version: 1.0.0
---

# MCP Server Structured Logging Verification

## Verifies

<!-- Authored immediately after REQ bc356fc9 finalized, per the "author VCR early, extend phase-by-phase" convention (feat-139-logging-telemetry). -->

REQ bc356fc9-964a-4274-93ec-4627c5aeb2e5: MCP Server Structured Logging

Confirms that structured logging is fully opt-in, covers every MCP item
(not tools only), redacts sensitive content, exposes the correlation ID
only on error, and supports an opt-in file sink -- as specified by the
requirement, ahead of `feat-139-logging-telemetry`'s implementation.

## Coverage

partial

## Acceptance Criteria

### AC-001 (Demonstration): Logging is off by default

With no `SPECMGR_LOG_*` environment variables set, running `specmgr mcp`
emits zero log records and writes nothing to stdout beyond the JSON-RPC
channel. Verified by `tests/telemetry/test_logging.py::TestSetupDisabled::test_disabled_config_is_a_no_op_on_the_root_logger` (the setup is a no-op when disabled, so the default configuration adds nothing to the existing root handler set), `tests/telemetry/test_logging.py::TestServerModuleScopeWiring::test_fresh_server_import_with_the_default_config_keeps_the_sdk_default_handlers` (a fresh `specmgr mcp` import under the default environment leaves the SDK's own `configure_logging()` handler set in place), and the stdout-safety pair `tests/telemetry/test_logging.py::TestStdoutSafety::test_rich_format_never_writes_stdout` / `tests/telemetry/test_logging.py::TestStdoutSafety::test_json_format_never_writes_stdout` (neither format ever writes to stdout).

#### Test Steps

1. Start `specmgr mcp` with no `SPECMGR_LOG_*` environment variables set.
2. Invoke any tool via an MCP client.
3. Confirm no log output is produced and stdout contains only JSON-RPC
   frames.

### AC-002 (Test): Every MCP tool call, resource read, and prompt invocation is logged, not tools only

With `SPECMGR_LOG_ENABLED=true`, invoking a tool, a resource, and a
prompt each produce a start and a completion (or error) log record,
tagged with a per-invocation correlation ID; a non-invocation request
sharing the same server-side dispatch mechanism (e.g. a capability-
listing request) produces no such record. Verified by
`tests/telemetry/test_middleware.py::TestMethodFilter::test_the_three_invocation_methods_produce_start_and_completion_records` (with `SPECMGR_LOG_ENABLED=true`, a `tools/call`, a `resources/read`, and a `prompts/get` each produce a start and a completion record tagged with the same per-invocation correlation ID), `tests/telemetry/test_middleware.py::TestMethodFilter::test_non_invocation_methods_produce_no_record_and_no_attachment` (`initialize`, `tools/list`, `resources/list`, `prompts/list`, `ping`, and a `notifications/*` message produce no record and pass through unmodified), `tests/telemetry/test_middleware.py::TestIdentityExtraction::test_resource_read_identity_comes_from_the_uri_param` (a resource read's logged identity comes from its `uri` param -- resources are observed, not tools only), and `tests/telemetry/test_middleware.py::TestEnablementGate::test_logging_only_engages_the_observability_path` (the records engage under `SPECMGR_LOG_ENABLED=true` alone).

### AC-003 (Test): Log content is redacted

A log record includes the invoked item's `id` and `type` (and, for
`set_status`, the new status value); this feature's own logging code
never itself attaches the full content of an item, an absolute
filesystem path, or a document/artifact title as a dedicated field.
Free-text log content is additionally passed through a best-effort
absolute-path scrub; the title-embedding exception messages already
known in non-deprecated domains are reworded at their source instead
(the deprecated ADR domain's title sites are an accepted residual gap;
path-embedding messages are scrub-covered), since no generic filter can
reliably detect free-form title text.

### AC-004 (Test): Correlation ID appears only in error responses

A failing tool call's error response includes a correlation ID; a
successful call's result never includes one. Verified by
`tests/telemetry/test_middleware.py::TestToolErrorChannel::test_an_is_error_dict_result_is_logged_and_gets_the_correlation_id_in__meta` (a failing tool call's `isError: true` error result gets the ID in its `_meta`), `tests/telemetry/test_middleware.py::TestMcpErrorChannel::test_a_mcp_error_gets_the_correlation_id_merged_into_its_data_preserving_the_uri` (a failing resource read's JSON-RPC error gets the ID in `error.data`, preserving the SDK's own `uri` entry), `tests/telemetry/test_middleware.py::TestRawExceptionChannel::test_a_validation_error_is_converted_to_the_dispatcher_invalid_params_wire_identically` (a failing prompt call's raw `ValidationError` is converted to the wire-identical dispatcher error carrying the ID in `error.data`), `tests/telemetry/test_middleware.py::TestToolErrorChannel::test_a_non_error_dict_result_never_gets_the_correlation_id` (a successful result never gets one), and `tests/telemetry/test_middleware.py::TestEnablementGate::test_both_off_passes_a_tool_error_result_through_untouched` (in the default both-off config the middleware is a pure pass-through and attaches nothing).

### AC-005 (Test): File sink behaves as specified

With `SPECMGR_LOG_ENABLED=true` and the file-sink sub-switch enabled, a
log file at the configured path receives structured JSON records; with
the file sink left at its default (disabled), no such file is written;
the file sink always emits JSON, even when the console format is set to
`rich`. Verified by `tests/telemetry/test_logging.py::TestFileSink::test_file_sink_receives_json_records_when_both_switches_are_on` (JSON records land at the configured path when both switches are enabled), `tests/telemetry/test_logging.py::TestFileSink::test_file_sink_is_json_even_when_the_console_format_is_rich` (always JSON, even when the console format is `rich`), `tests/telemetry/test_logging.py::TestFileSink::test_file_sink_writes_one_json_object_per_line` (line-delimited JSON records), `tests/telemetry/test_logging.py::TestFileSink::test_file_sink_inactive_when_the_file_switch_is_off` (no file written when the sub-switch is at its default), and `tests/telemetry/test_logging.py::TestFileSink::test_file_sink_inactive_when_logging_is_disabled` (no file written while `SPECMGR_LOG_ENABLED` is off, regardless of the sub-switch).

## More Information

Coverage is `partial`: AC-001, AC-002, AC-004, and AC-005 now carry
their concrete test references above -- AC-001/AC-005 from
feat-139-logging-telemetry Phase 2 (Tasks 2.1/2.2/2.5:
`telemetry/logging.py`'s `JsonFormatter`/`SpecmgrRichHandler`/
`setup_logging`, wired into `server.py`'s module scope) and
AC-002/AC-004 from Phase 3 (Tasks 3.1/3.4/3.7:
`telemetry/middleware.py`'s `SpecmgrTelemetryMiddleware`, appended to
`mcp.middleware` by `server.py`'s module scope under the Task 3.2
startup guard). AC-003 (redaction) remains pending Phase 6 -- its
id/type-only identity clause (incl. `set_status`'s new status value) is
already pinned by `tests/telemetry/test_middleware.py::TestLogRecordShape::test_a_set_status_call_records_the_new_status_value` and
`tests/telemetry/test_middleware.py::TestLogRecordShape::test_record_messages_carry_id_and_type_only`, while its scrub/rewording half awaits Phase 6's `telemetry/redact.py`; `## Coverage` moves to `full` when it lands.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-21 21:20:00.000+02:00 - Phase 3 landed: AC-002/AC-004 carry concrete test references; coverage stays partial

feat-139-logging-telemetry Phase 3 (Tasks 3.1-3.7) implemented
`telemetry/middleware.py`'s `SpecmgrTelemetryMiddleware` -- the
enablement-gated, ACC-013-filtered call observability: a per-invocation
correlation ID (`new_correlation_id` -- the active span's trace ID when
a recording span is current, else a fresh `uuid4().hex`), start/
completion/error log records with id/type-only messages (plus the new
status value for `set_status` invocations), per-method identity
extraction (`name` for tools/prompts, `uri` for resources), and the
per-channel error behavior (a `tools/call` `isError: true` result
detected post-call, with the ID merged into its `_meta`; a raised
`MCPError` kept, with the ID merged into its `error.data`, preserving
the SDK's own `uri` entry; a raised `ValidationError`/raw exception
converted to the wire-identical dispatcher error carrying the ID in
`data`, and re-raised) -- appended to `mcp.middleware` by
`server.py`'s module scope under the Task 3.2 startup guard (a broken
`Server.middleware` contract logs one warning and keeps starting). In
the default both-off config the middleware is a pure pass-through: no
record, no ID, no conversion. AC-002 and AC-004 now carry the concrete
test references above; AC-003 (redaction) remains pending Phase 6, so
`## Coverage` stays `partial`.

### 2026-09-21 16:35:22.494+02:00 - Phase 2 landed: AC-001/AC-005 carry concrete test references; coverage stays partial

feat-139-logging-telemetry Phase 2 (Tasks 2.1-2.5) implemented
`telemetry/logging.py` -- the pinned record shape in `JsonFormatter`
(JSON) and `SpecmgrRichHandler` (rich, built on the SDK's own rich
handler), plus the explicit, idempotent root-logger setup
`setup_logging` gated by `SPECMGR_LOG_ENABLED`, with the opt-in
always-JSON file sink -- and wired it unconditionally into `server.py`'s
module scope, before `MCPServer` is constructed, so the SDK's own
`configure_logging()` (a `logging.basicConfig`) cannot override the
enabled configuration. AC-001 and AC-005 now carry the concrete test
references above; AC-002/AC-004 (Phase 3) and AC-003 (Phase 6) remain
pending, so `## Coverage` stays `partial`.

### 2026-09-21 05:45:00.000+02:00 - Aligned AC-003 rewording clause to the post-exploration re-evaluation

AC-003's rewording clause was aligned to the feat-139-logging-telemetry
post-exploration re-evaluation's Task 6.7 scope decision: the mandatory
rewording set is the title-embedding sites in non-deprecated domains
(today the 13 `UcParseError` sites in `uc/models/v1/parser.py`), the
deprecated ADR domain's 9 title sites are an accepted residual gap
(the domain is planned for phase-out), and the path-embedding sites
are scrub-covered. No implementation exists yet; `## Coverage` stays
`partial`.

### 2026-09-19 13:25:00.000+02:00 - Initial draft created (partial coverage)

Initial VCR authored immediately once REQ bc356fc9 was finalized, before
any implementation phase of `feat-139-logging-telemetry` started.
Acceptance criteria above are limited to what is directly derivable from
the requirement's specified configuration/behavior contract.
