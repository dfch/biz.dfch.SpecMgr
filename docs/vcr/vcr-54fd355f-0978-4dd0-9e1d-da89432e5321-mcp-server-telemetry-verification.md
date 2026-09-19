---
classification: null
created: '2026-09-19 13:19:26.971+02:00'
id: 54fd355f-0978-4dd0-9e1d-da89432e5321
status: draft
type: vcr
updated: '2026-09-19 14:03:20.479+02:00'
version: 1.0.0
---

# MCP Server Telemetry Verification

## Verifies

<!-- Authored immediately after REQ dacd01f4 finalized, per the "author VCR early, extend phase-by-phase" convention (feat-139-logging-telemetry). -->

REQ dacd01f4-ffd8-4363-a20b-5ac1ce11eef2: MCP Server Telemetry (Metrics and Tracing)

Confirms that telemetry is fully opt-in, covers every MCP item (not
tools only), degrades gracefully when the OTLP endpoint or the
Server.middleware contract fails, uses MCP-specific metric/span
names, and never attaches full document bodies, absolute filesystem
paths, or document/artifact titles to any span or metric attribute --
as specified by the requirement, ahead of
feat-139-logging-telemetry's implementation.

## Coverage

partial

## Acceptance Criteria

### AC-001 (Demonstration): Telemetry is off by default

With no `SPECMGR_OTEL_*` environment variables set, running `specmgr
mcp` emits zero telemetry and writes nothing to stdout beyond the
JSON-RPC channel.

### AC-002 (Test): Every MCP item produces a trace span

With `SPECMGR_OTEL_ENABLED=true`, invoking a tool, a resource, and a
prompt each produce one trace span, correlated with the logging
correlation ID.

### AC-003 (Test): An unreachable OTLP endpoint degrades gracefully

With `SPECMGR_OTEL_ENABLED=true` and the OTLP exporter pointed at an
unreachable endpoint, tool calls keep succeeding, exactly one stderr
message records the export failure, and the message does not repeat on
subsequent calls while the endpoint remains unreachable.

### AC-004 (Test): A broken Server.middleware contract fails open

If the installed SDK's Server.middleware contract is incompatible with
this feature's middleware, the server logs a single warning and
continues operating with logging/telemetry disabled, rather than
failing to start.

### AC-005 (Inspection): Metric/span names follow the MCP-specific naming scheme

A source review confirms metric/span names use the `mcp.*` namespace
(e.g. `mcp.tool.duration`, `mcp.tool.name`, `mcp.domain`), not the raw
OpenTelemetry `rpc.*` semantic-convention names.

### AC-006 (Analysis): Trace sampling is always-on

A review of the documented environment variables confirms no
`SPECMGR_OTEL_*` sample-rate configuration is exposed, consistent with
the accepted always-on-sampling decision.

### AC-007 (Test): Span content is redacted, including spans the SDK's own built-in middleware creates

With `SPECMGR_OTEL_ENABLED=true`, an error raised during a tool call
never results in an exported span whose attributes or exception event
contain a full document body, an absolute filesystem path, or a
document/artifact title -- even though the span itself is created by
the MCP SDK's own built-in `OpenTelemetryMiddleware`, not by this
feature's own middleware. A global, `TracerProvider`-level
`SpanProcessor` is required to satisfy this, since scoping redaction
to only this feature's own attributes would not reach that
SDK-created span.

## More Information

Coverage is `partial`: AC-002 through AC-004 and AC-007 describe
intended, specified behavior only, since no implementation exists yet.
AC-007 was added during a pre-Phase-1 implementation-readiness review
that identified it as a REQ dacd01f4 clause (span/metric-attribute
redaction) not yet covered by any acceptance criterion in this VCR's
initial Phase 0 draft -- see
`.specmgr/feat/feat-139-logging-telemetry/README.md`'s Decisions Made
log ("Redaction widened to a global SpanProcessor after a follow-up
clarification"). Concrete test references will be added, and
`## Coverage` moved to `full`, as each relevant phase of
feat-139-logging-telemetry lands (Phase 6 for AC-007 specifically).

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
