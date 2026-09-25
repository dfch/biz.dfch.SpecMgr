---
status: accepted
date: '2026-09-19'
decision-makers: 'dfch (issue #139 owner), AI agent (feat-139-logging-telemetry session)'
consulted: 'GitHub issue #139 planning comment'
informed: REQ bc356fc9-964a-4274-93ec-4627c5aeb2e5, REQ dacd01f4-ffd8-4363-a20b-5ac1ce11eef2
id: fdbb6d22-278a-4ecf-b2f6-db208bc49fc6
version: 1.0.0
---

# Adopt stdlib logging and OpenTelemetry for SpecMgr logging and telemetry

## Context and Problem Statement

No logging or telemetry exists anywhere in `src/` today: error handling is 100% raised typed exceptions (`XNotFoundError`, `DeleteError`, ...), never log statements, and `feat-7-various-improvements/README.md` already flagged this as a deferred cross-cutting concern. GitHub issue #139 scopes the work as **logging + telemetry** (not logging-only), serving both local development debugging and production/operator observability, and deliberately leaves the choice of "standard components" open, to be resolved here.

The critical constraint is that specmgr's default transport is `stdio` (`specmgr mcp`), which reserves **stdout** for the JSON-RPC channel: any logging/telemetry output must go to stderr, a file, or an OTLP exporter, never stdout. The installed MCP SDK (`mcp>=2.0.0`) already ships a small stdlib-`logging` convenience helper (`mcp.server.mcpserver.utilities.logging.configure_logging`/`get_logger`, using a `RichHandler(stderr=True)` when `rich` is installed, confirmed stdout-safe) and already constructs its low-level `Server` with a built-in `OpenTelemetryMiddleware` in its `Server.middleware` list -- currently a no-op because no OpenTelemetry SDK/exporter is configured. `opentelemetry-api` is already an installed transitive dependency of the `mcp` package itself. `Server.middleware` is a live, appendable list on the single `MCPServer` instance constructed once in `server.py`, giving one integration point that can wrap every `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` call (correlation ID, latency, call/error counters) without editing any of the ~100+ existing tool/resource/prompt functions.

Requirements-elicitation interview (QA `40a17fb8-c069-4c38-a092-47912e1fa41d`) and the two requirements it produced (REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` for logging, REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` for telemetry) establish: both logging and telemetry must be fully opt-in and off by default; log format must be configurable between human-readable (local dev) and structured JSON (production); a correlation ID per tool call must tie a log line to its OpenTelemetry trace/span; full document bodies and absolute filesystem paths must never be logged or attached to spans; and telemetry signals of interest are tool-call latency, tool-call counts, error counts by exception type, the `feat-107` document-cache hit/miss rate, and per-domain lock wait time.

## Decision Drivers

- Must never write to stdout under the default `stdio` transport (JSON-RPC channel constraint).
- Must serve both local development debugging (human-readable) and production/operator observability (structured, exportable), per the issue's explicit scope.
- Must be fully opt-in and off by default (elicited stakeholder decision).
- Should minimize new required runtime dependencies -- `opentelemetry-api` is already an installed transitive dependency of `mcp`, and `rich` is already available via the existing `cli` extra.
- Should require zero edits to the ~100+ existing `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` definitions.
- Must never leak full document bodies or absolute filesystem paths into logs, spans, or metric attributes.
- Should let a correlation ID tie a log line to the corresponding distributed trace/span.

## Considered Options

