---
classification: null
created: '2026-09-19 12:24:35.775+02:00'
id: feat-139-logging-telemetry
status: planning
type: feat
updated: '2026-09-19 12:24:35.775+02:00'
version: 1.0.0
---

# Feature: Logging and Telemetry for the SpecMgr MCP Server

## Plan

### Overview

Add opt-in structured logging and OpenTelemetry-based telemetry (metrics + tracing) to the specmgr MCP server, serving both local development debugging and production/operator observability, without ever writing to stdout under the default `stdio` transport. This formalizes GitHub issue #139 ("Add telemetry and logging") through the standard doc-driven pipeline: QA `40a17fb8-c069-4c38-a092-47912e1fa41d` (elicitation) -> REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` (logging) and REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` (telemetry) -> ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` (technology decision: stdlib `logging` + OpenTelemetry API/SDK, wired through a single `ServerMiddleware` appended to `mcp.middleware`) -> this feature folder.

### Requirements

- REQ-001: REQ-bc356fc9-964a-4274-93ec-4627c5aeb2e5 (MCP Server Structured Logging) -- opt-in, correlation-ID-tagged, dual rich/JSON format logging of tool invocations, never touching stdout.
- REQ-002: REQ-dacd01f4-ffd8-4363-a20b-5ac1ce11eef2 (MCP Server Telemetry (Metrics and Tracing)) -- opt-in tool-call latency/count/error metrics, doc-cache hit/miss rate, domain-lock wait time, and one distributed trace span per tool invocation correlated with the logging correlation ID.

### Acceptance Criteria

- [ ] ACC-001: With both logging and telemetry left at their defaults (no `SPECMGR_LOG_*`/`SPECMGR_OTEL_*` env vars set), running `specmgr mcp` emits zero log records and zero telemetry, and writes nothing to stdout beyond the JSON-RPC channel.
- [ ] ACC-002: With `SPECMGR_LOG_ENABLED=true`, every tool invocation produces a start, completion (or error) log record on stderr, tagged with a per-invocation correlation ID, in the format selected by `SPECMGR_LOG_FORMAT` (`rich` or `json`).
- [ ] ACC-003: With `SPECMGR_OTEL_ENABLED=true`, every tool invocation produces one trace span, and metrics are recorded for tool-call latency, tool-call counts by tool, error counts by exception type, the `feat-107` doc-cache hit/miss rate, and per-domain lock wait time; the correlation ID from ACC-002 matches the span's trace/span ID.
- [ ] ACC-004: No log record or span attribute, under any configuration, ever contains a full document body or an absolute filesystem path.
- [ ] ACC-005: `README.md` documents every new `SPECMGR_LOG_*`/`SPECMGR_OTEL_*` environment variable, its default, and how to enable logging/telemetry for local development vs. production.
- [ ] ACC-006: The standard pre-commit/CI quality gate (`ruff format`, `ruff check`, `vulture`, `pytest`, docs regen) passes after every phase below.

### Scope

#### Included

- A new top-level `src/biz/dfch/specmgr/telemetry/` package (config parsing, logging setup, the `ServerMiddleware` implementation, and the OpenTelemetry SDK bootstrap).
- Structured logging: dual rich (local dev) / JSON (production) format, gated by `SPECMGR_LOG_ENABLED`/`SPECMGR_LOG_LEVEL`/`SPECMGR_LOG_FORMAT`.
- A per-tool-call correlation ID, generated once per invocation by the middleware, included in every related log record and (when telemetry is enabled) matching the active span's trace/span ID.
- OpenTelemetry metrics: tool-call latency histogram, tool-call counts by tool/domain, error counts by exception type, `feat-107` doc-cache hit/miss rate, and per-domain lock wait/contention time.
- OpenTelemetry tracing: one span per tool/resource/prompt invocation, activating the MCP SDK's existing built-in `OpenTelemetryMiddleware`.
- A redaction safeguard preventing full document bodies and absolute filesystem paths from reaching any log record or span/metric attribute.
- `README.md` documentation of every new environment variable.

#### Explicitly Out Of Scope

- A VCR verification case record (deferred until acceptance criteria are implementable/testable against real code).
- Propagating correlation IDs to MCP clients beyond what the SDK's own request/response envelope already carries.
- Any change to the existing exception-raising error-handling convention (`XNotFoundError`, `DeleteError`, ...); logging/telemetry observes these, it does not replace them.
- Building a dashboard, alerting rules, or any specific backend deployment (Grafana/Prometheus/Jaeger/etc.) -- only the exporter configuration surface (`console`/`otlp`) is in scope.
- The deferred ADR `3bf0326f-065a-424c-a2b9-87e5d5bcfa99` MCP-singleton extraction into its own module -- this feature instruments `mcp` where it is constructed today in `server.py`.

