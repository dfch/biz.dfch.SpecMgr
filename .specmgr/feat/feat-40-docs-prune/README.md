---
created: 2026-09-01
id: feat-40-docs-prune
status: planning
updated: 2026-09-01
version: 1.0.0
---

# Feature: `specmgr docs` prunes stale `docs/api/` pages

## Plan

### Overview

`specmgr docs` regenerates `docs/api/*.md` (one page per importable module,
plus the `README.md` index) and `docs/GENERATED.md` from the source tree, but
it only ever *writes* — it never deletes. When a module is removed from
`src/`, its API page lingers in `docs/api/` forever: an orphaned page no
current index links, a phantom module for readers, and growing noise for
anyone scanning the generated tree.

This is not hypothetical. As of 2026-09-01 the committed `docs/api/` already
holds five stale pages for modules deleted by feat-13-list-paging's
resource→tool conversion: `biz.dfch.specmgr.{adr,qa,req,tsk,uc}.resources.*_list.md`.
`docs/GENERATED.md` is unaffected — it is a single fully-rewritten file; only
the per-module `api/` pages accumulate.

The fix: after writing the current pages, delete every flat `*.md` file in
the output `api/` directory that is not the `README.md` index and does not
correspond to a page written in this run.

### Requirements

- REQ-001: `specmgr docs` deletes stale `api/*.md` pages — any flat
  `*.md` file in the output `api/` directory (default `docs/api/`, or
  wherever `--output` points) whose name is not a page written by the same
  run and is not the generated `README.md` index.
- REQ-002: Pruning is conservative and safe: it touches only flat `*.md`
  files inside the `api/` directory this command manages — never `README.md`,
  never other file types, never nested directories, never anything outside
  that directory. Pruning is skipped entirely rather than deleting the
  existing tree whenever the run cannot be trusted to have written the full
  current set: if a run generates *no* pages at all (e.g. the package import
  fails outright), if any module fails to import mid-run, or if module
  collection is truncated before the walk completes.
- REQ-003: Reproducibility is preserved: on an unchanged tree, repeated
  `specmgr docs` runs remain byte-identical and idempotent, so the
  pre-commit hook and CI drift check (ADR 9c687bb1) keep passing.
- REQ-004: The command reports pruning: the `docs` entry point echoes how
  many stale pages were removed (only when the count is non-zero), next to
  the existing "wrote N module file(s)" line.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — a test pre-seeds a stale `<module>.md`
  page in a scratch `api/` directory, runs `_generate_api_docs` (or the
  `docs()` entry point with `--output`), and asserts the stale file is gone
  while all current module pages and `README.md` remain.
- [ ] ACC-002: Verifies REQ-002 — tests assert (a) `README.md` is never
  pruned, (b) a run that generates zero pages (unimportable package) leaves
  pre-existing files untouched, (c) non-`.md` files and nested directories
  in the `api/` dir are left untouched, and (d) a run in which exactly one
  module fails to import (mocked) skips pruning entirely — pre-seeded stale
  pages remain and the pruned count is 0.
- [ ] ACC-003: Verifies REQ-003 — a test runs generation twice into the same
  scratch directory and asserts the resulting file sets are identical
  (idempotency); the existing signature-stability tests
  (`TestStableSignatureStr`) continue to pass.
- [ ] ACC-004: Verifies REQ-004 — an end-to-end test of `docs()` with a
  pre-seeded stale page asserts the stale page is removed and the echo
  output reports the pruning count.

### Scope

What is included in this feature:

- Pruning logic in `src/biz/dfch/specmgr/commands/docs.py`
  (`_generate_api_docs`, with `_collect_all_modules` gaining the
  `complete` flag), plus the `docs()` entry point's report line.
- Docstring updates: the `docs` command module docstring, the `docs()`
  function docstring, and the `_generate_api_docs` docstring (its return
  changes from `int` to `tuple[int, int]`) gain a sentence that stale pages
  are pruned.
- Tests in `tests/commands/test_docs.py` (ACC-001..ACC-004), plus adapting
  the two existing tests that assert on `_generate_api_docs`'s old `int`
  return.
- One real run of `specmgr docs` to prune the five existing stale pages in
  `docs/api/` and commit the result.
- `docs/coverage.svg` regenerated via `specmgr coverage-badge` — the new
  tests change coverage, and the pre-commit hook plus CI gate on the badge.
