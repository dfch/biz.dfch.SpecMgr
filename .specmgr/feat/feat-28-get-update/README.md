---
created: '2026-09-01T14:19:27.649184'
id: feat-28-get-update
status: planning
type: feat
updated: '2026-09-01T14:41:58.972675'
version: 1.0.0
---

# Feature: offset/limit Coordinates for the update and get Tools

## Plan

### Overview

This feature implements GitHub issue #28 ("specmgr_get and specmgr_update
must both support offset and limit"): the generic `update` tool and the
eleven `get_<d>` tools must both support read-style `offset`/`limit`
coordinates. Today `update` addresses its line-range splice with a 1-based
inclusive `begin`/`end` pair plus an `N+1` end-of-body sentinel, and the
`get_<d>` tools only support whole-document reads (structured, or raw via
`raw=True`). After this feature, `update` splices a read-style window
(`offset` = first line, `limit` = number of lines, omitted = through end of
body) and `get_<d>(raw=True, offset=…, limit=…)` returns exactly that window,
so an LLM caller can read and edit a body slice without fetching the whole
document. The rename is hard (no `begin`/`end` compatibility alias): every
LLM-facing text (packaged prompt instructions, tool descriptions,
docstrings, `AGENTS.md`, `CHANGELOG.md`) moves to the new vocabulary in the
same release, and the revised contract is recorded in a new ADR that
references ADR 36905d5b without superseding it.

### Requirements

