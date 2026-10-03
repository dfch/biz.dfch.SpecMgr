---
classification: null
created: '2026-10-03T09:39:04.941+02:00'
id: feat-183-ts-fff
status: planning
type: feat
updated: '2026-10-03T09:39:04.941+02:00'
version: 1.0.0
---

# Feature: Reduce Agent Misreading of the "fff" Millisecond Placeholder in Timestamp Format Notation

## Plan

### Overview

GitHub issue #183 reports that agents repeatedly emit the literal characters `fff` in timestamps
instead of actual millisecond digits, because every packaged template, example, and docstring
describes the millisecond field of the timestamp format using the placeholder notation
`yyyy-MM-ddTHH:mm:ss.fff[Z|+hh:mm]` (established by feat-146-date-time). The root cause of this
misunderstanding is not yet known. This feature (1) runs a short investigation into why the `fff`
placeholder notation is misread as literal text, (2) based on the findings, selects and validates
one replacement notation that is demonstrably less likely to be copied verbatim, and (3) rolls that
replacement out consistently across every occurrence (packaged templates, examples, docstrings/field
descriptions, generated JSON schemas, and `AGENTS.md`) -- without changing the underlying accepted
timestamp formats, separators, or validation regexes feat-146-date-time established, and without
adding bloated explanatory prose to address the confusion.

### Requirements

- REQ-001: Conduct a short root-cause investigation into why the `fff` placeholder notation is misread as literal text, including prompting several independent AI agent sessions with today's unmodified template/example wording and recording their literal interpretations/misreadings verbatim.
- REQ-002: Based on the investigation findings, select one replacement notation for the millisecond placeholder that is demonstrably less likely to be copied verbatim, validated using the same independent-agent-session method as REQ-001.
- REQ-003: Apply the chosen replacement notation consistently everywhere the current `fff` placeholder appears: packaged templates, packaged examples, domain docstrings/field descriptions, generated JSON schemas, and `AGENTS.md`.
- REQ-004: The timestamp parsing/validation rules established by feat-146-date-time (accepted separators, millisecond digit count, regex patterns) remain unchanged; only the human-facing notation changes.
- REQ-005: The replacement must not introduce bloated explanatory text -- it stays a narrow token/notation substitution, at most a short inline comment, not new paragraphs added to every occurrence.

### Acceptance Criteria

- [ ] ACC-001: A short written summary of the root-cause investigation (REQ-001) exists, citing concrete evidence (agent-session transcripts and/or historical examples) of why the current notation misleads.
- [ ] ACC-002: The chosen replacement notation (REQ-002) is documented with its rationale, including the validation evidence that it reduces misreading versus the current `fff` notation.
- [ ] ACC-003: Every occurrence of the old `fff` placeholder notation in packaged templates/examples/docstrings/JSON schemas/AGENTS.md is updated to the new notation; no occurrence of the literal substring `fff` describing a millisecond placeholder remains, verified by a repo-wide search.
- [ ] ACC-004: No template, example, docstring, or instruction file touched by this feature grows by more than a small, bounded amount of added prose per occurrence (the anti-bloat constraint), verified by reviewing the diff of each touched file.
- [ ] ACC-005: Every packaged template/example file still parses through its own domain's parser after the notation change (no structural/content regression).
- [ ] ACC-006: The full quality gate (ruff format/check, vulture, `pytest -n auto --cov`, pylint baseline unchanged) is green after the change.

### Scope

#### Included

- Investigating why agents misread the `fff` placeholder notation, by prompting independent AI agent sessions with today's unmodified wording.
- Selecting and validating a replacement notation for the millisecond placeholder.
- Updating every occurrence of the `fff` placeholder across packaged templates, examples, docstrings/field descriptions, generated JSON schemas, and `AGENTS.md`.

#### Explicitly Out Of Scope

- Changing the accepted timestamp formats, separators, or validation regexes established by feat-146-date-time -- only the human-facing notation changes.
- Adding verbose explanatory prose about timestamp formatting beyond the narrow notation substitution.
- Re-litigating the `T`-vs-space separator decision or any other feat-146-date-time decision.

### Dependencies

#### Depends On

- feat-146-date-time: establishes the `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]` notation this feature revises for clarity.

### Related Decisions

- ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf ("Use full ISO 8601 date+time timestamps in all entry headings and frontmatter (accept T or space, write T)"): established the notation this feature is revising for clarity, not reversing its format/validation rules.

### Task List

#### Phase 100: Root-cause investigation

- [ ] Task 100.100: Present the current, unmodified template/example timestamp wording to several independent AI agent sessions and record their literal interpretations/misreadings verbatim.
- [ ] Task 100.110: Synthesize the collected evidence into a short root-cause summary (ACC-001).

#### Phase 110: Notation selection

- [ ] Task 110.100: Draft 2-3 candidate replacement notations for the millisecond placeholder.
- [ ] Task 110.110: Validate the leading candidate(s) using the same independent-agent-session method as Phase 100 and record the results.
- [ ] Task 110.120: Record the final chosen notation and its rationale (ACC-002).

#### Phase 120: Rollout

- [ ] Task 120.100: Update all packaged template/example frontmatter and entry-heading format mentions to the new notation.
- [ ] Task 120.110: Update domain docstrings/field descriptions that cite the `fff` notation.
- [ ] Task 120.120: Regenerate the twelve `*_schema.json` files (`specmgr schema`) and `docs/api`/`docs/GENERATED.md`/`docs/adr/README.md` as needed.
- [ ] Task 120.130: Update `AGENTS.md`'s own mentions of the notation.
- [ ] Task 120.140: Repo-wide search confirms no remaining `fff`-as-placeholder occurrences (ACC-003); full quality gate green (ACC-006).

#### Phase 130: Closeout

- [ ] Task 130.100: Add a `CHANGELOG.md` `[Unreleased]` entry and comment on GitHub issue #183 with the fix summary.
- [ ] Task 130.110: Final full quality gate.

## Progress

### Current Status

**As of 2026-10-03**: Feature just created from GitHub issue #183; planning stage only -- no
investigation or implementation has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T07:38:37.000Z - Created

Feature created for GitHub issue #183 ("Agents misread 'fff' misunderstand in templates and
examples"). The plan covers a short root-cause investigation (prompting independent agent sessions
with today's unmodified wording), selection and validation of a replacement millisecond-placeholder
notation, and a full rollout across packaged templates/examples/docstrings/schemas/AGENTS.md,
without changing the underlying timestamp validation rules established by feat-146-date-time.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/183
