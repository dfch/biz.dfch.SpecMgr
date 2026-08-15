---
created: 2026-08-15
id: feat-7-various-improvements
status: planning
updated: 2026-08-15
version: 1.0.0
---

# Feature: Various cross-cutting improvements

## Plan

### Overview

A rolling bucket for small, cross-cutting improvements that touch more than
one document domain (`adr`/`req`/`uc`/`general`) but are each too small to
justify their own `feat-NNN-slug` folder. Sections/tasks are added here as
new concerns come up; a concern gets split into its own feature folder if
it grows large enough to need dedicated requirements/acceptance criteria of
its own (see Design Notes).

The first tracked concern: standardizing the output format/contract of the
MCP `specmgr://*/list` resources (`adr_list`, `req_list`, and any future
`uc_list`/`ac_list`), and reviewing/optimizing the MCP `@mcp.prompt()`
modules (`adr/prompts/`, `req/prompts/`) for consistency and token
efficiency, including deciding the fate of the step-gated `_test` prompt
variants (`adr/prompts/create_adr_test.py`, `update_adr_test.py`) that
currently exist alongside the narrated originals for A/B comparison.

### Requirements

- REQ-001: All `specmgr://*/list` resources (`adr_list`, `req_list`, and
  future `uc_list`/`ac_list`) share a consistent, documented output
  contract (fields, sort order, skip-on-parse-failure semantics).
- REQ-002: A decision is made on whether/how list resources should support
  pagination or size limits as the number of documents in a base directory
  grows (both `adr_list` and `req_list` currently do a full, unbounded
  directory scan on every call).
- REQ-003: Every existing MCP prompt module (`create_adr`, `update_adr`,
  `create_adr_test`, `update_adr_test`, `create_req`, `update_req`) is
  reviewed against a documented set of prompt-quality criteria (length,
  redundancy, step-gating, clarity of the tool-call sequence it drives).
- REQ-004: A decision is recorded on the fate of the step-gated `_test`
  prompt variants — keep both narrated and step-gated variants long-term,
  consolidate into one style, or retire one — applied consistently across
  the `adr` and (if adopted) `req` domains.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — `adr_list`/`req_list` (and any future
  `*_list` resource) share a common base summary shape/contract, checked
  by a shared test or an explicit side-by-side comparison.
- [ ] ACC-002: Verifies REQ-002 — a decision (ADR or an entry in this
  file's Decisions Made log, per the ADR-vs-feature-log tie-breaker in ADR
  e369ee2e) is recorded on list-resource pagination, with rationale even
  if the decision is "defer."
- [ ] ACC-003: Verifies REQ-003 — each prompt module has a recorded
  review outcome (kept as-is / changed / retired) against the documented
  criteria.
- [ ] ACC-004: Verifies REQ-004 — an explicit decision on the `_test`
  variants is recorded and, if it implies code changes, those changes are
  made consistently in both domains that have prompts.

### Scope

**Included in this feature:**

- The output shape/contract of `specmgr://adr/list` and `specmgr://req/list`
- Design guidance for future `*_list` resources (`uc`, `ac`, ...)
- Review and optimization of existing `adr/prompts/` and `req/prompts/`
  modules
- The decision on keeping/consolidating/retiring the `_test` prompt
  variants

**Explicitly out of scope:**

- Net-new domains or document types (tracked separately, e.g. `uc`
  currently has no `prompts`/`resources` sub-package yet — adding one is
  its own feature, not this one)
- Other cross-cutting concerns not yet described (logging, error-handling
  conventions, config management, etc.) — these get their own section/task
  list added to this same file when they come up, or are split into a
  dedicated `feat-NNN-slug` folder if they turn out to be large

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr`
  feature-folder structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2
  (domain-first hierarchy)
- Blocks: None identified yet

### Design Notes

- `adr_list` (`adr/resources/adr_list.py`) and `req_list`
  (`req/resources/req_list.py`) already follow the same general shape
  (id/title/status/filename, filename-sorted, skip-on-parse-failure) but
  catch different exception tuples per domain parser
  (`(AdrParseError, ValidationError)` vs. `(AssertionError, ValidationError)`) — worth confirming this divergence is intentional
  (domain-specific parser errors) rather than accidental drift.
- Neither list resource paginates; both differ from this project's own
  `asdste100` MCP tools (e.g. `word_list`, `rules_examples`), which
  already use a `max_results`/`offset` pattern — that pattern is a
  candidate model to reuse here rather than inventing a new one.
- `adr/prompts/create_adr_test.py`/`update_adr_test.py` are explicitly
  documented (AGENTS.md) as experimental, step-gated (`GATE 0`..`GATE N`)
  variants registered under distinct prompt names for side-by-side
  comparison against the narrated originals — this feature is where that
  comparison's outcome should get decided and recorded.

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
  `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 0: Housekeeping

