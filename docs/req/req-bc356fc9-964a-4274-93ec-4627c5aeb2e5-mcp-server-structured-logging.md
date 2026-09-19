---
classification: null
created: '2026-09-19 12:17:37.574+02:00'
id: bc356fc9-964a-4274-93ec-4627c5aeb2e5
status: draft
type: req
updated: '2026-09-19 12:18:54.412+02:00'
version: 1.0.0
---

# MCP Server Structured Logging

WHERE structured logging is enabled by configuration, THE specmgr MCP
server must record the start, completion, and any error of each tool
invocation, tagged with a per-invocation correlation ID, without writing
any output to standard output.

## Description

specmgr's default transport is `stdio`, which reserves standard output for
the JSON-RPC channel; any logging output on that channel would corrupt the
protocol stream. Today no logging exists anywhere in `src/`: error handling
is 100% raised typed exceptions, never log statements, which makes local
development debugging and production/operator diagnosis equally difficult.

This requirement covers structured, correlation-ID-tagged logging of tool
invocations (start, completion, error), configurable between a
human-readable format for local development and a structured JSON format
for production/operator log ingestion, entirely opt-in and off by default,
and never including full document body content or absolute filesystem
paths in any log record.

## Characteristics

1. Maintainability
2. Security
3. Compatibility

## Level

MUST

## Priority

50

## Tags

- Observability
- Logging
- MCP Server
- Cross-Cutting

## Source

GitHub issue #139 ("Add telemetry and logging"); QA document
`40a17fb8-c069-4c38-a092-47912e1fa41d` ("Logging and Telemetry Requirements
Elicitation Interview"), Maintainability/Security/Compatibility sections.

## Related Artifacts

### Requirements

- REQ-dacd01f4-ffd8-4363-a20b-5ac1ce11eef2: MCP Server Telemetry (Metrics
  and Tracing)

### Decisions

- ADR-fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and
  OpenTelemetry for SpecMgr logging and telemetry
