---
classification: null
created: '2026-09-19 13:17:07.823+02:00'
id: 41444084-6821-426d-84a2-028a3f4fed0b
status: draft
type: req
updated: '2026-09-19 13:17:07.823+02:00'
version: 1.0.0
---

# MCP Server Logging/Telemetry Status Resource

THE specmgr MCP server must expose a read-only resource that reports, as a
list of strings, whether structured logging and telemetry are each
currently enabled and in what mode.

## Description

`README.md` documentation of the logging/telemetry environment variables
(see REQ `bc356fc9-964a-4274-93ec-4627c5aeb2e5`'s and REQ
`dacd01f4-ffd8-4363-a20b-5ac1ce11eef2`'s acceptance criteria) tells an
operator how to configure logging and telemetry, but does not let an
already-running server confirm what is actually active without inspecting
its environment or restarting it under different settings.

This requirement covers a runtime-visible, queryable confirmation of the
current logging/telemetry state: a read-only resource returning a
`list[str]`, rather than a fixed-shape object, so that further status
lines can be added in the future without a breaking schema change.

## Characteristics

1. Interaction Capability

## Level

MUST

## Priority

50

## Tags

- Observability
- Status
- MCP Server
- Cross-Cutting

## Source

GitHub issue #139 ("Add telemetry and logging"); QA document
`40a17fb8-c069-4c38-a092-47912e1fa41d` ("Logging and Telemetry Requirements
Elicitation Interview"), Interaction Capability section.

## Related Artifacts

### Requirements

- REQ-bc356fc9-964a-4274-93ec-4627c5aeb2e5: MCP Server Structured Logging
- REQ-dacd01f4-ffd8-4363-a20b-5ac1ce11eef2: MCP Server Telemetry (Metrics
  and Tracing)

### Decisions

- ADR-fdbb6d22-278a-4ecf-b2f6-db208bc49fc6: Adopt stdlib logging and
  OpenTelemetry for SpecMgr logging and telemetry
