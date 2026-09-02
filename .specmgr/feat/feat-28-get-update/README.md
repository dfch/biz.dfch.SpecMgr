---
created: '2026-09-01T14:19:27.649184'
id: feat-28-get-update
status: in-progress
type: feat
updated: '2026-09-02T02:22:14.617316'
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
- [x] Task 0.4: Annotate `feat-7` Task 0.32 with the "split out into `feat-28-get-update`" pointer (Task 0.15 → feat-13 precedent) and bump `feat-7`'s frontmatter `updated` + a Recent Updates entry — depends on: none — status: done (2026-09-01)
- [x] Task 0.5: Create the ADR recording the revised `offset`/`limit` contract (draft; set to accepted at close) — depends on: none — status: done (2026-09-01, ADR `4ec08dcb-fcb7-4961-abaf-ff7803e2f21d`)
- [x] Task 0.6: Phase gate — complete test cycle + commit — depends on: Task 0.4, Task 0.5 — status: done (2026-09-01)

#### Phase 1: update Core (offset/limit Rename)

- [x] Task 1.1: Rework `general/tools/_splice.py` — `splice_body(current_body, offset, limit: int | None, content)` per the Design Notes contract (omitted limit = through end of body, 0 = insert, strict validation), module docstrings — depends on: Phase 0 — status: done (2026-09-01)
- [x] Task 1.2: Rework `general/tools/update.py` — public `offset`/`limit` parameters, new guard (`limit` without `offset` → `ValueError` before any file access), eleven `_update_<d>` adapter signatures, `_ADAPTERS` Callable type, tool description, docstrings — depends on: Task 1.1 — status: done (2026-09-01)
- [x] Task 1.3: Migrate every `update(begin=, end=)` test call site in the same commit — `tests/general/tools/test_update.py` (range cases re-expressed + all error cases incl. the new guard + input-schema assertions on `offset`/`limit`), the eleven `tests/<d>/tools/test_get_<d>.py` round-trip lines, `tests/feat/tools/test_integration.py`, `tests/sop/tools/test_integration.py` — depends on: Task 1.2 — status: done (2026-09-01)
- [x] Task 1.4: Phase gate — complete test cycle + doc regeneration + commit — depends on: Task 1.3 — status: done (2026-09-01)

#### Phase 2: get Windowing

- [x] Task 2.1: Add the no-I/O `window_body(text, offset, limit)` helper to `general/tools/_splice.py` (clamping per Design Notes) — depends on: Phase 1 — status: done (2026-09-01)
- [x] Task 2.2: Extend the eleven `get_<d>` tools — `offset`/`limit` parameters, raw-only guard, windowing via the shared helper, tool descriptions, docstrings — depends on: Task 2.1 — status: done (2026-09-01)
- [x] Task 2.3: New `tests/general/tools/test__splice.py` — direct unit tests for `window_body` (defaults, mid window, `offset>N` → `""`, `limit` capping, `limit=0`) and `splice_body`'s new signature — depends on: Task 2.1 — status: done (2026-09-01)
- [x] Task 2.4: Extend the eleven `tests/<d>/tools/test_get_<d>.py` — window slice equality, clamp/empty cases, coordinates + `raw=False` → `ValueError`, windowed read-into-splice round-trip — depends on: Task 2.2 — status: done (2026-09-01)
- [x] Task 2.5: Phase gate — complete test cycle + doc regeneration + commit — depends on: Task 2.4 — status: done (2026-09-01)

#### Phase 3: LLM-facing Contract

- [x] Task 3.1: Rewrite the range-update step in the ten `*_update_instructions.md` data files + `qa_refine_instructions.md` to `offset`/`limit` (incl. the `N+1` append wording) — depends on: Phase 2 — status: done (2026-09-02)
- [x] Task 3.2: Update the ~12 prompt test files asserting the old `begin=..., end=...` literals (`tests/req/prompts/`, `tests/tsk/prompts/`, `tests/qa/prompts/` (incl. `test_refine.py`), `tests/prb/prompts/`, `tests/gol/prompts/`, `tests/rsk/prompts/`, `tests/dec/prompts/`, `tests/sop/prompts/`, `tests/feat/prompts/`, `tests/vcr/prompts/`) to the new literals — depends on: Task 3.1 — status: done (2026-09-02)
- [x] Task 3.3: Phase gate — complete test cycle + commit — depends on: Task 3.2 — status: done (2026-09-02)

