---
status: accepted
decision-makers: dfch
id: c73e4f9d-81f3-495d-bd3a-f660ab992ed3
version: 1.0.0
---

# Base the ADR template on MADR 4.0.0

## Context and Problem Statement

The SpecMgr project needs a standard format for Architecture Decision Records to document design choices, trade-offs, and consequences. Multiple ADR template standards exist (MADR, Y-Statements, lightweight ADRs, etc.), each with different structures, conventions, and tooling maturity.

## Decision Drivers

Compatibility with existing tooling and widespread community adoption; structure that supports Pydantic schema validation and programmatic editing; clear sections for context, drivers, options, and outcomes; extensibility for system-owned metadata (id, version).

## Considered Options

MADR 4.0.0 (Markdown ADR template) vs. Y-Statements vs. other ADR formats

## Decision Outcome

Adopt MADR 4.0.0 as the base template. Extend the MADR frontmatter with two custom fields: `id` (server-assigned UUID for addressability) and `version` (schema version for long-term evolution). The MADR structure provides a well-established heading hierarchy (H1 title, H2 context/decision-drivers/considered-options/outcome/more-information, H3 sub-sections under outcome) that naturally maps to a Pydantic body model with optional and mandatory sections.

### Consequences

The SpecMgr codebase can leverage a well-known, mature template rather than inventing its own. MADR's clear structure (pros/cons under each option, clear decision outcome) aligns well with LLM-driven authoring. Extensions (`id`, `version`) are non-breaking additions to the MADR 4.0.0 standard, following the pattern of adding optional frontmatter keys.

## More Information

MADR 4.0.0 template: https://github.com/adr/madr/tree/refs/tags/4.0.0/template
