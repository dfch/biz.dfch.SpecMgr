---
classification: null
created: '2026-09-17 09:57:31.305+02:00'
id: feat-132-prb-update
status: planning
type: feat
updated: '2026-09-17 09:57:31.305+02:00'
version: 1.0.0
---

# Feature: Carry 5-Why/5W2H Answers from QA into PRB + Anchor a Fixed Problem Statement Sentence

## Plan

### Overview

This feature updates the existing `prb` (Problem Statement) domain so that (1) a
`create_prb` author can optionally link an existing QA (Question & Answer) interview
and have its already-answered 5W2H (5 Whats/Whys/Wheres/Whos/Whens plus 2 Hows)
question/answer pairs -- wherever they appear in the QA document (its
`## Elicitation Context` category, any ISO/IEC 25010:2023 characteristic category,
etc.) -- carried over automatically into the PRB's existing `## Current State` 5W2H
sub-questions, only being asked (via the `question` tool) for whichever of those 7
remain unanswered, so prior elicitation work is never redone; and (2) every PRB now
starts with a new, mandatory lead paragraph directly under its H1 title (no heading of
its own) holding exactly one sentence following the fixed template `[Current state]
is causing [specific issue], for [stakeholder] because [underlying cause].`, giving
every problem statement a consistent, comparable opening framing before the existing
5W2H/Gap/Impact/Future State detail.

### Requirements

- REQ-001: `prb/models/v1/body.py`'s `Prb` model gets a new mandatory `MarkdownParagraph` field, positioned directly after the existing optional `comment` field and before `current_state` (i.e. directly under the H1 title, no heading of its own), holding exactly one sentence following the template `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- mirroring the `general.models.rasci.Rasci.intro`/`general.models.ears.Ears.intro` precedent; requires zero changes to `models/md`.

- REQ-002: The `create_prb` prompt must accept an optional QA document id as input.

- REQ-003: When a QA id is supplied, the `create_prb` prompt must fetch that QA document (`get_qa`) and scan every one of its categories (not only `## Elicitation Context`) for question/answer pairs matching the PRB's 7 5W2H sub-questions (What/Why/Where/Who/When/How/How Often), pre-filling any match into the corresponding `## Current State` sub-question.

- REQ-004: The `create_prb` prompt must use the `question` tool to ask only for whichever of the 7 5W2H sub-questions were not already answered in the linked QA (or all 7, if no QA id was supplied).

- REQ-005: The `create_prb` prompt must use the `question` tool to elicit the 4 blanks of the new lead-paragraph Problem Statement template (`[Current state]`/`[specific issue]`/`[stakeholder]`/`[underlying cause]`) and compose the final sentence from them.

- REQ-006: The `prb` template/example resources (`get_prb_template`, `get_prb_example`) and the generated JSON schema (`specmgr://prb/schema`) must be updated to reflect the new mandatory lead paragraph.

- REQ-007: The `update_prb` prompt must be updated to guide adding the now-mandatory lead paragraph to older-shaped PRB drafts (created before this change) when revising them.

### Acceptance Criteria

- [ ] ACC-001: `create_prb`/`validate(type="prb")` reject a PRB body missing the mandatory lead paragraph directly under the H1 (before `## Current State`), with an actionable structural error.
- [ ] ACC-002: Given a QA id whose document has 5W2H-matching answers spread across multiple categories (e.g. one in `## Elicitation Context`, one in `## Reliability`), running `create_prb` with that QA id pre-fills those answers into `## Current State` without re-asking them.
- [ ] ACC-003: Given a QA id whose document leaves 3 of the 7 5W2H questions unanswered, running `create_prb` asks (via the `question` tool) only for those 3, not the other 4.
- [ ] ACC-004: Running `create_prb` without a QA id still works standalone, asking for all 7 5W2H sub-questions plus the 4 lead-paragraph blanks as before.
- [ ] ACC-005: `get_prb_template`/`get_prb_example` and `specmgr://prb/schema` all show the new mandatory lead paragraph directly under the H1, before `## Current State`.

### Scope

#### Included

- Adding the new mandatory lead `MarkdownParagraph` field to `prb/models/v1/body.py`'s `Prb` model (no `models/md` changes), plus updated template/example.
- Updating the `create_prb` prompt to accept an optional QA id, scan the linked QA across all its categories for 5W2H answers, pre-fill matches, and only ask for the remainder via the `question` tool.
- Updating the `update_prb` prompt to guide adding the new lead paragraph to older-shaped PRB drafts.
- Regenerating `docs/api/`/`docs/GENERATED.md`/the JSON schema resource to reflect the schema change.

#### Explicitly Out Of Scope

- Changing the `qa` schema itself (no new dedicated "5-Why"/"5W2H" QA category; matching happens by scanning existing QA categories/content, not a new structural field).
- Any deterministic, code-level NLP/keyword matcher for QA-to-PRB 5W2H matching; matching is performed by the prompt-driving agent reading the QA content, not new library code.
- Retroactively migrating/rewriting any existing on-disk PRB document (there are currently zero `prb` documents in this repo, per `list_prb`, so no migration is needed).
- Any change to `sysrs`'s `## Problem Statements` cross-reference bullet shape.
- Any change to the shared `models/md` parsing framework itself (confirmed unnecessary; see Design Notes).