#### Phase 4: Docs, Regen, Close

- [ ] Task 4.1: Update `server.py` + `general/tools/__init__.py` docstrings, `AGENTS.md` (eleven per-domain `raw` bullets + the generic `update` bullet), `CHANGELOG.md` `[Unreleased]` (Changed: breaking `begin`/`end` → `offset`/`limit` rename; Added: `get_<d>` windowing) — depends on: Phase 3 — status: not-started
- [ ] Task 4.2: Regenerate `specmgr mcp-docs` (+ `specmgr docs`/`specmgr adr-toc` drift check) — depends on: Task 4.1 — status: not-started
- [ ] Task 4.3: Set the ADR to `accepted`; annotate `feat-7` Task 0.32 done (split-out feature complete); set this feature's status to `done` — depends on: Task 4.2 — status: not-started
- [ ] Task 4.4: Final phase gate — complete test cycle + final commit — depends on: Task 4.3 — status: not-started

## Progress

### Current Status

**As of 2026-09-02**: Phase 3 complete. Every packaged LLM-facing
instruction data file now teaches the new `offset`/`limit` range
contract: the ten `*_update_instructions.md` files
(`req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`) read
"identify the 1-based line to start at and how many lines to replace --
`offset` is the first body line, `limit` the number of lines
(`offset`..`offset+limit-1`); `limit` omitted replaces through the last
body line, `limit=0` is a pure insert, and the `N+1` position is
end-of-body: `offset = N+1` appends after the last line" and name the
call shape `update(id, type="<d>", content, offset=..., limit=...)`;
their whole-body bullets now say "with no `offset`/`limit`"; and
`qa_refine_instructions.md`'s clean-append step uses `offset=N+1`. The
`feat`/`vcr` files keep their own local bullet structure around the
swapped vocabulary. The prompt tests moved to the new literals in the
same change (the ten `test_update_*` files plus
`tests/qa/prompts/test_refine.py`), and one Phase-1 leftover docstring
in `tests/sop/tools/test_integration.py` was reworded to
`offset`/`limit`. The ADR recording the revised contract remains
drafted (`4ec08dcb-fcb7-4961-abaf-ff7803e2f21d` in `docs/adr/`; set to
accepted at close per Task 4.3). The working tree is on branch
`feat-28-get-update`, with the complete test cycle green (2784 tests)
and `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` regenerated without
drift; never pushed. Next: Phase 4 (docs — the `server.py` +
`general/tools/__init__.py` docstrings, `AGENTS.md`, `CHANGELOG.md`
`[Unreleased]`, final regeneration, ADR to accepted).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 02:22:14.617+02:00 — Phase 3 complete (LLM-facing contract: instruction data files + prompt tests moved to `offset`/`limit` in the same change, gate green)