- REQ-001: The generic `update` tool replaces its 1-based inclusive `begin`/`end` body-line range with read-style `offset`/`limit` coordinates in a hard rename (no compatibility alias): `offset` is the 1-based first line to replace (allowed `1..N+1`, where `N` is the current body's line count and `N+1` the virtual end-of-body position for appending), `limit` omitted replaces through the last body line, `limit=0` is a pure insert, `limit=k>0` replaces `k` lines starting at `offset`, and out-of-range coordinates raise `ValueError` (strict, never clamped, because splicing is destructive) with nothing written, while splice-then-validate-whole, verbatim persistence, and frontmatter carry-over are unchanged.

- REQ-002: Each of the eleven `get_<d>` tools (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`) supports `offset`/`limit` windowed reads: coordinates are only valid with `raw=True` (coordinates with `raw=False` raise `ValueError`), `offset` defaults to 1 and is floored, `limit` defaults to through end of body and is capped at the remaining lines, out-of-range values clamp instead of erroring (read-only, consistent with the `list_<d>` paging convention "clamped, not errored"), and the result is the plain sliced body `str` produced by a new no-I/O `window_body` helper in `general/tools/_splice.py`.

- REQ-003: The raw/splice invariant holds under the new coordinates: `body_text` remains the single definition of the frontmatter-stripped body text, and the line numbers a client sees in any `get_<d>(raw=True)` read (windowed or not) index byte-for-byte into the same text the generic `update` tool splices against.

- REQ-004: Every LLM-facing contract moves to the new vocabulary in the same release: the ten `*_update_instructions.md` packaged data files plus `qa_refine_instructions.md`, the `update` and eleven `get_<d>` tool descriptions, the `server.py` and `general/tools/__init__.py` docstrings, `AGENTS.md`, and `CHANGELOG.md`'s `[Unreleased]` section, with no `begin`/`end` range references remaining in `src/`.

- REQ-005: The revised range/windowing contract is recorded in a new ADR (created as draft at implementation start, set to accepted at close) that references ADR 36905d5b (whose Consequences record the old `begin`/`end` + `N+1` contract) without superseding it, since that ADR's dispatch-only decision stands.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — `update`'s MCP input schema exposes `offset`/`limit` and no longer `begin`/`end`; range mode replaces exactly lines `offset..offset+limit-1`; omitted `limit` replaces through end of body; `limit=0` inserts; `offset=N+1` appends; and each of `offset<1`, `offset>N+1`, `limit<0`, `offset+limit-1>N`, and `limit` without `offset` raises `ValueError` with nothing written.

- [ ] ACC-002: Verifies REQ-002 — `get_<d>(raw=True, offset=…, limit=…)` returns exactly the requested body window (defaults reproduce today's full raw read byte-for-byte); `offset>N` returns the empty string; `limit` is capped at the remaining lines; coordinates with `raw=False` raise `ValueError`; and not-found errors are unchanged in every mode, verified for each of the eleven domains.

- [ ] ACC-003: Verifies REQ-003 — the per-domain raw-read-into-splice round-trip holds under the new coordinates (the existing invariant tests re-expressed with `offset`/`limit`), plus a windowed variant: line numbers obtained from a windowed `get_<d>(raw=True, offset=…, limit=…)` read splice at exactly those coordinates, leaving unchanged regions byte-identical.

- [ ] ACC-004: Verifies REQ-004 — all eleven instruction data files, the `update`/`get_<d>` tool descriptions, and the prompt tests reference `offset`/`limit` (prompt tests pass against the new literals), and a repository search for `begin`/`end` range references in `src/` and `AGENTS.md` finds none.

- [ ] ACC-005: Verifies REQ-005 — the new ADR exists, references 36905d5b, and is accepted at close; `docs/adr/README.md` is regenerated without drift.

- [ ] ACC-006: Verifies all — every phase ends green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite pass; `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` are regenerated without drift; exactly one commit per phase, never pushed.

### Scope

#### Included

- `general/tools/update.py`: parameter rename, new guard, eleven `_update_<d>` adapter signatures, dispatch-table type, tool description, docstrings.

- `general/tools/_splice.py`: `splice_body` reworked to `offset`/`limit`; new no-I/O `window_body` helper.

- The eleven `get_<d>` tools (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`): `offset`/`limit` parameters, raw-only guard, windowing, tool descriptions, docstrings.

- Tests: `tests/general/tools/test_update.py` (range cases + input-schema assertions), new `tests/general/tools/test__splice.py` (direct `window_body`/`splice_body` unit tests), the eleven `tests/<d>/tools/test_get_<d>.py` (window cases + re-expressed invariant tests), `tests/feat/tools/test_integration.py`, `tests/sop/tools/test_integration.py`.

- LLM-facing data: the ten `*_update_instructions.md` files plus `qa_refine_instructions.md`, and the ~12 prompt test files that assert their literals.

- Docs: `server.py` docstring, `general/tools/__init__.py` docstring, `AGENTS.md` (eleven per-domain `raw` bullets + the generic `update` bullet), `CHANGELOG.md` `[Unreleased]`, regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`.

- One new ADR; the `feat-7` Task 0.32 "split out" annotation pointer.

#### Explicitly Out Of Scope

- `get_adr` windowing (ADR reads have no `raw` mode; the issue and `feat-7` Task 0.32 target the `get_<d>` tools' existing `raw` parameter only).

- `begin`/`end` compatibility aliases (hard rename by decision; pre-1.0 surface, LLM clients re-read tool descriptions each session).

- Fixing `create_feat`'s id auto-assignment (expected behaviour: optional caller-chosen id, `0` when unspecified instead of a max+1 auto-generation fallback, fail if the id is already in use) — tracked in GitHub issue #48.

- The additional feat-domain `set_feat_id` tool (rename the feature folder + frontmatter `id`, e.g. `feat-0-…` → `feat-42-…`) — tracked in GitHub issue #48; until it exists, id changes stay manual (folder move + frontmatter edit), as this feature's own `feat-37-…` → `feat-28-get-update` rename demonstrates.

- Changes to `list_<d>` paging, structured-mode (`raw=False`) partial reads, the ADR domain's section-mutation contract, and the CLI.

### Dependencies

#### Depends On

- GitHub issue #28 ("specmgr_get and specmgr_update must both support offset and limit") — the source request, already tracked as `feat-7` Task 0.32.

#### Blocks

- Nothing.

### Design Notes

The new `update` range contract, and how it maps onto today's `begin`/`end`:

| today | new |
| --- | --- |
| `begin=k, end=m` (k<=m<=N) | `offset=k, limit=m-k+1` |
| `begin=k, end=N+1` (through end) | `offset=k` (limit omitted) |
| `begin=N+1, end=N+1` (append) | `offset=N+1` (limit 0 or omitted) |
| `begin=1, end=N` (whole body) | whole-body mode, or `offset=1` (limit omitted) |

`limit` is a count, like the `read` tool's: the replaced range is
`offset..offset+limit-1`. Omitted `limit` means "through end of body", which
preserves every capability of today's `end=N+1` sentinel without forcing the
client to know `N`; `limit=0` is a pure insert (with `offset=N+1` that is the
append case). Validation stays strict on the destructive path — `offset<1`,
`offset>N+1`, `limit<0`, or `offset+limit-1>N` each raise `ValueError` and
nothing is written; clamping a splice would silently change what gets
replaced.

`get_<d>` windowing takes the opposite posture: reads are non-destructive, so
out-of-range values clamp instead of erroring, matching the `list_<d>` paging
convention ("out-of-range values are clamped, not errored"). `offset` floors
to 1, `limit` caps at the remaining lines, `offset>N` yields the empty
string, and the defaults reproduce today's `raw=True` read byte-for-byte. The
window is served by a new no-I/O `window_body(text, offset, limit)` helper in
`general/tools/_splice.py`, beside `body_text`/`splice_body`, so the
raw/splice invariant (what the client counts is what the server splices) is
defined once and shared by all eleven tools. Coordinates with `raw=False`
raise `ValueError` because a parsed document requires the whole body.

Phase discipline: every phase ends with the complete test cycle (`ruff
format --check`, `ruff check`, `vulture src/ whitelist.py
--min-confidence 60`, full `unittest` suite) plus doc regeneration where
`src/` changed, and exactly one local commit (never pushed). Phase 1
migrates every test call site of `update(begin=, end=)` in the same commit as
the rename so each phase commit is green; the prompt data files and their
tests move together in the LLM-contract phase.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: the dispatch-only generic `update`/`set_status`/`delete` tools and the old `begin`/`end` + `N+1` range contract this feature revises (referenced, not superseded).

- ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614: id-based document reads are tools (`get_<d>`), not resources — the tools this feature extends.

- ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: paged `list_<d>` tools and the "clamped, not errored" paging convention the `get_<d>` windowing reuses.

- New ADR (to be created at implementation start, Task 0.5): the revised `offset`/`limit` range/windowing contract.

### Task List

#### Phase 0: Sync + Planning Artifacts

- [x] Task 0.1: Sync prerequisites — `git fetch origin` + `git merge --ff-only origin/dev` (branch was 0 ahead, fast-forwarded 72efee3 → 8c13e16), `uv sync --all-extras --frozen` (89 packages current), `uv run --frozen pre-commit install` (re-stamps the worktree-shared hook to this venv; the previous stamp pointed at the feat-27 worktree), baseline full test cycle green (2713 tests) — depends on: none — status: done (2026-09-01)
- [x] Task 0.2: Create the GitHub issue on `create_feat`'s id auto-assignment (expected behaviour: optional caller-chosen id, `0` when unspecified with no max+1 fallback, fail if the id is already in use; plus the additional `set_feat_id` tool) — depends on: none — status: done (2026-09-01, issue #48)
- [x] Task 0.3: Create this feature via `specmgr_create_feat` (auto-assigned `feat-37-offset-limit-coordinates-for-the-update-and-get-tools`, since `feat-36-delete` is the highest existing folder), then manually rename the folder + frontmatter `id` to `feat-28-get-update` (manual because the `set_feat_id` tool is out of scope, tracked in issue #48), verify with `specmgr_get_feat` — depends on: none — status: done (2026-09-01)
- [ ] Task 0.4: Annotate `feat-7` Task 0.32 with the "split out into `feat-28-get-update`" pointer (Task 0.15 → feat-13 precedent) and bump `feat-7`'s frontmatter `updated` + a Recent Updates entry — depends on: none — status: not-started
- [ ] Task 0.5: Create the ADR recording the revised `offset`/`limit` contract (draft; set to accepted at close) — depends on: none — status: not-started
- [ ] Task 0.6: Phase gate — complete test cycle + commit — depends on: Task 0.4, Task 0.5 — status: not-started

#### Phase 1: update Core (offset/limit Rename)

- [ ] Task 1.1: Rework `general/tools/_splice.py` — `splice_body(current_body, offset, limit: int | None, content)` per the Design Notes contract (omitted limit = through end of body, 0 = insert, strict validation), module docstrings — depends on: Phase 0 — status: not-started
- [ ] Task 1.2: Rework `general/tools/update.py` — public `offset`/`limit` parameters, new guard (`limit` without `offset` → `ValueError` before any file access), eleven `_update_<d>` adapter signatures, `_ADAPTERS` Callable type, tool description, docstrings — depends on: Task 1.1 — status: not-started
- [ ] Task 1.3: Migrate every `update(begin=, end=)` test call site in the same commit — `tests/general/tools/test_update.py` (range cases re-expressed + all error cases incl. the new guard + input-schema assertions on `offset`/`limit`), the eleven `tests/<d>/tools/test_get_<d>.py` round-trip lines, `tests/feat/tools/test_integration.py`, `tests/sop/tools/test_integration.py` — depends on: Task 1.2 — status: not-started
- [ ] Task 1.4: Phase gate — complete test cycle + doc regeneration + commit — depends on: Task 1.3 — status: not-started

#### Phase 2: get Windowing

- [ ] Task 2.1: Add the no-I/O `window_body(text, offset, limit)` helper to `general/tools/_splice.py` (clamping per Design Notes) — depends on: Phase 1 — status: not-started
- [ ] Task 2.2: Extend the eleven `get_<d>` tools — `offset`/`limit` parameters, raw-only guard, windowing via the shared helper, tool descriptions, docstrings — depends on: Task 2.1 — status: not-started
- [ ] Task 2.3: New `tests/general/tools/test__splice.py` — direct unit tests for `window_body` (defaults, mid window, `offset>N` → `""`, `limit` capping, `limit=0`) and `splice_body`'s new signature — depends on: Task 2.1 — status: not-started
- [ ] Task 2.4: Extend the eleven `tests/<d>/tools/test_get_<d>.py` — window slice equality, clamp/empty cases, coordinates + `raw=False` → `ValueError`, windowed read-into-splice round-trip — depends on: Task 2.2 — status: not-started
- [ ] Task 2.5: Phase gate — complete test cycle + doc regeneration + commit — depends on: Task 2.4 — status: not-started

#### Phase 3: LLM-facing Contract

- [ ] Task 3.1: Rewrite the range-update step in the ten `*_update_instructions.md` data files + `qa_refine_instructions.md` to `offset`/`limit` (incl. the `N+1` append wording) — depends on: Phase 2 — status: not-started
- [ ] Task 3.2: Update the ~12 prompt test files asserting the old `begin=..., end=...` literals (`tests/req/prompts/`, `tests/tsk/prompts/`, `tests/qa/prompts/` (incl. `test_refine.py`), `tests/prb/prompts/`, `tests/gol/prompts/`, `tests/rsk/prompts/`, `tests/dec/prompts/`, `tests/sop/prompts/`, `tests/feat/prompts/`, `tests/vcr/prompts/`) to the new literals — depends on: Task 3.1 — status: not-started
- [ ] Task 3.3: Phase gate — complete test cycle + commit — depends on: Task 3.2 — status: not-started

#### Phase 4: Docs, Regen, Close

- [ ] Task 4.1: Update `server.py` + `general/tools/__init__.py` docstrings, `AGENTS.md` (eleven per-domain `raw` bullets + the generic `update` bullet), `CHANGELOG.md` `[Unreleased]` (Changed: breaking `begin`/`end` → `offset`/`limit` rename; Added: `get_<d>` windowing) — depends on: Phase 3 — status: not-started
- [ ] Task 4.2: Regenerate `specmgr mcp-docs` (+ `specmgr docs`/`specmgr adr-toc` drift check) — depends on: Task 4.1 — status: not-started
- [ ] Task 4.3: Set the ADR to `accepted`; annotate `feat-7` Task 0.32 done (split-out feature complete); set this feature's status to `done` — depends on: Task 4.2 — status: not-started
- [ ] Task 4.4: Final phase gate — complete test cycle + final commit — depends on: Task 4.3 — status: not-started

## Progress

### Current Status

**As of 2026-09-01**: Planning complete. All design decisions are taken (see
Decisions Made); the working tree is synced to the latest upstream `dev`
(`8c13e16`) with the full suite green (2713 tests) and pre-commit hooks
installed against this worktree's venv. GitHub issue #48 (the deferred
`create_feat` id work) is filed. Implementation (Phase 0 remainder → Phase 4)
has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 14:41:58.971+02:00 — Session wrap-up; plan made self-contained for a fresh implementation session

Added a `### More Information` section with the operational facts a fresh
implementing agent would otherwise have to rediscover: worktree/branch,
never-push, the per-phase commit-message convention, the specmgr MCP server
cwd caveat (base dirs resolve relative to the server's own cwd — verify
created files land in this worktree via `git status`), the `specmgr adr-toc`
regeneration step for Task 0.5, and the `read`-tool reference for
"read-style" coordinates. No code or contract changes. Implementation picks
up at Task 0.4 (feat-7 Task 0.32 annotation) and Task 0.5 (ADR draft).

#### 2026-09-01 14:09:43.294+02:00 — Feature created; planning complete

Completed: the design phase — all contract decisions taken (see Decisions
Made); synced to upstream `dev` `8c13e16` (uv synced, pre-commit installed,
baseline 2713 tests green); filed GitHub issue #48 for the deferred
`create_feat` id behaviour (no caller id, no `set_feat_id` tool); created this
feature via `specmgr_create_feat` and renamed the auto-assigned
`feat-37-offset-limit-coordinates-for-the-update-and-get-tools` folder +
frontmatter id to `feat-28-get-update`. Next: Phase 0 remainder (feat-7 Task
0.32 annotation, ADR draft) then Phase 1 (`update` core rename).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 14:09:43.294+02:00 — Deferred create_feat id work to GitHub issue #48

The `create_feat` id auto-assignment fix (optional caller-chosen id, `0` when
unspecified instead of a max+1 auto-generation fallback, fail if the id is
already in use) and the additional `set_feat_id` tool (rename folder +
frontmatter id, e.g. `feat-0-…` → `feat-42-…`) are explicitly out of scope
for this feature; both are recorded in GitHub issue #48 so a future agent can
implement them without this being forgotten. This feature's own folder was
renamed manually in the interim.

#### 2026-09-01 14:09:43.294+02:00 — Feature id: specmgr_create_feat then manual rename to feat-28

`create_feat` auto-assigns `feat-<max existing NNN + 1>-<title slug>` and
accepts no caller id (the highest existing folder is `feat-36`, so this
feature became `feat-37-…`), which breaks the "NNN = GitHub issue number"
convention the worktree already follows; decided (user direction) to use the
tool and then rename the folder + frontmatter id to `feat-28-get-update`
manually — the underlying gap is filed as issue #48 rather than fixed here.

#### 2026-09-01 14:09:43.294+02:00 — New ADR for the revised range/windowing contract

ADR 36905d5b's Consequences record the old `begin`/`end` + `N+1` contract, so
the revision gets its own ADR (draft at implementation start, accepted at
close) referencing 36905d5b without superseding it — that ADR's dispatch-only
decision stands unchanged.

#### 2026-09-01 14:09:43.294+02:00 — get windowing: raw-only, clamping; update splice: strict

Window coordinates on `get_<d>` are valid with `raw=True` only (a parsed
document requires the whole body; coordinates with `raw=False` raise
`ValueError`) and out-of-range values clamp instead of erroring, matching the
`list_<d>` paging convention — reads are non-destructive. The `update` splice
path stays strict (`ValueError`, never clamped) because a silently shifted
range would corrupt the document. `get_adr` is untouched (no `raw` mode).

#### 2026-09-01 14:09:43.294+02:00 — update's limit: omitted means through end of body

`offset` enters range mode; `limit` is a count (`offset..offset+limit-1`)
like the `read` tool's, with `0` = pure insert and omitted = through end of
body — rationale: preserves every capability of today's `end=N+1` sentinel
without forcing the client to know `N`, while `offset=N+1` keeps the virtual
append position.

#### 2026-09-01 14:09:43.294+02:00 — Hard rename, no begin/end compatibility alias

The parameter rename is breaking and lands in one release with every
LLM-facing text (prompt data files, tool descriptions, docstrings,
`AGENTS.md`) moved to `offset`/`limit` — rationale: pre-1.0 surface, LLM
clients re-read tool descriptions each session, a dual-named parameter set
would steer agents at the older names, and repo precedent favors clean
breaks.

### Related PRs / Commits

- [Issue #28](https://github.com/dfch/biz.dfch.SpecMgr/issues/28): the source request — `specmgr_get` and `specmgr_update` must both support offset and limit.

- [Issue #48](https://github.com/dfch/biz.dfch.SpecMgr/issues/48): the deferred `create_feat` id behaviour + the additional `set_feat_id` tool (out of scope for this feature).

### More Information

Operational notes for the implementing session:

- Work in the git worktree
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-28-get-update` on branch
  `feat-28-get-update` (synced to upstream `dev` `8c13e16` as of 2026-09-01).
  Never push.

- Per-phase commits follow the repo's Conventional Commit style with the
  issue number as scope: `feat(28): …` for implementation phases,
  `docs(28): …` for docs-only phases.

- The connected specmgr MCP server resolves its base directories relative to
  its own cwd (`.specmgr/feat`, `docs/adr`; no `SPECMGR_*` env vars are
  set). After creating any file via the specmgr tools (e.g. the Task 0.5
  ADR), verify it landed in this worktree via `git status` before
  proceeding.

- Task 0.5: create the ADR via `specmgr_create_adr` (it lands in
  `docs/adr/`), then regenerate `docs/adr/README.md` via
  `uv run --frozen specmgr adr-toc` before the Phase 0 gate commit.

- "read-style" coordinates refer to the `read` tool convention the calling
  agent knows: `offset` = 1-based line number to start at, `limit` = number
  of lines to read.
