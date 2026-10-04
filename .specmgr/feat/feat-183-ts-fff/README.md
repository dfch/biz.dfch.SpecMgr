---
classification: null
created: '2026-10-03T09:39:04.941+02:00'
id: feat-183-ts-fff
status: planning
type: feat
updated: '2026-10-04T08:03:58.473+02:00'
version: 1.0.0
---

# Feature: Reduce Agent Misreading of the "fff" Millisecond Placeholder in Timestamp Format Notation

## Plan

### Overview

GitHub issue #183 reports that agents repeatedly emit the literal characters `fff` in
timestamps instead of actual millisecond digits, because the packaged instruction files,
docstrings, and runtime error messages describe the millisecond field of the timestamp
format using the placeholder notation `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]` (established
by feat-146-date-time). Packaged templates and examples carry only concrete sample
timestamps, not the placeholder notation (re-verified at Task 120.100). The root cause of
this misunderstanding is not yet known. This feature (1) runs a short investigation into
why the `fff` placeholder notation is misread as literal text, (2) based on the findings,
selects and validates one replacement notation against a pre-defined quantitative pass
bar, and (3) rolls that replacement out consistently across every occurrence (packaged
instruction files, docstrings/field descriptions, the runtime error message, generated
JSON schemas -- both the `docs/` and packaged `data/` copies -- and `AGENTS.md`) --
without changing the underlying accepted timestamp formats, separators, or validation
regexes feat-146-date-time established, and without adding bloated explanatory prose to
address the confusion. The two ADRs that document the old notation as historical decision
records (ADR 23a14195, ADR 8c889262) are deliberately left untouched -- see Scope.

### Requirements