Task 3.1: the ten packaged `*_update_instructions.md` data files
(`req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr` — no `uc`,
no prompts package; no `adr`, different mechanism) rewritten in the
"Line-range replace" bullet to the new coordinate wording: "identify
the 1-based line to start at and how many lines to replace -- `offset`
is the first body line, `limit` the number of lines
(`offset`..`offset+limit-1`); `limit` omitted replaces through the last
body line, `limit=0` is a pure insert, and the `N+1` position is
end-of-body: `offset = N+1` appends after the last line -- and call
`update(id, type=\"<d>\", content, offset=..., limit=...)`", and in the
"Whole-body replace" bullet "with no `begin`/`end`" → "with no
`offset`/`limit`". The seven req-shaped files
(`req`/`tsk`/`prb`/`gol`/`rsk`/`dec`/`sop`) take the target wording's
own line breaks verbatim; `qa` keeps its wider wrap style (the
orphaned "passing only" its old wrap produced was rejoined); `feat`
keeps its long trailing-`update(...)`-call line and its extra
`### Updates`/`### Decisions Made` insert sentence; `vcr` keeps its
own-line call + "passing only" continuation and its
"one paragraph, field, or acceptance criterion" bullet opening.
`qa/data/qa_refine_instructions.md`'s "Persist the appended questions"
clean-append step: `update(id, type="qa", content, begin=N+1, end=N+1)`
→ `update(id, type="qa", content, offset=N+1)` (limit omitted is the
append case; the `N+1` end-of-body wording kept). The only `begin`
left in `src/` markdown is the prose word in
`sop/data/sop_example.md:17` ("can begin productive work" — not a
range reference, deliberately untouched). Task 3.2: the ten
`test_update_*` prompt test files (`tests/{req,tsk,qa,prb,gol,rsk,dec,
sop,feat,vcr}/prompts/`) — each `test_mentions_range_update_flow` now
asserts the new literals, byte-identical to the data files:
`assertIn("offset = N+1", result)` and
`assertIn('update(id, type="<d>", content, offset=..., limit=...)',
result)` plus the matching `result.index(...)` ordering assertion; the
now-stale `assertIn("1-based, inclusive line range", result)` (that
phrase no longer exists in the new wording) was replaced by
`assertIn("1-based line to start at and how many", result)`, a phrase
that is contiguous on a single data-file line in all ten domains; the
method docstrings reworded to the `offset`/`limit` vocabulary.
`tests/qa/prompts/test_refine.py` — `test_mentions_n_plus_one_append_
range` literal `update(id, type="qa", content, begin=N+1, end=N+1)` →
`update(id, type="qa", content, offset=N+1)` (assertIn + index; the
docstring's "N+1 end-of-body append range" wording stays valid and was
kept). Beyond the verified 11-file list, one Phase-1 leftover:
`tests/sop/tools/test_integration.py`'s module docstring still said the
round-trip exercises "line-range (`begin`/`end`) branches of `update`"
while the test itself (line 169) calls `update(..., offset=k, limit=1)`
— reworded that one line to `offset`/`limit`. The intentional
`assertNotIn("begin", schema["properties"])` negative assertions in
`tests/general/tools/test_update.py` and the ACC-006 end-to-end walk's
real `update(..., offset=line_number, limit=1)` call (Phase 1) were
left untouched. All 144 prompt tests pass, proving the asserted
literals match the data files exactly. Task 3.3 gate (green): `ruff
format --check` (1475 files already formatted), `ruff check` (All
checks passed!), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), full `unittest` suite (Ran 2784 tests — OK; same
count as the Phase 2 baseline — data-file + literal changes only, no
tests added or removed), `specmgr docs` + `specmgr mcp-docs`
regenerated with no drift (`git status --short` byte-identical before
and after the runs — data files are not API docstrings and no tool
descriptions change in Phase 3). ACC-004 repo searches: `grep -rn
"begin" src/biz/dfch/specmgr --include=*.md` shows only the
`sop_example.md:17` prose word; `grep -rn "begin=\|end=\|begin\b"
src/biz/dfch/specmgr --include=*.py` shows only the two known Phase-4
items (`server.py:215` and `general/tools/__init__.py:24` docstrings)
plus two prose "to begin with" docstring hits in
`rsk/tools/__init__.py:28` and `tsk/tools/__init__.py:28` — no
`begin`/`end` range references remain in `src/`. Not committed (the
orchestrator commits); not pushed.

#### 2026-09-01 21:59:07.448+02:00 — Phase 2 complete (get windowing: `window_body` helper + `offset`/`limit` on the eleven `get_<d>` tools, gate green)

