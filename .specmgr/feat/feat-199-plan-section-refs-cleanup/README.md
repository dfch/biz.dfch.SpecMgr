---
classification: null
created: '2026-10-06T10:45:41.464+02:00'
id: feat-199-plan-section-refs-cleanup
status: planning
type: feat
updated: '2026-10-17T04:25:57.955+02:00'
version: 1.0.0
---

# Feature: Clean Up Bare `(plan §N)` Shorthand Citations of adr-tool-plan.md

## Plan

### Overview

Follow-up to feat-198-retire-adr-tool-plan-refs / GitHub issue #198. That
feature scopes only the 14 citations that spell out `adr-tool-plan.md` by
literal path. A broader sweep (done while scoping feat-198) found a much
larger, separate pattern: **~120 bare `(plan §N)`-style shorthand references
across ~25 files** in `src/biz/dfch/specmgr/adr/tools/`, `adr/resources/`,
and `models/adr/v1/` (plus one stray hit in `uc/models/v1/parser.py` to
double-check and one in `server.py`'s module docstring; exact counts
re-measured by Task 100.100 against the current tree) — e.g.
`"""``@mcp.tool()`` wrapper: get_adr (plan §8, §9a, §10 item 4)."""`.

These never spell out the filename `adr-tool-plan.md` at all — they rely on
the reader inferring from context that "plan" means that specific file and
its section numbering (§2 heading layout, §3 frontmatter, §4 body,
§5 options, §6 module layout, §7 cross-cutting decisions, §8 tool surface,
§9/§9a id-scheme, §10 next-steps, §11 prompts).

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

- [ ] ACC-001: Verifies REQ-001 — a sweep for the bare `plan §` pattern across all of `src/` returns no results (the same pattern and scope Task 100.100's investigation uses, so the acceptance check and the investigation cannot diverge).
- [ ] ACC-002: Verifies REQ-002 — disposition table recorded in this file's Design Notes, one row per distinct reference site (or logical group).
- [ ] ACC-003: Verifies REQ-003 — `uc/models/v1/parser.py`'s hit is explicitly addressed (confirmed in/out) with rationale recorded.
- [ ] ACC-004: Verifies REQ-004 — `git diff` shows no changes under `.specmgr/feat/feat-9-doc-in-specmgr/`.

### Scope

#### Included

- All bare `plan §` shorthand references in `src/biz/dfch/specmgr/adr/tools/`, `adr/resources/`, and `models/adr/` — `__init__.py` included (0 hits at filing, its 7 removed by feat-198, but the package stays whole so the sweep scope matches REQ-001) — plus `server.py` (one module-docstring hit).
- The one stray `uc/models/v1/parser.py` reference (confirm/address per REQ-003).
- A fresh per-reference investigation/mapping pass (not yet done) before any edits — this is the first task once this feature moves out of `planning`.

#### Explicitly Out Of Scope

- The 14 literal-path citations already covered by feat-198-retire-adr-tool-plan-refs (do not duplicate that work here).
- Editing `adr-tool-plan.md` itself or any of its feat-9 siblings.
- Any changes to the 17 other feature folders' stray sibling files (separate, already-deferred concern per feat-198's own Scope section).
- The ~19 same-pattern hits in `tests/` (module docstrings/comments in `tests/adr/tools/` and `tests/models/adr/v1/`; nothing asserts on the pattern, so no `tests/` change is required by the `src/` edits) — out of scope per REQ-001's `src/`-only wording; Task 110.130 records the residue and re-checks AGENTS.md's no-live-citations clause against it (feat-198's post-review follow-up I3).
- Non-`src/` artifacts carrying the pattern: `docs/MCP.md`, `docs/GENERATED.md`, and `docs/api/*.md` are auto-generated and clear via Task 110.120's regeneration (never hand-edited); `CHANGELOG.md` (2 hits) and `docs/adr/7a626b12-….md` (1 hit) are frozen historical records, untouched (same disposition as REQ-004).

### Dependencies

#### Depends On

- FEAT feat-198-retire-adr-tool-plan-refs (establishes the per-citation disposition pattern — ADR substitution vs. drop — this feature should reuse).

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

- ADR e369ee2e-3353-4f92-991c-6367d76d832e: governs `.specmgr/feat/` file layout; same frozen-historical-record disposition as feat-198 applies to `adr-tool-plan.md` itself here too.

### Task List

#### Phase 100: Investigation

- [ ] Task 100.100: Re-run the `plan §` sweep against the current tree (counts may have shifted since this feature was filed) and produce the per-reference disposition table in this file's Design Notes, one row per distinct citation site — depends on: none — status: not-started

- [ ] Task 100.110: Confirm or rule out the `uc/models/v1/parser.py` stray hit (REQ-003) — depends on: none — status: not-started

#### Phase 110: Implementation

- [ ] Task 110.100: Apply the dispositions from Task 100.100's table — depends on: Task 100.100, Task 100.110 — status: not-started

- [ ] Task 110.110: Update any test assertions affected by the docstring changes — depends on: Task 110.100 — status: not-started

- [ ] Task 110.120: Regenerate `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`; verify `ruff format --check`/`ruff check`/`vulture`/full test suite — depends on: Task 110.100, Task 110.110 — status: not-started

- [ ] Task 110.130: Final verification — re-run the `plan §` sweep across `src/` (must return no results, ACC-001), confirm `git diff` shows no changes under `.specmgr/feat/feat-9-doc-in-specmgr/` (ACC-004), re-run the sweep over `tests/` and record the residue, then re-check AGENTS.md's no-live-citations clause against that post-cleanup residue state (feat-198's post-review follow-up I3) — depends on: Task 110.120 — status: not-started

## Progress

### Current Status

**As of 2026-10-17**: Filed as a follow-up during feat-198's scoping discussion. Not yet investigated in depth — status `planning` reflects that an investigation pass (Phase 100) is needed before a real task breakdown exists. The sole dependency (feat-198) has been `done` since 2026-10-07, so this feature is fully unblocked and can move `planning` → `progress` the moment Phase 100 starts.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-17 02:25:57.000Z - Refinement pass

Applied the feat-refiner findings (G1–G4, D1–D4, I1–I4; positives P1–P6 left as-is): the Overview/Scope/ACC-001 site enumeration now includes the `server.py` module-docstring hit and the at-filing counts are corrected (~120 hits / ~25 files in the three named packages — the file count was right, the occurrence count ~30 low); ACC-001's sweep is redefined as the bare `plan §` pattern across all of `src/`, aligned with Task 100.100 and REQ-001; the section legend gains §2; `Included` annotates `models/adr/__init__.py`'s 0-hit state; Out Of Scope records the `tests/` residue and the non-`src/` artifact dispositions (auto-generated docs vs. frozen `CHANGELOG.md`/ADR); Depends On and Related Decisions are in machine-resolvable reference-tag form; new Task 110.130 verifies ACC-001/ACC-004 and closes feat-198's post-review follow-up I3; Current Status notes feat-198 is `done` (2026-10-07) and this feature is unblocked.

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
