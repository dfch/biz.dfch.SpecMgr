---
classification: null
created: '2026-09-19 13:18:34.380+02:00'
id: 0a1c2f63-9576-4463-bf40-8f771f14fefb
status: draft
type: vcr
updated: '2026-09-19 13:18:34.380+02:00'
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
channel.

#### Test Steps

1. Start `specmgr mcp` with no `SPECMGR_LOG_*` environment variables set.
2. Invoke any tool via an MCP client.
3. Confirm no log output is produced and stdout contains only JSON-RPC
   frames.

### AC-002 (Test): Every MCP item is logged, not tools only

With `SPECMGR_LOG_ENABLED=true`, invoking a tool, a resource, and a
prompt each produce a start and a completion (or error) log record,
tagged with a per-invocation correlation ID.

### AC-003 (Test): Log content is redacted

A log record includes the invoked item's `id` and `type` (and, for
`set_status`, the new status value), but never the full content of an
item, an absolute filesystem path, or a document/artifact title.

### AC-004 (Test): Correlation ID appears only in error responses

A failing tool call's error response includes a correlation ID; a
successful call's result never includes one.

### AC-005 (Test): File sink behaves as specified

With `SPECMGR_LOG_ENABLED=true` and the file-sink sub-switch enabled, a
log file at the configured path receives structured JSON records; with
the file sink left at its default (disabled), no such file is written;
the file sink always emits JSON, even when the console format is set to
`rich`.

## More Information

Coverage is `partial`: the Test Steps above describe intended,
specified behavior only, since no implementation exists yet. Concrete
test references (pytest test IDs) will be added, and `## Coverage` moved
to `full`, as each relevant phase of `feat-139-logging-telemetry` lands.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-19 13:25:00.000+02:00 - Initial draft created (partial coverage)

Initial VCR authored immediately once REQ bc356fc9 was finalized, before
any implementation phase of `feat-139-logging-telemetry` started.
Acceptance criteria above are limited to what is directly derivable from
the requirement's specified configuration/behavior contract.
