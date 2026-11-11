---
status: accepted
date: '2026-09-01'
id: 1af6787b-eaab-4e8f-888f-531c1e76c19d
version: 1.0.0
---

# Replace domain-specific delete tools with a generic type-dispatched delete tool

## Context and Problem Statement

Every document domain except ADR shipped an unimplemented `delete_<d>` MCP tool: eleven registered stubs (`delete_req`, `delete_uc`, `delete_tsk`, `delete_qa`, `delete_prb`, `delete_gol`, `delete_rsk`, `delete_dec`, `delete_sop`, `delete_feat`, `delete_vcr`), each a near-duplicate module that always raised `NotImplementedError`. They inflated the tool surface without providing any capability, and no delete path-safety of any kind existed anywhere in the codebase: nothing prevented a malformed `id` (e.g. `../x`) from contributing to a resolved path. GitHub issue #36 asks for one generic, safe, locked delete.

## Decision Drivers

- Minimal tool surface: one entry point instead of eleven.
- An explicit `type` parameter keeps id resolution single-domain (no cross-domain ambiguity).
- Injection safety: the free-form `id` input must be validated before any filesystem access, and the resolved path must be confined to the domain's base directory.
- Reuse of each domain's existing per-id lock, `load_by_id` resolver, and base-dir plumbing rather than new plumbing.
- Filesystem is the sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a delete is a hard removal from disk, with no separate deletion record.
- The structural precedent of the generic, type-dispatched `update` and `set_status` tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0).

## Considered Options

Three options were considered:

1. A generic `delete(id, type)` tool with one private per-domain adapter inside `general/tools/delete.py`, plus a reusable, doc-type-agnostic path-safety module `general/tools/_path_safety.py`.
2. Implement each `delete_<d>` stub independently as its own real per-domain tool.
3. Resolve by UUID-only id, scanning all domains for a match, with no explicit `type` parameter.

## Decision Outcome

Option 1 was chosen and implemented in feature `feat-36-delete`. The generic `delete` tool covers the eleven whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`); ADR is deliberately excluded — no `delete_adr` ever existed, and hard-deleting an ADR risks breaking other ADRs' "superseded by X" cross-references. The eleven `delete_<d>` stubs are removed outright (no deprecated wrappers). The new forward convention: every current and future domain implements a `delete` adapter in the generic tool — never a per-domain `delete_<d>` tool.

### Consequences

- Breaking (0.x): eleven MCP tools removed, one added. The MCP tool list is the only client contract and the change is recorded in `CHANGELOG.md` under `[Unreleased]`.
- The reusable `general/tools/_path_safety.py` guards (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`) are wired into `delete` only; the `get_<d>`, `update`, and `set_status` tools are untouched here but can adopt the module later with zero rework for their own injection protection.
- `feat` deletes its entire `<base>/<id>/` folder (folder-per-document, ADR 8cf940c5-3100-485c-a12d-14b59b631712); the ten flat domains delete their single `*.md` file. The tool returns the deleted path as a string.

## Pros and Cons of the Options

### Option 1: Generic `delete(id, type)` with per-domain adapters and a reusable path-safety module

Good: a single delete entry point (eleven near-duplicate stubs collapse into one tool plus eleven small private adapters in one file, mirroring `update`/`set_status`); the explicit `type` keeps id resolution single-domain; the id is validated (`validate_id`) before any filesystem access and the resolved path is confined to the domain base directory (`assert_within`) inside the domain's own per-id lock; the path-safety module is pure and doc-type-agnostic, so `get_<d>`/`update`/`set_status` can adopt it later with zero rework.
Bad: the `delete` tool file grows as domains are added (one adapter per domain); callers must pass the explicit `type` (which is also what makes the tool safe and unambiguous).

### Option 2: Implement each `delete_<d>` stub independently

Good: no new generic surface; each domain stays self-contained.
Bad: eleven near-duplicate implementations of the same resolve/lock/delete sequence; no shared path-safety module (each would need its own, or none); the tool surface stays at eleven delete tools, contradicting the minimal-surface driver and the `update`/`set_status` precedent of ADR 36905d5b-8057-4294-8665-c7eed5534db0. Rejected.

### Option 3: UUID-only id resolution scanning all domains

Good: no `type` parameter required by callers.
Bad: cross-domain UUID ambiguity (the same UUID could exist in several domains — which one is deleted?); a full-directory scan over every domain on the write path; the same reasons ADR 36905d5b-8057-4294-8665-c7eed5534db0 rejected this shape for `update`. Rejected.

## More Information

- Feature plan: `.specmgr/feat/feat-36-delete/README.md` (requirements REQ-001..REQ-008, acceptance criteria ACC-001..ACC-008, design notes).
- Related ADRs: 36905d5b-8057-4294-8665-c7eed5534db0 (generic type-dispatched `update`/`set_status` tools — the structural precedent), 8cf940c5-3100-485c-a12d-14b59b631712 (`feat` folder-per-document addressing), 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth), 898bfcd0-85f9-462f-93a8-747bda4166c8 (ADRs authored only through MCP structured tools — this ADR was created with `create_adr`).
