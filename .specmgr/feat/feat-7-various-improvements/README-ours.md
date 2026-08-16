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

#### Phase 0: Housekeeping — backfill GitHub issue numbers for `feat-0-*` folders

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
  Task 1.1 — status: not-started
- [ ] Task 2.2: Decide the fate of the `_test` prompt variants and the
  criteria used for the prompt-quality review — depends on: Task 1.2 —
  status: not-started

#### Phase 3: Implement

- [ ] Task 3.1: Apply the standardized list-resource contract to
  `adr_list`/`req_list` (and document it for future `*_list` resources) —
  depends on: Task 2.1 — status: not-started
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
including this one) is complete. Phase 1 (audit) not started.

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
- Next: Phase 1 audit — inventory current list resources and prompt
  modules.
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

### Related PRs / Commits

None yet.
