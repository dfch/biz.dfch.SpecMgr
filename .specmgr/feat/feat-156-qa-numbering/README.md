---
classification: null
created: '2026-09-25T10:44:57.323+02:00'
id: feat-156-qa-numbering
status: planning
type: feat
updated: '2026-09-25T11:08:13.565+02:00'
version: 1.0.0
---

# Feature: Add a numbering scheme for QA question/answer pairs (qa/models/v2 schema, template, example)

## Plan

### Overview

Introduce a fixed, permanent numbering scheme for question/answer pairs inside QA documents (`qa/models/v2`), so each question can be referenced unambiguously (e.g. `1.0020`) in discussion, review, and cross-references without ever needing to renumber existing questions when new ones are inserted later. The number is a bold prefix on the question text itself (`> **1.0010**: <question>`), enforced by a `field_validator` on `QaQuestionAnswer.question` inside `qa/models/v2/` only (no shared `models/md` parser change), modeled on VCR's `Verifies`/`Coverage` validators. Unanswered questions are additionally marked by a `TODO: ` placeholder (e.g. `TODO: answer pending`) as their answer text, which is replaced by the real answer once elicited -- an authoring convention demonstrated in the template and example, explicitly not parsed or validated. This `TODO: ` placeholder **replaces the legacy `_(awaiting response)_` placeholder** the `refine` prompt currently instructs (see REQ-009): the two conventions never coexist, and every live reference to the old placeholder is retired. Tracked by GitHub issue #156; raised during feat-150-mcp-lifecycle-commands planning but explicitly out of scope for feat-150 itself.

### Requirements

- REQ-001: Each Q&A pair's question carries a number `<category-digit>.<sequence>` (e.g. `0.0010`) as a bold prefix in the question text itself: `> **0.0010**: <question text>`; the number lives in exactly one place (the `<!-- ... -->` comment field keeps its original free-form purpose).
- REQ-002: The category digit is fixed per Q&A-bearing section in document order: 0=Elicitation Context, 1=Functional Suitability, 2=Performance Efficiency, 3=Compatibility, 4=Interaction Capability, 5=Reliability, 6=Security, 7=Maintainability, 8=Flexibility, 9=Safety (`General`/`More Information` never hold Q&A pairs).
- REQ-003: The sequence is a 4-digit zero-padded, per-section counter starting at 0010; the convention of incrementing by 10 is a human authoring guideline only and is never parser-enforced, so inserting a number in between (e.g. `0.0015`) must always be possible.
- REQ-004: `qa/models/v2` enforces the number format via a `field_validator("question")` regex (`\A\*\*\d\.\d{4}\*\*:\s`) on `question.text`, with no shared `models/md/` parser change.
- REQ-005: Once assigned, a number is permanent -- never reused, never renumbered; a removed question leaves a gap (mirrors VCR `AC-NNN` and feat phase numbering).
- REQ-006: `qa/data/qa_template.md` and `qa/data/qa_example.md` are updated to demonstrate the numbering scheme; the `QaQuestionAnswer.question`/`QaAnswer` field descriptions (and any affected docstrings) are updated so the number-prefix and `TODO: ` conventions are visible in the generated JSON Schema; and both `docs/qa_schema.json` and the packaged `qa/data/qa_schema.json` are regenerated (`SCHEMA_COMMENT_VERSION` stays `v2` -- a `field_validator` is invisible to `model_json_schema()`, so only the description change alters the output; see Design Note 11).
- REQ-007: An unanswered question is marked by a `TODO: ` placeholder (e.g. `TODO: answer pending`) as its answer text -- the placeholder lives in the answer position, never in the question text, so the question keeps its number prefix at the start; it is replaced by the real answer once the question is answered.
- REQ-008: The `TODO: ` placeholder is a pure authoring convention demonstrated in the template and example, and is explicitly not parsed or validated by `qa/models/v2`.
- REQ-009: The `TODO: ` placeholder retires the legacy `_(awaiting response)_` placeholder: every live reference to it is updated to the `TODO: ` convention -- the `refine` prompt's instructions (`qa/data/qa_refine_instructions.md`) and module docstring (`qa/prompts/refine.py`), the `server.py` docstring's qa-prompts registration line, the cross-domain mention in `prb/data/prb_create_instructions.md` ("non-committal counts as unanswered"), and the tests asserting those texts (`tests/qa/prompts/test_refine.py`, `tests/prb/prompts/test_create_prb.py`) -- and `docs/api/` + `docs/MCP.md` are regenerated.
- REQ-010: The `refine` prompt's instructions are updated so each appended question is written with its target category's next number in `> **<d>.<NNNN>**: ` form (step-10 guideline: that category's existing max sequence + 10, or `0010` when the category holds no numbered question yet) and `TODO: answer pending` as its answer text.

### Acceptance Criteria

- [ ] ACC-001: Parsing a QA document whose questions carry the `**<d>.<NNNN>**: ` prefix succeeds, while a question missing the prefix or carrying a malformed one (wrong digit count, non-zero-padded, missing `: `, number not at the start) fails validation with an actionable error (REQ-001/004).
- [ ] ACC-002: Gaps and non-10 steps (e.g. `0.0015` between `0.0010` and `0.0020`) parse without complaint (REQ-003).
- [ ] ACC-003: The change is confined to `qa/models/v2/` -- no `models/md/` diff (REQ-004).
- [ ] ACC-004: `qa_template.md` and `qa_example.md` parse via `parse_qa` and round-trip (`str(parsed) == source`) with their numbered questions and `TODO: answer pending` placeholders -- the template gains a `parse_qa`-based test (previously string assertions only; the example already has one); both `docs/qa_schema.json` and the packaged `qa/data/qa_schema.json` regenerated (REQ-006).
- [ ] ACC-005: Full quality gate green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, plus `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` regeneration leaving no drift).
- [ ] ACC-006: No live reference to `_(awaiting response)_` remains in `src/`, `tests/`, or the regenerated `docs/api/` + `docs/MCP.md` (REQ-009).
- [ ] ACC-007: The `refine` prompt output instructs appending questions with the next per-category number and the `TODO: answer pending` placeholder, and no longer mentions `_(awaiting response)_` (REQ-010).

