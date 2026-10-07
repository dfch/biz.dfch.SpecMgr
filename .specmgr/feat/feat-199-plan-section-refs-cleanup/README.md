---
classification: null
created: '2026-10-06T10:45:41.464+02:00'
id: feat-199-plan-section-refs-cleanup
status: planning
type: feat
updated: '2026-10-06T10:45:41.464+02:00'
version: 1.0.0
---

# Feature: Clean Up Bare `(plan §N)` Shorthand Citations of adr-tool-plan.md

## Plan

### Overview

Follow-up to feat-198-retire-adr-tool-plan-refs / GitHub issue #198. That
feature scopes only the 14 citations that spell out `adr-tool-plan.md` by
literal path. A broader sweep (done while scoping feat-198) found a much
larger, separate pattern: **~90 bare `(plan §N)` shorthand references across
~25 files** in `src/biz/dfch/specmgr/adr/tools/`, `adr/resources/`, and
`models/adr/v1/` (plus one stray hit in `uc/models/v1/parser.py` to
double-check) — e.g.
`"""``@mcp.tool()`` wrapper: get_adr (plan §8, §9a, §10 item 4)."""`.

These never spell out the filename `adr-tool-plan.md` at all — they rely on
the reader inferring from context that "plan" means that specific file and
its section numbering (§3 frontmatter, §4 body, §5 options, §6 module
layout, §7 cross-cutting decisions, §8 tool surface, §9/§9a id-scheme, §10
next-steps, §11 prompts).

**Confirmed, not assumed, before filing this**: spot-checked via `git
blame`/`git log --follow` across four independent files
(`adr/tools/_paths.py`, `adr/tools/update_section.py`,
`models/adr/v1/body.py`, `adr/resources/adr_get.py`) — all "plan §N" lines
were introduced on 2026-08-03, the exact day `doc/adr-tool-plan.md`
(pre-`.specmgr`-migration path) was being actively authored; one commit
(`9e844dbc`) even touched both `doc/adr-tool-plan.md` and the citing
`_paths.py` line in the same commit. This is a genuinely different usage
from the many `docs(feat-NNN): update plan` commits in this repo's history,
which refer to an individual feature's own `README.md` "## Plan" section (no
`§N` sub-numbering at all) — unrelated and not to be confused with this.

This feature is deliberately left at `planning` status with a shallow task
list: it needs its own dedicated investigation/mapping pass (per-reference
disposition, mirroring feat-198's Design Notes table) before a real task
breakdown can be written, since it touches the most mature, heavily-tested
domain in the repo (ADR tooling).

### Requirements

- REQ-001: No file under `src/` carries a bare `(plan §N)`-style citation referring to `adr-tool-plan.md` after this feature closes.
- REQ-002: Every citation removed per REQ-001 has a recorded disposition (ADR substitution, drop, or other), mirroring feat-198's per-citation Design Notes approach.
- REQ-003: The one stray `uc/models/v1/parser.py` hit is explicitly confirmed (or ruled out) as the same `adr-tool-plan.md` referent before being lumped into this cleanup.
- REQ-004: `adr-tool-plan.md` itself remains untouched (same disposition as feat-198 — frozen historical record).

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — a repo-wide sweep for the `(plan §N)` pattern within the `adr`/`models/adr` packages returns no results.
- [ ] ACC-002: Verifies REQ-002 — disposition table recorded in this file's Design Notes, one row per distinct reference site (or logical group).
- [ ] ACC-003: Verifies REQ-003 — `uc/models/v1/parser.py`'s hit is explicitly addressed (confirmed in/out) with rationale recorded.
- [ ] ACC-004: Verifies REQ-004 — `git diff` shows no changes under `.specmgr/feat/feat-9-doc-in-specmgr/`.

### Scope

#### Included

- All `(plan §N)` shorthand references in `src/biz/dfch/specmgr/adr/tools/`, `adr/resources/`, `models/adr/v1/`, `models/adr/__init__.py`.
- The one stray `uc/models/v1/parser.py` reference (confirm/address per REQ-003).
- A fresh per-reference investigation/mapping pass (not yet done) before any edits — this is the first task once this feature moves out of `planning`.

#### Explicitly Out Of Scope

- The 14 literal-path citations already covered by feat-198-retire-adr-tool-plan-refs (do not duplicate that work here).
- Editing `adr-tool-plan.md` itself or any of its feat-9 siblings.
- Any changes to the 17 other feature folders' stray sibling files (separate, already-deferred concern per feat-198's own Scope section).

