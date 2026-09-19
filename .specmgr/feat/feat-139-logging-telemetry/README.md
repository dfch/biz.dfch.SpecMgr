---
classification: null
created: '2026-09-19 12:24:35.775+02:00'
id: feat-139-logging-telemetry
status: planning
type: feat
updated: '2026-09-19 13:26:46.221+02:00'
version: 1.0.0
---

# Feature: Logging and Telemetry for the SpecMgr MCP Server

## Plan

### Overview

Add opt-in structured logging and OpenTelemetry-based telemetry (metrics + tracing) to the specmgr MCP server, serving both local development debugging and production/operator observability, without ever writing to stdout under the default `stdio` transport. This formalizes GitHub issue #139 ("Add telemetry and logging") through the standard doc-driven pipeline: QA `40a17fb8-c069-4c38-a092-47912e1fa41d` (elicitation) -> REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` (logging), REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` (telemetry), and REQ `41444084-6821-426d-84a2-028a3f4fed0b` (status resource) -> ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` (technology decision: stdlib `logging` + OpenTelemetry API/SDK, wired through a single `ServerMiddleware` appended to `mcp.middleware`) -> this feature folder. A second elicitation round refined the two original REQs (every MCP item, not tools only; id/type-only logging; an opt-in file sink; correlation ID on error responses only; MCP-specific metric naming; fail-open on a broken SDK middleware contract) and produced the third REQ. Per that same round's answer, three initial, partial-coverage VCRs (one per REQ, since a VCR's `## Verifies` is single-valued) were authored immediately in Phase 0 below, ahead of any implementation, and are extended phase-by-phase rather than written after the fact -- see `.specmgr/conventions.md`'s "Verification Case Records (VCR) -- Author Early, Extend as Implementation Lands" section for the general convention this follows.

### Requirements

- REQ-001: REQ-bc356fc9-964a-4274-93ec-4627c5aeb2e5 (MCP Server Structured Logging) -- opt-in, correlation-ID-tagged, dual rich/JSON format logging of every MCP tool/resource/prompt invocation, never touching stdout.
- REQ-002: REQ-dacd01f4-ffd8-4363-a20b-5ac1ce11eef2 (MCP Server Telemetry (Metrics and Tracing)) -- opt-in tool-call latency/count/error metrics, doc-cache hit/miss rate, domain-lock wait time, and one distributed trace span per MCP tool/resource/prompt invocation correlated with the logging correlation ID.
- REQ-003: REQ-41444084-6821-426d-84a2-028a3f4fed0b (MCP Server Logging/Telemetry Status Resource) -- a read-only resource reporting current logging/telemetry enablement state as an extensible `list[str]`.

### Acceptance Criteria

- [ ] ACC-001: With both logging and telemetry left at their defaults (no `SPECMGR_LOG_*`/`SPECMGR_OTEL_*` env vars set), running `specmgr mcp` emits zero log records and zero telemetry, and writes nothing to stdout beyond the JSON-RPC channel.
- [ ] ACC-002: With `SPECMGR_LOG_ENABLED=true`, every MCP tool, resource, or prompt invocation produces a start, completion (or error) log record on stderr, tagged with a per-invocation correlation ID, in the format selected by `SPECMGR_LOG_FORMAT` (`rich` or `json`).
- [ ] ACC-003: With `SPECMGR_OTEL_ENABLED=true`, every MCP tool, resource, or prompt invocation produces one trace span, and metrics are recorded for tool-call latency, tool-call counts by tool, error counts by exception type, the `feat-107` doc-cache hit/miss rate, and per-domain lock wait time; the correlation ID from ACC-002 matches the span's trace/span ID.
- [ ] ACC-004: No log record or span attribute, under any configuration, ever contains a full document body, an absolute filesystem path, or a document/artifact title.
- [ ] ACC-005: `README.md` documents every new `SPECMGR_LOG_*`/`SPECMGR_OTEL_*` environment variable, its default, and how to enable logging/telemetry for local development vs. production.
- [ ] ACC-006: The standard pre-commit/CI quality gate (`ruff format`, `ruff check`, `vulture`, `pytest`, docs regen) passes after every phase below.
- [ ] ACC-007: The status resource (REQ-003) returns a `list[str]` accurately reflecting whether logging and telemetry are each currently enabled, reflecting the actual configuration in effect.
- [ ] ACC-008: A failing MCP tool/resource/prompt call's error response includes a correlation ID; a successful call's result never includes one.
- [ ] ACC-009: The file log sink honors its own on/off and filename environment variables (active only when `SPECMGR_LOG_ENABLED=true`), and always emits structured JSON regardless of the console format setting.
- [ ] ACC-010: An unreachable OTLP endpoint, or a broken `Server.middleware` contract, never breaks a tool call; each condition logs at most one stderr message per failure episode, never repeating while the condition persists.

