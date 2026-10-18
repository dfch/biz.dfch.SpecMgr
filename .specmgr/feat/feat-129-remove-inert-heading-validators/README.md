---
classification: null
created: '2026-10-17T08:55:17.578+02:00'
id: feat-129-remove-inert-heading-validators
status: planning
type: feat
updated: '2026-10-18T21:17:24.066+02:00'
version: 1.0.0
---

# Feature: Remove the Inert `validate_heading_structure`/`validate_headings` Heading Validators (models/md)

## Plan

### Overview

`models/md/markdown_section.py` and `markdown_section1.py`..`markdown_section6.py` each declare a `@model_validator(mode="after")` (`validate_heading_structure` on the base `MarkdownSection`, `validate_headings` on each `MarkdownSectionN`) that runs on every parsed instance but whose actual assertions have been commented out since they were drafted -- they do nothing today. This is documented as a known follow-up in the founding ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae (v1.5.0). The real structural invariant ("no illegal same-or-higher nested heading") is already enforced procedurally by `MarkdownSection.get_extent`'s own stop condition plus `MarkdownStr.from_text`'s mandatory trailing-completeness check -- the inert validators were only ever meant as a second, defense-in-depth layer. The drafted `MarkdownSection1.validate_headings` body is also incompatible with real usage: it would reject *any* heading after the H1's own triple, but domains like `req` legitimately nest a `##`-rendering `Description` field inside `Requirement(MarkdownSection1)`, so every real top-level document would fail this check if it were simply uncommented. This feature removes the dead validators, the never-populated `_tokens: list[Token]` `PrivateAttr` they would have depended on, and the now-stale docstrings that contradict real usage (e.g. `MarkdownSection1`'s "no nested headings allowed" claim) -- and records the resolution as a dated revision on the founding ADR.

### Requirements

