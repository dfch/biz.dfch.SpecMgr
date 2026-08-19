---
created: 2026-08-19
id: feat-13-list-paging
status: planning
updated: 2026-08-19
version: 1.0.0
---

# Feature: Pagination for `<domain>_list` MCP tools

## Plan

### Overview

Convert the five `<domain>_list` MCP resources (`adr_list`, `req_list`,
`uc_list`, `tsk_list`, `qa_list`) into `@mcp.tool()` tools that support
pagination via `max_results`/`offset`, returning a shared `PagedResult`
wrapper. Split out of `feat-7-various-improvements` Task 0.15 (and closes
its REQ-002/ACC-002 pagination decision) into a dedicated, orchestrator-
drivable feature folder.

Today every `<domain>_list` is an `@mcp.resource("specmgr://<d>/list")`
returning a bare `list[<D>Summary]` via a full, unbounded
`sorted(glob("*.md"))` scan on every call. MCP resources cannot take
arbitrary parameters (only URI-template path segments), so
`max_results`/`offset` fit cleanly only as tool parameters — the same
resource→tool reasoning already applied in feat-7 Task 0.9 (`get_req`).

### Requirements

- REQ-001: All five `list_<domain>` tools share one documented paged output
  contract — a `PagedResult` wrapper with fields `total`, `offset`,
  `max_results`, `truncated`, `results`.
