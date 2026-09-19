---
classification: null
created: '2026-09-19 12:16:45.563+02:00'
id: 40a17fb8-c069-4c38-a092-47912e1fa41d
status: draft
type: qa
updated: '2026-09-19 13:20:31.172+02:00'
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

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> The feature plan defers drafting a Verification Case Record (VCR) for the
> two REQs produced here "until acceptance criteria are implementable/
> testable against real code." Should that VCR be drafted immediately after
> Phase 9 of `feat-139-logging-telemetry` completes, or tracked separately
> (e.g. its own follow-up issue), so it does not silently fall off?

The VCR must be authored as soon as the requirements are fully defined --
immediately following this elicitation round, not deferred until after
implementation. Each initial VCR is scoped to whatever acceptance criteria
are genuinely verifiable from its requirement's specified
configuration/behavior contract alone, marked `## Coverage: partial`, and
is then extended (not rewritten) at the end of each subsequent
implementation phase as further criteria become concretely verifiable,
reaching `## Coverage: full` once the requirement is demonstrably covered.
Authoring a VCR only after implementation risks describing whatever was
built rather than independently re-deriving criteria from the requirement;
authoring it early and extending it phase by phase surfaces any deviation
between the intended design and the actual implementation immediately, at
the phase boundary where it is cheapest to address.

## Functional Suitability

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> The ADR and feature plan assume the logging/telemetry middleware
> instruments every `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()`
> call, but both REQs' statements speak only of "tool invocation". Should
> resources and prompts be covered too, or should the REQs be narrowed to
> tools only?

Every MCP item -- tools, resources, and prompts alike -- must be
instrumented, not tool invocations only; both REQs are reworded
accordingly to speak of an "MCP tool, resource, or prompt invocation"
rather than a "tool invocation".

> Should tool-call arguments (e.g. an `id`, a `type`) be included in log
> lines / span attributes for debugging, or should only call metadata
> (tool name, duration, outcome) be recorded?

Yes -- an item's `id` and `type` are included in log lines/span
attributes, but never the full content of an item (e.g. a document body).
Where a call's own purpose is to report a changed value the operator would
want to see (e.g. `set_status`), the actual new value (the status string)
is included as well, since it is metadata about the call, not document
content.

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

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> Is there a maximum acceptable overhead (percentage added latency, or an
> absolute time budget per call) when telemetry is enabled?

No fixed overhead budget is defined. Enabling telemetry inherently adds
some overhead -- that is intrinsic to what OpenTelemetry instrumentation
does -- and an a-priori percentage or absolute time budget would be
arbitrary and unenforceable in practice. The added overhead is accepted as
a known, deliberate trade-off of turning telemetry on; it is not treated
as a requirement to be verified against a numeric threshold.

> Should trace sampling be configurable (e.g. a sample-rate environment
> variable), or is always-on (100%) sampling acceptable given expected call
> volumes?

Trace sampling is the decision of which invocations actually produce an
exported trace versus being dropped, used to control telemetry data
volume/overhead on high-throughput services; a 100% ("always-on") sample
rate exports a trace for every call, while a fractional rate (e.g. 10%)
exports only a statistical subset. Given specmgr's expected call volumes
(a low-QPS, largely local MCP server, not a high-throughput web service),
always-on sampling is accepted for this feature: no sample-rate
configuration is introduced. This can be revisited later if real-world
overhead turns out to be a problem.

## Compatibility

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Are there transport-specific (`stdio` vs `sse`) logging/telemetry
> behavior differences to account for, beyond the constraint that `stdio`
> reserves stdout for JSON-RPC?

No additional transport-specific behavior is required beyond the existing
constraint: under `stdio` transport, log and telemetry output must never
touch stdout (stderr, a file, or an OTLP exporter only); no differing
behavior was requested for `sse` transport.

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> `Server.middleware` is flagged in the ADR as a provisional SDK API. If a
> future `mcp` SDK upgrade changes or removes it, should logging/telemetry
> silently disable themselves with a warning, or should the server fail to
> start?

`Server.middleware` is the MCP SDK's own middleware chain on its `Server`
object: a list of wrappers around every tool/resource/prompt call
(comparable to ASGI/Express-style middleware), each receiving a
`call_next` continuation so it can run code before/after the call, inspect
or modify the request/response, or catch exceptions. The SDK already
carries one built-in, currently inert `OpenTelemetryMiddleware` in that
list; this feature appends its own middleware to the same list, giving one
interception point for logging, correlation-ID generation, and metrics
without touching any of the ~100+ existing tool functions. Since a future
SDK upgrade could change this provisional API's contract: if that happens,
logging/telemetry must disable themselves with a single warning and let
the server keep running normally -- fail open, not fail closed --
consistent with the general rule that an observability failure must never
break a tool call.

## Interaction Capability

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> Beyond documenting configuration in `README.md` (ACC-005), do you want
> any runtime-visible signal -- e.g. a startup log line, or an MCP resource
> -- confirming whether logging/telemetry are currently enabled and in what
> mode?

Yes -- add a dedicated read-only MCP resource reporting whether
logging/telemetry are currently enabled and in what mode. It must return a
`list[str]` (rather than a single value or a rigid object), so the set of
reported items can grow in the future without a breaking shape change.

## Reliability

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Do you want a correlation/request ID per MCP tool call, included in every
> related log line?

Yes -- a correlation ID per tool call, tied to the OpenTelemetry trace/span
ID when telemetry is enabled, so an operator can jump from a log line
straight to the corresponding trace.

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> If the OTLP exporter endpoint is unreachable, or a configured log file
> sink is unwritable, must the server keep operating normally (a
> logging/telemetry failure must never break a tool call), or is silent
> best-effort degradation acceptable?

