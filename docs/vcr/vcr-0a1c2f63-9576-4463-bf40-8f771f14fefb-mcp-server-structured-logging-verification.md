---
classification: null
created: '2026-09-19 13:18:34.380+02:00'
id: 0a1c2f63-9576-4463-bf40-8f771f14fefb
status: draft
type: vcr
updated: '2026-09-25T12:59:01.952+02:00'
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

full

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
`tests/telemetry/test_middleware.py::TestMethodFilter::test_the_three_invocation_methods_produce_start_and_completion_records` (with `SPECMGR_LOG_ENABLED=true`, a `tools/call`, a `resources/read`, and a `prompts/get` each produce a start and a completion record tagged with the same per-invocation correlation ID), `tests/telemetry/test_middleware.py::TestMethodFilter::test_non_invocation_methods_produce_no_record_and_no_attachment` (`initialize`, `tools/list`, `resources/list`, `prompts/list`, `ping`, and a `notifications/*` message produce no record and pass through unmodified), `tests/telemetry/test_middleware.py::TestIdentityExtraction::test_resource_read_identity_comes_from_the_uri_param` (a resource read's logged identity comes from its `uri` param -- resources are observed, not tools only), and `tests/telemetry/test_middleware.py::TestEnablementGate::test_logging_only_engages_the_observability_path` (the records engage under `SPECMGR_LOG_ENABLED=true` alone). The enablement's own configuration path is additionally pinned by `tests/test_cli.py::TestDotenvTelemetryOrdering` (the project `.env`'s `SPECMGR_LOG_ENABLED=true`/`SPECMGR_LOG_FORMAT=json` alone, in a fresh child with a clean `SPECMGR_*`-stripped process environment, installs the configured scrub-wired JSON console handler on the root logger at CLI import time -- i.e. the `.env` value reaches `server.py`'s import-scope config read; its companion test pins the `.env`-only static misconfiguration refusing to start with exit code 1, empty stdout, and exactly one stderr line -- the `TelemetryConfigError` message, ACC-011. Both are the post-close review's ordering fix, Phase 10 Task 10.3).

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
reliably detect free-form title text. Verified by
`tests/telemetry/test_redact.py::TestScrubPaths` (the scrub's regex:
POSIX two-or-more-segment paths, Windows drive paths, and UNC paths --
raw and JSON-escaped alike -- are replaced by the pinned
`<redacted-path>` token, while single-slash tokens, `scheme://`/
`specmgr://` shapes, URLs without multi-segment paths, and
version-matrix tokens are left alone, pinning the documented
false-positive/negative limits),
`tests/telemetry/test_redact.py::TestFormatterScrub::test_a_path_in_the_message_is_scrubbed_from_the_final_rendered_string`
(the scrub runs at formatter level on the final rendered JSON string),
`tests/telemetry/test_redact.py::TestFormatterScrub::test_a_path_in_the_exception_extra_is_scrubbed_from_the_final_rendered_string`
(the middleware's own `exception` extra -- type + message + traceback --
is scrubbed in the rendered record),
`tests/telemetry/test_redact.py::TestFormatterScrub::test_a_formatter_rendered_exc_text_traceback_is_scrubbed`
(a record's standard `exc_info` -- whose formatter-rendered `exc_text`
embeds absolute file paths that a handler-attached `logging.Filter`
cannot see -- is scrubbed in the final rendered string),
`tests/telemetry/test_redact.py::TestFormatterScrub::test_a_third_party_originating_logger_is_covered_too`
(every rendered record reaching a specmgr-installed handler is covered,
regardless of the record's originating logger),
`tests/telemetry/test_redact.py::TestFormatterScrub::test_the_file_sink_handler_carries_the_scrubbing_formatter_and_scrubs_what_it_writes`
(the opt-in file sink's records land on disk scrubbed),
`tests/telemetry/test_redact.py::TestRichHandlerScrub::test_a_path_in_the_rich_message_text_is_scrubbed` /
`tests/telemetry/test_redact.py::TestRichHandlerScrub::test_a_path_in_the_rich_structured_exception_field_is_scrubbed`
(the rich format's `render_message` seam scrubs the combined message
text, documented residual: the rich-rendered traceback itself), and the
rewording at the source by `tests/uc/models/v1/test_parser.py::TestParseErrorMessagesOmitTitles`
(the 13 reworded `UcParseError` sites -- one test per site -- no longer
embed the heading title, the exception's type and raise condition
unchanged; the deprecated ADR domain's 9 title sites are the accepted
residual gap, the path-embedding sites are scrub-covered and
deliberately not reworded).

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

Coverage is `full`: every acceptance criterion now carries its concrete
test references above -- AC-001/AC-005 from feat-139-logging-telemetry
Phase 2 (Tasks 2.1/2.2/2.5: `telemetry/logging.py`'s
`JsonFormatter`/`SpecmgrRichHandler`/`setup_logging`, wired into
`server.py`'s module scope), AC-002/AC-004 from Phase 3 (Tasks
3.1/3.4/3.7: `telemetry/middleware.py`'s
`SpecmgrTelemetryMiddleware`, appended to `mcp.middleware` by
`server.py`'s module scope under the Task 3.2 startup guard), and
AC-003 (redaction) from Phase 6 (Tasks 6.1/6.2/6.7:
`telemetry/redact.py`'s formatter-level `<redacted-path>` scrub wired
onto every specmgr-installed handler plus the 13 reworded
`UcParseError` title sites in `uc/models/v1/parser.py`, with the
deprecated ADR domain's 9 title sites as the accepted residual gap and
the path-embedding sites scrub-covered). AC-002 additionally carries the Phase 10 post-close review pin of the project-`.env` configuration path (`tests/test_cli.py::TestDotenvTelemetryOrdering`).

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-25T12:40:09.000+02:00 - Post-close review (Phase 10): AC-002 carries the .env configuration-path pin; coverage stays full

feat-139-logging-telemetry's post-close review (feat-reviewer) found the one real defect, in the enablement's configuration path: cli.py's command import chain transitively executes server.py's module scope -- where load_telemetry_config()/setup_logging()/bootstrap_telemetry() read os.environ at import time -- before cli.py's own \_load_default_dotenv() ran, so a project .env's `SPECMGR_LOG_*`/`SPECMGR_OTEL_*` values were silently ignored: a .env-only SPECMGR_LOG_ENABLED=true left the feature disabled at import scope, and a .env-only static misconfiguration bypassed the ACC-011 fail-closed refusal while the status resource (which re-parses the env at read time) reported the enabled configuration that was not in effect (ACC-007). Phase 10 Task 10.3 moved the .env load above the command import chain (find_dotenv's frame-walk start is cli.py itself in either position, so discovery semantics are unchanged) and pinned both directions with the new tests/test_cli.py::TestDotenvTelemetryOrdering subprocess pair (a fresh child per test, the `SPECMGR_*`-stripped process environment, the temp .env the child's only telemetry configuration): the .env-only enablement now installs the configured scrub-wired JSON console handler on the root logger at import time, and the .env-only misconfiguration refuses with exit code 1, empty stdout, and exactly one stderr line -- the TelemetryConfigError message naming the offending env var(s). Both tests are red against the pre-fix ordering. Every acceptance criterion remains demonstrably covered, so ## Coverage stays full.

### 2026-09-24 06:00:00.000+02:00 - Phase 6 landed: AC-003 carries concrete test references; coverage is full

feat-139-logging-telemetry Phase 6 (Tasks 6.1-6.8) implemented
`telemetry/redact.py` -- the free-text redaction backstop: the shared
`scrub_paths` regex (POSIX two-or-more-segment absolute paths, Windows
drive paths, and UNC paths, raw and JSON-escaped alike, replaced by the
pinned `<redacted-path>` token), the formatter-level scrub
(`ScrubbingFormatter` around the JSON console handler's and the file
sink's `JsonFormatter` -- on the final rendered string, where the
`exc_text` traceback exists; `ScrubbingSpecmgrRichHandler` at the rich
`render_message` seam), wired onto every handler `setup_logging`
installs (Task 6.2), so every rendered record reaching those handlers
is covered regardless of originating logger. AC-003 now carries the
concrete test references above (incl. the `exc_text` traceback case and
the Task 6.7 rewording at the source: the 13 `UcParseError` title sites
in `uc/models/v1/parser.py` reworded to omit the title -- exception
type and raise condition unchanged -- with the deprecated ADR domain's
9 title sites as the accepted residual gap and the path-embedding sites
scrub-covered, deliberately not reworded). Every acceptance criterion
is now demonstrably covered, so `## Coverage` moves from `partial` to
`full`.

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
