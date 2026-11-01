---
classification: null
created: '2026-11-01T07:22:27.849+01:00'
id: feat-247-dec-outcome-blocks
status: planning
type: feat
updated: '2026-11-01T07:59:53.587+01:00'
version: 1.0.0
---

# Feature: Relax DEC Decision Outcome to Accept Multiple Blocks

## Plan

### Overview

The `dec` parser requires `## Decision Outcome` to hold exactly one lead paragraph (`DecisionOutcome.statement`) before the first `###` sub-section; any further block (a second paragraph, a bullet list of sub-decisions, a code block) is rejected with "text left over after processing all fields". ADR has no such restriction, so about 20 of the 46 ADRs in `docs/adr/` (for example `750842b2`, `92cc4ce8`, `356d8781`) cannot be converted to DEC verbatim. This feature (GitHub issue #247) relaxes `DecisionOutcome` so that further markdown blocks may follow the mandatory lead paragraph, which unblocks the UUID-preserving ADR to DEC migration of GitHub issue #46 without rewriting any decision text.

### Requirements

- REQ-001: `## Decision Outcome` MUST accept zero or more further markdown blocks after the mandatory lead paragraph and before the first `###` sub-section; the accepted block kinds are paragraphs, bullet lists, ordered lists and code blocks, and every other kind (block quotes, tables, comments, H4+ headings, raw HTML) MUST stay rejected.
- REQ-002: The lead paragraph MUST stay mandatory and MUST stay the value of the lead-paragraph field of `DecisionOutcome` (`statement` today); a section whose first block is not a paragraph (a bare list, a `###` heading, nothing) MUST still be rejected.
- REQ-003: A DEC document using the extra blocks MUST round-trip byte-exact through parse and then model-to-text (DEC has no renderer, and none is introduced), and the extra blocks MUST be visible in `model_dump()` output.
- REQ-004: `### Consequences` and `### Confirmation` MUST keep their position, optionality and meaning; a document without extra blocks MUST parse to the same result as before; the schema version stays `v1` because the relaxation is additive and every previously valid document still parses.
- REQ-005: The change MUST be confined to the `dec` domain; no other domain, no shared `models/md` rule and no DEC frontmatter field changes.
- REQ-006: The generated artifacts (both copies of `dec_schema.json`, the DEC template and example if they change, `docs/api/*`, `docs/MCP.md`, `docs/GENERATED.md`) MUST be regenerated and the DEC create/update instructions MUST describe the relaxed rule.

### Acceptance Criteria

- [ ] ACC-001: A DEC whose `## Decision Outcome` has a lead paragraph followed by a second paragraph and a bullet list parses via `parse_dec` and the generic `validate` tool (`type="dec"`), and the lead-paragraph field holds the first paragraph (REQ-001, REQ-002).
- [ ] ACC-002: A DEC whose `## Decision Outcome` starts with a bullet list, starts with `### Consequences`, or is empty is still rejected with an actionable error (REQ-002).
- [ ] ACC-003: The same document round-trips byte-exact through parse and model-to-text, and the extra blocks appear in `model_dump()` (REQ-003).
- [ ] ACC-004: All pre-existing `tests/dec/` tests pass unchanged, including the i18n tests that read the lead paragraph; new tests are additive only (REQ-004).
- [ ] ACC-005: `git diff` of the change touches no file outside the `dec` package, its tests, the DEC data files, the generated docs and `CHANGELOG.md` (REQ-005, REQ-006).
- [ ] ACC-006: Both copies of `dec_schema.json` are regenerated and `specmgr docs` leaves no drift (REQ-006).
- [ ] ACC-007: Committed regression fixtures derived from the outcomes of the ADRs `750842b2`, `92cc4ce8` and `356d8781` parse without "text left over" in `DecisionOutcome` (REQ-001).
- [ ] ACC-008: The DEC create and update instruction texts (`dec_create_instructions.md`, `dec_update_instructions.md`) describe that further paragraphs, lists and code blocks may follow the lead paragraph (REQ-006).
- [ ] ACC-009: A block placed after `### Consequences` or between `### Consequences` and `### Confirmation` that violates the H3 order, and a block quote, table, comment or H4+ heading inside the outcome lead, are still rejected (REQ-001, REQ-004).

### Scope

#### Included

- Changing the `dec` body model (`dec/models/v1/body.py`) so `DecisionOutcome` accepts the extra blocks after the lead paragraph.
- Parser, model and tool-level tests, including the rejected shapes, the byte-exact round-trip, the committed ADR-derived fixtures and one translated-variant i18n test.
- Regenerating both copies of `dec_schema.json` and the generated docs, and updating the DEC create/update instruction texts, template/example and AGENTS.md wording where they state the one-paragraph rule.
- A CHANGELOG `[Unreleased]` entry.

#### Explicitly Out Of Scope

- Any change to the DEC frontmatter, to other domains or to the shared `models/md` engine.
- Accepting block quotes, tables, comments, H4+ headings or raw HTML tokens such as `<d>` in the outcome lead; the migration handles raw HTML mechanically.
- The ADR to DEC conversion itself and the removal of the ADR artifact type (GitHub issue #46).
- Relaxing any other DEC section.

### Dependencies

#### Depends On

- None.

#### Blocks

- FEAT feat-46-remove-adr (GitHub issue #46): the rollout of the ADR to DEC conversion needs this change merged first; that feature currently exists only on its own branch `feat-46-remove-adr`, not on `dev`.

### Design Notes

Today `DecisionOutcome` declares `statement: MarkdownParagraph`, then the optional `consequences` and `confirmation` H3 sections; the engine leaves the second block of the lead as leftover text. The task is to find the smallest model change that keeps `statement` as the first paragraph and absorbs the remaining blocks into a new optional field (for example a list of further blocks declared before the H3 fields), so that the existing field order, the strict section order and the generated schema stay stable. Task 100.100 decides the exact shape after a short spike against the engine; candidates are a trailing-blocks field on `DecisionOutcome` or a dedicated leaf class that consumes everything up to the next heading. Selection criteria, in order: smallest schema delta, unchanged `statement` field and field order, byte-exact text round-trip, unchanged H3 ordering rules. If neither candidate works without a `models/md` change, stop and re-plan instead of changing the shared engine. The rule that the lead must be a paragraph (REQ-002) comes from the field order itself and must not be weakened.

The change goes inside `## Decision Outcome` only, between the H2 heading and the first `###` sub-section; nothing under the H1 or in any other section changes. After the spike, update the field names in REQ-002, ACC-001 and ACC-003 if they differ from the wording above.

Every list item in this document is written as a single physical line (the soft-wrap rule of GitHub issue #99).

### Related Decisions

- None; if the spike shows that `models/md` must change, stop and re-plan.

### Task List

#### Phase 100: Spike and Design

- [ ] Task 100.100: Spike the engine behaviour for a block sequence after a leaf `MarkdownParagraph` and choose the model shape (new optional field or dedicated leaf) using the selection criteria in Design Notes, recording the choice in Decisions Made; if `models/md` would have to change, stop and re-plan.
- [ ] Task 100.110: After the spike, align the field names used in REQ-002, ACC-001 and ACC-003 with the chosen shape.

#### Phase 110: Implementation

- [ ] Task 110.100: Change `DecisionOutcome` in `dec/models/v1/body.py` per the chosen shape, with docstrings.
- [ ] Task 110.110: Check every consumer of the lead paragraph for assumptions about a single-paragraph lead: the i18n tests (`tests/dec/tools/test_i18n_language.py`, `test_i18n_write.py`), the DEC create/update instruction texts, the DEC prompts and resources.
- [ ] Task 110.120: Add tests in `tests/dec/models/v1/test_body.py` and `test_parser.py` for ACC-001, ACC-002, ACC-003 and ACC-009 (including the rejected shapes: bare list first, `### Consequences` first, empty, extra block after or between the H3 sections, block quote, table, comment, H4+), and run the existing `tests/dec/` suite for ACC-004.
- [ ] Task 110.130: Add tool-level tests in `tests/dec/tools/` for `parse_dec` and the generic `validate` (`type="dec"`) with the relaxed shape, and one i18n test with a translated variant that carries extra blocks.
- [ ] Task 110.140: Commit regression fixtures derived from the outcomes of the ADRs `750842b2`, `92cc4ce8` and `356d8781` and a test asserting they parse (ACC-007).

#### Phase 120: Generated Artifacts and Documentation

- [ ] Task 120.100: Regenerate both copies of `dec_schema.json` (`src/biz/dfch/specmgr/dec/data/` and `docs/`), the API docs, `docs/MCP.md` and `docs/GENERATED.md` with `specmgr schema`, `specmgr docs` and `specmgr mcp-docs`, update the `dec/models` and `dec/models/v1` export lists and `whitelist.py` if a new class is added, and confirm no drift.
- [ ] Task 120.110: Update `dec_create_instructions.md` (lines 28-30) and `dec_update_instructions.md` (line 50) for ACC-008, the DEC template/example (`dec_template.md`, `dec_example.md`) if they describe the one-paragraph lead, and AGENTS.md's DEC bullet if it states the rule; record in Decisions Made whether AGENTS.md needed a change.
- [ ] Task 120.120: Add the CHANGELOG `[Unreleased]` entry.

#### Phase 130: Verification

- [ ] Task 130.100: Run the local quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src --cov-report=`).
- [ ] Task 130.105: Review `git diff --stat` against ACC-005 and confirm no file outside the allowed set changed.
- [ ] Task 130.110: Run the one-off in-memory trial conversion of the 46 ADRs, record the result as a snapshot in Updates (before: 46 total, 20 blocked, 26 clean; expected after: 46 clean for this rule), and hand the result to feat-46.

## Progress

### Current Status

**As of 2026-11-01**: Planned from GitHub issue #247, the prerequisite found while reviewing the feat-46 migration plan. The plan was refined (feat-refiner) and the findings were applied; no code has been changed yet.

**Handover**: the next step is Phase 100, the engine spike. The only deliberately open point is the model shape (a trailing-blocks field on `DecisionOutcome` versus a dedicated leaf class); the other refinement points are resolved in Decisions Made.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 07:45:00.000Z - Plan refined

Applied the feat-refiner findings: defined the accepted block set, added ACC-008 and ACC-009, made ACC-007 reproducible through committed fixtures, added the tool-level, i18n and diff-scope tasks, listed the full set of generated artifacts, aligned the round-trip wording with the absence of a DEC renderer, and fixed the `Blocks` reference to the `FEAT <id>` form.

#### 2026-11-01 06:22:27.849Z - Created

Planned from a trial conversion of the 46 ADRs through the real `parse_dec`: 20 failed only because of the single-paragraph lead rule of `## Decision Outcome`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 07:45:00.000Z - Refinement decisions

- No shared-engine fallback: if the spike shows that `models/md` must change, stop and re-plan; REQ-005 and ACC-005 stay strict and no decision record is pre-planned for it.
- Accepted further blocks are paragraphs, bullet lists, ordered lists and code blocks only; block quotes, tables, comments and H4+ headings stay rejected, which also keeps the i18n heading skeleton unaffected.
- ACC-007 is proven by committed fixtures derived from three representative ADR outcomes; the full 46-ADR run is a one-off manual check recorded as a snapshot, because it depends on the feat-46 conversion rules and on `docs/adr/`, which that feature removes.
- The schema stays at `dec/models/v1`: the relaxation is additive and non-breaking.
