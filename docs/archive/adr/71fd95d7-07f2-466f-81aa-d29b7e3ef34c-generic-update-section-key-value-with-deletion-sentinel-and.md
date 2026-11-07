---
status: accepted
decision-makers: dfch
id: 71fd95d7-07f2-466f-81aa-d29b7e3ef34c
version: 1.0.0
---

# Generic update_section(key, value) with deletion sentinel and mandatory-section rejection

## Context and Problem Statement

ADR body sections (title, context, decision drivers, outcome, consequences, etc.) must be independently editable. The question is how to structure the tool surface: should each section have its own dedicated tool, or should there be one generic tool that operates on any section key? Additionally, deletion semantics must be clear: how does a caller indicate they want to remove a section?

## Decision Drivers

Maintainability and consistency across the 7 body section types; clear deletion semantics that cannot be confused with other operations; prevent deletion of mandatory sections that would leave the ADR invalid.

## Considered Options

Per-field dedicated tools (update_title, update_context, update_drivers, etc.) vs. one generic keyed tool (update_section); silent drop on empty input vs. explicit deletion sentinel vs. separate delete tool; allow deleting mandatory sections vs. reject with error.

## Decision Outcome

Implement one generic `update_section(id, key, value)` tool for whole-section body edits. Mandatory sections (title, context_and_problem_statement, considered_options, decision_outcome) cannot be deleted; attempting to delete them raises AdrSectionError. Deletion is indicated by submitting an empty string, a whitespace-only string, or the literal case-insensitive "REMOVE". When deletion is requested for a non-mandatory optional section (decision_drivers, consequences, confirmation, more_information), the section heading and content are dropped from the render. Each call re-reads, mutates through in-memory Pydantic models, validates, and re-renders the full file.

### Consequences

One consistent tool interface for all body sections reduces cognitive load and maintenance burden. Clear sentinel-based deletion prevents accidental data loss. Mandatory-section protection ensures ADRs remain schema-valid. Trade-off: the tool surface is slightly more abstract than per-field tools.
