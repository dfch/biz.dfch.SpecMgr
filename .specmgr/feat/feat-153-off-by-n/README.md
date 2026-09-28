---
classification: null
created: '2026-09-26T18:33:23.901+02:00'
id: feat-153-off-by-n
status: planning
type: feat
updated: '2026-09-28T07:01:30.000+02:00'
version: 1.0.0
---

# Feature: Off-by-N line-offset corruption risk in the generic update tool

## Plan

### Overview

The generic `update` tool's line-range mode (`offset`/`limit`) addresses 1-based lines of the frontmatter-stripped body, sourced correctly only via `get_<d>(id, raw=True)`. GitHub issue #153 reports two independent gaps that let a wrong-but-in-bounds `offset` silently corrupt a document: (1) nothing warns that the on-disk file's YAML frontmatter block is variable-length, so computing a body-line offset as "raw file line number minus an assumed frontmatter length" is unsafe -- yet `feat`'s own AGENTS.md-sanctioned direct-file-editing workflow invites exactly that; and (2) `update` is "splice-then-validate-whole": a wrong offset that lands on a structurally similar line (e.g. a blank line instead of the intended list item) can still pass schema validation and is written with no feedback at all, leaving silent duplication/loss discoverable only by an unprompted manual re-read.

This feature closes issue #153 by adopting three of its four suggested fixes: (1) documenting the coordinate mismatch explicitly in `update`'s tool description and AGENTS.md's `feat` entry; (2) returning a small, bounded before/after snippet of the touched region on every successful `update` call, via a new `UpdateResult` wrapper return type; and (4) adding an opt-in `numbered` parameter to every `get_<d>(raw=True)` read so a caller can see 1-based body-line numbers without manually counting. The optional `dry_run` parameter (fix #3) is explicitly deferred -- not part of this feature.

Note that the snippet (fix #2) is detection, not prevention: since `dry_run` is deferred, a wrong `offset` is still written to disk before the caller ever sees the returned snippet. Recovery from a bad write is a follow-up manual `update` call, not an automatic rollback.

### Requirements

- REQ-001: `update`'s tool description/docstring and AGENTS.md's `feat` entry state explicitly that a raw on-disk `.md` file's line numbers are never the same as `update`'s `offset`/`limit` body-line coordinates -- the YAML frontmatter block is variable-length -- and that the only safe source of coordinates is `get_<d>(id, raw=True)`, never a raw file read minus an assumed constant.

- REQ-002: In range mode (`offset` given), `update` returns a new wrapper result type (`UpdateResult` or similar) carrying the existing per-domain `frontmatter` plus a `snippet`: the lines dropped (before) and inserted (after) by the splice, plus 2 lines of unchanged context immediately above and below the touched range. Before-lines are labeled with their original **pre-splice** 1-based body-line numbers (they no longer exist afterward, so no post-splice number applies to them); after-lines and context lines are labeled with their **post-splice** 1-based body-line numbers. When the number of removed lines (`limit`) differs from the number of inserted lines, the before- and after-line-number sequences are not guaranteed to be contiguous or to overlap -- this is expected and must not be "fixed" by re-numbering one side to match the other.

- REQ-003: In whole-body mode (no `offset`), `update` returns the same wrapper type with `snippet=None`, so the return shape is uniform across both modes and every whole-body domain.

- REQ-004: Every whole-body domain's `get_<d>` tool gains a new `numbered: bool = False` parameter, meaningful only combined with `raw=True`: when `True`, each line of the returned raw text is prefixed with its 1-based body-line number in `"<n>: "` form (mirroring this environment's own file-reading tool's convention); the default (`False`) preserves today's exact byte-verbatim `raw=True` output. When `numbered=True` is combined with `offset`/`limit` windowing, the printed numbers are the line's **absolute** position in the full body (matching `update`'s own coordinate space), starting at the **clamped** offset `max(1, k)` (a `k < 1` window starts at `1`; a `k > N` window is empty and prints no numbers) and never restarting at `1` within a valid window -- this is the entire point of the feature: a caller must be able to feed a number seen here straight back into `update`'s `offset`. Since feat-150 (PR #155, merged into upstream dev) gave every `get_<d>` tool a non-raising `ParseFailureResult` return for a document that exists on disk but fails to parse -- including for `raw=True` reads ("raw=True never returns a broken document's raw text") -- that channel takes precedence over numbering: a numbered read of a parse-failing document returns `ParseFailureResult`, never numbered text; `numbered` adds no new member to the (already-extended) `X | str | ParseFailureResult` return union.