- `CHANGELOG.md`: a `### Fixed` entry under `[Unreleased]` for the prune
  behavior (GitHub issue #40).

What is explicitly out of scope:

- `docs/GENERATED.md` — a single fully-rewritten file; nothing to prune.
- `specmgr mcp-docs` / `docs/MCP.md` — also a single fully-rewritten file.
- `specmgr adr-toc` / `docs/adr/README.md` — single regenerated index file.
- Pruning of anything other than flat `*.md` files inside the `api/`
  directory (nested dirs, non-md files are left alone by design, REQ-002).
- Any change to page content, naming, or the index format.

### Dependencies

- Depends on: ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73 (pre-commit/CI
  drift check that makes byte-identical reproducibility, REQ-003, a hard
  constraint).
- Blocks: nothing.

### Design Notes

- **Stale = written-now set complement.** The write loop already knows
  exactly which filenames it wrote (`f"{module_name}.md"` per successfully
  generated page). Pruning is therefore `existing flat *.md in api_dir`
  minus `written filenames` minus `README.md` — no re-import, no
  re-walk, no second source of truth.
- **Guard against catastrophic deletion.** The written set is only a
  trustworthy complement if the run saw the *whole* module tree. Pruning is
  skipped entirely rather than deleting the existing tree in three failure
  modes: (1) zero pages written (the package import failed outright);
  (2) any module failed to import mid-run (`_generate_module_markdown`
  returned `None`); (3) module collection was truncated —
  `pkgutil.walk_packages` dies at the first subpackage whose import fails,
  so `_collect_all_modules` must flag the list incomplete. The per-module
  failure count alone is *not* enough: depending on directory order, a
  truncated walk can return a small list in which every listed module
  imports fine, and the complement would then delete most of the tree.
  (The original motivating example — running without the `mcp` extra — can
  in practice never reach this code via the CLI: `cli.py` → `commands` →
  `req_parse` → `req` → `req.tools` → `server` → `import mcp` crashes the
  CLI at startup, before any write. The guard protects direct/programmatic
  use of `_generate_api_docs` and any environment where only part of the
  tree is importable.)
- **Flat, top-level only, files only.** Pages are written flat into
  `api_dir` (module dots stay in the filename, no subdirectories). Pruning
  only considers `api_dir.glob("*.md")` at that level, and only unlinks
  paths for which `is_file()` is true — a *directory* named `*.md` is never
  unlinked, and nested directories are never descended into.
- **Return shape.** `_generate_api_docs` returns the tuple
  `(written, pruned)` (previously `written` only); `_collect_all_modules`
  returns `(modules, complete)` (previously `modules` only). Both are
  private helpers with a single caller each, and the two existing tests
  that assert on the old `int` return are adapted. When pruning is skipped
  because the run was untrustworthy, `docs()` additionally echoes a
  one-line `⚠` warning — failure-path output only, so an unchanged,
  healthy tree never sees it (REQ-003).
- **`README.md` is the index, not a module page.** It is written
  conditionally (only when at least one page exists) and is excluded from
  the prune set unconditionally.
- **Report line.** `docs()` already echoes `✓ Wrote {module_count} module
  file(s) to {api_dir}`; pruning adds `✓ Pruned {n} stale page(s) from
  {api_dir}` only when `n > 0`, keeping unchanged-tree output unchanged
  (REQ-003).

### Related ADRs

- 9c687bb1-8ee7-41c8-84ec-07606356bc73: Enforce doc generation/lint/tests
  locally via pre-commit hook, not just CI (the drift check that makes
  idempotency mandatory).

No new ADR is expected: this is a bug fix to the existing `docs` command's
write path, not an architectural decision. If implementation reveals a
genuinely cross-cutting choice (e.g. extending pruning to other generators),
revisit.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 1: Implement pruning
- [x] Task 1.1: In `src/biz/dfch/specmgr/commands/docs.py`, extend
  `_generate_api_docs` to prune: after the write loop, when
  `index_entries` is non-empty, no module failed to import, and module
  collection completed (`_collect_all_modules` returns `(modules,
  complete)`; its existing `except` marks `complete=False`), delete every
  `api_dir/*.md` (flat, top-level, `is_file()` only) whose name is neither
  `README.md` nor a filename written this run; return the pruned count
  alongside the written count as the tuple `(written, pruned)` and update
  its docstring. Update the module docstring and the `docs()` docstring to
  state that stale pages are pruned, and have `docs()` echo the pruning
  line (REQ-004, only when count > 0) plus a one-line `⚠` warning when
  pruning was skipped due to import problems — depends on: none —
  status: done (2026-09-01)
- [x] Task 1.2: Tests in `tests/commands/test_docs.py` covering
  ACC-001..ACC-004 (stale page removed; `README.md`/non-md/nested-dir
  untouched; zero-page run leaves pre-existing files intact; single-module
  import failure skips pruning; idempotent double run; end-to-end `docs()`
  echo of the prune count), plus adapting the two existing tests that
  assert on the old `int` return of `_generate_api_docs` — depends on:
  Task 1.1 — status: done (2026-09-01)
- [x] Task 1.3: Phase gate — `ruff format --check`, `ruff check`,
  `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite,
  `uv run --frozen specmgr coverage-badge` (commit the regenerated
  `docs/coverage.svg` if it changed) — depends on: Task 1.2 —
  status: done (2026-09-01)
- [x] Task 1.4: Run `uv run --frozen specmgr docs` (Python 3.13) to prune
  the five real stale pages (`{adr,qa,req,tsk,uc}.resources.*_list.md`)
  from the committed `docs/api/`; verify the only resulting diff is the
  deletion of exactly those five files — depends on: Task 1.3 —
  status: done (2026-09-01)

#### Phase 2: Verify & close out
- [ ] Task 2.1: Full quality gate re-run (`ruff format --check`, `ruff
  check`, `vulture src/ whitelist.py --min-confidence 60`, full `unittest`
  suite, `specmgr coverage-badge` diff-clean) with the pruned `docs/api/`
  committed, plus a `### Fixed` entry under `CHANGELOG.md`'s
  `[Unreleased]` for the prune behavior (issue #40) — depends on:
  Task 1.4 — status: not-started
- [ ] Task 2.2: Close GitHub issue #40 reference — record the issue link in
  "Related PRs / Commits" below when the PR/commit lands; move
  frontmatter `status` to `done` and update "Current Status" — depends on:
  Task 2.1 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-09-01**: Phase 1 (Tasks 1.1–1.4) done — pruning implemented
in `commands/docs.py`, tested (ACC-001..ACC-004), phase gate green, and
the real run pruned exactly the five stale pages
(`{adr,qa,req,tsk,uc}.resources.*_list.md`) from `docs/api/`. One expected
additional `docs/` diff: the regenerated
`docs/api/biz.dfch.specmgr.commands.docs.md` (the API page of the very
module Phase 1 modified — its signatures and docstrings changed, so the
generated page must too; `GENERATED.md` and the index are byte-identical).
A second `specmgr docs` run over the pruned tree is byte-identical
(idempotent, REQ-003). Phase 2 (verify & close out) not started.

### Recent Updates

#### Update 2026-09-01 (newest)
- Completed: Phase 1 (Tasks 1.1–1.4). `commands/docs.py`:
  `_generate_api_docs` now prunes stale flat `api/*.md` pages after the
  write loop (complement of the just-written filenames, `README.md`
  excluded, `is_file()` only) and returns `(written, pruned)`;
  `_collect_all_modules` returns `(modules, complete)`; pruning is skipped
  entirely on any untrustworthy run (zero pages, any per-module import
  failure, truncated collection); `docs()` echoes `✓ Pruned {n} stale
  page(s) from {api_dir}` only when n > 0 and one `⚠` warning line when a
  skip is detected (re-derived via the new `_pruning_was_skipped` helper).
  `tests/commands/test_docs.py`: 7 new tests in `TestApiDocsPruning`
  (ACC-001..ACC-004) + 2 existing tests adapted to the tuple return.
- Gate results: `ruff format --check` PASS (1477 files); `ruff check`
  PASS; `vulture src/ whitelist.py --min-confidence 60` PASS (no findings);
  full `unittest` PASS (2720 tests, 0 failures); `specmgr coverage-badge`
  PASS (99% overall — `docs/coverage.svg` unchanged).
- Task 1.4 real run: `specmgr docs` (Python 3.13) pruned exactly the five
  stale pages (`biz.dfch.specmgr.{adr,qa,req,tsk,uc}.resources.*_list.md`)
  and echoed `✓ Pruned 5 stale page(s) from …/docs/api`. Verified via
  `git status --short` / `git diff --stat`: those five deletions plus one
  additional diff — `docs/api/biz.dfch.specmgr.commands.docs.md`
  regenerated because Phase 1 changed the module it documents (new
  signatures/docstrings; no unrelated drift). `docs/api/README.md`,
  `docs/GENERATED.md`, `docs/coverage.svg`, and every other page are
  byte-identical. A second `specmgr docs` run over the pruned tree
  changed nothing (idempotent, REQ-003; no prune line at 0, no `⚠`).
- Next: Phase 2 (Task 2.1 — full gate re-run + `CHANGELOG.md` entry).

#### Update 2026-09-01
- Completed: Plan review against the tree. Verified the audit exactly
  (5 stale / 0 missing; 414 live modules vs. 420 flat `docs/api/*.md`
  files). Corrected two inaccurate claims: the "dead link in the index"
  phrasing (the stale pages are orphaned files, not linked by the current
  index) and the guard rationale (without the `mcp` extra the CLI crashes
  at startup — `cli.py` → `commands` → `req_parse` → `req` → `req.tools`
  → `server` → `import mcp` — so that scenario never reaches the prune
  code). Strengthened the REQ-002 guard to skip pruning on *any*
  untrustworthy run (zero pages, any per-module import failure, or
  truncated module collection — the per-module count alone is insufficient
  because a truncated `walk_packages` can return a small list in which
  every listed module imports fine); added ACC-002(d) for the
  single-failure case. Fixed the return shape (`(written, pruned)` tuple;
  `_collect_all_modules` → `(modules, complete)`), noted the two existing
  tests to adapt, and made the `is_file()` filter explicit. Added the
  missing close-out steps to Scope and the task gates:
  `docs/coverage.svg` regeneration via `specmgr coverage-badge` (Tasks
  1.3/2.1) and a `CHANGELOG.md` `[Unreleased]` `### Fixed` entry (Task
  2.1).
- Next: Phase 1 (Task 1.1 — pruning in `commands/docs.py`).
- Notes: See git history for the original plan wording.

#### Update 2026-09-01 (oldest)
- Completed: Created this feature folder from
  `.specmgr/_template/v1/README.md` for GitHub issue #40
  ("`specmgr docs` does not prune stale pages"). Audited the current
  `docs/api/` against the live module set: 5 stale pages
  (`biz.dfch.specmgr.adr.resources.adr_list.md`,
  `biz.dfch.specmgr.qa.resources.qa_list.md`,
  `biz.dfch.specmgr.req.resources.req_list.md`,
  `biz.dfch.specmgr.tsk.resources.tsk_list.md`,
  `biz.dfch.specmgr.uc.resources.uc_list.md`), 0 missing pages.
- Next: Phase 1 (Task 1.1 — pruning in `commands/docs.py`).
- Notes: Root cause is `_generate_api_docs` (write-only, no delete).
  `docs/GENERATED.md` and `docs/MCP.md` are single fully-rewritten files
  and need no equivalent change.

### Decisions Made

- **2026-09-01**: Prune as a complement of the just-written filename set,
  flat `*.md` files only (`is_file()` filter), `README.md` excluded — and
  skip pruning entirely whenever the run is untrustworthy: zero pages
  written, any module failed to import, or module collection truncated.
  Guards against wiping the real `docs/api/` in any partial-import
  environment; the originally cited "missing `mcp` extra" case was found
  to be unreachable via the CLI (the CLI crashes at startup before any
  write), so the guard is for programmatic/partial-import use.
- **2026-09-01**: `_generate_api_docs` returns the tuple `(written,
  pruned)` and `_collect_all_modules` returns `(modules, complete)` —
  both private helpers with a single caller; the two existing tests that
  assert on the old `int` return are adapted in Task 1.2.
- **2026-09-01**: Close-out steps are in scope: `docs/coverage.svg`
  regenerated via `specmgr coverage-badge` in the Task 1.3/2.1 gates, and
  a `CHANGELOG.md` `[Unreleased]` `### Fixed` entry in Task 2.1.
- **2026-09-01**: No new ADR planned; this is a bug fix, not an
  architecture decision (see "Related ADRs").
- **2026-09-01**: How `docs()` detects a skipped prune. The resolved
  decisions fixed both the `_generate_api_docs` return shape
  (`(written, pruned)` only) and the requirement to warn on *any* of the
  three skip causes, but the two-count tuple cannot convey the skip state
  to `docs()` (a healthy run with nothing to prune and a skipped run both
  yield `pruned == 0`). Settled: `docs()` re-derives the skip state only
  when `pruned == 0`, via a new `_pruning_was_skipped(module_count)`
  helper that calls `_collect_all_modules` a second time (cheap — all
  imports are already cached in `sys.modules`) and warns when the
  collection is incomplete or fewer pages were written than modules were
  collected (a per-module import failure). This is the only mechanism that
  keeps the fixed 2-tuple return while warning on all three skip causes;
  it does add a second caller to `_collect_all_modules` (the "exactly one
  caller" note in the plan predates this).
- **2026-09-01**: Exact `⚠` warning wording: `⚠ Pruning skipped due to
  import problems; stale pages were not removed.` — deterministic (no
  timestamps, addresses, or machine-specific paths), failure-path only, so
  an unchanged healthy tree never sees it (REQ-003).

### Related PRs / Commits

- [Issue #40](https://github.com/dfch/biz.dfch.SpecMgr/issues/40): `specmgr docs`
  does not prune stale pages
