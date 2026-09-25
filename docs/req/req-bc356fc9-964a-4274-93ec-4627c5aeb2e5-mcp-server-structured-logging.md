---
classification: null
created: '2026-09-19 12:17:37.574+02:00'
id: bc356fc9-964a-4274-93ec-4627c5aeb2e5
status: draft
type: req
updated: '2026-09-19 16:08:34.238+02:00'
version: 1.0.0
---

# MCP Server Structured Logging

WHERE structured logging is enabled by configuration, THE specmgr MCP
server must record the start, completion, and any error of each MCP tool,
resource, or prompt invocation, tagged with a per-invocation correlation
ID, without writing any output to standard output.

## Description

specmgr's default transport is `stdio`, which reserves standard output for
the JSON-RPC channel; any logging output on that channel would corrupt the
protocol stream. Today no logging exists anywhere in `src/`: error handling
is 100% raised typed exceptions, never log statements, which makes local
development debugging and production/operator diagnosis equally difficult.

This requirement covers structured, correlation-ID-tagged logging of every
MCP tool call, resource read, and prompt invocation (start, completion,
error) -- not tool invocations only, and not every other JSON-RPC method a
single shared server-side instrumentation point may also observe (e.g.
capability negotiation or listing operations), which this requirement does
not require logging for -- configurable between a human-readable format
for local development and a structured JSON format for production/operator
log ingestion, entirely opt-in and off by default.

A log record may include an invoked item's `id` and `type`, and, where the
call itself reports a changed value (e.g. `set_status`), the new value.
This requirement's own logging code must never itself construct a log
record field that carries the full content of an item (e.g. a document
body), an absolute filesystem path, or a document/artifact title as a
dedicated value. Free-text content reaching a log record (e.g. an
exception's message) is additionally passed through a best-effort scrub
for absolute-filesystem-path-shaped substrings; a document/artifact title
embedded in free text has no comparable detectable shape, so an exception
message already known to embed one is instead reworded at its source to
omit that content, rather than relied on to be caught by a generic filter.
The per-invocation correlation ID may be included in an error response
returned to the MCP client, but must never appear in a successful result.

In addition to the console/stderr sink, an opt-in file sink is supported:
off by default, enabled only as a sub-switch under the main logging enable
switch, with its own filename configurable via a dedicated environment
variable, and always emitting the structured JSON format regardless of the
console format setting.

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
Elicitation Interview"), Functional Suitability/Reliability/Security/
Maintainability/Compatibility sections.

## Related Artifacts

### Requirements

- REQ-dacd01f4-ffd8-4363-a20b-5ac1ce11eef2: MCP Server Telemetry (Metrics
  and Tracing)
- REQ-41444084-6821-426d-84a2-028a3f4fed0b: MCP Server Logging/Telemetry
  Status Resource

### Decisions

- ADR-fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and
  OpenTelemetry for SpecMgr logging and telemetry
