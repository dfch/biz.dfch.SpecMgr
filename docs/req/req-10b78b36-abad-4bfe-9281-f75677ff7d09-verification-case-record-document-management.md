---
classification: null
created: '2026-09-03 10:27:45.937+02:00'
id: 10b78b36-abad-4bfe-9281-f75677ff7d09
status: draft
type: req
updated: '2026-09-03 10:27:45.937+02:00'
version: 1.0.0
---

# Verification Case Record Document Management

THE system shall provide verification case record (VCR) document management, including create, read, list, and validate operations for DTAIS-classified acceptance criteria that record how a single requirement or use case is verified, so that a requirement's fulfillment can be objectively assessed and tested.

## Description

AGENTS.md's Status section documents the `vcr` package's tools (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`, `get_vcr_example`, `get_vcr_template`, `validate_vcr`). Each `### AC-NNN (Method): ...` entry uses a closed DTAIS vocabulary (Demonstration, Test, Analysis, Inspection, Special, documented by the cross-cutting `specmgr://dtais` resource) that lets an objective, feasible test be designed to determine whether a requirement is met -- the Testability sub-characteristic of Maintainability.

## Characteristics

1. Maintainability

## Level

MUST

## Source

AGENTS.md's Status section (the `vcr` bullet) and `.specmgr/feat/feat-33-vcr/README.md`.

## Related Artifacts

### Goals

- GOL-b663528e-08c5-426b-9f20-32192c0a3bdb: Cross-Referenceable, Non-Duplicating Specification Artifacts
