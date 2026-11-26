# History: Carry 5-Why/5W2H Answers from QA into PRB + Anchor a Fixed Problem Statement Sentence

#### 2026-09-19 22:00:00.000Z - Phase 6 (Second External-Review Hardening) planned from another external `feat-reviewer` review pass

A second independent `feat-reviewer` review of the merged, Phase-5-complete
implementation found zero Errors (no functional defects) and one Gap plus three
Inconsistencies, none blocking: (1) `_PROBLEM_STATEMENT_PATTERN`'s
greedy-backtracking trade-off (REQ-013) is demonstrated by only one test,
covering the `"is causing"` joiner but not the other two; (2) this file's own
`### Updates` narrative still uses the out-of-vocabulary status word
`"in-progress"` in five entries even though `AGENTS.md` and this file's
frontmatter were already corrected to the actual `FeatFrontmatter.status`
value `progress` in an earlier commit (`a6fbb3d`); (3) the 2026-09-19
21:00:00.000Z Decisions Made entry's claim that "every row's comment column
... starts at the same position (column 50)" is inaccurate -- the file
actually has two distinct comment-start columns (48 and 49), though the
specific `### What Is the Problem?` row Task 5.3 targeted is genuinely
aligned with its own block; (4) a few `AGENTS.md` `prb`-bullet continuation
lines carry inconsistent (3- vs. 2-space) leading whitespace from this
feature's own edits. The review also offered two optional, non-required
Improvement suggestions (a one-sentence regex-anchoring doc note;
parametrizing two near-duplicate tests in
`tests/prb/data/test_instructions_consistency.py`). All four defect-class
findings were accepted and added as REQ-016 through REQ-019/ACC-012 through
ACC-015 and Phase 6 (Tasks 6.1-6.7) above; the two Improvement suggestions
were added as optional, non-ACC-bound Phase 6 tasks (6.5/6.6). `status`
reopened from `review` to `progress` pending Phase 6. This entry is planning
only -- no `prb/`, `AGENTS.md`, or test file has been touched yet.


#### 2026-09-19 21:00:00.000Z - Phase 5 (External-Review Hardening) implemented

Implemented Task 5.1-5.5 in full, touching only
`prb/models/v1/body.py`, `prb/data/prb_create_instructions.md`,
`prb/data/prb_update_instructions.md`, `tests/prb/models/v1/test_body.py`,
`tests/prb/prompts/test_create_prb.py`, and the new
`tests/prb/data/__init__.py`/`tests/prb/data/test_instructions_consistency.py`
-- no other Phase 1-4 territory was touched. In `body.py`, extended
`_PROBLEM_STATEMENT_PATTERN`'s explanatory `#:` comment block with a new
paragraph explicitly naming the greedy-backtracking trade-off (REQ-013): a
blank's own free text containing a literal joiner substring (e.g.
`" is causing "`) can still produce a false-positive template match, and why
this is deliberately left unfixed (cross-referencing the 2026-09-19
17:15:00.000Z Decisions Made entry). Added
`test_blank_containing_a_literal_joiner_substring_still_matches_documented_trade_off`
to `TestProblemStatementMandatoryAndTemplateValidated`, constructing a
`problem_statement` whose `[Current state]`/`[specific issue]` blank text
itself contains a second, literal "is causing" occurrence and asserting
`Prb(**kwargs)` still succeeds (a documentation test, not a behavior change);
`test_malformed_template_raises_validation_error_naming_template_and_text`
was left untouched and still correctly fails on genuinely non-matching text
(ACC-009). Independently re-verified Task 5.3's target: the module docstring
ASCII layout diagram's `### What Is the Problem?` row's comment column
already aligns with every sibling row (all at column 50, confirmed via a
column-index check) -- the one-space misalignment the plan targeted had
already been incidentally resolved by Phase 1's own docstring edit adding the
`problem_statement` row, so no further code change was made for it (only Task
5.1's comment-block extension touched this file). Added a worked example to
`prb_create_instructions.md`'s one-pair-to-one-question rule (REQ-014): a QA
pair ("When does the checkout page time out?" / "During peak traffic hours,
right at the payment confirmation step") that could plausibly answer both
`### When Was the Problem First Observed?` and
`### Where Is the Problem Observed?`, and how "best match only" resolves it
by picking the sub-question the QA pair's own question wording most directly
matches. Added
`test_one_pair_to_one_question_rule_has_a_worked_example` to
`tests/prb/prompts/test_create_prb.py`, alongside the existing
`test_mentions_one_pair_to_one_question_rule` (ACC-010). Aligned the
`What`/`Who`/`Why` -> 4-blank derive-mapping clause to the plan's exact,
verbatim wording in both `prb_create_instructions.md` (step 9) and
`prb_update_instructions.md` (step 1's old-shape recovery sub-list),
replacing each file's own independently-paraphrased version (REQ-015); added
`tests/prb/data/__init__.py` and
`tests/prb/data/test_instructions_consistency.py`, which loads both packaged
`.md` files via `general.tools._packaged_data.read_packaged_text` and asserts
the exact clause string appears verbatim in both (ACC-011). Ran both edited
instruction files through the `specmgr_mdformat` tool for house-style
consistency (cosmetic reflow of the newly added worked-example bullet only;
`prb_update_instructions.md` was already formatted, no change). Quality gate
green: `ruff format --check`, `ruff check`,
`vulture src/ whitelist.py --min-confidence 60`, and the full
`pytest -n auto --cov=src` suite (3331 passed, up from 3327 at the end of
Phase 4 -- the 4 new tests: 1 in `test_body.py`, 1 in `test_create_prb.py`,
2 in the new `test_instructions_consistency.py`). All 11 acceptance criteria
(ACC-001 through ACC-011) are now met; the feature's status moves from
`in-progress` back to `review`.


#### 2026-09-19 20:00:00.000Z - Phase 5 task wording refined ahead of implementation

Refined Phase 5's task wording ahead of implementation, based on further research: (1) Task 5.1 now specifies the exact demonstration approach -- embedding a duplicate literal "is causing" inside the `[Current state]`/`[specific issue]` blank -- rather than leaving the test construction unspecified; (2) Task 5.3's ASCII-diagram misalignment was traced via `git show d41e05f:src/biz/dfch/specmgr/prb/models/v1/body.py` (the pre-feat-132, feat-16-era version of the file) to a genuine, pre-existing one-row bug on the `### What Is the Problem?` line, unrelated to this feature's own edits, resolving the earlier ambiguity between fixing that one row versus realigning the whole table; (3) Task 5.4 now locks in the exact shared derive-mapping clause wording both instruction files must share verbatim, plus the new test module's exact location (`tests/prb/data/test_instructions_consistency.py`), removing any remaining wording latitude for whoever implements it. No `prb/` source, test, or data file has been touched by this update -- planning only.


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
