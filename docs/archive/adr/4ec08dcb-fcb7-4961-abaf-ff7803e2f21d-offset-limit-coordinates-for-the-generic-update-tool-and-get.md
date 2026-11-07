---
status: accepted
date: '2026-09-01'
decision-makers: OpenCode agent + user decision
id: 4ec08dcb-fcb7-4961-abaf-ff7803e2f21d
version: 1.0.0
---

# offset/limit coordinates for the generic update tool and get_<d> windowed reads

## Context and Problem Statement

GitHub issue #28 ("specmgr_get and specmgr_update must both support offset and limit") asks the specmgr MCP server's generic `update` tool and the eleven `get_<d>` tools to both support read-style `offset`/`limit` coordinates, so an LLM client can read and edit a body slice without fetching the whole document. Today the generic `update` tool (`general/tools/update.py`) splices its line-range replacement with a 1-based, inclusive `begin`/`end` body-line pair plus an `N+1` end-of-body sentinel — the contract recorded in ADR 36905d5b-8057-4294-8665-c7eed5534db0's Consequences — and each `get_<d>` tool supports only whole-document reads: a parsed document, or the frontmatter-stripped body text verbatim via `raw=True`. Two mismatches follow: `update`'s `begin`/`end` vocabulary is foreign to the `read` tool's `offset`/`limit` convention the calling agent already knows, and a client editing a slice must first fetch (and count) the whole body. Because ADR 36905d5b's Consequences record the old contract, the revision is recorded here, referencing that ADR without superseding it — its dispatch-only decision (generic type-dispatched `update`/`set_status`/`delete` tools, no per-domain `update_<d>`) stands unchanged.

## Decision Drivers

- The calling client (an LLM agent) already knows the `read` tool's `offset`/`limit` convention (`offset` = 1-based start line, `limit` = count); `update` and `get_<d>` should speak the same coordinate vocabulary.
- The raw/splice invariant must hold: the line numbers a client sees in any `get_<d>(raw=True)` read (windowed or not) must index byte-for-byte into the same text the generic `update` tool splices against.
- The package is 0.x and the MCP tool list is the only client contract; LLM clients re-read tool descriptions each session, so a hard rename rolls out with the next tool-list fetch, while a dual-named parameter set would steer agents at the older names.
- Preserve the existing invariants: validation before any write (nothing is written on validation failure), filesystem as the sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3), verbatim persistence of the validated body, and frontmatter carry-over.

## Considered Options

Three design axes were considered, each with the chosen approach and its rejected alternative: naming (Option 1 vs. Option 2 — hard rename vs. dual-named alias), the `update` splice validation posture (Option 3 vs. Option 4 — strict vs. clamping), and the `get_<d>` windowing scope (Option 5 vs. Option 6 — raw-only vs. both modes).

- Option 1: hard rename of `update`'s `begin`/`end` to `offset`/`limit` in one release, with no compatibility alias. Chosen.
- Option 2: dual-named parameters — `offset`/`limit` introduced while `begin`/`end` remain accepted as aliases.
- Option 3: strict splice validation — any out-of-range `offset`/`limit` coordinate raises `ValueError` and nothing is written. Chosen.
- Option 4: clamping splice validation — out-of-range coordinates are clamped to the valid range and the splice proceeds.
- Option 5: raw-only windowed reads — `offset`/`limit` on `get_<d>` are valid with `raw=True` only, and out-of-range values clamp instead of erroring (consistent with `list_<d>` paging). Chosen.
- Option 6: windowed reads in both modes — `offset`/`limit` accepted with `raw=False` as well, returning a partial parsed document.

## Decision Outcome

Option 1, Option 3, and Option 5. The generic `update` tool's line-range mode becomes read-style `offset`/`limit` coordinates (hard rename, no `begin`/`end` compatibility alias), validated strictly; the eleven `get_<d>` tools gain the same coordinates for windowed raw reads, validated by clamping. The exact semantics:

`update` — `offset` is the 1-based first body line to replace; allowed `1..N+1` where `N` is the current body line count and `N+1` is the virtual end-of-body position (append). Omitted `limit` replaces through the last body line; `limit=0` is a pure insert; `limit=k>0` replaces the `k` lines `offset..offset+limit-1`. `limit` given without `offset` raises `ValueError` before any file access. Any out-of-range coordinate — `offset<1`, `offset>N+1`, `limit<0`, or `offset+limit-1>N` — raises `ValueError` with nothing written (strict, never clamped: a silently shifted range would corrupt the document). Splice-then-validate-whole, verbatim persistence, and frontmatter carry-over are unchanged.

`get_<d>` — `offset`/`limit` are valid with `raw=True` only; coordinates with `raw=False` raise `ValueError` because a parsed document requires the whole body. `offset` defaults to 1 and is floored to 1; `limit` defaults to through end of body and is capped at the remaining lines; `offset>N` returns the empty string. Out-of-range values clamp instead of erroring — reads are non-destructive, matching the `list_<d>` paging convention ("out-of-range values are clamped, not errored", ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). The window is served by a new no-I/O `window_body(text, offset, limit)` helper in `general/tools/_splice.py` beside `body_text`/`splice_body`, so the raw/splice invariant holds by construction: `body_text` remains the single definition of the frontmatter-stripped body text, and the line numbers a client sees in any `get_<d>(raw=True)` read (windowed or not) index byte-for-byte into the same text the generic `update` tool splices against.

Migration of today's `begin`/`end` calls to the new coordinates:

| today | new |
| --- | --- |
| `begin=k, end=m` (k<=m<=N) | `offset=k, limit=m-k+1` |
| `begin=k, end=N+1` (through end) | `offset=k` (limit omitted) |
| `begin=N+1, end=N+1` (append) | `offset=N+1` (limit 0 or omitted) |
| `begin=1, end=N` (whole body) | whole-body mode, or `offset=1` (limit omitted) |

### Consequences

- Bad (breaking): the `update` tool's input schema loses `begin`/`end` and gains `offset`/`limit` in one release, with no compatibility alias. Every LLM-facing surface moves to the new vocabulary in the same release: the ten `*_update_instructions.md` packaged prompt data files plus `qa_refine_instructions.md`, the `update` and eleven `get_<d>` tool descriptions, the `server.py` and `general/tools/__init__.py` docstrings, `AGENTS.md`, and the `CHANGELOG.md` `[Unreleased]` section — after which no `begin`/`end` range reference remains in `src/`.
- Good: `read`, `get_<d>` raw reads, and `update` range splices speak one coordinate vocabulary, and an LLM client can read and edit a body slice without fetching the whole document; the raw/splice invariant is defined once (shared `body_text`/`splice_body`/`window_body` in `general/tools/_splice.py`) for all eleven domains.
- Neutral: `get_adr` is untouched — ADR reads have no `raw` mode, and issue #28 targets the `get_<d>` tools' existing `raw` parameter only.
- Neutral: ADR 36905d5b-8057-4294-8665-c7eed5534db0 is referenced, not superseded — its dispatch-only decision stands; only its Consequences' `begin`/`end` + `N+1` contract is revised here.

## Pros and Cons of the Options

### Option 1: Hard rename begin/end to offset/limit (no compatibility alias)

#### Pros

- One coordinate vocabulary across the `read` tool, `get_<d>` raw reads, and `update` range splices — the calling agent already knows `offset`/`limit`.
- Pre-1.0 surface: the MCP tool list is the only client contract, and LLM clients re-read tool descriptions each session, so the rename reaches every client with the next tool-list fetch.
- No dual-named parameters in the `update` input schema — a dual set would steer agents at the older names.
- Repo precedent favors clean breaks over long-lived compatibility shims.

#### Cons

- Breaking in one release: every `update(begin=, end=)` call site (including the test suite) and every LLM-facing text (the ten `*_update_instructions.md` prompt data files plus `qa_refine_instructions.md`, tool descriptions, docstrings, `AGENTS.md`, `CHANGELOG.md`) must move to the new vocabulary in the same release.

### Option 2: Dual-named parameters: offset/limit alongside begin/end aliases

#### Pros

- No breaking change: existing `begin`/`end` call sites keep working through a transition period.

#### Cons

- The `update` input schema carries two names for one concept, inflating every client's tool context.
- LLM clients re-read tool descriptions each session and would be steered at the older names, prolonging the migration indefinitely.
- The pre-1.0 surface has no stable contract to preserve; repo precedent favors clean breaks.

### Option 3: Strict splice validation: out-of-range raises ValueError, nothing written

#### Pros

- Splicing is destructive: a silently clamped (shifted) range would replace different lines than the client intended, corrupting the document.
- Consistent with the validate-before-write invariant (ADR 36905d5b-8057-4294-8665-c7eed5534db0): nothing is written on validation failure.
- Errors are explicit and carry the offending coordinate.

#### Cons

- The client must know the current body line count `N` (or re-read via `get_<d>(raw=True)`) to form valid `offset`/`limit` coordinates.

### Option 4: Clamping splice validation: out-of-range coordinates clamp to the valid range

#### Pros

- The client can pass loose or stale coordinates (e.g. a `limit` from an earlier read) without erroring.

#### Cons

- A silently shifted range replaces different lines than the client intended — silent corruption is worse than a loud `ValueError`.
- Inconsistent with the validate-before-write invariant on the destructive path.

### Option 5: Raw-only windowed reads: offset/limit valid with raw=True; out-of-range clamps

#### Pros

- Reads are non-destructive, so clamping instead of erroring is safe and consistent with the `list_<d>` paging convention ("out-of-range values are clamped, not errored", ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
- Defaults reproduce today's whole-body raw read byte-for-byte, so existing clients are unaffected.
- An LLM client can read and edit a body slice without fetching the whole document.
- The no-I/O shared `window_body(text, offset, limit)` helper keeps the raw/splice invariant defined once for all eleven domains.

#### Cons

- Coordinates are useless in structured mode: a parsed document requires the whole body, so `offset`/`limit` with `raw=False` raise `ValueError`.

### Option 6: Windowed reads in both modes: offset/limit accepted with raw=False

#### Pros

- A uniform parameter surface regardless of `raw`.

#### Cons

- A parsed (structured) document cannot be meaningfully produced from a body slice — the parser requires the whole body — so the feature is either unimplementable or silently lossy.
- A `ValueError` guard rejecting the partial parse is still needed, at extra cost.

## More Information

- GitHub issue #28 ("specmgr_get and specmgr_update must both support offset and limit"): https://github.com/dfch/biz.dfch.SpecMgr/issues/28.
- Feature plan and progress: `.specmgr/feat/feat-28-get-update/README.md` (split out from feat-7 Task 0.32, `.specmgr/feat/feat-7-various-improvements/README.md`).
- Related ADRs: 36905d5b-8057-4294-8665-c7eed5534db0 (the generic type-dispatched `update` tool and the old `begin`/`end` + `N+1` contract this ADR revises — referenced, not superseded), ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based document reads are tools, not resources — the `get_<d>` tools this ADR extends), ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tools and the "clamped, not errored" paging convention the `get_<d>` windowing reuses).