- REQ-005: `numbered=True` combined with `raw=False` raises `ValueError` before any file access, mirroring the existing rule that `offset`/`limit` combined with `raw=False` already raises `ValueError`. Like the existing guard, this fires before the `load_by_id` attempt and the post-feat-150 parse-failure channel, so a misused argument reports `ValueError` even for a document that fails to parse.

- REQ-006: The tool descriptions for both `update` and every `get_<d>` explicitly warn that numbered output must never be fed back verbatim into `content` for `update`/`create_<d>` without first stripping the `"<n>: "` prefix from each line.

- REQ-007: Both changes (the REQ-002/REQ-003 snippet and the REQ-004/REQ-005 `numbered` parameter) apply uniformly across all 12 whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`); `adr` remains excluded, consistent with `update`'s existing scope.

- REQ-008: `server.py`'s module docstring, the regenerated `docs/MCP.md`, the regenerated `docs/api/`, `AGENTS.md`, all 12 `update_<d>` prompt files that narrate the "`get_<d>(raw=True)` -> compute offset -> `update`" workflow, and `CHANGELOG.md` are updated to reflect the new `UpdateResult` return shape, the coordinate-mismatch warning, and the new `numbered` parameter.

- REQ-009: A new ADR is authored and accepted documenting that `update`'s return contract is revised from feature feat-69-update-context's "frontmatter-only" precedent to `frontmatter` + optional `snippet`, scoped to `update` alone -- `create_<d>`, `set_status`, and `set_classification` are unaffected and keep returning bare frontmatter. The ADR also records that `get_<d>`'s post-feat-150 `ParseFailureResult` channel is unaffected by this feature (a numbered read of a parse-failing document returns that channel, never numbered text).

### Acceptance Criteria

- [ ] ACC-001: `update`'s tool description text states, in prose, that the frontmatter block is variable-length and that raw on-disk file line numbers never equal `offset`/`limit` body-line coordinates; the corresponding bullet in AGENTS.md's `feat` entry carries the same warning.

- [ ] ACC-002: Calling `update(id, type, content, offset=k, limit=m)` on any of the 12 whole-body domains returns an object exposing both `frontmatter` and a non-`None` `snippet` string containing the before/after lines of the touched range plus 2 lines of context on each side, each line prefixed with its 1-based number per the pre-splice/post-splice split in REQ-002. This is verified for both a line-for-line replacement (`limit` lines replaced by the same number of lines) and a size-changing replacement (`limit` lines replaced by a different number of lines), confirming the before/after number sequences behave as specified in the size-changing case.

- [ ] ACC-003: Calling `update(id, type, content)` with no `offset` returns the same object shape with `snippet=None`.

- [ ] ACC-004: `get_<d>(id, raw=True, numbered=True)` returns the body text with every line prefixed `"<n>: "` (1-based); `get_<d>(id, raw=True)` (default `numbered=False`) is unchanged and remains byte-identical to today's output. A numbered read of a parse-failing document returns `ParseFailureResult` (never numbered text), consistent with feat-150's `raw=True` contract.

- [ ] ACC-005: `get_<d>(id, raw=False, numbered=True)` raises `ValueError` before any file access, for every one of the 12 domains.

- [ ] ACC-006: The `update` and `get_<d>` tool descriptions each contain an explicit warning against feeding `numbered=True` output back as `content` without stripping the prefix.

- [ ] ACC-007: `server.py`'s docstring, `docs/MCP.md`, `docs/api/`, and AGENTS.md reflect every change above; the repo's own drift checks (`specmgr docs`) pass.

- [ ] ACC-008: The full test suite passes, including new unit tests for the snippet-window helper (boundary clamping at the start/end of the body, whole-body-mode `snippet=None`) and the numbered-line formatter, plus tool tests exercising both features across all 12 domains.

- [ ] ACC-009: A new ADR exists under `docs/adr/`, is `accepted`, and appears in `docs/adr/README.md`'s table of contents after `specmgr adr-toc` regeneration.

- [ ] ACC-010: `CHANGELOG.md`'s `[Unreleased]` section gains a `**BREAKING**` entry describing `update`'s new `frontmatter` + `snippet` return shape.

- [ ] ACC-011: `get_<d>(id, raw=True, numbered=True, offset=k, ...)` returns numbers starting at the **clamped** offset `max(1, k)` (a `k < 1` window starts at `1`; a `k > N` window returns the empty string with no numbers), never restarting at `1` within a valid window and never using the raw requested `k` when it differs from the clamp, confirming numbered output stays in `update`'s absolute coordinate space even when combined with windowing.

- [ ] ACC-012: All 12 `update_<d>` prompt files that narrate the raw-read-then-offset workflow (one per whole-body domain: `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) mention the `numbered` option and the coordinate-mismatch warning.

