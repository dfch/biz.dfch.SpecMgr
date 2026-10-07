---
classification: null
created: '2026-10-06T10:37:25.837+02:00'
id: feat-198-retire-adr-tool-plan-refs
status: review
type: feat
updated: '2026-10-07T14:13:49.519+02:00'
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

- [x] ACC-001: Verifies REQ-001 — `grep -rn "adr-tool-plan.md" src/ AGENTS.md` returns no results.
- [x] ACC-002: Verifies REQ-002 — each of the 14 original citation sites has a recorded disposition (ADR substitution or drop) in this file's Decisions Made log.
- [x] ACC-003: Verifies REQ-003 — `git diff` shows zero changes under `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md`, `create-adr.md`, `docs-generator-cleanup-plan.md`.
- [x] ACC-004: Verifies REQ-004 — `AGENTS.md`'s Development Artifacts section contains the new clause.
- [x] ACC-005: Verifies REQ-005 — full `pytest` suite passes, including `tests/adr/prompts/test_*.py`.

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
| `models/adr/__init__.py` (module docstring: line-20 lead-in sentence citing `adr-tool-plan.md` by name, plus 7x `(plan §N)` parentheticals) | Drop the line-20 lead-in sentence ("See ``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md`` §3-§6 for the design this package implements:") and all seven `(plan §N)` parentheticals; prose is already self-contained |
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
- 7531106b-074b-4bd8-a83a-e433d01676e2 (ADR): alternative/supplementary citation for the `server.py` `specmgr://adr/{id}` resource docstring (see Design Notes).
- 9c687bb1-8ee7-41c8-84ec-07606356bc73 (ADR): "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI" — already covers the same fact as `AGENTS.md`'s standalone "§10 Next steps" paragraph, which this feature removes as redundant.

### Task List

#### Phase 100: Source and AGENTS.md Citation Cleanup

- [x] Task 100.100: Fix `server.py`'s two citations per the Design Notes table (resource docstring, prompt-surface docstring) — depends on: none — status: done

- [x] Task 100.110: Fix `uc/models/v1/use_case.py`'s citation (drop the file reference clause) — depends on: none — status: done

- [x] Task 100.120: Fix `models/adr/__init__.py`'s module docstring — drop both the line-20 lead-in sentence that cites `adr-tool-plan.md` by name ("See ``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md`` §3-§6 for the design this package implements:") *and* all seven `(plan §N)` parentheticals (lines 22-38); dropping only the parentheticals leaves a literal `adr-tool-plan.md` citation and fails ACC-001 — depends on: none — status: done

- [x] Task 100.130: Fix `models/adr/v1/__init__.py`'s module docstring (drop the §6 lead-in) — depends on: none — status: done

- [x] Task 100.140: Consolidate the 7 `adr/prompts/*` citations into one, in `adr/prompts/__init__.py`'s package docstring, citing `ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f`; remove the other 6 (`create_adr.py`, `update_adr.py`, `create_adr_test.py` x2, `update_adr_test.py` x2) — depends on: none — status: done

- [x] Task 100.150: Fix `AGENTS.md`'s two citations (the `adr/` domain bullet, and remove the standalone "§10 Next steps" paragraph) — depends on: none — status: done

- [x] Task 100.160: Add the new `AGENTS.md` convention clause (REQ-004) to the "Development Artifacts (`.specmgr/`)" section — insert as a new bullet directly after the existing "No CI/pre-commit enforcement exists ..." bullet, worded along the lines of: "A feature folder may contain other local files beyond `README.md`/optional `history.md` (session transcripts, reference copies, templates, etc.), but nothing in `src/`/`AGENTS.md` may cite them by path — anything needing a stable, live citation from code must be a proper specmgr artifact (normally its own ADR)." — depends on: none — status: done

#### Phase 110: Verification

- [x] Task 110.100: Update `tests/adr/prompts/test_*.py` assertions that check for the literal `"adr-tool-plan.md"` string (or old docstring wording changed by Phase 100) — depends on: Task 100.140 — status: done

