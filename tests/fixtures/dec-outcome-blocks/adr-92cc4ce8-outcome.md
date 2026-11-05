---
created: '2026-11-01T00:00:00.000Z'
id: 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c
status: accepted
type: dec
updated: '2026-11-01T00:00:00.000Z'
version: 1.0.0
---

# Regression fixture: Remove the Confluence tools (`confluence_fetch`, `confluence_update`) from the MCP server (outcome of DEC 92cc4ce8)

## Context and Problem Statement

This document is a committed regression fixture for feat-247-dec-outcome-blocks (GitHub issue #247): it carries the real `## Decision Outcome` outcome lead (the section from its H2 heading through the first `###` sub-section) of DEC 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c verbatim inside a minimal-but-valid `dec` body, to prove that the relaxed `DecisionOutcome` lead (a mandatory paragraph plus zero or more further blocks) parses this outcome without "text left over".

## Decision Outcome

**Chosen option: "Option 2: remove the Confluence tools entirely"**, directly implementing GitHub issue #120's explicit request. Keeping the tools (Option 1) leaves an unrelated domain mixed into a server whose entire purpose, as documented throughout `AGENTS.md`, is spec-document management -- every other tool in `general/` is either a generic dispatch tool operating on the twelve whole-body domains or a reference resource those domains depend on; the Confluence tools are the sole exception, and the issue that requested their removal reflects that this mismatch is no longer acceptable. Extracting them into a standalone MCP server (Option 3) was considered as a way to preserve the functionality for whichever consumer relies on it, but issue #120 asks for removal, not relocation, and building/maintaining a second MCP server/package is a materially larger undertaking than deleting code -- if Confluence integration is still needed by some consumer, this repo's own coding environment already demonstrates that a separate, general-purpose Atlassian MCP server (exposing `atlassian_confluence_*` tools) is the appropriate place for it, not a bespoke reimplementation maintained inside this repository.

This decision covers the ADR/decision-record step only (Phase 1 of feat-120-remove-confluence); the actual deletion of source code, tests, documentation, and the `httpx` dependency is carried out in Phase 2 of the same feature.

## Roles and Responsibilities

### Accountable

The platform architecture lead.

### Responsible

- The order service team.

## Source

Regression fixture derived from the `## Decision Outcome` section of DEC 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c.
