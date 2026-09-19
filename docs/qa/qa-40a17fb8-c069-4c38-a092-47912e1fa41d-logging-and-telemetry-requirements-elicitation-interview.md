---
classification: null
created: '2026-09-19 12:16:45.563+02:00'
id: 40a17fb8-c069-4c38-a092-47912e1fa41d
status: draft
type: qa
updated: '2026-09-19 12:19:36.596+02:00'
version: 1.0.0
---

# Logging and Telemetry Requirements Elicitation Interview

## General

### Introduction

Interview held on 2026-09-19 for GitHub issue #139 ("Add telemetry and
logging"), between the issue owner (`dfch`) and the AI agent picking up the
issue on branch `feat-139-logging-telemetry`. The interview used the
`question` tool to resolve the open design points the issue's own planning
comment deliberately left open (choice of "standard components" is left to a
later ADR), so that formal REQ document(s) and an ADR can be drafted from
concrete answers rather than assumptions.

### Raw Requirements

From the GitHub issue #139 planning comment (2026-09-19):

> Add logging and telemetry to the specmgr MCP server, based on standard
> components. Scope agreed: logging + telemetry (not logging-only), serving
> both local dev debugging and production/operator observability. The choice
> of "standard components" (library/stack) is deliberately left open, to be
> resolved via ADR rather than assumed.
>
> Critical constraint: specmgr's default transport is `stdio`, which
> reserves stdout for the JSON-RPC channel. Any logging/telemetry output
> must go to stderr, a file, or an OTLP exporter -- never stdout.

No other pre-existing raw requirement notes (wiki pages, earlier documents)
existed for this topic before this interview.

## Elicitation Context

<!-- Elicited 2026-09-19 via the `question` tool during feat-139 planning, directly from the issue owner. -->

> This document formalizes decisions made through the `question` tool ahead
> of formal QA authoring. Each ISO/IEC 25010 category below records the
> actual question put to the stakeholder and their answer, mapped onto the
> category it is most relevant to.

The interview intentionally focused on the categories the issue's own
planning comment called out as relevant (Reliability, Performance
Efficiency, Maintainability, Security, Compatibility, Flexibility);
Functional Suitability, Interaction Capability, and Safety were not probed
and are left empty below.

## Functional Suitability

## Performance Efficiency

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Which approach should the ADR treat as the leading candidate for
> telemetry (metrics/traces: tool latency, call counts, error rates,
> feat-107 cache hit rate)?

OpenTelemetry API+SDK. `opentelemetry-api` is already an installed
transitive dependency (pulled in by the `mcp` package itself), so there is
low incremental cost; it is the industry-standard choice and can export to
Prometheus, OTLP, or the console.

> Which telemetry signals matter most?

All of: tool-call latency, tool-call counts by tool/domain, error counts by
exception type, `feat-107` doc-cache hit/miss rate, and domain lock
wait/contention time.

## Compatibility

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Are there transport-specific (`stdio` vs `sse`) logging/telemetry
> behavior differences to account for, beyond the constraint that `stdio`
> reserves stdout for JSON-RPC?

No additional transport-specific behavior is required beyond the existing
constraint: under `stdio` transport, log and telemetry output must never
touch stdout (stderr, a file, or an OTLP exporter only); no differing
behavior was requested for `sse` transport.

## Interaction Capability

## Reliability

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Do you want a correlation/request ID per MCP tool call, included in every
> related log line?

Yes -- a correlation ID per tool call, tied to the OpenTelemetry trace/span
ID when telemetry is enabled, so an operator can jump from a log line
straight to the corresponding trace.

## Security

<!-- Elicited 2026-09-19 via the `question` tool. -->

> What must never appear in logs/telemetry?

Full document bodies/content and absolute filesystem paths must never be
logged or attached to spans. Beyond that, no further restriction applies:
document ids, titles, and other metadata are not considered sensitive
(literal secrets/credentials were never in scope for this server to begin
with).

## Maintainability

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Which logging library/approach should the ADR treat as the leading
> candidate for structured application logging?

Standard library `logging`, using the MCP SDK's own
`configure_logging()`/rich handler (already confirmed stderr-safe),
extended with a custom formatter to support a structured JSON output mode
alongside the default human-readable (rich) mode.

> What log output format do you want?

Configurable: human-readable (rich) for local dev, structured JSON for
production/operator ingestion, selected via an environment variable,
following the existing `SPECMGR_*_DIR` naming convention. The stakeholder
explicitly asked that `README.md` be updated to document this
configuration.

## Flexibility

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Should logging/telemetry be on by default or require explicit opt-in?

Both logging and telemetry are fully opt-in and off by default; nothing is
emitted unless the operator explicitly enables it via an environment
variable.

## Safety

## More Information

Formal requirements distilled from this interview: REQ
`bc356fc9-964a-4274-93ec-4627c5aeb2e5` ("MCP Server Structured Logging")
and REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` ("MCP Server Telemetry
(Metrics and Tracing)"). The architecture decision resolving the "standard
components" question: ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6` ("Adopt
stdlib logging and OpenTelemetry for SpecMgr logging and telemetry"). See
the feature folder `.specmgr/feat/feat-139-logging-telemetry/README.md`
for the full implementation plan.
