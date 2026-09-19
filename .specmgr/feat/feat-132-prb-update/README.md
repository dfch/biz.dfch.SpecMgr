---
classification: null
created: '2026-09-17 09:57:31.305+02:00'
id: feat-132-prb-update
status: progress
type: feat
updated: '2026-09-19 19:00:00.000+02:00'
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
its own), named `problem_statement`, holding exactly one sentence following the fixed
template `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].`, enforced at the code level by a template-skeleton validator (not
prompt guidance alone), giving every problem statement a consistent, comparable, and
schema-checked opening framing before the existing 5W2H/Gap/Impact/Future State detail.

### Requirements

- REQ-001: `prb/models/v1/body.py`'s `Prb` model gets a new mandatory `MarkdownParagraph` field named `problem_statement`, declared first among `Prb`'s own fields (so it lands after the existing optional `comment` field, inherited from `MarkdownSection1WithComment`, and before `current_state` -- i.e. directly under the H1 title, no heading of its own), holding exactly one sentence following the template `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- mirroring the `general.models.rasci.Rasci.intro`/`general.models.ears.Ears.intro` precedent. The template skeleton is enforced at the code level by a `field_validator` applying a `re.DOTALL` regex fullmatch against the paragraph's own inline text (the sentence can soft-wrap across lines, retaining embedded line breaks in `.text`), mirroring `rsk.models.v1.body.Strategy._validate_value`'s `MarkdownParagraph`-value precedent -- raising an actionable `pydantic.ValidationError` naming the expected template and the actual text. Requires zero changes to `models/md`.

- REQ-002: The `create_prb` prompt must accept an optional QA document id (`qa_id`) in addition to the existing `topic` input.

- REQ-003: When a QA id is supplied, the `create_prb` prompt must fetch that QA document (`get_qa`) and scan every one of its Q&A-holding categories (the 10 `_QaCategory`-shaped sections: `## Elicitation Context` plus the 9 ISO/IEC 25010:2023 characteristics, not only `## Elicitation Context`) for question/answer pairs matching the PRB's 7 5W2H sub-questions (What/Why/Where/Who/When/How/How Often), pre-filling any match into the corresponding `## Current State` sub-question. Matching rules: each QA pair maps to at most one 5W2H sub-question (best match only, never duplicated across two sub-questions), and a non-committal QA answer (e.g. "unknown", "not yet answered") counts as unanswered, not as a pre-fill.

- REQ-004: When a QA id is supplied but does not resolve (`get_qa` raises `QaNotFoundError`), the `create_prb` prompt must surface that failure to the user and use the `question` tool to ask whether to proceed standalone (all 7 questions, no pre-fill) or retry with a corrected QA id -- never silently fall through to standalone behavior without telling the user why.

- REQ-005: The `create_prb` prompt must use the `question` tool to ask only for whichever of the 7 5W2H sub-questions were not already answered in the linked QA (or all 7, if no QA id was supplied or it did not resolve), explicitly allowing the user to skip any question, same as today.

- REQ-006: The `create_prb` prompt must compose the new lead-paragraph Problem Statement sentence from its 4 blanks (`[Current state]`/`[specific issue]`/`[stakeholder]`/ `[underlying cause]`). When a QA id was supplied and 5W2H answers were pre-filled, the 4 blanks must first be *derived* from those pre-filled answers (`What` -> `[Current state]`/`[specific issue]`, `Who` -> `[stakeholder]`, `Why` -> `[underlying cause]`) and the composed sentence *confirmed* with the user via the `question` tool, rather than asked as 4 fresh questions; only a blank no pre-filled answer supports is asked for directly. In standalone mode (no QA id, or nothing pre-filled), all 4 blanks are elicited via the `question` tool as before. Because a single `What` answer must populate two distinct blanks (`[Current state]` and `[specific issue]`), the prompt should draft its best split of that answer across both blanks and rely on the required user confirmation step (not a fresh derivation rule) to catch a bad split -- this is a judgment call for the prompt-driving agent, not a code-level concern.

- REQ-007: The `prb` template/example resources (`get_prb_template`, `get_prb_example`) and both generated JSON Schema copies (`docs/prb_schema.json` and the packaged `src/biz/dfch/specmgr/prb/data/prb_schema.json` behind `specmgr://prb/schema`) must be updated to reflect the new mandatory `problem_statement` lead paragraph, landing in the same commit as the model change -- the packaged template/example are parsed against the model by `tests/prb/tools/test_integration.py`'s drift-guard test.

