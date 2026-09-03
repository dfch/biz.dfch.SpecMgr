---
classification: null
created: '2026-09-03 10:25:14.254+02:00'
id: b663528e-08c5-426b-9f20-32192c0a3bdb
status: draft
type: gol
updated: '2026-09-03 10:25:14.254+02:00'
version: 1.0.0
---

# Cross-Referenceable, Non-Duplicating Specification Artifacts

THE project shall keep every specification artifact type schema-validated and addressable by a stable id, so that higher-level documents such as a System Requirements Specification can aggregate existing goal, problem-statement, question-and-answer, use-case, requirement, risk, decision, and verification artifacts by cross-reference rather than by duplicating their content.

## Description

AGENTS.md describes the domain-first architecture underlying every document-type package: each domain owns its own schema, and cross-cutting generic tools (`update`/`set_status`/`set_classification`/`delete`) operate uniformly across domains instead of duplicating per-domain logic. The `sysrs` domain package (feat-32-sysrs) is built specifically around this idea: its sections accept only type-tagged cross-reference bullets (e.g. `GOL <uuid>: <title>`, `REQ <uuid>: <title>`) pointing at existing documents, never inline copies of their content. This goal states the underlying design intent that makes that aggregation possible in the first place.

## Source

AGENTS.md's description of the domain-first architecture (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and the `sysrs` domain's cross-reference-only design (`.specmgr/feat/feat-32-sysrs/README.md`).

## Notes

Captured retrospectively during feat-84-specmgr-sysrs (GitHub issue #84) while drafting this repository's own System Requirements Specification.