- REQ-001: Conduct a short root-cause investigation into why the `fff` placeholder notation is misread as literal text, by spawning several (at least three) independent, fresh-context AI agent sessions via the `task` tool, presenting each with today's unmodified instruction-file/docstring wording and a neutral prompt, and recording their literal interpretations/misreadings verbatim -- together with the neutral prompt template used -- in a `session-*.md` sibling of this README.
- REQ-002: Based on the investigation findings, select one replacement notation for the millisecond placeholder that is demonstrably less likely to be copied verbatim, validated using the same independent fresh-context `task`-tool-session method as REQ-001 against a quantitative pass bar defined up front (Task 110.100).
- REQ-003: Apply the chosen replacement notation consistently everywhere the current `fff` placeholder appears: the 12 packaged instruction files (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs` `*_create_instructions.md` and `*_update_instructions.md`), domain docstrings/field descriptions, the runtime validation error message in `models/md/frontmatter.py` (the only user-visible error string carrying the notation), the generated JSON schemas (the 6 affected types, in both the `docs/` and packaged `data/` copies), and `AGENTS.md`; packaged templates/examples are verified at rollout and updated only if an occurrence is found. The two historical ADRs that illustrate the old notation and `CHANGELOG.md`'s existing entries are explicitly excluded -- see Scope.
- REQ-004: The timestamp parsing/validation rules established by feat-146-date-time (accepted separators, millisecond digit count, regex patterns) remain unchanged; only the human-facing notation -- including the wording of runtime error messages -- changes, not the behavior that produces or matches them.
- REQ-005: The replacement must not introduce bloated explanatory text -- it stays a narrow token/notation substitution, at most a short inline comment, not new paragraphs added to every occurrence.

### Acceptance Criteria

- [ ] ACC-001: A short written summary of the root-cause investigation (REQ-001) exists, citing concrete evidence (the `session-*.md` verbatim agent-session records and/or historical examples) of why the current notation misleads, recorded in this README's `### Design Notes` > `#### Investigation Findings` > `##### Root Cause (ACC-001)` subsection.
- [ ] ACC-002: The chosen replacement notation (REQ-002) is documented with its rationale, including the pass-bar validation evidence that it reduces misreading versus the current `fff` notation, recorded in this README's `### Design Notes` > `#### Investigation Findings` > `##### Chosen Notation and Rationale (ACC-002)` subsection.
- [ ] ACC-003: Every occurrence of the old `fff` placeholder notation describing a millisecond placeholder -- in the in-scope files of Task 100.105's baseline inventory (packaged instruction files, docstrings, the runtime error message, JSON schemas, `AGENTS.md`) -- is updated to the new notation. Verified by a scoped search (not a blind repo-wide `fff` grep) that targets that baseline file set and notation-shaped patterns (e.g. `ss.fff`, `HH:mm:ss.fff`), explicitly excluding unrelated matches (e.g. the `#fff` CSS color literal in `commands/coverage_badge.py`, gitignored `build/`, `.opencode/node_modules/`) and the out-of-scope historical content named in Scope (the two ADRs, `CHANGELOG.md`, `.specmgr/feat/*/session-*.md`, `docs/tsk/*.md`) as well as this README's own deliberate references to the notation being replaced.
- [ ] ACC-004: No template, example, instruction file, docstring, or error message touched by this feature grows by more than a small, bounded amount of added prose per occurrence (the anti-bloat constraint), verified by reviewing the diff of each touched file.
- [ ] ACC-005: Every packaged template and example still parses through its own domain's parser after the notation change (no structural/content regression); the packaged instruction files are verified by diff review to carry only the notation substitution, since they are frontmatter-less prompt markdown, not domain documents.
- [ ] ACC-006: The full quality gate (ruff format/check, vulture, `pytest -n auto --cov`, pylint baseline unchanged) is green after the change, including any test that previously pinned the literal old-notation error-message text (e.g. `tests/general/tools/test_validate.py`) now updated to match the new notation.

### Scope

#### Included

- Investigating why agents misread the `fff` placeholder notation, by spawning independent, fresh-context `task`-tool agent sessions with today's unmodified wording; the verbatim interpretations and the neutral prompt template are recorded in a `session-*.md` sibling of this README.
- Taking a baseline inventory of the in-scope file set (Task 100.105) that ACC-003's scoped search targets.
- Selecting and validating a replacement notation for the millisecond placeholder against a pre-defined quantitative pass bar.
- Updating every occurrence of the `fff` placeholder across the packaged instruction files (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`), docstrings/field descriptions, the runtime error message, the generated JSON schemas (`docs/` and packaged `data/` copies), and `AGENTS.md`; verifying packaged templates/examples carry no occurrence.
- Updating the runtime validation/error-message text that currently cites the `fff` notation (wording only, not the validation logic/regex itself), and the tests that pin that exact message text.

#### Explicitly Out Of Scope

- Changing the accepted timestamp formats, separators, or validation regexes established by feat-146-date-time -- only the human-facing notation changes.
- Editing the historical ADR documents that illustrate the old notation (ADR 23a14195-339c-48af-99d2-97c9964041ae "Use ISO 8601 for all dates and times" and ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf) -- ADRs are immutable historical decision records; this feature cites them, it does not rewrite them.
- Rewriting historical narrative content that happens to contain the old notation (`CHANGELOG.md`'s existing entries, `.specmgr/feat/*/session-*.md` transcripts, `docs/tsk/*.md` historical task records) -- only currently-authoritative, forward-facing content is in scope.
- The old-notation references in this feature README itself (its Overview, Requirements, Acceptance Criteria, Scope, Design Notes, and Task List name the notation being replaced as the subject of the work) -- deliberate historical references, excluded from ACC-003's residual check.
- Adding verbose explanatory prose about timestamp formatting beyond the narrow notation substitution.
- Re-litigating the `T`-vs-space separator decision or any other feat-146-date-time decision.

### Dependencies

#### Depends On

- feat-146-date-time: establishes the `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]` notation this feature revises for clarity.

### Design Notes

#### Investigation Findings

##### Baseline Inventory (Task 100.105)

_To be completed by Task 100.105: the exact in-scope file set and occurrence count that
ACC-003's scoped search targets (planning-review expectation: 29 `src/` files with 33
occurrences, `AGENTS.md` line 945, `tests/general/tools/test_validate.py` line 895, plus
the generated `docs/api` pages and `docs/`/packaged `data/` schema copies)._

##### Root Cause (ACC-001)

_To be completed by Task 100.110, after the independent agent-session evidence from Task
100.100 has been collected._

##### Chosen Notation and Rationale (ACC-002)

_To be completed by Task 110.120, after the candidate notations from Task 110.100 have
been validated per Task 110.110._

### Related Decisions

- ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO 8601 for all dates and times"): the earlier, foundational ADR that first documented the `HH:mm:ss.fff` example this feature revises for clarity; cited for context, not edited.
- ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf ("Use full ISO 8601 date+time timestamps in all entry headings and frontmatter (accept T or space, write T)"): established the notation this feature is revising for clarity, not reversing its format/validation rules.

### Task List

#### Phase 100: Root-cause investigation

- [ ] Task 100.100: Bump this README's frontmatter `status` to `progress` (via the generic `set_status` tool, `type="feat"`), spawn at least three independent, fresh-context `task`-tool agent sessions, present each with the current, unmodified instruction-file/docstring timestamp wording and a neutral prompt, and record their literal interpretations/misreadings verbatim -- together with the neutral prompt template used -- in a `session-*.md` sibling of this README (REQ-001). -- depends on: none
- [ ] Task 100.105: Produce the baseline inventory of the in-scope file set -- every file carrying the `fff` placeholder notation as of this commit, with file:line occurrences -- and record it in this README's `#### Investigation Findings` > `##### Baseline Inventory` subsection (ACC-003's scoped search targets this set). -- depends on: none
- [ ] Task 100.110: Synthesize the collected evidence into a short root-cause summary and record it in this README's `#### Investigation Findings` > `##### Root Cause (ACC-001)` subsection (ACC-001). -- depends on: Task 100.100

#### Phase 110: Notation selection

- [ ] Task 110.100: Draft 2-3 candidate replacement notations for the millisecond placeholder and define the quantitative pass bar up front (each candidate validated in at least three fresh-context sessions of the REQ-001 method; pass = zero verbatim placeholder copies and a correct-millisecond-substitution rate at least as high as the `fff` baseline). -- depends on: Task 100.110
- [ ] Task 110.110: Validate the leading candidate(s) against the pass bar using the same independent fresh-context `task`-tool-session method as Phase 100 and record the results. -- depends on: Task 110.100
- [ ] Task 110.115: Select the one candidate that meets the pass bar (if none does, re-draft per Task 110.100's criteria). -- depends on: Task 110.110
- [ ] Task 110.120: Record the final chosen notation and its rationale, including the pass-bar evidence, in this README's `#### Investigation Findings` > `##### Chosen Notation and Rationale (ACC-002)` subsection (ACC-002). -- depends on: Task 110.115

#### Phase 120: Rollout

- [ ] Task 120.100: Verify by search that no packaged template/example carries the `fff` placeholder notation (expected: zero occurrences, concrete sample timestamps only); update any occurrence found to the new notation. -- depends on: Task 110.120
- [ ] Task 120.105: Update the 12 packaged instruction files that cite the `fff` notation -- `*_create_instructions.md` and `*_update_instructions.md` in `tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`. -- depends on: Task 110.120
- [ ] Task 120.110: Update the core sources -- the runtime error string in `models/md/frontmatter.py` (the only user-visible error text carrying the notation) and the docstring/comment mentions in `models/md/_timestamps.py`, `models/md/_ordering.py`, `general/tools/_timestamps.py`, and the 7 per-domain model files (`tsk`/`vcr`/`sysrs`/`sop`/`dec` `models/v1/body.py`, plus `feat` `models/v1/body.py` and `feat` `models/v1/frontmatter.py`). -- depends on: Task 110.120
- [ ] Task 120.115: Update the test that pins the exact literal error-message text containing the old notation (`tests/general/tools/test_validate.py`) to match the new notation. -- depends on: Task 120.110
- [ ] Task 120.120: Regenerate the affected artifacts -- `uv run --frozen specmgr schema` for the `docs/` schema copies, `uv run --frozen specmgr schema --type <d> --output-dir src/biz/dfch/specmgr/<d>/data` for the 6 packaged `data/` schema copies served by `specmgr://<d>/schema` (dec/feat/sop/sysrs/tsk/vcr are the only schema files carrying the notation), and `uv run --frozen specmgr docs` for `docs/api`/`docs/GENERATED.md` (`docs/adr/README.md` is unaffected -- no ADR changes). -- depends on: Task 120.110
- [ ] Task 120.130: Update `AGENTS.md`'s own mentions of the notation. -- depends on: Task 110.120
- [ ] Task 120.140: Scoped search (per ACC-003's pattern/exclusion rules, targeting Task 100.105's baseline file set) confirms no remaining `fff`-as-placeholder occurrences in in-scope files; full quality gate green (ACC-006); bump this README's frontmatter `status` to `review` (via the generic `set_status` tool). -- depends on: Task 120.100, Task 120.105, Task 120.115, Task 120.120, Task 120.130

#### Phase 130: Closeout

- [ ] Task 130.100: Add a `CHANGELOG.md` `[Unreleased]` entry and comment on GitHub issue #183 with the fix summary. -- depends on: Task 120.140
- [ ] Task 130.110: Final full quality gate; bump this README's frontmatter `status` to `done` (via the generic `set_status` tool). -- depends on: Task 130.100

## Progress

### Current Status

**As of 2026-10-03**: Feature just created from GitHub issue #183; planning stage only -- no
investigation or implementation has started yet.

**As of 2026-10-04**: Plan refined against the live tree per a review that found and fixed
3 errors, 3 gaps, 4 discrepancies, and 4 improvements (see the `Plan refined` Updates
entry); still planning stage.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-04T06:00:51.526Z - Plan refined (review findings applied)

Plan review against the live tree found and fixed: E1 (Task 120.105 said 6 instruction
files; 12 carry the notation), E2 (Task 120.120 now names both schema output locations --
`docs/` vs the packaged `data/` copies -- and the 6-of-12 affected types), E3 (ACC-005's
parser regression re-scoped from the frontmatter-less instruction files to
templates/examples), G1 (verbatim agent records plus the neutral prompt template now stored
in a `session-*.md` sibling of this README), G2 (new Task 100.105 baseline inventory
defines ACC-003's in-scope file set), G3 (quantitative pass bar defined up front in Task
110.100, selection in Task 110.115), D1 (templates/examples premise corrected -- they carry
concrete timestamps, not the notation; Task 120.100 is verify-and-update-if-found), D2
(notation rendering unified on `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]`), D3 (unaffected
`docs/adr/README.md` dropped from Task 120.120), D4 (the runtime error string in
`models/md/frontmatter.py` distinguished from docstring/comment-only mentions), I1
(`-- depends on:` suffixes added to every task line), I2 (this README's own old-notation
references explicitly out of scope for ACC-003), I3 (prompt template persisted with the
verbatim records), I4 (frontmatter `status` transitions tracked in the task lines).

#### 2026-10-03T07:39:04.941Z - Created

Feature created for GitHub issue #183 ("Agents misread 'fff' misunderstand in templates and
examples"). The plan covers a short root-cause investigation (spawning independent fresh-context
`task`-tool agent sessions with today's unmodified wording), selection and validation of a
replacement millisecond-placeholder notation, and a full rollout across packaged
templates/examples/create-update-instruction-files/docstrings/runtime-error-messages/schemas/AGENTS.md,
without changing the underlying timestamp validation rules established by feat-146-date-time. The
two ADRs that document the old notation as historical decision records, and other historical
narrative content (`CHANGELOG.md`, session transcripts, historical task docs), are explicitly out
of scope.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/183
