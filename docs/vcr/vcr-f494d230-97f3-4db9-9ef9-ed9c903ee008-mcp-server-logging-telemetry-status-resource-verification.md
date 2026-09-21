---
classification: null
created: '2026-09-19 13:19:31.013+02:00'
id: f494d230-97f3-4db9-9ef9-ed9c903ee008
status: draft
type: vcr
updated: '2026-09-21 14:02:50.232+02:00'
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

full

## Acceptance Criteria

### AC-001 (Test): Status resource returns a list of strings

Reading the status resource returns a `list[str]`, with entries
reporting whether logging and telemetry are each currently enabled and
in what mode. Verified by `tests/general/resources/test_telemetry_status.py::TestTelemetryStatusResource::test_returns_a_list_of_strings` and `tests/general/resources/test_telemetry_status.py::TestTelemetryStatusResource::test_default_config_reports_both_disabled`.

### AC-002 (Demonstration): Status resource matches actual configuration

With `SPECMGR_LOG_ENABLED=true` and `SPECMGR_OTEL_ENABLED=false`, the
status resource's returned list reports logging enabled and telemetry
disabled; changing the environment variables and restarting the server
changes the reported values accordingly. Verified by `tests/general/resources/test_telemetry_status.py::TestTelemetryStatusResource::test_logging_enabled_telemetry_disabled_reports_mode` (the scenario above), `tests/general/resources/test_telemetry_status.py::TestTelemetryStatusResource::test_logging_enabled_with_all_modes_reports_them`, `tests/general/resources/test_telemetry_status.py::TestTelemetryStatusResource::test_telemetry_enabled_reports_the_exporter`, and `tests/general/resources/test_telemetry_status.py::TestTelemetryStatusResource::test_a_changed_environment_changes_the_reported_values`.

## More Information

Coverage is `full`: the resource is implemented at
`specmgr://telemetry/status` (registered from `general/resources/
telemetry_status.py`, feat-139-logging-telemetry Phase 1, Tasks 1.3/1.4)
and reports from the same parsed, fail-closed-validated config object
the server startup validates (`telemetry/config.py`, Tasks 1.1/1.6).
Both acceptance criteria carry their concrete test references above.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-21 14:01:05.541+02:00 - Phase 1 landed: resource implemented, AC-001/AC-002 verified, coverage moved to full

feat-139-logging-telemetry Phase 1 (Tasks 1.1-1.6) implemented the
resource at `specmgr://telemetry/status` as a two-line `list[str]`
(logging enablement plus level/format/file-sink mode; telemetry
enablement plus exporter), built from the same parsed config the
server-startup validation now enforces fail-closed at `specmgr mcp`
import time. AC-001/AC-002 gained the concrete test references above
and `## Coverage` moved from `partial` to `full`.

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
