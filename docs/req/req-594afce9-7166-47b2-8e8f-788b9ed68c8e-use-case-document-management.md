---
classification: null
created: '2026-09-03 10:26:35.045+02:00'
id: 594afce9-7166-47b2-8e8f-788b9ed68c8e
status: draft
type: req
updated: '2026-09-03 10:26:35.045+02:00'
version: 1.0.0
---

# Use Case Document Management

THE system shall provide use case (UC) document management, including create, read, list, and validate operations for operational-scenario documents, with a `raw` read mode that returns the frontmatter-stripped body text unchanged for line-range editing.

## Description

AGENTS.md's Status section documents the `uc` package's tools (`create_uc`, `parse_uc`, `list_uc`, `get_uc`, `get_uc_example`, `get_uc_template`, `validate_uc`), mirroring `req`'s shape. Its schema exists in two versions, `uc/models/v1/` (legacy) and `uc/models/v2/` (current), both inside the domain package rather than under top-level `models/`.

## Characteristics

1. Functional Suitability

## Level

MUST

## Source

AGENTS.md's Status section (the `uc` bullet) and `.specmgr/feat/feat-4-use-cases/README.md`.

## Related Artifacts

### Goals

- GOL-08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
