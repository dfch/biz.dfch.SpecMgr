---
classification: null
created: '2026-11-01T07:22:27.849+01:00'
id: feat-247-dec-outcome-blocks
status: planning
type: feat
updated: '2026-11-01T07:34:22.926+01:00'
version: 1.0.0
---

# Feature: Relax DEC Decision Outcome to Accept Multiple Blocks

## Plan

### Overview

The `dec` parser requires `## Decision Outcome` to hold exactly one lead paragraph (`DecisionOutcome.statement`) before the first `###` sub-section; any further block (a second paragraph, a bullet list of sub-decisions, a code block) is rejected with "text left over after processing all fields". ADR has no such restriction, so about 20 of the 46 ADRs in `docs/adr/` (for example `750842b2`, `92cc4ce8`, `356d8781`) cannot be converted to DEC verbatim. This feature (GitHub issue #247) relaxes `DecisionOutcome` so that further markdown blocks may follow the mandatory lead paragraph, which unblocks the UUID-preserving ADR to DEC migration of GitHub issue #46 without rewriting any decision text.

### Requirements

- REQ-001: `## Decision Outcome` MUST accept zero or more further markdown blocks (paragraphs, bullet lists, code blocks) after the mandatory lead paragraph and before the first `###` sub-section.
- REQ-002: The lead paragraph MUST stay mandatory and MUST stay the value of `DecisionOutcome.statement`; a section whose first block is not a paragraph (a bare list, a `###` heading, nothing) MUST still be rejected.
- REQ-003: A DEC document using the extra blocks MUST round-trip byte-exact through parse and render, and the extra blocks MUST be visible in `model_dump()` output.
- REQ-004: `### Consequences` and `### Confirmation` MUST keep their position, optionality and meaning; a document without extra blocks MUST parse to the same result as before.
- REQ-005: The change MUST be confined to the `dec` domain; no other domain, no shared `models/md` rule and no DEC frontmatter field changes.
- REQ-006: The generated artifacts (`dec_schema.json`, the DEC template and example if they change, `docs/api/*`) MUST be regenerated and the DEC create/update instructions MUST describe the relaxed rule.

### Acceptance Criteria

- [ ] ACC-001: A DEC whose `## Decision Outcome` has a lead paragraph followed by a second paragraph and a bullet list parses via `parse_dec` and the generic `validate` tool (`type="dec"`), and its `body.outcome.statement` is the first paragraph (REQ-001, REQ-002).
- [ ] ACC-002: A DEC whose `## Decision Outcome` starts with a bullet list, starts with `### Consequences`, or is empty is still rejected with an actionable error (REQ-002).
- [ ] ACC-003: The same document round-trips byte-exact and the extra blocks appear in `model_dump()` (REQ-003).
- [ ] ACC-004: All pre-existing `tests/dec/` tests pass unchanged, including the i18n tests that read `outcome.statement` (REQ-004).
- [ ] ACC-005: `git diff` of the change touches no file outside the `dec` package, its tests, the DEC data files, the generated docs and `CHANGELOG.md` (REQ-005, REQ-006).
- [ ] ACC-006: `dec_schema.json` is regenerated and `specmgr docs` leaves no drift (REQ-006).
- [ ] ACC-007: The trial conversion of the 46 ADRs (in memory, per the feat-46 SOP rules) no longer fails with "text left over" in `DecisionOutcome` (REQ-001).

### Scope

#### Included

- Changing the `dec` body model (`dec/models/v1/body.py`) so `DecisionOutcome` accepts the extra blocks after the lead paragraph.
- Parser and model tests in `tests/dec/models/v1/`, including the rejected shapes and byte-exact round-trip.
- Regenerating `dec_schema.json` and the generated docs, and updating the DEC create/update instruction texts and AGENTS.md wording where they state the one-paragraph rule.
- A CHANGELOG `[Unreleased]` entry.

#### Explicitly Out Of Scope

- Any change to the DEC frontmatter, to other domains or to the shared `models/md` engine.
- Accepting raw HTML tokens such as `<d>` in DEC bodies; the migration handles those mechanically.
- The ADR to DEC conversion itself and the removal of the ADR artifact type (GitHub issue #46).
- Relaxing any other DEC section.

### Dependencies

#### Depends On

- None.

#### Blocks

- Feature feat-46-remove-adr (GitHub issue #46): the rollout of the ADR to DEC conversion needs this change merged first.

### Design Notes

Today `DecisionOutcome` declares `statement: MarkdownParagraph`, then the optional `consequences` and `confirmation` H3 sections; the engine leaves the second block of the lead as leftover text. The task is to find the smallest model change that keeps `statement` as the first paragraph and absorbs the remaining blocks into a new optional field (for example a list of further blocks declared before the H3 fields), so that the existing field order, the strict section order and the generated schema stay stable. Task 100.100 decides the exact shape after a short spike against the engine; candidates are a trailing-blocks field on `DecisionOutcome` or a dedicated leaf class that consumes everything up to the next heading. The rule that the lead must be a paragraph (REQ-002) comes from the field order itself and must not be weakened.

Every list item in this document is written as a single physical line (the soft-wrap rule of GitHub issue #99).

### Related Decisions

- None yet; record an ADR or DEC if the spike chooses a shared-engine change.

### Task List

#### Phase 100: Spike and Design

- [ ] Task 100.100: Spike the engine behaviour for a block sequence after a leaf `MarkdownParagraph` and choose the model shape (new optional field or dedicated leaf), recording the choice in Decisions Made.
- [ ] Task 100.110: Verify with the spike that ACC-002's rejected shapes stay rejected and that a document without extra blocks parses identically.

#### Phase 110: Implementation

- [ ] Task 110.100: Change `DecisionOutcome` in `dec/models/v1/body.py` per the chosen shape, with docstrings.
- [ ] Task 110.110: Check every `DecisionOutcome`/`statement` consumer (`dec/models/v1/summary.py`, the i18n heading normalization, the DEC resources and prompts) for assumptions about a single-paragraph lead.
- [ ] Task 110.120: Add tests in `tests/dec/models/v1/test_body.py` and `test_parser.py` for ACC-001, ACC-002 and ACC-003, and run the existing `tests/dec/` suite for ACC-004.

#### Phase 120: Generated Artifacts and Documentation

- [ ] Task 120.100: Regenerate `dec_schema.json` and the API docs with `specmgr schema` and `specmgr docs`, and confirm no drift.
- [ ] Task 120.110: Update the DEC create/update instruction texts and the DEC template/example if they describe the one-paragraph lead, and AGENTS.md's DEC bullet if it does.
- [ ] Task 120.120: Add the CHANGELOG `[Unreleased]` entry.

#### Phase 130: Verification

- [ ] Task 130.100: Run the local quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src --cov-report=`).
- [ ] Task 130.110: Re-run the in-memory trial conversion of the 46 ADRs and confirm ACC-007; hand the result to feat-46.

## Progress

### Current Status

**As of 2026-11-01**: Planned from GitHub issue #247, the prerequisite found while reviewing the feat-46 migration plan. No code has been changed yet.

**Handover**: the next step is a plan refinement (feat-refiner) of this plan and of `feat-46-remove-adr` before any implementation starts. Open points for the refiner: the model shape is deliberately undecided (Task 100.100 spike: a trailing-blocks field on `DecisionOutcome` versus a dedicated leaf class), whether a shared-engine change would need its own decision record, the list of `DecisionOutcome`/`statement` consumers in Task 110.110, and how ACC-007 is checked (the in-memory trial is `100-110-survey-adrs.sh` of feat-46, which classifies each ADR as `clean` or `blocked-by-247`; the expected result is 20 moving from blocked to clean).

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 06:22:27.849Z - Created

Planned from a trial conversion of the 46 ADRs through the real `parse_dec`: 20 failed only because of the single-paragraph lead rule of `## Decision Outcome`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 06:22:27.849Z - Relax the parser instead of rewriting the ADR content

Decided with the maintainer to relax the DEC parser so migrated decision text stays verbatim, accepting the small schema change in the `dec` domain, instead of moving the extra blocks into `### Consequences` or `## More Information` or having an agent rewrite them. Delivered as its own feature so the schema change is reviewed and released separately from the data migration.

### Related PRs / Commits

- [Issue #247](https://github.com/dfch/biz.dfch.SpecMgr/issues/247): this feature.
- [Issue #46](https://github.com/dfch/biz.dfch.SpecMgr/issues/46): remove the ADR artifact type; depends on this feature.
