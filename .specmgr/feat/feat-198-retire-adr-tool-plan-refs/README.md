---
classification: null
created: '2026-10-06T10:37:25.837+02:00'
id: feat-198-retire-adr-tool-plan-refs
status: planning
type: feat
updated: '2026-10-06T10:45:58.862+02:00'
version: 1.0.0
---

# Feature: Retire Live Citations of adr-tool-plan.md

## Plan

### Overview

`.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` is a pre-formal-ADR design/planning
document for the ADR tooling feature (§1 Goal through §11 Prompt surface). It is currently cited
inline, with hand-numbered `§N` section references, from 12 `src/` docstrings and 2 places in
`AGENTS.md` — 14 live citations total. This is a fragile, hand-maintained cross-reference: a
single folder rename already broke ~20 such references once (feat-7-various-improvements Task
100.120), and the plan file itself contains a dangling self-reference (4x) to a sibling file
(`refactor-domain.md`) that no longer exists on disk.

Investigation (see feat-7-various-improvements Task 100.140 discussion) found that nearly every
section of `adr-tool-plan.md` already has its content captured in a dedicated, formal, stable,
tool-addressable ADR (cited inline in the plan itself). The remaining citations (§7, §6 in
`models/adr/v1/__init__.py`, §3-§6 in `models/adr/__init__.py`) turn out to already restate their
content in the citing docstring's own prose — the file citation is pure, non-load-bearing
decoration there.