- REQ-008: The `update_prb` prompt must guide recovery of an old-shape PRB draft (created before this change, whose body lacks the now-mandatory `problem_statement` paragraph). Because `get_prb(id)` itself will fail to parse such a document post-change, the prompt must instruct the agent: on that specific missing-lead-paragraph parse error, re-read via `get_prb(id, raw=True)`, elicit/confirm (or derive from the document's own What/Who/Why answers, mirroring REQ-006) the sentence's 4 blanks, insert the composed sentence directly under the H1, then proceed with whatever change was originally requested.

- REQ-009: The existing "problem statements stay free of assumed causes by design" design texts must be reconciled with the new lead sentence, which by design now carries the best-known cause in its `because [underlying cause]` clause. Reword, in the same commit as REQ-001: `prb/models/v1/body.py`'s module and `Prb` class docstrings (currently phrased as "No `Root Cause` section... a deliberate, Six-Sigma-discipline-driven omission" -- not the literal "free of assumed causes" wording, which only appears in the instructions/example files below), `prb/data/prb_create_instructions.md`'s structure-recap note ("a problem statement stays free of assumed causes by design"), and `prb/data/prb_example.md`'s `## More Information` paragraph ("No root cause analysis is included here by design...") -- all reworded to "no `## Root Cause` section exists; the lead sentence carries the best-known cause by design; formal root-cause analysis remains a separate, later activity" (or equivalent wording) -- and rewrite the prompt test asserting the old wording (`tests/prb/prompts/test_create_prb.py::test_mentions_no_root_cause_section`) to match.

- REQ-010: `prb/models/v1/body.py`'s `_PROBLEM_STATEMENT_PATTERN` must tolerate a `problem_statement` paragraph whose soft-wrap lands exactly at one of its three fixed literal joiners (`" is causing "`, `", for "`, `" because "`), since `MarkdownParagraph.text` preserves a soft-wrapped sentence's embedded line breaks verbatim (`mdformat` never reflows) and a literal single space would otherwise not match an embedded `\n` even under `re.DOTALL` (which only makes `.` match `\n`, not a literal `" "`). Fix by replacing each literal single space in the three joiners with `\s+`, keeping `re.DOTALL` for the four blank captures. Found during a post-Phase-3 self-review, not part of GitHub issue #132's original request.

- REQ-011: `_PROBLEM_STATEMENT_PATTERN`'s four named capture groups (`current_state`/`specific_issue`/`stakeholder`/`underlying_cause`) are dead code -- only `fullmatch()`'s truthiness is ever checked, the groups themselves are never read. Convert them to non-capturing groups (`(?:.+)`); no behavior or error-message change.

- REQ-012: `prb/prompts/create_prb.py`'s module docstring says "a 12-step interview flow", but `prb_create_instructions.md` numbers `## 0.` through `## 12.` -- 13 sections, an off-by-one drift versus `update_prb.py`'s own "N-step = section count" convention (its "9-step revision flow" correctly counts `prb_update_instructions.md`'s 9 numbered sections). Reword to "13-step interview flow".

- REQ-013: (Phase 5, found during an external `feat-reviewer` review pass, not part of GitHub issue #132's original request) `_PROBLEM_STATEMENT_PATTERN`'s greedy `.+` blanks under `re.DOTALL` can still backtrack across an embedded joiner phrase inside a blank's own free text (e.g. a `[Current state]` blank whose text literally contains the substring `" is causing "`), producing a false-positive match against a sentence that does not actually follow the intended 4-blank structure. This trade-off is already acknowledged in this file's own Decisions Made log (2026-09-19 17:15:00.000Z entry) but is not documented anywhere in the code itself, nor exercised by any test. Extend the pattern's explanatory comment to name this limitation explicitly, and add a test that demonstrates (not "fixes") the current, accepted behavior.

- REQ-014: (Phase 5) `prb_create_instructions.md`'s one-pair-to-one-question / best-match-only rule (REQ-003) is stated as prose with no worked example illustrating a QA pair that could plausibly match two of the 7 5W2H sub-questions and how the tie-break should be resolved in practice. Add one concrete worked example to the instructions; the existing prompt test (`tests/prb/prompts/test_create_prb.py::test_mentions_one_pair_to_one_question_rule`) must be extended to also assert the example is present.

- REQ-015: (Phase 5) The `What -> [Current state]/[specific issue]`, `Who -> [stakeholder]`, `Why -> [underlying cause]` derive-mapping clause is currently paraphrased independently in `prb_create_instructions.md` (step 9) and `prb_update_instructions.md` (step 1's old-shape recovery sub-list), with no mechanism keeping the two in sync. Align the mapping clause itself (not necessarily its surrounding sentence, which may legitimately differ by context) to identical, verbatim wording in both files, and add a dedicated consistency test that loads both packaged `.md` files and fails if the shared clause ever drifts apart again.

### Acceptance Criteria

- [x] ACC-001: `create_prb`/`validate(type="prb")` reject a PRB body missing the mandatory `problem_statement` lead paragraph directly under the H1 (before `## Current State`), with an actionable structural error, *and* reject a present lead paragraph whose text does not match the template skeleton, with an actionable field-validation error naming the expected template and the actual text.
- [x] ACC-002: Given a QA id whose document has 5W2H-matching answers spread across multiple categories (e.g. one in `## Elicitation Context`, one in `## Reliability`), running `create_prb` with that QA id pre-fills those answers into `## Current State` without re-asking them, with each QA pair mapped to at most one sub-question.
- [x] ACC-003: Given a QA id whose document leaves 3 of the 7 5W2H questions unanswered (including any non-committal answers, which count as unanswered), running `create_prb` asks (via the `question` tool) only for those 3, not the other 4.
- [x] ACC-004: Running `create_prb` with a nonexistent QA id surfaces the failure and asks whether to proceed standalone or retry with a corrected id (REQ-004). Running it without a QA id still works standalone, asking for all 7 5W2H sub-questions plus the 4 lead-paragraph blanks as fresh questions (nothing is pre-filled to derive them from).
- [x] ACC-005: `get_prb_template`/`get_prb_example`, `docs/prb_schema.json`, and the packaged `specmgr://prb/schema` copy all show the new mandatory `problem_statement` lead paragraph directly under the H1, before `## Current State`.
- [x] ACC-006: In a QA-linked run with at least one pre-filled 5W2H answer, the lead sentence's blanks are derived from those answers and the composed sentence is confirmed with the user (not asked as 4 fresh questions, REQ-006); the composed sentence passes the code-level template validator.
- [x] ACC-007: Running `update_prb` against an old-shape PRB (no `problem_statement` paragraph) recovers via `get_prb(id, raw=True)` plus sentence insertion (REQ-008), then applies the originally requested change, leaving the result parseable by `get_prb`.
- [x] ACC-008: A `problem_statement` paragraph whose soft-wrap lands exactly at any of the three literal joiners ("is causing"/"for"/"because") still passes `Prb`'s `field_validator`/`create_prb`/`validate(type="prb")` (REQ-010).
- [ ] ACC-009: `_PROBLEM_STATEMENT_PATTERN`'s comment block explicitly names the greedy-backtracking trade-off (REQ-013); a test in `tests/prb/models/v1/test_body.py` demonstrates the documented, accepted edge case.
- [ ] ACC-010: `prb_create_instructions.md` contains a worked example of the one-pair-to-one-question tie-break (REQ-014); `tests/prb/prompts/test_create_prb.py` asserts its presence.
- [ ] ACC-011: The `What`/`Who`/`Why` -> 4-blank derive-mapping clause is byte-identical between `prb_create_instructions.md` and `prb_update_instructions.md` (REQ-015), enforced by a dedicated consistency test that fails on future drift.

### Scope

#### Included

- Adding the new mandatory `problem_statement` `MarkdownParagraph` field, plus a
  code-level template-skeleton `field_validator`, to `prb/models/v1/body.py`'s `Prb`
  model -- an in-place `prb/models/v1` schema evolution (no `prb/models/v2`, no
  `models/md` changes), plus updated template/example and both JSON schema copies.
- Rewording the "free of assumed causes"/"no Root Cause" design texts across the model
  docstrings, the create/update instruction files, and the packaged example (REQ-009).
- Updating the `create_prb` prompt to accept an optional QA id, fetch it via `get_qa`
  (with bad-id handling, REQ-004), scan the linked QA across all Q&A-holding categories
  for 5W2H answers under the one-pair-to-one-question/non-committal-is-unanswered rules,
  pre-fill matches, ask only for the remainder, and derive-then-confirm the 4
  lead-paragraph blanks from pre-filled answers where possible.
- Updating the `update_prb` prompt to guide recovery of old-shape PRB drafts (raw
  re-read + lead-paragraph insertion, REQ-008).
- Regenerating `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`, both JSON schema copies,
  the `server.py` docstring, the AGENTS.md `prb` bullet, and a `CHANGELOG.md`
  `[Unreleased]` entry (with a **BREAKING** marker).

#### Explicitly Out Of Scope

- Changing the `qa` schema itself (no new dedicated "5-Why"/"5W2H" QA category; matching
  happens by scanning existing QA categories/content, not a new structural field).
- Any deterministic, code-level NLP/keyword matcher for QA-to-PRB 5W2H matching; that
  matching is performed by the prompt-driving agent reading the QA content, not new
  library code. (REQ-001's code-level validator concerns only the PRB lead sentence's
  own template skeleton, not QA matching.)
- Retroactively migrating/rewriting any existing on-disk PRB document. In this repo
  there are currently zero `prb` documents (per `list_prb`), so no in-repo migration is
  needed. Pre-existing PRB documents outside this repo (`prb` shipped in v0.10.0) will
  fail `parse_prb`/`get_prb` after this change until the lead paragraph is added -- a
  deliberate, documented **BREAKING** consequence of the in-place `prb/models/v1`
  evolution (see Decisions Made); the `update_prb` prompt (REQ-008) is the guided
  recovery path, not an automated migration.
- Creating a `prb/models/v2` package (considered and rejected -- see Decisions Made).
- Any change to `sysrs`'s `### Problem Statement` cross-reference bullet shape
  (`sysrs.models.v1.body.ProblemStatement`, nested under `## Business Context and Goals`).
- Any change to the shared `models/md` parsing framework itself (confirmed unnecessary;
  see Design Notes).
- Recording the linked QA as a structured `QA <uuid>: <title>` bullet in the new PRB's
  `## References` -- possible future follow-up; the section stays free-form, so nothing
  prevents an agent from adding one by hand.

### Dependencies

#### Depends On

- feat-16-problem-statement: the original `prb` domain creation (status `done`); this
  feature updates that existing domain rather than creating it.

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
of the H1 -> (mandatory lead paragraph) -> first H2 shape, built on the same,
unmodified `MarkdownParagraph`/`MarkdownSection.from_text` machinery `prb` will reuse
-- note both are plain `MarkdownSection1` with no inherited field ahead of `intro`, so
they don't themselves exercise the "own-declared-first places it after an inherited
field" nuance `Prb` needs (that part is separately confirmed via
`MarkdownStr._get_field_names()`'s base-class-first Pydantic field ordering, next
paragraph). Because `comment` is *inherited* from `MarkdownSection1WithComment` rather than
declared on `Prb` itself, `problem_statement` must be declared *first* among `Prb`'s
own fields -- Pydantic orders `model_fields` base-class-first, and `MarkdownStr.from_text`'s
distribution loop walks fields in that same declaration order, so this ordering (not an
explicit position argument) is what actually places `problem_statement` between
`comment` and `current_state`.

The template skeleton itself is validated at the code level, not left to prompt
guidance alone: `rsk.models.v1.body.Strategy._validate_value` is a live precedent for
applying a `field_validator`/regex check against a `MarkdownParagraph` field's own
`.text` (Pydantic's `Field(pattern=...)` cannot apply to a model-typed field directly).
Because a soft-wrapped sentence's `.text` retains its embedded line breaks, the regex
must use `re.DOTALL` (not whitespace-collapsing, for which there is no codebase
precedent) so `.` also matches `\n`, mirroring
`general.models.rasci._ROLE_ITEM_PATTERN`'s existing `re.DOTALL` handling of the same
soft-wrap issue.

**No `Root Cause` *section*** remains absent -- a deliberate, Six-Sigma-discipline-driven
omission carried over from feat-16 -- but the *rationale* text changes: the new lead
sentence's `because [underlying cause]` clause does put a single, best-known cause into
every PRB by design (per the issue's own template), so the "free of assumed causes"
wording is now reworded rather than merely preserved (REQ-009).

### Related Decisions

- No ADR or DEC exists for this feature's two placement/matching decisions -- both are
  scoped entirely to this feature's own implementation and were confirmed as comments on
  GitHub issue #132 rather than filed as a standalone architecture decision, per the
  ADR-vs-feature-decision rule in AGENTS.md.

### Task List

#### Phase 1: Schema (atomic -- model, template, example, both schema copies, and every affected test fixture land together, since the integration drift-guard test parses the packaged template/example against the model)

- [x] Task 1.1: Add the new mandatory `problem_statement: MarkdownParagraph` field to `prb/models/v1/body.py`'s `Prb` model, declared first among `Prb`'s own fields, with a `field_validator` enforcing the template skeleton `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` via a `re.DOTALL` regex fullmatch on the paragraph's `.text`, mirroring `rsk.models.v1.body.Strategy._validate_value`. Update the module docstring's layout diagram and the `Prb` class docstring's Parameters section, and reword the "no Root Cause section" texts per REQ-009.
- [x] Task 1.2: Update `prb/data/prb_template.md` and `prb/data/prb_example.md` to show the new mandatory lead paragraph following the template; reword the example's `## More Information` "no root cause analysis ... by design" line per REQ-009.
- [x] Task 1.3: Regenerate both JSON schema copies (`specmgr schema` for `docs/prb_schema.json`; `specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data` for the packaged copy) and confirm `problem_statement` appears in both.
- [x] Task 1.4: Add/update unit tests in `tests/prb/models/v1/` covering the new field (present + valid, absent -> actionable structural error, present but malformed template -> actionable field-validation error).
- [x] Task 1.5: Sweep every hand-written PRB-body fixture across `tests/prb/` (`models/v1/test_parser.py`, `tools/test_integration.py`, `tools/test_parse_prb.py`, `tools/test_get_prb.py`, `tools/test_create_prb.py`, `tools/test_list_prb.py`, `tools/test__io.py`, `tools/test__paths.py`, `tools/test__write.py`) to insert the new lead sentence; add a dedicated old-shape-rejection test asserting a pre-change-shaped body fails `Prb.from_text` with an actionable error (documents the REQ-008 recovery trigger).

#### Phase 2: Prompts

- [x] Task 2.1: Update `prb/prompts/create_prb.py`'s signature to `create_prb(topic: str, qa_id: str | None = None)`, substituting a "(not given ...)" fallback when absent (the existing `update_prb` instructions pattern); update the module docstring (step count/flow) and the `@mcp.prompt` description to mention the optional QA carry-over.
- [x] Task 2.2: Update `prb/data/prb_create_instructions.md`: when a QA id is supplied, instruct fetching the QA document via `get_qa` with explicit bad-id handling (`QaNotFoundError` -> surface + ask standalone-or-corrected-id, REQ-004); scan every Q&A-holding category for answers matching the PRB's 7 5W2H sub-questions under the one-pair-to-one-question / non-committal-counts-as-unanswered rules (REQ-003), pre-filling matches into `## Current State`.
- [x] Task 2.3: Instruct the flow (same file) to use the `question` tool to ask only for whichever of the 7 5W2H sub-questions remain unanswered (or all 7 if no QA id given or it didn't resolve, skips still allowed), and to compose the lead-paragraph sentence: derive-then-confirm its 4 blanks from pre-filled What/Who/Why answers in QA-linked mode (REQ-006), or elicit all 4 as fresh questions in standalone mode.
- [x] Task 2.4: Update the structure recap in `prb/data/prb_create_instructions.md` to include the new mandatory lead paragraph, and reword the "no `## Root Cause` section ... free of assumed causes" note per REQ-009.
- [x] Task 2.5: Update `prb/prompts/update_prb.py` and `prb/data/prb_update_instructions.md` to guide recovery of old-shape PRB drafts (REQ-008): on the missing-lead-paragraph parse error from `get_prb`, re-read via `get_prb(id, raw=True)`, elicit/confirm or derive the 4 blanks, insert the sentence under the H1, then proceed.
- [x] Task 2.6: Add/update prompt tests in `tests/prb/prompts/`: `qa_id` interpolation/fallback, `get_qa` mention plus bad-id handling, the one-pair-to-one-question rule, the derive-then-confirm flow, and old-shape recovery via raw re-read; rewrite `test_mentions_no_root_cause_section` per REQ-009.

#### Phase 3: Verification and Docs

- [x] Task 3.1: Regenerate `docs/api/`/`docs/GENERATED.md` via `specmgr docs` and `docs/MCP.md` via `specmgr mcp-docs` (the new `qa_id` prompt parameter changes the generated prompt schema).
- [x] Task 3.2: Update `server.py`'s "Problem statement prompts" docstring line and the `prb` bullet in `AGENTS.md` (optional `qa_id`, mandatory validated lead paragraph, in-place-v1 **BREAKING** note).
- [x] Task 3.3: Add `CHANGELOG.md` `[Unreleased]` entries: **Added** (mandatory `problem_statement` lead paragraph + template validator; `create_prb`'s optional `qa_id` and QA carry-over; `update_prb`'s old-shape recovery) and **Changed (BREAKING)** (pre-existing PRB documents without the lead paragraph fail `parse_prb`/`get_prb` until it is added; `update_prb` guides the recovery).
- [x] Task 3.4: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`).
- [x] Task 3.5: Final review confirming no stale references to the old (pre-change) PRB shape, or the old "free of assumed causes" rationale, remain in `AGENTS.md`/ `server.py` docstrings or the instruction data files.

#### Phase 4: Post-Review Hardening (found during a self-review pass after Phase 3, not part of GitHub issue #132's original request)

- [x] Task 4.1: In `prb/models/v1/body.py`, update `_PROBLEM_STATEMENT_PATTERN`: replace the three literal `" "` joiners (`" is causing "`, `", for "`, `" because "`) with `\s+` so a soft-wrap landing exactly at one of them still matches (REQ-010); convert the four named capture groups to non-capturing `(?:.+)` (REQ-011), keeping `re.DOTALL`. Extend the pattern's explanatory comment to cover the `\s+` rationale alongside the existing `re.DOTALL` rationale.
- [x] Task 4.2: Add 3 regression tests to `tests/prb/models/v1/test_body.py` -- one `problem_statement` paragraph per joiner (`is causing`/`for`/`because`), each soft-wrapped exactly at that joiner, asserting `Prb(**kwargs)` still succeeds (ACC-008). Leave the existing malformed-template rejection test (`test_malformed_template_raises_validation_error_naming_template_and_text`) unchanged -- it must keep failing on genuinely non-matching text.
- [x] Task 4.3: Fix `prb/prompts/create_prb.py`'s module docstring wording per REQ-012 ("12-step" -> "13-step").
- [x] Task 4.4: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src`), update Progress (Current Status, a dated Updates entry, a Decisions Made entry noting Phase 4 originated from a self-review rather than the GitHub issue), and flip `status` back to `review`.

#### Phase 5: External-Review Hardening (found during an external `feat-reviewer` review pass after Phase 4, not part of GitHub issue #132's original request)

- [ ] Task 5.1: In `prb/models/v1/body.py`, extend `_PROBLEM_STATEMENT_PATTERN`'s explanatory comment block to explicitly document the greedy-backtracking trade-off (REQ-013): a blank's own free text containing a literal joiner substring (e.g. `" is causing "`) can still produce a false-positive template match. Add one test to `tests/prb/models/v1/test_body.py` constructing such a blank and asserting the current, accepted match behavior (a documentation test, not a behavior change; `test_malformed_template_raises_validation_error_naming_template_and_text` must keep failing on genuinely non-matching text).
- [ ] Task 5.2: In `prb/data/prb_create_instructions.md`, add a worked example to the one-pair-to-one-question rule (REQ-014): a QA pair that could plausibly answer two of the 7 5W2H sub-questions, and how "best match only" resolves it. Update `tests/prb/prompts/test_create_prb.py` to assert the example is present, alongside the existing rule-text assertion.
- [ ] Task 5.3: In `prb/models/v1/body.py:35`'s module docstring, fix the one-space column misalignment in the ASCII layout diagram (the `### What Is the Problem?` row), same file already touched by Task 5.1.
- [ ] Task 5.4: Align the `What -> [Current state]/[specific issue]`, `Who -> [stakeholder]`, `Why -> [underlying cause]` derive-mapping clause to identical, verbatim wording in both `prb_create_instructions.md` and `prb_update_instructions.md` (REQ-015). Add a new consistency test (e.g. `tests/prb/data/test_instructions_consistency.py`) that loads both packaged `.md` files and asserts the shared clause matches exactly, so future drift fails loudly instead of silently.
- [ ] Task 5.5: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src`), update Progress (Current Status, a dated Updates entry, a Decisions Made entry noting Phase 5 originated from an external `feat-reviewer` review rather than the GitHub issue), and flip `status` back to `review`.

## Progress

### Current Status

**As of 2026-09-19**: Phases 1-4 are complete -- Phase 1 (Schema), Phase 2
(Prompts), Phase 3 (Verification and Docs), and Phase 4 (Post-Review Hardening,
added after a self-review pass). All 8 original acceptance criteria (ACC-001
through ACC-008) are fully met. Phase 5 (External-Review Hardening) has now
been *planned* -- added following an independent external `feat-reviewer`
review pass -- but not yet implemented; ACC-009 through ACC-011 remain
unchecked pending Tasks 5.1-5.5. `prb/models/v1/body.py`'s `Prb` model carries the
mandatory `problem_statement: MarkdownParagraph` lead field with its code-level
template-skeleton `field_validator`; the packaged template/example and both JSON
schema copies (`docs/prb_schema.json`,
`src/biz/dfch/specmgr/prb/data/prb_schema.json`) reflect it. `_PROBLEM_STATEMENT_PATTERN`
now tolerates a soft-wrap landing exactly at any of its three fixed joiners
(`\s+` in place of each literal single space, REQ-010) and no longer carries
dead named capture groups (`(?:.+)`, REQ-011). `create_prb`'s prompt accepts an
optional `qa_id`, narrating a `get_qa`-backed carry-over of already-answered
5W2H questions across all 10 QA categories (with explicit `QaNotFoundError`
handling and a derive-then-confirm lead-sentence flow), and its module docstring
now correctly says "13-step interview flow" (REQ-012); `update_prb`'s prompt
narrates a raw-re-read-based recovery flow for old-shape PRB drafts.
`docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`, `server.py`'s module docstring,
`AGENTS.md`'s `prb` bullet, and `CHANGELOG.md`'s `[Unreleased]` section all
reflect the feature; both JSON schema copies confirmed drift-free via a fresh
`specmgr schema --type prb` run. The full quality gate (`ruff format --check`,
`ruff check`, `vulture`, the full `pytest -n auto --cov=src` suite -- 3327
passed) is green at the end of Phase 4. Final sign-off is now pending Phase 5.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-19 19:00:00.000Z - Phase 5 (External-Review Hardening) planned from an external `feat-reviewer` review pass

An independent `feat-reviewer` review of the merged, Phase-4-complete implementation
(against `dev` at the time) found five items, none blocking (zero Errors; all 8
original acceptance criteria confirmed still met): (1) `_PROBLEM_STATEMENT_PATTERN`'s
greedy-backtracking trade-off is acknowledged in this file's own history but not
documented in the code itself, nor exercised by a test; (2) the one-pair-to-one-question
rule in `prb_create_instructions.md` has no worked example of an ambiguous QA-pair
tie-break; (3) commit `b97ccf3` bundled unrelated `.opencode/agent/feat-reviewer.md` and
`.opencode/command/review-feature.md` additions into an otherwise `prb`-scoped docs
commit; (4) `prb/models/v1/body.py:35`'s module docstring layout diagram has a
pre-existing, one-space column misalignment on the `### What Is the Problem?` row that
this feature's own edits touched without correcting; (5) the `What`/`Who`/`Why` -> blank
derive-mapping clause is paraphrased independently (and could silently drift) between
`prb_create_instructions.md` and `prb_update_instructions.md`.
Items (1), (2), (4), and (5) were accepted and added as REQ-013/014/015, ACC-009/010/011,
and Phase 5 (Tasks 5.1-5.5) above; `status` reopened from `review` to `in-progress`
pending Phase 5. Item (5) was escalated beyond the reviewer's own "accepted trade-off"
suggestion to a dedicated consistency test (see Decisions Made) rather than left
undocumented. Item (3) was explicitly declined as a Phase 5 task -- see Decisions Made --
since it concerns commit-history hygiene, not `prb/` code, and this feature has no
mechanism (nor mandate) to rewrite already-pushed git history. This entry is planning
only; no `prb/` source, test, or data file has been touched yet.

#### 2026-09-19 18:00:00.000Z - Phase 4 (Post-Review Hardening) implemented

Implemented Task 4.1-4.4 in full, touching only `prb/models/v1/body.py`,
`tests/prb/models/v1/test_body.py`, and `prb/prompts/create_prb.py` -- no other
Phase 1/2/3 territory was touched. In `body.py`, replaced
`_PROBLEM_STATEMENT_PATTERN`'s three literal single-space joiners
(`" is causing "`, `", for "`, `" because "`) with `\s+` at each embedded space
(REQ-010), so a soft-wrap landing exactly at one of those spaces (which
`MarkdownParagraph.text` preserves verbatim as an embedded `\n`) still matches;
converted the four named capture groups (`current_state`/`specific_issue`/
`stakeholder`/`underlying_cause`) to non-capturing groups (`(?:.+)`, REQ-011),
keeping `re.DOTALL`. Extended the pattern's explanatory `#:` comment block to
cover both the `\s+`-for-soft-wrap-tolerance rationale and the
non-capturing-groups rationale, alongside the existing `re.DOTALL` rationale.
Added 3 regression tests to `tests/prb/models/v1/test_body.py`'s
`TestProblemStatementMandatoryAndTemplateValidated` class -- one
`problem_statement` paragraph per joiner (`is causing`/`for`/`because`), each
constructed with an embedded newline landing exactly at that joiner's space
(mid-joiner for "is causing", right after the comma for "for", right before
the word for "because"), asserting `Prb(**kwargs)` still succeeds and that the
embedded newline survives in `.text` (ACC-008). The existing malformed-template
rejection test (`test_malformed_template_raises_validation_error_naming_template_and_text`)
was left unchanged and still correctly fails on genuinely non-matching text.
Fixed `prb/prompts/create_prb.py`'s module docstring per REQ-012: "a 12-step
interview flow" -> "a 13-step interview flow" (the generated
`docs/api/biz.dfch.specmgr.prb.prompts.create_prb.md` mirror of this docstring
was intentionally left as-is, since Phase 4's quality gate does not include a
`specmgr docs` regeneration step and no other Phase 4 task calls for it; it
will pick up the fix the next time `specmgr docs` runs). Quality gate green:
`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`,
and the full `pytest -n auto --cov=src` suite (3327 passed, up from 3324 at the
end of Phase 3 -- the 3 new regression tests). All 8 acceptance criteria
(ACC-001 through ACC-008) are now met; the feature's status moves from
`in-progress` back to `review`.

#### 2026-09-19 17:15:00.000Z - Phase 4 (Post-Review Hardening) planned from a self-review pass

A post-Phase-3 review of the merged implementation (commits `c6ccad6`, `aedf6e6`,
`def911f`) against the plan found three issues, none blocking but all worth fixing:
(1) `_PROBLEM_STATEMENT_PATTERN`'s three literal single-space joiners (`" is causing "`,
`", for "`, `" because "`) do not tolerate a soft-wrap landing exactly at one of them --
`MarkdownParagraph.text` preserves embedded line breaks verbatim and `re.DOTALL` only
makes `.` match `\n`, not a literal `" "` -- so an otherwise-valid sentence could be
rejected purely due to word-wrap placement, with no existing test covering this edge
case; (2) the pattern's four named capture groups are dead code, never read outside
`fullmatch()`'s truthiness check; (3) `create_prb.py`'s module docstring says "a
12-step interview flow" but `prb_create_instructions.md` numbers 13 sections (`## 0.`
through `## 12.`), an off-by-one versus `update_prb.py`'s own "N-step = section count"
convention. Added REQ-010/011/012, ACC-008, and Phase 4 (Tasks 4.1-4.4) to this plan to
track the fixes; reopened `status` from `review` to `in-progress` pending Phase 4.
Nothing under Phase 1-3's `prb/` code was touched by this update -- planning only.

#### 2026-09-19 16:30:00.000Z - Phase 3 (Verification and Docs) implemented

Implemented Task 3.1-3.5 in full, touching only `server.py`'s module docstring,
`AGENTS.md`'s `prb` bullet, `CHANGELOG.md`, and the generated doc artifacts -- no
`prb/models/v1/`, template/example, JSON schema, or `prb/prompts/`/`prb/data/`
content was touched (Phase 1/2 territory, already committed). Reworded
`server.py`'s "Problem statement prompts" docstring line to mention `create_prb`'s
optional `qa_id` QA carry-over and the mandatory, code-level-validated
`problem_statement` lead sentence. Updated `AGENTS.md`'s `prb/` bullet in place,
matching the house style of neighboring bullets (e.g. `gol/`/`rsk/`): it now
documents the optional `qa_id` parameter and its 10-category QA scan, the mandatory
`problem_statement` lead paragraph and its code-level `field_validator`, and the
in-place, **BREAKING** `prb/models/v1` schema evolution (pre-existing PRB documents
without the lead paragraph fail `parse_prb`/`get_prb` until it is added, with
`update_prb`'s guided recovery), citing `feat-132-prb-update`. Added `CHANGELOG.md`
`[Unreleased]` `### Added` (3 bullets: the mandatory lead paragraph + validator,
`create_prb`'s `qa_id`/carry-over, `update_prb`'s recovery guidance) and
`### Changed` (1 **BREAKING** bullet) entries, all citing GitHub issue #132,
matching the file's existing heading/bullet/citation style. Regenerated
`docs/api/`/`docs/GENERATED.md` via `specmgr docs` and `docs/MCP.md` via `specmgr mcp-docs` after the `server.py` docstring edit: confirmed regeneration is
idempotent -- the only diff produced was `docs/api/biz.dfch.specmgr.server.md`'s
mirror of the docstring edit itself; `docs/GENERATED.md` and `docs/MCP.md` showed
zero diff, confirming Phase 2's earlier regeneration already covered the `qa_id`
prompt-schema change. Independently confirmed both JSON schema copies
(`docs/prb_schema.json`, `src/biz/dfch/specmgr/prb/data/prb_schema.json`) still
match a fresh `specmgr schema --type prb` run (no drift). Ran the Task 3.5 final
review: grepped `AGENTS.md`, `server.py`, and `src/biz/dfch/specmgr/prb/data/*.md`
for the old "free of assumed causes" wording and any other stale pre-change PRB
shape references -- none found (Phases 1/2 had already reworded every live
reference; only historical session logs and this README's own history retain the
old phrasing, which is expected and correct). Confirmed
`tests/prb/prompts/test_create_prb.py::test_mentions_no_root_cause_section`'s
asserted wording still matches `prb/data/prb_create_instructions.md`'s current text
verbatim. Quality gate green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `pytest -n auto --cov=src` suite
(3324 passed, unchanged from the end of Phase 2 since Phase 3 added no new tests).
All 7 acceptance criteria (ACC-001 through ACC-007) are met; the feature's status
moves from `in-progress` to `review`.

#### 2026-09-19 15:20:00.000Z - Phase 2 (Prompts) implemented

Implemented Task 2.1-2.6 in full, updating only the `prb` prompt modules/data files
and their own tests (no `prb/models/v1/`, `prb/data/prb_template.md`/`prb_example.md`,
JSON schema, or `tests/prb/models/v1/` changes -- Phase 1 territory, left untouched).
`prb/prompts/create_prb.py`'s signature is now `create_prb(topic: str, qa_id: str | None = None)`, substituting `"(not given -- proceed standalone, asking all 7 5W2H questions)"` when `qa_id` is absent (mirroring `update_prb`'s existing fallback
pattern); its module docstring and `@mcp.prompt` description now describe the optional
QA carry-over. `prb/data/prb_create_instructions.md` was extended from a 0-10-step to
a 0-12-step flow: a new step 2 instructs fetching the linked QA via `get_qa(qa_id)`,
with explicit `QaNotFoundError` handling (surface the failure, then use the `question`
tool to ask standalone-vs-corrected-id, REQ-004) and scanning all 10 `_QaCategory`-
shaped sections (`Elicitation Context` plus the 9 ISO/IEC 25010:2023 characteristics)
for 5W2H-matching Q&A pairs, under the one-pair-to-one-question and non-committal-
counts-as-unanswered rules (REQ-003, explicitly calling out QA's own literal
`_(awaiting response)_` placeholder as a non-committal example); step 3 now asks only
for whichever 5W2H sub-questions remain unanswered (REQ-005); a new step 9 composes the
lead-paragraph sentence via derive-then-confirm from pre-filled What/Who/Why answers in
QA-linked mode, or fresh elicitation of all 4 blanks in standalone mode (REQ-006). The
structure recap (step 1) now includes the mandatory lead paragraph, and the root-cause
note is reworded per REQ-009 ("no `## Root Cause` section exists; the lead sentence
carries the best-known cause by design; formal root-cause analysis remains a separate,
later activity"). `prb/prompts/update_prb.py`'s docstring/description and
`prb/data/prb_update_instructions.md`'s step 1 now narrate an old-shape-PRB recovery
sub-flow (REQ-008): on a `get_prb(id)` parse failure caused by the missing mandatory
lead paragraph, re-read via `get_prb(id, raw=True)`, derive/confirm (or elicit) the 4
blanks from the document's own What/Who/Why answers mirroring `create_prb`'s own
derive-then-confirm flow, insert the composed sentence under the H1, `update` the whole
body, then re-verify via `get_prb(id)` before proceeding with the originally requested
change. Added 10 new tests across `tests/prb/prompts/test_create_prb.py` (`qa_id`
interpolation/fallback, `get_qa`/`QaNotFoundError` handling, scanning all 10 QA
categories, the one-pair-to-one-question/non-committal rules, asking only remaining
questions, the derive-then-confirm lead sentence) and
`tests/prb/prompts/test_update_prb.py` (old-shape recovery via raw re-read, deriving/
eliciting the lead-sentence blanks, inserting under the H1 then proceeding), and
rewrote `test_mentions_no_root_cause_section` per REQ-009's new wording. Both touched
instruction `.md` files were run through the `specmgr_mdformat` tool for house-style
consistency, which reflowed a few existing lines in the process (cosmetic, no wording
changes to unrelated content). Quality gate green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full
`pytest -n auto --cov=src` suite (3324 passed, up from 3314 at the end of Phase 1 --
the 10 new prompt tests). No Phase 3 work was touched.

#### 2026-09-19 13:00:00.000Z - Phase 1 (Schema) implemented

Implemented Task 1.1-1.5 in full: added the mandatory `problem_statement: MarkdownParagraph` field (declared first among `Prb`'s own fields) to
`prb/models/v1/body.py`, with a `field_validator` (`_validate_problem_statement`)
enforcing the fixed template skeleton via a `re.DOTALL` regex fullmatch against
`.text`, mirroring `rsk.models.v1.body.Strategy._validate_value`; updated the module
docstring's layout diagram and the `Prb` class docstring's Parameters section, and
reworded the "No `Root Cause` section" texts per REQ-009. Updated
`prb/data/prb_template.md`/`prb/data/prb_example.md` to show the new lead paragraph
and reworded the example's `## More Information` root-cause note. Regenerated both
JSON schema copies (`docs/prb_schema.json`,
`src/biz/dfch/specmgr/prb/data/prb_schema.json`) via `specmgr schema`; confirmed
`problem_statement` appears in both. Added new tests in `tests/prb/models/v1/`
(`test_body.py`'s `TestProblemStatementMandatoryAndTemplateValidated`/
`TestParsePrbRejectsMissingLeadParagraph`, `test_parser.py`'s
`test_malformed_problem_statement_raises_validation_error`/
`test_old_shape_without_problem_statement_raises_assertion_error`) covering
present+valid, absent (structural `AssertionError`), and malformed-template
(`ValidationError`) cases, plus the dedicated old-shape-rejection test against
`Prb.from_text`. Swept every hand-written PRB-body fixture across `tests/prb/`
(all 9 files named in Task 1.5) and, since the generic `general/tools` test suite
also carries its own per-domain PRB body fixtures, the same sweep was additionally
required (not originally itemized in Task 1.5) across `tests/general/tools/ test_update.py`/`test_set_status.py`/`test_set_classification.py`/`test_delete.py`/
`test_validate.py`'s `_PRB_MINIMAL_BODY`/`_PRB_UPDATED_BODY`/`_PRB_FULL_DOCUMENT`
fixtures and one hardcoded line-offset constant in
`tests/prb/tools/test_get_prb.py::test_windowed_raw_read_coordinates_index_into_the_splice_target`
(shifted by the 2 new lead-paragraph lines). Also updated the `.specmgr/feat/ feat-16-problem-statement/prb_reference.md` fixture file (read by
`test_parser.py::test_parses_full_reference_document`) with the new lead sentence and
reworded root-cause note. Quality gate green: `ruff format --check`, `ruff check`,
`vulture src/ whitelist.py --min-confidence 60` (after adding
`_._validate_problem_statement` to `whitelist.py`'s Pydantic-validator group), and the
full `pytest -n auto --cov=src` suite (3314 passed). No Phase 2/3 work was touched.

#### 2026-09-19 10:40:00.000Z - Plan corrected after a review pass

A review of the plan against the current codebase found six issues, all now corrected
in the sections above: (1) Task 1.5's fixture-sweep list was missing four test files
with their own hand-rolled PRB body fixtures (`tools/test_create_prb.py`,
`tools/test_list_prb.py`, `tools/test__io.py`, `tools/test__paths.py`) -- added; (2) the
Scope exclusion cited the wrong `sysrs` cross-reference heading (`## Problem Statements`, plural H2) instead of the actual `### Problem Statement` (singular, H3,
under `## Business Context and Goals`) -- corrected; (3) REQ-009's `body.py`-docstring
reword target was imprecise (the literal "free of assumed causes" phrase doesn't appear
there; only "No Root Cause section" wording does) -- clarified per-file; (4) Design
Notes conflated "collapse whitespace" with `re.DOTALL` for the soft-wrapped-paragraph
regex -- corrected to specify `re.DOTALL` (the codebase's actual, only precedent) rather
than an unprecedented whitespace-collapsing step; (5) Design Notes overstated what the
`Rasci.intro`/`Ears.intro` precedent proves (both are plain `MarkdownSection1` with no
inherited field ahead of `intro`, so they don't exercise the "own-declared-first after
an inherited field" nuance `Prb` needs) -- scoped precisely; (6) REQ-006 left
unspecified how a single `What` QA answer should populate two distinct blanks
(`[Current state]`/`[specific issue]`) -- added guidance that the prompt drafts its best
split and relies on the required confirmation step to catch a bad one. No requirement,
acceptance criterion, or task numbering changed; only wording/scope precision.

#### 2026-09-18 15:33:31.717Z - Plan revised: blocker cleared, four open decisions resolved

Recorded the reporter's 2026-09-17 13:18 UTC GitHub confirmation of the lead-paragraph
placement (clearing the Blockers entry that had been waiting on it), then revised the
plan around four resolved decisions: (1) the template skeleton is enforced at the code
level via a `field_validator` (mirroring `rsk.Strategy._validate_value`), not left to
prompt guidance alone; (2) the schema evolves in place in `prb/models/v1` rather than a
new `prb/models/v2` package, documented as a **BREAKING** change for any pre-existing
PRB document outside this repo; (3) the new field is named `problem_statement`; (4) the
plan now also covers rewording the "free of assumed causes" design texts the new lead
sentence contradicts (REQ-009), an `update_prb` recovery flow for old-shape documents
whose own `get_prb` read would otherwise fail (REQ-008), QA-id-not-found handling
(REQ-004), a one-pair-to-one-question/non-committal-is-unanswered matching rule
(REQ-003), a derive-then-confirm lead sentence in QA-linked mode instead of 4 fresh
questions (REQ-006), and the previously missing Phase 3 `docs/MCP.md`/`CHANGELOG.md`/
`server.py`/`AGENTS.md` tasks.

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

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-19 19:00:00.000Z - Strengthen the instructions-duplication finding into a sync-guard test, not a comment-only note

The external review flagged `prb_create_instructions.md`/`prb_update_instructions.md`'s
duplicated `What`/`Who`/`Why` -> blank derive-mapping clause as a drift risk but
suggested leaving it as an accepted trade-off (a text-diff test between two prose files
was called "brittle for low payoff"). Decided instead to align the mapping clause itself
to verbatim-identical wording in both files and add a dedicated test asserting that
exact match (Task 5.4) -- the mapping clause is a short, precisely-bounded phrase (not
the surrounding free prose), so a substring-equality test against it is neither brittle
nor high-maintenance, and the project's own conventions already favor drift-guard tests
over documentation-only trade-offs wherever a mechanical check is feasible (e.g. the
packaged-template/example drift-guard test, `docs/prb_schema.json` vs. the packaged copy,
`docs/GENERATED.md` regeneration checks).

#### 2026-09-19 19:00:00.000Z - Decline a Phase 5 task for the unrelated `.opencode/` commit bundling

The external review noted that commit `b97ccf3` bundled unrelated `.opencode/agent/ feat-reviewer.md` and `.opencode/command/review-feature.md` additions into an otherwise
`prb`-scoped docs commit -- scope creep, but harmless (neither file affects `prb/`
runtime behavior, tests, or docs generation) and already merged/pushed. No Phase 5 task
was added for this: it is a commit-history hygiene concern, not a code defect, this
feature's task list has no mandate or mechanism to rewrite already-pushed git history,
and doing so risks disrupting collaborators who may have already based work on this
branch. Recorded here purely so the finding is not silently dropped; future commits
should keep unrelated tooling/config changes in their own commit.

#### 2026-09-19 17:15:00.000Z - Drop the dead capture groups rather than use them for a richer error

REQ-011's fix converts `_PROBLEM_STATEMENT_PATTERN`'s four named capture groups to
non-capturing groups rather than wiring them into a per-blank diagnostic error message.
The existing error (full template plus the actual offending text) is already actionable
enough for a 4-blank template; a per-blank diagnosis would need partial-match logic
(which blank, if any, is the first to fail) for marginal benefit over the simpler fix,
and would reintroduce exactly the greedy-backtracking ambiguity (a blank's own free text
could contain one of the three joiners) that made the groups risky to rely on in the
first place.

#### 2026-09-19 15:20:00.000Z - Prompt renumbering and recovery-flow placement

`prb_create_instructions.md`'s flow was renumbered from steps 0-10 to steps 0-12 (new
step 2 for the QA fetch/scan, new step 9 for composing the lead sentence, everything
after shifted down) rather than using decimal sub-steps (e.g. "2a"), matching this
file's existing plain-integer house style. For `prb_update_instructions.md`, the
old-shape recovery sub-flow (REQ-008) was nested as a lettered/numbered sub-list
*inside* step 1 ("Read current state first") rather than promoted to its own top-level
numbered step -- it is conditional (only triggered by a specific parse failure) and
logically still part of "read current state", so adding it as a new step 2 would have
forced renumbering every later step for a flow most runs never enter. This was a
judgment call, not specified by the plan's task wording.

#### 2026-09-18 15:33:31.717Z - Code-level template enforcement

`problem_statement` carries a `field_validator` enforcing the fixed template's skeleton
via regex fullmatch against its whitespace-collapsed `.text`, mirroring
`rsk.models.v1.body.Strategy._validate_value`'s existing `MarkdownParagraph`-value
pattern, rather than relying on prompt wording guidance alone -- the issue explicitly
asks for "eine einheitliche Struktur" (a unified structure) across all PRB documents,
and the codebase already has a proven pattern for this exact kind of check.

#### 2026-09-18 15:33:31.717Z - In-place `prb/models/v1` schema evolution (BREAKING)

The new mandatory field is added directly to `prb/models/v1`, not a new
`prb/models/v2` package. The only breaking-change precedent in this codebase (QA
v1 -> v2, feat-14) is a wholesale re-shape with no dual-schema read support either way,
and no version-gate/migration mechanism exists for any domain body schema regardless of
which path is chosen -- the frontmatter `version` field tracks the shared `models/md`
framework version, not a per-domain body schema version. A `v2` package would only buy
a cosmetic version label at roughly double the diff (re-pointing every tool/resource/
prompt/schema/test). Documented as a **BREAKING** change for any pre-existing PRB
document outside this repo (`prb` shipped in v0.10.0); the `update_prb` prompt's new
old-shape recovery flow (REQ-008) is the guided remediation path.

#### 2026-09-18 15:33:31.717Z - Field name: `problem_statement`

Named `problem_statement`, not `intro` (the literal `Rasci.intro`/`Ears.intro`
precedent's own field name) -- `intro` reads as "introduction to the document", which
this lead sentence is not; `problem_statement` matches the issue's own requested
`## Problem Statement` heading text and `sysrs`'s existing `### Problem Statement`
cross-reference-list naming, and stays unambiguous in the generated JSON schema and any
validation error path.

#### 2026-09-17 13:18:00.000Z - Lead-paragraph placement confirmed by the reporter

Placement of the fixed "Problem Statement" template sentence as a mandatory lead
paragraph directly under the H1 title (no separate heading) was proposed as a GitHub
comment on issue #132 and confirmed by the reporter (@XyZ-321n) the same day, over the
issue's own originally requested `## Problem Statement` H2 -- confirmed feasible with
zero changes to the shared `models/md` parsing framework via the `Rasci.intro`/
`Ears.intro` precedent.

#### 2026-09-17 09:00:00.000Z - QA-to-PRB matching stays prompt-driven, not code-level

QA-to-PRB 5W2H carry-over is performed by the prompt-driving agent reading the linked
QA document's free-form Q&A content across every category, not a new deterministic,
code-level matcher -- QA v2's un-headed, adjacent Q&A pairs resist rigid keyword
parsing but are straightforward for an LLM-driven prompt to interpret. (The code-level
validator added 2026-09-18 concerns only the PRB lead sentence's own template skeleton,
not QA-to-PRB matching.)

### Related PRs / Commits

- [Issue #132](https://github.com/dfch/biz.dfch.SpecMgr/issues/132): tracking issue for
  this feature (filed in German).

### More Information

GitHub issue #132 was filed in German by @XyZ-321n. This feature's body is an English
translation and elaboration of that issue; the German original on the GitHub issue
itself remains the source of truth for the original request wording.
