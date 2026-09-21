---
classification: null
created: '2026-09-19 13:19:31.013+02:00'
id: f494d230-97f3-4db9-9ef9-ed9c903ee008
status: draft
type: vcr
updated: '2026-09-21 06:27:21.340+02:00'
version: 1.0.0
---

# MCP Server Logging/Telemetry Status Resource Verification

## Verifies

<!-- Authored immediately after REQ 41444084 finalized, per the "author VCR early, extend phase-by-phase" convention (feat-139-logging-telemetry). -->

REQ 41444084-6821-426d-84a2-028a3f4fed0b: MCP Server Logging/Telemetry Status Resource

Confirms that a read-only resource reports the current
logging/telemetry enablement state as an extensible `list[str]`, as
specified by the requirement, ahead of feat-139-logging-telemetry's
implementation.

## Coverage

partial

## Acceptance Criteria

### AC-001 (Test): Status resource returns a list of strings

Reading the status resource returns a `list[str]`, with entries
reporting whether logging and telemetry are each currently enabled and
in what mode.

### AC-002 (Demonstration): Status resource matches actual configuration

With `SPECMGR_LOG_ENABLED=true` and `SPECMGR_OTEL_ENABLED=false`, the
status resource's returned list reports logging enabled and telemetry
disabled; changing the environment variables and restarting the server
changes the reported values accordingly.

## More Information

Coverage is `partial`: no implementation exists yet. The resource's
exact URI (`specmgr://telemetry/status`) and its `list[str]` entry
format were fixed by feat-139-logging-telemetry's post-exploration
re-evaluation (see that feature README's Design Notes, "Status
resource"). Concrete test references will be added, and `## Coverage`
moved to `full`, once the resource is implemented in
feat-139-logging-telemetry.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-21 05:45:00.000+02:00 - URI and entry format fixed by the post-exploration re-evaluation

The feat-139-logging-telemetry post-exploration re-evaluation fixed
the resource's exact URI (`specmgr://telemetry/status`) and its
`list[str]` entry format (enablement plus mode per line, e.g.
`logging: enabled (level=INFO, format=rich, file=disabled)` /
`telemetry: disabled`), registered from a new
`general/resources/telemetry_status.py` module. AC-001/AC-002 are
unchanged in substance. No implementation exists yet; `## Coverage`
stays `partial`.

### 2026-09-19 13:27:00.000+02:00 - Initial draft created (partial coverage)

Initial VCR authored immediately once REQ 41444084 was finalized,
before any implementation phase of feat-139-logging-telemetry started.
