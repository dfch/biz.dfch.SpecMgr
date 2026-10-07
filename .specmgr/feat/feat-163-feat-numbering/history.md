# History: FEAT Phase/Task Numbering Scheme (Phase NNN, Task NNN.MMM)

#### 2026-09-29 09:03:06.007+02:00 - Round 2 post-implementation review fixes applied (feat-reviewer)

Applied the round-2 post-implementation review fixes (feat-reviewer over the merged branch -- the
review found no errors, only these six close-out items, per the feat-156/feat-159 round-N
precedent). (1) `tests/opencode/test_skill_feat_numbering.py`: corrected the stale module-docstring
claim that feat-numbering is the repo's first OpenCode skill -- it is the repo's second project
skill, with feat-150's `repair` skill (`.opencode/skill/repair/SKILL.md`, landed on `dev` and
merged into this branch during implementation) named as the first; only the sentence containing
the stale claim was reworded, the remaining docstring sentences are unchanged. (2) Same file:
replaced the under-sensitive legacy-task-number guard (`(?<!\d)Task \d{1,2}\.\d{1,2}(?!\d)`, which
caught only 1-2 digit/1-2 digit numbers and let mixed-width `Task 99.100`/`Task 100.10` and
over-width `Task 1000.100` slip through) with a two-capturing-group pattern
`(?<!\d)Task (\d+)\.(\d+)(?!\d)` plus a module-level `_legacy_task_numbers(text)` helper returning
every `Task X.Y` token whose components are not both exactly 3 digits -- the guard now flags any
width drift (`Task 0.1`, `Task 1.1`, `Task 99.100`, `Task 100.10`, `Task 1000.100`) while the
skill body's own 3-digit examples (`Task 100.100`, `Task 100.110`, `Task 100.105`, `Task 110.100`,
`Task 110.110`) and the letter placeholder `Task NNN.MMM` stay clean; the test now asserts the
helper's list is empty (a better failure message than `assertIsNone`), and the three docstrings
that overclaimed the old 1-2 digit sensitivity (module, class, test) now state the actual one --
the `_LEGACY_PHASE_PATTERN` guard and its docstrings were already correct and are untouched. (3)
`tests/opencode/__init__.py`: the package docstring now names both project-skill locations the
repo carries -- `.opencode/skill/` (singular, feat-150's `repair`) and `.opencode/skills/`
(plural, feat-163's `feat-numbering`) -- matching opencode's `{skill,skills}/**/SKILL.md` project
config-dir scan. (4) `tests/regression/test_issue_70.py`: the module-docstring bullet, the feat
class docstring, and the section-divider comment above the fixture no longer overclaim that the
whole renumbered heading is "the literal issue #70 reproduction" -- "literal" now applies only to
the heading's title wording (`Per-domain create_<d> tools`), and all three state explicitly that
the phase number is `Phase 300`, renumbered from the issue's `Phase 3` by the feat-163 numbering
scheme; the historical quote of the issue's own reported heading and the `feat-67-70-71 Phase 3
(REQ-003/ACC-002)` self-reference are untouched. (5) `tests/feat/models/v1/test_body.py`: added the trailing-colon/empty-description
boundary entry `Task 100.100:` to `TestFeatTaskItem.test_malformed_item_raises_actionable_assertion_error_on_access`'s
subTest matrix -- the `Task NNN.MMM:` prefix is present but the description after the colon is
empty, and the loop's existing expected-message format handles it unchanged (7 subtests now, all
green). (6) `tests/feat/prompts/test_prompt_schema_optionality.py`: switched the
`read_packaged_text` import to the suite-dominant module-import form
(`from biz.dfch.specmgr.general.tools import _packaged_data`) and updated both call sites to
`_packaged_data.read_packaged_text(...)`, matching the three neighboring test files. Gate stays
green on the merged tree: `ruff format --check` (1741 files already formatted), `ruff check`
(all checks passed), `vulture src/ whitelist.py --min-confidence 60` (exit 0, no findings), and
`pytest -n auto --cov=src --cov-report=` (3616 passed, 0 failures, in 60.61s; coverage 99% --
11046 statements, 122 missed), with the drift checks all no-ops: `specmgr docs`, `specmgr
mcp-docs`, and `specmgr schema` (all 12 artifacts reported unchanged) leave `docs/` byte-identical
(`git status` shows only the five touched test files and this plan document).



#### 2026-09-29 06:32:35.789+02:00 - Round 1 post-implementation review fixes applied (feat-reviewer)

Applied the round-1 post-implementation review fixes (feat-reviewer over the merged branch -- the
review found no errors, only these close-out items, per the feat-156/feat-159 round-N precedent).
Added the missing `CHANGELOG.md` `[Unreleased]` entry in the file's existing style: an
`### Added` pair (the fixed, permanent FEAT phase/task numbering scheme -- 3-digit zero-padded
`Phase` headings starting at 100, step 10, `Task NNN.MMM: ` checklist prefixes enforced by the
new feat-local `FeatTaskItem`, shape-only enforcement with in-between insertion -- and the
`feat-numbering` project OpenCode Skill) and a `### Changed` triple (the **BREAKING** consequence
for legacy unpadded `Phase N`/`Task N.M` documents, which now fail `parse_feat`/`list_feat`/
`validate(type="feat")` until the follow-up migration renumbers them, tracked by TSK
`tsk-2687d267`; the create/update prompt instruction updates -- the canonical scheme description
plus the two wording alignments the REQ-008 optionality audit recommended, which confirmed zero
optionality discrepancies -- with the new prompt↔schema optionality regression test; and the TSK
document's normative FEAT-shape entry updated to the new scheme), all referencing GitHub issue
#163 the way the existing entries reference theirs. Ticked all seven ACC checkboxes
(ACC-001..ACC-007) per the reviewed-feature convention (feat-110-truncate-validation-errors,
feat-123-test-gap-cache, and feat-132-prb-update all carry fully-ticked ACCs at `status:
review`). Corrected the two stale forward-looking "first skill" claims (the Scope bullet and the
Design Notes bullet) -- feat-150's `repair` skill, `.opencode/skill/repair/SKILL.md`, landed on
`dev` and was merged into this branch during implementation, so this is the repo's second project
skill; the dated `### Updates` entries were left as written at the time. Extended the AGENTS.md
feat-99 paragraph and the conventions.md "Markdown Authoring (List Items Must Not Soft-Wrap)"
enumeration with `feat.FeatTaskItem.task_description`, with the same transitive-coverage
treatment as the existing `feat.AcceptanceCriterionItem.criterion_description` parenthetical
(covered transitively via `TaskItem.description`'s `single_line_text` guard, no direct wiring
needed). Aligned the packaged template's `### Related Decisions` placeholder bullet with
`RelatedDecisions`' docstring and the create prompt's wording (the phase-100 optionality audit
flagged the narrower "bullet list of related ADR or DEC ids" phrasing; phase 120 fixed it in the
create prompt, the template still carried it). And appended one sentence to the TSK document
`tsk-2687d267`'s header comment noting that, once feat-163 (GitHub issue #163) merges, its
failure set grows by the ~26 previously-valid legacy `Phase N`/`Task N.M` documents (the strict
no-migration policy), so the follow-up must renumber them to the new `Phase NNN`/`Task NNN.MMM`
scheme. Gate on the merged tree stays green: `ruff format --check` (1741 files), `ruff check`,
`vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto --cov=src` (3616 passed,
0 failures, 99% coverage), `specmgr coverage-badge` byte-identical, and `specmgr
docs`/`mcp-docs`/`schema` leave every generated `docs/` artifact unchanged (only this round's
intentional TSK source edit shows in `git status`); both touched documents re-verified to parse
(`validate(type="feat")` and `validate(type="tsk")` with `full=True`, both printing exactly
`True`).



#### 2026-09-28 18:50:40.838+02:00 - Merged upstream dev (feat-150 repair command + v0.33.0) into the feature branch

After the implementation was complete and the feature status had been set to review, upstream dev moved ahead with
feat-150's MCP-native repair command + get_* parse-failure error channel (issue #155) and the v0.33.0 release bump,
adding two test files, so the PR's CI docs-drift check (which runs on the branch merged with dev) regenerated
docs/GENERATED.md with 368 test files against the 366 committed on the branch. Merged origin/dev into
feat-163-feat-numbering (clean, no conflicts); the full gate on the merged tree is green -- ruff format/check and
vulture clean, pytest -n auto 3616 passed (3533 from this feature plus the 83 new feat-150 tests, no interaction
breakage), specmgr docs/mcp-docs/schema all idempotent with only docs/GENERATED.md changing (test count 366 -> 368),
and docs/coverage.svg byte-identical at 99% coverage.



#### 2026-09-28 12:49:46.129+02:00 - Phase 140 (Tests and Quality Gate): fixtures moved, optionality test, gate green

Moved the last two legacy-shape surfaces in the repo to the new scheme (Task 140.100): the
`tests/feat/prompts/test_create_feat.py` `_WALKTHROUGH_BODY` and the
`tests/feat/prompts/test_update_feat.py` `_INITIAL_BODY` fixtures now read `#### Phase 100:
Scaffolding` / `- [x] Task 100.100: Create branch and package skeleton` (nothing else in either
body changed), and both walkthrough tests are green with no line-offset fix needed -- the update
walkthrough derives its splice coordinates from `raw_lines.index("Short description.")` rather
than hardcoding them, and the fixture kept its line count. The resource parse tests
(`tests/feat/resources/test_feat_template.py`/`test_feat_example.py` plus the
`get_feat_template`/`get_feat_example` tool tests) were re-run and confirmed still green against
the new-shape packaged data. New regression test (Task 140.110, REQ-008/ACC-005)
`tests/feat/prompts/test_prompt_schema_optionality.py` (2 tests) pins the mandatory/optional
section sets claimed by both packaged prompt instruction files against the model's own
required/optional field sets: the model side is derived programmatically from `Plan.model_fields`
and `Progress.model_fields` via each Pydantic v2 field's `is_required()` (7 required --
`overview`, `requirements`, `acceptance_criteria`, `scope`, `task_list`, `current_status`,
`updates`; 7 optional -- `dependencies`, `design_notes`, `related_decisions`, `blockers`,
`decisions_made`, `related_prs_commits`, `more_information`), and the prompt side parses create
step 2's "one entry per: the mandatory ..." sentence and update step 3's "the sections -- the
mandatory ... (always present) ..." sentence with two narrow, well-commented regexes each (one
per list), maps every backtick-quoted display name through an explicit 18-entry table (the 14 H3
container sections plus the 4 H4 leaves, each leaf to its parent container's field, since the
prompts' lists name the H3 sections and a leaf and its container share optionality), and asserts,
for both prompts, that the parsed mandatory set equals the model's required set, the parsed
optional set equals the model's optional set, and the two sets partition the 14 container
sections with nothing missing and nothing extra; an unknown display name or a drifted anchor
sentence is a hard failure (a four-case mutation check -- an optionality swap in each prompt, an
invented section name, and a reworded anchor sentence -- confirmed the test fails loudly on all
four). Full quality gate (Task 140.120): `ruff format --check` (1728 files), `ruff check`, and
`vulture src/ whitelist.py --min-confidence 60` (exit 0, no findings) are clean, and `pytest -n
auto --cov=src` is fully green -- 3533 tests passed in 62.24s with 0 failures (up from the 3531
that failed only the two walkthrough tests), total coverage 99% (10860 statements, 122 missed),
with `specmgr coverage-badge` regenerating a byte-identical `docs/coverage.svg`; the drift checks
are all clean: `specmgr schema` (both runs exit 0, all 12 artifacts unchanged), `specmgr
mcp-docs` (`docs/MCP.md` byte-identical), and `specmgr docs` (only `docs/GENERATED.md` changed,
test-file count 365 -> 366, and a second run left `docs/` byte-identical per before/after md5
snapshot).


#### 2026-09-28 11:52:18.732+02:00 - Phase 130 (Agent Skill): feat-numbering skill and ACC-006 consistency test

Created the repo's first project OpenCode skill at `.opencode/skills/feat-numbering/SKILL.md` (the
default project skill path is scanned automatically, so no `opencode.json` was created or changed
and no other `.opencode/` file touched). Its YAML frontmatter carries exactly the two spec-required
keys: `name: feat-numbering` (matching the folder name, lowercase, at most 64 characters) and a
single-sentence, third-person `description` front-loading the four plan-named trigger keywords
FEAT, Task List, Phase, and specmgr. The body teaches the scheme by mirroring the prompts'
canonical "Task List numbering scheme:" paragraph verbatim in its `## The scheme` section (3-digit
zero-padded phase numbers starting at 100, step 10; `Task NNN.MMM:` task lines whose component
starts at 100, step 10, within its phase; shape-only enforcement -- the schema enforces only
`#### Phase NNN: {title}` and the `Task NNN.MMM: ` prefix, not the step-10 increments, not
uniqueness, not the task-to-phase match; in-between insertion such as `Phase 105`/`Task 100.105`
so existing numbers never renumber; numbers permanent once assigned, removals leave gaps), then
directs agents to fetch `specmgr://feat/template`, `specmgr://feat/example`, and
`specmgr://feat/schema` rather than rely on memory, and gives the practical rules: a new phase
starts its own task series at 100 (the first task of `Phase 110` is `Task 110.100`), pick the
number between its neighbours and insert the one new line (never renumber existing lines), and
legacy documents written before the scheme are handled by the follow-up migration TSK
tsk-2687d267 -- the body contains no legacy shape description at all (no short-number examples,
no unpadded wording). New test package `tests/opencode/` (Task 130.110; 12 tests in
`test_skill_feat_numbering.py`, AGPL header mirrored from the repo standard in both files):
frontmatter validity (exactly two keys; folder-matching lowercase name; non-empty third-person
description; all four trigger keywords, matched case-insensitively by deliberate choice), scheme
agreement (the canonical paragraph extracted from BOTH packaged prompt instruction files is equal
and occurs verbatim in the whitespace-normalized skill body, plus the key constants "starting at
100", "step 10", "3-digit", `Phase 105`, `Task 100.105`, "permanent", and "The schema enforces
only the number SHAPES"), the three `specmgr://feat/*` resource pointers, cross-agreement with the
packaged data (every concrete example named in the skill -- `Phase 100`/`Task 100.100` in the
template and the example, `Phase 110`/`Task 110.100`/`Task 110.110` in the example -- actually
occurs there), and stale-wording regexes (no "unpadded" anywhere, no 1-2 digit phase number, no
1-2 digit/1-2 digit task number, with negative lookarounds keeping the 3-digit examples clean).
Gate: `ruff format --check` (1727 files), `ruff check`, and `vulture` are green; the new package's
12 tests pass under `unittest discover -s tests/opencode`; `specmgr schema` (both runs, all
unchanged) and `specmgr mcp-docs` (`docs/MCP.md` byte-identical) report no drift; `specmgr docs`
changed `docs/GENERATED.md` only (test-file count 364 -> 365) and a second run left `docs/`
byte-identical (before/after md5 snapshot). The full suite (3531 tests) fails ONLY the two Phase
140 walkthrough tests, for the legacy-walkthrough-body reason.


#### 2026-09-28 10:33:54.474+02:00 - Phase 120 (Data, Prompts, Generated Artifacts): data, prompts, fixtures

Updated the packaged data to the new scheme: `feat_template.md` (`Phase 1`/`Task 1.1` to `Phase 100`/
`Task 100.100`) and `feat_example.md` (`Phase 0`/`Phase 1` to `Phase 100`/`Phase 110`, `Task 0.1`/
`Task 1.1`/`Task 1.2` to `Task 100.100`/`Task 110.100`/`Task 110.110`) -- no frontmatter or other line
changed -- both still parsing via `parse_feat`/`validate`, and `feat_example.md` re-verified
byte-identical (`cmp`) to the `feat_reference.md` fixture already moved in Phase 110. Both prompt
instruction files now carry the canonical Task List numbering-scheme wording: phases are 3-digit
zero-padded starting at 100, step 10, task lines are `- [ ] Task NNN.MMM: {text}` (or `- [x] ...` once
done) with `MMM` a 3-digit zero-padded number starting at 100, step 10, within its phase, the schema
enforces only the number SHAPES (`#### Phase NNN: {title}` and the `Task NNN.MMM: ` prefix) and not
the step-10 increments, not uniqueness, not the task-to-phase match, and gaps are deliberate with
in-between insertion (e.g. `Phase 105`, `Task 100.105`) so existing numbers never renumber and a
number is permanent once assigned. In the create prompt, step 1's `### Task List` bullet was rewritten
to name the new shapes with the scheme paragraph following it; in the update prompt, step 4's
line-range guidance gained the same paragraph plus the note that adding a phase or task is a
line-range insert of one new numbered line, never a renumber. The two Task 100.110 wording-level fixes
were applied (the Phase 100.110 optionality audit found NO optionality discrepancies): create step 1's
`Related Decisions` bullet now reads 'optional free-form cross-reference list; entries may reference
an ADR id, a dec id, or any other decision record' and its `Blockers` bullet 'optional free-form list
of open blockers', both matching the model's docstrings; every static substring the prompt tests assert
against the instruction text was preserved verbatim (only the two walkthrough BODY fixtures in
`tests/feat/prompts/` remain legacy-shape, off-limits until Phase 140). All four artifacts were
regenerated: `specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data` (packaged
`feat_schema.json` rewritten, second run exit 0), `specmgr schema` (only `docs/feat_schema.json`
changed, second run exit 0), `specmgr mcp-docs` (`docs/MCP.md` byte-identical -- the instruction files
are runtime-loaded, not embedded in registration) and `specmgr docs` (only
`docs/api/biz.dfch.specmgr.feat.models.v1.body.md` changed -- Phase 110's docstring edits;
`docs/GENERATED.md` byte-identical, no test files added this phase); re-running every generator leaves
`docs/` unchanged. Consistency sweep: no legacy FEAT-shape prose remained in `src/` after Phase 110
(re-grep clean; the `tools/_cache.py` 'Phase 6' and feat-14/feat-144 references are immutable history
cross-references to other features' own numbering); `whitelist.py`'s feat block re-verified as a no-op
(bare field names plus the immutable 'feat-31 Phase 1' comment, `vulture` exit 0);
`tests/regression/test_issue_70.py`'s `_FEAT_BAD_BODY` renumbered to `Phase 300`/`Task 300.100` with
the title kept verbatim (the raw-HTML `<d>` token is the point of the regression) and the docstring
sentences describing the fixture's current shape re-pointed to `Phase 300`, while the historical quote
of the issue's own literal reported heading stays; `tests/regression/test_issue_71.py`'s
`_FEAT_VALID_BASE_BODY` renumbered to `Phase 100`/`Task 100.100` with the `_MALFORMED_HEADING`
'(Phase 1)' literal (the issue-#71 repro, asserted verbatim) and every feat-67-70-71 self-reference
untouched; the 18 inline test fixtures across `tests/feat/tools/` (9 files, 10 bodies --
`test_integration.py` carries two) and `tests/general/tools/` (9 files -- `Phase 0: N/A`/
`Task 0.1: Not a real task.` in the two doc-cache files, 8-space indentation in
`test_list_references.py` preserved) all moved to `Phase 100`/`Task 100.100` with every
title/description verbatim; and the TSK document `tsk-2687d267`'s single 'The required FEAT document
shape' entry now mandates `#### Phase NNN: {title}` (3-digit; first phase 100, step 10 by authoring
convention, shape-only enforcement, in-between insertion allowed) with `- [ ]/- [x] Task NNN.MMM:
{text}` items -- still one prose paragraph, every other entry byte-identical, frontmatter `updated`
bumped, and the full document's `validate` (`type="tsk"`, `full=True`) printing exactly `True`. Gate:
`ruff format --check` (1724 files), `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and
the feat (253 tests), general (403), and regression (21) suites are all green; the full suite (3519
tests) fails ONLY the two Phase 140 walkthrough tests, both for the legacy-walkthrough-body reason.


#### 2026-09-28 08:35:13.728+02:00 - Phase 110 (Schema): 3-digit Phase/Task shapes, FeatTaskItem, eager validation

Updated `feat/models/v1/body.py` to the new numbering scheme: `Phase`'s `@alias` is now `^Phase \d{3}: .+$` and
`_PHASE_HEADING_PATTERN` is `^Phase (?P<number>\d{3}): (?P<title>.+)$`, with the computed `number`/`title` kept as
an `int`/`str` derived from the heading (docstring examples re-pointed to `#### Phase 100: X` and the assertion
messages now read `expected heading 'Phase NNN: <title>'`); a new feat-local `FeatTaskItem` (declared in `body.py`,
exported from `feat.models.v1`) subclasses `tsk`'s own `TaskItem` and adds exactly one computed field,
`task_description`, re-matching `_FEAT_TASK_ITEM_PATTERN` (`^Task \d{3}\.\d{3}: (?P<description>.+)$`) against the
inherited, checkbox-stripped `description` with the same actionable message shape as
`AcceptanceCriterionItem.criterion_description` (`expected 'Task NNN.MMM: <description>'`, plus the item's own
field path and 1-based line); `Phase.items` is now `list[FeatTaskItem]` (min_length=1, field description naming
the new `- [ ] Task NNN.MMM: ...` shape), and `Phase._validate_items_eagerly` now forces both `.checked` and
`.task_description` for every item, so a malformed task fails at parse time rather than lazily. Only the shapes
are enforced: the step-10 increment, uniqueness, and the cross-check between a task's phase component and the
enclosing `Phase.number` stay authoring conventions, so `Phase 105`, `Task 100.105`, and `Task 999.999` parse and
no assigned number is ever renumbered. All legacy-shape prose in `body.py` was re-pointed per the Phase 100
enumeration (the module docstring's `TaskItem`-reuse sentence, the pattern comment, the `Phase` class docstring,
both computed fields' docstrings/messages, and the `TaskList` docstring plus `phases` field description). Tests
(Task 110.120): `test_body.py`'s alias matrix was redone for the 3-digit shape (accepts `Phase 100: X`,
`Phase 105: A: B`, `Phase 999: X`; rejects title-less headings, legacy `Phase 0`/`Phase 1`/`Phase 12`, 4-digit
`Phase 1000`, non-numeric `Phase one: X`, lowercase `phase 100: X`, `Phases 100: X`, `Phase100: X`); new
`TestFeatTaskItem` (unit-level accept/reject matrix with the exact actionable message for `Task 1.1`,
`Task 100.10`, `Task 1000.100`, `Task 100-100`, a missing colon, and a bare unprefixed item, plus the soft-wrap
guard and checked/unchecked parsing) and `TestPhaseTaskItemEagerValidation` (Phase-level eager acceptance of
`Task 100.100`/`Task 100.110`/`Task 105.105`/`Task 999.999` -- including a task whose phase component mismatches
its enclosing phase -- and eager rejection of every malformed shape above); `TestPhaseComputedFields`/
`TestTaskListComposite`/`_minimal_plan` moved to the new shapes (including a gap/in-between phase test,
`Phase 100`/`Phase 105`/`Phase 120`); `test_parser.py`'s `_MINIMAL_DOC` and the four inline docs were re-pointed
(`Phase 0`/`Task 0.1` to `Phase 100`/`Task 100.100`), the "Phase Zero" negative test's `.replace` source literal
updated, and new whole-document tests added: in-between numbers parse, a task phase component mismatched against
the enclosing phase number still parses (REQ-004), legacy unpadded phase headings raise the engine `AssertionError`
naming the `^Phase \d{3}: .+$` alias, and legacy/malformed task numbers raise an actionable `ValidationError`
naming `FeatTaskItem`, a 1-based line, and the expected shape. Gate outcome: `ruff format --check`, `ruff check`,
and `vulture src/ whitelist.py --min-confidence 60` are all green (no new whitelist entry needed -- `FeatTaskItem`
and `task_description` are referenced by the eager validator and the `Phase.items` annotation); the feat model
tests (`tests/feat/models/v1`) are fully green at 122 tests; the full suite shows 98 unique failing tests, of
which 97 lie inside the expected-red fixture list and every one of them was verified to fail for the legacy-shape
reason (a phase-alias `expected list[Phase]` assertion or a task-prefix `expected 'Task NNN.MMM: <description>'`
assertion on the still-legacy packaged-data, tool, prompt, general-tool, and regression fixture bodies); the
single failing test outside that list, `tests.feat.resources.test_feat_schema.TestFeatSchemaResource.
test_matches_fresh_generate_feat_schema_output`, is the in-suite mirror of the pre-approved schema drift -- the
stale packaged `feat/data/feat_schema.json` still carries the old `TaskItem` `$defs` while a fresh
`generate_feat_schema()` now emits `FeatTaskItem`, and regenerating it is Task 120.120's job; the drift checks
confirm it: `specmgr schema --type feat` exits 1 with `docs/feat_schema.json` rewritten (reverted afterwards) and
`specmgr docs` rewrites only `docs/api/biz.dfch.specmgr.feat.models.v1.body.md` (also reverted; `docs/GENERATED.md`
unchanged), i.e. the generated-doc drift is present and limited to `feat`. `tests/regression/test_issue_70`'s feat
class stays green (not in the failing set) because its raw-HTML token check fires at tokenization time, before any
phase alias matching. One boundary call, flagged for the orchestrator: the test-local reference fixture
`tests/feat/models/v1/data/feat_reference.md` (Task 120.100's) was moved to the new scheme in this phase --
`Phase 0`/`Phase 1` to `Phase 100`/`Phase 110` and `Task 0.1`/`Task 1.1`/`Task 1.2` to `Task 100.100`/
`Task 110.100`/`Task 110.110`, the plan's exact target mapping -- because the phase gate requires the feat model
tests fully green and the reference round-trip tests read that fixture; Task 120.100 now only has to bring the
packaged `feat_example.md`/`feat_template.md` to the same state and re-verify the byte-identity.


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
