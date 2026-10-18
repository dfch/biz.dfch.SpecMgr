---
classification: null
created: '2026-10-17T08:55:17.578+02:00'
id: feat-129-remove-inert-heading-validators
status: planning
type: feat
updated: '2026-10-18T09:27:00.492+02:00'
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
- [ ] ACC-007: ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae carries a new dated revision entry documenting the removal decision and rationale.
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

- [ ] Task 100.100: Re-verify no other code path reads `MarkdownSection._tokens` or depends on `validate_heading_structure`/`validate_headings` (repo-wide grep).
- [ ] Task 100.110: Draft the ADR revision wording (removal decision + rationale) for review before editing the ADR.

#### Phase 105: Address Plan-Refinement Findings

- [x] Task 105.100: E1 (resolved) -- the frontmatter `updated` timestamp already matched the newest `### Updates` entry as of the prior refinement pass; the described defect no longer applied (see D1 in the 2026-10-18 refinement round).
- [x] Task 105.110: G1 -- Added REQ-010 (Requirements) and ACC-010 (Acceptance Criteria) covering Phase 135's `markdown_str.py` dead-code removal, closing the traceability gap between the Task List and Requirements/Acceptance Criteria.
- [x] Task 105.120: I1/D2 -- Normalized every ADR cross-reference citation in this document (Overview, REQ-008, ACC-007, Scope, Related Decisions, Task 130.110) to the plain `ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae` tag form (no backticks, tag before id, no truncation), so `list_references`/the reference-graph diagram tooling can resolve this feature's one external dependency.
- [x] Task 105.130: I2 -- Added a one-line note under `### Related Decisions` confirming this feature intentionally has no Depends-On/Blocks relationships beyond the founding ADR, to disambiguate "none" from "forgotten."
- [x] Task 105.140: G2 -- Added REQ-011/ACC-011, a `CHANGELOG.md` Scope bullet, and Task 130.120 to add a brief `[Unreleased]` entry recording this internal cleanup, closing the gap of an undecided CHANGELOG question.
- [x] Task 105.150: I3 -- Added a Design Notes line acknowledging that `docs/sysrs/sysrs-8d752304-...-appendix.md`'s manually-snapshotted ADR `more_information` text (GitHub issue #86) will intentionally diverge from the ADR after Task 130.110's new revision entry.

#### Phase 110: Remove Dead Validators

- [ ] Task 110.100: Remove `validate_heading_structure` and the `_tokens` `PrivateAttr` from `markdown_section.py`; drop now-unused imports.
- [ ] Task 110.110: Remove `validate_headings` from `markdown_section1.py` through `markdown_section6.py`; drop now-unused `model_validator` imports.
- [ ] Task 110.120: Update stale class/method docstrings in all seven files to accurately describe current behavior.

#### Phase 120: Test & Lint Cleanup

- [ ] Task 120.100: Update `tests/models/md/test_markdown_section.py` to remove the stale `validate_headings` reference.
- [ ] Task 120.110: Remove `_.validate_heading_structure`/`_.validate_headings` from `whitelist.py`.
- [ ] Task 120.120: Run `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60`; fix any fallout.

#### Phase 130: Docs & ADR

- [ ] Task 130.100: Regenerate `docs/api/` via `specmgr docs` and confirm the stale entries are gone.
- [ ] Task 130.110: Add the dated revision entry to ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae recording the removal decision.
- [ ] Task 130.120: Add a brief `[Unreleased]` entry to `CHANGELOG.md` documenting this internal cleanup (dead-validator/dead-code removal), satisfying REQ-011/ACC-011.

#### Phase 135: Remove the markdown_str.py Dead-Code Block

- [ ] Task 135.100: Delete the fully-commented-out `# @field_validator("_value") ... def validate_and_convert_text` block in `markdown_str.py`.
- [ ] Task 135.110: Delete the fully-commented-out `# @model_validator(mode="after") ... def model_validator_after` block in `markdown_str.py` (asserts on the same stale `self._tokens` concept the ADR already says was abandoned in favor of `_value: str`).
- [ ] Task 135.120: Re-run `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` to confirm the removal leaves no dangling unused imports or whitelist entries.

#### Phase 140: Verification

- [ ] Task 140.100: Run the full test suite (`uv run --frozen pytest -n auto --cov=src --cov-report=`) and confirm no regressions.
- [ ] Task 140.110: Spot-check that at least one fixture/example per domain still round-trips correctly.

## Progress

### Current Status

**As of 2026-10-17**: Planning. GitHub issue #129 (opened 2026-09-13) leaves the redesign-vs-removal decision open; this plan adopts removal, confirmed with the repo owner, who requested the consequences be documented explicitly (see Design Notes) before implementation begins. No code changes have been made yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

#### 2026-10-17T12:00:00.000Z - Resolved redesign vs. removal: removal

Chose removal over redesigning a genuine second-layer heading-structure check. Rationale: the drafted redesign is incompatible with real multi-level documents (e.g. REQ's nested `## Description`) and depends on a never-populated `_tokens` attribute, so it could not ship as drafted regardless; the load-bearing invariant is already fully enforced by `MarkdownSection.get_extent`/`MarkdownStr.from_text`'s trailing-completeness check, so removal costs no real protection while eliminating a misleading "looks like it checks something" false sense of security.
