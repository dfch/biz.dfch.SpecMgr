---
created: '2026-09-01 00:00:00.000Z'
id: feat-40-docs-prune
status: done
updated: '2026-10-07T06:21:40.937Z'
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

- REQ-001: `specmgr docs` deletes stale `api/*.md` pages — any flat `*.md` file in the output `api/` directory (default `docs/api/`, or wherever `--output` points) whose name is not a page written by the same run and is not the generated `README.md` index.
- REQ-002: Pruning is conservative and safe: it touches only flat `*.md` files inside the `api/` directory this command manages — never `README.md`, never other file types, never nested directories, never anything outside that directory. Pruning is skipped entirely rather than deleting the existing tree whenever the run cannot be trusted to have written the full current set: if a run generates *no* pages at all (e.g. the package import fails outright), if any module fails to import mid-run, or if module collection is truncated before the walk completes.
- REQ-003: Reproducibility is preserved: on an unchanged tree, repeated `specmgr docs` runs remain byte-identical and idempotent, so the pre-commit hook and CI drift check (ADR 9c687bb1) keep passing.
- REQ-004: The command reports pruning: the `docs` entry point echoes how many stale pages were removed (only when the count is non-zero), next to the existing "wrote N module file(s)" line.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — a test pre-seeds a stale `<module>.md` page in a scratch `api/` directory, runs `_generate_api_docs` (or the `docs()` entry point with `--output`), and asserts the stale file is gone while all current module pages and `README.md` remain.
- [x] ACC-002: Verifies REQ-002 — tests assert (a) `README.md` is never pruned, (b) a run that generates zero pages (unimportable package) leaves pre-existing files untouched, (c) non-`.md` files and nested directories in the `api/` dir are left untouched, and (d) a run in which exactly one module fails to import (mocked) skips pruning entirely — pre-seeded stale pages remain and the pruned count is 0.
- [x] ACC-003: Verifies REQ-003 — a test runs generation twice into the same scratch directory and asserts the resulting file sets are identical (idempotency); the existing signature-stability tests (`TestStableSignatureStr`) continue to pass.
- [x] ACC-004: Verifies REQ-004 — an end-to-end test of `docs()` with a pre-seeded stale page asserts the stale page is removed and the echo output reports the pruning count.

### Scope

#### Included

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

#### Explicitly Out Of Scope

- `docs/GENERATED.md` — a single fully-rewritten file; nothing to prune.
- `specmgr mcp-docs` / `docs/MCP.md` — also a single fully-rewritten file.
- `specmgr adr-toc` / `docs/adr/README.md` — single regenerated index file.
- Pruning of anything other than flat `*.md` files inside the `api/`
  directory (nested dirs, non-md files are left alone by design, REQ-002).
- Any change to page content, naming, or the index format.

### Dependencies

#### Depends On

- ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73 (pre-commit/CI
  drift check that makes byte-identical reproducibility, REQ-003, a hard
  constraint).
#### Blocks

- nothing.

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


Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).


**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.


### Related Decisions

- 9c687bb1-8ee7-41c8-84ec-07606356bc73: Enforce doc generation/lint/tests
  locally via pre-commit hook, not just CI (the drift check that makes
  idempotency mandatory).

No new ADR is expected: this is a bug fix to the existing `docs` command's
write path, not an architectural decision. If implementation reveals a
genuinely cross-cutting choice (e.g. extending pruning to other generators),
revisit.

### Task List
#### Phase 100: Implement pruning
- [x] Task 100.100: In `src/biz/dfch/specmgr/commands/docs.py`, extend `_generate_api_docs` to prune: after the write loop, when `index_entries` is non-empty, no module failed to import, and module collection completed (`_collect_all_modules` returns `(modules, complete)`; its existing `except` marks `complete=False`), delete every `api_dir/*.md` (flat, top-level, `is_file()` only) whose name is neither `README.md` nor a filename written this run; return the pruned count alongside the written count as the tuple `(written, pruned)` and update its docstring. Update the module docstring and the `docs()` docstring to state that stale pages are pruned, and have `docs()` echo the pruning line (REQ-004, only when count > 0) plus a one-line `⚠` warning when pruning was skipped due to import problems — depends on: none — status: done (2026-09-01)
- [x] Task 100.110: Tests in `tests/commands/test_docs.py` covering ACC-001..ACC-004 (stale page removed; `README.md`/non-md/nested-dir untouched; zero-page run leaves pre-existing files intact; single-module import failure skips pruning; idempotent double run; end-to-end `docs()` echo of the prune count), plus adapting the two existing tests that assert on the old `int` return of `_generate_api_docs` — depends on: Task 1.1 — status: done (2026-09-01)
- [x] Task 100.120: Phase gate — `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite, `uv run --frozen specmgr coverage-badge` (commit the regenerated `docs/coverage.svg` if it changed) — depends on: Task 1.2 — status: done (2026-09-01)
- [x] Task 100.130: Run `uv run --frozen specmgr docs` (Python 3.13) to prune the five real stale pages (`{adr,qa,req,tsk,uc}.resources.*_list.md`) from the committed `docs/api/`; verify the only resulting diff is the deletion of exactly those five files — depends on: Task 1.3 — status: done (2026-09-01)

#### Phase 110: Verify & close out
- [x] Task 110.100: Full quality gate re-run (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite, `specmgr coverage-badge` diff-clean) with the pruned `docs/api/` committed, plus a `### Fixed` entry under `CHANGELOG.md`'s `[Unreleased]` for the prune behavior (issue #40) — depends on: Task 1.4 — status: done (2026-09-01)
- [x] Task 110.110: Close GitHub issue #40 reference — record the issue link in "Related PRs / Commits" below when the PR/commit lands; move frontmatter `status` to `done` and update "Current Status" — depends on: Task 2.1 — status: done (2026-09-01)


