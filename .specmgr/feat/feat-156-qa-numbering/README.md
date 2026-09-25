---
classification: null
created: '2026-09-25T10:44:57.323+02:00'
id: feat-156-qa-numbering
status: planning
type: feat
updated: '2026-09-25T10:44:57.323+02:00'
version: 1.0.0
---

# Feature: Add a numbering scheme for QA question/answer pairs (qa/models/v2 schema, template, example)

## Plan

### Overview

Introduce a fixed, permanent numbering scheme for question/answer pairs inside QA documents (`qa/models/v2`), so each question can be referenced unambiguously (e.g. `1.0020`) in discussion, review, and cross-references without ever needing to renumber existing questions when new ones are inserted later. The number is a bold prefix on the question text itself (`> **1.0010**: <question>`), enforced by a `field_validator` on `QaQuestionAnswer.question` inside `qa/models/v2/` only (no shared `models/md` parser change), modeled on VCR's `Verifies`/`Coverage` validators. Unanswered questions are additionally marked by a `TODO: ` placeholder (e.g. `TODO: answer pending`) as their answer text, which is replaced by the real answer once elicited -- an authoring convention demonstrated in the template and example, explicitly not parsed or validated. Tracked by GitHub issue #156; raised during feat-150-mcp-lifecycle-commands planning but explicitly out of scope for feat-150 itself.

### Requirements

- REQ-001: Each Q&A pair's question carries a number `<category-digit>.<sequence>` (e.g. `0.0010`) as a bold prefix in the question text itself: `> **0.0010**: <question text>`; the number lives in exactly one place (the `<!-- ... -->` comment field keeps its original free-form purpose).
- REQ-002: The category digit is fixed per Q&A-bearing section in document order: 0=Elicitation Context, 1=Functional Suitability, 2=Performance Efficiency, 3=Compatibility, 4=Interaction Capability, 5=Reliability, 6=Security, 7=Maintainability, 8=Flexibility, 9=Safety (`General`/`More Information` never hold Q&A pairs).
- REQ-003: The sequence is a 4-digit zero-padded, per-section counter starting at 0010; the convention of incrementing by 10 is a human authoring guideline only and is never parser-enforced, so inserting a number in between (e.g. `0.0015`) must always be possible.
- REQ-004: `qa/models/v2` enforces the number format via a `field_validator("question")` regex (`\A\*\*\d\.\d{4}\*\*:\s`) on `question.text`, with no shared `models/md/` parser change.
- REQ-005: Once assigned, a number is permanent -- never reused, never renumbered; a removed question leaves a gap (mirrors VCR `AC-NNN` and feat phase numbering).
- REQ-006: `qa/data/qa_template.md` and `qa/data/qa_example.md` are updated to demonstrate the numbering scheme, and `qa/data/qa_schema.json` is regenerated to match the new question format.
- REQ-007: An unanswered question is marked by a `TODO: ` placeholder (e.g. `TODO: answer pending`) as its answer text -- the placeholder lives in the answer position, never in the question text, so the question keeps its number prefix at the start; it is replaced by the real answer once the question is answered.
- REQ-008: The `TODO: ` placeholder is a pure authoring convention demonstrated in the template and example, and is explicitly not parsed or validated by `qa/models/v2`.

### Acceptance Criteria

- [ ] ACC-001: Parsing a QA document whose questions carry the `**<d>.<NNNN>**: ` prefix succeeds, while a question missing the prefix or carrying a malformed one (wrong digit count, non-zero-padded, missing `: `, number not at the start) fails validation with an actionable error (REQ-001/004).
- [ ] ACC-002: Gaps and non-10 steps (e.g. `0.0015` between `0.0010` and `0.0020`) parse without complaint (REQ-003).
- [ ] ACC-003: The change is confined to `qa/models/v2/` -- no `models/md/` diff (REQ-004).
- [ ] ACC-004: `qa_template.md` and `qa_example.md` parse via `parse_qa` and round-trip with their numbered questions and `TODO: answer pending` placeholders; `qa_schema.json` regenerated (REQ-006).
- [ ] ACC-005: Full quality gate green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

### Scope

#### Included

- `qa/models/v2` schema/validator change (question-number format enforcement only).
- Updates to `qa/data/qa_template.md`, `qa/data/qa_example.md`, and `qa/data/qa_schema.json` demonstrating the scheme and the `TODO: ` answer placeholder.
- qa prompt instruction files (`qa/prompts/*.py`) where they describe the question format.
- Unit tests for the new number validator.

#### Explicitly Out Of Scope