Originally flagged as feat-7-various-improvements Task 100.140 ("Review whether repeatedly
referencing `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` ... is genuinely useful or
just redundant bloat"); split out into its own feature per that folder's established convention
(e.g. Task 100.230 → feat-13-list-paging).

This feature does **not** audit or change the other 17 feature folders that also carry extra
sibling files (session transcripts, `rsk_tara.md`, `qa_reference.md`, ISO standard copies,
templates, etc.) — none of those are cited from `src/`/`AGENTS.md`, so they carry no equivalent
maintenance liability today. That is explicitly out of scope (see Scope below).

### Requirements

- REQ-001: No file under `src/` or `AGENTS.md` cites `adr-tool-plan.md` (by path or by path+§N) after this feature closes.
- REQ-002: Every citation removed per REQ-001 either (a) is replaced by a citation of the formal ADR that already governs that design decision, or (b) is dropped outright where the citing docstring/comment already fully explains itself without the external reference.
- REQ-003: `adr-tool-plan.md` and its feat-9 siblings (`create-adr.md`, `docs-generator-cleanup-plan.md`) are left byte-for-byte untouched — including the dangling `refactor-domain.md` self-reference — as a frozen historical record.
- REQ-004: `AGENTS.md`'s "Development Artifacts (`.specmgr/`)" section gains one new clause codifying the going-forward rule: a feature folder may contain other local files beyond `README.md`/optional `history.md`, but nothing in `src/`/`AGENTS.md` may cite them — anything needing a stable, live citation from code must be a proper specmgr artifact (normally its own ADR).
- REQ-005: Every test asserting on the literal `"adr-tool-plan.md"` string (or an old docstring wording this feature changes) is updated to match.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — `grep -rn "adr-tool-plan.md" src/ AGENTS.md` returns no results.
- [ ] ACC-002: Verifies REQ-002 — each of the 14 original citation sites has a recorded disposition (ADR substitution or drop) in this file's Decisions Made log.
- [ ] ACC-003: Verifies REQ-003 — `git diff` shows zero changes under `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md`, `create-adr.md`, `docs-generator-cleanup-plan.md`.
- [ ] ACC-004: Verifies REQ-004 — `AGENTS.md`'s Development Artifacts section contains the new clause.
- [ ] ACC-005: Verifies REQ-005 — full `pytest` suite passes, including `tests/adr/prompts/test_*.py`.

### Scope

#### Included

- The 12 `src/` docstring citations: `server.py` (x2), `uc/models/v1/use_case.py`, `models/adr/__init__.py`, `models/adr/v1/__init__.py`, `adr/prompts/__init__.py`, `adr/prompts/create_adr.py`, `adr/prompts/update_adr.py`, `adr/prompts/create_adr_test.py` (x2), `adr/prompts/update_adr_test.py` (x2).
- The 2 `AGENTS.md` citations (the `adr/` domain bullet, and the standalone "§10 Next steps" paragraph).
- The one new `AGENTS.md` convention clause (REQ-004).
- Updating any test assertions on the changed docstring text.
- Regenerating `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`.

#### Explicitly Out Of Scope

- Editing, archiving, or deleting `adr-tool-plan.md` or any of its feat-9 siblings (frozen per REQ-003).
- Auditing or changing the 17 other feature folders' stray sibling files (session transcripts, `rsk_tara.md`, `qa_reference.md`, ISO standard copies, templates, etc.) — none are cited from live code; no evidenced problem to fix.
- The ~90 bare `(plan §N)` shorthand citations (no literal filename) found across `adr/tools/`, `adr/resources/`, `models/adr/v1/`, and one stray hit in `uc/models/v1/parser.py` — confirmed via `git blame`/`git log --follow` to also refer to `adr-tool-plan.md`, but deliberately split out into feat-199-plan-section-refs-cleanup (GitHub issue #199) rather than folded into this already-scoped, already-filed feature. See that feature for the full finding and rationale.
- Writing a new ADR about feature-folder file layout — the going-forward rule is codified as an `AGENTS.md` convention clause instead (REQ-004), per the user's explicit direction: this is an authoring convention (like docstring style, already governed by `.specmgr/conventions.md`-adjacent material in `AGENTS.md`), not an architectural decision with competing tradeoffs to record.
- Fixing the dangling `refactor-domain.md` self-reference inside `adr-tool-plan.md` (out of scope per REQ-003's "untouched" rule).

### Dependencies

#### Depends On

- feat-7-various-improvements Task 100.140 (the task this feature is split out of).
- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` structure) — the existing ADR this feature's `AGENTS.md` clause extends without amending.

#### Blocks

- None identified.

### Design Notes

Per-citation disposition (see the originating discussion in feat-7-various-improvements for the
full investigation):

| Location(s) | Fix |
|---|---|
| `server.py` (specmgr://adr/{id} resource docstring) | Cite `ADR 8cf940c5-3100-485c-a12d-14b59b631712` / `ADR 7531106b-074b-4bd8-a83a-e433d01676e2` (id/addressing scheme) instead, or drop if self-evident |
| `server.py` (prompt-surface docstring) | Cite `ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f` instead |
| `uc/models/v1/use_case.py` (Options-gap comment) | Drop the file citation clause; sentence is already self-contained |
| `models/adr/__init__.py` (module docstring, 5+ `(plan §N)` annotations) | Drop all `(plan §N)` parentheticals; prose is already self-contained |
| `models/adr/v1/__init__.py` (module docstring, §6 versioning) | Drop the "See adr-tool-plan.md §6..." lead-in; rest of the paragraph is already self-contained |
| `adr/prompts/__init__.py`, `create_adr.py`, `update_adr.py`, `create_adr_test.py` (x2), `update_adr_test.py` (x2) — 7 spots across 5 files | Consolidate to **one** citation of `ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f` in `adr/prompts/__init__.py`'s package docstring; drop the other 6 |
| `AGENTS.md` (`adr/` domain bullet) | Cite `ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f` instead |
| `AGENTS.md` (standalone "§10 Next steps" paragraph) | Remove entirely — redundant with the existing "Still genuinely missing" bullet, which already cites `ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73` for the same fact (CI/pre-commit `validate_adr` wiring still missing) |

`ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f` ("Prompt surface: narrated guidance plus step-gated
test variants") and `ADR 8cf940c5-3100-485c-a12d-14b59b631712` ("id/filename/addressing scheme")
were both re-read in full during planning and confirmed to cover the cited content accurately.

### Related Decisions

- e369ee2e-3353-4f92-991c-6367d76d832e (ADR): governs `.specmgr/feat/` file layout (`README.md` + optional `history.md`); this feature's new `AGENTS.md` clause extends its silence on other siblings without amending the ADR itself.
- ddd038f0-ae16-4f4b-beef-df06f7ed226f (ADR): prompt surface design — replaces most of the `adr/prompts/*` citations.
- 8cf940c5-3100-485c-a12d-14b59b631712 (ADR): id/filename/addressing scheme — replaces the `server.py` resource citation.

### Task List

#### Phase 100: Source and AGENTS.md Citation Cleanup

- [ ] Task 100.100: Fix `server.py`'s two citations per the Design Notes table (resource docstring, prompt-surface docstring) — depends on: none — status: not-started

- [ ] Task 100.110: Fix `uc/models/v1/use_case.py`'s citation (drop the file reference clause) — depends on: none — status: not-started

- [ ] Task 100.120: Fix `models/adr/__init__.py`'s module docstring (drop all `(plan §N)` annotations) — depends on: none — status: not-started

- [ ] Task 100.130: Fix `models/adr/v1/__init__.py`'s module docstring (drop the §6 lead-in) — depends on: none — status: not-started

- [ ] Task 100.140: Consolidate the 7 `adr/prompts/*` citations into one, in `adr/prompts/__init__.py`'s package docstring, citing `ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f`; remove the other 6 (`create_adr.py`, `update_adr.py`, `create_adr_test.py` x2, `update_adr_test.py` x2) — depends on: none — status: not-started

- [ ] Task 100.150: Fix `AGENTS.md`'s two citations (the `adr/` domain bullet, and remove the standalone "§10 Next steps" paragraph) — depends on: none — status: not-started

- [ ] Task 100.160: Add the new `AGENTS.md` convention clause (REQ-004) to the "Development Artifacts (`.specmgr/`)" section — depends on: none — status: not-started

#### Phase 110: Verification

- [ ] Task 110.100: Update `tests/adr/prompts/test_*.py` assertions that check for the literal `"adr-tool-plan.md"` string (or old docstring wording changed by Phase 100) — depends on: Task 100.140 — status: not-started

- [ ] Task 110.110: Confirm `grep -rn "adr-tool-plan.md" src/ AGENTS.md` returns no results (ACC-001) — depends on: Task 100.100 through Task 100.160 — status: not-started

- [ ] Task 110.120: Regenerate `docs/api/`, `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 — depends on: Task 100.100 through Task 100.160 — status: not-started

- [ ] Task 110.130: Verify `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `pytest` suite — depends on: Task 110.100, Task 110.120 — status: not-started

- [ ] Task 110.140: Mark feat-7-various-improvements Task 100.140 as "split out into feat-198-retire-adr-tool-plan-refs" per that folder's established convention; record this feature's Decisions Made / Recent Updates logs — depends on: Task 110.100 through Task 110.130 — status: not-started

## Progress

### Current Status

**As of 2026-10-06**: Feature created, split out of feat-7-various-improvements Task 100.140 after a scoping discussion. Not yet implemented.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-06 00:00:00.000Z - Created

Split out of feat-7-various-improvements Task 100.140 (GitHub issue #198), after investigating the actual scope: only `adr-tool-plan.md` is cited live from `src/`/`AGENTS.md` (14 sites); the other 17 feature folders' extra sibling files carry no equivalent liability and are explicitly out of scope.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-06 00:00:00.000Z - Split the (plan §N) shorthand pattern into feat-199

While implementing this feature, a broader sweep (`grep -rn "plan §"`) found ~90 additional bare shorthand citations (no literal filename) across ~25 files in `adr/tools/`, `adr/resources/`, `models/adr/v1/`. Confirmed via `git blame`/`git log --follow` (all introduced 2026-08-03, the exact day `doc/adr-tool-plan.md` was being authored; one commit touched both files together) that these do refer to the same document. Decided to keep feat-198 strictly to its original 14-citation scope and split the larger pattern into feat-199-plan-section-refs-cleanup (GitHub issue #199), since issue #198 was already filed against the narrower set and the larger cleanup (most mature domain in the repo, 6x the scale) deserves its own dedicated investigation.

#### 2026-10-06 00:00:00.000Z - Convention in AGENTS.md, not a new ADR

Decided to codify the going-forward "no live citations of feature-folder sibling files" rule as a new clause in `AGENTS.md`'s existing "Development Artifacts (`.specmgr/`)" section, rather than writing a new ADR. Rationale: this is an authoring/process convention (no competing tradeoffs being weighed, just "stop doing X going forward"), and `AGENTS.md` already owns and summarizes this exact topic (it already restates ADR e369ee2e's `README.md`/`history.md` file-layout decision in the same section).

#### 2026-10-06 00:00:00.000Z - adr-tool-plan.md itself left untouched

Decided to leave `adr-tool-plan.md` and its feat-9 siblings (`create-adr.md`, `docs-generator-cleanup-plan.md`) completely untouched, including the dangling `refactor-domain.md` self-reference, once nothing in `src/`/`AGENTS.md` cites them anymore. ADR e369ee2e already tolerates these as one-time `doc/`-migration leftovers; once de-referenced they are harmless frozen historical records.

#### 2026-10-06 00:00:00.000Z - Scope limited to adr-tool-plan.md only

Decided not to audit the other 17 feature folders' stray sibling files in this pass — investigation confirmed none of them are cited from `src/`/`AGENTS.md`, so they carry no evidenced maintenance liability today, unlike `adr-tool-plan.md`'s 14 live citations.

### Related PRs / Commits

- [Issue #198](https://github.com/dfch/biz.dfch.SpecMgr/issues/198): tracking issue for this feature.

### More Information

Originating discussion: feat-7-various-improvements Task 100.140.