## Progress

### Current Status

**As of 2026-09-01**: feature complete — both phases done (Phase 1,
Tasks 1.1–1.4: pruning implemented, tested, and the five stale
`docs/api/` pages pruned in commit `08bcefc`; Phase 2, Tasks 2.1–2.2:
full quality gate re-run green with the pruned tree committed,
`CHANGELOG.md` `[Unreleased]` `### Fixed` entry added, frontmatter
`status` moved to `done`). All four acceptance criteria
(ACC-001..ACC-004) are verified by tests; gates are green (ruff
format/check, vulture, 2720-test suite, `docs/coverage.svg` diff-clean at
99%); repeated `specmgr docs` runs over the pruned tree remain
byte-identical (REQ-003). Ready for a PR to `dev` and closure of
GitHub issue #40 — no PR exists yet; the work is on the local branch
`feat-40-docs-prune` only.

### Updates

#### 2026-09-01T00:00:00.000Z - Update (newest)
Completed: Phase 2 (Tasks 2.1–2.2). Full quality gate re-run with the
  pruned `docs/api/` committed — `ruff format --check` PASS (1472 files;
  the 5 pruned `.md` pages no longer counted); `ruff check` PASS;
  `vulture src/ whitelist.py --min-confidence 60` PASS (no findings);
  full suite via the pre-commit hook's exact invocation
  (`coverage run -m unittest discover -v -s tests -t . -p "test_*.py"`)
  PASS (2720 tests, 0 failures); `specmgr coverage-badge` PASS (99%
  overall, 7692 stmts / 106 miss — `docs/coverage.svg` diff-clean,
  unchanged). Added the `### Fixed` entry under `CHANGELOG.md`'s
  `[Unreleased]` for the prune behavior (issue #40); recorded the Phase 1
  commit (`08bcefc`, full hash
  `08bcefcb73133020c44d6863c92d3eeacb3f1627`) in "Related PRs / Commits";
  moved frontmatter `status` to `done` and updated "Current Status".
Next: PR to `dev` / closure of GitHub issue #40 (no PR yet — local
  branch `feat-40-docs-prune` only); the closing commit for this update +
  the CHANGELOG entry lands immediately after (a commit cannot record its
  own hash).

### Decisions Made

#### 2026-09-01 00:00:00.000Z : Prune as a complement of the just-written filename set,
Prune as a complement of the just-written filename set,
#### 2026-09-01 00:00:00.000Z : `_generate_api_docs` returns the tuple `(written,
`_generate_api_docs` returns the tuple `(written,
#### 2026-09-01 00:00:00.000Z : Close-out steps are in scope
Close-out steps are in scope: `docs/coverage.svg`
#### 2026-09-01 00:00:00.000Z : No new ADR planned
No new ADR planned; this is a bug fix, not an
#### 2026-09-01 00:00:00.000Z : How `docs()` detects a skipped prune. The resolved
How `docs()` detects a skipped prune. The resolved
#### 2026-09-01 00:00:00.000Z : Exact `⚠` warning wording
Exact `⚠` warning wording: `⚠ Pruning skipped due to
### Related PRs / Commits

- [Issue #40](https://github.com/dfch/biz.dfch.SpecMgr/issues/40): `specmgr docs`
  does not prune stale pages
- [08bcefc](https://github.com/dfch/biz.dfch.SpecMgr/commit/08bcefcb73133020c44d6863c92d3eeacb3f1627): fix(docs): prune stale docs/api pages in `specmgr docs` (#40) — Phase 1, full hash `08bcefcb73133020c44d6863c92d3eeacb3f1627`
- The closing commit for Phase 2 (this update + the `CHANGELOG.md` entry) lands immediately after this one — a commit cannot record its own hash. No PR yet: the work is on the local branch `feat-40-docs-prune` only.