- [x] Task 110.110: Confirm `grep -rn "adr-tool-plan.md" src/ AGENTS.md` returns no results (ACC-001) — depends on: Task 100.100 through Task 100.160 — status: done

- [x] Task 110.112: Confirm `git diff` shows zero changes under `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md`, `create-adr.md`, `docs-generator-cleanup-plan.md` (ACC-003) — depends on: Task 100.100 through Task 100.160 — status: done

- [x] Task 110.114: Confirm `AGENTS.md`'s "Development Artifacts (`.specmgr/`)" section contains the new convention clause added by Task 100.160, e.g. via `grep -n "may not cite\|may cite them" AGENTS.md` or manual inspection (ACC-004) — depends on: Task 100.160 — status: done

- [x] Task 110.120: Regenerate `docs/api/`, `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 — depends on: Task 100.100 through Task 100.160 — status: done

- [x] Task 110.130: Verify `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `pytest` suite — depends on: Task 110.100, Task 110.120 — status: done

- [x] Task 110.140: Mark feat-7-various-improvements Task 100.140 as "split out into feat-198-retire-adr-tool-plan-refs" per that folder's established convention; copy the Design Notes per-citation disposition table (or an equivalent per-citation summary) into a new Decisions Made entry in this file to literally satisfy ACC-002 ("each of the 14 original citation sites has a recorded disposition ... in this file's Decisions Made log"), then record the remaining Recent Updates log entries — depends on: Task 110.100 through Task 110.130 — status: done

## Progress

### Current Status

**As of 2026-10-07**: all phases complete — pending review. Phase 100 (source + AGENTS.md citation cleanup, Tasks 100.100-100.160) removed all 14 live citations; Phase 110 (verification, Tasks 110.100-110.140) confirmed every acceptance criterion (ACC-001..ACC-005), removed the 4 remaining plan citations from the `tests/adr/prompts/test_*.py` module docstrings, re-ran the full quality gate green, and recorded the final per-citation dispositions in Decisions Made (ACC-002).

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07 14:10:19.428+02:00 - Status set to review; all acceptance criteria verified and ticked

Implementation complete (Phase 100: `83d102e`, Phase 110: `0815742`). All five
acceptance criteria verified with concrete evidence: ACC-001 (`grep -rn
"adr-tool-plan.md" src/ AGENTS.md` → no results — in fact no text file under
`src/`/`AGENTS.md`/`tests/` contains `adr-tool-plan` at all after the
user-decision extension of Task 110.100), ACC-002 (final per-citation
disposition table recorded in Decisions Made below), ACC-003 (`git diff
3c5818d --` the three frozen feat-9 files → empty), ACC-004 (new REQ-004
clause present in `AGENTS.md`'s Development Artifacts section), ACC-005 (full
pytest suite: 4088 passed, including `tests/adr/prompts/test_*.py`). feat-7
Task 100.140 marked split out per that folder's convention. Status moves to
`review`; a PR against `dev` follows. Note: branch commit `458c881` (test
harness robustness fix) carries a patch byte-identical to `dev`'s `f27525a`;
a test merge of `dev` into the branch confirmed a conflict-free merge.

#### 2026-10-07 13:20:44.307+02:00 - Phase 110 complete (verification)

