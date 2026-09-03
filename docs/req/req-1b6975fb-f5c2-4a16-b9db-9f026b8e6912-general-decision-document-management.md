---
classification: null
created: '2026-09-03 10:27:12.539+02:00'
id: 1b6975fb-f5c2-4a16-b9db-9f026b8e6912
status: draft
type: req
updated: '2026-09-03 10:27:12.539+02:00'
version: 1.0.0
---

# General Decision Document Management

THE system shall provide decision (DEC) document management, including create, read, list, and validate operations for MADR-style decisions that are not architecture-specific, built on the generic `models/md` parser with a simple, renderer-free surface.

## Description

AGENTS.md's Status section documents the `dec` package's tools (`parse_dec`, `get_dec`, `list_dec`, `get_dec_example`, `get_dec_template`, `create_dec`, `validate_dec`). A DEC keeps the ADR's general MADR-style structure (headings, `Options` collection) but has no fine-grained mutation tools or renderer: writes persist the caller's raw validated body byte-for-byte.

## Characteristics

1. Functional Suitability

## Level

MUST

## Source

AGENTS.md's Status section (the `dec` bullet) and `.specmgr/feat/feat-21-decision/README.md`.

## Related Artifacts

### Goals

- GOL-08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
