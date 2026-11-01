---
classification: null
created: '2026-09-25T19:42:03.316+02:00'
id: feat-123-test-gap-cache
status: done
type: feat
updated: '2026-10-07T06:21:40.889Z'
version: 1.0.0
---

# Feature: Close the Write-Path Cache-Wiring Test Gap for the 11 Non-req Domains (feat-107 follow-up)

## Plan

### Overview

`feat-107-doc-cache` (issue #107) shipped a per-domain, content-hash-validated in-memory read cache for the 12 generic whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs`) and wired it into every read and write path: post-write cache warming in each `create_<domain>` tool and in the generic `update`/`set_status`/`set_classification` adapters, eager invalidation in the generic `delete` adapters, and reconcile-on-scan in every `list_<domain>` tool and in `find_doc_path_by_id`'s scan.

A post-closeout review (issue #123) confirmed the shipped implementation is correct across all 12 domains -- no live bug -- but found a real, unaddressed test coverage gap: only `req` has a dedicated wiring-test file (`tests/req/tools/test_doc_cache_wiring.py`) that exercises cache behavior end-to-end through the real MCP tools, while the other 11 domains (the 10 flat non-`req` domains plus `feat`'s own bespoke, folder-per-document integration) are covered only by the narrow, existence-of-routing structural test (`tests/general/tools/test_doc_cache_structural.py`), which never proves that a `create_<domain>`/`update`/`set_status`/`set_classification` write actually warms the cache, that a `delete` actually invalidates it, or that a `list_<domain>` actually reconciles it.

This feature closes that gap: a future refactor that silently drops one of those cache-wiring call sites for any one of those 11 domains would today ship unnoticed; after this feature, a table-driven test fails on the exact domain row whose call site was dropped.

### Requirements

- REQ-001: A table-driven test must prove that `create_<domain>` warms the cache after a successful write for every whole-body domain, by asserting that the `read_<domain>` name bound into `create_<domain>`'s own module is invoked with the just-written document path.
- REQ-002: A table-driven test must prove that the generic `update` tool warms the cache for every whole-body domain on both the whole-body replace path (no `offset`/`limit`) and the range-splice path (with `offset`/`limit`), by asserting that the `read_<domain>` name bound into `general/tools/update.py` is invoked with the written path on each branch.
- REQ-003: A table-driven test must prove that the generic `set_status` tool warms the cache for every whole-body domain, using a real (non-no-op) status transition per domain, by asserting that the `read_<domain>` name bound into `general/tools/set_status.py` is invoked with the written path.
- REQ-004: A table-driven test must prove that the generic `set_classification` tool warms the cache for every whole-body domain, by asserting that the `read_<domain>` name bound into `general/tools/set_classification.py` is invoked with the written path.
- REQ-005: A table-driven test must prove that the generic `delete` tool invalidates the cache for every whole-body domain, by asserting that the `invalidate_<domain>_cache` name bound into `general/tools/delete.py` is invoked with the deleted path and that the path is subsequently absent from the domain's own `_cache` singleton entries.
- REQ-006: A table-driven test must prove that `list_<domain>` reconciles the cache for every whole-body domain, by asserting that the `reconcile_<domain>_cache` name bound into the domain's own `list_<domain>` module is invoked with the live path listing before summary building.
- REQ-007: The table-driven tests must patch each caller module's own bound name of the cache helper (never the helper's definition site in `_cache.py`/`_io.py`) with `mock.patch(..., wraps=<real function>)`, so the real write path still executes end-to-end while the call count and arguments of the documented call site are recorded -- the same mocking discipline `tests/req/tools/test_doc_cache_wiring.py` documents for its `parse_req` spy.
- REQ-008: The table-driven tests must reuse `tests/general/tools/test_doc_cache_structural.py`'s fixture sources in two shapes: the **create rows** pass each flat domain's packaged template (via `general.tools._packaged_data.read_packaged_text`) with its frontmatter block stripped, to the `create_<domain>` tool, which builds its own frontmatter and rejects a submitted frontmatter block (feeding the full template fails parsing with `AssertionError Token[0]: expected 'heading_open', got 'hr'`); **every other row** (update / set_status / set_classification / delete / list) writes the full template with only its frontmatter `id` line substituted (the structural test's `_with_id` helper) directly to disk. Every class additionally runs `reset_<domain>_cache()` in both `setUp` and `tearDown`, so no test observes another test's cached state under `pytest-xdist`.
- REQ-009: The flat-domain table rows must be driven from the shared `general.tools._domains` source of truth (not a hand-listed domain tuple, per the feat-125-domain-lists sweep ruling), with `feat`'s distinct fixture shape (folder-per-document addressing, `SPECMGR_FEAT_DIR` env override, `create_feat` lifecycle) handled by a dedicated `feat` test class in the same file, mirroring `test_doc_cache_structural.py`'s own flat/feat split -- together covering all 12 whole-body domains, so a future 13th flat domain is picked up by construction.

### Acceptance Criteria

- [x] ACC-001: For every whole-body domain, a table row asserts that a real `create_<domain>` call invokes the caller-bound `read_<domain>` exactly once with the written path, and the row fails if that call site is dropped, mistyped, or re-pointed. Evidence: the create class in the new `tests/general/tools/test_doc_cache_write_wiring.py`, green in the final quality gate.
- [x] ACC-002: For every whole-body domain, table rows assert that a real `update` call (whole-body path and range-splice path), a real non-no-op `set_status` call, and a real `set_classification` call each invoke the caller-bound `read_<domain>` exactly once with the written path. Evidence: the write-tools classes in the new file, green in the final quality gate.
- [x] ACC-003: For every whole-body domain, a table row asserts that a real `delete` call invokes the caller-bound `invalidate_<domain>_cache` exactly once with the deleted path, and that the path is absent from the domain's `_cache` entries immediately afterward. Evidence: the delete class in the new file, green in the final quality gate.
- [x] ACC-004: For every whole-body domain, a table row asserts that a real `list_<domain>` call invokes the caller-bound `reconcile_<domain>_cache` exactly once with the live path listing. Evidence: the list class in the new file, green in the final quality gate.
- [x] ACC-005: A mutation check confirms the new tests actually bite: for each of the seven row types (create, update whole-body, update range-splice, set_status, set_classification, delete, list), temporarily dropping one domain's cache call site makes the matching table row fail, and restoring the call site turns the suite green again -- issue #123's four gap classes are covered this way with the bundled write-tools class verified row type by row type. Evidence: the Phase 2 mutation-check `### Updates` entry recording all seven drop/restore cycles.
- [x] ACC-006: The full quality gate is green with no regressions: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, and `uv run --frozen pytest -n auto --cov=src --cov-report=` (every pre-existing test still passing), plus `uv run --frozen specmgr docs` showing exactly one expected drift -- the `docs/GENERATED.md` `**Test files**` count bumping from 362 to 363 for the new file -- which is regenerated and committed with the change (the pre-commit `specmgr docs` hook is scoped to `src/**` changes and will not fire on a tests-only commit, but CI's drift check requires the regenerated file).

### Scope

#### Included

- The new table-driven test file `tests/general/tools/test_doc_cache_write_wiring.py` covering the four write-path/list cache-wiring gaps (create-warm, update/set_status/set_classification-warm, delete-invalidate, list-reconcile) across all 12 whole-body domains.
- Per-domain fixture and env-var setup: packaged-template + `SPECMGR_DOCS_DIR` for the 11 flat domains, `create_feat`/minimal-body + `SPECMGR_FEAT_DIR` for `feat`, plus a per-domain non-no-op `set_status` pair derived from each domain's own closed status vocabulary.
- The ACC-005 mutation check (drop one call site per row type -- seven in total: create, update whole-body, update range-splice, set_status, set_classification, delete, list -- confirm failure, restore).
- Progress tracking in this feature document (updates, decisions, status transitions to `progress` and `done`).

#### Explicitly Out Of Scope

- Any change to `src/` production code: the post-closeout review confirmed the shipped implementation is correct across all 12 domains, so this feature adds tests only -- if a new test surfaced a real bug, that fix would be a separate feature.
- Re-implementation or duplication of `req`'s dedicated end-to-end wiring-test behaviors (`tests/req/tools/test_doc_cache_wiring.py`: exact parse counts, content-change detection, orphan reconciliation, concurrency) -- the `req` rows in the new table cover only the four call-site gaps.
- Any coverage of `adr`, which is permanently excluded from the cache mechanism (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d).
- The `find_doc_path_by_id` reconcile-on-scan wiring, already covered by `tests/general/tools/test_doc_cache_structural.py`.
- Refactoring the existing structural test or `req`'s wiring test into the new table -- both stay as-is.

### Dependencies

#### Depends On

- feat-107-doc-cache (done): the per-domain cache singletons and every write-path cache call site this feature's tests pin down.
- feat-125-domain-lists (review): the shared `general.tools._domains` domain-name source of truth the table drives from (REQ-009) -- already present in this branch's code, so no gating is expected.

#### Blocks

- None identified.

### Design Notes

**Why caller-bound-name spies, not definition-site spies or parse counts.** Each caller module imports the cache helper into its own namespace (`from ._io import read_req` in `create_req.py`, `from ...req.tools._io import read_req` in `general/tools/update.py`, and so on -- except `feat`, whose caller modules import `read_feat` directly from `feat.tools._cache` rather than via its `feat.tools._io` re-export), so the wiring contract "this call site calls this documented helper" is only observable by patching the caller module's own bound name. A pure parse-count assertion (the style of `req`'s dedicated wiring test) would still pass if a future refactor inlined `DocCache.read(path)` directly at a call site, silently breaking the per-domain helper convention every other domain follows; spying the bound name with `wraps=` keeps the real write path running (the file is genuinely written, parsed, and cached) while recording exactly whether the documented call site fired with the right path. For `delete`, one behavioral assertion on top (path absent from `_cache` entries after the call) additionally guards against a call that fires with the wrong path.

**Per-domain `set_status` pairs must be real transitions.** `set_status` is a no-op for an unchanged status (feat-104-109): it returns early before any write and before the cache-warm call, so a row that transitions a domain to its own current status would see zero spy calls and fail. Each row therefore picks a per-domain pair -- the fixture's current status -> another value in that domain's own closed vocabulary -- read from the shared `general/tools/set_status.py::_ALLOWED_STATUSES_BY_TYPE` mapping (itself built from each domain's own frontmatter `_ALLOWED_STATUSES` constant, so the test needs no per-domain `models/v1`-vs-`models/v2` import map) plus the fixture's own frontmatter `status` value (every packaged template ships `draft` except `rsk`'s `open`, and `create_feat` always writes `planning`), never hardcoded per domain in prose.

**`set_classification` is uniformly a real write.** The packaged templates ship without a `classification` frontmatter field, so setting any non-blank value (the tests use `internal`) is a real write -- and therefore a real cache warm -- for every domain.

**`update`'s two branches per domain.** `general/tools/update.py` carries one warm call site per domain per branch (24 total): the whole-body replace path and the range-splice path. The table exercises both per domain; the range-splice row uses `offset=1, limit=1` replacing the body's H1 line with a valid H1 (`# {title}` for the ten free-H1 flat domains, `# System Requirements Specification: {title}` for `sysrs`, whose body model mandates the prefix, and `# Feature: {title}` for `feat`, whose model enforces the prefix) -- verified against all 12 packaged templates, whose `body_text()` line 1 is the H1 in every case since the frontmatter-stripping mechanism drops the leading blank line.

**Create-row path derivation.** `create_<domain>` returns frontmatter only (no body, no path), so each create row derives the written path from the returned id -- the sole `*.md` in the domain's own base dir (the flat domains) or `feat_base_dir() / id / README_FILENAME` (`feat`) -- the same glob-by-id shape `tests/req/tools/test_doc_cache_wiring.py` already uses.

**Why the delete row's behavioral assertion bites.** `delete`'s own `load_by_id` scan reads the target through the cache before the `unlink()`, so the entry exists at invalidation time: with the `invalidate_<domain>_cache` call site dropped, that entry would remain and the "absent from `_cache` entries" assertion fails -- no pre-warming step is needed in the row.

**File shape.** One new file, `tests/general/tools/test_doc_cache_write_wiring.py`, with one test class per gap (create / update / set_status / set_classification / delete / list) looping the flat domains with `self.subTest(domain=...)`, plus the dedicated `feat` counterpart classes -- the same flat/feat split `test_doc_cache_structural.py` already uses. License header, module docstring naming issue #123 as the feat-107 follow-up, shared `_with_id`-style fixture helpers, and `reset_<domain>_cache()` in both `setUp` and `tearDown` per class.

**Pre-commit interaction.** The pre-commit `pytest` hook runs the full suite (`-n auto`) on every commit touching `src/`/`tests/`, and the `specmgr docs`/`adr-toc`/drift hooks run alongside it, so every Phase 2 commit is already a full-suite gate; Phase 3's explicit quality-gate run is the final independent verification before the status flips to `done`, not a new mechanism.

**Size budget.** 12 domains x 7 row types (1 create, 2 update, 1 set_status, 1 set_classification, 1 delete, 1 list) = 84 subtest rows, each writing one small temp file and parsing one document -- the same per-domain cost profile as the existing structural test's loops, negligible against the full suite's runtime.

### Related Decisions

- bfd76370-b59b-4d65-b550-a969f6c93c9d (ADR): the per-domain, content-hash-validated read cache design these tests protect, including its explicit, permanent `adr`-domain exclusion.
- 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (ADR): "filesystem is the sole source of truth" -- the cache refines, never overrides, this invariant, and the new tests pin down the write paths that maintain it.
- 36905d5b-8057-4294-8665-c7eed5534db0 (ADR): the dispatch-only convention for the generic `update`/`set_status`/`set_classification`/`delete` tools -- the very per-domain dispatch arms these tests pin down.

### Task List

#### Phase 100: Audit and Confirm the Gap

- [x] Task 100.100: Verify the shipped call-site inventory by inspection/grep (12 `create_<domain>` warm sites; 24 `update` + 12 `set_status` + 12 `set_classification` warm sites; 12 `delete` invalidate sites; 12 `list_<domain>` reconcile sites) and confirm no test exercises them for the 11 non-`req` domains (issue #123's gap statement).
- [x] Task 100.110: Determine each domain's non-no-op `set_status` pair from the fixture's own frontmatter `status` value (template `draft`, `rsk` `open`, `feat` `planning`) and the shared `general/tools/set_status.py::_ALLOWED_STATUSES_BY_TYPE` mapping, and verify the uniform H1 range-splice content per domain (including `feat`'s `Feature: ` prefix).
- [x] Task 100.120: Set this feature's status to `progress` via the generic `set_status` tool (`type="feat"`).

#### Phase 110: Implement the Table-Driven Wiring Tests

- [x] Task 110.100: Create `tests/general/tools/test_doc_cache_write_wiring.py` with the license header, the module docstring naming issue #123 as the feat-107 follow-up, the shared `_with_id`-style fixture helpers (REQ-008), and per-domain cache resets in `setUp`/`tearDown`.
- [x] Task 110.110: Implement the create-warm flat-domain table class (REQ-001, ACC-001) with caller-bound `read_<domain>` spies.
- [x] Task 110.120: Implement the update / set_status / set_classification warm flat-domain table classes (REQ-002/003/004, ACC-002), update covering both the whole-body and range-splice paths.
- [x] Task 110.130: Implement the delete-invalidate flat-domain table class (REQ-005, ACC-003) including the `_cache` entries behavioral assertion.
- [x] Task 110.140: Implement the list-reconcile flat-domain table class (REQ-006, ACC-004).
- [x] Task 110.150: Implement the dedicated `feat` counterpart classes for Tasks 2.2--2.5 (REQ-009) using `SPECMGR_FEAT_DIR` + `create_feat` fixtures, and drive every flat class from `general.tools._domains`.
- [x] Task 110.160: Run the new file standalone (`uv run --frozen pytest tests/general/tools/test_doc_cache_write_wiring.py -v`) and confirm every row passes against the shipped code.
- [x] Task 110.170: Run the ACC-005 mutation check: for each of the seven row types (create, update whole-body, update range-splice, set_status, set_classification, delete, list), drop one domain's call site, confirm the matching row fails, restore, and confirm green -- record the seven drop/restore cycles in an `### Updates` entry.

#### Phase 120: Verification and Closeout

- [x] Task 120.100: Run the full quality gate (ACC-006): `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen pytest -n auto --cov=src --cov-report=`, and `uv run --frozen specmgr docs`, committing the regenerated `docs/GENERATED.md` (whose `**Test files**` count is expected to bump from 362 to 363 for the new file; no other drift).
- [x] Task 120.110: Check off the satisfied ACCs in this file, add the closeout `### Updates` entry, and set this feature's status to `done` via the generic `set_status` tool (`type="feat"`).

#### Phase 130: Address Post-Implementation Review Findings

- [x] Task 130.100: Rename the eight row classes to the ACC numbering they implement (post-implementation review minor #1): the set_status classes to `TestAcc002SetStatusWarm...`, the set_classification classes to `TestAcc002SetClassificationWarm...`, the delete classes to `TestAcc003DeleteInvalidates...`, and the list classes to `TestAcc004ListReconciles...` (flat and feat counterparts alike); the create (`Acc001`) and update (`Acc002`) classes keep their names.
- [x] Task 130.110: Make the delete rows' `_cache` entries behavioral assertion environment-independent by checking `path.resolve()` (the cache's own key normalization, minor #2) in both the flat and feat delete classes.
- [x] Task 130.120: Add the import-time drift guard `assert set(_SET_STATUS_TARGETS_BY_DOMAIN) == set(WHOLE_BODY_DOMAINS)` with a self-documenting sync-obligation message (minor #3), mirroring `general/tools/set_status.py`'s own mapping guard idiom.
- [x] Task 130.130: Nit cleanups in the test file: count-free docstring phrasing for the domain count (nit #4) and a named module constant for feat's `create_feat`-written `planning` status (nit #6).
- [x] Task 130.140: Add PR #160 to this plan's Related PRs / Commits section (nit #7).
- [x] Task 130.150: Run the Phase 4 quality gate: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, the new file standalone (`uv run --frozen pytest tests/general/tools/test_doc_cache_write_wiring.py -v`, expected 12 passed / 84 subtests), the full suite (`uv run --frozen pytest -n auto --cov=src --cov-report=`, expected 3452 passed), and `uv run --frozen specmgr docs` (expected zero drift — no test files added or removed, the `**Test files**` count stays at 363).
- [x] Task 130.160: Check off this phase's tasks, add the closeout `### Updates` entry (review verdict, finding-to-fix mapping, gate evidence), and rewrite `### Current Status` (which must reflect status `review`, the committed `docs/GENERATED.md`, and the open PR #160 — replacing the stale Phase 3 prose).

#### Phase 140: Address Second-Round (feat-reviewer) Review Findings

- [x] Task 140.100: Correct the Design Notes' range-splice H1 wording, which the 2026-09-26 12:13:14 Decisions Made entry already flagged as contradicted by `sysrs`'s mandated `System Requirements Specification: ` prefix (second-round finding: inconsistency): "`# {title}` for the 11 flat domains" now names all three H1 shapes (the ten free-H1 flat domains, `sysrs`, and `feat`), matching the implementation and the test file's module docstring.
- [x] Task 140.110: Add the import-time drift guard `assert set(_H1_PREFIX_BY_DOMAIN) <= set(WHOLE_BODY_DOMAINS)` with a self-documenting sync-obligation message (second-round finding: improvement), extending the constant's comment to state the obligation (a future domain whose body model mandates an H1 prefix must add its own entry) and why the full-equality guard `_SET_STATUS_TARGETS_BY_DOMAIN` carries is inapplicable to this intentionally sparse table (the free-H1 domains legitimately carry no entry).
- [x] Task 140.120: Pin REQ-006's "before summary building" ordering in both list classes (second-round finding: gap): each list row now additionally patches the caller-bound `build_summaries` name in the `list_<domain>` module with a side effect that asserts a per-row `call_order` list reads `["reconcile"]` before delegating to the real `build_summaries`, and asserts the build spy fired once -- a refactor that moves the reconcile after summary building fails the exact domain row (verified by a mutation cycle on `req`: the two calls swapped in `list_req`, the `req` subtest failed with the ordering message, restore byte-exact, green); the row count is unchanged (12 passed / 84 subtests).
- [x] Task 140.130: Record the second-round code-smell finding (the ~60 lines of private helpers and fixtures -- `_ID_LINE_PATTERN`, `_with_id`, `_cache_module`, and the feat minimal-body fixture -- duplicated verbatim or near-verbatim between this file and `test_doc_cache_structural.py`) as a conscious decision in `### Decisions Made` rather than acting on it: the Out-of-Scope list keeps the structural test untouched, and a shared fixture module would couple the two files' private names; a dedup is separate-feature scope if ever wanted.
- [x] Task 140.140: Run the Phase 5 quality gate: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, the test file standalone (`uv run --frozen pytest tests/general/tools/test_doc_cache_write_wiring.py -v`, expected 12 passed / 84 subtests), the full suite (`uv run --frozen pytest -n auto --cov=src --cov-report=`, expected 3452 passed), and `uv run --frozen specmgr docs` (expected zero drift -- no test files added or removed, the `**Test files**` count stays at 363).
- [x] Task 140.150: Check off this phase's tasks, add the closeout `### Updates` entry (review verdict, finding-to-fix mapping, gate evidence), and rewrite `### Current Status` (which must reflect status `review`, the open PR #160, and the addressed second-round findings).

## Progress

### Current Status

**As of 2026-09-26**: All five phases are complete and the feature is `review` -- closed for implementation, with PR #160 open against `dev`. Phases 1-3 shipped and verified the feature (the table-driven `tests/general/tools/test_doc_cache_write_wiring.py` plus the regenerated `docs/GENERATED.md`, committed in 13f441e with its `**Test files**` count at 363); Phase 4 addressed the post-implementation review's PASS WITH NITS verdict (three minor findings, four nits); Phase 5 addressed the second-round feat-reviewer pass -- one gap (the list rows' unpinned reconcile-before-summary-building ordering), one inconsistency (the Design Notes' stale range-splice H1 wording), one code smell (the deliberate helper duplication with the structural test, recorded as a decision), and one improvement (the missing drift guard on `_H1_PREFIX_BY_DOMAIN`) -- with each actionable fix in the one test file and this plan README only (no `src/` change, no status change). No further implementation is expected before merge; the frontmatter status stays `review`.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26 19:03:16.000Z - Phase 5 Second-Round (feat-reviewer) Review Findings Addressed

Phase 5 is complete: the second-round feat-reviewer pass found no errors and four findings -- one gap, one inconsistency, one code smell, and one improvement -- of which three were actionable in this feature's own files and one was recorded as a decision. Finding-to-fix mapping: the gap (the list rows pinned the reconcile call's existence and arguments but not REQ-006's "before summary building" ordering, so a refactor moving the reconcile inside a `list_<d>` module to after `build_summaries` would still pass) is fixed in both `TestAcc004ListReconcilesForEveryFlatDomain` and `TestAcc004ListReconcilesForFeat`, where each row now additionally patches the caller-bound `build_summaries` name in the `list_<domain>` module with a side effect that asserts a per-row `call_order` list reads `["reconcile"]` before delegating to the real `build_summaries`, plus `build_spy.assert_called_once()` -- verified biting by a mutation cycle on `req` (the two calls swapped in `list_req` made exactly the `req` subtest fail with the ordering message; restore byte-exact, green), and the row count is unchanged (12 passed / 84 subtests); the inconsistency (the Design Notes' "`# {title}` for the 11 flat domains" wording, already contradicted by this file's own 2026-09-26 12:13:14 Decisions Made entry on `sysrs`'s mandated `System Requirements Specification: ` prefix) is corrected to name all three H1 shapes (the ten free-H1 flat domains, `sysrs`, `feat`), matching the implementation and the test file's module docstring; the improvement (`_H1_PREFIX_BY_DOMAIN` silently defaulting to `""` via `.get()` with no drift guard, unlike `_SET_STATUS_TARGETS_BY_DOMAIN`'s import-time assert) is fixed with the import-time subset guard `assert set(_H1_PREFIX_BY_DOMAIN) <= set(WHOLE_BODY_DOMAINS)` and an extended comment stating the sync obligation -- a future domain whose body model mandates an H1 prefix must add its own entry here, and the full-equality guard is inapplicable to this intentionally sparse table (the free-H1 domains legitimately carry no entry); the code smell (the ~60 lines of private helpers and fixtures -- `_ID_LINE_PATTERN`, `_with_id`, `_cache_module`, and the feat minimal-body fixture -- duplicated verbatim or near-verbatim between this file and `test_doc_cache_structural.py`) is recorded as a conscious decision in `### Decisions Made` rather than acted upon. The Phase 5 quality gate is green: `uv run --frozen ruff format --check` clean (1717 files already formatted), `uv run --frozen ruff check` clean (All checks passed!), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` clean (no findings, exit 0), the test file standalone green (`12 passed, 84 subtests passed in 32.24s`), the full suite green (`3452 passed in 72.03s (0:01:12)`), and `uv run --frozen specmgr docs` exit 0 with zero drift -- `git status --short` shows only the test file and this plan README as modified, nothing under `docs/`, the `**Test files**` count staying at 363. No `src/` change, no status change (the frontmatter stays `review`, matching the open PR #160); this commit updates PR #160.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26 19:03:16.000Z - The Helper Duplication With the Structural Test Is Deliberate, Not a Refactoring Target

The second-round feat-reviewer pass flagged roughly 60 lines of private helpers and fixtures -- `_ID_LINE_PATTERN` (identical regex), `_with_id` (identical body and docstring), `_cache_module` (identical), and the feat minimal-body fixture (near-identical, differing only in title/dates) -- duplicated verbatim or near-verbatim between `tests/general/tools/test_doc_cache_write_wiring.py` and its sibling `tests/general/tools/test_doc_cache_structural.py`. Decision: leave both files as-is and record the duplication instead of refactoring it. Rationale: (1) this feature's Out-of-Scope list explicitly keeps the structural test untouched -- extracting shared helpers would expand the diff into a file the plan promised not to modify, in a feature whose value is a self-contained, reviewable test addition; (2) a shared private fixture module (feasible, since `tests/` is a package) would couple the two files' private names, so any later independent evolution of one file's helpers would ripple into the other; (3) the duplicated surface is small, stable, and each file's own quality gate covers it. If a future feature wants the dedup, it is a scope decision of its own -- this feature closes the coverage gap, not the test-suite layout.

#### 2026-09-26 13:54:52.000Z - The set_status Targets Are Encoded as a Module Constant, Re-checked Per Row Against the Shared Mapping

Phase 2's set_status rows encode Phase 1's derived per-domain target pair as a module constant in the new test file (`_SET_STATUS_TARGETS_BY_DOMAIN`, target only — the fixture's starting status is read from the template's own frontmatter at runtime) rather than as a pure runtime derivation from the shared `general.tools.set_status._ALLOWED_STATUSES_BY_TYPE` mapping alone, because every domain's own `_ALLOWED_STATUSES` constant is an unordered `frozenset` (its iteration order is hash-based and randomized per process), so the plan's "first member of the domain's own allowed vocabulary other than the starting value" is only well-defined in the domain's source-literal order, which is not recoverable at runtime from the shared mapping; a deterministic runtime choice (e.g. `sorted(...)`) would instead pick a different, vocabulary-legal target per domain than Phase 1 recorded. To keep the constant honest, every row re-checks its encoded target against the shared `_ALLOWED_STATUSES_BY_TYPE` mapping and the fixture's own status (`assertIn` + `assertNotEqual` before the tool call), so a domain-vocabulary drift fails the row loudly instead of silently sending a no-op, zero-spy-call status — and a future 13th flat domain missing from the constant fails with a loud `KeyError` rather than a silent pass.

#### 2026-09-26 12:13:14.000Z - The sysrs Range-Splice H1 Carries the Domain's Own Mandatory Prefix

Phase 1's H1 verification found that the `sysrs` body model mandates the H1 prefix `System Requirements Specification: ` (`sysrs/models/v1/body.py:1121`, `@alias(value=r"^System Requirements Specification: .+$", type=AliasType.REGEX)`), not just `feat`'s `Feature: ` prefix as the Design Notes' "`# {title}` for the 11 flat domains" wording assumes; a bare `# {title}` fails `sysrs` parsing (empirical negative control, `AssertionError`). Decision: Phase 2's `sysrs` range-splice row splices `# System Requirements Specification: {title}`; the other ten flat domains keep `# {title}`, and `feat` keeps `# Feature: {title}`.

### Related PRs / Commits

- [Issue #123](https://github.com/dfch/biz.dfch.SpecMgr/issues/123): the tracking issue for this feature (the post-closeout review of feat-107-doc-cache that found the gap).
- [PR #160](https://github.com/dfch/biz.dfch.SpecMgr/pull/160): the implementation PR for this feature (open against dev).
