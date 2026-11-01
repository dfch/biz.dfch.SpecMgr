---
classification: null
created: '2026-09-27T16:03:36.781+02:00'
id: feat-163-feat-numbering
status: done
type: feat
updated: '2026-10-07T06:21:40.909Z'
version: 1.0.0
---

# Feature: FEAT Phase/Task Numbering Scheme (Phase NNN, Task NNN.MMM)

## Plan

### Overview

Introduces a stable, gap-friendly numbering scheme to the FEAT Task List, modeled on the QA question numbering of feat-156 (GitHub issue #156). Phases carry 3-digit numbers starting at 100, step 10 (Phase 100, Phase 110, ...); tasks inside a phase are numbered {phase}.{task} with the task component also starting at 100, step 10 (Task 100.100, Task 100.110, ...). Only the number SHAPES are enforced by the schema; step-10 and uniqueness are authoring conventions, so phases and tasks can be inserted in-between without ever renumbering. The feat schema (feat/models/v1), the packaged template and example, both JSON Schema artifacts, the create_feat/update_feat prompt instructions, and a new project OpenCode skill are all updated to the new scheme, including the issue's side task: auditing that the prompts' section descriptions match the schema's mandatory/optional reality.

### Requirements

- REQ-001: The `Phase` heading alias enforces 3-digit zero-padded phase numbers: `#### Phase NNN: {title}` matches `^Phase \d{3}: .+$`, and legacy unpadded headings (`Phase 1`) are rejected.
- REQ-002: Every `### Task List` checklist item carries the task-number prefix `Task NNN.MMM: ` (3-digit phase component, dot, 3-digit task component), enforced by a new feat-local task-item class replacing the current as-is reuse of `tsk.models.v1.task_item.TaskItem` in `Phase.items`.
- REQ-003: Neither the step-10 increment nor the uniqueness of phase or task numbers is enforced: gaps and in-between values (e.g. `Phase 105`, `Task 100.105`) always parse; once assigned, a number is permanent, and removals leave gaps.
- REQ-004: No cross-check of a task's phase component against the enclosing phase's number; that match is an authoring convention documented in the prompts and skill, never validated.
- REQ-005: The validation failures introduced by this feature are actionable (document-relative field path, 1-based line, cause + fix hint) and evaluated eagerly at parse time, per the existing `_validate_items_eagerly` and feat-27-validation conventions.
- REQ-006: The packaged template (`feat/data/feat_template.md`), packaged example (`feat/data/feat_example.md`), and its byte-identical reference fixture (`tests/feat/models/v1/data/feat_reference.md`) use the new scheme (Phase 100/110, Task 100.100/110.100/110.110) and still round-trip through `parse_feat`.
- REQ-007: The `create_feat` and `update_feat` prompt instruction files (`feat/data/feat_create_instructions.md`, `feat/data/feat_update_instructions.md`) describe the numbering scheme (start values, step 10, in-between insertion, permanence, shape-only enforcement).
- REQ-008: The create/update prompts' section optionality descriptions match `feat/models/v1/body.py` (issue #163 side task); any discrepancy found is fixed, and a regression test pins the prompts' mandatory/optional section sets against the model's required/optional field sets.
- REQ-009: A new project OpenCode skill `.opencode/skills/feat-numbering/SKILL.md` teaches the FEAT numbering scheme (phase/task start values and step, in-between insertion, permanence, pointers to `specmgr://feat/template`/`example`/`schema`) and its content agrees with the prompts.
- REQ-010: Both schema artifacts are regenerated from the updated model with no drift: packaged `feat/data/feat_schema.json` and `docs/feat_schema.json` (`specmgr schema`), plus `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`) where docstrings change.
- REQ-011: A consistency sweep updates every remaining reference to the legacy "Phase N"/"Task N.M" convention: code docstrings, test fixtures (the create walkthrough body `Phase 0`/`Task 0.1`, the issue-70 regression body `Phase 3`/`Task 3.1`), `whitelist.py` vulture entries, and the TSK document `tsk-2687d267` that describes the FEAT shape.

### Acceptance Criteria