### Dependencies

#### Depends On

- feat-198-retire-adr-tool-plan-refs (establishes the per-citation disposition pattern — ADR substitution vs. drop — this feature should reuse).

#### Blocks

- None identified.

### Design Notes

No per-reference disposition table yet — this needs its own investigation
pass (reading each citing docstring's surrounding prose, checking whether it
already self-explains per feat-198's precedent, and checking whether the
cited plan section maps to an existing formal ADR) before any edits are
made. Do not treat this as a blanket find/replace: feat-198 found that some
citations are pure decoration (self-contained prose already) while others
needed an actual ADR substitution — the same per-site judgment applies here,
at roughly 6x the scale.

### Related Decisions

- e369ee2e-3353-4f92-991c-6367d76d832e (ADR): governs `.specmgr/feat/` file layout; same frozen-historical-record disposition as feat-198 applies to `adr-tool-plan.md` itself here too.

### Task List

#### Phase 100: Investigation

- [ ] Task 100.100: Re-run the `plan §` sweep against the current tree (counts may have shifted since this feature was filed) and produce the per-reference disposition table in this file's Design Notes, one row per distinct citation site — depends on: none — status: not-started

- [ ] Task 100.110: Confirm or rule out the `uc/models/v1/parser.py` stray hit (REQ-003) — depends on: none — status: not-started

#### Phase 110: Implementation

- [ ] Task 110.100: Apply the dispositions from Task 100.100's table — depends on: Task 100.100, Task 100.110 — status: not-started

- [ ] Task 110.110: Update any test assertions affected by the docstring changes — depends on: Task 110.100 — status: not-started

- [ ] Task 110.120: Regenerate `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`; verify `ruff format --check`/`ruff check`/`vulture`/full test suite — depends on: Task 110.100, Task 110.110 — status: not-started

## Progress

### Current Status

**As of 2026-10-06**: Filed as a follow-up during feat-198's scoping discussion. Not yet investigated in depth — status `planning` reflects that an investigation pass (Phase 100) is needed before a real task breakdown exists.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-06 00:00:00.000Z - Created

Split out from feat-198-retire-adr-tool-plan-refs's scoping discussion (GitHub issue #199) after discovering ~90 bare `(plan §N)` shorthand citations across ~25 files, confirmed via `git blame`/`git log --follow` to refer to `adr-tool-plan.md`. Deliberately kept separate from feat-198 to avoid expanding an already-scoped, already-filed issue; deliberately left at a shallow planning depth pending its own investigation pass.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-06 00:00:00.000Z - Kept separate from feat-198

Decided not to fold this into feat-198-retire-adr-tool-plan-refs despite the overlapping root cause (both are about fragile, redundant citations of `adr-tool-plan.md`). Rationale: feat-198 was already scoped and its GitHub issue (#198) already filed against the narrower 14-citation set before this larger pattern was found; the ~90-reference, 25+-file scale across the most mature domain in the repo deserves its own dedicated investigation and review rather than a late, silent scope expansion.

### Related PRs / Commits

- [Issue #199](https://github.com/dfch/biz.dfch.SpecMgr/issues/199): tracking issue for this feature.
- [Issue #198](https://github.com/dfch/biz.dfch.SpecMgr/issues/198): the narrower, already-scoped sibling this was split out of.

### More Information

Originating discussion: feat-198-retire-adr-tool-plan-refs's scoping conversation (2026-10-06).