- [x] Task 0.1: Create GitHub issue #7 for this feature and rename
  `feat-0-various-improvements` → `feat-7-various-improvements`, updating
  the frontmatter `id` to match — depends on: none — status: done
  (2026-08-15)
- [x] Task 0.2: Create and immediately close GitHub issue #8
  (`feat-0-coverage-badge`, already-completed feature) and rename the
  folder → `feat-8-coverage-badge`, updating the frontmatter `id` to match
  — depends on: none — status: done (2026-08-15)
- [x] Task 0.3: Create and immediately close GitHub issue #9
  (`feat-0-doc-in-specmgr`) and rename the folder →
  `feat-9-doc-in-specmgr`, updating the frontmatter `id` to match —
  depends on: none — status: done (2026-08-15)
- [x] Task 0.4: Fix all ~20 live cross-references to the old
  `feat-0-doc-in-specmgr` path across `AGENTS.md`, source docstrings
  (`server.py`, `adr/prompts/*.py`, `models/adr/__init__.py`,
  `models/adr/v1/__init__.py`, `uc/models/v1/use_case.py`), tests
  (`tests/adr/prompts/test_*.py`), and other feature docs
  (`feat-4-use-cases/README.md`, `v1/uc-schema.md`, `v1/eval-uc.md`) —
  deliberately left one reference untouched in an archived session
  transcript (`feat-9-doc-in-specmgr/history/session-ses_038f-adr-tool-plan.md`)
  since historical logs are point-in-time records, not live docs — depends
  on: Task 0.3 — status: done (2026-08-15)
- [x] Task 0.5: Regenerate `docs/api/` and `docs/GENERATED.md` via
  `uv run --frozen specmgr docs` (Python 3.13) to pick up the renamed
  path, then verify with `ruff format --check`, `ruff check`, and the full
  `unittest` suite (771 tests, all passing) — depends on: Task 0.4 —
  status: done (2026-08-15)
- [ ] Task 0.6: Review whether repeatedly referencing
  `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` (and its section
  numbers) inline in source docstrings (`server.py`, `adr/prompts/*.py`,
  `models/adr/__init__.py`, `models/adr/v1/__init__.py`,
  `uc/models/v1/use_case.py`) is genuinely useful or just redundant bloat
  that also creates a maintenance liability (as Task 0.4 just showed —
  ~20 references had to be fixed for a single folder rename). Decide a
  tighter convention (e.g. reference the plan once per module/file at
  most, or drop path+section references from docstrings entirely in
  favor of the plan file itself being the single source of truth) and
  apply it — depends on: Task 0.4 — status: not-started
- [ ] Task 0.7: Update ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO
  8601 for all dates and times") to require timezone information on every
  timestamp — either an explicit offset (`±HHMM`) or `Z` for UTC — rather
  than treating it as optional, if this is not already stated; the current
  "Standard Format (Non-Filename Contexts)" section only shows `±HHMM` as
  an example under "With timezone" without mandating it — depends on: none
  — status: not-started
- [ ] Task 0.8: Create a new `general` MCP resource that returns the main
  characteristics of ISO/IEC 25010:2023 (system/software quality model)
  with a description for each — depends on: none — status: not-started
