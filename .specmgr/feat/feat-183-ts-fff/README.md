---
classification: null
created: '2026-10-03T09:39:04.941+02:00'
id: feat-183-ts-fff
status: planning
type: feat
updated: '2026-10-04T06:15:14.431+02:00'
version: 1.0.0
---

# Feature: Reduce Agent Misreading of the "fff" Millisecond Placeholder in Timestamp Format Notation

## Plan

### Overview

GitHub issue #183 reports that agents repeatedly emit the literal characters `fff` in timestamps
instead of actual millisecond digits, because every packaged template, example, instruction file,
and docstring describes the millisecond field of the timestamp format using the placeholder notation
`yyyy-MM-ddTHH:mm:ss.fff[Z|+hh:mm]` (established by feat-146-date-time). The root cause of this
misunderstanding is not yet known. This feature (1) runs a short investigation into why the `fff`
placeholder notation is misread as literal text, (2) based on the findings, selects and validates
one replacement notation that is demonstrably less likely to be copied verbatim, and (3) rolls that
replacement out consistently across every occurrence (packaged templates, examples, packaged
create/update instruction files, docstrings/field descriptions, runtime validation/error-message
text, generated JSON schemas, and `AGENTS.md`) -- without changing the underlying accepted
timestamp formats, separators, or validation regexes feat-146-date-time established, and without
adding bloated explanatory prose to address the confusion. The two ADRs that document the old
notation as historical decision records (ADR 23a14195, ADR 8c889262) are deliberately left
untouched -- see Scope.

### Requirements

