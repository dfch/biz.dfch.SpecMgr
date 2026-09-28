---
classification: null
created: '2026-09-27T16:03:36.781+02:00'
id: feat-163-feat-numbering
status: progress
type: feat
updated: '2026-09-28T05:45:10.313+02:00'
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

- [ ] ACC-001: A document with `#### Phase 100: X` and items `- [ ] Task 100.100: Y` / `- [x] Task 100.110: Z` parses via `parse_feat`/`create_feat`/`validate(type="feat")`, including an in-between item (`Task 100.105: ...`).
- [ ] ACC-002: A legacy phase heading (`#### Phase 1: X`) or a task item lacking the number prefix (or carrying a legacy `Task 1.1:` number) is rejected with an actionable error naming the item's field path and 1-based line.
- [ ] ACC-003: The packaged template and example (and the byte-identical reference fixture) parse via `parse_feat`, and the resource/tool parity tests stay green.
- [ ] ACC-004: The create/update prompts contain the scheme description, and the create walkthrough test (`list_feat` -> `create_feat` against a temporary `SPECMGR_FEAT_DIR`) is green with a new-shape body.
- [ ] ACC-005: The new regression test asserting the prompts' mandatory/optional section sets equal the model's required/optional field sets is green (after the REQ-008 fixes, if any).
- [ ] ACC-006: The project skill exists at `.opencode/skills/feat-numbering/SKILL.md` with a valid `name`/`description` frontmatter, and its scheme wording agrees with the prompts, template, and example (no stale "Phase N"/"Task N.M" guidance).
- [ ] ACC-007: `specmgr schema`, `specmgr mcp-docs`, and `specmgr docs` report no drift, and the full quality gate is green: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen pytest -n auto --cov=src`.

### Scope

#### Included

- `feat/models/v1/body.py`: `Phase` alias/heading pattern + computed `number`/`title`, and the new feat-local task-item class with the `Task NNN.MMM: ` prefix + eager validation.
- `feat/data/feat_template.md`, `feat_example.md`, `feat_schema.json`, `feat_create_instructions.md`, `feat_update_instructions.md`.
- The new project skill `.opencode/skills/feat-numbering/SKILL.md` (first skill in this repo; the default project skill path is scanned automatically, so no `opencode.json` change is needed).
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
- The skill (the repo's first) lives at the default project skill path `.opencode/skills/feat-numbering/SKILL.md`; its frontmatter carries the required `name` plus a third-person `description` that front-loads the trigger keywords (FEAT, Task List, Phase, specmgr), and its body mirrors the prompts' scheme description and points agents at `specmgr://feat/template`/`specmgr://feat/example`/`specmgr://feat/schema` as the authoritative references.
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

- [ ] Task 110.100: Update the `Phase` alias and `_PHASE_HEADING_PATTERN` to the 3-digit shape (`^Phase \d{3}: .+$`), including the computed `number`/`title` and their error messages.
- [ ] Task 110.110: Add the feat-local task-item class enforcing the `Task NNN.MMM: ` prefix and wire it into `Phase.items` with eager validation (mirroring `AcceptanceCriterionItem`).
- [ ] Task 110.120: Add model tests: the phase-alias + task-prefix accept/reject matrix (gaps, in-betweens, legacy rejections with actionable messages).

#### Phase 120: Data, Prompts, Generated Artifacts

- [ ] Task 120.100: Update `feat_template.md`, `feat_example.md`, and the `feat_reference.md` fixture to the new scheme (Phase 100/110, Task 100.100/110.100/110.110).
- [ ] Task 120.110: Update `feat_create_instructions.md` + `feat_update_instructions.md` with the numbering-scheme description and the Task 100.110 optionality fixes.
- [ ] Task 120.120: Regenerate the packaged `feat_schema.json`, `docs/feat_schema.json`, `docs/MCP.md`, `docs/api/` + `docs/GENERATED.md`.
- [ ] Task 120.130: Consistency sweep: code docstrings, `whitelist.py`, the `tests/regression/test_issue_70.py` fixture (to `Phase 300`/`Task 300.100`), and the TSK document's FEAT-shape text.

