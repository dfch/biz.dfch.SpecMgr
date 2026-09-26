---
classification: null
created: '2026-09-25T19:42:03.316+02:00'
id: feat-123-test-gap-cache
status: progress
type: feat
updated: '2026-09-26T14:12:24.672+02:00'
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

- [ ] ACC-001: For every whole-body domain, a table row asserts that a real `create_<domain>` call invokes the caller-bound `read_<domain>` exactly once with the written path, and the row fails if that call site is dropped, mistyped, or re-pointed. Evidence: the create class in the new `tests/general/tools/test_doc_cache_write_wiring.py`, green in the final quality gate.
- [ ] ACC-002: For every whole-body domain, table rows assert that a real `update` call (whole-body path and range-splice path), a real non-no-op `set_status` call, and a real `set_classification` call each invoke the caller-bound `read_<domain>` exactly once with the written path. Evidence: the write-tools classes in the new file, green in the final quality gate.
- [ ] ACC-003: For every whole-body domain, a table row asserts that a real `delete` call invokes the caller-bound `invalidate_<domain>_cache` exactly once with the deleted path, and that the path is absent from the domain's `_cache` entries immediately afterward. Evidence: the delete class in the new file, green in the final quality gate.
- [ ] ACC-004: For every whole-body domain, a table row asserts that a real `list_<domain>` call invokes the caller-bound `reconcile_<domain>_cache` exactly once with the live path listing. Evidence: the list class in the new file, green in the final quality gate.
- [ ] ACC-005: A mutation check confirms the new tests actually bite: for each of the seven row types (create, update whole-body, update range-splice, set_status, set_classification, delete, list), temporarily dropping one domain's cache call site makes the matching table row fail, and restoring the call site turns the suite green again -- issue #123's four gap classes are covered this way with the bundled write-tools class verified row type by row type. Evidence: the Phase 2 mutation-check `### Updates` entry recording all seven drop/restore cycles.
- [ ] ACC-006: The full quality gate is green with no regressions: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, and `uv run --frozen pytest -n auto --cov=src --cov-report=` (every pre-existing test still passing), plus `uv run --frozen specmgr docs` showing exactly one expected drift -- the `docs/GENERATED.md` `**Test files**` count bumping from 362 to 363 for the new file -- which is regenerated and committed with the change (the pre-commit `specmgr docs` hook is scoped to `src/**` changes and will not fire on a tests-only commit, but CI's drift check requires the regenerated file).

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

**`update`'s two branches per domain.** `general/tools/update.py` carries one warm call site per domain per branch (24 total): the whole-body replace path and the range-splice path. The table exercises both per domain; the range-splice row uses `offset=1, limit=1` replacing the body's H1 line with a valid H1 (`# {title}` for the 11 flat domains, `# Feature: {title}` for `feat`, whose model enforces the prefix) -- verified against all 12 packaged templates, whose `body_text()` line 1 is the H1 in every case since the frontmatter-stripping mechanism drops the leading blank line.

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

#### Phase 1: Audit and Confirm the Gap

- [x] Task 1.1: Verify the shipped call-site inventory by inspection/grep (12 `create_<domain>` warm sites; 24 `update` + 12 `set_status` + 12 `set_classification` warm sites; 12 `delete` invalidate sites; 12 `list_<domain>` reconcile sites) and confirm no test exercises them for the 11 non-`req` domains (issue #123's gap statement).
- [x] Task 1.2: Determine each domain's non-no-op `set_status` pair from the fixture's own frontmatter `status` value (template `draft`, `rsk` `open`, `feat` `planning`) and the shared `general/tools/set_status.py::_ALLOWED_STATUSES_BY_TYPE` mapping, and verify the uniform H1 range-splice content per domain (including `feat`'s `Feature: ` prefix).
- [x] Task 1.3: Set this feature's status to `progress` via the generic `set_status` tool (`type="feat"`).

#### Phase 2: Implement the Table-Driven Wiring Tests

- [ ] Task 2.1: Create `tests/general/tools/test_doc_cache_write_wiring.py` with the license header, the module docstring naming issue #123 as the feat-107 follow-up, the shared `_with_id`-style fixture helpers (REQ-008), and per-domain cache resets in `setUp`/`tearDown`.
- [ ] Task 2.2: Implement the create-warm flat-domain table class (REQ-001, ACC-001) with caller-bound `read_<domain>` spies.
- [ ] Task 2.3: Implement the update / set_status / set_classification warm flat-domain table classes (REQ-002/003/004, ACC-002), update covering both the whole-body and range-splice paths.
- [ ] Task 2.4: Implement the delete-invalidate flat-domain table class (REQ-005, ACC-003) including the `_cache` entries behavioral assertion.
- [ ] Task 2.5: Implement the list-reconcile flat-domain table class (REQ-006, ACC-004).
- [ ] Task 2.6: Implement the dedicated `feat` counterpart classes for Tasks 2.2--2.5 (REQ-009) using `SPECMGR_FEAT_DIR` + `create_feat` fixtures, and drive every flat class from `general.tools._domains`.
- [ ] Task 2.7: Run the new file standalone (`uv run --frozen pytest tests/general/tools/test_doc_cache_write_wiring.py -v`) and confirm every row passes against the shipped code.
- [ ] Task 2.8: Run the ACC-005 mutation check: for each of the seven row types (create, update whole-body, update range-splice, set_status, set_classification, delete, list), drop one domain's call site, confirm the matching row fails, restore, and confirm green -- record the seven drop/restore cycles in an `### Updates` entry.

#### Phase 3: Verification and Closeout

- [ ] Task 3.1: Run the full quality gate (ACC-006): `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen pytest -n auto --cov=src --cov-report=`, and `uv run --frozen specmgr docs`, committing the regenerated `docs/GENERATED.md` (whose `**Test files**` count is expected to bump from 362 to 363 for the new file; no other drift).
- [ ] Task 3.2: Check off the satisfied ACCs in this file, add the closeout `### Updates` entry, and set this feature's status to `done` via the generic `set_status` tool (`type="feat"`).

## Progress

### Current Status

**As of 2026-09-26**: Phase 1 audit complete and confirmed — the full shipped call-site inventory was re-verified in place (12 create-warm, 24 update-warm, 12 set_status-warm, 12 set_classification-warm, 12 delete-invalidate, 12 list-reconcile sites), issue #123's gap was confirmed (no test asserts any of the seven wiring row types for the 11 non-`req` domains), the per-domain `set_status` pairs and H1 splice content were derived, and this document's status was flipped to `progress` via the generic `set_status` tool. One plan premise was corrected in the process: `sysrs` also mandates an H1 prefix (`System Requirements Specification: `), so its Phase 2 range-splice row uses that prefix (see Decisions Made). No implementation work yet; Phase 2 is next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26 12:13:14.000Z - Phase 1 Audit Complete

Task 1.1 — call-site inventory and gap, confirmed. `general/tools/_domains.py:55` lists the 12 whole-body domains in canonical order, and all six shipped site classes exist exactly as the plan claims: 12 create-warms, one per domain's own `create_<d>` tool after the successful write (`req/tools/create_req.py:127`, `uc/tools/create_uc.py:125`, `tsk/tools/create_tsk.py:140`, `qa/tools/create_qa.py:128`, `prb/tools/create_prb.py:125`, `gol/tools/create_gol.py:125`, `rsk/tools/create_rsk.py:126`, `dec/tools/create_dec.py:125`, `sop/tools/create_sop.py:124`, `vcr/tools/create_vcr.py:125`, `sysrs/tools/create_sysrs.py:125`, and `feat/tools/create_feat.py:182` — whose `read_feat` import at `create_feat.py:54` comes directly from `feat.tools._cache`, matching the plan's description); 24 update-warms in `general/tools/update.py`, two per domain — the range-splice branch (`:202, :245, :288, :331, :374, :417, :460, :505, :550, :595, :637, :681`) and the whole-body branch (`:217, :260, :303, :346, :389, :432, :475, :520, :565, :610, :652, :696`); 12 set_status-warms in `general/tools/set_status.py` (`:338, :367, :396, :425, :455, :484, :513, :544, :576, :607, :636, :666`), the `adr` dispatch branch (`_set_status_adr`, `:670–690`) not warming, as expected; 12 set_classification-warms in `general/tools/set_classification.py` (`:216, :239, :262, :285, :308, :331, :354, :377, :405, :431, :455, :481`); 12 delete-invalidates in `general/tools/delete.py` (`:161, :178, :195, :212, :229, :246, :263, :280, :294, :322, :339, :356`), each after a successful `unlink()`; and 12 list-reconciles, one per domain's own `list_<d>` module, called with the live path listing immediately before summary building (`req/tools/list_req.py:124`, `uc/tools/list_uc.py:116`, `tsk/tools/list_tsk.py:116`, `qa/tools/list_qa.py:118`, `prb/tools/list_prb.py:116`, `gol/tools/list_gol.py:115`, `rsk/tools/list_rsk.py:123`, `dec/tools/list_dec.py:117`, `sop/tools/list_sop.py:115`, `vcr/tools/list_vcr.py:116`, `sysrs/tools/list_sysrs.py:116`, `feat/tools/list_feat.py:157`). The gap is confirmed: `tests/req/tools/test_doc_cache_wiring.py` is req-only (8 classes, feat-107's ACC-001–006/012); `tests/general/tools/test_doc_cache_structural.py` checks existence-of-routing only (every `_cache.py`'s API, `read_<d>`'s cache-backing via direct helper calls, the `find_doc_path_by_id` scan — its `feat` part invokes the real `create_feat` solely as a fixture writer and discards its warming at `:270`, and asserts `set_feat_id`'s own entry move); `tests/general/tools/test_doc_cache_delete_scan_race.py` (ACC-016/017/018) calls `find_doc_path_by_id`/`_io.load_by_id` directly and, while it does invoke the real `list_<d>` tool, asserts only vanishing-file omission, never the reconcile wiring; `tests/general/tools/test__doc_cache.py` covers the domain-agnostic `DocCache` mechanism; so no test asserts any of the seven row types (create, update whole-body, update range-splice, set_status, set_classification, delete, list) for any of the 11 non-`req` domains. Task 1.2 — per-domain `set_status` pairs and H1 splice content, derived. Fixture starting statuses (each packaged template's own frontmatter, resolved via `general.tools._packaged_data.read_packaged_text`): `draft` for req/uc/tsk/qa/prb/gol/dec/sop/vcr/sysrs, `open` for rsk, `planning` for feat (`feat_template.md`'s frontmatter; `create_feat.py:176` always writes `status="planning"`). Non-no-op pairs (starting → target, the target being the first member of the domain's own allowed vocabulary other than the starting value, from each domain's `_ALLOWED_STATUSES` constant as imported into `general/tools/set_status.py:246–260`'s `_ALLOWED_STATUSES_BY_TYPE`; the allowed-list source in parentheses): req draft→proposed (`req/models/v1/frontmatter.py:35`), uc draft→proposed (`uc/models/v2/frontmatter.py:43`), tsk draft→active (`tsk/models/v1/frontmatter.py:38`), qa draft→active (`qa/models/v2/frontmatter.py:46`), prb draft→active (`prb/models/v1/frontmatter.py:43`), gol draft→proposed (`gol/models/v1/frontmatter.py:42`), rsk open→mitigating (`rsk/models/v1/frontmatter.py:50`), dec draft→proposed (`dec/models/v1/frontmatter.py:43`), sop draft→review (`sop/models/v1/frontmatter.py:44`), feat planning→progress (`feat/models/v1/frontmatter.py:53`), vcr draft→progress (`vcr/models/v1/frontmatter.py:45`), sysrs draft→review (`sysrs/models/v1/frontmatter.py:49`). H1 splice verification: for all 12 packaged templates, `body_text()`'s line 1 is the H1 (empirically, via the same `frontmatter` parse `general/tools/_splice.py:68` uses — the frontmatter block plus its one following blank line is dropped), and an in-memory splice of line 1 followed by a full re-parse succeeded for all 12 — `# {title}` for the ten free-H1 domains and `# Feature: {title}` for `feat` (`feat/models/v1/body.py:726`); one plan premise corrected in the process, the `sysrs` model also mandates an H1 prefix (`@alias(value=r"^System Requirements Specification: .+$", type=AliasType.REGEX)` at `sysrs/models/v1/body.py:1121`, "unlike every other domain's free-form H1"), and a negative control confirmed a bare `# {title}` fails `sysrs` parsing with `AssertionError`, so Phase 2's `sysrs` range-splice row must splice `# System Requirements Specification: {title}` (see Decisions Made). Task 1.3 — done: the generic `set_status` tool (`type="feat"`) flipped this document's status to `progress`, bumping `updated` to `2026-09-26T14:12:24.672+02:00` by the tool itself.

#### 2026-09-26 10:29:49.000Z - Plan Refined After Code-Level Verification Pass

The plan was verified line-by-line against the current branch before implementation. Confirmed: the full call-site inventory (12 create-warm, 24 update-warm, 12 set_status-warm, 12 set_classification-warm, 12 delete-invalidate, 12 list-reconcile), `set_status`'s no-op return ordering ahead of the cache-warm call, `set_classification`'s lack of any no-op guard, that `body_text()`'s line 1 is the H1 for all 12 packaged templates (empirically), the fixture frontmatter statuses (`draft` x10, `rsk` `open`, `create_feat` always `planning`), the shared `SPECMGR_DOCS_DIR` per-domain-subdir layout, and that every caller module binds the helper names the spies target. Fixed: (1) the size-budget arithmetic -- 7 row types x 12 domains = 84 subtest rows, not 6 x 12 = 72; (2) REQ-008 -- `create_<domain>` rejects a submitted frontmatter block (empirically: `AssertionError Token[0]: expected 'heading_open', got 'hr'`), so the create rows use the frontmatter-stripped template body while every other row keeps the `_with_id` full-template fixture; (3) ACC-005/Task 2.8/Scope -- the mutation check now runs one drop/restore cycle per row type (seven total), since issue #123's four gap classes bundle update/set_status/set_classification and a single cycle inside that bundle would prove only one of its row types; (4) the `set_status` pairs now derive from the shared `general/tools/set_status.py::_ALLOWED_STATUSES_BY_TYPE` mapping plus the fixture's own status, removing the need for a per-domain `models/v1`-vs-`models/v2` import map; (5) ACC-006/Task 3.1 -- the `docs/GENERATED.md` `**Test files**` count bump (362 -> 363) is named as the single expected `specmgr docs` drift to be committed with the change; (6) ACC-002/003/004 now assert "exactly once" like ACC-001. Added design notes: `feat`'s `feat.tools._cache` import source in the caller modules, the create-row path derivation from the returned id, and why the delete row's behavioral assertion bites without pre-warming.

#### 2026-09-25 17:39:18.000Z - Created

Feature created from GitHub issue #123 ("test: close write-path cache-wiring test gap for 10 non-req domains (feat-107 follow-up)"), with scope refined per planning: the issue's gap list names the 10 flat non-`req` domains plus `feat`'s own bespoke integration (11 domains), and the new table includes `req` rows as well so all 12 whole-body domains are pinned uniformly -- the `req` rows do not duplicate its dedicated end-to-end wiring-test file, which stays as-is.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26 12:13:14.000Z - The sysrs Range-Splice H1 Carries the Domain's Own Mandatory Prefix

Phase 1's H1 verification found that the `sysrs` body model mandates the H1 prefix `System Requirements Specification: ` (`sysrs/models/v1/body.py:1121`, `@alias(value=r"^System Requirements Specification: .+$", type=AliasType.REGEX)`), not just `feat`'s `Feature: ` prefix as the Design Notes' "`# {title}` for the 11 flat domains" wording assumes; a bare `# {title}` fails `sysrs` parsing (empirical negative control, `AssertionError`). Decision: Phase 2's `sysrs` range-splice row splices `# System Requirements Specification: {title}`; the other ten flat domains keep `# {title}`, and `feat` keeps `# Feature: {title}`.

### Related PRs / Commits

- [Issue #123](https://github.com/dfch/biz.dfch.SpecMgr/issues/123): the tracking issue for this feature (the post-closeout review of feat-107-doc-cache that found the gap).
