---
classification: null
created: '2026-10-07T07:48:18.241+02:00'
id: feat-200-list
status: review
type: feat
updated: '2026-10-07T17:03:20.962+02:00'
version: 1.0.0
---

# Feature: Add a glob parameter to list_feat (and other list_ tools) for partial-id lookup

## Plan

### Overview

`list_feat` and the other paged `list_<d>` tools return every artifact in the corpus — there is no way to filter by id. When a user or agent only knows part of an id — "feat-7" without the full `feat-7-<slug>`, or the leading characters of a UUID — the only option is an unfiltered full listing, which for `feat` is also the expensive cold case (feat-187). This feature adds an optional `glob` parameter to `list_feat` that matches against the feature's `id`, and extends the same parameter to the other paged `list_<d>` tools (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs), whose ids are UUIDs and where a known prefix is equally common (e.g. `dead*`). One simple rule — glob-match the full id string — covers both id shapes.

### Requirements

- REQ-001: `list_feat` accepts an optional `glob: str | None = None` parameter; when given, only features whose `id` (`feat-NNN-slug`) matches the glob are returned.

- REQ-002: Each of the other eleven paged `list_<d>` tools (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs) accepts the same `glob` parameter, matching against the document's id (UUID).

- REQ-003: `total`, `max_results`/`offset` paging, `truncated`, and `error_count` are computed on the filtered set, so their meaning is unchanged (a `glob`-given result has `error_count = 0` by construction, since failed rows carry `id=None` and never match — see Design Notes).

- REQ-004: Matching is case-insensitive: the stored id and the pattern are both lowercased before matching, so a pattern may be given in any case. Ids are stored in one canonical lowercase form (`feat` slugs are shape-validated as lowercase, UUIDs are created via `str(uuid.uuid4())`); by-id lookups are exact and case-sensitive, so the case-insensitive glob is a deliberate search-UX choice, not a property of existing lookup behaviour.

- REQ-005: When `glob` is absent (`None`), every tool that receives the parameter (all twelve) behaves exactly as today (byte-identical results and return shape).

### Acceptance Criteria

- [x] ACC-001: `list_feat(glob="feat-7*")` against a fixture corpus (temp dir with `SPECMGR_FEAT_DIR` overridden, holding a known set of `feat-7*` ids plus non-matching ids) returns exactly the matching features and no others, and `total` equals that count.

- [x] ACC-002: For a document with a known UUID (e.g. from `docs/req/`), `list_req(glob="<first 4 hex chars>*")` — in any case of the pattern — returns that row and no others.

- [x] ACC-003: With `glob=None`, all twelve tools' output is unchanged (existing tests stay green, no new drift).

- [x] ACC-004: Paging composes with the filter: for a pattern with N matches, `offset=N` returns zero rows and `truncated` reflects the filtered total.