Task 2.1: `general/tools/_splice.py` gains the no-I/O
`window_body(text, offset=1, limit=None)` helper (added to `__all__`
beside `body_text`/`splice_body`): read-style windowing with clamping,
never erroring — `offset` floors to 1, `offset > N` (incl. empty text)
returns `""`, `limit` caps at the remaining lines (`None` = through end
of body, negative = `""`), and the result keeps each window line's
trailing newline (`""` for an empty window, else
`"\n".join(lines[start-1 : start-1+count]) + "\n"`), so the defaults
reproduce a normal trailing-newline body byte-for-byte and consecutive
non-overlapping windows concatenate back to the body; the module
docstring moves to the three-helper shape and the raw/splice invariant
paragraph extends (windowed or not, `window_body` is the single
windowing definition shared by all eleven tools). Task 2.2: the eleven
`get_<d>` tools (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/
`feat`/`vcr`) extended — signature `get_<d>(id, raw=False, offset=None,
limit=None)`, a raw-only guard before any file access (coordinates with
`raw=False` → `ValueError` naming both values, `update`-guard style),
the raw branch returning `body_text(path)` directly when both
coordinates are omitted (byte-for-byte pass-through, no rejoin) and
`window_body(text, offset or 1, limit)` otherwise, not-found behaviour
unchanged (incl. windowed raw mode), the `@mcp.tool` descriptions
extended with the windowing sentence, the docstrings gained
`offset`/`limit` Parameters entries + a `ValueError` Raises entry, the
stale Phase-1 `begin`/`end` wording in the `raw` parameter reworded to
`offset`/`limit` and extended for the window, and the module
docstrings' `raw=True` paragraphs extended for the windowing capability
(feat's folder-convention `id` docstring kept). Task 2.3: new
`tests/general/tools/test__splice.py` (18 direct no-I/O tests):
`window_body` defaults byte-for-byte, mid window, `offset > N` → `""`,
limit capping, `limit=0` → `""`, `offset < 1` floors, negative limit →
`""`, empty text → `""`, consecutive-window concatenation; and
`splice_body`'s new signature — single-line replace, multi-line replace,
omitted limit through end, `limit=0` mid-body insert, `offset=N+1`
append (both limit forms), and each strict branch (`offset<1`,
`offset>N+1`, `limit<0`, `offset+limit-1>N`) raising `ValueError`
naming the offending value(s). Task 2.4: the eleven
`tests/<d>/tools/test_get_<d>.py` extended (four new tests per domain,
mirroring the existing style/naming): window slice equality (offset=2,
limit=3 vs the seeded body's lines), clamp/empty cases (`offset` past
the last line → `""`; oversized `limit` caps at the remaining lines),
coordinates + `raw=False` → `ValueError` (offset/limit and limit-only
variants; message names raw), and the windowed ACC-003
read-into-splice round-trip (windowed raw read at domain-specific
`k`/`m` asserted equal to the full read's slice, same-count replacement
fragment spliced via the generic `update` at those coordinates, replaced
lines equal the fragment and unchanged regions byte-identical); the
existing both-modes not-found tests each gained a windowed raw
assertion. All pre-existing tests pass unchanged (default raw read
byte-for-byte identical). Task 2.5 gate (green): `ruff format --check`
(1475 files already formatted — 1474 + the new test file), `ruff check`
(All checks passed!), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), full `unittest` suite (Ran 2784 tests — OK; 2722 +
18 new `test__splice` + 44 new per-domain window tests), `specmgr docs`
+ `specmgr mcp-docs` regenerated (only the eleven
`docs/api/...get_<d>.md` pages, `docs/api/..._splice.md`,
`docs/api/README.md`, `docs/GENERATED.md` — test-file count 318 → 319 —
and `docs/MCP.md`'s eleven `get_<d>` entries changed; a second
regeneration run is byte-identical, no drift). Not committed (the
orchestrator commits); not pushed.

#### 2026-09-01 18:04:04.427+02:00 — Phase 1 complete (update core `begin`/`end` → `offset`/`limit` rename + test migration, gate green)

