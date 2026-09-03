---
classification: null
created: '2026-09-03 10:27:06.481+02:00'
id: 7c0e56e2-3fa5-437e-b886-1be32b142292
status: draft
type: req
updated: '2026-09-03 10:27:06.481+02:00'
version: 1.0.0
---

# Goal Document Management

THE system shall provide goal (GOL) document management, including create, read, list, and validate operations for high-level business goal documents that sit above individual requirements, whose body mirrors REQ minus the `## Characteristics` and `## Level` sections.

## Description

AGENTS.md's Status section documents the `gol` package's tools (`create_gol`, `parse_gol`, `list_gol`, `get_gol`, `get_gol_example`, `get_gol_template`, `validate_gol`), with `create_gol` first checking `list_gol` for a near-duplicate goal. See `.specmgr/feat/feat-18-goal/README.md` for the full body-shape rationale.

## Characteristics

1. Functional Suitability

## Level

MUST

## Source

AGENTS.md's Status section (the `gol` bullet) and `.specmgr/feat/feat-18-goal/README.md`.

## Related Artifacts

### Goals

- GOL-08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
