---
classification: null
created: '2026-09-19 13:19:26.971+02:00'
id: 54fd355f-0978-4dd0-9e1d-da89432e5321
status: draft
type: vcr
updated: '2026-09-19 13:19:26.971+02:00'
version: 1.0.0
---

# MCP Server Telemetry Verification

## Verifies

<!-- Authored immediately after REQ dacd01f4 finalized, per the "author VCR early, extend phase-by-phase" convention (feat-139-logging-telemetry). -->

REQ dacd01f4-ffd8-4363-a20b-5ac1ce11eef2: MCP Server Telemetry (Metrics and Tracing)

Confirms that telemetry is fully opt-in, covers every MCP item (not
tools only), degrades gracefully when the OTLP endpoint or the
Server.middleware contract fails, and uses MCP-specific metric/span
names -- as specified by the requirement, ahead of
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

## More Information

Coverage is `partial`: AC-002 through AC-004 describe intended,
specified behavior only, since no implementation exists yet. Concrete
test references will be added, and `## Coverage` moved to `full`, as
each relevant phase of feat-139-logging-telemetry lands.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-19 13:26:00.000+02:00 - Initial draft created (partial coverage)

Initial VCR authored immediately once REQ dacd01f4 was finalized, before
any implementation phase of feat-139-logging-telemetry started.
Acceptance criteria above are limited to what is directly derivable from
the requirement's specified configuration/behavior contract.
