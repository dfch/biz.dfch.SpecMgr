---
created: '2026-11-01T00:00:00.000Z'
id: 356d8781-e446-4c26-917a-eda85648ce9d
status: accepted
type: dec
updated: '2026-11-01T00:00:00.000Z'
version: 1.0.0
---

# Regression fixture: Expose cross-cutting reference resources as raw markdown with model-backed drift-guard tests, not structured JSON (outcome of DEC 356d8781)

## Context and Problem Statement

This document is a committed regression fixture for feat-247-dec-outcome-blocks (GitHub issue #247): it carries the real `## Decision Outcome` outcome lead (the section from its H2 heading through the first `###` sub-section) of DEC 356d8781-e446-4c26-917a-eda85648ce9d verbatim inside a minimal-but-valid `dec` body, to prove that the relaxed `DecisionOutcome` lead (a mandatory paragraph plus zero or more further blocks) parses this outcome without "text left over".

## Decision Outcome

Adopt Option 1. Every reference resource -- the four existing raw-markdown ones (`dtais`, `tara`, `risk-matrix`, and `rasci` once it gains a model), the one existing JSON one (`iso25010`, switched to markdown), and the new `ears` -- returns raw markdown (`mime_type="text/markdown"`) and is backed by a dedicated internal Pydantic model. That model is parsed on every resource call purely to fail fast on structural drift at request time, with the parsed result discarded and the original raw text returned unchanged to the caller; it is additionally covered by its own dedicated `tests/models/test_*.py` drift-guard suite, replacing the ad hoc regex-based drift checks that previously lived inside `dtais`/`tara`/`risk-matrix`'s own resource test files. Model placement follows the existing domain-first precedent: cross-cutting models (`dtais`, `rasci`, `ears`) live in `general/models/`, alongside `general/models/paged_result.py`/`summary.py`; RSK-owned models (`tara`, `risk_matrix`) live in `rsk/models/v1/`, alongside `Strategy`/`level_from_product`. Closed-vocabulary bullet lists (DTAIS method words, TARA strategy words, EARS template keywords) are modeled as `MarkdownListItem` subclasses with a `@computed_field` regex-extracting the leading keyword, reusing `feat.RequirementItem`/`tsk.TaskItem`'s precedent rather than inventing a new shared `models/md` primitive. The visual 5x5 risk matrix table is deliberately left unmodeled (only its accompanying 4-item "Product thresholds" list is parsed), accepting a small residual drift risk on the table itself rather than adding a general-purpose markdown-table-parsing primitive to `models/md` for a single, narrow use.

Why Option 1 wins: the audience for every one of these resources is an LLM reading prose via a prompt instruction, not programmatic code indexing into a parsed structure, so returning structured JSON (Option 2) buys nothing for any actual caller while still paying JSON's schema-shape/serialization cost -- and for `iso25010` specifically, its current JSON shape is itself a breaking-change surface with no consumer to protect. Dropping validation down to ad hoc, resource-test-local regex assertions (Option 3) is strictly worse than a dedicated model: it scales badly (each resource reinvents its own checks), gives no reusable fail-fast guard at request time, and was already producing inconsistency (`iso25010` had a model, its siblings did not). Option 1 keeps the human/LLM-readable raw markdown every consumer actually wants, while still getting drift protection for free via the parse-and-discard pattern plus a dedicated, reusable model test -- unifying the two previously-inconsistent conventions (`iso25010`'s JSON vs. `dtais`/`tara`/`risk-matrix`'s raw-markdown-with-regex-tests) into the one pattern every future reference resource should now follow.

## Roles and Responsibilities

### Accountable

The platform architecture lead.

### Responsible

- The order service team.

## Source

Regression fixture derived from the `## Decision Outcome` section of DEC 356d8781-e446-4c26-917a-eda85648ce9d.