### Scope

#### Included

- A new top-level `src/biz/dfch/specmgr/telemetry/` package (config parsing, logging setup, the `ServerMiddleware` implementation, and the OpenTelemetry SDK bootstrap).
- Structured logging: dual rich (local dev) / JSON (production) format, gated by `SPECMGR_LOG_ENABLED`/`SPECMGR_LOG_LEVEL`/`SPECMGR_LOG_FORMAT`, covering every MCP tool, resource, and prompt invocation.
- An opt-in file log sink, off by default, its own on/off sub-switch layered under `SPECMGR_LOG_ENABLED`, its own configurable filename, always emitting structured JSON regardless of the console format setting.
- A per-tool-call correlation ID, generated once per invocation by the middleware, included in every related log record and, when telemetry is enabled, matching the active span's trace/span ID; included in a client-visible error response, but never in a successful result.
- OpenTelemetry metrics: tool-call latency histogram, tool-call counts by tool/domain, error counts by exception type, `feat-107` doc-cache hit/miss rate, and per-domain lock wait/contention time, named using an MCP-specific scheme (e.g. `mcp.tool.duration`, `mcp.tool.name`, `mcp.domain`) rather than the raw OpenTelemetry RPC semantic-convention names.
- OpenTelemetry tracing: one span per tool/resource/prompt invocation, activating the MCP SDK's existing built-in `OpenTelemetryMiddleware`, with always-on (100%) sampling and no sample-rate configuration.
- A read-only status resource (REQ-003) returning a `list[str]` reporting current logging/telemetry enablement state.
- A redaction safeguard preventing full document bodies, absolute filesystem paths, and document/artifact titles from reaching any log record or span/metric attribute.
- Graceful, fail-open degradation: an unreachable OTLP endpoint or a broken `Server.middleware` contract never breaks a tool call, and never spams stderr.
- Three initial, partial-coverage VCRs (one per REQ above), authored in Phase 0, extended phase-by-phase as implementation lands.
- `README.md` documentation of every new environment variable.

#### Explicitly Out Of Scope