### Scope

#### Included

- An explicit coordinate-mismatch warning in `update`'s tool description and AGENTS.md's `feat` entry (fix #1).

- A new `UpdateResult`-style wrapper return type for `update`, carrying `frontmatter` + `snippet` (fix #2), with `snippet` populated in range mode only.

- A small, fixed-size (2-line-context) before/after snippet-window helper, shared across all 12 whole-body domains, using the pre-splice/post-splice numbering split from REQ-002.

- A new opt-in `numbered: bool = False` parameter on every domain's `get_<d>` tool, meaningful only combined with `raw=True`, always reporting absolute body-line numbers (fix #4).

- `ValueError` for `numbered=True` combined with `raw=False`.

- Explicit "don't feed numbered output back as content" warnings in both the `update` and `get_<d>` tool descriptions.

- A new ADR documenting the revision to `update`'s return contract.

- `server.py` docstring, `docs/MCP.md`, `docs/api/`, `AGENTS.md`, all 12 `update_<d>` prompt files, and `CHANGELOG.md` updates.

- Unit and tool tests across all 12 whole-body domains.

#### Explicitly Out Of Scope

- The optional `dry_run: bool` parameter on `update` (fix #3) -- explicitly deferred, not part of this feature.

- Any change to `adr`'s own `update_section`/`option_*`/`update_frontmatter` tools (ADR stays excluded from the generic `update` tool).

- The already-merged generic `edit` tool (feat-159-edit, GitHub issue #159). `edit` is a different tool -- exact-match `old_str`/`new_str` with no `offset`/`limit` range mode -- so issue #153's off-by-N corruption risk does not apply to it, and its before/after is self-evident from the match itself. It independently documents a frontmatter-only return and does not share `update`'s return shape, so **no `edit` code or doc change is required by this feature**; declared out of scope here and in Related Decisions below.

- Server-side enforcement that prevents direct raw-file hand-editing of `feat` READMEs -- the sanctioned workflow itself is unchanged; only the coordinate-computation guidance changes.

- A configurable snippet context-line count (fixed at 2 lines, not a new parameter).

### Design Notes

The snippet-window helper lives alongside `body_text`/`splice_body`/`window_body` in `general/tools/_splice.py` (or a new sibling module, e.g. `_snippet.py`, if `_splice.py` grows too large) and stays doc-type-agnostic like its neighbors. It is computed **once**, in `update`'s shared public dispatcher, not duplicated into each of the 12 per-domain `_update_<d>` adapters: each adapter is extended to hand back the pre-splice body, the post-splice body, and the resolved `offset`/`limit` it used, and the dispatcher assembles the `UpdateResult` from that shared information.

Given the pre-splice body, the `offset`/`limit` coordinates, and the post-splice body, the helper computes: the *before* window (the `offset..offset+limit-1` lines as they existed pre-splice, empty for a pure insert/`limit=0`), the *after* window (the lines the fragment actually occupies in the spliced result), and up to 2 lines of unchanged context immediately above and below the touched range in the *post-splice* body (clamped at the start/end of the body, mirroring `window_body`'s own clamp-not-error convention).

Per REQ-002, before-lines are labeled with their **pre-splice** line numbers and after-/context-lines are labeled with their **post-splice** line numbers; the two numbering sequences are independent and need not be contiguous. A line-for-line replacement (1 line removed, 1 line inserted) happens to show the same number on both sides only by coincidence:

```
   3: ## Some Heading
-  4: (old line that was replaced)
+  4: (new line that replaces it)
   5: (unchanged context line)
```

A size-changing replacement (e.g. 1 line removed, 3 lines inserted) does not:

```
   3: ## Some Heading
-  4: (the single old line that was replaced)
+  4: (first new line)
+  5: (second new line)
+  6: (third new line)
   7: (unchanged context line -- was line 5 pre-splice, now line 7 post-splice)
```

`update`'s return type changes from the current per-domain `FooFrontmatter` union to a new `UpdateResult` wrapper (exact name TBD during implementation) exposing `frontmatter: FooFrontmatter` and `snippet: str | None` (populated only in range mode); this is a deliberate, documented narrowing of feature feat-69-update-context's "frontmatter-only" precedent, scoped to `update` alone -- `create_<d>`, `set_status`, and `set_classification` keep returning bare frontmatter, unchanged. Because this reverses a repo-wide precedent for a generic tool used by all 12 whole-body domains, it is recorded in a new ADR (REQ-009) rather than only in this feature's own Decisions Made log.

The `numbered` parameter is implemented by extending `window_body` with a `numbered: bool = False` argument -- `window_body` already computes the clamped `start`, so the `f"{n}: "` prefix reuses that same clamped start directly and is added per returned line only when requested (mirroring the `<line>: <content>` convention this environment's own file-reading tool already uses), with `n` always the line's absolute position in the full body -- not a per-window restart -- so a number seen in a windowed, numbered read can be fed straight back into `update`'s `offset`. No change to `body_text`/`splice_body`, which stay numbering-agnostic since `update`'s range coordinates must keep addressing the *unprefixed* line count. Positioning after feat-150: each `get_<d>` now carries a parse-failure channel (a try/except around `load_by_id` that returns `ParseFailureResult`) ahead of the `if raw:` branch; the numbered wiring sits inside that branch, after the channel. Note also that the current no-window path returns `body_text(path)` directly, bypassing `window_body`, so the implementation must route every raw read through the extended `window_body` (whose defaults already equal the full body) -- or number both branches -- so numbering applies uniformly.

While touching all 12 `get_<d>.py` files anyway, consider factoring the existing (already hand-duplicated 12x) "`offset`/`limit` combined with `raw=False` raises `ValueError`" guard together with the new "`numbered` combined with `raw=False` raises `ValueError`" guard into one shared helper, rather than hand-duplicating a second near-identical guard into all 12 files. This is an opportunistic improvement, not a hard requirement. After feat-150 each of the 12 files also carries the try/except parse-failure channel that must be preserved -- the shared-guard factoring is now more relevant, not less.

### Related Decisions

- Feature feat-69-update-context: established `update`'s current "frontmatter-only" return contract; this feature deliberately revises it for `update` specifically (adds a bounded `snippet` alongside `frontmatter`), without touching `create_<d>`/`set_status`/`set_classification`. Unlike feat-69 itself, this revision is recorded in a new ADR (REQ-009), since it reverses a repo-wide precedent for a tool shared by all 12 domains.

- feat-159-edit (the `edit` tool, already merged -- status `done`): shares the same `general/tools/` dispatch pattern but is a distinct tool (exact-match, no `offset`/`limit` range mode). It independently returns the updated frontmatter only and is unaffected by `update`'s new `UpdateResult` shape, so no reconciliation is needed and `edit` is declared out of scope above; no `edit` code or doc change is required by this feature.

- feat-150 (PR #155, merged into upstream dev): added the non-raising `ParseFailureResult` return channel to all 12 `get_<d>` tools (ADR `9080b37c-82b3-4f63-81f1-79641d0bf14c`) -- the companion return-shape change on the same read surface. feat-153's `numbered` parameter and this plan's Phase 0 reconciliation build on top of that baseline; the new ADR (REQ-009) references it.

### Task List

#### Phase 0: Upstream sync (feat-150) & plan reconciliation

- [x] Task 0.1: `git fetch origin` and verify `origin/dev` is exactly this branch's base plus {the v0.33.0 release bump `639ba07`, the feat-150 Phase 1 merge `3569c02` ("feat-150: MCP-native repair command + get_* parse-failure error channel (Phase 1 scope) (#155)")}; then `git merge origin/dev` (expected clean: the only file this branch has changed is this README, which feat-150 does not touch; on any conflict, `git merge --abort` and report -- never force). Baseline note for Task 0.3: feat-150 gives all 12 `get_<d>` tools a non-raising `ParseFailureResult` (`error`/`path`/`id`) return for a document that exists on disk but fails to parse -- including for `raw=True` reads -- via the new `find_parse_failure` helper (`general/tools/_doc_paths.py`, plus `feat/tools/_paths.py` for the bespoke `feat` domain).

- [x] Task 0.2: Full quality gate on the merged tree: `uv run --frozen ruff format --check && uv run --frozen ruff check`, then `uv run --frozen pytest -n auto --cov=src --cov-report=` (expected green -- feat-150's suite already passed on dev, and this branch adds no code).

- [x] Task 0.3: Reconcile this plan against the post-feat-150 `get_*` baseline: (a) REQ-004 -- state that `numbered` applies only to parseable documents; a numbered read of a parse-failing document returns `ParseFailureResult`, never numbered text (no new return member is added to the already-extended `X | str | ParseFailureResult` union); (b) REQ-005 -- state that the `numbered`+`raw=False` `ValueError` fires before the `load_by_id` attempt / parse-failure channel (same early position as the existing `offset`/`limit` guard), so a misused argument reports `ValueError` even for a broken document; (c) ACC-004 -- add the clause "a numbered read of a parse-failing document returns `ParseFailureResult` (never numbered text)"; (d) Design Notes -- the numbered wiring sits inside the `if raw:` branch after the parse-failure channel, and since the current no-window path returns `body_text(path)` directly (bypassing `window_body`), all raw reads must be routed through the extended `window_body` (or both branches numbered); the shared-guard factoring note is now more relevant because each of the 12 files also carries the try/except parse-failure channel that must be preserved; (e) Task 3.3 -- the `get_<d>` `@mcp.tool` description/docstring now carry feat-150's `ParseFailureResult` text: append the numbered explanation + "don't feed back verbatim" warning, never replace; (f) Task 4.1 -- AGENTS.md now carries feat-150's additions (the `repair` prompt, the `get_*` parse-failure channel in the `general` bullet): feat-153's edits layer on top, not replace; (g) Task 5.3 -- the per-domain `test_get_<d>.py` files already hold feat-150's parse-failure test classes: the numbered tests join the same files, including the broken-document -> `ParseFailureResult` case; (h) REQ-009 + Related Decisions -- feat-150's ADR `9080b37c-82b3-4f63-81f1-79641d0bf14c` (structured parse-failure result for `get_*`) is the companion return-shape change on the same read surface: add a Related-Decisions bullet, and the new ADR (REQ-009) references it and records that the `ParseFailureResult` channel is unaffected by this feature.

- [x] Task 0.4: Record Phase 0 in Progress: prepend an Updates note (clean merge, green gate, reconciliation per Task 0.3), update Current Status's "As of" date, bump frontmatter `updated`, check boxes 0.1--0.4, and commit (docs only; the merge commit already exists from Task 0.1).

- [x] Task 0.5: `git push` and verify PR #164 is OPEN and shows the merge commit plus the Task 0.4 commit (never merge or close the PR); check this box, commit, and push again.

#### Phase 1: Design

- [ ] Task 1.1: Finalize the `UpdateResult` wrapper shape and the snippet-window algorithm (pre-splice/post-splice before/after numbering split, 2-line context, boundary clamping) from this feature's Design Notes

- [ ] Task 1.2: Finalize the `numbered` parameter contract for `get_<d>` (opt-in, raw-only, absolute body-line numbers even under windowing, `ValueError` when combined with `raw=False`) and the exact `"<n>: "` line-prefix format

- [ ] Task 1.3: Draft the new ADR (REQ-009) revising feature feat-69-update-context's "frontmatter-only" return precedent for `update` and get it accepted before/alongside implementation

#### Phase 2: Implementation -- update() snippet

- [ ] Task 2.1: Add a snippet-window helper (pre-splice/post-splice before/after lines + 2-line context) alongside `body_text`/`splice_body`/`window_body` in `general/tools/_splice.py`

- [ ] Task 2.2: Introduce the `UpdateResult` wrapper type; extend `update`'s per-domain `_update_<d>` adapters to hand back the pre-splice body, post-splice body, and resolved `offset`/`limit`, and compute the snippet once in the shared public dispatcher (range mode populates `snippet`; whole-body mode sets `snippet=None`)

- [ ] Task 2.3: Update `update`'s tool description/docstring with the coordinate-mismatch warning (fix #1) and the "never feed a numbered read back as content" warning

#### Phase 3: Implementation -- numbered raw reads

- [ ] Task 3.1: Add the `numbered: bool = False` parameter to every one of the 12 domains' `get_<d>` tools, wired through the extended `window_body` (new `numbered` argument) and `body_text` helpers, always reporting absolute body-line numbers

- [ ] Task 3.2: Enforce `ValueError` for `numbered=True` combined with `raw=False`, before any file access (consider factoring this together with the pre-existing, already-duplicated `offset`/`limit`-with-`raw=False` guard into one shared helper while touching all 12 files anyway)

- [ ] Task 3.3: Update every `get_<d>` tool description/docstring with the numbered-format explanation and the "don't feed back verbatim" warning, **appended to** the `ParseFailureResult` channel text feat-150 already added to those descriptions/docstrings (never replacing it)

#### Phase 4: Docs

- [ ] Task 4.1: Update AGENTS.md's `feat` entry and the `general`/`update` bullet with the coordinate-mismatch warning and the new `UpdateResult`/`numbered` capabilities; AGENTS.md now also carries feat-150's additions (the `repair` prompt, the `get_*` parse-failure channel in the `general` bullet) -- feat-153's edits layer on top, not replace

- [ ] Task 4.2: Update all 12 `update_<d>` prompt files (one per whole-body domain: `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) that narrate the raw-read-then-offset workflow to mention `numbered=True` and the coordinate-mismatch warning

- [ ] Task 4.3: Add a `CHANGELOG.md` `[Unreleased]` `**BREAKING**` entry for `update`'s new `frontmatter` + `snippet` return shape

- [ ] Task 4.4: Regenerate `docs/MCP.md`, `docs/api/`, and `docs/adr/README.md` via `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc`

#### Phase 5: Tests & Quality Gate

- [ ] Task 5.1: Unit tests for the snippet-window helper (before/after content, 2-line context, boundary clamping at body start/end, pure-insert/append cases, and a size-changing replacement case verifying the pre-splice/post-splice before/after numbering split from REQ-002)

- [ ] Task 5.2: Unit tests for the numbered-line formatter (format, default-off behavior, `ValueError` path, and absolute-vs-window-relative numbering when combined with `offset`/`limit`)

- [ ] Task 5.3: Tool tests across all 12 whole-body domains for both features (happy path, whole-body-mode `snippet=None`, numbered on/off, `ValueError` paths); the per-domain `test_get_<d>.py` files already hold feat-150's parse-failure test classes -- the numbered tests join the same files, including the broken-document -> `ParseFailureResult` case

- [ ] Task 5.4: Run ruff/pylint/vulture and the full test suite (phase-end quality gate)

## Progress

### Current Status

**As of 2026-09-28**: Feature drafted for GitHub issue #153; design decisions confirmed with the author (three of the issue's four suggested fixes adopted -- explicit documentation, a bounded before/after snippet via a new `UpdateResult` wrapper, and an opt-in `numbered` parameter on `get_<d>(raw=True)`; the optional `dry_run` parameter is explicitly **not** adopted). A follow-up review pinned down the snippet's pre-splice/post-splice numbering split for size-changing replacements, confirmed `numbered` reports absolute (not window-relative) body-line numbers, added a new ADR requirement for the return-contract revision, and added missing `CHANGELOG.md`/prompt-file update tasks. A second refinement pass corrected factual references (12, not 11, `update_<d>` prompt files; the related tool is the already-merged `edit`, not an unmerged `replace`), removed a dead AGENTS.md sub-task, added the regenerated `docs/api/` to REQ-008, and pinned the numbered-read start to the clamped offset. Phase 0 (upstream sync) is complete: upstream dev -- which now carries feat-150's non-raising `ParseFailureResult` channel on all 12 `get_<d>` tools (PR #155) -- is merged in, and this plan is reconciled to that baseline (Task 0.3). No implementation of Phases 1--5 started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-28T05:01:30.000Z - Phase 0: merged upstream dev (feat-150, PR #155) and reconciled the plan

Upstream `dev` moved past this branch's base by exactly two commits: the v0.33.0 release bump and feat-150's Phase 1 merge (PR #155, "feat-150: MCP-native repair command + get_* parse-failure error channel (Phase 1 scope)"). The `git merge origin/dev` into `feat-153-off-by-n` was clean (no conflicts -- the only file this branch had changed was this README, which feat-150 does not touch). feat-150's `get_*` change: all 12 `get_<d>` tools now return `X | str | ParseFailureResult`; a document that exists on disk but fails to parse returns a non-raising `ParseFailureResult` (`error`/`path`/`id`) instead of the domain not-found error, even for `raw=True` reads, via the new `find_parse_failure` helper. Task 0.3 reconciled this plan to that baseline: `numbered` applies only to parseable documents (a numbered read of a parse-failing document returns `ParseFailureResult`, never numbered text; no new return member); the `numbered`+`raw=False` `ValueError` fires before the parse-failure channel; the numbered wiring sits after that channel inside the `if raw:` branch, with all raw reads routed through the extended `window_body`; the `get_<d>` description/docstring edits append to (never replace) feat-150's `ParseFailureResult` text; the AGENTS.md edits layer on top of feat-150's additions; the numbered tool tests join the same per-domain files as feat-150's parse-failure tests, including the broken-document case; the new ADR (REQ-009) references feat-150's ADR `9080b37c`. Full quality gate (ruff format/check + full pytest suite) green on the merged tree.

#### 2026-09-27T13:23:01.000Z - Second refinement pass: corrected factual references, pinned numbered clamping

A second review (read-only findings, applied in place) corrected: (1) the `update_<d>` prompt-file count is **12, not 11** -- all 12 whole-body domains narrate the raw-read-then-offset workflow, and the old "minus `adr`" phrasing was wrong since `adr` is not one of the 12 (REQ-008, ACC-012, Scope, and Task 4.2 updated; the historical 13:00 note's "11" is left as-is for log integrity); (2) the related-feature cross-reference named a non-existent "feat-159-replace" / unmerged `replace` tool -- it is actually the **already-merged `edit` tool** (feat-159-edit, status `done`), a different tool (exact-match, no `offset`/`limit`) that independently returns frontmatter-only, so it is unaffected by `update`'s new `UpdateResult` shape and needs no code/doc change (Out-of-Scope and Related-Decisions bullets rewritten, `edit` declared out of scope with rationale); (3) removed Task 4.1's instruction to "correct AGENTS.md's existing 'ADR feat-69-update-context' mislabeling" -- no such string exists (AGENTS.md already cites feat-69 correctly as a feature); (4) added the regenerated `docs/api/` to REQ-008 for parity with ACC-007; (5) pinned the numbered-read start to the **clamped** offset `max(1, k)` (a `k < 1` window starts at `1`, a `k > N` window is empty) and named the mechanism: `window_body` gains a `numbered: bool = False` argument so numbering reuses its already-computed clamped start (REQ-004, ACC-011, Design Notes, Task 3.1). No scope change: `dry_run` remains explicitly **not** adopted, `edit` remains out of scope. No implementation started.

#### 2026-09-26T13:00:00.000Z - Refinement pass: fixed gaps, inconsistencies, and an ADR requirement

A review pass found and fixed: (1) a citation error referring to "ADR feat-69-update-context", which is actually a feature folder, not an ADR; (2) an under-specified snippet-numbering scheme for size-changing replacements (before-lines now explicitly use pre-splice numbers, after-/context-lines post-splice numbers, not guaranteed contiguous); (3) an unstated absolute-vs-window-relative numbering rule for `numbered` combined with `offset`/`limit` (now explicitly absolute); (4) a missing `CHANGELOG.md` task, inconsistent with comparable prior features; (5) a missing task to update the 11 `update_<d>` prompt files that narrate the raw-read-then-offset workflow; (6) a missing cross-reference noting feat-159-replace's REQ-006 currently assumes `update`'s pre-this-feature return shape; and (7) added REQ-009/ACC-009/Task 1.3 for a new ADR documenting the return-contract revision, since it reverses a repo-wide precedent (feat-69-update-context) for a tool shared by all 12 whole-body domains -- matching the precedent set by feat-146-date-time for comparably broad, precedent-reversing changes. No implementation started.

#### 2026-09-26T12:00:00.000Z - Created

Feature drafted for GitHub issue #153 (off-by-N line-offset corruption risk in the generic `update` tool). Design decisions on which of the issue's four suggested fixes to adopt, the `UpdateResult` snippet shape, and the `numbered` raw-read parameter contract were confirmed with the author before drafting.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26T13:00:00.000Z - Snippet numbering split, absolute numbered coordinates, and a new ADR

Resolved three open design questions from the refinement review: (1) the snippet's before-lines are labeled with their pre-splice line numbers and after-/context-lines with post-splice line numbers, independently and not guaranteed contiguous, rather than forcing a single "post-splice for everything" scheme that breaks down whenever a replacement changes the line count; (2) `numbered=True` combined with `offset`/`limit` windowing on `get_<d>(raw=True)` always reports absolute body-line numbers (matching `update`'s own coordinate space), never a 1-based restart within the returned window; (3) since this feature reverses feature feat-69-update-context's repo-wide "frontmatter-only" return precedent for a tool shared by all 12 whole-body domains, it is documented by a new ADR (REQ-009) rather than only in this feature's own Decisions Made log, matching the precedent feat-146-date-time set for a comparably broad change.

#### 2026-09-26T12:00:00.000Z - Confirmed which suggested fixes to adopt and their exact shapes

Adopted fixes #1 (explicit documentation), #2 (bounded before/after snippet), and #4 (opt-in numbered raw reads) from GitHub issue #153; fix #3 (`dry_run` parameter) was explicitly deferred. The snippet is a before/after window with 2 lines of unchanged context on each side, populated only in `update`'s range mode; whole-body mode returns `snippet=None`. This requires a new `UpdateResult` wrapper return type for `update` (frontmatter + snippet), a deliberate, documented narrowing of feature feat-69-update-context's "frontmatter-only" precedent scoped to `update` alone. The `numbered` parameter on `get_<d>` is opt-in (default `False`, preserving today's byte-verbatim `raw=True` output), meaningful only combined with `raw=True`; `numbered=True` with `raw=False` raises `ValueError`, mirroring the existing `offset`/`limit`-with-`raw=False` contract.

### Related PRs / Commits

- [Issue #153](https://github.com/dfch/biz.dfch.SpecMgr/issues/153): tracking issue for this feature.