- REQ-002: `max_results`/`offset` with a sane default page size (25) and cap
  (100); out-of-range inputs are clamped, not errored (mirrors this
  project's `asdste100` MCP tools).
- REQ-003: The five id/title/status/`ref` summaries share a documented
  common base model (carries forward feat-7 ACC-001).
- REQ-004: No behavioral regression in directory scan/sort/skip-broken-file
  semantics; each domain's existing parse-failure exception tuple is
  preserved.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — all five tools return the same
  `PagedResult` shape, asserted by tests across every domain.
- [ ] ACC-002: Verifies REQ-002 — tests cover default page size, cap
  clamping, negative-offset flooring, and `offset` past the end returning
  empty `results` with `truncated == False`.
- [ ] ACC-003: Verifies REQ-003 — all five Summary models share a common
  base field set, asserted by a shared/side-by-side test.
- [ ] ACC-004: Verifies REQ-004 — existing skip-malformed-file and
  empty-directory behavior still holds; per-domain exception tuples
  unchanged.

### Scope

What is included in this feature:

- New shared infrastructure in `general/`: `PagedResult[T]` model and a
  `paginate`/`normalize_paging` helper.
- Optional shared base `DocSummary` for the five Summary models.
- Resource→tool conversion of all five `<domain>_list` (adr/req/uc/tsk/qa),
  including deleting the old resource modules and updating registrations.
- Repointing prompt instruction files and `server.py` docstring from
  `specmgr://<d>/list` to the new `list_<d>` tool.
- A short ADR recording the resource→tool + `PagedResult` contract decision.

What is explicitly out of scope:

- Filtering (feat-7 Task 0.16) — the contract must stay forward-compatible
  with it, but no filtering is implemented here.
- Migrating ADR onto the shared `general/tools/_doc_paths` module — ADR
  keeps its own `adr/tools/_paths` (only its resource→tool layer changes).
- Any change to the `specmgr://<d>/{id}` / `get_<d>` single-document reads.

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr`
  feature-folder structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2
  (domain-first hierarchy).
- Split out of: `feat-7-various-improvements` Task 0.15 (pointer left in
  that file). Closes feat-7 REQ-002/ACC-002; advances feat-7 REQ-001/ACC-001.
- Blocks: feat-7 Task 3.1b (pagination piece of the list-resource contract).

### Design Notes

- **Result shape** is taken verbatim from this project's `asdste100` MCP
  tools (e.g. `word_list`, `rules_examples`), whose live shape is
  `{ total, offset, max_results, truncated, results: [...] }`. Reused rather
  than invented so the contract is consistent across d-fens MCP servers.
- **Full materialize, then slice.** `total` must reflect the count of
  *parseable* documents (skip-broken-file semantics), so each tool builds
  the complete `summaries` list exactly as today, then paginates the
  in-memory list. Behavior is therefore identical to the current scan; a
  streaming/early-stop optimization is explicitly out of scope.
- **Tool naming** `list_<domain>` (verb-first, matching `get_<domain>` /
  `create_<domain>`). The retired resource *name* `<domain>_list` is not
  resurrected as a tool name.
- **Module location** `<d>/tools/list_<d>.py` (it is now a tool, so it
  belongs under `tools/`, not `resources/`), registered in
  `<d>/tools/__init__.py` like `get_<d>`.
- **ADR outlier.** ADR uses its own `adr/tools/_paths.iter_adr_paths` and
  the top-level `models/adr` `AdrSummary`; the conversion happens at the
  tool layer only, leaving its `_paths` untouched. Its parse-failure tuple
  `(AdrParseError, ValidationError)` differs from the others'
  `(AssertionError, ValidationError)` — this divergence is intentional and
  must be preserved (REQ-004).
- **Shared base Summary** (`DocSummary`) is the concrete way to satisfy
  ACC-001/REQ-003; the five domain Summaries subclass it, keeping their
  domain-specific docstrings.

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
  `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: `get_req` tool vs. resource
  (precedent for resource→tool for agent reliability)
- (to be written) short ADR recording the `<domain>_list` resource→tool +
  `PagedResult` contract decision (Task 4.3)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 1: Shared infrastructure

- [x] Task 1.1: Add `general/models/` sub-package (does not exist yet) with
  `paged_result.py` — `PagedResult(BaseModel, Generic[T])`, fields in order
  `total: int`, `offset: int`, `max_results: int`, `truncated: bool`,
  `results: list[T]`, fully documented per `.specmgr/conventions.md`; export
  from `general/models/__init__.py` — depends on: none — status: done
- [x] Task 1.2: Add `general/tools/_paging.py` (no `mcp` dependency, like
  `_doc_paths.py`): `DEFAULT_MAX_RESULTS = 25`, `MAX_MAX_RESULTS = 100`,
  `normalize_paging(max_results, offset) -> tuple[int, int]` (clamp/floor),
  `paginate(items, offset, max_results) -> PagedResult[T]` (`total = len`,
  slice, `truncated = offset + max_results < total`) — depends on: Task 1.1
  — status: done
- [x] Task 1.3: Add `general/models/summary.py::DocSummary(BaseModel)` with
  the four common fields (`id`, `title`, `status`, `ref`) and make
  `AdrSummary`/`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary` subclass it
  (ACC-001/REQ-003) — depends on: none — status: done, with one deliberate
  exception: `AdrSummary` does **not** subclass `DocSummary` (see Decisions
  Made below) — `ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary` do.
- [x] Task 1.4: Tests — `tests/general/models/test_paged_result.py`,
  `tests/general/tools/test_paging.py` (empty, exact-fit, over-offset,
  `truncated` boundary, clamping, negative offset), and (if 1.3 adopted) a
  shared-base assertion — depends on: Task 1.1, Task 1.2, Task 1.3 —
  status: done (`tests/general/models/test_summary.py` added for the
  shared-base assertion, including the structural-equivalence check for
  the `AdrSummary` exception)
- [x] Task 1.5: Phase gate — `ruff format --check`, `ruff check`,
  `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite —
  depends on: Task 1.4 — status: done, all green (see Recent Updates)

#### Phase 2: Per-domain resource→tool conversion

Each of these adds `<d>/tools/list_<d>.py` (`@mcp.tool(name="list_<d>")`
returning `PagedResult[<D>Summary]`, same scan + preserved exception tuple,
then `paginate(summaries, *normalize_paging(...))`), deletes
`<d>/resources/<d>_list.py`, drops its import/`__all__` from
`<d>/resources/__init__.py`, registers the tool in `<d>/tools/__init__.py`,
updates `<d>/__init__.py`'s module docstring, and moves/rewrites that
domain's list test to `tests/<d>/tools/test_list_<d>.py` with paging
assertions. All depend only on Phase 1 (parallelizable).

- [x] Task 2.1: ADR (`adr/tools/list_adr.py`; delete
  `adr/resources/adr_list.py`; keep `adr_get` in
  `adr/resources/__init__.py`; uses `iter_adr_paths` + top-level
  `AdrSummary`; exception tuple `(AdrParseError, ValidationError)`) —
  depends on: Task 1.5 — status: done
- [x] Task 2.2: REQ (`req/tools/list_req.py`) — depends on: Task 1.5 —
  status: done
- [x] Task 2.3: UC (`uc/tools/list_uc.py`; uses `..models.v2` `UcSummary`)
  — depends on: Task 1.5 — status: done
- [x] Task 2.4: TSK (`tsk/tools/list_tsk.py`) — depends on: Task 1.5 —
  status: done
- [x] Task 2.5: QA (`qa/tools/list_qa.py`) — depends on: Task 1.5 —
  status: done
- [x] Task 2.6: Phase gate — `ruff format --check`, `ruff check`,
  `vulture src/ whitelist.py --min-confidence 60` (catches the five deleted
  resource modules), full `unittest` suite — depends on: Task 2.1, Task 2.2,
  Task 2.3, Task 2.4, Task 2.5 — status: done, all green (see Recent
  Updates); one pre-existing test
  (`tests/commands/test_docs.py::test_count_mcp_features_matches_known_counts`)
  needed its hardcoded ADR tool/resource counts updated (11->12 tools,
  2->1 resources) to reflect the resource->tool conversion -- `docs/
  GENERATED.md`/`docs/MCP.md` themselves are left stale on purpose,
  regeneration is Task 4.1

#### Phase 3: Cross-references

- [ ] Task 3.1: Repoint `specmgr://<d>/list` mentions in prompt instruction
  data files (`qa/data/qa_create_instructions.md`,
  `qa/data/qa_refine_instructions.md`, `adr/data/adr_create_instructions.md`,
  `adr/data/adr_create_test_instructions.md`,
  `tsk/data/tsk_create_instructions.md`, `req/data/req_create_instructions.md`)
  and `qa/prompts/refine.py`'s docstring to the new `list_<d>` tool; update
  `tests/qa/prompts/test_refine.py` if it asserts the old resource string —
  depends on: Phase 2 — status: not-started
- [ ] Task 3.2: `server.py` module docstring — remove the five
  `specmgr://<d>/list` resource lines, add `list_<d>` to each domain's Tools
  line — depends on: Phase 2 — status: not-started

#### Phase 4: Verify & document

- [ ] Task 4.1: Regenerate `docs/api/`/`docs/GENERATED.md`
  (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 —
  depends on: Task 3.1, Task 3.2 — status: not-started
- [ ] Task 4.2: Full quality gate — `ruff format --check`, `ruff check`,
  `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite —
  depends on: Task 4.1 — status: not-started
- [ ] Task 4.3: Write a **short** ADR recording the resource→tool +
  `PagedResult` contract decision (mirroring ADR `ddfb1109`'s precedent);
  run `specmgr adr-toc`; update `AGENTS.md` if the per-domain
  resource/tool inventory shifts — depends on: Task 4.2 — status: not-started
- [ ] Task 4.4: Back-update `feat-7-various-improvements/README.md` — mark
  Task 0.15 done/split, close REQ-002/ACC-002, advance REQ-001/ACC-001,
  update Task 2.1/3.1b status lines — depends on: Task 4.3 — status:
  not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-19**: Phase 1 and Phase 2 are done. `PagedResult`
(`general/models/paged_result.py`), `DocSummary`
(`general/models/summary.py`), and the `normalize_paging`/`paginate` helpers
(`general/tools/_paging.py`) all exist, tested, and pass the full quality
gate. `ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary` now subclass
`DocSummary`; `AdrSummary` deliberately does not (see Decisions Made). All
five `<domain>_list` resources (`adr_list`, `req_list`, `uc_list`,
`tsk_list`, `qa_list`) have been converted into paged `list_<domain>`
`@mcp.tool()`s (`adr/tools/list_adr.py`, `req/tools/list_req.py`,
`uc/tools/list_uc.py`, `tsk/tools/list_tsk.py`, `qa/tools/list_qa.py`),
each returning `PagedResult[<D>Summary]` and preserving its own
skip-malformed-file exception tuple exactly (REQ-004). Next: Phase 3
(cross-references -- repoint `specmgr://<d>/list` mentions in prompt
instruction data files and `server.py`'s docstring to `list_<d>`).

### Recent Updates

#### Update 2026-08-19 (newest)

- Completed: Phase 2 (Per-domain resource->tool conversion) -- Tasks
  2.1-2.6.
  - Added `adr/tools/list_adr.py`, `req/tools/list_req.py`,
    `uc/tools/list_uc.py`, `tsk/tools/list_tsk.py`, `qa/tools/list_qa.py`
    -- each an `@mcp.tool(name="list_<d>")` returning
    `PagedResult[<D>Summary]`; same directory scan and skip-broken-file
    logic as the retired resource, then
    `paginate(summaries, *normalize_paging(max_results, offset))`.
    ADR's `(AdrParseError, ValidationError)` exception tuple and the other
    four's `(AssertionError, ValidationError)` were both preserved exactly
    unchanged, per-domain.
  - Deleted the five retired resource modules: `adr/resources/adr_list.py`,
    `req/resources/req_list.py`, `uc/resources/uc_list.py`,
    `tsk/resources/tsk_list.py`, `qa/resources/qa_list.py`.
  - Updated every `<d>/resources/__init__.py` to drop the `<d>_list`
    import/`__all__` entry (ADR's `adr_get` stays); updated every
    `<d>/tools/__init__.py` to register `list_<d>`; updated every
    `<d>/__init__.py`'s own module docstring where it enumerated
    tools/resources.
  - Migrated list tests: `tests/adr/tools/test_list_adr.py` (new; the old
    `TestAdrListResource` class was removed from
    `tests/adr/resources/test_adr.py`, leaving `TestAdrGetResource` in
    place), `tests/req/tools/test_list_req.py`,
    `tests/uc/tools/test_list_uc.py`, `tests/tsk/tools/test_list_tsk.py`,
    `tests/qa/tools/test_list_qa.py` (each replaces the deleted
    `tests/<d>/resources/test_<d>_list.py`). Each migrated
    skip-malformed-file/empty-directory coverage as-is, plus added: default
    page size/shape, `max_results` limiting + `truncated`, `offset` paging
    to a second page, `max_results` clamped to the cap, negative `offset`
    floored to zero, `truncated` boundary (false when a page exactly covers
    all items, true when one item remains), and `total` reflecting the full
    parseable count independent of paging.
  - Fixed one pre-existing test that broke as a direct, expected
    consequence of the ADR resource->tool conversion:
    `tests/commands/test_docs.py::test_count_mcp_features_matches_known_counts`
    hardcoded ADR's tool/resource counts (11/2); updated to 12/1 now that
    `list_adr` lives under `adr/tools/` instead of `adr/resources/`.
    `docs/GENERATED.md`/`docs/MCP.md` themselves are deliberately left
    stale -- their regeneration is Task 4.1, not Phase 2's job.
  - Quality gate: `ruff format --check`, `ruff check`,
    `vulture src/ whitelist.py --min-confidence 60`, and the full
    `unittest` suite (1276 tests) all pass clean.
- Next: Phase 3 (cross-references, Tasks 3.1-3.2).

- Completed: Phase 1 (Shared infrastructure) — Tasks 1.1-1.5.
  - Added `general/models/` (new sub-package): `__init__.py`,
    `paged_result.py::PagedResult(BaseModel, Generic[T])`,
    `summary.py::DocSummary(BaseModel)`.
  - Added `general/tools/_paging.py`: `DEFAULT_MAX_RESULTS`/
    `MAX_MAX_RESULTS`/`MIN_MAX_RESULTS`/`MIN_OFFSET` constants,
    `normalize_paging(max_results, offset) -> tuple[int, int]` (returns
    `(offset, max_results)`, clamped/floored), `paginate(items, offset,
    max_results) -> PagedResult[T]`.
  - Made `ReqSummary`, `UcSummary`, `TskSummary`, `QaSummary` subclass
    `DocSummary`, dropping their now-duplicated field declarations.
    `AdrSummary` was deliberately **not** changed to subclass it (see
    Decisions Made) — a structural-equivalence test covers it instead.
  - Added tests: `tests/general/models/test_paged_result.py`,
    `tests/general/models/test_summary.py` (`DocSummary` +
    shared/side-by-side base-field-set assertion across all five domains),
    `tests/general/tools/test_paging.py` (empty, exact-fit, over-offset,
    `truncated` boundary, clamping, negative-offset flooring,
    `normalize_paging` + `paginate` splat-unpacking integration).
  - Added `results`/`truncated` to `whitelist.py`'s "Pydantic model fields
    read only via (de)serialization/rendering" section (flagged by
    vulture since nothing under `src/` reads them as plain attributes
    yet -- that lands in Phase 2).
  - Quality gate: `ruff format --check`, `ruff check`,
    `vulture src/ whitelist.py --min-confidence 60`, and the full
    `unittest` suite (1236 tests) all pass clean.
- Next: Phase 2 (per-domain resource→tool conversion, Tasks 2.1-2.6).
- Notes: Confirmed via a simulated mcp-import-blocked run that
  `biz.dfch.specmgr.models.adr`/`AdrSummary` still import successfully
  without the `mcp` extra installed, preserving the base-library
  invariant documented in `AGENTS.md`'s "models location" note.

#### Update 2026-08-19

- Completed: Created GitHub issue #13; created this feature folder from
  `.specmgr/_template/v1/README.md` with the full four-phase plan.
- Next: Phase 1 (shared `PagedResult` model + `_paging` helper).
- Notes: Split out of `feat-7` Task 0.15; a pointer was added there.

### Decisions Made

- **2026-08-19**: Convert `<domain>_list` from `@mcp.resource` to
  `@mcp.tool()` (`list_<domain>`) — resources cannot take arbitrary
  parameters, so paging params only fit as tool inputs; consistent with the
  feat-7 Task 0.9 `get_req` resource→tool precedent.
- **2026-08-19**: Return an `asdste100`-style `PagedResult` wrapper
  (`total`/`offset`/`max_results`/`truncated`/`results`) — reuse an existing
  d-fens MCP shape rather than invent one.
- **2026-08-19**: Put paging infrastructure in `general/`
  (`general/models/PagedResult`, `general/tools/_paging`) shared by all five
  domains; ADR stays the outlier (own `_paths`), converted at the tool layer
  only.
- **2026-08-19**: Paging only; filtering stays feat-7 Task 0.16, but the
  contract must remain forward-compatible with it.
- **2026-08-19**: `normalize_paging` clamping semantics (not fully pinned
  down by the plan text): a caller-supplied `max_results` out of
  `[MIN_MAX_RESULTS, MAX_MAX_RESULTS]` is *clamped* to the nearer bound
  (e.g. `500` -> `100`, `0` -> `1`), not reset to `DEFAULT_MAX_RESULTS`;
  only an actually-absent (`None`) `max_results`/`offset` gets the default
  (`DEFAULT_MAX_RESULTS`/`0`). A negative `offset` floors to `0`.
  `normalize_paging` returns `(offset, max_results)` -- offset first, the
  reverse of its own parameter order -- specifically so Phase 2 call sites
  can write `paginate(items, *normalize_paging(max_results, offset))`
  exactly as sketched in the Phase 2 task description, since `paginate`
  takes `(items, offset, max_results)`.
- **2026-08-19 (Task 1.3 implementation note -- flagging for follow-up)**:
  `AdrSummary` (`models/adr/v1/summary.py`) does **not** subclass the new
  `general/models/summary.py::DocSummary`, unlike the other four domains.
  Root cause: `models/adr` is documented (`AGENTS.md`'s "models location"
  note) as having *no* dependency on `mcp`/`tools`/`resources`/`prompts`,
  so it stays usable from the dependency-free base library without the
  `mcp` extra installed. `general/__init__.py`, however, unconditionally
  imports `general.tools`/`general.resources`/`general.prompts`, which
  import `server.mcp` -- so importing anything under `general` (including
  `general.models`) already requires the `mcp` extra, by way of Python
  needing to run every ancestor package's `__init__.py`. Making
  `AdrSummary` subclass `DocSummary` would therefore silently add a new,
  previously-absent `mcp` dependency to `models.adr` -- confirmed by
  actually blocking `mcp`'s import and re-running
  `from biz.dfch.specmgr.models.adr import AdrSummary`, which succeeds
  today and would not once `AdrSummary` imports from `general`. Resolved
  conservatively: `AdrSummary` keeps its own field-identical declaration;
  `tests/general/models/test_summary.py` asserts structural (not
  inheritance-based) equivalence for it, plus a side-by-side field-set
  assertion across all five Summary classes for ACC-001/ACC-003. **Flagged
  for a follow-up decision** (candidate for Task 4.3's short ADR, or an
  `AGENTS.md` update): whether this asymmetry is acceptable long-term, or
  whether `DocSummary` should instead live somewhere with no `general`/
  `mcp` dependency (e.g. top-level `models/`, alongside `models/adr` and
  `models/iso25010.py`) so `AdrSummary` can subclass it too.
- **2026-08-19 (Phase 2)**: The ADR resource->tool conversion shifts one
  module from `adr/resources/` to `adr/tools/`, which changes the
  hardcoded MCP feature counts a pre-existing test
  (`tests/commands/test_docs.py::test_count_mcp_features_matches_known_counts`)
  asserts (11 tools/2 resources -> 12 tools/1 resource). Updated that
  test's literals in place rather than deferring the fix to Phase 4,
  since Phase 2's own quality gate requires a green full test suite.
  `docs/GENERATED.md`/`docs/MCP.md` regeneration (which would otherwise
  reflect the same shift) stays out of scope here -- that is explicitly
  Task 4.1's job, run once after every domain's cross-references are
  repointed in Phase 3.

### Related PRs / Commits

- [Issue #13](https://github.com/dfch/biz.dfch.SpecMgr/issues/13): Add
  pagination to `<domain>_list` (resource→tool + shared `PagedResult`)