#### Phase 130: Agent Skill

- [ ] Task 130.100: Author `.opencode/skills/feat-numbering/SKILL.md` (name + trigger-keyword description frontmatter; body: start values, step, in-between insertion, permanence, pointers to the `specmgr://feat` resources).
- [ ] Task 130.110: Add a test asserting the skill's scheme wording agrees with the prompts, template, and example (no stale "Phase N"/"Task N.M" wording).

#### Phase 140: Tests and Quality Gate

- [ ] Task 140.100: Update the prompt walkthrough tests and the resource parse tests to the new shapes.
- [ ] Task 140.110: Add the prompt ↔ schema optionality regression test (REQ-008/ACC-005).
- [ ] Task 140.120: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov`) and fix fallout.

## Progress

### Current Status

**As of 2026-09-28**: Phase 100 (Audit and Baseline) complete -- the legacy-surface
enumeration (Task 100.100), the prompt-vs-schema optionality audit (Task 100.110, verdict:
no discrepancies), and the confirmed design decisions (Task 100.120) are recorded in the
Updates entries below. Implementation (Phase 110, the schema change) has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-28 05:45:10.313+02:00 - Task 100.120: Confirmed design decisions restated

The four design decisions confirmed at planning are restated here for the record, without
re-litigation. (a) Task lines keep the word `Task`: the enforced line shape is
`- [ ] Task NNN.MMM: {text}` (or `- [x] Task NNN.MMM: {text}` once done), with the `NNN.MMM: `
prefix re-matched by a new feat-local task-item class in the same layering
`AcceptanceCriterionItem` uses for `ACC-NNN: `. (b) Backward compatibility is strict with NO
migration: existing `.specmgr/feat/*/README.md` documents written in the legacy shape are not
migrated by this feature and will fail `parse_feat`/`list_feat` once the schema ships until a
follow-up rewrites them; the existing TSK document `tsk-2687d267` ("Fix Remaining feat-*
README.md Documents to Validate Against the Current FEAT Schema") is the natural follow-up
vehicle. (c) A first project OpenCode skill is in scope at
`.opencode/skills/feat-numbering/SKILL.md` (the default project skill path is scanned
automatically, so no `opencode.json` change is needed). (d) Scheme details: phases carry
3-digit numbers starting at 100, step 10 (`Phase 100`, `Phase 110`, ...); task numbers are
`{phase}.{task}` with the task component also 3-digit, starting at 100, step 10; only the
number SHAPES are enforced by the schema -- the step-10 increment, number uniqueness, and the
match between a task's phase component and the enclosing phase number are authoring
conventions documented in the prompts and the skill, never validated; gaps and in-between
values (e.g. `Phase 105`, `Task 100.105`) always parse, so inserting a phase or task never
requires renumbering; a number is permanent once assigned, and removals leave gaps.

#### 2026-09-28 05:40:00.000+02:00 - Task 100.110: Prompt optionality audit against feat/models/v1/body.py

Compared the section optionality claimed by both prompt instruction files against the model's
actual required/optional field set, section by section: NO discrepancies found -- the prompts
fully agree with `feat/models/v1/body.py` on every mandatory/optional claim, and no fix is
required (this audit-only phase changes nothing). Per-section comparison. Plan -- `Overview`
mandatory prose (both agree); `Requirements` mandatory, at least one `REQ-NNN: {text}` bullet
(both agree, model `Requirements.items` carries `min_length=1`); `Acceptance Criteria`
mandatory, at least one `- [ ]/[x] ACC-NNN: {text}` checklist item (both agree,
`AcceptanceCriteria.items` carries `min_length=1`); `Scope` mandatory container, no own text,
holding two mandatory leaves `Included` and `Explicitly Out Of Scope` (both agree);
`Dependencies` optional container, no own text, holding two independently optional leaves
`Depends On` and `Blocks` (both agree, model declares `dependencies: Dependencies | None` with
both sub-fields `| None`); `Design Notes` optional (both agree); `Related Decisions` optional
(both agree); `Task List` mandatory container, no own text, at least one phase, each phase
at least one task item (both agree, `TaskList.phases` and `Phase.items` carry `min_length=1`).
Progress -- `Current Status` mandatory (both agree); `Blockers` optional (both agree);
`Updates` mandatory, optional leading HTML comment, at least one
`#### {timestamp} ( - | : ) {title}` entry, newest-first, each entry with a lead paragraph
(both agree, `Updates.updates` carries `min_length=1`, `_validate_newest_first` is enforced,
`UpdateEntry.content` is mandatory); `Decisions Made` optional as a whole, same entry shape,
at least one entry once present (both agree, `decisions_made: DecisionsMade | None` with
`DecisionsMade.decisions` carrying `min_length=1`); `Related PRs / Commits` optional (both
agree); `More Information` optional (both agree). The create prompt's step 2 todo list
(mandatory: `Overview`, `Requirements`, `Acceptance Criteria`, `Scope` both leaves, `Task
List`, `Current Status`, `Updates`; optional: `Dependencies`, `Design Notes`, `Related
Decisions`, `Blockers`, `Decisions Made`, `Related PRs / Commits`, `More Information`) and the
update prompt's step 3 partition ('always present' vs optional) state exactly the same sets.
The prompts' 'no own text' claims match all five containers (`Plan`, `Scope`, `Dependencies`,
`Task List`, `Progress` declare subsection fields only, and the model's own docstrings say
'No own text'). Two wording-level (non-optionality) observations, recorded here for
Task 120.110's review: (i) create step 1 describes `Related Decisions` as 'optional bullet
list of related ADR/DEC ids with a short description each' while the model's docstring says
'free-form cross-reference list; entries may reference either an ADR id or a dec id (or any
other decision record)' -- the prompt is narrower than the model on format, not on
optionality; (ii) create step 1 describes `Blockers` as 'optional prose/list of open
blockers' where the model says 'free-form list of open blockers' -- substantively the same.
Section order as listed in create step 1 also matches the model's field declaration order.

#### 2026-09-28 05:35:00.000+02:00 - Task 100.100: Legacy "Phase N"/"Task N.M" surface enumeration (verified baseline)

Verified by reading every file named in the planning cross-check, plus repo-wide pattern
searches for the legacy heading and item shapes and for the shape descriptions themselves
-- this is the complete baseline of legacy FEAT numbering surfaces, i.e. phase headings
`#### Phase N: {title}` with unpadded N and task items `- [ ] Task N.M: {text}`, that the
consistency sweep (Task 120.130) and the test updates (Phases 110/140) execute against.
(model code) `src/biz/dfch/specmgr/feat/models/v1/body.py`: line 283 (the
`_PHASE_HEADING_PATTERN` comment 'Matches a Phase N: {title} heading line'), line 286 (the
unpadded pattern `^Phase (?P<number>\d+): (?P<title>.+)$`), line 289 (the `@alias` value
`^Phase \d+: .+$`), lines 291-295 (the `Phase` docstring: '#### Phase N: {title}' plus
'Unpadded phase numbers (matching this very plan's own "Phase 0".."Phase 5" headings)'),
lines 303 and 319 (the `number` docstring 'e.g. 1 for #### Phase 1: X'), line 340 (the
`title` docstring 'e.g. X for #### Phase 1: X'), lines 333 and 355 (the error message
`expected heading 'Phase N: <title>'`), lines 371-383 (the `TaskList` docstring and the
`phases` field description: '#### Phase N: ...' / '#### Phase N: {title}').
(packaged data) `feat/data/feat_template.md` lines 56-58 (`#### Phase 1: Placeholder Phase`,
`- [ ] Task 1.1: A short description of one task in this phase.`); `feat/data/feat_example.md`
lines 66-74 (`Phase 0: Scaffolding`/`Task 0.1`, `Phase 1: Implementation`/`Task 1.1`/`Task
1.2`); `feat/data/feat_create_instructions.md` lines 47-50 (step 1: 'least one #### Phase N:
{title} entry (unpadded phase number, e.g. "Phase 1")'); `feat/data/feat_schema.json` lines
280, 514, 517 (generated `Phase`/`TaskList` descriptions embedding the legacy docstrings --
regenerated, not hand-edited). (fixture) `tests/feat/models/v1/data/feat_reference.md`
lines 66-74 (verified byte-identical to `feat_example.md`; must stay so). (model tests,
inline bodies) `tests/feat/models/v1/test_body.py`: line 166 (docstring '`Phase {N}:
{title}` ... unpadded number'), lines 169/174/179 (alias accept/reject matrix: 'Phase 0:
Scaffolding', 'Phase 1: Models', 'Phase 12: A: B', 'Phase 1', 'Phase 1:', 'Phase 1: ',
'Phase one: X', 'phase 1: X', 'Phases 1: X', 'Phase1: X'), lines 388/397/404/411 (`Phase 1:
Implementation`/`Task 1.1`, `Phase 2: A: B`/`Task 2.1`, bare `Phase 1`/`Task 1.1`, bad
`[z]` marker/`Task 1.1`), lines 423-426 and 629-630 (two-phase bodies `Phase 0`/`Task 0.1`
plus `Phase 1`/`Task 1.1`); `tests/feat/models/v1/test_parser.py`: `_MINIMAL_DOC` lines
86-88 (`Phase 0: Scaffolding`/`Task 0.1: Set up`), four unnamed inline docs at lines
230-232, 290-292, 342-344, 463-465 (same `Phase 0`/`Task 0.1`), line 364 (the 'Phase Zero'
negative test, whose `.replace` references the literal `#### Phase 0: Scaffolding`).
(prompt walkthrough tests) `tests/feat/prompts/test_create_feat.py` `_WALKTHROUGH_BODY`
lines 197-199 and `tests/feat/prompts/test_update_feat.py` `_INITIAL_BODY` lines 225-227
(both `Phase 0: Scaffolding`/`Task 0.1: Create branch and package skeleton`). (feat tool
tests, inline `Phase 0`/`Task 0.1: Create branch and package skeleton` bodies)
`tests/feat/tools/`: `test__io.py` `_DOC_TEMPLATE` lines 74-76; `test__paths.py`
`_DOC_TEMPLATE` lines 82-84; `test__write.py` `_BODY` lines 61-63; `test_create_feat.py`
`_MINIMAL_BODY` lines 67-69; `test_get_feat.py` `_MINIMAL_BODY` lines 65-67;
`test_integration.py` `_INITIAL_BODY` lines 100-102 and `_REVISED_BODY` lines 150-152;
`test_list_feat.py` `_MINIMAL_BODY` lines 76-78; `test_parse_feat.py` `_VALID_DOC` lines
68-70; `test_set_feat_id.py` `_MINIMAL_BODY` lines 64-66. (generic tool tests, inline feat
bodies) `tests/general/tools/`: `test_set_status.py` lines 935-937;
`test_set_classification.py` lines 421-423; `test_update.py` lines 683-685; `test_edit.py`
lines 503-505; `test_validate.py` lines 603-605; `test_delete.py` lines 387-389 (all
`Phase 0: Scaffolding`/`Task 0.1: Create branch and package skeleton`);
`test_list_references.py` lines 382-384 (unnamed inline f-string, same body);
`test_doc_cache_structural.py` lines 112-114 and `test_doc_cache_write_wiring.py` lines
227-229 (both `Phase 0: N/A`/`Task 0.1: Not a real task.`). (regression tests)
`tests/regression/test_issue_70.py` `_FEAT_BAD_BODY` lines 134-136 (`#### Phase 3:
Per-domain create_<d> tools`, `- [x] Task 3.1: Create branch and package skeleton` -- the
file Task 120.130 names, to be renumbered to `Phase 300`/`Task 300.100`);
`tests/regression/test_issue_71.py` `_FEAT_VALID_BASE_BODY` lines 140-142 (`#### Phase 1:
Placeholder Phase`, `- [ ] Task 1.1: A short description.`) -- an ADDITIONAL surface beyond
Task 120.130's named file, covered by REQ-011's 'every remaining reference' wording.
(TSK document) `docs/tsk/tsk-2687d267-...`: line 107 (the 'The required FEAT document shape'
entry -- 'mandatory ### Task List with at least one #### Phase N: {title} each holding at
least one flat checklist item - [ ] Task N.M: {text} or - [x] Task N.M: {text}' -- the
primary FEAT-shape text); line 103 (the soft-wrap defect entry's
'`REQ-NNN:`/`ACC-NNN:`/`Task N.M:`' bullet-pattern mention); line 57 (Task 20's known error
citing '#### Phase N' and the '- [ ]/-[x] Task N.M: ...' pattern); line 81 (Task 32's known
error citing '#### Phase N' and a malformed '- [x] Task 4.1: ...' quote -- the 'Task 4.1:'
wording is a quote of the feat-92 document, immutable history embedded in a shape
description). The same file's lines 53, 63, 77 quote titles/wording from OTHER documents'
own updates entries (e.g. 'Phase 6: Release (Task 6.2, PR opened)') and are NOT
FEAT-shape text. (whitelist) `whitelist.py` lines 189-205: no in-scope surface -- the feat
block's entries are bare field names (`plan`, `progress`, `overview`, `dependencies`,
`design_notes`, `related_decisions`, `task_list`, `included`, `explicitly_out_of_scope`,
`depends_on`, `phases`, `current_status`, `blockers`, `decisions_made`,
`related_prs_commits`) and the block comment's 'feat (feat-31 Phase 1)' is a cross-reference
to feat-31's own development phase (immutable history). (generated -- regenerated, not
hand-edited) `docs/feat_schema.json` lines 280, 514, 517 (mirrors the packaged schema);
`docs/api/biz.dfch.specmgr.feat.models.v1.body.md` lines 12484, 12496, 19251, 19257
(rendered `body.py` docstrings); `docs/MCP.md` verified to carry no legacy-shape reference,
so no drift is expected from regeneration. OUT OF SCOPE, deliberately not touched (excluded
per the plan's rules): prose cross-references to OTHER features' own numbering -- e.g.
'Phase 6: text in, not Path' in every domain's `tools/_cache.py` docstring, 'feat-14 Phase
8' in `qa/models/v2/`, 'feat-144 Task 7.4' in `general/tools/_references.py`,
'feat-38-39-41-43-44 Phase 4' in the `get_<d>` test comments, 'feat-27-validation Task N.M'
docstrings in `tests/models/md/`, 'feat-159-edit'/'feat-22'/'feat-144'/'feat-36' docstrings
in `tests/general/tools/`, and feat's own development-history references ('feat-31 Task
3.5', 'Phase 2, list_feat', 'feat-48-feat-id Phase 3', 'feat-107-doc-cache Phase 4-8')
across `src/biz/dfch/specmgr/feat/` and `tests/feat/`; ADRs under `docs/adr/` (no matches);
`tests/regression/test_issue_27.py` (its bodies are tsk-domain documents -- tsk keeps its
unpadded shape); `docs/sysrs/sysrs-8d752304-...appendix.md` lines 594-601, 740-746,
762-768 (the sysrs document's own `### Task List` example content, `#### Phase 1: [Phase
name]`/`Task 1.1: [description]` -- not a FEAT-shape surface); `CHANGELOG.md` line 1026 (the
`[0.14.0]` release entry describing the feat domain as shipped then -- immutable release
history); `tests/feat/resources/test_feat_example.py` line 66 ('the Phase 1 reference
fixture' -- a reference to feat-31's development phase); and the existing `.specmgr/feat/**`
documents themselves (other features' own task lists -- immutable history and, once this
feature ships, the migration target of tsk-2687d267 under the strict no-migration policy).

#### 2026-09-27 13:57:39.543Z - Created

Drafted this feature from GitHub issue #163 ("Update feat schema, template and example and suggest specific phase numbering") via the `create_feat` prompt workflow, with the explicit id `feat-163-feat-numbering`. Design decisions confirmed: task lines keep the `Task` word (`Task NNN.MMM:`), the schema goes strict with no migration of legacy documents, and a first project OpenCode skill (`.opencode/skills/feat-numbering/`) is in scope.

### Related PRs / Commits

- GitHub issue #163: https://github.com/dfch/biz.dfch.SpecMgr/issues/163