### Dependencies

#### Depends On

- feat-16-problem-statement: the original `prb` domain creation (status `done`); this feature updates that existing domain rather than creating it.

### Design Notes

QA-to-PRB 5W2H matching is intentionally performed by the prompt-driving agent reading
the QA document's free-form question/answer prose (the `create_prb` prompt instructs
the agent to scan every QA category, not just `## Elicitation Context`), not by a new
deterministic, code-level parser/matcher -- QA's own Q&A pairs are un-headed, adjacent
block-quote-question-plus-free-prose-answer pairs (feat-14 v2 schema), which resist
rigid keyword parsing but are straightforward for an LLM-driven prompt to interpret.

The new mandatory Problem Statement sentence is placed as a lead `MarkdownParagraph`
directly under the PRB's H1 title (no heading of its own), confirmed feasible with
zero changes to the shared `models/md` parsing framework: `general/models/rasci.py`'s
`Rasci.intro` and `general/models/ears.py`'s `Ears.intro` are live, tested precedents
of exactly this H1 -> (mandatory lead paragraph) -> first H2 shape, both built on the
same, unmodified `MarkdownParagraph`/`MarkdownSection.from_text` machinery `prb` will
reuse.

### Task List

#### Phase 1: Schema

- [ ] Task 1.1: Add a new mandatory `MarkdownParagraph` field to `prb/models/v1/body.py`'s `Prb` model, positioned after the existing optional `comment` field and before `current_state`, matching the `Rasci.intro`/`Ears.intro` precedent.
- [ ] Task 1.2: Update `prb/data/` template and example markdown files (backing `get_prb_template`/`get_prb_example`) to show the new mandatory lead paragraph following the `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` template.
- [ ] Task 1.3: Regenerate/verify the `specmgr://prb/schema` JSON Schema resource reflects the new field.
- [ ] Task 1.4: Add/update unit tests in `tests/prb/models/v1/` covering the new mandatory field (present, absent -> structural error, malformed).

#### Phase 2: Prompts

- [ ] Task 2.1: Update the `create_prb` prompt (`prb/prompts/create_prb.py`) to accept an optional QA document id.
- [ ] Task 2.2: When a QA id is supplied, instruct the prompt flow to fetch the QA document (`get_qa`) and scan every one of its categories for answers matching the PRB's 7 5W2H sub-questions, pre-filling matches into `## Current State`.
- [ ] Task 2.3: Use the `question` tool to ask only for whichever of the 7 5W2H sub-questions remain unanswered (or all 7 if no QA id given), plus the 4 blanks of the new lead-paragraph template.
- [ ] Task 2.4: Update the `update_prb` prompt (`prb/prompts/update_prb.py`) to guide adding the new mandatory lead paragraph when revising a PRB drafted before this change.
- [ ] Task 2.5: Add/update prompt tests in `tests/prb/prompts/`.

#### Phase 3: Verification and Docs

- [ ] Task 3.1: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).
- [ ] Task 3.2: Regenerate `docs/api/`/`docs/GENERATED.md` via `specmgr docs`.
- [ ] Task 3.3: Final review confirming no stale references to the old (pre-change) PRB shape remain in `AGENTS.md`/`server.py` docstrings.

## Progress

### Current Status

Planning only -- this feature has not started implementation. This README captures
the English translation of GitHub issue #132 (filed in German) and the design
decisions reached during this drafting session: (1) the mandatory Problem Statement
sentence will be a lead paragraph directly under the PRB's H1 title, confirmed
feasible with zero changes to the shared `models/md` framework via the
`Rasci.intro`/`Ears.intro` precedent, and (2) QA-to-PRB 5W2H carryover will be
performed by the `create_prb` prompt's agent reading the linked QA document across
all its categories, not a new code-level matcher.

### Blockers

- Waiting on @XyZ-321n (the issue's original reporter) to confirm/accept the "lead paragraph directly under H1" placement, proposed as a comment on GitHub issue #132, before implementation starts.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 09:00:00.000Z - Created from GitHub issue #132

Drafted this feature from GitHub issue #132 (translated from German), which requests
(1) carrying already-answered 5-Why/5W2H questions from a linked QA document into a
PRB's `## Current State` sub-questions, only asking the user for the remainder, and
(2) anchoring a fixed-template Problem Statement sentence into the `prb` structure.
During drafting, examined the shared `models/md` parsing framework and confirmed the
Problem Statement sentence can be placed as a mandatory lead paragraph directly under
the H1 (no heading of its own), with zero framework changes, mirroring the existing
`general.models.rasci.Rasci.intro`/`general.models.ears.Ears.intro` precedent. Drafted
a GitHub comment proposing and recommending this placement, pending the reporter's
confirmation.

### Related PRs / Commits

- [Issue #132](https://github.com/dfch/biz.dfch.SpecMgr/issues/132): tracking issue for this feature (filed in German).

### More Information

GitHub issue #132 was filed in German by @XyZ-321n. This feature's body is an English
translation and elaboration of that issue; the German original on the GitHub issue
itself remains the source of truth for the original request wording.
