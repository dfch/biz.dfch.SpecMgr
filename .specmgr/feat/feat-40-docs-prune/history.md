# History: `specmgr docs` prunes stale `docs/api/` pages

#### 2026-09-01T00:00:00.000Z - Update
Completed: Phase 1 (Tasks 1.1–1.4). `commands/docs.py`:
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
Gate results: `ruff format --check` PASS (1477 files); `ruff check`
  PASS; `vulture src/ whitelist.py --min-confidence 60` PASS (no findings);
  full `unittest` PASS (2720 tests, 0 failures); `specmgr coverage-badge`
  PASS (99% overall — `docs/coverage.svg` unchanged).
Task 1.4 real run: `specmgr docs` (Python 3.13) pruned exactly the five
  stale pages (`biz.dfch.specmgr.{adr,qa,req,tsk,uc}.resources.*_list.md`)
  and echoed `✓ Pruned 5 stale page(s) from …/docs/api`. Verified via
  `git status --short` / `git diff --stat`: those five deletions plus one
  additional diff — `docs/api/biz.dfch.specmgr.commands.docs.md`
  regenerated because Phase 1 changed the module it documents (new
  signatures/docstrings; no unrelated drift). `docs/api/README.md`,
  `docs/GENERATED.md`, `docs/coverage.svg`, and every other page are
  byte-identical. A second `specmgr docs` run over the pruned tree
  changed nothing (idempotent, REQ-003; no prune line at 0, no `⚠`).
Next: Phase 2 (Task 2.1 — full gate re-run + `CHANGELOG.md` entry).

#### 2026-09-01T00:00:00.000Z - Update
Completed: Plan review against the tree. Verified the audit exactly
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
Next: Phase 1 (Task 1.1 — pruning in `commands/docs.py`).
Notes: See git history for the original plan wording.

#### 2026-09-01T00:00:00.000Z - Update (oldest)
Completed: Created this feature folder from
  `.specmgr/_template/v1/README.md` for GitHub issue #40
  ("`specmgr docs` does not prune stale pages"). Audited the current
  `docs/api/` against the live module set: 5 stale pages
  (`biz.dfch.specmgr.adr.resources.adr_list.md`,
  `biz.dfch.specmgr.qa.resources.qa_list.md`,
  `biz.dfch.specmgr.req.resources.req_list.md`,
  `biz.dfch.specmgr.tsk.resources.tsk_list.md`,
  `biz.dfch.specmgr.uc.resources.uc_list.md`), 0 missing pages.
Next: Phase 1 (Task 1.1 — pruning in `commands/docs.py`).
Notes: Root cause is `_generate_api_docs` (write-only, no delete).
  `docs/GENERATED.md` and `docs/MCP.md` are single fully-rewritten files
  and need no equivalent change.