- feat-150-mcp-lifecycle-commands (issue #156 is explicitly not part of it).
- Any shared `models/md/` parser change.
- Parser-enforcement of the category-digit-to-section mapping or of the step-10 convention (human guidelines only).
- Parsing or validation of the `TODO: ` answer placeholder by `qa/models/v2` (explicitly a convention demonstrated in the template/example only).
- Migration/renumbering of any pre-existing QA documents in the repo (none currently exist under `docs/qa/`).

### Design Notes

1. Number format: `<category-digit>.<sequence>`; digits are fixed per Q&A-bearing section in document order: 0=Elicitation Context, 1=Functional Suitability, 2=Performance Efficiency, 3=Compatibility, 4=Interaction Capability, 5=Reliability, 6=Security, 7=Maintainability, 8=Flexibility, 9=Safety.
2. `MarkdownBlockQuote.text` strips the `>` marker but preserves inline markdown verbatim, so the validator can regex-match `\A\*\*\d\.\d{4}\*\*:\s` at the start of `question.text`.
3. The number-format validator runs only when `question` is present (a pair may omit it); it is modeled on VCR's `Verifies`/`Coverage` `field_validator`s in `vcr/models/v1/body.py`.
4. Explicit decision: no strict start-at/step-by sequence validator, and no parser-enforced digit-to-section mapping -- both stay human authoring guidelines so later in-between insertion (e.g. `0.0015`) always works.
5. Permanence: never reuse or renumber; removals leave gaps (mirrors VCR `AC-NNN` and feat phase numbering).
6. The `<!-- ... -->` comment field keeps its original free-form purpose (who/when a pair was elicited).
7. No pre-existing QA documents exist under `docs/qa/`, so there is no migration burden.
8. The `TODO: ` placeholder (e.g. `TODO: answer pending`) is the *answer text* of an unanswered question -- it never lives in the question text, so the question keeps its number prefix at the start (`> **1.0010**: <question>`) and the parser sees an ordinary, answered pair.
9. Explicit decision: the placeholder is not parsed or validated -- the user must be able to replace it with a real answer freely; the convention is demonstrated in the template and example only, where each Q&A-bearing category is written with one answered question and one `TODO: ` question.

### Related Decisions

- GitHub issue #156 -- design source of record: https://github.com/dfch/biz.dfch.SpecMgr/issues/156
- The linked Q&A document `docs/qa/qa-76229d40-55e9-4640-9249-c391e1f3e84c-feat-150-phase-1-make-valid-design-clarification-q-a.md` (questions 1.0010/1.0020/1.0030 under Functional Suitability) held the full discussion/decisions; it no longer exists on disk.

### Task List

#### Phase 1: Schema and Validator

- [ ] Task 1.1: Implement the question-number format constant and the `field_validator("question")` for the number prefix on `QaQuestionAnswer` in `qa/models/v2/`.
- [ ] Task 1.2: Add unit tests for valid/malformed number prefixes, gaps, and section-independence.
- [ ] Task 1.3: Run the full quality gate after Phase 1 (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

#### Phase 2: Data and Prompts

- [ ] Task 2.1: Number every question in `qa/data/qa_template.md` and `qa/data/qa_example.md` and add one `TODO: answer pending` question to each Q&A-bearing category (including Compatibility, whose `## More Information` note gets reworded to match).
- [ ] Task 2.2: Regenerate `qa/data/qa_schema.json`.
- [ ] Task 2.3: Update `qa/prompts/*.py` instruction text where it describes the question format or the `TODO: ` answer placeholder.
- [ ] Task 2.4: Run the full quality gate after Phase 2 (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

#### Phase 3: Close-out

- [ ] Task 3.1: Update `AGENTS.md`/`server.py` docstrings if the qa-domain description is affected.
- [ ] Task 3.2: Run the final full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) and mark the acceptance criteria as verified.

## Progress

### Current Status

**As of 2026-09-25**: Planning. GitHub issue #156 is open with the full design (scheme, enforceability, scope); the `TODO: ` answer-placeholder convention for unanswered questions has been added to the feature scope (demonstrated in template/example, explicitly not parser-enforced); this feature document has just been created and no implementation work has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-25T08:10:37.616Z - Created

Created this feature to track GitHub issue #156 (QA question/answer pair numbering for `qa/models/v2`). The issue carries the complete design -- fixed `<category-digit>.<sequence>` numbering with a bold question prefix, `field_validator`-enforced format, permanent never-renumbered numbers, and template/example/schema data updates. The scope additionally covers a `TODO: ` answer placeholder on unanswered questions (e.g. `TODO: answer pending`), demonstrated in the template and example and explicitly not parser-enforced. See `### Design Notes` for the scheme details.