### Dependencies

#### Depends On

- ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` (technology decision, already accepted).

#### Blocks

- A future VCR for the two REQs above.

### Design Notes

- **Package location**: new top-level `telemetry/` package (not a document domain, so it does not fit the domain-first `<domain>/tools` convention; mirrors `models/` as shared infrastructure). Proposed modules: `telemetry/config.py` (env var parsing), `telemetry/logging.py` (formatter + setup, building on `mcp.server.mcpserver.utilities.logging.configure_logging`), `telemetry/middleware.py` (the `ServerMiddleware` implementation: correlation ID, latency timing, call/error counters), `telemetry/otel.py` (OpenTelemetry SDK bootstrap: `TracerProvider`/`MeterProvider` + exporter), `telemetry/redact.py` (the body/path redaction safeguard).
- **Environment variables** (all default to "disabled"/safe, following the existing `SPECMGR_*_DIR` naming convention): `SPECMGR_LOG_ENABLED` (`true`/`false`, default `false`); `SPECMGR_LOG_LEVEL` (default `INFO`); `SPECMGR_LOG_FORMAT` (`rich`\|`json`, default `rich`); `SPECMGR_OTEL_ENABLED` (`true`/`false`, default `false`); `SPECMGR_OTEL_EXPORTER` (`console`\|`otlp`, default `console`); `SPECMGR_OTEL_ENDPOINT` (OTLP endpoint URL, only used when exporter is `otlp`).
- **Tool-call instrumentation mechanism**: a single `ServerMiddleware` appended to `mcp.middleware` in `server.py`, right where `mcp = MCPServer(...)` is constructed -- no edits to any of the ~100+ existing `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` functions (confirmed feasible via research into the installed `mcp==2.0.0` SDK: `Server.middleware` is a live, appendable list, and the SDK's own built-in `OpenTelemetryMiddleware` in `mcp/server/_otel.py` is a ready-made template for span creation, exception tagging, and `error.type` recording).
- **Doc-cache hit/miss counters**: add counters directly to the shared `general/tools/_doc_cache.py`'s `DocCache` class (instruments all 12 per-domain caches at once) plus a `stats()` accessor the OTel meter reads.
- **Domain-lock wait time**: instrument each of the 13 `<domain>/tools/_lock.py` files' `_lock_for`/`<domain>_lock` context manager individually (no shared chokepoint exists today -- mirrors the `feat-99-list-item` "one shared helper, many wiring sites" precedent).
- **Redaction**: a logging `Filter`/span-attribute processor that strips known-sensitive fields (document body content, absolute filesystem paths) before a record/span is emitted; unit-tested directly.
- **Risk flagged in the ADR**: `Server.middleware` is documented as a provisional API in the installed SDK ("signature and semantics change ... before v2 final") -- add a dedicated compatibility test that fails loudly if the SDK's middleware contract changes shape.

### Related Decisions

- ADR fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and OpenTelemetry for SpecMgr logging and telemetry.

### Task List

#### Phase 1: Config surface

- [ ] Task 1.1: Add `telemetry/config.py` parsing the six env vars above into a typed, validated config object, all defaulting to disabled.
- [ ] Task 1.2: Unit tests for config parsing (defaults, valid/invalid values).
- [ ] Task 1.3: Quality gate (ruff, vulture, pytest).

#### Phase 2: Structured logging

- [ ] Task 2.1: Add `telemetry/logging.py`: a JSON `Formatter` and a setup function building on the MCP SDK's `configure_logging`/rich handler, selected by `SPECMGR_LOG_FORMAT`, gated by `SPECMGR_LOG_ENABLED`.
- [ ] Task 2.2: Unit tests asserting stdout is never written to, in either format, and that the JSON formatter produces valid, parseable JSON.
- [ ] Task 2.3: Quality gate.

#### Phase 3: Correlation ID + call middleware

- [ ] Task 3.1: Add `telemetry/middleware.py`'s `ServerMiddleware` implementation: generate a correlation ID per request, log start/completion/error, increment call/error counters.
- [ ] Task 3.2: Append the middleware to `mcp.middleware` in `server.py`.
- [ ] Task 3.3: Unit tests exercising the middleware directly against a fake `call_next`, covering the success and exception paths.
- [ ] Task 3.4: Quality gate.

#### Phase 4: OpenTelemetry SDK bootstrap

- [ ] Task 4.1: Add `telemetry/otel.py`: configure `TracerProvider`/`MeterProvider` + exporter (`console`/`otlp`) only when `SPECMGR_OTEL_ENABLED`; this activates the SDK's existing built-in `OpenTelemetryMiddleware`.
- [ ] Task 4.2: Tie the correlation ID from Phase 3 to the active span's trace/span ID.
- [ ] Task 4.3: Compatibility test guarding against a breaking change to the installed SDK's provisional `Server.middleware` contract.
- [ ] Task 4.4: Quality gate.

#### Phase 5: Metrics instrumentation

- [ ] Task 5.1: Tool-call latency histogram + call counters by tool/domain, in the middleware, via an OTel `Meter` (no-op when disabled).
- [ ] Task 5.2: Error-type counter (`type(exc).__qualname__`).
- [ ] Task 5.3: Add hit/miss counters + a `stats()` accessor to the shared `DocCache` class; wire a meter callback reading them.
- [ ] Task 5.4: Add wait-time timing to each of the 13 `<domain>/tools/_lock.py` files' lock context manager, recorded to the same meter.
- [ ] Task 5.5: Unit tests for each counter/histogram.
- [ ] Task 5.6: Quality gate.

#### Phase 6: Redaction safeguards

- [ ] Task 6.1: Add `telemetry/redact.py`: a logging filter and a span-attribute processor stripping document body content and absolute filesystem paths.
- [ ] Task 6.2: Wire the filter/processor into both the logging and OTel setup from Phases 2 and 4.
- [ ] Task 6.3: Unit tests asserting redaction on representative payloads.
- [ ] Task 6.4: Quality gate.

#### Phase 7: Packaging

- [ ] Task 7.1: Add `opentelemetry-sdk` (+ an OTLP exporter package, if needed for Task 4.1) to `pyproject.toml`, most likely under the existing `mcp` extra.
- [ ] Task 7.2: Regenerate `uv.lock`.
- [ ] Task 7.3: Quality gate.

#### Phase 8: Documentation

- [ ] Task 8.1: Add a "Logging and Telemetry" section to `README.md` documenting every new environment variable, its default, and local-dev vs. production usage examples.
- [ ] Task 8.2: Regenerate `docs/GENERATED.md` (`specmgr docs`) and update `AGENTS.md`'s Status section with a short bullet for the new `telemetry/` package.
- [ ] Task 8.3: Quality gate.

#### Phase 9: Final verification

- [ ] Task 9.1: Run the full acceptance-criteria checklist above end to end.
- [ ] Task 9.2: Full pre-commit/CI quality gate.
- [ ] Task 9.3: Consider drafting a VCR for REQ-bc356fc9.../REQ-dacd01f4... once ACC-001..006 are demonstrably met.

## Progress

### Current Status

**As of 2026-09-19**: Planning complete. QA `40a17fb8-c069-4c38-a092-47912e1fa41d`, REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5`, REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2`, and ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` are all created and cross-linked. No implementation has started yet (Phase 1 not started).

