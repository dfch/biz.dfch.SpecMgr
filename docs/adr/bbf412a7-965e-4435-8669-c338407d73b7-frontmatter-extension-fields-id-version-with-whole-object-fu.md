---
status: accepted
decision-makers: dfch
id: bbf412a7-965e-4435-8669-c338407d73b7
version: 1.0.0
---

# Frontmatter extension fields (id, version) with whole-object full-replace update contract

## Context and Problem Statement

MADR 4.0.0 defines a standard set of frontmatter keys (status, date, decision-makers, consulted, informed). SpecMgr needs to add metadata: a unique identifier for each ADR so the MCP server can address it programmatically, and a schema version field for long-term evolution and migration. Additionally, the semantics of updating frontmatter must be clear: should callers be able to send partial updates, or must they send the entire frontmatter object?

## Decision Drivers

Need a stable, unique identifier for each ADR independent of filename; need to track schema version for future migrations; update semantics must be unambiguous and prevent accidental data loss from partial updates.

## Considered Options

Partial/patch frontmatter updates (PATCH semantics) vs. whole-object full-replace (PUT semantics); system-owned `id` excluded from user updates vs. allowing callers to submit/modify `id`.

## Decision Outcome

Add two extension fields to AdrFrontmatter: `id` (str | None, server-assigned UUID, system-managed) and `version` (str, default to CURRENT_SCHEMA_VERSION, e.g. '1.0.0'). Use a whole-object, full-replace update contract for frontmatter: callers submit the entire new AdrFrontmatter object, omitting a key drops it. However, the `id` is never part of this replacement contract—the `update_frontmatter` tool always re-injects the resolved `id` after reconstructing the model, ignoring whatever `id` the caller submitted. This makes `id` system-owned and immutable through the tool surface, while every other frontmatter key follows normal full-replace semantics.

### Consequences

Clear, unambiguous update semantics (full-replace prevents accidental partial overwrites and loss of unrelated fields). The `id` is guaranteed unique and never changes, providing stable addressability. Schema evolution is trackable: each document carries the version it was written with, enabling future migrations. Trade-off: callers must send the full frontmatter object, carrying forward unrelated fields they didn't intend to change.

## More Information

Pre-existing/hand-authored ADRs without an `id` field still parse (id: None), but are not addressable by id-based tools until the tool chain assigns one.