If the server cannot reach the configured OTLP endpoint, it must not stop
any MCP client-side functionality -- tool calls keep working normally. A
single stderr log message recording the failure is acceptable, but the
failure must not be logged repeatedly ("spamming" stderr) for as long as
the endpoint remains unreachable. Only after a reconnect-then-drop cycle
(i.e. the endpoint recovers and then fails again) is a further, single
message acceptable.

> The raw issue text names "a file" as an allowed sink alongside stderr and
> an OTLP exporter, but the current implementation plan only wires up
> console/OTLP exporters plus rich/JSON output to stderr. Is file-based log
> output still required for this feature, or can it be dropped from scope?

File-based log output is still required. It is off by default, and its
own on/off state is controlled by a dedicated environment variable,
layered under (only ever active when) structured logging as a whole is
enabled. The log file's path/name is also configurable via its own
environment variable. The file sink always emits the structured JSON
format, never the human-readable format, regardless of the console/stderr
format setting.

## Security

<!-- Elicited 2026-09-19 via the `question` tool. -->

> What must never appear in logs/telemetry?

Full document bodies/content and absolute filesystem paths must never be
logged or attached to spans. Beyond that, no further restriction applies:
document ids, titles, and other metadata are not considered sensitive
(literal secrets/credentials were never in scope for this server to begin
with).

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> Document titles are free text a user or agent writes and could contain
> project-confidential wording. Is the OTLP/log export target assumed to be
> self-hosted/internal only, or should titles also be treated as
> sensitive/redacted?

Document/artifact titles can also be sensitive (they are free text a user
or agent writes and may contain project-confidential wording); they must
not appear in logs or telemetry either, extending the redaction rule above
beyond body content and absolute filesystem paths.

> Should the correlation ID be safe to expose to MCP clients (e.g. surfaced
> in error messages), or should it be treated purely as an internal/
> operator-only identifier?

Exposing the correlation ID to the client lets an operator or agent quote
it back after a failed call, so the exact server-side call can be located
in logs/traces without correlating purely by timestamp. It does not
require threading anything through the MCP SDK's per-tool `Context` object
(`ctx`) that individual tool handlers receive -- the middleware operates
at the transport layer and can attach the ID to the outgoing response
independently of what any given tool does with its own `ctx`. Weighing the
(low-sensitivity, non-secret) exposure against the diagnostic benefit: the
correlation ID is included in error responses only, never in successful
results.

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

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> Should metric and span names follow OpenTelemetry semantic conventions
> (e.g. `rpc.server.duration`) for compatibility with existing
> dashboards/tooling, or is a specmgr-specific naming scheme acceptable?

OpenTelemetry's RPC semantic conventions define `rpc.server.duration`
together with required attributes (`rpc.system`, `rpc.service`,
`rpc.method`, ...) for classic RPC systems such as gRPC or HTTP. MCP has
no registered `rpc.system` value, and resource/prompt calls do not map
cleanly onto "RPC" semantics either, so adopting the literal `rpc.*` names
risks a future clash with an eventual official MCP semantic convention
that names things differently. The chosen approach follows the spirit of
OpenTelemetry's conventions (structured names, standard units, histogram
buckets) using MCP-specific names instead of the raw `rpc.*` namespace --
e.g. `mcp.tool.duration`, with attributes such as `mcp.tool.name` and
`mcp.domain`.

> Should logging and telemetry stay controlled by one enable switch each,
> or do you want finer-grained control (e.g. metrics without tracing)?

One enable switch each for logging and telemetry, not per-signal toggles
-- with the exception already agreed for the file log sink, which has its
own separate on/off switch layered under (only effective when) the main
logging switch is enabled.

## Flexibility

<!-- Elicited 2026-09-19 via the `question` tool. -->

> Should logging/telemetry be on by default or require explicit opt-in?

Both logging and telemetry are fully opt-in and off by default; nothing is
emitted unless the operator explicitly enables it via an environment
variable.

## Safety

<!-- Follow-up question raised 2026-09-19 during a QA review pass; resolved in a second review pass the same day. -->

> Confirming: is Safety considered not applicable to this feature (no
> safety-critical implications), or is there a safety concern (e.g.
> audit-trail completeness) that should be captured here?

Safety is not applicable to this feature; there are no safety-critical
implications, and no audit-trail-completeness concern is being tracked
here.

## More Information

Formal requirements distilled from this interview: REQ
`bc356fc9-964a-4274-93ec-4627c5aeb2e5` ("MCP Server Structured Logging"),
REQ `dacd01f4-ffd8-4363-a20b-5ac1ce11eef2` ("MCP Server Telemetry (Metrics
and Tracing)"), and REQ `41444084-6821-426d-84a2-028a3f4fed0b` ("MCP
Server Logging/Telemetry Status Resource", added after a follow-up
Interaction Capability answer). The architecture decision resolving the
"standard components" question: ADR `fdbb6d22-278a-4ecf-b2f6-db208bc49fc6`
("Adopt stdlib logging and OpenTelemetry for SpecMgr logging and
telemetry"). Initial, partial-coverage verification case records authored
immediately after these requirements were finalized, per this interview's
own "author VCR early" answer: VCR `0a1c2f63-9576-4463-bf40-8f771f14fefb`
(logging), VCR `54fd355f-0978-4dd0-9e1d-da89432e5321` (telemetry), and VCR
`f494d230-97f3-4db9-9ef9-ed9c903ee008` (status resource). See the feature
folder `.specmgr/feat/feat-139-logging-telemetry/README.md` for the full
implementation plan.