1. stdlib `logging` (dual rich/JSON format, via the MCP SDK's own `configure_logging` helper) + OpenTelemetry API/SDK for metrics and tracing, wired through a single `ServerMiddleware` appended to `mcp.middleware`
2. `structlog` for logging + OpenTelemetry API/SDK for metrics and tracing
3. `loguru` for logging + custom, in-process lightweight counters for telemetry (no OpenTelemetry)
4. Logging only (stdlib `logging`), deferring all telemetry/metrics/tracing to a later, separate feature

## Decision Outcome

Chosen option: "stdlib `logging` + OpenTelemetry API/SDK, wired through a single `ServerMiddleware`", because it is the only option that satisfies every decision driver simultaneously: it adds no new logging dependency (stdlib + the already-available `rich`), it adds telemetry on top of a dependency (`opentelemetry-api`) already present transitively, it activates rather than replaces the MCP SDK's own dormant `OpenTelemetryMiddleware`, and the single `mcp.middleware` integration point instruments every current and future tool/resource/prompt call without touching any of their ~100+ individual definitions. `structlog` (Option 2) and `loguru` (Option 3) both add a new logging dependency for no corresponding decision-driver benefit over stdlib `logging` given the MCP SDK already provides a stdout-safe stdlib-based helper. Option 4 (logging only) directly contradicts the issue's explicit "logging + telemetry, not logging-only" scope decision.

### Consequences

- Good, because activates the MCP SDK's own built-in `OpenTelemetryMiddleware` (already present, currently inert) instead of building tracing from scratch.
- Good, because the single `mcp.middleware` extension point instruments every current and future `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` call site with zero per-tool edits.
- Good, because it adds only one genuinely new runtime dependency footprint (`opentelemetry-sdk` plus an exporter), since `opentelemetry-api` and `rich` are already present.
- Bad, because `Server.middleware` is documented in the installed SDK as a provisional API ("signature and semantics change with the Context/middleware rework... before v2 final"), so an SDK upgrade could require rework; mitigated by a dedicated compatibility test.
- Bad, because `opentelemetry-sdk` (and an exporter package) is still a new dependency to maintain, even though it is opt-in at runtime.
- Neutral, because per-domain instrumentation (the 13 `_lock.py` files' wait-time timing, and the shared `DocCache` hit/miss counters) still requires deliberate, hand-wired changes -- the middleware only covers the tool/resource/prompt call boundary, not internal domain-level chokepoints.

### Confirmation

Confirmed via: (1) unit tests asserting zero bytes are ever written to stdout under the default (both-features-disabled) configuration and under the `stdio` transport with both features enabled; (2) unit tests verifying a correlation ID is generated per tool call and, when telemetry is enabled, matches the active OpenTelemetry span's trace/span ID; (3) unit tests verifying the redaction safeguard strips document bodies and absolute filesystem paths from log records and span attributes; (4) the standard pre-commit/CI quality gate (`ruff`, `vulture`, `pytest`) passing on every implementation phase in `.specmgr/feat/feat-139-logging-telemetry/README.md`.

## Pros and Cons of the Options

### Option 1: stdlib logging + OpenTelemetry API/SDK via a single ServerMiddleware

Structured logging built on stdlib `logging`, dual-formatted (rich for local dev, JSON for production) via the MCP SDK's own `configure_logging` helper, plus OpenTelemetry API/SDK for metrics and tracing, both wired through one `ServerMiddleware` appended to `mcp.middleware`.

- Good, because zero new logging dependency: stdlib `logging` + already-available `rich`.
- Good, because `opentelemetry-api` is already an installed transitive dependency of `mcp`; only `opentelemetry-sdk` (+ exporter) is genuinely new.
- Good, because it activates the MCP SDK's own built-in, currently-inert `OpenTelemetryMiddleware` instead of duplicating tracing infrastructure.
- Good, because the single `mcp.middleware` integration point instruments every `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` call without editing any of the ~100+ individual definitions.
- Bad, because `Server.middleware` is a provisional SDK API, so a future SDK upgrade could require rework.

### Option 2: structlog + OpenTelemetry API/SDK

Structured logging built on `structlog` instead of stdlib `logging`, with OpenTelemetry API/SDK for metrics and tracing, still wired through the `mcp.middleware` extension point.

- Good, because `structlog` is purpose-built for structured (JSON) logging with strong ergonomics for that use case.
- Good, because still benefits from the already-installed `opentelemetry-api` and the SDK's dormant `OpenTelemetryMiddleware`, same as the chosen option.
- Bad, because it adds a new logging dependency for no decision-driver benefit over stdlib `logging`, given the MCP SDK already ships a stdout-safe, stdlib-based `configure_logging` helper.
- Bad, because it introduces a second logging idiom (`structlog` calls) alongside any stdlib `logging` calls other libraries (including the MCP SDK itself) already emit, complicating log correlation.

### Option 3: loguru + custom lightweight counters (no OpenTelemetry)

Logging built on `loguru`, with telemetry implemented as custom, in-process counters/timers (no OpenTelemetry, no distributed tracing).

- Good, because `loguru` has a very ergonomic API for local development.
- Good, because no new telemetry dependency at all.
- Bad, because it adds a new logging dependency that sits awkwardly next to the MCP SDK's own stdlib-based logging and its built-in `OpenTelemetryMiddleware`.
- Bad, because custom counters have no distributed tracing, no standard export format (Prometheus/OTLP/console), and duplicate work OpenTelemetry already solves -- while `opentelemetry-api` is already installed transitively regardless of this choice.
- Bad, because it cannot satisfy the elicited requirement to tie a correlation ID to a distributed trace/span, since no trace/span concept exists in this option.

### Option 4: Logging only, deferring telemetry to a later feature

Ship stdlib `logging` only in this feature; defer all metrics/tracing/telemetry work to a separate, later feature.

- Good, because smaller, faster-to-ship scope.
- Good, because still reuses the MCP SDK's stdout-safe `configure_logging` helper.
- Bad, because it directly contradicts GitHub issue #139's explicit scope decision: "logging + telemetry (not logging-only)".
- Bad, because it leaves the MCP SDK's built-in `OpenTelemetryMiddleware` permanently inert and defers activating an already-present dependency (`opentelemetry-api`) for no cost saving.

## More Information

Requirements: REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` ("MCP Server Structured Logging"), REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` ("MCP Server Telemetry (Metrics and Tracing)"). Elicitation: QA `40a17fb8-c069-4c38-a092-47912e1fa41d`. Implementation plan: `.specmgr/feat/feat-139-logging-telemetry/README.md`.