### Blockers

None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-19 12:30:00.000Z - Planning pipeline completed

Ran the full QA -> REQ -> ADR -> feature-folder pipeline recommended by the GitHub issue #139 planning comment. Elicited stakeholder answers via the `question` tool (logging: stdlib `logging` + MCP SDK rich handler; telemetry: OpenTelemetry API+SDK; dual rich/JSON log format; both features fully opt-in/off by default; redact document bodies and absolute paths; correlation ID tied to OTel span; five telemetry signals of interest). The stakeholder later decided two separate REQ documents (logging, telemetry) were wanted instead of one combined REQ, so REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` and REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` were created and cross-referenced, while a single ADR (`fdbb6d22-278a-4ecf-b2f6-db208bc49fc6`) still covers the combined technology decision. Research during planning (via a dedicated explore sub-task) confirmed the concrete, no-per-tool-edit implementation mechanism: the installed `mcp==2.0.0` SDK's `Server.middleware` list, appendable on the single `mcp = MCPServer(...)` instance in `server.py`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-19 12:29:00.000Z - Two REQs, one ADR

The stakeholder chose to split the formal requirement into two REQ documents (logging vs. telemetry) to reflect that these are two distinct requirements, while keeping a single ADR since only one technology decision (the combined stdlib-logging + OpenTelemetry stack) is being made.

#### 2026-09-19 12:28:00.000Z - stdlib logging + OpenTelemetry, both opt-in/off by default

See ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` for the full rationale: stdlib `logging` (dual rich/JSON format) plus OpenTelemetry API/SDK for metrics and tracing, wired through a single `ServerMiddleware`, both features fully opt-in and off by default.

### Related PRs / Commits

### More Information

Traceability chain: QA `40a17fb8-c069-4c38-a092-47912e1fa41d` -> REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` / REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` -> ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` -> this feature folder. GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/139.