### Scope

#### Included

- `qa/models/v2` schema/validator change (question-number format enforcement only) plus the `question`/`answer` field-description update that makes the scheme visible in the generated JSON Schema.
- Updates to `qa/data/qa_template.md`, `qa/data/qa_example.md`, and `qa/data/qa_schema.json` demonstrating the scheme and the `TODO: ` answer placeholder.
- qa prompt instruction text (`qa/data/qa_create_instructions.md`, `qa_update_instructions.md`, `qa_refine_instructions.md` -- the `qa/prompts/*.py` modules are thin wrappers that only read these files) and the `qa/prompts/refine.py` module docstring.
- The `server.py` docstring's qa-prompts registration line, and the cross-domain `prb/data/prb_create_instructions.md` mention of QA's placeholder.
- Migration of the existing qa test fixtures (inline block-quote questions without a number prefix in `tests/qa/models/v2/test_{body,parser,question_answer}.py` and `tests/qa/tools/test_{parse_qa,create_qa,get_qa,list_qa,__io,__lock,__write}.py`) to the numbered form, and of the placeholder-asserting tests (`tests/qa/prompts/test_refine.py`, `tests/prb/prompts/test_create_prb.py`).
- Unit tests for the new number validator, plus a `parse_qa` round-trip test for the template.
- Regeneration of `docs/qa_schema.json`, `qa/data/qa_schema.json`, `docs/api/`, and `docs/MCP.md` (the pre-commit hooks enforce the drift).

#### Explicitly Out Of Scope

