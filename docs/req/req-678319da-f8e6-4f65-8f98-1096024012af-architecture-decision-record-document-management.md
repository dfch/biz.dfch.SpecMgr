---
classification: null
created: '2026-09-03 10:26:29.090+02:00'
id: 678319da-f8e6-4f65-8f98-1096024012af
status: draft
type: req
updated: '2026-09-03 10:26:29.090+02:00'
version: 1.0.0
---

# Architecture Decision Record Document Management

THE system shall provide Architecture Decision Record (ADR) document management, including create, read, update-frontmatter, update-section, option management, status-change, and validate operations for MADR-style decision records with a Context/Decision Drivers/Considered Options/Decision Outcome/Pros-and-Cons-of-the-Options structure.

## Description

AGENTS.md's Status section documents the `adr` package as the original, most complete domain: 11 `@mcp.tool()` wrappers (`get_adr`, `list_adr`, `create_adr`, `update_frontmatter`, `update_section`, the five `option_*` tools, and `validate_adr`), with status changes going through the generic `set_status` tool (`type="adr"`). Although ADR is deprecated in favor of `dec` for new decisions, all 28 existing ADR documents on disk remain `status: accepted` and continue to be managed through these tools.

## Characteristics

1. Functional Suitability

## Level

MUST

## Source

AGENTS.md's Status section (the `adr` bullet) and `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md`.

## Related Artifacts

### Goals

- GOL-08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