- [x] ACC-005: A corpus containing a broken (failed-to-parse) document: the unfiltered listing still shows its failed row and `error_count` counts it (today's behaviour); for any `glob` the failed row is absent and `error_count = 0`.

### Scope

#### Included

- The `glob` parameter on `list_feat` and the eleven other paged `list_<d>` tools.

- One shared id-filter helper in `general/tools/`.

- Docstring updates and the `docs/MCP.md` regeneration they trigger.

- Unit tests for filtering and its composition with paging.

#### Explicitly Out Of Scope

- Filtering on any field other than `id` (title, status, classification).

- Fuzzy or typo-tolerant matching.

- Changes to `get_<d>`/`parse_<d>` or to resources (listing is a tool, not a resource, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

- Any new CLI command.

- `list_adr`: the thirteenth paged `list_<d>` tool, deliberately excluded — ADR is being phased out (issue #46), `AdrSummary` does not subclass `DocSummary`, and `list_adr` produces no failed-to-parse rows.

### Dependencies

#### Depends On

- FEAT feat-187-list-feat-timeout: `list_feat`'s two-stage (dirty/clean `DocCache`) row resolution — `status: done`, dependency satisfied.

### Design Notes

Matching rule. The `glob` value is evaluated with `fnmatchcase(id.lower(), pattern.lower())` — both the stored id and the pattern are explicitly lowercased first. This is deliberate: on POSIX, `fnmatch.fnmatch` is case-sensitive (its `os.path.normcase` is the identity), so the portable case-insensitive form is lowercase-both-sides plus `fnmatchcase`. The case-insensitivity is a deliberate search-UX choice, not an alignment with existing lookups: by-id resolution (`get_<d>` and path scanning) is exact and case-sensitive, and the true shared property is that ids are stored in one canonical lowercase form (`feat` slugs are shape-validated as lowercase via `assert_feat_id`; document UUIDs are created as `str(uuid.uuid4())`). An empty string is a pattern, not an off-switch: `glob=""` matches no id (ids are never empty) and yields a zero-row result; only `glob=None` disables filtering.

Pipeline position. Each `list_<d>` tool builds one summary row per document, then computes `total`, applies `offset`/`max_results` paging, and sets `truncated`. The filter runs on the row list between the row build and the `total` computation, so `total` is the match count and paging keeps its existing meaning on the smaller set. `error_count` is recomputed on the same filtered row list; because failed-to-parse rows carry `id=None` and never match any `glob`, a `glob`-given result has no failed rows and `error_count = 0` by construction (keeping the whole-directory count would allow `error_count > total`). Broken-document discovery — the `repair` workflow's `list_<d>`-based surfacing of failed rows — therefore stays an unfiltered-listing / `ref`-based job: ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 rejected hiding parse failures for exactly this reason. For `feat` specifically the row build is feat-187's two-stage (dirty/clean `DocCache`) resolution — the filter applies to the rows it produces and must not re-scan the filesystem on its own (that would bypass the cache and regress the cold-scan timeout fix) — and during the warmup window a not-yet-fully-parsed broken folder transiently resolves to a healthy row with a real id (so it can match) before converging to an `id=None` failed row; the filter sees whatever its row build produces, healthy or failed.

One shared helper. The filter lives in a single function in `general/tools/` (alongside the other shared list plumbing) and is called by all twelve tools, so the matching rule cannot drift between domains and is tested in one place.

### Related Decisions

- ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: listing is a paged `list_<d>` tool, not a `specmgr://<d>/list` resource — this feature extends those tools' parameter surface.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (feat-187): `list_feat`'s two-stage dirty/clean `DocCache` — the filter must sit after that resolution (see Design Notes).

### Task List

#### Phase 100: list_feat glob

- [x] Task 100.100: Add the shared id-glob filter helper in `general/tools/` (lowercase id + pattern, then `fnmatchcase`) with unit tests.
- [x] Task 100.110: Add the `glob: str | None = None` parameter to `list_feat`, applied after the domain's row build (both cache stages) and before `total`/paging; update the docstring.
- [x] Task 100.120: Tests for `list_feat` on fixture corpora (temp dir, `SPECMGR_FEAT_DIR` overridden): the `feat-7*` case, filtered `total`/`offset`/`truncated`/`error_count`, uppercase-pattern case-insensitivity, failed-row exclusion for a broken fixture (ACC-005), and unchanged `glob=None` output.

#### Phase 110: Extend to the other list tools

- [x] Task 110.100: Add the same `glob` parameter to the eleven other paged `list_<d>` tools via the shared helper.
- [x] Task 110.110: Tests for a UUID-prefix match (e.g. `dead*`) on fixture corpora plus docstring updates and `docs/MCP.md` regeneration.

#### Phase 120: Quality gate

- [x] Task 120.100: Run `ruff format --check`, `ruff check`, `vulture`, the full `pytest` suite, and the `specmgr docs`/`specmgr mcp-docs` drift checks; update this feature's Progress section.

## Progress

### Current Status

**As of 2026-10-07**: All three phases complete — the feature is ready for review.

- Phase 100 (`list_feat` glob): the shared `filter_summaries_by_glob` helper in `general/tools/_listing.py` (with unit tests), the `glob: str | None = None` parameter on `list_feat` (applied to the materialized row list after feat-187's two-stage dirty/clean resolution and before `total`/paging), and `tests/feat/tools/test_list_feat_glob.py` (ACC-001, ACC-004, ACC-005, REQ-004, the empty-string-is-a-pattern decision, and the `glob=None`-unchanged half of ACC-003).
- Phase 110 (eleven other tools): the same `glob` parameter on `list_req`/`list_uc`/`list_tsk`/`list_qa`/`list_prb`/`list_gol`/`list_rsk`/`list_dec`/`list_sop`/`list_vcr`/`list_sysrs`, each wired to the shared helper between its row build and `total`/paging, one new per-domain fixture test module each (`tests/<d>/tools/test_list_<d>_glob.py`; the `req` module additionally carries the plan's named ACC-002/ACC-004/ACC-005 additions), docstrings updated, `docs/MCP.md`/`docs/api/` regenerated.
- Phase 120 (quality gate): every gate green, each walked with per-test evidence for ACC-001..ACC-005 (see the 2026-10-07T15:22:39.247+02:00 Updates entry):
  - `uv run --frozen ruff format --check` — 1925 files already formatted (pass)
  - `uv run --frozen ruff check` — All checks passed! (pass)
  - `uv run --frozen vulture src/ whitelist.py --min-confidence 60` — no output, exit 0 (pass)
  - `uv run --frozen pytest -n auto --cov=src --cov-report=` — 4137 passed in 72.68s (pass)
  - `uv run --frozen specmgr docs` / `specmgr mcp-docs` / `specmgr coverage-badge` — all idempotent, `git status --short` clean after each (pass)

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T17:03:20.962+02:00 - Post-implementation review findings addressed (G1/D1/D2); watch item recorded

Addressed the three findings of the post-implementation code review (docs only; no production or test code changes): (G1) `CHANGELOG.md` gained the feature's missing `[Unreleased]` `### Added` bullet for the new `glob` id-filter parameter on the twelve paged `list_<d>` tools, placed before the pre-existing `### Changed` per Keep a Changelog section order; (D1) the Phase-120 entry's claim that all thirteen test files on the branch were pure additions was corrected to the factually accurate form — twelve new `test_list_<d>_glob.py` modules plus one appended `TestFilterSummariesByGlob` class in the pre-existing `tests/general/tools/test__listing.py` (the change is additive-only, zero removed or altered lines, so ACC-003's substance holds); (D2) the five `### Acceptance Criteria` boxes ACC-001..ACC-005 were ticked to `- [x]` (criterion text untouched), each covered by the named, passing tests the Phase-120 entry walks to its test. The review's watch item is recorded here: commit `52ab39c`'s message discloses that `tests/feat/tools/test_list_feat_glob.py` failed intermittently under the pre-commit hook's staged-snapshot full-suite run (order-dependent; passes standalone and in direct full-suite runs); the post-implementation review could not reproduce it (two full-suite runs, 4137 passed) and found no mechanism, so it is tracked as a watch item with no code change.

#### 2026-10-07T15:36:37.959+02:00 - Status set to review

All three phases (100/110/120) are implemented, committed, and gate-green (4137 tests, ruff/vulture clean, doc/schema drift idempotent); the frontmatter status moved from `progress` to `review` for the post-implementation review and the pull request against `dev`.

#### 2026-10-07T15:22:39.247+02:00 - Phase 120 complete: quality gate green, ACC-001..ACC-005 walked

Ran every gate of Task 120.100 — all green on the first run, no production or test changes needed. `ruff format --check`: 1925 files already formatted. `ruff check`: All checks passed! `vulture src/ whitelist.py --min-confidence 60`: no output (clean, exit 0). `pytest -n auto --cov=src --cov-report=`: 4137 passed in 72.68s. Drift checks `specmgr docs` (487 module files + GENERATED.md), `specmgr mcp-docs` (docs/MCP.md), and `specmgr coverage-badge` (docs/coverage.svg, 99%) all idempotent — `git status --short` clean after each. ACC walk (re-run with `-v`, every covering test PASSED): ACC-001 → `tests/feat/tools/test_list_feat_glob.py::TestListFeatGlob::test_acc001_glob_returns_exactly_the_matching_features_and_no_others`; ACC-002 → `tests/req/tools/test_list_req_glob.py::TestListReqGlob::test_acc002_known_repo_uuid_matches_in_any_case_of_the_pattern` (the real `docs/req` UUID `10b78b36-abad-4bfe-9281-f75677ff7d09`, subtests over `10b7*` and `10B7*`); ACC-003 → all thirteen test-file changes on this branch are additive-only (twelve new `test_list_<d>_glob.py` modules plus one appended test class in the pre-existing `tests/general/tools/test__listing.py`; no pre-existing test modified or removed) and the full suite's pre-existing `test_list_<d>.py` suites stayed green, plus the per-module `glob=None`-unchanged tests (feat `test_acc003_glob_none_output_is_unchanged`, the other eleven domains `test_glob_none_output_is_unchanged_and_reports_the_full_corpus`); ACC-004 → `test_acc004_paging_composes_with_the_glob_filter` in both the `feat` and `req` modules; ACC-005 → `test_acc005_broken_folder_is_reported_unfiltered_but_absent_for_any_glob` (feat) and `test_acc005_broken_file_is_reported_unfiltered_but_absent_for_any_glob` (req). Scope discipline confirmed: the `src/` diff over 52ab39c..HEAD is exactly `general/tools/_listing.py` plus twelve `tools/list_<d>.py` files; `adr/tools/list_adr.py` is unmodified and contains no `glob`; the shared helper is untouched by Phase 110 (empty diff 7a0f297..HEAD). No decision was forced this phase, so Decisions Made is unchanged.

#### 2026-10-07T14:43:27.097+02:00 - Phase 110 complete: the glob parameter on the eleven other list tools

Implemented Phase 110 (Tasks 110.100/110.110): the same optional `glob: str | None = None` parameter (third position, after `max_results`/`offset`) on `list_req`/`list_uc`/`list_tsk`/`list_qa`/`list_prb`/`list_gol`/`list_rsk`/`list_dec`/`list_sop`/`list_vcr`/`list_sysrs`, each calling the shared `general.tools._listing.filter_summaries_by_glob` helper once, between its own `build_summaries` row build and the `total`/`offset`/`max_results`/`truncated` step (`list_adr` remains out of scope, `list_feat` already shipped in Phase 100; the helper itself is untouched). Each tool's `@mcp.tool` description gained the glob sentence (UUID-prefix example `dead*`), its numpydoc docstring the materialize→filter→paginate intro, the `glob` Parameters entry, and the Returns clarification, in the `list_feat` precedent's own style; `rsk`'s module docstring additionally notes that its sentinel-built failed rows also carry `id=None`/`error`, so the helper's `error_count = 0`-by-construction guarantee holds for it like the other domains. Eleven new fixture test modules `tests/<d>/tools/test_list_<d>_glob.py` (per-test temp `SPECMGR_DOCS_DIR`, the domain cache reset in `setUp`/`tearDown`, hand-built corpus written directly to disk: two healthy documents with known different-prefix UUIDs `deadbeef-*`/`cafe...` plus one broken file) cover the per-domain floor — UUID-prefix match (exactly the matching rows, filtered `total`, `error_count = 0`), uppercase/mixed-case pattern case-insensitivity, and `glob=None`-unchanged output reporting the full corpus including the failed row — and the `req` module additionally carries the plan's named ACC-002 (a real UUID read off `docs/req/req-10b78b36-abad-4bfe-9281-f75677ff7d09-verification-case-record-document-management.md`, pattern `10b7*`/`10B7*`), ACC-004 (paging composes with the filter on the two-match `dead*` corpus), and ACC-005 (broken file reported unfiltered, absent and `error_count = 0` for any glob including `*`). All pre-existing `tests/<d>/tools/test_list_<d>.py` stay green untouched (ACC-003). Regenerated `docs/MCP.md` (the `glob` parameter row + description sentence for all eleven tools), the eleven `docs/api/biz.dfch.specmgr.<d>.tools.list_<d>.md` files, and `docs/GENERATED.md`'s test-file count (384 → 395); `docs/coverage.svg` is unchanged (99% before and after).

#### 2026-10-07T10:56:19.858+02:00 - Phase 100 complete: the list_feat glob parameter

Implemented Phase 100 (Tasks 100.100/100.110/100.120): (1) the shared id-glob helper `filter_summaries_by_glob(summaries, pattern) -> (filtered, error_count)` in `general/tools/_listing.py` — a row matches iff `fnmatchcase(row.id.lower(), pattern.lower())`, rows with `id=None` never match, and the returned `error_count` is recomputed on the filtered list (a glob-given result therefore has `error_count = 0` by construction) — plus its unit tests in `tests/general/tools/test__listing.py`; (2) the `glob: str | None = None` parameter on `list_feat`, applied to the materialized row list after feat-187's two-stage (dirty/clean `DocCache`) resolution loop and before the `total`/paging step (never a filesystem re-scan), with the numpydoc and `@mcp.tool` description updated (regenerated into `docs/MCP.md`); (3) the new fixture tests `tests/feat/tools/test_list_feat_glob.py` (per-test temp `SPECMGR_FEAT_DIR`, both feat cache stages reset, a small hand-built corpus of two `feat-7*` + two non-matching + one broken folder): ACC-001, ACC-004 (paging composes with the filter), ACC-005 (broken row reported unfiltered, absent and `error_count = 0` for any glob), REQ-004 (uppercase patterns), the empty-string-is-a-pattern decision, `glob=None`-unchanged output, and rows produced by both cache stages. All pre-existing `tests/feat/tools/test_list_feat*.py` stay green without modification. Also corrected this feature's frontmatter `status`, which commit 722a135 had prematurely set to `done` before any implementation existed, back to `progress`.

#### 2026-10-07T09:17:56.462+02:00 - Plan refined (feat-refiner pass)

Refined the plan against the codebase (no implementation): `error_count` is now recomputed on the filtered row list, so a `glob`-given result has `error_count = 0` by construction (failed rows carry `id=None` and never match; broken-document discovery stays an unfiltered-listing / `ref`-based job — new ACC-005); `list_adr` named explicitly out of scope (ADR phase-out, `AdrSummary` not a `DocSummary` subclass, no failed rows); the case-insensitivity rationale corrected (by-id lookups are exact and case-sensitive — ids are merely stored in canonical lowercase — a deliberate search-UX choice); a `### Dependencies` section added with a machine-resolvable `FEAT feat-187-list-feat-timeout` reference; REQ-005's quantifier aligned with ACC-003 ("all twelve"); ACC-001/Task 100.120/Task 110.110 switched from the live repo corpus to fixture corpora (`SPECMGR_FEAT_DIR` overridden, the feat-187 test convention); the Created and Decisions-Made entry timestamps aligned to the frontmatter `created` (`2026-10-07T07:48:18.241+02:00`, the programmatic stamp taken as authoritative over the earlier hand-written clock).

#### 2026-10-07T07:48:18.241+02:00 - Created

Created the feature plan for GitHub issue #200 (an optional `glob` id-filter parameter for `list_feat` and the other paged `list_<d>` tools).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T14:43:27.097+02:00 - Fixture writing: direct disk writes with hand-authored frontmatter

The Phase 110 fixture corpora are written directly to disk rather than via `create_<d>` (which would assign random `uuid4` ids the filter could not be tested against deterministically): each healthy fixture is a minimal valid body copied from the domain's own pre-existing `tests/<d>/tools/test_list_<d>.py` (`_MINIMAL_BODY`, plus for `dec`/`rsk` that test's own `MANDATORY_*` helper snippet) under a hand-authored frontmatter block carrying the chosen id (`deadbeef-...`/`cafe...`), `status: draft`, and the domain's `type` discriminator. One domain-specific wrinkle: `rsk`'s closed status vocabulary (`accepted`/`closed`/`dropped`/`mitigating`/`occurred`/`open`) has no `draft`, so the `rsk` fixtures use `status: open` (surfaced by a parse failure in the first test run). The `req` corpus carries two `deadbeef-*` documents so its ACC-004 paging test has N = 2 matches; the other ten domains carry one each (the plan's floor).

#### 2026-10-07T10:56:19.858+02:00 - Helper location and signature

Per the plan's recommendation, the shared helper lives in `general/tools/_listing.py` (the existing doc-type-agnostic summary plumbing module; no `mcp` import, `__all__` extended). Named `filter_summaries_by_glob(summaries: list[_SummaryT], pattern: str) -> tuple[list[_SummaryT], int]` — bound to that module's existing `DocSummary`-bound `_SummaryT` TypeVar — returning the filtered rows *and* the recomputed `error_count` (rows whose `error` field is set) so every tool that takes the parameter calls it in one place and `error_count` cannot drift from the filtered row list. The caller keeps the `glob is not None` guard itself, so the `REQ-005` no-op path stays structurally untouched.

#### 2026-10-07T07:48:18.241+02:00 - Parameter named glob; matching is case-insensitive

Issue #200 proposed the name `glob` (alternative: `filter`); `glob` was chosen because it names the matching semantics. Matching was settled as case-insensitive — the stored id and the pattern are both lowercased before `fnmatchcase` — because ids are stored in one canonical lowercase form (`feat` slugs are shape-validated, UUIDs via `str(uuid.uuid4())`); by-id lookups are exact and case-sensitive, so the case-insensitive glob is a deliberate search-UX choice, not an alignment with existing lookup behaviour. An empty-string pattern matches nothing; only `None` disables filtering.

### Related PRs / Commits

- [Issue #200](https://github.com/dfch/biz.dfch.SpecMgr/issues/200): tracking issue for this feature.