Implemented all of Phase 110 (Tasks 110.100-110.140). Task 110.100: per the
orchestrator/user decision (Q2, 2026-10-07), first verified that no
assertion in the 4 `tests/adr/prompts/test_*.py` files checks the literal
`adr-tool-plan.md` string or any Phase-100-changed wording (the prompts'
returned body text comes from the untouched packaged data files
`src/biz/dfch/specmgr/adr/data/*.md`; `pytest tests/adr/prompts/ -q` → 44
passed), then removed the parenthetical plan citation from the 4 test
module docstrings — nothing else in those files changed, and after the
edit no text file under `src/`/`AGENTS.md`/`tests/` contains
`adr-tool-plan` at all (the only remaining grep hits are gitignored
`__pycache__/*.pyc` bytecode, which embeds the worktree's own path
`feat-198-retire-adr-tool-plan-refs`). Task 110.110 (ACC-001): `grep -rn
"adr-tool-plan.md" src/ AGENTS.md` → no results. Task 110.112 (ACC-003):
`git diff 3c5818d --` the three frozen feat-9 files (`adr-tool-plan.md`,
`create-adr.md`, `docs-generator-cleanup-plan.md`) → empty. Task 110.114
(ACC-004): `AGENTS.md`'s Development Artifacts section carries the new
REQ-004 clause ("No live citations of feature-folder sibling files").
Task 110.120: re-ran `specmgr docs` and `specmgr mcp-docs` (Python 3.13) —
both byte-identical no-ops (`git diff --exit-code -- docs/` clean). Task
110.130 (ACC-005): `ruff format --check` clean (1913 files), `ruff check`
clean, vulture clean, full `pytest -n auto --cov=src` → 4088 passed
(including the 4 edited test files), coverage badge unchanged (99%,
`docs/coverage.svg` no diff). Task 110.140: marked
feat-7-various-improvements Task 100.140 as split out per that folder's
established convention, and recorded the final per-citation disposition
for all 14 original sites in a new Decisions Made entry (ACC-002).

#### 2026-10-07 11:30:41.528+02:00 - Phase 100 complete (source + AGENTS.md citation cleanup)

Implemented all of Phase 100 (Tasks 100.100-100.160): removed all 14 live
citations of `adr-tool-plan.md` per the Design Notes disposition table —
`server.py` x2 (resource docstring now cites ADR 7531106b, prompt-surface
docstring cites ADR ddd038f0), `uc/models/v1/use_case.py` (dropped the §7
clause), `models/adr/__init__.py` (dropped the §3-§6 lead-in sentence and
all seven `(plan §N)` parentheticals), `models/adr/v1/__init__.py` (dropped
the §6 lead-in), the 7 `adr/prompts/*` citations consolidated into one
ADR ddd038f0 citation in `adr/prompts/__init__.py`, and `AGENTS.md` x2
(`adr/` bullet now cites ADR ddd038f0; the §10 "Next steps" paragraph
reduced to its second sentence verbatim per the orchestrator override) plus
the new REQ-004 convention bullet. Quality gate green: ruff format/check,
vulture, full pytest (4088 passed), coverage badge unchanged (99%),
`specmgr docs`/`specmgr mcp-docs` regenerated and staged (MCP.md unchanged),
`pre-commit run --all-files` all passed. `grep -rn "adr-tool-plan.md" src/
AGENTS.md` returns nothing (ACC-001).

#### 2026-10-06 00:00:00.000Z - Created

