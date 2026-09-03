---
classification: null
created: '2026-09-03 10:27:42.023+02:00'
id: 3bbe6a0e-038c-4abb-987c-79d4db8abd51
status: draft
type: req
updated: '2026-09-03 10:27:42.023+02:00'
version: 1.0.0
---

# Standard Operating Procedure Document Management

THE system shall provide Standard Operating Procedure (SOP) document management, including create, read, list, and validate operations for structured, step-by-step operational documents with a RASCI-style responsibility assignment and a closed approval/effectivity lifecycle, built dispatch-only on the generic `update`/`set_status`/`set_classification`/`delete` tools from day one instead of adding new per-domain tools.

## Description

AGENTS.md's Status section documents `sop` as the first domain built dispatch-only from day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0): it has no per-domain `update_sop`/`set_status_sop`/`set_classification_sop` tools at all, relying entirely on the generic dispatch tools with `type="sop"`. This reduces the number of tools that must be built, tested, and maintained as new domains are added, improving the system's overall modifiability and reducing duplicated logic across domains.

## Characteristics

1. Maintainability

## Level

MUST

## Source

AGENTS.md's Status section (the `sop` bullet) and ADR 36905d5b-8057-4294-8665-c7eed5534db0.

## Related Artifacts

### Goals

- GOL-b663528e-08c5-426b-9f20-32192c0a3bdb: Cross-Referenceable, Non-Duplicating Specification Artifacts