Task 1.1: `general/tools/_splice.py` reworked — `splice_body(current_body,
offset, limit, content)` now takes read-style coordinates (`offset` =
1-based first line to replace, `limit` = count; omitted `limit` = through
end of body, `0` = pure insert, `offset=N+1` = virtual end-of-body append
position) with strict validation (`offset<1`, `offset>N+1`, `limit<0`,
`offset+limit-1>N` each raise `ValueError` naming the offending value(s)
and the allowed range; never clamped); the module and `body_text`
docstrings move to the new vocabulary (and the stale "seven get tools"
count is corrected to eleven). `window_body` deliberately not added yet
(Phase 2, Task 2.1). Task 1.2: `general/tools/update.py` reworked — public
`offset`/`limit` parameters, the old both-or-neither guard replaced by
`limit` without `offset` → `ValueError` before any file access, all eleven
`_update_<d>` adapter signatures/branches/`splice_body` calls updated,
`_update_req` docstring and the module docstring reworded, the `@mcp.tool`
description rewritten for the new contract. Task 1.3: every
`update(begin=, end=)` test call site migrated — `tests/general/tools/
test_update.py` (success cases re-expressed per the Design Notes mapping,
error cases re-expressed incl. the new pre-file-access guard tested
against both a non-existent and an existing id, `TestUpdateRegistration`
now asserts `offset`/`limit` in the input schema, that `begin`/`end` are
gone, and that `required` is unchanged), the eleven
`tests/<d>/tools/test_get_<d>.py` round-trip lines,
`tests/feat/tools/test_integration.py`, `tests/sop/tools/test_integration.
py`, and — beyond the Task 1.3 list — the real ACC-006 end-to-end prompt
walk call site in `tests/feat/prompts/test_update_feat.py` (its comment
too); the prompt-literal `assertIn("begin=..., end=...")` assertions in
the `*_prompts` test files were left untouched per the Phase 3 boundary.
Task 1.4 gate (green): `ruff format --check` (1474 files already
formatted), `ruff check` (All checks passed!), `vulture src/ whitelist.py
--min-confidence 60` (clean, no output), full `unittest` suite (Ran 2722
tests — OK), `specmgr docs` + `specmgr mcp-docs` regenerated (only
`docs/api/..._splice.md`, `docs/api/...update.md`, and `docs/MCP.md`'s
`update` entry changed; re-run shows no drift). One flagged observation:
`general/tools/__init__.py`'s package docstring still describes the old
`begin`/`end` range (and predates the dec/sop/feat/vcr domains) — left
untouched as the Phase 4 item the prompt lists under "do not touch"; the
Phase 1 sanity grep therefore shows exactly that one file as the only
`begin`/`end` range vocabulary remaining in `src/biz/dfch/specmgr/
general/`. Not committed (the orchestrator commits); not pushed.

#### 2026-09-01 15:58:41.327+02:00 — Phase 0 complete (feat-7 split-out annotation, ADR draft, gate green)

Task 0.4: feat-7's Task 0.32 annotated per the Task 0.15 → feat-13
precedent — checkbox `[x]`, status set to "split out into
`feat-28-get-update` (GitHub issue #28,
`.specmgr/feat/feat-28-get-update/README.md`) on 2026-09-01" plus a clause
noting the revised contract (`offset`/`limit` for the generic `update` tool
+ windowed `get_<d>` reads, hard rename, ADR draft) is recorded in this
plan; feat-7 frontmatter `updated` bumped to 2026-09-01; a new `#### Update
2026-09-01 (Task 0.32 split out)` entry prepended to feat-7's Recent Updates
(the indented Background paragraph left untouched). Task 0.5: ADR
`4ec08dcb-fcb7-4961-abaf-ff7803e2f21d` ("offset/limit coordinates for the
generic update tool and get_<d> windowed reads") created via
`specmgr_create_adr` with status `draft` (set to accepted at close, Task
4.3) — six options across the three decided axes (hard rename vs. dual
alias; strict vs. clamping splice validation; raw-only vs. both-modes
windowing), the exact `offset`/`limit` semantics including the today→new
`begin`/`end` mapping table, and Consequences naming every LLM-facing
surface that moves in the same release; references ADR
36905d5b-8057-4294-8665-c7eed5534db0 without superseding it. Verified via
`git status` that it landed in this worktree's `docs/adr/`, then `uv run
--frozen specmgr adr-toc` regenerated `docs/adr/README.md`. Task 0.6 gate
(green): `ruff format --check` (1474 files already formatted), `ruff check`
(All checks passed!), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), full `unittest` suite (Ran 2720 tests — OK). No `src/`
changes, so no `specmgr docs`/`mcp-docs` regeneration needed. Not committed
(the orchestrator commits); not pushed.

#### 2026-09-01 15:13:17.413+02:00 — Merged upstream dev (8e07594)

Upstream `dev` advanced one commit (`8e07594 fix(40): specmgr docs prunes
stale docs/api pages`); merged it into this branch (merge commit `e5d665b`,
no conflicts) and re-ran the complete test cycle — 2720 tests green (up from
2713, the merged commit added 7), `ruff format --check`/`ruff check`/
`vulture` clean. Not pushed. The `More Information` sync reference was
updated to the new dev tip.

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
  `feat-28-get-update` (synced to upstream `dev` `8e07594` as of 2026-09-01,
  via merge commit `e5d665b`). Never push.

- If re-syncing with upstream `dev` before starting implementation: the
  branch now carries local commits, so after `git fetch origin` use
  `git rebase origin/dev` (the Phase 0 `--ff-only` merge no longer applies),
  then re-run the complete test cycle before touching code.

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
