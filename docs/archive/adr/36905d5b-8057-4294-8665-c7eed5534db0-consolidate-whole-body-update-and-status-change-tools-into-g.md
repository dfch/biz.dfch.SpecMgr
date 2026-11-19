---
status: accepted
date: '2026-08-27'
decision-makers: OpenCode agent + user decision
id: 36905d5b-8057-4294-8665-c7eed5534db0
version: 1.0.0
---

# Consolidate whole-body update and status-change tools into generic type-dispatched tools

## Context and Problem Statement

The specmgr MCP server currently exposes 15 near-duplicate mutation tools for what are two conceptual operations: seven per-domain whole-body updates (`update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`), seven per-domain status changes (`set_status_req`, `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`, `set_status_gol`, `set_status_rsk`), and ADR's own `set_status`. Each tool shares the same shape — id resolution in one domain directory, validation, frontmatter carry-over, `updated` bump, write — and differs only in domain vocabulary. LLM/agent clients see 15 entries in the MCP tool list for 2 conceptual operations, and every future document domain (e.g. the planned `ac`) would add more of the same duplicates, growing the surface linearly with the number of domains.

## Decision Drivers

- A simpler tool surface: the two conceptual operations should be exposed as two tools, not fifteen near-duplicates.
- Id resolution must not require an all-domains directory scan on the write path, and must not introduce per-domain v4-UUID-collision ambiguity — uuid-only id resolution was considered and rejected (per-domain v4 UUIDs are not guaranteed unique across domains).
- The calling client already knows the domain it is operating on (the same vocabulary as the frontmatter `type` field), so passing it explicitly costs the client nothing.
- Preserve the existing invariants: the filesystem is the sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3) and validation happens before any write (nothing is written on validation failure).

## Considered Options

- Option 1: two generic tools in `general/tools/` with an explicit `type` parameter — `update(id, type, content, begin, end)` covering the seven whole-body domains and `set_status(id, type, status, superseded_by)` covering all eight domains including `adr` — each dispatching to a private, verbatim-ported per-domain adapter. Chosen.
- Option 2: generic tools that resolve the id by uuid alone, scanning every domain directory to locate the matching document.
- Option 3: keep the 15 per-domain tools unchanged.

## Decision Outcome

Option 1: two generic, type-dispatched tools — `update(id, type, content, begin, end)` in `general/tools/update.py` for the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`), and `set_status(id, type, status, superseded_by)` in `general/tools/set_status.py` for all eight domains including `adr`. The explicit `type` parameter keeps id resolution single-domain (no directory scan, no cross-domain UUID ambiguity), matches the domain vocabulary the calling client already has, and reduces the tool surface from 15 near-duplicate entries to 2. Each domain's semantics are preserved 1:1 by a private adapter that is a verbatim port of the deleted tool body, so the filesystem-is-source-of-truth and validate-before-write invariants are untouched.

### Consequences

- Bad (breaking): the 14 per-domain tools are removed outright, and ADR `set_status`'s signature gains a required `type` parameter — existing ADR callers must now pass `type="adr"`. The package is 0.x and the MCP tool list is the only client contract; the breaking change is recorded in `CHANGELOG.md`.
- ADR is excluded from `update` — its section-level MADR contract (`update_frontmatter`/`update_section`/`option_*`, ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) has no whole-body replace by design — but is included in `set_status` with the `superseded_by` special case: `superseded_by` composes the status as `"superseded by {superseded_by}"`, and `superseded_by` given with any `type` other than `"adr"` raises `ValueError` before any file access.
- The `update` line-range contract: optional 1-based, inclusive body-line coordinates `begin`/`end`, with `N+1` as the EOF sentinel (`begin = end = N+1` appends at end of body; `end = N+1` extends the range through the last line). The spliced result is validated as a whole document before anything is written (splice-then-validate-whole), and the YAML frontmatter is never addressable (coordinates are body-relative by construction).
- Line numbers for range updates are served by a new `get_<d>(raw=True)` parameter returning the frontmatter-stripped body text verbatim — tool-first per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (agents invoke tools more reliably than parameterized resources); re-introducing `specmgr://<d>/{id}` resources was considered and rejected.
- Good: future domains (e.g. `ac`) add one dispatch entry per generic tool (plus a `raw` getter parameter), not new tools.

## Pros and Cons of the Options

### Option 1: Generic tools with an explicit type parameter

#### Pros

- Minimal tool surface: two tools for the two conceptual operations (the feature ends at 71 tools / 25 resources / 19 prompts, from 84/25/19: −15 +2), instead of 15 near-duplicate entries in the MCP tool list.
- The calling client already knows the domain — it is the same vocabulary as the frontmatter `type` field — so the explicit parameter costs the client nothing, and id resolution stays single-domain: no all-directories scan on the write path, no per-domain v4-UUID-collision ambiguity.
- Every future domain (e.g. the planned `ac`) adds one dispatch entry per generic tool, keeping the surface flat as domains grow.
- Preserves all per-domain semantics: each adapter is a verbatim port of the deleted tool body (same lock, same `load_by_id`, same frontmatter carry-over and `updated` bump, same write path, same domain not-found error), and the filesystem-is-source-of-truth and validate-before-write invariants are untouched.

#### Cons

- Breaking change for 0.x clients: the 14 per-domain tools disappear, and ADR `set_status`'s signature gains a required `type` (existing ADR callers must now pass `type="adr"`).
- ADR needs special-casing in `set_status` (the `superseded_by` composition) and is excluded from `update` by design (its MADR section-level contract has no whole-body replace).

### Option 2: uuid-only id resolution scanning all domain directories

#### Pros

- Shortest client call: no `type` parameter; any document in any domain is addressable by id alone.

#### Cons

- Full-directory scan on every write: all domain directories must be traversed and every file parsed to locate the matching id, and the cost grows with each added domain on the write path.
- Per-domain v4 UUIDs are not guaranteed unique across domains, so a collision between two domains makes the id ambiguous — the server would have to pick one arbitrarily or raise a new class of errors.
- Loses the explicit domain vocabulary clients already use everywhere else (the frontmatter `type` field) and obscures which domain's semantics (status vocabulary, lock, write path) are actually being applied.

### Option 3: Keep the per-domain tools

#### Pros

- No breaking change; existing clients keep working unchanged.
- No dispatch-table machinery; each tool remains a simple single-domain wrapper.

#### Cons

- The MCP tool list carries 15 near-duplicate entries for 2 conceptual operations, inflating every client's tool context.
- Every future domain adds more near-duplicate tools (a `update_<d>` / `set_status_<d>` pair per domain), growing the surface linearly with the number of domains.
- LLM clients must pick among the duplicates for each operation, which risks mis-selection and makes the surface harder to document, test, and keep consistent.

## More Information

- Feature plan and progress: `.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`.
- Related ADRs: ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based document reads are tools, not resources), 71fd95d7-07f2-466f-81aa-d29b7e3ef34c (the ADR `update_section` contract that `update` deliberately does not extend to ADR), 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth), ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy — the generic tools live in the cross-cutting `general/` package).