- REQ-001: Conduct a short root-cause investigation into why the `fff` placeholder notation is misread as literal text, by spawning several (at least three) independent, fresh-context AI agent sessions via the `task` tool, presenting each with today's unmodified template/example wording and a neutral prompt, and recording their literal interpretations/misreadings verbatim.
- REQ-002: Based on the investigation findings, select one replacement notation for the millisecond placeholder that is demonstrably less likely to be copied verbatim, validated using the same independent fresh-context `task`-tool-session method as REQ-001.
- REQ-003: Apply the chosen replacement notation consistently everywhere the current `fff` placeholder appears: packaged templates, packaged examples, packaged create/update instruction files (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`), domain docstrings/field descriptions, runtime validation/error-message text (e.g. `models/md/frontmatter.py`, `general/tools/_timestamps.py`, `models/md/_timestamps.py`, `models/md/_ordering.py`), generated JSON schemas, and `AGENTS.md`. The two historical ADRs that illustrate the old notation and `CHANGELOG.md`'s existing entries are explicitly excluded -- see Scope.
- REQ-004: The timestamp parsing/validation rules established by feat-146-date-time (accepted separators, millisecond digit count, regex patterns) remain unchanged; only the human-facing notation -- including the wording of runtime error messages -- changes, not the behavior that produces or matches them.
- REQ-005: The replacement must not introduce bloated explanatory text -- it stays a narrow token/notation substitution, at most a short inline comment, not new paragraphs added to every occurrence.

### Acceptance Criteria

- [ ] ACC-001: A short written summary of the root-cause investigation (REQ-001) exists, citing concrete evidence (agent-session transcripts and/or historical examples) of why the current notation misleads, recorded in this README's `### Investigation Findings` subsection (under Design Notes).
- [ ] ACC-002: The chosen replacement notation (REQ-002) is documented with its rationale, including the validation evidence that it reduces misreading versus the current `fff` notation, recorded in the same `### Investigation Findings` subsection.
- [ ] ACC-003: Every occurrence of the old `fff` placeholder notation describing a millisecond placeholder -- in packaged templates/examples/create-update-instruction-files/docstrings/runtime error messages/JSON schemas/AGENTS.md -- is updated to the new notation. Verified by a scoped search (not a blind repo-wide `fff` grep) that targets the in-scope file set and notation-shaped patterns (e.g. `ss.fff`, `HH:mm:ss.fff`), explicitly excluding unrelated matches (e.g. the `#fff` CSS color literal in `commands/coverage_badge.py`) and the out-of-scope historical content named in Scope (the two ADRs, `CHANGELOG.md`, `.specmgr/feat/*/session-*.md`, `docs/tsk/*.md`).
- [ ] ACC-004: No template, example, instruction file, docstring, or error message touched by this feature grows by more than a small, bounded amount of added prose per occurrence (the anti-bloat constraint), verified by reviewing the diff of each touched file.
- [ ] ACC-005: Every packaged template/example/instruction file still parses through its own domain's parser after the notation change (no structural/content regression).
- [ ] ACC-006: The full quality gate (ruff format/check, vulture, `pytest -n auto --cov`, pylint baseline unchanged) is green after the change, including any test that previously pinned the literal old-notation error-message text (e.g. `tests/general/tools/test_validate.py`) now updated to match the new notation.

### Scope

#### Included

- Investigating why agents misread the `fff` placeholder notation, by spawning independent, fresh-context `task`-tool agent sessions with today's unmodified wording.
- Selecting and validating a replacement notation for the millisecond placeholder.
- Updating every occurrence of the `fff` placeholder across packaged templates, examples, the packaged create/update instruction files (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`), docstrings/field descriptions, generated JSON schemas, and `AGENTS.md`.
- Updating the runtime validation/error-message text that currently cites the `fff` notation (wording only, not the validation logic/regex itself), and the tests that pin that exact message text.

#### Explicitly Out Of Scope

- Changing the accepted timestamp formats, separators, or validation regexes established by feat-146-date-time -- only the human-facing notation changes.
- Editing the historical ADR documents that illustrate the old notation (ADR 23a14195-339c-48af-99d2-97c9964041ae "Use ISO 8601 for all dates and times" and ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf) -- ADRs are immutable historical decision records; this feature cites them, it does not rewrite them.
- Rewriting historical narrative content that happens to contain the old notation (`CHANGELOG.md`'s existing entries, `.specmgr/feat/*/session-*.md` transcripts, `docs/tsk/*.md` historical task records) -- only currently-authoritative, forward-facing content is in scope.
- Adding verbose explanatory prose about timestamp formatting beyond the narrow notation substitution.
- Re-litigating the `T`-vs-space separator decision or any other feat-146-date-time decision.

### Dependencies

#### Depends On

- feat-146-date-time: establishes the `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]` notation this feature revises for clarity.

### Design Notes

#### Investigation Findings

##### Root Cause (ACC-001)

_To be completed by Task 100.110, after the independent agent-session evidence from Task 100.100 has been collected._

##### Chosen Notation and Rationale (ACC-002)

_To be completed by Task 110.120, after the candidate notations from Task 110.100 have been validated per Task 110.110._

### Related Decisions

- ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO 8601 for all dates and times"): the earlier, foundational ADR that first documented the `HH:mm:ss.fff` example this feature revises for clarity; cited for context, not edited.
- ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf ("Use full ISO 8601 date+time timestamps in all entry headings and frontmatter (accept T or space, write T)"): established the notation this feature is revising for clarity, not reversing its format/validation rules.

### Task List

#### Phase 100: Root-cause investigation

- [ ] Task 100.100: Spawn at least three independent, fresh-context `task`-tool agent sessions, present each with the current, unmodified template/example timestamp wording and a neutral prompt, and record their literal interpretations/misreadings verbatim.
- [ ] Task 100.110: Synthesize the collected evidence into a short root-cause summary and record it in this README's `### Investigation Findings` > `Root Cause` subsection (ACC-001).

#### Phase 110: Notation selection

- [ ] Task 110.100: Draft 2-3 candidate replacement notations for the millisecond placeholder.
- [ ] Task 110.110: Validate the leading candidate(s) using the same independent fresh-context `task`-tool-session method as Phase 100 and record the results.
- [ ] Task 110.120: Record the final chosen notation and its rationale in this README's `### Investigation Findings` > `Chosen Notation and Rationale` subsection (ACC-002).

#### Phase 120: Rollout

- [ ] Task 120.100: Update all packaged template/example frontmatter and entry-heading format mentions to the new notation.
- [ ] Task 120.105: Update the 6 packaged create/update instruction markdown files that cite the `fff` notation (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs` `*_create_instructions.md` and `*_update_instructions.md`).
- [ ] Task 120.110: Update domain docstrings/field descriptions and runtime validation/error-message text that cite the `fff` notation (`models/md/frontmatter.py`, `general/tools/_timestamps.py`, `models/md/_timestamps.py`, `models/md/_ordering.py`, and any per-domain `body.py`/`frontmatter.py` docstrings).
- [ ] Task 120.115: Update any test that pins the exact literal error-message text containing the old notation (e.g. `tests/general/tools/test_validate.py`) to match the new notation.
- [ ] Task 120.120: Regenerate the twelve `*_schema.json` files (`specmgr schema`) and `docs/api`/`docs/GENERATED.md`/`docs/adr/README.md` as needed.
- [ ] Task 120.130: Update `AGENTS.md`'s own mentions of the notation.
- [ ] Task 120.140: Scoped search (per ACC-003's pattern/exclusion rules, not a blind repo-wide `fff` grep) confirms no remaining `fff`-as-placeholder occurrences in in-scope files; full quality gate green (ACC-006).

#### Phase 130: Closeout

- [ ] Task 130.100: Add a `CHANGELOG.md` `[Unreleased]` entry and comment on GitHub issue #183 with the fix summary.
- [ ] Task 130.110: Final full quality gate.

## Progress

### Current Status

**As of 2026-10-03**: Feature just created from GitHub issue #183; planning stage only -- no
investigation or implementation has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
