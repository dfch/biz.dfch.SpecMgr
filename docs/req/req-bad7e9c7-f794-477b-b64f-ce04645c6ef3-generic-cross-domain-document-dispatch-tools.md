---
classification: null
created: '2026-09-03 10:27:53.793+02:00'
id: bad7e9c7-f794-477b-b64f-ce04645c6ef3
status: draft
type: req
updated: '2026-09-03 10:27:53.793+02:00'
version: 1.0.0
---

# Generic Cross-Domain Document Dispatch Tools

THE system shall provide generic, type-dispatched `update`, `set_status`, `set_classification`, and `delete` tools that operate uniformly across every whole-body document domain, so that adding a new document type requires only one dispatch entry per generic tool, not new per-domain `update_<d>`/`set_status_<d>`/`set_classification_<d>`/`delete_<d>` tools.

## Description

AGENTS.md's Status section documents the cross-cutting `general` package: the generic `update` tool (whole-body and line-range replace for the twelve whole-body domains), `set_status` (all thirteen domains including `adr`), `set_classification`, and `delete`, plus `mdformat` and shared resources (`specmgr://version`, `specmgr://iso25010`, `specmgr://dtais`, `specmgr://rasci`). ADR 36905d5b-8057-4294-8665-c7eed5534db0 fixes this as the required convention for every future domain (e.g. the reserved but not-yet-built `ac` domain), reducing per-domain tool duplication and the maintenance burden of the codebase as a whole.

## Characteristics

1. Maintainability

## Level

MUST

## Source

AGENTS.md's Status section (the `general` bullet) and ADR 36905d5b-8057-4294-8665-c7eed5534db0.

## Related Artifacts

### Goals

- GOL-b663528e-08c5-426b-9f20-32192c0a3bdb: Cross-Referenceable, Non-Duplicating Specification Artifacts
