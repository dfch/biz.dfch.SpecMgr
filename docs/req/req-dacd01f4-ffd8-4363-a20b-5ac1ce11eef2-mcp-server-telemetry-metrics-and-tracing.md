---
classification: null
created: '2026-09-19 12:17:45.447+02:00'
id: dacd01f4-ffd8-4363-a20b-5ac1ce11eef2
status: draft
type: req
updated: '2026-09-19 12:19:00.165+02:00'
version: 1.0.0
---

# MCP Server Telemetry (Metrics and Tracing)

WHERE telemetry is enabled by configuration, THE specmgr MCP server must
emit tool-call latency, tool-call counts, error counts by exception type,
document-cache hit/miss rate, and domain-lock wait time as metrics, and
must correlate each tool invocation with a distributed trace, without
writing any output to standard output.

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
distributed tracing (one span per tool invocation, correlated with the
structured-logging correlation ID), entirely opt-in and off by default, and
never attaching full document body content or absolute filesystem paths to
any span or metric attribute.

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
Elicitation Interview"), Performance Efficiency/Reliability/Compatibility
sections.

## Related Artifacts

### Requirements

- REQ-bc356fc9-964a-4274-93ec-4627c5aeb2e5: MCP Server Structured Logging

### Decisions

- ADR-fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and
  OpenTelemetry for SpecMgr logging and telemetry