Split out of feat-7-various-improvements Task 100.140 (GitHub issue #198), after investigating the actual scope: only `adr-tool-plan.md` is cited live from `src/`/`AGENTS.md` (14 sites); the other 17 feature folders' extra sibling files carry no equivalent liability and are explicitly out of scope.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07 13:20:44.307+02:00 - Final per-citation disposition of all 14 sites (ACC-002)

Final per-citation disposition for all 14 original sites (satisfies
ACC-002): the Design Notes table's content with the two Phase 100 outcomes
folded in — (a) the `server.py` resource line cites ADR
7531106b-074b-4bd8-a83a-e433d01676e2 (not 8cf940c5, not dropped; rationale
in the Phase 100 entry below), and (b) `AGENTS.md`'s standalone §10 "Next
steps" paragraph was reduced to its second sentence verbatim
(orchestrator/user override 2026-10-07). Every one of the 14 sites has an
explicit "ADR substitution" or "drop" disposition:

| # | Site | Final disposition (Phase 100, 2026-10-07) |
|---|------|-------------------------------------------|
| 1 | `server.py` — `specmgr://adr/{id}` resource docstring | ADR substitution: cites ADR 7531106b-074b-4bd8-a83a-e433d01676e2 (not 8cf940c5, not dropped) |
| 2 | `server.py` — prompt-surface docstring | ADR substitution: cites ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f |
| 3 | `uc/models/v1/use_case.py` — Options-gap comment | Drop: sentence already self-contained |
| 4 | `models/adr/__init__.py` — module docstring (lead-in sentence + 7 `(plan §N)` parentheticals) | Drop: prose already self-contained (Task 100.120) |
| 5 | `models/adr/v1/__init__.py` — module docstring (§6 versioning lead-in) | Drop: rest of the paragraph already self-contained |
| 6 | `adr/prompts/__init__.py` — package docstring | ADR substitution: the single consolidated citation of ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f |
| 7 | `adr/prompts/create_adr.py` | Drop (consolidated into site 6) |
| 8 | `adr/prompts/update_adr.py` | Drop (consolidated into site 6) |
| 9 | `adr/prompts/create_adr_test.py` — 1st citation | Drop (consolidated into site 6) |
| 10 | `adr/prompts/create_adr_test.py` — 2nd citation | Drop (consolidated into site 6) |
| 11 | `adr/prompts/update_adr_test.py` — 1st citation | Drop (consolidated into site 6) |
| 12 | `adr/prompts/update_adr_test.py` — 2nd citation | Drop (consolidated into site 6) |
| 13 | `AGENTS.md` — `adr/` domain bullet | ADR substitution: cites ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f |
| 14 | `AGENTS.md` — standalone "§10 Next steps" paragraph | Drop sentence 1; keep sentence 2 verbatim (orchestrator/user override 2026-10-07) |

#### 2026-10-07 11:30:41.528+02:00 - Phase 100 implementation decisions

(a) Task 100.100, `server.py` `specmgr://adr/{id}` resource docstring: cited
ADR 7531106b-074b-4bd8-a83a-e433d01676e2 ("Expose listing and by-id reads as
MCP resources in addition to tools") rather than ADR 8cf940c5 or a drop —
7531106b's Decision Outcome is literally the decision to expose
`specmgr://adr/{id}` as an RFC 6570 template resource, so it is the most
directly governing ADR for that line; the plan allowed either. (b) Task
100.150, orchestrator/user override (2026-10-07): removed only the first
sentence of `AGENTS.md`'s standalone §10 "Next steps" paragraph (the one
about keeping the plan's per-item done/not-done status in sync with
`src/`); kept the second sentence — "Don't assume any domain package
exists beyond the per-domain bullets in the Status section above ... — check
first." — verbatim as the surviving paragraph, because it is unique,
non-redundant guidance not covered by the "Still genuinely missing" bullet.

#### 2026-10-07 00:00:00.000Z - Plan refinement pass (feat-refiner)

Ran a plan refinement pass (feat-refiner subagent) before implementation started. Applied fixes:
(E1) Task 100.120's scope was widened to also drop `models/adr/__init__.py`'s line-20 lead-in
sentence, not just the `(plan §N)` parentheticals — the original wording would have left a literal
`adr-tool-plan.md` citation and failed ACC-001; the matching Design Notes row was corrected too.
(G1/G2) Added Task 110.112 (verify ACC-003, frozen feat-9 files untouched) and Task 110.114
(verify ACC-004, new `AGENTS.md` clause present) — Phase 110 previously had no explicit check for
either acceptance criterion. (D1) Added `ADR 7531106b-074b-4bd8-a83a-e433d01676e2` and
`ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73` to Related Decisions — both already cited in Design
Notes but missing from the catalog section. (D2/I2) Tightened Task 110.140's wording to explicitly
require copying the Design Notes per-citation disposition table into a new Decisions Made entry,
resolving the ambiguity over where ACC-002's "recorded disposition ... in this file's Decisions
Made log" requirement is actually satisfied. (I1) Task 100.160 now names the exact insertion point
and suggested wording for the new `AGENTS.md` clause.

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