- [x] Task 0.9: Add an id-based `get_req` MCP **tool** (not just the
  existing `specmgr://req/{id}` resource) — reason: in practice, LLMs and
  agents fail to reliably use `specmgr://req/{id}` (a resource, not a
  tool) to retrieve an artifact by id, defeating the point of exposing it
  that way. This directly revisits `feat-6-requirement-artifact` Task
  3.17's design decision ("`specmgr://req/{id}` resource ... supersedes
  the earlier considered `get_req` tool — id-based single-document read is
  a resource only"); may also need the equivalent look at `get_adr` (which
  already exists as a tool, unlike REQ) and any future `uc`/`get_uc` for
  consistency — depends on: none — status: done (2026-08-15)
  - [x] Task 0.9.1: Write a new ADR recording the decision: add a `get_req`
    tool mirroring `get_adr`; remove `specmgr://req/{id}` (`req_get`)
    entirely so REQ is tool-only for id-based reads; explicitly leave
    `specmgr://adr/{id}` (`adr_get`) coexisting with `get_adr` as-is
    (accepted, deliberate cross-domain divergence, not silently ignored);
    note future `uc`/`get_uc` should follow the REQ (tool-only) precedent
    — depends on: none — status: done (2026-08-15)
  - [x] Task 0.9.2: Add `req/tools/get_req.py` — `@mcp.tool(name="get_req")`
    wrapper mirroring `adr/tools/get_adr.py`, using
    `req/tools/_io.py`/`_paths.py`'s `load_by_id(req_base_dir(), id)`,
    returning `ReqDocument` — depends on: Task 0.9.1 — status: done (2026-08-15)
  - [x] Task 0.9.3: Remove `req/resources/req_get.py` and drop its
    import/registration from `req/resources/__init__.py` (module
    docstring, the `from . import ...` line, and `__all__`) — depends on:
    Task 0.9.2 — status: done (2026-08-15)
  - [x] Task 0.9.4: Update `req/__init__.py`'s module docstring — drop
    `specmgr://req/{id}` from the resources list, add `get_req` to the
    tools list — depends on: Task 0.9.3 — status: done (2026-08-15)
  - [x] Task 0.9.5: Update `server.py`'s module docstring — remove the
    `specmgr://req/{id}` resource line, add `get_req` to the "Requirement
    tools" line — depends on: Task 0.9.3 — status: done (2026-08-15)
  - [x] Task 0.9.6: Update `req/prompts/update_req.py`'s `## 1. Read current state first` step to call `get_req(id)` instead of reading the
    now-removed `specmgr://req/{id}` resource (mirror `update_adr.py`'s
    phrasing style) — depends on: Task 0.9.2, Task 0.9.3 — status:
    done (2026-08-15)
  - [x] Task 0.9.7: Add `tests/req/tools/test_get_req.py`, mirroring
    `tests/adr/tools/test_get_adr.py`'s two cases
    (`test_returns_matching_document`, `test_raises_not_found_for_unknown_id`)
    — depends on: Task 0.9.2 — status: done (2026-08-15)
  - [x] Task 0.9.8: Remove `tests/req/resources/test_req_get.py` — depends
    on: Task 0.9.3 — status: done (2026-08-15)
  - [x] Task 0.9.9: Update `tests/req/prompts/test_update_req.py`'s
    assertions (currently asserting on the literal `"specmgr://req/{id}"`
    string) to assert on the new `get_req(id)` wording instead — depends
    on: Task 0.9.6 — status: done (2026-08-15)
  - [x] Task 0.9.10: Regenerate `docs/adr/README.md` (`specmgr adr-toc`)
    and `docs/api/`/`docs/GENERATED.md` (`specmgr docs`), Python 3.13 —
    depends on: Task 0.9.1, Task 0.9.4, Task 0.9.5 — status: done (2026-08-15)
  - [x] Task 0.9.11: Annotate `feat-6-requirement-artifact/README.md`'s
    Task 3.17 line with a short pointer note ("revisited/superseded by
    feat-7 Task 0.9 and ADR `<new-id>` — `get_req` tool added, resource
    removed"), without rewriting its existing history — depends on: Task
    0.9.1 — status: done (2026-08-15)
  - [x] Task 0.9.12: Update this feature's own Decisions Made / Recent
    Updates logs and mark Task 0.9 (and this sub-list) done — depends on:
    Task 0.9.1 through Task 0.9.11 — status: done (2026-08-15)
  - [x] Task 0.9.13: Verify — `ruff format --check`, `ruff check`,
    `vulture src/ whitelist.py --min-confidence 60` (catches the removed
    `req_get` file), and the full `unittest` suite — depends on: Task 0.9.2
    through Task 0.9.9 — status: done (2026-08-15)
- [ ] Task 0.10: Create a new `general` MCP resource that returns the RFC
  2119\. This is an ad interim solution until we have a filter option in
  ASD-STE100 MCP by source. — depends on: none — status: not-started
- [ ] Task 0.11: Make "mdformat" CLI command. This command formats a markdown
  document with or without frontmatter in the same procedure as the SpecMgr
  formats artifacts (example: consecutive numbering in ordered lists).

#### Phase 1: Audit

- [ ] Task 1.1: Inventory current `specmgr://*/list` resources and diff
  their output shape/behavior (`adr_list` vs. `req_list`) — depends on:
  none — status: not-started
- [ ] Task 1.2: Inventory current MCP prompt modules and their
  structure/length/gating style (`create_adr`, `update_adr`,
  `create_adr_test`, `update_adr_test`, `create_req`, `update_req`) —
  depends on: none — status: not-started

#### Phase 2: Decide

- [ ] Task 2.1: Decide the standardized list-resource contract (shared
  base summary model, pagination yes/no and shape if yes) — depends on:
  Task 1.1 — status: in-progress — one piece already decided directly
  (2026-08-15, ahead of the formal audit): the fallback identifier field is
  named `ref`, not `filename`, and holds the extensionless base name, not
  the raw on-disk filename (see Decisions Made). Pagination is still
  undecided.
- [ ] Task 2.2: Decide the fate of the `_test` prompt variants and the
  criteria used for the prompt-quality review — depends on: Task 1.2 —
  status: not-started

#### Phase 3: Implement

- [x] Task 3.1a: Rename `AdrSummary.filename`/`ReqSummary.filename` to
  `ref`, changing its value from `path.name` (e.g. `"<uuid>-a-title.md"`)
  to the extensionless `path.stem` (e.g. `"<uuid>-a-title"`), and update
  the `adr_list`/`req_list` resource descriptions accordingly — done to
  stop steering the calling LLM toward reading the file off disk directly
  instead of using `get_adr`/`get_req`/`specmgr://{adr,req}/{id}` — depends
  on: none — status: done (2026-08-15)
- [ ] Task 3.1b: Apply the remaining piece of the standardized
  list-resource contract (pagination) to `adr_list`/`req_list` (and
  document the full contract for future `*_list` resources) — depends on:
  Task 2.1 — status: not-started
- [ ] Task 3.2: Apply prompt optimizations and the `_test`-variant decision
  — depends on: Task 2.2 — status: not-started

#### Phase 4: Verify

- [ ] Task 4.1: Update/extend tests covering the list resources and
  prompts affected by Phase 3 — depends on: Task 3.1, Task 3.2 — status:
  not-started
- [ ] Task 4.2: Update `AGENTS.md`/`docs/GENERATED.md` (via `specmgr docs`)
  to reflect the final state — depends on: Task 4.1 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-15**: Feature folder created with the first tracked
concern (MCP list-resource format + prompt optimizations) scoped. Phase 0
housekeeping (backfilling GitHub issue numbers for `feat-0-*` folders,
including this one) is complete. The `filename` → `ref` field rename
(Task 3.1a) is implemented ahead of the formal Phase 1/2 audit/decision;
the rest of Phase 1 (audit) and the pagination question are not started.
Task 0.9 (`get_req` tool, all 13 sub-tasks) is now complete: `get_req` was
added, `specmgr://req/{id}` was removed, `specmgr://adr/{id}` was
deliberately left untouched, and the decision is recorded in ADR
`ddfb1109-422d-4507-8dbc-dc5e4bec9614`.

### Recent Updates

#### 2026-08-15

- Completed: Created `feat-0-various-improvements` with initial scope
  (list-resource format standardization + prompt optimizations, including
  the `_test` prompt-variant decision).
- Completed: Opened [GitHub issue #7](https://github.com/dfch/biz.dfch.SpecMgr/issues/7)
  and renamed the folder to `feat-7-various-improvements` accordingly
  (frontmatter `id` updated to match).
- Completed: Phase 0 housekeeping — backfilled GitHub issue numbers for
  the two other `feat-0-*` folders (`feat-0-coverage-badge` → issue #8 →
  `feat-8-coverage-badge`; `feat-0-doc-in-specmgr` → issue #9 →
  `feat-9-doc-in-specmgr`), including fixing ~20 live cross-references to
  the renamed path and regenerating `docs/api/`/`docs/GENERATED.md`. See
  Phase 0 in the Task List for the full breakdown.
- Completed: Renamed `AdrSummary.filename`/`ReqSummary.filename` to `ref`
  and changed its value to the extensionless base name (`path.stem`
  instead of `path.name`) in `adr_list`/`req_list`, with matching resource
  description/docstring updates and new test coverage
  (`tests/adr/resources/test_adr.py`, `tests/req/resources/test_req_list.py`).
  Verified with `ruff format --check`/`ruff check` (clean) and the full
  `unittest` suite (771 tests, all passing), and regenerated `docs/api/`.
- Corrected: The `filename` → `ref` change above was implemented directly
  from a request that only asked for it to be logged as a task — user
  flagged this as jumping ahead without confirmation. Reverted all of it
  (`git checkout --` on the touched source/test files, then re-ran
  `specmgr docs` to bring `docs/api/` back in sync).
- Completed: User then clarified the implementation should in fact be
  kept, not reverted — re-applied the identical `filename` → `ref` change
  (models, resources, tests, docstrings) by hand, re-verified with
  `ruff format --check`/`ruff check` (clean) and the full `unittest` suite
  (771 tests, all passing), and regenerated `docs/api/` again. Net effect
  matches the entry above; recorded here for the process lesson: confirm
  scope (log-only vs. implement) before writing code on an ambiguously
  worded request.
- Completed: Task 0.9 (`get_req` MCP tool) end to end, via sub-tasks
  0.9.1-0.9.13:
  - Wrote ADR `ddfb1109-422d-4507-8dbc-dc5e4bec9614` ("Expose id-based REQ
    document reads as a tool (get_req), not a resource") recording the
    decision and its rationale.
  - Added `req/tools/get_req.py` (`@mcp.tool(name="get_req")`), mirroring
    `adr/tools/get_adr.py`, and registered it in `req/tools/__init__.py`.
  - Removed `req/resources/req_get.py` (the `specmgr://req/{id}` resource)
    and its registration/docstring in `req/resources/__init__.py`; deleted
    the now-orphaned `docs/api/biz.dfch.specmgr.req.resources.req_get.md`.
  - Updated `req/__init__.py` and `server.py`'s module docstrings to match
    the new tool/resource surface.
  - Updated `req/prompts/update_req.py`'s "read current state first" step
    to call `get_req(id)` instead of reading the removed resource.
  - Added `tests/req/tools/test_get_req.py` (mirrors
    `tests/adr/tools/test_get_adr.py`); removed
    `tests/req/resources/test_req_get.py`; updated
    `tests/req/prompts/test_update_req.py`'s assertions accordingly.
  - Regenerated `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and
    `docs/adr/README.md` (`specmgr adr-toc`).
  - Annotated `feat-6-requirement-artifact/README.md` Task 3.17 with a
    pointer to this decision, without rewriting its existing history.
  - Verified: `ruff format --check`/`ruff check` (clean, after also fixing
    unrelated pre-existing trailing-whitespace in
    `req/prompts/create_req.py` that was blocking a clean `ruff check`),
    and the full `unittest` suite (771 tests, all passing). `specmgr://adr/{id}`
    (`adr_get`) was deliberately left coexisting with `get_adr`, unchanged.
- Notes: Found the working tree already carrying unrelated, uncommitted
  changes predating this session (the `filename` → `ref` rename touching
  `adr_list`/`req_list`/`AdrSummary`/`ReqSummary`, plus three new
  `docs/req/*.md` requirement documents and an unrelated edit to
  `req/prompts/create_req.py`) — left as-is, out of scope for Task 0.9.
  `vulture` also flags two pre-existing `unused variable 'ref'` warnings
  from that same rename in `whitelist.py`-adjacent files; confirmed via
  `git stash` that these predate Task 0.9's changes and are not caused by
  `get_req`. Not fixed here — candidate follow-up task if this feature's
  Phase 3.1b/pagination work revisits the same files.
- Next: Phase 1 audit — inventory current list resources and prompt
  modules; Task 3.1b (pagination) still open.
- Notes: This folder is a rolling bucket for cross-cutting concerns; split
  any single concern into its own `feat-NNN-slug` folder if it grows large
  enough to need its own dedicated requirements/acceptance criteria.

### Decisions Made

- **2026-08-15**: Use a shared feature folder (`feat-0-various-improvements`,
  later renamed to `feat-7-various-improvements` once issue #7 was opened)
  as a home for small cross-cutting concerns rather than one folder per
  concern — rationale: per-concern folders would be disproportionately
  small relative to the ADR's per-feature template overhead; this can be
  split later if any tracked concern grows.
- **2026-08-15**: `AdrSummary`/`ReqSummary`'s fallback identifier field is
  named `ref`, not `filename`, and holds the extensionless base name
  (`path.stem`), not the raw on-disk filename (`path.name`) — rationale:
  a field literally called `filename` invites an LLM caller to go read the
  file directly off disk instead of calling `get_adr`/`get_req`/
  `specmgr://{adr,req}/{id}`, which is the whole point of exposing these
  as MCP resources in the first place.
- **2026-08-15**: Recorded as ADR `ddfb1109-422d-4507-8dbc-dc5e4bec9614` —
  add a `get_req` tool and remove `specmgr://req/{id}` entirely (REQ
  becomes tool-only for id-based reads), while deliberately leaving
  `specmgr://adr/{id}` coexisting with `get_adr` untouched. Future document
  domains (`uc`/`get_uc`, `ac`/`get_ac`, ...) should follow the REQ
  (tool-only) precedent rather than the older ADR one, absent a specific
  reason to add a resource counterpart.

### Related PRs / Commits

None yet.
