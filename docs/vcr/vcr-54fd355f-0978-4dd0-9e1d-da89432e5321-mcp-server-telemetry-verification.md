---
classification: null
created: '2026-09-19 13:19:26.971+02:00'
id: 54fd355f-0978-4dd0-9e1d-da89432e5321
status: draft
type: vcr
updated: '2026-09-24 09:15:13.217+02:00'
version: 1.0.0
---

# MCP Server Telemetry Verification

## Verifies

<!-- Authored immediately after REQ dacd01f4 finalized, per the "author VCR early, extend phase-by-phase" convention (feat-139-logging-telemetry). -->

REQ dacd01f4-ffd8-4363-a20b-5ac1ce11eef2: MCP Server Telemetry (Metrics and Tracing)

Confirms that telemetry is fully opt-in, covers every MCP item (not
tools only), degrades gracefully when the OTLP endpoint or the
Server.middleware contract fails, uses MCP-specific metric/span
names, records the metrics themselves with correct values, and never
attaches full document bodies, absolute filesystem paths, or
document/artifact titles to any span or metric attribute -- as
specified by the requirement, ahead of
feat-139-logging-telemetry's implementation.

## Coverage

full

## Acceptance Criteria

### AC-001 (Demonstration): Telemetry is off by default

With no `SPECMGR_OTEL_*` environment variables set, running `specmgr mcp` emits zero telemetry and writes nothing to stdout beyond the
JSON-RPC channel. Verified by `tests/telemetry/test_otel.py::TestBootstrapDisabled::test_disabled_config_installs_no_providers_and_leaves_the_meter_slot_none` (the bootstrap installs no providers and leaves the meter slot `None` under the default config, so the SDK's built-in middleware keeps producing only non-recording spans) and the default-exporter case `tests/telemetry/test_otel.py::TestStdoutSafetySubprocess::test_default_exporter_console_writes_zero_bytes_beyond_json_rpc_to_stdout` (a real stdio session with the default `console` exporter writes zero bytes to stdout beyond the JSON-RPC frames).

### AC-002 (Test): Every MCP tool call, resource read, and prompt invocation is correlated, not tools only

With `SPECMGR_OTEL_ENABLED=true`, invoking a tool, a resource, and a
prompt each has its correlation ID matching the trace/span ID of the
span the SDK's built-in `OpenTelemetryMiddleware` creates for that
request (that middleware spans every JSON-RPC method regardless, out
of this feature's control; only the correlation behavior is scoped to
actual invocations). Verified by `tests/telemetry/test_otel.py::TestSpanCorrelationRealImportOrder::test_every_invocation_correlation_id_matches_the_sdk_span_trace_id` (a real `specmgr mcp` stdio subprocess session with `SPECMGR_OTEL_ENABLED=true` and `SPECMGR_LOG_ENABLED=true`: for a `tools/call`, a `resources/read`, and a `prompts/get`, the correlation ID the middleware's completion log record carries equals the `traceId` of the span the SDK's built-in middleware exported for that same request -- the span-ID branch of the Phase 3 helper, confirmed under the real import order, not a pre-import provider installation).

### AC-003 (Test): An unreachable OTLP endpoint degrades gracefully

With `SPECMGR_OTEL_ENABLED=true` and the OTLP exporter pointed at an
unreachable endpoint, tool calls keep succeeding, exactly one stderr
message records the export failure, and the message does not repeat on
subsequent calls while the endpoint remains unreachable. Verified by
`tests/telemetry/test_otel_exporter_wrapper.py::TestEpisodeStateMachine::test_a_first_failure_emits_exactly_one_warning_and_attaches_the_suppression`, `tests/telemetry/test_otel_exporter_wrapper.py::TestEpisodeStateMachine::test_repeated_failures_emit_no_further_warnings`, and `tests/telemetry/test_otel_exporter_wrapper.py::TestEpisodeStateMachine::test_a_subsequent_episode_emits_one_further_warning` (the wrapper's episode state machine: exactly one stderr message per failure episode, never repeating while the condition persists, and a further single message only after a subsequent reconnect-then-drop cycle), `tests/telemetry/test_otel_exporter_wrapper.py::TestExporterLogSuppression::test_the_exporters_own_logs_are_suppressed_while_the_episode_is_active` (the SDK's own 3x WARNING + 1x ERROR per failed export cycle is suppressed while the episode is active, and flows again after recovery), and end to end by `tests/telemetry/test_otel.py::TestStdoutSafetySubprocess::test_unreachable_otlp_endpoint_writes_zero_bytes_beyond_json_rpc_to_stdout` (tool calls keep succeeding against a deliberately unreachable endpoint, and exactly one stderr message records the span-export failure episode).

### AC-004 (Test): A broken Server.middleware contract fails open

If the installed SDK's Server.middleware contract is incompatible with
this feature's middleware, the server logs a single warning and
continues operating with logging/telemetry disabled, rather than
failing to start. Verified by `tests/telemetry/test_middleware.py::TestServerWiring::test_an_incompatible_sdk_contract_fails_open_at_startup_with_one_warning` (a simulated contract change -- the SDK's `ServerMiddleware.__call__` renamed -- makes a fresh `server` import log exactly one warning, append no middleware, and still construct an operating server) and `tests/telemetry/test_middleware.py::TestCallTimeFailOpen::test_a_broken_ctx_method_at_call_time_fails_open_with_one_warning_and_completes_the_request` (a first contract violation at call time logs exactly one warning, disables observability for the process, and still completes the request); the installed SDK's contract shape itself is pinned by the canary assertions in `tests/telemetry/test_middleware.py::TestMiddlewareContractCanary`, and an app-level exception is proven not to be misread as a contract violation by `tests/telemetry/test_middleware.py::TestCallTimeFailOpen::test_an_app_exception_is_not_misread_as_a_contract_violation`.

### AC-005 (Inspection): Metric/span names follow the MCP-specific naming scheme

A source review confirms metric/span names use the `mcp.*` namespace
(`mcp.tool.duration`, `mcp.tool.call.count`, `mcp.tool.error.count`,
`mcp.cache.hit`/`mcp.cache.miss`, `mcp.lock.wait_time`, with the
`mcp.tool.name`/`mcp.domain`/`mcp.item.type`/`error.type` attributes),
not the raw OpenTelemetry `rpc.*` semantic-convention names. Verified
by `tests/telemetry/test_metrics.py::TestMiddlewareCallCount::test_a_success_is_counted_once_with_the_pinned_attributes` (the exported instrument carries the pinned `mcp.tool.call.count` name with the `mcp.tool.name`/`mcp.item.type`/`mcp.domain` attribute keys), `tests/telemetry/test_metrics.py::TestBootstrapInstruments::test_lock_wait_records_land_in_the_bootstrap_histogram_with_the_pinned_buckets` (the bootstrap-created `mcp.lock.wait_time` histogram, its `ms` unit, and the pinned explicit bucket boundaries), `tests/telemetry/test_metrics.py::TestBootstrapInstruments::test_the_cache_observables_carry_one_series_per_registered_domain` (the `mcp.cache.hit`/`mcp.cache.miss` observable counters, one `mcp.domain`-attributed series per registered doc-cache domain), and `tests/telemetry/test_domain_mapping.py` (the name/uri -> domain mapping behind the `mcp.domain` attribute, including the live-registration drift test that keeps it in sync with what `server.py` actually registers).

### AC-006 (Analysis): Trace sampling is always-on

A review of the documented environment variables confirms no
`SPECMGR_OTEL_*` sample-rate configuration is exposed, consistent with
the accepted always-on-sampling decision. Verified by
`tests/telemetry/test_metrics.py::TestBootstrapSampler::test_the_config_module_defines_exactly_the_pinned_eight_env_vars` (the config module defines exactly the pinned eight `SPECMGR_LOG_*`/`SPECMGR_OTEL_*` environment variables -- no sample-rate variable exists) and `tests/telemetry/test_metrics.py::TestBootstrapSampler::test_the_bootstrap_passes_no_sampler_to_the_tracer_provider` (the bootstrap constructs the `TracerProvider` without a `sampler=` argument, i.e. the SDK's default always-on sampler); that the default configuration actually exports every span is demonstrated end to end by `tests/telemetry/test_otel.py::TestSpanCorrelationRealImportOrder::test_every_invocation_correlation_id_matches_the_sdk_span_trace_id` (a real stdio session exports the SDK span for every one of the three invocations under the default, unconfigured sampling).

### AC-007 (Test): Span content is redacted, including spans the SDK's own built-in middleware creates

With `SPECMGR_OTEL_ENABLED=true`, this feature's own code (middleware,
meter) never itself attaches a full document body, an absolute
filesystem path, or a document/artifact title as a dedicated span or
metric attribute value -- on any span, including one created entirely
by the MCP SDK's own built-in `OpenTelemetryMiddleware`, not only ones
this feature's own middleware would create. A global,
`TracerProvider`-level `SpanProcessor` (required to reach an
SDK-created span at all) additionally runs a best-effort scrub for
absolute-filesystem-path-shaped substrings in a span's attributes and
exception-event message text; the title-embedding exception messages
already known in non-deprecated domains are reworded at their source
instead (the deprecated ADR domain's title sites are an accepted
residual gap; path-embedding messages are scrub-covered), since no
generic filter can reliably detect free-form title text. Verified by
`tests/telemetry/test_redact.py::TestSpanProcessorScrub::test_a_span_attribute_carrying_a_path_is_scrubbed_and_non_string_attributes_pass_through` (the global processor replaces a span attribute carrying an absolute path with the pinned `<redacted-path>` token; non-string attributes pass through untouched), `tests/telemetry/test_redact.py::TestSpanProcessorScrub::test_a_span_exception_event_message_and_stacktrace_are_scrubbed_and_type_is_not` (the `exception.message`/`exception.stacktrace` keys `record_exception` sets are scrubbed -- the stacktrace carries the raising file's own absolute path -- while `exception.type`/`exception.escaped` are unchanged), `tests/telemetry/test_redact.py::TestSpanProcessorScrub::test_the_batch_chain_export_sees_the_scrubbed_containers` (the production `BatchSpanProcessor`/export path reads the replaced containers), `tests/telemetry/test_redact.py::TestSpanProcessorScrub::test_a_span_created_entirely_by_the_sdk_builtin_middleware_is_scrubbed` (a span created entirely by the SDK's built-in `OpenTelemetryMiddleware` -- the exception recorded by the middleware's own `record_exception`/`set_status` calls -- exports with its exception-event paths scrubbed), `tests/telemetry/test_redact.py::TestSpanProcessorCanary` (the canary pinning the installed SDK's `ReadableSpan._attributes`/`_events`/`Event._attributes` private containers and the end-to-end visibility of the processor's replacement, so a future SDK restructure fails loudly in CI), `tests/telemetry/test_redact.py::TestTelemetryWiring` (the bootstrap installs the processor before the `BatchSpanProcessor`, and a path-carrying attribute plus exception event export scrubbed through the real production chain), and the rewording at the source by `tests/uc/models/v1/test_parser.py::TestParseErrorMessagesOmitTitles` (the 13 reworded `UcParseError` sites no longer embed the heading title, so the `record_exception`/`set_status(str(e))` payload of those messages no longer carries it).

### AC-008 (Test): Metrics are recorded with correct values and attributes

With `SPECMGR_OTEL_ENABLED=true`, invoking a tool, a resource, and a
prompt each increments the `mcp.tool.call.count` counter tagged with
the correct `mcp.tool.name`/`mcp.domain`/`mcp.item.type` attributes,
records a latency observation on the `mcp.tool.duration` histogram,
and a failure increments the `mcp.tool.error.count` counter tagged
with the per-channel error-type signal (the exception's type where
observable at the middleware layer, the SDK's `tool_error` value for
`tools/call` `isError` results, the JSON-RPC error code for wrapped
errors); the `feat-107` document-cache
hit/miss counters and the per-domain lock wait-time histogram both
reflect real cache/lock activity observed during the same calls.
Verified by `tests/telemetry/test_metrics.py::TestMiddlewareCallCount` (exactly one `mcp.tool.call.count` increment per observed invocation, whatever its outcome, with the pinned attributes; an unobserved protocol method is never counted; a `None` meter slot allocates nothing per call), `tests/telemetry/test_metrics.py::TestMiddlewareItemTypesAndDomains` (a tool/resource/prompt invocation is tagged with its per-method identity key -- `name` for tools/prompts, `uri` for resources -- the `mcp.item.type` value, and the Task 5.1-mapped `mcp.domain`, which is omitted entirely, never empty, for the no-domain items and for a generic dispatch tool called without a `type` argument), `tests/telemetry/test_metrics.py::TestMiddlewareDurationHistogram` (one `mcp.tool.duration` observation per invocation, unit `ms`), `tests/telemetry/test_metrics.py::TestMiddlewareErrorCount` (the per-channel `error.type` signal: `tool_error` for a `tools/call` `isError: true` result, the `MCPError`'s JSON-RPC code as a string for SDK-wrapped errors, and `type(exc).__qualname__` for raw/`ValidationError` exceptions), `tests/telemetry/test_metrics.py::TestBootstrapInstruments::test_the_cache_observables_carry_one_series_per_registered_domain` (the `mcp.cache.hit`/`mcp.cache.miss` values reflect real `DocCache` activity per domain), `tests/telemetry/test_lock_wait.py::TestLockWaitRecording` (each of the thirteen domain locks records its acquire wait -- not hold -- to the `mcp.lock.wait_time` histogram with its `mcp.domain` attribute), and the underlying DocCache counters/registry by `tests/general/tools/test__doc_cache.py::TestDocCacheStatsAndRegistry` and the `mcp.domain` mapping by `tests/telemetry/test_domain_mapping.py`.

## More Information

Coverage is `full`: every acceptance criterion now carries its
concrete test references above -- AC-001 (off by default) and AC-002
(correlation ID matches the SDK span's trace ID) from
feat-139-logging-telemetry Phase 4's OpenTelemetry SDK bootstrap
(`telemetry/otel.py`, Tasks 4.1/4.2/4.9/4.11: providers + exporters
installed only when `SPECMGR_OTEL_ENABLED=true`, called at
`server.py`'s module scope in the config -> logging -> OTel ->
middleware order, with the `service.name = "specmgr"` resource
confirmed on every exported span and metric), AC-003
(unreachable-OTLP graceful degradation) from the Task 4.5 exporter
wrapper's episode de-duplication, AC-004 (broken `Server.middleware`
contract fails open) from the Task 4.3 fail-open policy and its Task
4.4 canary/simulation tests, AC-005/AC-006/AC-008 from Phase 5's
metrics instrumentation, and AC-007 (span redaction) from Phase 6
(Tasks 6.1/6.2: `telemetry/redact.py`'s global
`RedactionSpanProcessor`, added to the `TracerProvider` before the
exporting `BatchSpanProcessor`, scrubbing every span's attributes and
exception events -- incl. the SDK's built-in middleware's spans -- by
replacing the SDK's private attribute containers, per Task 1a.3's
confirmed mechanism, with the Task 6.3 canary pinning that reliance;
plus the Task 6.7 rewording of the 13 `UcParseError` title sites at
the source). AC-007 was added during a pre-Phase-1
implementation-readiness review that identified it as a REQ dacd01f4
clause (span/metric-attribute redaction) not yet covered by any
acceptance criterion in this VCR's initial Phase 0 draft, and AC-008
was added during a later plan-consistency review that found REQ
dacd01f4's central metrics clause (tool-call latency/count,
error-type counts, doc-cache hit/miss rate, domain-lock wait time) had
no corresponding acceptance criterion either -- see
`.specmgr/feat/feat-139-logging-telemetry/README.md`'s Decisions Made
log ("Redaction widened to a global SpanProcessor after a follow-up
clarification" and "Metrics-correctness VCR gap closed with a new AC
instead of folded into an existing one").

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-24 06:00:00.000+02:00 - Phase 6 landed: AC-007 carries concrete test references; coverage is full

feat-139-logging-telemetry Phase 6 (Tasks 6.1-6.8) implemented
`telemetry/redact.py`'s span-side half: the global,
`TracerProvider`-level `RedactionSpanProcessor` (Task 6.1), added by
the Task 6.2 bootstrap wiring *before* the exporting
`BatchSpanProcessor` (the provider invokes `on_end` in add order, so
the scrub runs before the span reaches the export path), covering
every span the process creates -- including the SDK's own built-in
`OpenTelemetryMiddleware`'s spans, this feature creating none of its
own. Per Task 1a.3's confirmed mechanism (no public mutation API on
`ReadableSpan`; the span's `BoundedAttributes` locked immutable at
`end()`), the processor scrubs by replacing the private containers
(`readable_span._attributes` and each `event._attributes` with fresh
`BoundedAttributes` copies, only when the scrub changed a value),
which both the in-memory/console export paths and the OTLP protobuf
encoder see at export time. AC-007 now carries the concrete test
references above -- the attribute/event scrub, the batch-chain
visibility, the SDK-built-in-middleware span case (an exception whose
message carries a fake absolute path is injected through the
middleware's own `record_exception`/`set_status` calls and the
exported span no longer contains it), the Task 6.3 canary (the
installed SDK's `ReadableSpan._attributes`/`_events`/`Event.
_attributes` containers exist and the replacement is visible end to
end, so a future SDK restructure fails loudly in CI), and the Task 6.7
rewording of the 13 `UcParseError` title sites (the
`record_exception`/`set_status(str(e))` payload of those messages no
longer carries a title). Every acceptance criterion (AC-001 through
AC-008) is now demonstrably covered, so `## Coverage` moves from
`partial` to `full`.

### 2026-09-22 22:40:00.000+02:00 - Phase 5 landed: AC-005/AC-006/AC-008 carry concrete test references; coverage stays partial

feat-139-logging-telemetry Phase 5 (Tasks 5.1-5.8) implemented the
metrics instrumentation this VCR's AC-008 was written for: the Task 5.1
explicit name/uri -> domain mapping (`telemetry/domain_mapping.py`,
with a live-registration drift test), the middleware's lazily created
`mcp.tool.duration`/`mcp.tool.call.count`/`mcp.tool.error.count`
instruments (the pinned `mcp.tool.name`/`mcp.item.type`/`mcp.domain`
attributes, the domain omitted for the no-domain case, and the
per-channel `error.type` signal), the bootstrap-created
`mcp.lock.wait_time` histogram and `mcp.cache.hit`/`mcp.cache.miss`
observable counters (the `telemetry/metrics.py` callbacks reading the
new `DocCache` registry, the `stats()` accessor, and the plain-int
hit/miss counters at `DocCache.read`'s real decision points), and the
thirteen `_lock.py` context managers' acquire/release refactor around
the shared `record_lock_wait` helper (with its release-on-exception
regression tests). AC-005 (the MCP-specific naming scheme), AC-006
(always-on sampling -- no sample-rate variable on the config surface,
no `sampler=` in the bootstrap), and AC-008 (the metrics recorded with
correct values/attributes) now carry the concrete test references
above; only AC-007 (Phase 6's span redaction) remains outstanding, so
`## Coverage` stays `partial`.

### 2026-09-22 12:49:41.000+02:00 - Phase 4 landed: AC-001 through AC-004 carry concrete test references; coverage stays partial

feat-139-logging-telemetry Phase 4 (Tasks 4.1-4.11) implemented
`telemetry/otel.py` -- the OpenTelemetry SDK bootstrap (a
`TracerProvider` with a `BatchSpanProcessor`, a `MeterProvider` with a
`PeriodicExportingMetricReader`, both carrying a fixed
`service.name = "specmgr"` resource; the default `console` exporters
redirected to `out=sys.stderr`; the OTLP/HTTP exporters wrapped in the
Task 4.5 `OtlpExporterWrapper` for one-message-per-episode degradation),
called unconditionally at `server.py`'s module scope in the pinned
config -> logging -> OTel -> middleware order, with provider shutdown
in `_lifespan`'s post-`yield` section -- plus the Task 4.3 fail-open
policy (startup contract check + call-time self-disable), the Task 4.4
canary/simulation tests, and the Task 4.2 end-to-end confirmation that
the correlation ID is the SDK span's trace ID under the real import
order. AC-001 through AC-004 now carry the concrete test references
above; AC-005/AC-006/AC-008 (Phase 5) and AC-007 (Phase 6) remain
outstanding, so `## Coverage` stays `partial`.

### 2026-09-21 05:45:00.000+02:00 - Aligned AC-007/AC-008 wording to the post-exploration re-evaluation

AC-007's rewording clause and AC-008's error-counter tagging were
aligned to the feat-139-logging-telemetry post-exploration
re-evaluation: the per-method error-channel model verified against the
installed mcp 2.0.0 SDK (`tools/call` failures arrive as `isError`
results, not raised exceptions), and the Task 6.7 scope decision (the
deprecated ADR domain's title sites excluded from rewording as an
accepted residual gap; path sites scrub-covered). No implementation
exists yet; `## Coverage` stays `partial`.

### 2026-09-19 15:32:00.000+02:00 - Added AC-008 (metrics correctness) during a plan-consistency review

A plan-consistency review found that, despite REQ dacd01f4's central
metrics clause (tool-call latency/count, error-type counts, doc-cache
hit/miss rate, domain-lock wait time), this VCR had no acceptance
criterion actually verifying the metrics themselves are recorded with
correct values/attributes -- only span creation, degradation, naming,
sampling, and redaction were covered. Added AC-008, and clarified the
`mcp.item.type` attribute in AC-005's naming-scheme description to
match the same clarification added to REQ dacd01f4. Concrete test
references will be added in Phase 5 of
feat-139-logging-telemetry once the metrics instrumentation lands. No
implementation exists yet; `## Coverage` stays `partial`.

### 2026-09-19 14:22:00.000+02:00 - Added AC-007 (span redaction) during pre-implementation review

A pre-Phase-1 implementation-readiness review found that REQ dacd01f4's
span/metric-attribute redaction clause had no corresponding acceptance
criterion in this VCR's initial Phase 0 draft. Added AC-007, and
clarified in "Verifies" that redaction is part of what this VCR
confirms. No implementation exists yet; `## Coverage` stays `partial`.

### 2026-09-19 13:26:00.000+02:00 - Initial draft created (partial coverage)

Initial VCR authored immediately once REQ dacd01f4 was finalized, before
any implementation phase of feat-139-logging-telemetry started.
Acceptance criteria above are limited to what is directly derivable from
the requirement's specified configuration/behavior contract.