- [x] ACC-001: A document with `#### Phase 100: X` and items `- [ ] Task 100.100: Y` / `- [x] Task 100.110: Z` parses via `parse_feat`/`create_feat`/`validate(type="feat")`, including an in-between item (`Task 100.105: ...`).
- [x] ACC-002: A legacy phase heading (`#### Phase 1: X`) or a task item lacking the number prefix (or carrying a legacy `Task 1.1:` number) is rejected with an actionable error naming the item's field path and 1-based line.
- [x] ACC-003: The packaged template and example (and the byte-identical reference fixture) parse via `parse_feat`, and the resource/tool parity tests stay green.
- [x] ACC-004: The create/update prompts contain the scheme description, and the create walkthrough test (`list_feat` -> `create_feat` against a temporary `SPECMGR_FEAT_DIR`) is green with a new-shape body.
- [x] ACC-005: The new regression test asserting the prompts' mandatory/optional section sets equal the model's required/optional field sets is green (after the REQ-008 fixes, if any).
- [x] ACC-006: The project skill exists at `.opencode/skills/feat-numbering/SKILL.md` with a valid `name`/`description` frontmatter, and its scheme wording agrees with the prompts, template, and example (no stale "Phase N"/"Task N.M" guidance).
- [x] ACC-007: `specmgr schema`, `specmgr mcp-docs`, and `specmgr docs` report no drift, and the full quality gate is green: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen pytest -n auto --cov=src`.

### Scope

#### Included

- `feat/models/v1/body.py`: `Phase` alias/heading pattern + computed `number`/`title`, and the new feat-local task-item class with the `Task NNN.MMM: ` prefix + eager validation.
- `feat/data/feat_template.md`, `feat_example.md`, `feat_schema.json`, `feat_create_instructions.md`, `feat_update_instructions.md`.
- The new project skill `.opencode/skills/feat-numbering/SKILL.md` (the repo's second project skill -- feat-150's `repair` skill, `.opencode/skill/repair/SKILL.md`, landed on `dev` and was merged into this branch during implementation; the default project skill path is scanned automatically, so no `opencode.json` change is needed).
- Regeneration of `docs/feat_schema.json`, `docs/MCP.md`, and `docs/api/` + `docs/GENERATED.md`.
- Tests: `tests/feat/**` updates, the `tests/regression/test_issue_70.py` fixture update, the new prompt ↔ schema optionality regression test, and a skill-content consistency test.
- `whitelist.py` vulture entries as needed.
- The side-task optionality audit (REQ-008) and any wording fixes it produces.
- The FEAT-shape description text in the TSK document `tsk-2687d267` (REQ-011).

#### Explicitly Out Of Scope

- Migrating/renumbering the existing `.specmgr/feat/*/README.md` documents from legacy `Phase N`/`Task N.M` to the new scheme -- under the strict policy they fail `list_feat` parsing until a follow-up migrates them (candidate vehicle: extending the existing TSK `tsk-2687d267`).
- The `tsk` domain's own `TaskItem` convention (tsk keeps its unpadded shape).
- Any step-10 or uniqueness enforcement of any kind.
- Changes to the shared `models/md` parsing engine.
- Changes to the `REQ-NNN`/`ACC-NNN` numbering (already 3-digit; unchanged).
- Global/user-level opencode configuration changes (nothing under `~/.config/opencode/`).

### Design Notes

The scheme (confirmed against issue #163):

- Phase: `#### Phase NNN: {title}`, alias `^Phase \d{3}: .+$`. First phase 100, step 10 (100, 110, 120, ...). The issue's example "first task in phase 2 := 200.100" is treated as a typo: phase 2 is 110, so its first task is 110.100.
- Task: `- [ ] Task NNN.MMM: {text}` (the word `Task` is kept, confirmed). The `NNN.MMM` prefix is enforced by a new feat-local `TaskItem` subclass -- the same layering `AcceptanceCriterionItem` uses to re-match `ACC-NNN: ` against the inherited `description`. First task in a phase 100, step 10.
- Deliberately NOT enforced (issue's explicit wishes, feat-156 precedent): the step-10 increments, uniqueness, and the match between a task's phase component and the enclosing phase number. Gaps and in-between numbers (e.g. `Phase 105`, `Task 100.105`) always parse, so inserting a phase or task never requires renumbering anything. Numbers are permanent; removals leave gaps.
- Backward compatibility: strict, no migration (confirmed). The ~26 of 62 legacy `Phase N`/`Task N.M` documents that currently parse will fail parsing once this ships; the existing TSK `tsk-2687d267` ("fix remaining feat README.md documents to validate against the feat schema") is the natural follow-up vehicle. This document itself uses the new numbering and stays valid both before and after the schema change (`Phase 100` matches both the old unpadded-digits alias and the new 3-digit alias, and `Task 100.100:` is free-form text under the current schema).
- The skill (the repo's second -- feat-150's `repair` skill, `.opencode/skill/repair/SKILL.md`, landed on `dev` and was merged into this branch during implementation) lives at the default project skill path `.opencode/skills/feat-numbering/SKILL.md`; its frontmatter carries the required `name` plus a third-person `description` that front-loads the trigger keywords (FEAT, Task List, Phase, specmgr), and its body mirrors the prompts' scheme description and points agents at `specmgr://feat/template`/`specmgr://feat/example`/`specmgr://feat/schema` as the authoritative references.
- Authoring constraints for this document and every fixture it updates: each list item on a single physical line (the feat-99 `single_line_text` guard) and no bare raw-HTML-shaped tokens outside code spans (the issue-70 regression).

### Related Decisions

- feat-156-qa-numbering (GitHub issue #156, done): the QA question-numbering precedent this scheme mirrors -- shape enforced by a validator, step-10 and uniqueness left to the agent, gaps allowed, numbers permanent.
- ADR e369ee2e-3353-4f92-991c-6367d76d832e: origin of the `.specmgr/feat/<id>/README.md` convention this feature refines on its Task List numbering.

### Task List

#### Phase 100: Audit and Baseline

- [x] Task 100.100: Enumerate every legacy "Phase N"/"Task N.M" surface (code docstrings, `feat/data/*`, `tests/**` fixtures, `whitelist.py`, the TSK document) and record the list in this feature's Updates.
- [x] Task 100.110: Run the side-task optionality audit: compare the create/update prompts' section optionality against `feat/models/v1/body.py` and record the findings (and any fixes) in this feature's Updates.
- [x] Task 100.120: Record the confirmed design decisions (task line shape, strict-no-migration policy, skill decision, scheme details) in this feature's Updates.

#### Phase 110: Schema

- [x] Task 110.100: Update the `Phase` alias and `_PHASE_HEADING_PATTERN` to the 3-digit shape (`^Phase \d{3}: .+$`), including the computed `number`/`title` and their error messages.
- [x] Task 110.110: Add the feat-local task-item class enforcing the `Task NNN.MMM: ` prefix and wire it into `Phase.items` with eager validation (mirroring `AcceptanceCriterionItem`).
- [x] Task 110.120: Add model tests: the phase-alias + task-prefix accept/reject matrix (gaps, in-betweens, legacy rejections with actionable messages).

#### Phase 120: Data, Prompts, Generated Artifacts

- [x] Task 120.100: Update `feat_template.md`, `feat_example.md`, and the `feat_reference.md` fixture to the new scheme (Phase 100/110, Task 100.100/110.100/110.110).
- [x] Task 120.110: Update `feat_create_instructions.md` + `feat_update_instructions.md` with the numbering-scheme description and the Task 100.110 optionality fixes.
- [x] Task 120.120: Regenerate the packaged `feat_schema.json`, `docs/feat_schema.json`, `docs/MCP.md`, `docs/api/` + `docs/GENERATED.md`.
- [x] Task 120.130: Consistency sweep: code docstrings, `whitelist.py`, the `tests/regression/test_issue_70.py` fixture (to `Phase 300`/`Task 300.100`), and the TSK document's FEAT-shape text.

#### Phase 130: Agent Skill

- [x] Task 130.100: Author `.opencode/skills/feat-numbering/SKILL.md` (name + trigger-keyword description frontmatter; body: start values, step, in-between insertion, permanence, pointers to the `specmgr://feat` resources).
- [x] Task 130.110: Add a test asserting the skill's scheme wording agrees with the prompts, template, and example (no stale "Phase N"/"Task N.M" wording).

#### Phase 140: Tests and Quality Gate

- [x] Task 140.100: Update the prompt walkthrough tests and the resource parse tests to the new shapes.
- [x] Task 140.110: Add the prompt ↔ schema optionality regression test (REQ-008/ACC-005).
- [x] Task 140.120: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov`) and fix fallout.

## Progress

### Current Status

**As of 2026-09-29**: All five phases (100-140) complete -- the full quality gate is green on the
merged tree (3616 tests passed, 0 failures; 99% coverage; `ruff format --check`, `ruff check`,
and `vulture` clean; `specmgr schema`, `specmgr mcp-docs`, and `specmgr docs` all report no
drift) -- and both rounds of post-implementation review fixes are applied: round 1 (the
`CHANGELOG.md` `[Unreleased]` entry, all seven ACC boxes ticked, the stale "first skill" wording
corrected, the AGENTS.md/conventions.md list-item enumerations extended with `FeatTaskItem`, the
template's `Related Decisions` placeholder aligned, and the TSK `tsk-2687d267` failure-set note)
and round 2 (the stale "first skill" test-module docstring corrected to name feat-150's `repair`
skill as the first, the skill test's legacy-task-number guard widened from 1-2 digit/1-2 digit to
any non-3-digit component with its three docstrings aligned, the `tests/opencode` package
docstring naming both `.opencode/skill/` and `.opencode/skills/`, the issue-70 regression
docstrings' "literal" claim scoped to the heading title with the `Phase 300` renumbering stated,
the trailing-colon/empty-description boundary case added to the `FeatTaskItem` malformed-item
subTest matrix, and the `_packaged_data` import style aligned in the optionality test), keeping
the gate green with `docs/` and `docs/coverage.svg` byte-identical. The feature is in `review`
status.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-29 17:36:54.847+02:00 - Feature closeout (author review approved, status set to `done`)

PR #165 (this feature's plan PR) was squash-merged into `dev` as `a5613e3` on 2026-09-29 and shipped in
v0.34.0 before the round-2 review fixes were committed, so the round-2 commit `d49f9e3` (the stale 'first
skill' test-module docstring correction, the widened legacy-task-number guard, the `tests/opencode` package
docstring naming both project-skill directories, the issue-70 'literal' claims scoped to the heading title,
the `FeatTaskItem` trailing-colon/empty-description boundary case, and the `_packaged_data` import-style
alignment -- cosmetic only, no behavior change) lands via this follow-up branch, cherry-picked as `cabbfd8`.
The author approved the feature for merge; frontmatter `status` set from `review` to `done` by direct edit
in this worktree (the enabled specmgr MCP server is the packaged `uvx` build with its default base directory,
not this repo, so the generic `set_status` tool was deliberately not used).

### Related PRs / Commits

- GitHub issue #163: https://github.com/dfch/biz.dfch.SpecMgr/issues/163