- Propagating the correlation ID any further than a client-visible error response (e.g. into successful results, or into the MCP SDK's per-tool `Context` object).
- Any change to the existing exception-raising error-handling convention (`XNotFoundError`, `DeleteError`, ...); logging/telemetry observes these, it does not replace them.
- Building a dashboard, alerting rules, or any specific backend deployment (Grafana/Prometheus/Jaeger/etc.) -- only the exporter configuration surface (`console`/`otlp`) is in scope.
- A configurable trace sample rate -- always-on (100%) sampling is accepted for this feature; revisit only if real-world overhead becomes a problem.
- The deferred ADR `3bf0326f-065a-424c-a2b9-87e5d5bcfa99` MCP-singleton extraction into its own module -- this feature instruments `mcp` where it is constructed today in `server.py`.

### Dependencies

#### Depends On

- ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` (technology decision, already accepted).
- The three initial VCRs authored in Phase 0 (`0a1c2f63-9576-4463-bf40-8f771f14fefb` logging, `54fd355f-0978-4dd0-9e1d-da89432e5321` telemetry, `f494d230-97f3-4db9-9ef9-ed9c903ee008` status resource), each starting at `## Coverage: partial` and extended by the Task List below.

#### Blocks

- None currently -- the VCRs are authored within this feature's own Phase 0 and Task List, not tracked as a separate follow-up.

### Design Notes

- **Package location**: new top-level `telemetry/` package (not a document domain, so it does not fit the domain-first `<domain>/tools` convention; mirrors `models/` as shared infrastructure). Proposed modules: `telemetry/config.py` (env var parsing), `telemetry/logging.py` (formatter + setup, building on `mcp.server.mcpserver.utilities.logging.configure_logging`), `telemetry/middleware.py` (the `ServerMiddleware` implementation: correlation ID, latency timing, call/error counters, correlation-ID-on-error attachment), `telemetry/otel.py` (OpenTelemetry SDK bootstrap: `TracerProvider`/`MeterProvider` + exporter, fail-open handling), `telemetry/redact.py` (the body/path/title redaction safeguard).
- **Environment variables** (all default to "disabled"/safe, following the existing `SPECMGR_*_DIR` naming convention): `SPECMGR_LOG_ENABLED` (`true`/`false`, default `false`); `SPECMGR_LOG_LEVEL` (default `INFO`); `SPECMGR_LOG_FORMAT` (`rich`\|`json`, default `rich`); `SPECMGR_LOG_FILE_ENABLED` (`true`/`false`, default `false`, only takes effect when `SPECMGR_LOG_ENABLED=true`); `SPECMGR_LOG_FILE_PATH` (file path for the JSON-only file sink, required only when the file sink is enabled); `SPECMGR_OTEL_ENABLED` (`true`/`false`, default `false`); `SPECMGR_OTEL_EXPORTER` (`console`\|`otlp`, default `console`); `SPECMGR_OTEL_ENDPOINT` (OTLP endpoint URL, only used when exporter is `otlp`).
- **Tool-call instrumentation mechanism**: a single `ServerMiddleware` appended to `mcp.middleware` in `server.py`, right where `mcp = MCPServer(...)` is constructed -- no edits to any of the ~100+ existing `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` functions (confirmed feasible via research into the installed `mcp==2.0.0` SDK: `Server.middleware` is a live, appendable list, and the SDK's own built-in `OpenTelemetryMiddleware` in `mcp/server/_otel.py` is a ready-made template for span creation, exception tagging, and `error.type` recording).
- **Metric/span naming scheme**: MCP-specific names (`mcp.tool.duration`, `mcp.tool.call.count`, `mcp.tool.error.count`, `mcp.cache.hit`/`mcp.cache.miss`, `mcp.lock.wait_time`, with attributes `mcp.tool.name`/`mcp.domain`) rather than the literal OpenTelemetry RPC semantic-convention names (e.g. `rpc.server.duration`), since MCP has no registered `rpc.system` value and resource/prompt calls do not map cleanly onto RPC semantics; follows the spirit (structured names, standard units, histogram buckets), not the letter, of the OTel semantic conventions.
- **Correlation ID exposure**: generated once per invocation by the middleware; included in every related log record and, when telemetry is enabled, tied to the active span's trace/span ID; included in a client-visible error response so an operator/agent can quote it back for log lookup, but never included in a successful result.
- **Fail-open policy**: both the OTLP-exporter-unreachable case and a broken `Server.middleware` contract (a future SDK upgrade) must never break a tool call -- the server keeps operating normally, logging/telemetry disable themselves (fully or partially) with at most one stderr warning per failure episode, and a further single message is only emitted after a subsequent reconnect-then-drop cycle, never repeating while the condition persists.
- **Doc-cache hit/miss counters**: add counters directly to the shared `general/tools/_doc_cache.py`'s `DocCache` class (instruments all 12 per-domain caches at once) plus a `stats()` accessor the OTel meter reads.
- **Domain-lock wait time**: instrument each of the 13 `<domain>/tools/_lock.py` files' `_lock_for`/`<domain>_lock` context manager individually (no shared chokepoint exists today -- mirrors the `feat-99-list-item` "one shared helper, many wiring sites" precedent).
- **Redaction**: a logging `Filter`/span-attribute processor that strips known-sensitive fields (document body content, absolute filesystem paths, document/artifact titles) before a record/span is emitted; unit-tested directly.
- **Status resource**: a read-only MCP resource (candidate URI `specmgr://telemetry/status`) returning a `list[str]` describing current logging/telemetry enablement state, reading the same parsed config as the middleware; since `telemetry/` is shared infrastructure rather than a document domain, register it from a small `general/resources/` module (mirroring the existing `specmgr://version` precedent) rather than inventing a new domain-first location.
- **VCR maintenance**: each of Phases 2 through 6 below ends with a task extending the relevant initial VCR(s) (created in Phase 0) with concrete test references for whatever acceptance criteria that phase just made verifiable, per `.specmgr/conventions.md`'s VCR-early convention; Phase 9 confirms every VCR has reached `## Coverage: full`.
- **Risk flagged in the ADR**: `Server.middleware` is documented as a provisional API in the installed SDK ("signature and semantics change ... before v2 final") -- Phase 4 adds a dedicated compatibility test asserting the fail-open behavior above, so a breaking SDK change is caught loudly (via the test) while the running server itself degrades quietly (via the fail-open policy).

### Related Decisions

- ADR fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and OpenTelemetry for SpecMgr logging and telemetry.

### Task List

#### Phase 0: Requirements finalization and initial verification records

- [x] Task 0.1: Reword REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` (Logging) per the second elicitation round: every MCP item, id/type-only logging (`set_status` includes the actual status), opt-in file sink, redaction extended to titles, correlation ID on error responses only.
- [x] Task 0.2: Reword REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` (Telemetry) per the same round: every MCP item, fail-open on a broken `Server.middleware` contract, graceful OTLP-unreachable degradation, always-on sampling, MCP-specific metric/span naming.
- [x] Task 0.3: Create REQ `41444084-6821-426d-84a2-028a3f4fed0b` (MCP Server Logging/Telemetry Status Resource), cross-linked to the two REQs above.
- [x] Task 0.4: Finalize QA `40a17fb8-c069-4c38-a092-47912e1fa41d`: formalize the second round's raw answers into prose, and answer the four previously-pending questions (trace sampling, `Server.middleware`, correlation-ID/`ctx` exposure, `rpc.server.duration` naming impact).
- [x] Task 0.5: Author three initial, partial-coverage VCRs, one per REQ above (`0a1c2f63-9576-4463-bf40-8f771f14fefb` logging, `54fd355f-0978-4dd0-9e1d-da89432e5321` telemetry, `f494d230-97f3-4db9-9ef9-ed9c903ee008` status resource), each populated only with acceptance criteria genuinely derivable from its REQ's specified configuration/behavior contract.
- [x] Task 0.6: Add the "author VCR early, extend phase-by-phase" convention to `.specmgr/conventions.md`, generalizing this phase's approach for future features.

#### Phase 1: Config surface and status resource

- [ ] Task 1.1: Add `telemetry/config.py` parsing the eight env vars above (including the two file-sink vars) into a typed, validated config object, all defaulting to disabled.
- [ ] Task 1.2: Unit tests for config parsing (defaults, valid/invalid values).
- [ ] Task 1.3: Add a read-only status resource (candidate URI `specmgr://telemetry/status`) returning `list[str]`, reporting current logging/telemetry enablement state per REQ `41444084-6821-426d-84a2-028a3f4fed0b`; unit tests.
- [ ] Task 1.4: Extend VCR `f494d230-97f3-4db9-9ef9-ed9c903ee008` (status resource) with concrete test references for AC-001/AC-002; move `## Coverage` to `full` once both are demonstrably covered.
- [ ] Task 1.5: Quality gate (ruff, vulture, pytest).

#### Phase 2: Structured logging

- [ ] Task 2.1: Add `telemetry/logging.py`: a JSON `Formatter` and a setup function building on the MCP SDK's `configure_logging`/rich handler, selected by `SPECMGR_LOG_FORMAT`, gated by `SPECMGR_LOG_ENABLED`, plus the opt-in JSON-only file sink gated by `SPECMGR_LOG_FILE_ENABLED`/`SPECMGR_LOG_FILE_PATH`.
- [ ] Task 2.2: Unit tests asserting stdout is never written to, in either format, that the JSON formatter produces valid, parseable JSON, and that the file sink is JSON-only and inactive unless both its own switch and the main logging switch are enabled.
- [ ] Task 2.3: Extend VCR `0a1c2f63-9576-4463-bf40-8f771f14fefb` (logging) with concrete test references for AC-001/AC-005 now that this phase makes them demonstrable; keep `## Coverage: partial` if other criteria remain outstanding.
- [ ] Task 2.4: Quality gate.

#### Phase 3: Correlation ID + call middleware

- [ ] Task 3.1: Add `telemetry/middleware.py`'s `ServerMiddleware` implementation: generate a correlation ID per request, log start/completion/error, increment call/error counters.
- [ ] Task 3.2: Append the middleware to `mcp.middleware` in `server.py`.
- [ ] Task 3.3: Attach the correlation ID to a client-visible error response only, never to a successful result.
- [ ] Task 3.4: Unit tests exercising the middleware directly against a fake `call_next`, covering the success and exception paths, and asserting the correlation-ID-on-error-only behavior for tools, resources, and prompts alike.
- [ ] Task 3.5: Extend VCR `0a1c2f63-9576-4463-bf40-8f771f14fefb` (logging) with concrete test references for AC-002/AC-004; keep `## Coverage: partial` if other criteria remain outstanding.
- [ ] Task 3.6: Quality gate.

#### Phase 4: OpenTelemetry SDK bootstrap

- [ ] Task 4.1: Add `telemetry/otel.py`: configure `TracerProvider`/`MeterProvider` + exporter (`console`/`otlp`) only when `SPECMGR_OTEL_ENABLED`; this activates the SDK's existing built-in `OpenTelemetryMiddleware`.
- [ ] Task 4.2: Tie the correlation ID from Phase 3 to the active span's trace/span ID.
- [ ] Task 4.3: Implement the fail-open policy: if the installed SDK's `Server.middleware` contract is incompatible with this feature's middleware, log a single warning and continue operating with logging/telemetry disabled, rather than failing to start.
- [ ] Task 4.4: Compatibility test guarding against a breaking change to the installed SDK's provisional `Server.middleware` contract, asserting the fail-open behavior from Task 4.3.
- [ ] Task 4.5: Extend VCR `54fd355f-0978-4dd0-9e1d-da89432e5321` (telemetry) with concrete test references for AC-001/AC-004; keep `## Coverage: partial` if other criteria remain outstanding.
- [ ] Task 4.6: Quality gate.

#### Phase 5: Metrics instrumentation

- [ ] Task 5.1: Tool-call latency histogram + call counters by tool/domain, in the middleware, via an OTel `Meter` (no-op when disabled), named per the MCP-specific scheme (`mcp.tool.duration`, `mcp.tool.name`, `mcp.domain`).
- [ ] Task 5.2: Error-type counter (`type(exc).__qualname__`).
- [ ] Task 5.3: Add hit/miss counters + a `stats()` accessor to the shared `DocCache` class; wire a meter callback reading them.
- [ ] Task 5.4: Add wait-time timing to each of the 13 `<domain>/tools/_lock.py` files' lock context manager, recorded to the same meter.
- [ ] Task 5.5: Implement graceful OTLP-unreachable degradation: at most one stderr message per failure episode, a further single message only after a subsequent reconnect-then-drop cycle, never spamming.
- [ ] Task 5.6: Unit tests for each counter/histogram and for the OTLP-unreachable degradation behavior.
- [ ] Task 5.7: Extend VCR `54fd355f-0978-4dd0-9e1d-da89432e5321` (telemetry) with concrete test references for AC-003/AC-005/AC-006; move `## Coverage` to `full` if every telemetry AC is now demonstrably covered.
- [ ] Task 5.8: Quality gate.

#### Phase 6: Redaction safeguards

- [ ] Task 6.1: Add `telemetry/redact.py`: a logging filter and a span-attribute processor stripping document body content, absolute filesystem paths, and document/artifact titles.
- [ ] Task 6.2: Wire the filter/processor into both the logging and OTel setup from Phases 2 and 4.
- [ ] Task 6.3: Unit tests asserting redaction on representative payloads, including titles.
- [ ] Task 6.4: Extend VCR `0a1c2f63-9576-4463-bf40-8f771f14fefb` (logging) with a concrete test reference for AC-003; move `## Coverage` to `full` if every logging AC is now demonstrably covered.
- [ ] Task 6.5: Quality gate.

#### Phase 7: Packaging

- [ ] Task 7.1: Add `opentelemetry-sdk` (+ an OTLP exporter package, if needed for Task 4.1) to `pyproject.toml`, most likely under the existing `mcp` extra.
- [ ] Task 7.2: Regenerate `uv.lock`.
- [ ] Task 7.3: Quality gate.

#### Phase 8: Documentation

- [ ] Task 8.1: Add a "Logging and Telemetry" section to `README.md` documenting every new environment variable (including the file-sink pair), its default, the status resource, and local-dev vs. production usage examples.
- [ ] Task 8.2: Regenerate `docs/GENERATED.md` (`specmgr docs`) and update `AGENTS.md`'s Status section with a short bullet for the new `telemetry/` package.
- [ ] Task 8.3: Quality gate.

#### Phase 9: Final verification

- [ ] Task 9.1: Run the full acceptance-criteria checklist above (ACC-001..010) end to end.
- [ ] Task 9.2: Full pre-commit/CI quality gate.
- [ ] Task 9.3: Confirm all three VCRs (`0a1c2f63-9576-4463-bf40-8f771f14fefb`, `54fd355f-0978-4dd0-9e1d-da89432e5321`, `f494d230-97f3-4db9-9ef9-ed9c903ee008`) have reached `## Coverage: full`; for any acceptance criterion that still cannot be demonstrated, resolve it or explicitly document why before closing the feature.

## Progress

### Current Status

**As of 2026-09-19**: Planning and Phase 0 complete. QA `40a17fb8-c069-4c38-a092-47912e1fa41d` has been through two elicitation rounds and is fully answered. REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5`, REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2`, REQ `41444084-6821-426d-84a2-028a3f4fed0b`, and ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` are all created/updated and cross-linked. Three initial, partial-coverage VCRs (one per REQ) are authored. No implementation has started yet (Phase 1 not started).

### Blockers

None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-19 13:30:00.000Z - Phase 0 complete: REQs finalized, third REQ added, three initial VCRs authored

A second elicitation round on QA `40a17fb8-c069-4c38-a092-47912e1fa41d` resolved six follow-up questions raised during a review pass (VCR timing, functional-suitability scope, performance-efficiency overhead/sampling, compatibility middleware behavior, interaction-capability status signal, reliability degradation/file-sink, security title redaction/correlation-ID exposure, maintainability naming/switch granularity), including four that required an explanation before the stakeholder could decide (trace sampling, `Server.middleware`, correlation-ID/`ctx` exposure advantage, `rpc.server.duration` naming impact). REQ `bc356fc9...`/`dacd01f4...` were reworded to broaden scope to every MCP item, add id/type-only logging, an opt-in file sink, title redaction, correlation-ID-on-error-only, MCP-specific metric naming, and fail-open behavior on OTLP/middleware failures. A new REQ `41444084-6821-426d-84a2-028a3f4fed0b` (status resource, Interaction Capability) was created. Per the stakeholder's explicit instruction, three initial, partial-coverage VCRs (one per REQ, since a VCR's `## Verifies` is single-valued) were authored immediately rather than deferred until after implementation, and the general "author VCR early, extend phase-by-phase" practice was added to `.specmgr/conventions.md` so it applies to future features too.

#### 2026-09-19 12:30:00.000Z - Planning pipeline completed

Ran the full QA -> REQ -> ADR -> feature-folder pipeline recommended by the GitHub issue #139 planning comment. Elicited stakeholder answers via the `question` tool (logging: stdlib `logging` + MCP SDK rich handler; telemetry: OpenTelemetry API+SDK; dual rich/JSON log format; both features fully opt-in/off by default; redact document bodies and absolute paths; correlation ID tied to OTel span; five telemetry signals of interest). The stakeholder later decided two separate REQ documents (logging, telemetry) were wanted instead of one combined REQ, so REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` and REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` were created and cross-referenced, while a single ADR (`fdbb6d22-278a-4ecf-b2f6-db208bc49fc6`) still covers the combined technology decision. Research during planning (via a dedicated explore sub-task) confirmed the concrete, no-per-tool-edit implementation mechanism: the installed `mcp==2.0.0` SDK's `Server.middleware` list, appendable on the single `mcp = MCPServer(...)` instance in `server.py`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-19 13:29:00.000Z - Author VCR early, extend phase-by-phase; not after implementation

Per the stakeholder's explicit instruction, VCRs for this feature's REQs are authored as soon as the REQs are finalized (Phase 0), scoped to whatever is genuinely verifiable from each REQ's specified contract alone (`## Coverage: partial`), and are then extended -- not rewritten -- at the end of each implementation phase that makes further criteria concretely verifiable. This avoids both a purely ceremonial post-implementation VCR (describing whatever got built) and a purely aspirational pre-implementation one (never updated once code exists); it also surfaces a design/implementation deviation immediately, at the cheapest point to fix it. This practice is generalized into `.specmgr/conventions.md` for future features, not left as a one-off decision scoped to this feature alone.

#### 2026-09-19 13:28:00.000Z - Third REQ split out for the status resource

The stakeholder's Interaction Capability answer (a status resource returning `list[str]`) does not fit either existing REQ's characteristics (Maintainability/Security/Compatibility for logging; Performance Efficiency/Reliability/Compatibility for telemetry), so it was split into its own REQ (`41444084-6821-426d-84a2-028a3f4fed0b`, Interaction Capability), mirroring the earlier "two REQs, one ADR" split decision below.

#### 2026-09-19 12:29:00.000Z - Two REQs, one ADR

The stakeholder chose to split the formal requirement into two REQ documents (logging vs. telemetry) to reflect that these are two distinct requirements, while keeping a single ADR since only one technology decision (the combined stdlib-logging + OpenTelemetry stack) is being made.

#### 2026-09-19 12:28:00.000Z - stdlib logging + OpenTelemetry, both opt-in/off by default

See ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` for the full rationale: stdlib `logging` (dual rich/JSON format) plus OpenTelemetry API/SDK for metrics and tracing, wired through a single `ServerMiddleware`, both features fully opt-in and off by default.

### Related PRs / Commits

### More Information

Traceability chain: QA `40a17fb8-c069-4c38-a092-47912e1fa41d` -> REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5` / REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` / REQ `41444084-6821-426d-84a2-028a3f4fed0b` -> ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` -> VCR `0a1c2f63-9576-4463-bf40-8f771f14fefb` / VCR `54fd355f-0978-4dd0-9e1d-da89432e5321` / VCR `f494d230-97f3-4db9-9ef9-ed9c903ee008` -> this feature folder. GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/139.
