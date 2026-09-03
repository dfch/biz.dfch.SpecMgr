---
classification: null
created: '2026-09-03 10:27:15.700+02:00'
id: ccbf7ade-7d9e-4b2e-9868-0740bdc0e824
status: draft
type: req
updated: '2026-09-03 10:27:15.700+02:00'
version: 1.0.0
---

# Feature Folder Document Management

THE system shall provide feature (FEAT) document management, including create, read, list, and validate operations for the `.specmgr/feat/<id>/README.md` feature-folder convention, plus a dedicated `set_feat_id` tool for renaming a feature's chosen id after the fact.

## Description

AGENTS.md's Status section documents the `feat` package as the one domain whose addressing genuinely deviates from every other domain's precedent (ADR 8cf940c5-3100-485c-a12d-14b59b631712): `id` is a chosen `feat-NNN-slug`, the containing folder's own name, not a server-generated UUID, and documents live one-per-folder as `<base>/<id>/README.md`. This very feature (feat-84-specmgr-sysrs) is itself a FEAT document managed through these tools.

## Characteristics

1. Functional Suitability

## Level

MUST

## Source

AGENTS.md's Status section (the `feat` bullet) and `.specmgr/feat/feat-31-feature/README.md`.

## Related Artifacts

### Goals

- GOL-08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