- REQ-001: Remove the inert `validate_heading_structure` `model_validator` from `MarkdownSection` (`markdown_section.py`).
- REQ-002: Remove the inert `validate_headings` `model_validator` from each of `MarkdownSection1`..`MarkdownSection6` (`markdown_section1.py`..`markdown_section6.py`).
- REQ-003: Remove the unused `_tokens: list[Token] = PrivateAttr(default_factory=list)` declaration from `MarkdownSection`, and any `Token`/`PrivateAttr`/`model_validator` imports left unused by REQ-001/REQ-002 across all seven files.
- REQ-004: Correct every now-stale docstring that claims a removed check exists or that nested headings are disallowed (notably `MarkdownSection1`'s class docstring and its removed method's docstring) across `markdown_section.py` and `markdown_section1.py`..`markdown_section6.py`, to accurately state that a deeper nested heading is allowed and silently retained, with only same-or-higher-level nesting excluded, by `get_extent`.
- REQ-005: Remove the now-stale `_.validate_heading_structure` / `_.validate_headings` vulture whitelist entries from `whitelist.py`.
- REQ-006: Update `tests/models/md/test_markdown_section.py`'s `test_directly_assigning_a_nested_heading_to_value_raises_nothing` (and its docstring, which currently describes `validate_headings` as "currently a no-op") since the method it describes no longer exists.
- REQ-007: Regenerate `docs/api/` via `specmgr docs` so every generated page's stale `validate_heading_structure`/`validate_headings` entries are pruned.
- REQ-008: Add a dated revision entry to ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae recording the removal decision and its rationale, per the ADR's own established revision-entry convention.
- REQ-009: Every existing domain fixture/example (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs`) must continue to parse/round-trip exactly as before this removal -- no behavioral change, since the removed checks were already no-ops.
- REQ-010: `markdown_str.py`'s fully-commented-out `validate_and_convert_text`/`model_validator_after` dead-code block (Phase 135) must be removed as a first-class requirement of this feature, not treated as an unscoped side effect of the Scope `Included` bullet alone.
- REQ-011: Add a brief `[Unreleased]` entry to `CHANGELOG.md` documenting this internal dead-code/dead-validator removal, consistent with the project's established convention of recording internal reorganizations there.

### Acceptance Criteria

- [ ] ACC-001: `markdown_section.py` no longer declares `validate_heading_structure` or the `_tokens` `PrivateAttr`; `markdown_section1.py`..`markdown_section6.py` no longer declare `validate_headings`.
- [ ] ACC-002: No import of `model_validator`, `PrivateAttr`, or `Token` remains unused in these seven files (ruff/vulture clean).
- [ ] ACC-003: `MarkdownSection1`'s docstring (and any sibling class docstring with the same stale claim) accurately describes current behavior.
- [ ] ACC-004: `whitelist.py` no longer lists `_.validate_heading_structure`/`_.validate_headings`.
- [ ] ACC-005: `tests/models/md/test_markdown_section.py` has no reference to the removed `validate_headings` method, and still documents/tests that a leaf section silently retains a deeper nested heading via `get_extent`.
- [ ] ACC-006: `docs/api/` no longer lists `validate_heading_structure`/`validate_headings` anywhere, confirmed by regenerating docs via `specmgr docs`.
- [x] ACC-007: ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae carries a new dated revision entry documenting the removal decision and rationale (v1.6.0, 2026-10-18).
- [ ] ACC-008: Full test suite (`uv run --frozen pytest -n auto`) passes with no regressions.
- [ ] ACC-009: `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` all pass clean.
- [ ] ACC-010: `markdown_str.py` no longer contains the fully-commented-out `# @field_validator("_value") ... validate_and_convert_text` or `# @model_validator(mode="after") ... model_validator_after` blocks.
- [ ] ACC-011: `CHANGELOG.md`'s `[Unreleased]` section includes an entry for this removal.

### Scope

#### Included

- `markdown_section.py`: remove `validate_heading_structure`, remove `_tokens` `PrivateAttr`, update docstrings/imports.
- `markdown_section1.py` through `markdown_section6.py`: remove `validate_headings`, update docstrings/imports.
- `whitelist.py`: remove the two now-stale vulture entries.
- `tests/models/md/test_markdown_section.py`: update the test(s) referencing the removed validator.
- `docs/api/` regeneration via `specmgr docs`.
- ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae: new dated revision entry recording the resolution.
- `markdown_str.py`: remove the fully-commented-out `# @field_validator("_value") ... validate_and_convert_text` and `# @model_validator(mode="after") ... model_validator_after` dead-code block (lines ~687-707) -- not named by issue #129 itself, but the same class of dead code, found during this feature's own repo-wide no-op scan (see Phase 135).
- `CHANGELOG.md`: add a brief `[Unreleased]` entry documenting this internal dead-code/dead-validator removal.

#### Explicitly Out Of Scope

- Designing or implementing a genuine second-layer heading-structure check (the rejected "redesign" resolution).
- Any change to `MarkdownSection.get_extent` or `MarkdownStr.from_text`'s trailing-completeness check -- these already provide the real invariant and are unaffected by this feature.

### Design Notes

Consequences of removal: there is no behavioral change for any document, since both validators are already no-ops -- their assertions are fully commented out, so no document that currently parses successfully will newly fail, and no currently-invalid document will newly be accepted. What is given up is only an already-nonexistent "second layer" of defense-in-depth the founding ADR originally envisioned; since the drafted `MarkdownSection1.validate_headings` body (`assert not any(heading in self._tokens[3:] ...)`) is incompatible with real multi-level documents (e.g. REQ's nested `## Description`) and also depends on a `_tokens` attribute the current design never populates, it could not have been safely uncommented as-is regardless -- removal does not forfeit a check that could realistically have shipped without a nontrivial rework. The real structural invariant ("no illegal same-or-higher nested heading") remains fully enforced by `MarkdownSection.get_extent`'s own stop condition plus `MarkdownStr.from_text`'s trailing completeness check, unaffected by this change. Leaving the dead validators in place carries its own risk: a future maintainer debugging a heading-structure bug could assume `validate_headings` still provides protection (it is still invoked on every parse) when it does nothing -- removing it removes that false sense of security, which is a net benefit, not merely a neutral cleanup.

Note: `docs/sysrs/sysrs-8d752304-...-appendix.md` embeds a manually-generated, point-in-time snapshot of this ADR's `more_information` text (GitHub issue #86); it is not auto-regenerated, so once REQ-008/Task 130.110 adds a new dated revision entry to the live ADR, that snapshot will intentionally no longer match it verbatim -- this is expected drift, not a defect introduced by this feature.

### Related Decisions

- ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae: founding ADR for `models/md`'s heading-mapped parser; this feature adds the dated revision entry resolving its documented "known follow-up."

This feature intentionally has no `Depends On`/`Blocks` relationships beyond the founding ADR above -- the plan's `dependencies: null` is deliberate, not an oversight.

### Task List

#### Phase 100: Confirm Scope

- [x] Task 100.100: Re-verified via repo-wide grep -- no code path outside the seven declaring files reads `MarkdownSection._tokens` or depends on `validate_heading_structure`/`validate_headings`; `Token`/`PrivateAttr`/`model_validator` are each used exactly once per file, confirming REQ-003's unused-import prediction.
- [x] Task 100.110: Drafted and applied the ADR revision wording -- see ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae's `more_information` (v1.6.0, dated 2026-10-18) and Task 130.110 below.

#### Phase 105: Address Plan-Refinement Findings

- [x] Task 105.100: E1 (resolved) -- the frontmatter `updated` timestamp already matched the newest `### Updates` entry as of the prior refinement pass; the described defect no longer applied (see D1 in the 2026-10-18 refinement round).
- [x] Task 105.110: G1 -- Added REQ-010 (Requirements) and ACC-010 (Acceptance Criteria) covering Phase 135's `markdown_str.py` dead-code removal, closing the traceability gap between the Task List and Requirements/Acceptance Criteria.
- [x] Task 105.120: I1/D2 -- Normalized every ADR cross-reference citation in this document (Overview, REQ-008, ACC-007, Scope, Related Decisions, Task 130.110) to the plain `ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae` tag form (no backticks, tag before id, no truncation), so `list_references`/the reference-graph diagram tooling can resolve this feature's one external dependency.
- [x] Task 105.130: I2 -- Added a one-line note under `### Related Decisions` confirming this feature intentionally has no Depends-On/Blocks relationships beyond the founding ADR, to disambiguate "none" from "forgotten."
- [x] Task 105.140: G2 -- Added REQ-011/ACC-011, a `CHANGELOG.md` Scope bullet, and Task 130.120 to add a brief `[Unreleased]` entry recording this internal cleanup, closing the gap of an undecided CHANGELOG question.
- [x] Task 105.150: I3 -- Added a Design Notes line acknowledging that `docs/sysrs/sysrs-8d752304-...-appendix.md`'s manually-snapshotted ADR `more_information` text (GitHub issue #86) will intentionally diverge from the ADR after Task 130.110's new revision entry.

#### Phase 110: Remove Dead Validators

- [x] Task 110.100: Remove `validate_heading_structure` and the `_tokens` `PrivateAttr` from `markdown_section.py`; drop now-unused imports.
- [x] Task 110.110: Remove `validate_headings` from `markdown_section1.py` through `markdown_section6.py`; drop now-unused `model_validator` imports.
- [x] Task 110.120: Update stale class/method docstrings in all seven files to accurately describe current behavior.

#### Phase 120: Test & Lint Cleanup

- [x] Task 120.100: Update `tests/models/md/test_markdown_section.py` to remove the stale `validate_headings` reference.
- [x] Task 120.110: Remove `_.validate_heading_structure`/`_.validate_headings` from `whitelist.py`.
- [x] Task 120.120: Run `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60`; fix any fallout.

#### Phase 130: Docs & ADR

- [x] Task 130.100: Regenerate `docs/api/` via `specmgr docs` and confirm the stale entries are gone.
- [x] Task 130.110: Added the dated revision entry to ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae recording the removal decision (bumped to v1.6.0, dated 2026-10-18; full wording in the ADR's own `more_information`, drafted under Task 100.110 above).
- [x] Task 130.120: Add a brief `[Unreleased]` entry to `CHANGELOG.md` documenting this internal cleanup (dead-validator/dead-code removal), satisfying REQ-011/ACC-011.

#### Phase 135: Remove the markdown_str.py Dead-Code Block

- [x] Task 135.100: Delete the fully-commented-out `# @field_validator("_value") ... def validate_and_convert_text` block in `markdown_str.py`.
- [x] Task 135.110: Delete the fully-commented-out `# @model_validator(mode="after") ... def model_validator_after` block in `markdown_str.py` (asserts on the same stale `self._tokens` concept the ADR already says was abandoned in favor of `_value: str`).
- [x] Task 135.120: Re-run `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` to confirm the removal leaves no dangling unused imports or whitelist entries.

#### Phase 140: Verification

- [x] Task 140.100: Run the full test suite (`uv run --frozen pytest -n auto --cov=src --cov-report=`) and confirm no regressions.
- [x] Task 140.110: Spot-check that at least one fixture/example per domain still round-trips correctly.

## Progress

### Current Status

**As of 2026-10-18**: Implementation complete -- all phases (100/105/110/120/130/135/140) closed, and all acceptance criteria verified with concrete evidence in the 2026-10-18T21:17 Phase 140 entry: the full suite passed (4668 passed, 17 skipped -- identical counts to every prior phase's baseline, no regressions, ACC-008), the 12-domain packaged-example round-trip spot-check (Task 140.110, REQ-009) PASSed 7 domains with the 5 failing domains (req/uc/dec/sop/vcr) proven pre-existing via byte-identical behavior at the pre-implementation base `3b746d4`, and every ACC grep/lint gate was clean (zero residual `validate_heading*`/`validate_and_convert_text`/`model_validator_after` matches in `src/`/`tests/`/`whitelist.py`/`docs/api/`, ruff format/check + vulture all green, CHANGELOG `[Unreleased]` entry in place, ADR v1.6.0 revision line present). Awaiting review.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-18T21:17:00.000+02:00 - Closed Phase 140: final verification passed

Ran the full suite (`uv run --frozen pytest -n auto --cov=src --cov-report=`): **4668 passed, 17 skipped** in 47.50s (exit 0) -- identical passed/skipped counts to the Phase 110/120/130/135 baseline, so Task 140.100/ACC-008 ("no regressions") holds (the "5662 subtests" figure in prior entries is the unittest-discovery gate's count; this pytest configuration reports no subtests line in its summary). Task 140.110 (REQ-009): a spot-check script (`/tmp/opencode/roundtrip_spotcheck.py`, kept outside the repo) parsed each of the 12 packaged examples (`<d>/data/<d>_example.md`) with the domain's own `parse_<d>` entry point and asserted the repo-canonical round-trip used by every domain's own parser tests (`str(document.body) == format_text(frontmatter.loads(raw).content)`): **PASS x7** (tsk, qa, prb, gol, rsk, feat, sysrs) and **FAIL x5** (req, uc, dec, sop, vcr). The five failures are a pre-existing engine/example property (the rendered body inserts a blank line between consecutive list items those examples author without one), **not** a regression: re-running the identical script at the pre-implementation base `3b746d4` in a throwaway worktree (removed afterward) produced byte-identical PASS/FAIL lines for all 12 domains, and a dump of every domain's rendered example body diffed empty between base and branch -- no behavioral change, evidence-backed. ACC evidence: the `validate_heading_structure|validate_headings|validate_and_convert_text|model_validator_after` grep across `src/`/`tests/`/`whitelist.py` returns zero matches (exit 1; ACC-001/ACC-002/ACC-010), `whitelist.py` has zero `validate_heading` matches (ACC-004), `docs/api/` has zero matches (ACC-006), `ruff format --check` (2063 files already formatted), `ruff check` (All checks passed!), and `vulture src/ whitelist.py --min-confidence 60` (exit 0) are all clean (ACC-009), `CHANGELOG.md` carries the `[Unreleased]` `### Changed` entry (line 23, ACC-011), and ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae carries exactly one `Revised 2026-10-18 (v1.6.0)` line (ACC-007). All acceptance criteria verified; the ACC boxes are intentionally left unticked for the orchestrator's review-status commit per repo precedent.

#### 2026-10-18T20:57:00.000+02:00 - Closed Phase 135: removed the markdown_str.py dead-code block

Deleted the fully commented-out dead-code block at the end of `MarkdownStr` in `src/biz/dfch/specmgr/models/md/markdown_str.py` (lines 687-707: the `# @field_validator("_value") ... validate_and_convert_text` and `# @model_validator(mode="after") ... model_validator_after` methods, plus the preceding blank separator line so the file ends with a single trailing newline per ruff convention) (REQ-010, ACC-010). The names referenced inside the block (`md`, `Token`, `field_validator`, `model_validator`) appear only within comments and were never imported, so no import changes were needed and the file is now 685 lines. Gate evidence: `ruff format --check` (2063 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean), zero grep matches for the removed names or `_tokens` in the file and repo-wide for `validate_and_convert_text`, `tests/models/md/` green (365 passed, 48 subtests), and the full suite passed (4668 passed, 17 skipped, 5662 subtests).

#### 2026-10-18T20:47:00.000+02:00 - Closed Phase 130: docs regeneration verified, CHANGELOG entry added

Ran `uv run --frozen specmgr docs` (515 module pages + `docs/GENERATED.md` rewritten) and confirmed zero working-tree changes under `docs/` (`git status --short docs/` empty) -- the regenerated `docs/api/` pages already landed in Phase 110's commit (48175dd) via the pre-commit drift hook, so Task 130.100 is a verification pass proving ACC-006 with no generated page listing the removed `validate_heading_structure`/`validate_headings` (the only remaining `docs/`-wide matches are the ADR's own revision-history prose, out of scope, and the sysrs appendix's point-in-time snapshot, expected drift per Design Notes). Added a new `### Changed` subsection under `## [Unreleased]` in `CHANGELOG.md`, positioned before the existing `### Fixed`, with one bullet documenting the feature's dead-validator/dead-code removal and its no-behavioral-change rationale (REQ-011/ACC-011); Task 130.110's ADR v1.6.0 dated revision entry was re-verified in place (line 52).

#### 2026-10-18T20:37:00.000+02:00 - Closed Phase 120: test and lint-whitelist cleanup

Updated `tests/models/md/test_markdown_section.py`'s
`test_directly_assigning_a_nested_heading_to_value_raises_nothing` docstring (REQ-006): it no
longer describes the removed `validate_headings` as "a no-op" but now states that no model
validator re-checks `_value`'s content shape after construction, citing ADR
832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.6.0 / feat-129 -- the test body is unchanged and,
together with its untouched sibling `test_leaf_section_silently_retains_a_deeper_nested_heading`,
still covers ACC-005. Removed the two stale `_.validate_heading_structure`/`_.validate_headings`
vulture whitelist entries from `whitelist.py` (REQ-005/ACC-004), leaving the surrounding block
intact. Gate evidence: `ruff format --check` (2063 files already formatted), `ruff check` (all
checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean, nothing new reported),
a repo-wide grep for both removed names across `tests/`/`src/`/`whitelist.py` (zero matches),
the targeted `test_markdown_section.py` run green (22 passed, 6 subtests), and the full suite
passed (4668 passed, 17 skipped, 5662 subtests).

#### 2026-10-18T20:18:00.000+02:00 - Closed Phase 110: removed the inert heading validators

Removed `validate_heading_structure` (together with the never-populated `_tokens` `PrivateAttr`) from
`markdown_section.py` and `validate_headings` from `markdown_section1.py`..`markdown_section6.py`,
dropping the now-unused `Token`, `PrivateAttr`, and `model_validator` imports (REQ-001..REQ-003), and
corrected the six sibling class docstrings to state that a deeper heading is allowed and silently
retained while a same-or-higher heading ends the section -- enforced by `MarkdownSection.get_extent`
plus `MarkdownStr.from_text`'s trailing-completeness check, not by any model validator (REQ-004/
ACC-003). No behavioral change: `ruff format --check`, `ruff check`, and `vulture` are all clean,
`tests/models/md/` is green (365 passed, 48 subtests), and the full suite passed (4668 passed, 17
skipped, 5662 subtests). The stale `whitelist.py` entries and the `test_markdown_section.py` docstring
reference to `validate_headings` are deliberately left for Phase 120.

#### 2026-10-18T19:30:00.000+02:00 - Closed Phase 100: verified no dependents and landed the ADR revision

Completed Task 100.100 (repo-wide grep: confirmed no code path outside the seven declaring files
reads `MarkdownSection._tokens` or depends on `validate_heading_structure`/`validate_headings`,
and that `Token`/`PrivateAttr`/`model_validator` are each used exactly once per file -- matching
REQ-003's unused-import prediction exactly) and Task 100.110 (drafted the ADR revision wording,
reviewed, and applied it). Added the dated revision entry to ADR
832cd6c1-ef8a-4bfc-990e-a610823f61ae's `more_information` and bumped its version to v1.6.0,
closing Task 130.110 and ACC-007 ahead of the rest of implementation. Phase 100 is now fully
closed; Phase 110 (the actual code removal) can begin.

#### 2026-10-18T09:00:00.000+02:00 - Second refinement pass: closed Phase 105's open items and added two new findings

Ran a second plan refinement pass. Closed Tasks 105.100-130: corrected the now-moot E1 description
(D1 -- `updated` already matched the newest Updates entry), normalized every ADR cross-reference in
this document to the plain `ADR <uuid>` tag form (I1, also fixing D2's truncated `ACC-007` citation),
and added the no-dependencies note under `### Related Decisions` (I2). Added REQ-010/ACC-010 (G1)
explicitly covering Phase 135's `markdown_str.py` removal. Added two new findings as Tasks
105.140/105.150: G2 (no decision had been recorded on whether this cleanup warrants a
`CHANGELOG.md` entry -- resolved yes, via new REQ-011/ACC-011/Task 130.120) and I3 (a Design Notes
line acknowledging that `docs/sysrs/sysrs-8d752304-...-appendix.md`'s manually-snapshotted ADR text
will diverge once Task 130.110 lands).

#### 2026-10-17T15:45:00.000+02:00 - Added Phase 105 to track plan-refinement findings

Ran a plan refinement pass and added `#### Phase 105: Address Plan-Refinement Findings`
(between Phase 100 and Phase 110, per the feat-numbering insertion convention) tracking the
identified error (E1: stale `updated` timestamp), gap (G1: Phase 135 missing its own
REQ/ACC entries), and improvements (I1: non-machine-resolvable ADR citation style; I2: no
explicit no-dependencies note) as Task 105.100-105.130, to be addressed before implementation
begins.

#### 2026-10-17T13:30:00.000Z - Added Phase 135 for a second dead-code block in markdown_str.py

A repo-wide scan for similar inert/fully-commented-out validators found one more instance outside issue #129's named files: `markdown_str.py`'s fully-commented-out `# @field_validator("_value") ... validate_and_convert_text` and `# @model_validator(mode="after") ... model_validator_after` block, which also references the abandoned `_tokens` concept. Added Phase 135 to remove it in the same pass, and moved the corresponding bullet from Scope's "Explicitly Out Of Scope" to "Included" accordingly.

#### 2026-10-17T12:00:00.000Z - Created

Drafted the feature plan from GitHub issue #129, grounded in a read of `markdown_section.py`/`markdown_section1.py`..`6.py`, ADR `832cd6c1-...`, `whitelist.py`, and the existing test file documenting the no-op behavior.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-18T21:17:00.000+02:00 - Phase 140 round-trip criterion: domain `parse_<d>` + canonical body comparison, byte-identical base attribution for the pre-existing failures

Task 140.110's literal `cls.from_text(raw)` / `str(parsed) == raw` form does not exist at the document level: every domain's `<DocClass>` (e.g. `ReqDocument`) is a plain frontmatter+body `BaseModel` wrapper whose `document.py` docstring explicitly declines a `from_text`, and the domain's actual parse machinery is the free function `parse_<d>(raw)` the `parse_<d>`/`create_<d>` tools delegate to. The spot-check therefore parses via `parse_<d>` and asserts the repo-canonical round-trip every domain's own parser tests use (`str(document.body) == format_text(frontmatter.loads(raw).content)`), keeping the task's byte-exact spirit by additionally diffing every domain's rendered example body between the branch and the pre-implementation base `3b746d4` -- the two sides are byte-identical for all 12 domains, the strongest available no-behavioral-change evidence (the 5 canonical-form failures -- req/uc/dec/sop/vcr -- exist identically on both sides and are a pre-existing list-spacing rendering property of those packaged examples).

#### 2026-10-17T12:00:00.000Z - Resolved redesign vs. removal: removal

Chose removal over redesigning a genuine second-layer heading-structure check. Rationale: the drafted redesign is incompatible with real multi-level documents (e.g. REQ's nested `## Description`) and depends on a never-populated `_tokens` attribute, so it could not ship as drafted regardless; the load-bearing invariant is already fully enforced by `MarkdownSection.get_extent`/`MarkdownStr.from_text`'s trailing-completeness check, so removal costs no real protection while eliminating a misleading "looks like it checks something" false sense of security.
