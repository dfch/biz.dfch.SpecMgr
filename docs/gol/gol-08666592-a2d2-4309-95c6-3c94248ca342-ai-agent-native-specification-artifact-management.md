---
classification: null
created: '2026-09-03 10:25:10.866+02:00'
id: 08666592-a2d2-4309-95c6-3c94248ca342
status: draft
type: gol
updated: '2026-09-03 10:25:10.866+02:00'
version: 1.0.0
---

# AI-Agent-Native Specification Artifact Management

THE project shall provide an MCP server that AI agents and other MCP clients can use to create, read, list, update, and validate structured specification artifacts across the full requirements-engineering document lifecycle, so that specification work stays machine-readable and consistently structured for the agents performing it.

## Description

The project's own README.md states its purpose as "An artifact manager for system specifications" and describes itself as "an MCP server that you can use to manage different specification artifacts", listing thirteen already-implemented artifact types (ADR, DEC, FEAT, GOL, PRB, QA, REQ, RSK, SOP, SYSRS, TSK, UC, VCR). AGENTS.md's Status section confirms each of these types is backed by its own schema-validated domain package exposing create/read/list/validate MCP tools. This goal captures that founding, organization-wide purpose, not any single domain package's behavior.

## Source

README.md ("An artifact manager for system specifications" / "This project is an MCP server that you can use to manage different specification artifacts") and AGENTS.md's Status section (the domain-package inventory).

## Notes

Captured retrospectively during feat-84-specmgr-sysrs (GitHub issue #84) while drafting this repository's own System Requirements Specification.
