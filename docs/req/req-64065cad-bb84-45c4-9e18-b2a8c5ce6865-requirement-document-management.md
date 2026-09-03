---
classification: null
created: '2026-09-03 10:26:32.304+02:00'
id: 64065cad-bb84-45c4-9e18-b2a8c5ce6865
status: draft
type: req
updated: '2026-09-03 10:26:32.304+02:00'
version: 1.0.0
---

# Requirement Document Management

THE system shall provide requirement (REQ) document management, including create, read, list, and validate operations for individual requirement statements categorized by ISO/IEC 25010:2023 characteristic, RFC 2119 obligation level, priority, and related-artifact cross-references.

## Description

AGENTS.md's Status section documents the `req` package's tools (`create_req`, `parse_req`, `list_req`, `validate_req`), with whole-body/line-range updates, status changes, classification changes, and deletions dispatched through the generic `update`/`set_status`/`set_classification`/`delete` tools (`type="req"`). The `specmgr://req/schema` shows a REQ document's mandatory `## Characteristics` field must name at least one ISO/IEC 25010:2023 main characteristic.

## Characteristics

1. Functional Suitability

## Level

MUST

## Source

AGENTS.md's Status section (the `req` bullet) and `.specmgr/feat/feat-6-requirement-artifact/README.md`.

## Related Artifacts

### Goals

- GOL-08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
