---
classification: null
created: '2026-09-19 12:17:45.447+02:00'
id: dacd01f4-ffd8-4363-a20b-5ac1ce11eef2
status: draft
type: req
updated: '2026-09-19 14:32:47.209+02:00'
version: 1.0.0
---

# MCP Server Telemetry (Metrics and Tracing)

WHERE telemetry is enabled by configuration, THE specmgr MCP server must
emit tool-call latency, tool-call counts, error counts by exception type,
document-cache hit/miss rate, and domain-lock wait time as metrics, and
must correlate each MCP tool, resource, or prompt invocation with a
distributed trace, without writing any output to standard output.

## Description

The issue that opened this work explicitly scoped "logging + telemetry
(not logging-only)", serving both local development debugging and
production/operator observability. The installed MCP SDK (`mcp>=2.0.0`)
already carries `opentelemetry-api` as a transitive dependency and already
initializes its low-level server with a built-in (currently inert, because
unconfigured) `OpenTelemetryMiddleware`, so adopting OpenTelemetry as the
telemetry backbone has a low incremental dependency cost.

This requirement covers metrics (tool-call latency histogram, tool-call
counts by tool/domain, error counts by exception type, the `feat-107`
document-cache hit/miss rate, and per-domain lock wait/contention time) and
distributed tracing (one span per MCP tool, resource, or prompt invocation
-- not tool invocations only -- correlated with the structured-logging
correlation ID), entirely opt-in and off by default, and never attaching
full document body content, absolute filesystem paths, or document/
artifact titles to any span or metric attribute.

Metric and span names follow the spirit of OpenTelemetry's semantic
conventions (structured names, standard units, histogram buckets) using
MCP-specific names (e.g. `mcp.tool.duration`, attributes `mcp.tool.name`/
`mcp.domain`) rather than the literal RPC semantic-convention names (e.g.
`rpc.server.duration`), since MCP has no registered `rpc.system` value and
resource/prompt calls do not map cleanly onto RPC semantics. Every
metric/span additionally carries an `mcp.item.type` attribute
(`tool`/`resource`/`prompt`) alongside `mcp.tool.name`/`mcp.domain`, so a
resource or prompt invocation recorded under the `mcp.tool.*` metric
namespace is not mistaken for a literal tool call. Trace sampling is
always-on (100%); no sample-rate configuration is provided by this
requirement.

Telemetry must never break a tool call. If the configured OTLP exporter
endpoint is unreachable, the server keeps operating normally, and a single
stderr log message records the failure without repeating for as long as
the endpoint stays unreachable (a further single message is acceptable
only after a subsequent reconnect-then-drop cycle). If a future SDK
upgrade changes or removes the `Server.middleware` contract this
requirement's instrumentation depends on, logging and telemetry must
disable themselves with a single warning and let the server continue
operating normally, rather than failing to start.

## Characteristics

1. Performance Efficiency
2. Reliability
3. Compatibility

## Level

MUST

## Priority

50

## Tags

- Observability
- Telemetry
- OpenTelemetry
- MCP Server
- Cross-Cutting

## Source

GitHub issue #139 ("Add telemetry and logging"); QA document
`40a17fb8-c069-4c38-a092-47912e1fa41d` ("Logging and Telemetry Requirements
Elicitation Interview"), Functional Suitability/Performance Efficiency/
Compatibility/Reliability sections.

## Related Artifacts

### Requirements

- REQ-bc356fc9-964a-4274-93ec-4627c5aeb2e5: MCP Server Structured Logging
- REQ-41444084-6821-426d-84a2-028a3f4fed0b: MCP Server Logging/Telemetry
  Status Resource

### Decisions

- ADR-fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and
  OpenTelemetry for SpecMgr logging and telemetry