- feat-150-mcp-lifecycle-commands (issue #156 is explicitly not part of it).
- Any shared `models/md/` parser change.
- Parser-enforcement of the category-digit-to-section mapping or of the step-10 convention (human guidelines only).
- Parsing or validation of the `TODO: ` answer placeholder by `qa/models/v2` (explicitly a convention demonstrated in the template/example only).
- Bumping `qa/models/v2/_util.py`'s `SCHEMA_COMMENT_VERSION` (stays `v2` -- this change is non-breaking per that module's own bump policy).
- Any code-level detection of unanswered questions (there is none; the `/resolve` lifecycle command is feat-150's, and no command/tool greps for a placeholder string today).
- Migration/renumbering of any pre-existing QA documents in the repo (none currently exist under `docs/qa/` on this branch).

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
10. Placeholder unification: the `refine` prompt already ships a legacy unanswered marker -- the literal `_(awaiting response)_` written as the answer text of each appended question (`qa/data/qa_refine_instructions.md` steps 4 and 6, `qa/prompts/refine.py`'s module docstring, and the `server.py` docstring's registration line). `prb/data/prb_create_instructions.md`'s "non-committal counts as unanswered" rule cites that placeholder by name, and `tests/qa/prompts/test_refine.py`/`tests/prb/prompts/test_create_prb.py` assert it. REQ-007's `TODO: ` convention **replaces** it (REQ-009/010); the two never coexist, and no code parses either one, so the retirement is pure text migration plus doc regeneration.
11. Schema visibility: a `field_validator` is invisible to `model_json_schema()`, so the number format would never reach the `specmgr://qa/schema` resource without updating the `QaQuestionAnswer.question`/`QaAnswer` field descriptions; `qa_create_instructions.md` step 3 tells the LLM to check that resource "to confirm field names and constraints", so the description update is in scope (REQ-006). Only that description change alters the regenerated JSON -- `SCHEMA_COMMENT_VERSION` stays `v2` (`qa/models/v2/_util.py` bumps it only when a breaking change to the generated schema's structure warrants a new `vN`, not on validator additions).
12. Refine's next-number rule: appended questions take the target category's existing max sequence + 10 (`0010` when none exists), per the step-10 human guideline (REQ-010); the parser never enforces the step-10 rule itself (Design Note 4), so the instruction text carries it.
13. Empirically verified against the real parser (2026-09-25): mdformat is stable on `> **<d>.<NNNN>**: text` block quotes; `MarkdownBlockQuote.text` strips the `>` per line and keeps the `**` markers verbatim, so `\A\*\*\d\.\d{4}\*\*:\s` accepts single- and multi-line questions and rejects every malformed shape in ACC-001 (3/5-digit sequence, 2-digit category, missing `: `, space before `:`, number not at the start, and a bare number-only `**<d>.<NNNN>**: ` line). The one softness: `\s` after the colon also accepts a line break (number line, question continuing on the next quoted line) -- accepted as-is. The validator raises `ValueError` (VCR `Verifies`, `req.Level`, `rsk.Strategy` precedent); the shared feat-27 error wrapping adds the document-relative field path and line reference.
14. Empty-category demonstration trade-off: after Task 2.1 no template/example category stays empty, so the "empty heading with nothing under it" case (create-instructions step 1) and the example's `## More Information` narrative ("`Compatibility` was intentionally left without any question/answer pairs") lose their worked demonstration. Accepted: the create instructions still state the empty case in words, and the example's `## More Information` note is reworded to explain that `Compatibility` holds only a `TODO: ` placeholder question for this iteration.

### Related Decisions

- GitHub issue #156 -- design source of record: https://github.com/dfch/biz.dfch.SpecMgr/issues/156
- The linked Q&A document `docs/qa/qa-76229d40-55e9-4640-9249-c391e1f3e84c-feat-150-phase-1-make-valid-design-clarification-q-a.md` (questions 1.0010/1.0020/1.0030 under Functional Suitability) held the full discussion/decisions; it exists only on the `feat-139-logging-telemetry` branch, not on this one, so issue #156 is the only design source of record available here.

### Task List

#### Phase 1: Schema and Validator

- [ ] Task 1.1: Implement the question-number format constant and the `field_validator("question")` for the number prefix on `QaQuestionAnswer` in `qa/models/v2/question_answer.py` -- raises `ValueError` on a missing/malformed prefix, skipped when `question` is absent (Design Notes 3, 13).
- [ ] Task 1.2: Add unit tests for valid/malformed number prefixes (ACC-001's shapes, incl. the bare number-only line), gaps, non-10 steps, and section-independence.
- [ ] Task 1.3: Migrate the existing qa test fixtures to numbered questions -- `tests/qa/models/v2/test_{body,parser,question_answer}.py` and `tests/qa/tools/test_{parse_qa,create_qa,get_qa,list_qa,__io,__lock,__write}.py`; unprefixed questions survive only as negative fixtures where a test asserts the new failure.
- [ ] Task 1.4: Update the `QaQuestionAnswer.question`/`QaAnswer` field descriptions (and affected docstrings) to document the number prefix and the `TODO: ` answer-placeholder convention (REQ-006, Design Note 11).
- [ ] Task 1.5: Run the full quality gate after Phase 1 (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

#### Phase 2: Data, Prompts, and Cross-Domain Retirement

- [ ] Task 2.1: Number every question in `qa/data/qa_template.md` and `qa/data/qa_example.md` and add one `TODO: answer pending` question to each Q&A-bearing category (including Compatibility, whose `## More Information` note in the example gets reworded to match; accepted consequence: no category stays empty -- Design Note 14).
- [ ] Task 2.2: Add a `parse_qa`-based round-trip test for the template (`tests/qa/resources/test_qa_template.py`; the example already has `test_parses_successfully_as_a_v2_document`).
- [ ] Task 2.3: Update the qa prompt instruction text -- `qa/data/qa_create_instructions.md` (structure recap: `> **<d>.<NNNN>**: {question}` shape), `qa_update_instructions.md` (carry the prefix forward on line-range edits), and `qa_refine_instructions.md` (steps 4/6: `TODO: answer pending` replacing `_(awaiting response)_`, plus the next-number rule -- Design Note 12) -- and the `qa/prompts/refine.py` module docstring (REQ-009/010).
- [ ] Task 2.4: Update the `server.py` docstring's qa-prompts registration line and the cross-domain `prb/data/prb_create_instructions.md` placeholder mention, and the tests asserting those texts (`tests/qa/prompts/test_refine.py::test_mentions_response_placeholder`, `tests/prb/prompts/test_create_prb.py`) (REQ-009).
- [ ] Task 2.5: Regenerate `docs/qa_schema.json` + the packaged `qa/data/qa_schema.json` (`specmgr schema` and the qa-package hook; `SCHEMA_COMMENT_VERSION` stays `v2`) and `docs/api/` + `docs/MCP.md` (`specmgr docs`, `specmgr mcp-docs`).
- [ ] Task 2.6: Run the full quality gate after Phase 2 (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, no doc/schema drift).

#### Phase 3: Close-out

- [ ] Task 3.1: Update the `AGENTS.md` qa bullet's pair shape (`> {question}` block quote -> `> **<d>.<NNNN>**: {question}`) and add the placeholder-unification note; verify `server.py`'s registration list is already covered by Task 2.4/2.5.
- [ ] Task 3.2: Run the final full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` clean) and mark the acceptance criteria as verified.

## Progress

### Current Status

**As of 2026-09-25**: Planning (refined after first review). GitHub issue #156 is open with the full design (scheme, enforceability, scope). The review against the live codebase found and fixed: (1) a scope error -- the qa prompt instruction text lives in `qa/data/qa_*_instructions.md`, not `qa/prompts/*.py`; (2) a collision with the legacy `_(awaiting response)_` placeholder the `refine` prompt already ships (incl. a cross-domain mention in `prb/data/prb_create_instructions.md` and two tests) -- now explicitly retired in favor of `TODO: ` (new REQ-009/010); (3) a vacuous schema requirement -- a `field_validator` is invisible to `model_json_schema()`, so the `question`/`answer` field descriptions are now in scope and both schema artifacts (`docs/` + packaged copy) must be regenerated (REQ-006 revised); (4) ~10 test files with unprefixed question fixtures that must be migrated (new Task 1.3); (5) missing doc/schema regeneration in the quality gates (ACC-005 revised); (6) the number-assignment rule for the `refine` prompt's appended questions (Design Note 12); (7) the empty-category demonstration trade-off accepted (Design Note 14). No implementation work has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-25T09:08:13.565Z - Refined after first review

Reviewed the plan against the live codebase (`qa/models/v2/`, `qa/data/`, `qa/prompts/`, `prb/data/`, `server.py`, `tests/qa/`, `tests/prb/`, the pre-commit config, and an empirical parser run of the proposed regex) and refined it. Fixed: Task 2.3/Scope named `qa/prompts/*.py` as the instruction-text location, but the text lives in `qa/data/qa_{create,update,refine}_instructions.md` (the `.py` files are thin `read_packaged_text` wrappers). Found a collision: the `refine` prompt already mandates a different unanswered marker, the literal `_(awaiting response)_` (`qa_refine_instructions.md` steps 4/6, the `refine.py` and `server.py` docstrings, plus `prb_create_instructions.md`'s non-committal rule and two asserting tests); the `TODO: ` placeholder now explicitly replaces it (REQ-009/010, Design Note 10, ACC-006/007). Made the schema requirement real: `model_json_schema()` ignores `field_validator`s, so REQ-006 now includes updating the `question`/`answer` field descriptions, regenerating both `docs/qa_schema.json` and the packaged copy, and keeping `SCHEMA_COMMENT_VERSION` at `v2` (Design Note 11). Added missing tasks: test-fixture migration (Task 1.3, ~10 files), a template `parse_qa` round-trip test (Task 2.2), doc/schema regeneration (Task 2.5), and the `refine` next-number rule (Design Note 12). Accepted a trade-off: after Task 2.1 no template/example category stays empty, which weakens the empty-heading demonstration (Design Note 14). Clarified: the design-source Q&A document exists only on the `feat-139-logging-telemetry` branch; the validator raises `ValueError` per the VCR/REQ/RSK precedent; and the regex was verified against the real parser (mdformat-stable, rejects all ACC-001 malformed shapes).

#### 2026-09-25T08:10:37.616Z - Created

Created this feature to track GitHub issue #156 (QA question/answer pair numbering for `qa/models/v2`). The issue carries the complete design -- fixed `<category-digit>.<sequence>` numbering with a bold question prefix, `field_validator`-enforced format, permanent never-renumbered numbers, and template/example/schema data updates. The scope additionally covers a `TODO: ` answer placeholder on unanswered questions (e.g. `TODO: answer pending`), demonstrated in the template and example and explicitly not parser-enforced. See `### Design Notes` for the scheme details.
