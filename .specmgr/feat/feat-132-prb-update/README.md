---
classification: null
created: '2026-09-17 09:57:31.305+02:00'
id: feat-132-prb-update
status: planning
type: feat
updated: '2026-09-18 17:33:31.717+02:00'
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

- REQ-001: `prb/models/v1/body.py`'s `Prb` model gets a new mandatory `MarkdownParagraph`
  field named `problem_statement`, declared first among `Prb`'s own fields (so it lands
  after the existing optional `comment` field, inherited from
  `MarkdownSection1WithComment`, and before `current_state` -- i.e. directly under the H1
  title, no heading of its own), holding exactly one sentence following the template
  `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- mirroring the `general.models.rasci.Rasci.intro`/`general.models.ears.Ears.intro`
  precedent. The template skeleton is enforced at the code level by a `field_validator`
  applying a regex fullmatch against the paragraph's own whitespace-collapsed inline text
  (the sentence can soft-wrap across lines), mirroring
  `rsk.models.v1.body.Strategy._validate_value`'s `MarkdownParagraph`-value precedent --
  raising an actionable `pydantic.ValidationError` naming the expected template and the
  actual text. Requires zero changes to `models/md`.

- REQ-002: The `create_prb` prompt must accept an optional QA document id (`qa_id`) in
  addition to the existing `topic` input.

- REQ-003: When a QA id is supplied, the `create_prb` prompt must fetch that QA document
  (`get_qa`) and scan every one of its Q&A-holding categories (the 10 `_QaCategory`-shaped
  sections: `## Elicitation Context` plus the 9 ISO/IEC 25010:2023 characteristics, not
  only `## Elicitation Context`) for question/answer pairs matching the PRB's 7 5W2H
  sub-questions (What/Why/Where/Who/When/How/How Often), pre-filling any match into the
  corresponding `## Current State` sub-question. Matching rules: each QA pair maps to at
  most one 5W2H sub-question (best match only, never duplicated across two
  sub-questions), and a non-committal QA answer (e.g. "unknown", "not yet answered")
  counts as unanswered, not as a pre-fill.

- REQ-004: When a QA id is supplied but does not resolve (`get_qa` raises
  `QaNotFoundError`), the `create_prb` prompt must surface that failure to the user and
  use the `question` tool to ask whether to proceed standalone (all 7 questions, no
  pre-fill) or retry with a corrected QA id -- never silently fall through to standalone
  behavior without telling the user why.

- REQ-005: The `create_prb` prompt must use the `question` tool to ask only for whichever
  of the 7 5W2H sub-questions were not already answered in the linked QA (or all 7, if no
  QA id was supplied or it did not resolve), explicitly allowing the user to skip any
  question, same as today.

- REQ-006: The `create_prb` prompt must compose the new lead-paragraph Problem Statement
  sentence from its 4 blanks (`[Current state]`/`[specific issue]`/`[stakeholder]`/
  `[underlying cause]`). When a QA id was supplied and 5W2H answers were pre-filled, the
  4 blanks must first be *derived* from those pre-filled answers (`What` ->
  `[Current state]`/`[specific issue]`, `Who` -> `[stakeholder]`, `Why` -> `[underlying cause]`) and the composed sentence *confirmed* with the user via the `question` tool,
  rather than asked as 4 fresh questions; only a blank no pre-filled answer supports is
  asked for directly. In standalone mode (no QA id, or nothing pre-filled), all 4 blanks
  are elicited via the `question` tool as before.

- REQ-007: The `prb` template/example resources (`get_prb_template`, `get_prb_example`)
  and both generated JSON Schema copies (`docs/prb_schema.json` and the packaged
  `src/biz/dfch/specmgr/prb/data/prb_schema.json` behind `specmgr://prb/schema`) must be
  updated to reflect the new mandatory `problem_statement` lead paragraph, landing in the
  same commit as the model change -- the packaged template/example are parsed against the
  model by `tests/prb/tools/test_integration.py`'s drift-guard test.

- REQ-008: The `update_prb` prompt must guide recovery of an old-shape PRB draft (created
  before this change, whose body lacks the now-mandatory `problem_statement` paragraph).
  Because `get_prb(id)` itself will fail to parse such a document post-change, the prompt
  must instruct the agent: on that specific missing-lead-paragraph parse error, re-read
  via `get_prb(id, raw=True)`, elicit/confirm (or derive from the document's own
  What/Who/Why answers, mirroring REQ-006) the sentence's 4 blanks, insert the composed
  sentence directly under the H1, then proceed with whatever change was originally
  requested.

- REQ-009: The existing "problem statements stay free of assumed causes by design"
  design texts must be reconciled with the new lead sentence, which by design now
  carries the best-known cause in its `because [underlying cause]` clause. Reword, in the
  same commit as REQ-001: `prb/models/v1/body.py`'s module and `Prb` class docstrings,
  `prb/data/prb_create_instructions.md`'s structure-recap note, and
  `prb/data/prb_example.md`'s `## More Information` paragraph -- from "a problem
  statement stays free of assumed causes by design" to "no `## Root Cause` section
  exists; the lead sentence carries the best-known cause by design; formal root-cause
  analysis remains a separate, later activity" (or equivalent wording) -- and rewrite the
  prompt test asserting the old wording (`tests/prb/prompts/test_create_prb.py:: test_mentions_no_root_cause_section`) to match.

### Acceptance Criteria

- [ ] ACC-001: `create_prb`/`validate(type="prb")` reject a PRB body missing the mandatory
  `problem_statement` lead paragraph directly under the H1 (before `## Current     State`), with an actionable structural error, *and* reject a present lead paragraph
  whose text does not match the template skeleton, with an actionable field-validation
  error naming the expected template and the actual text.
- [ ] ACC-002: Given a QA id whose document has 5W2H-matching answers spread across
  multiple categories (e.g. one in `## Elicitation Context`, one in `## Reliability`),
  running `create_prb` with that QA id pre-fills those answers into `## Current State`
  without re-asking them, with each QA pair mapped to at most one sub-question.
- [ ] ACC-003: Given a QA id whose document leaves 3 of the 7 5W2H questions unanswered
  (including any non-committal answers, which count as unanswered), running
  `create_prb` asks (via the `question` tool) only for those 3, not the other 4.
- [ ] ACC-004: Running `create_prb` with a nonexistent QA id surfaces the failure and asks
  whether to proceed standalone or retry with a corrected id (REQ-004). Running it
  without a QA id still works standalone, asking for all 7 5W2H sub-questions plus the
  4 lead-paragraph blanks as fresh questions (nothing is pre-filled to derive them
  from).
- [ ] ACC-005: `get_prb_template`/`get_prb_example`, `docs/prb_schema.json`, and the
  packaged `specmgr://prb/schema` copy all show the new mandatory `problem_statement`
  lead paragraph directly under the H1, before `## Current State`.
- [ ] ACC-006: In a QA-linked run with at least one pre-filled 5W2H answer, the lead
  sentence's blanks are derived from those answers and the composed sentence is
  confirmed with the user (not asked as 4 fresh questions, REQ-006); the composed
  sentence passes the code-level template validator.
- [ ] ACC-007: Running `update_prb` against an old-shape PRB (no `problem_statement`
  paragraph) recovers via `get_prb(id, raw=True)` plus sentence insertion (REQ-008),
  then applies the originally requested change, leaving the result parseable by
  `get_prb`.

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
- Any change to `sysrs`'s `## Problem Statements` cross-reference bullet shape.
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
of exactly this H1 -> (mandatory lead paragraph) -> first H2 shape, both built on the
same, unmodified `MarkdownParagraph`/`MarkdownSection.from_text` machinery `prb` will
reuse. Because `comment` is *inherited* from `MarkdownSection1WithComment` rather than
declared on `Prb` itself, `problem_statement` must be declared *first* among `Prb`'s
own fields -- Pydantic orders `model_fields` base-class-first, and `MarkdownStr.from_text`'s
distribution loop walks fields in that same declaration order, so this ordering (not an
explicit position argument) is what actually places `problem_statement` between
`comment` and `current_state`.

The template skeleton itself is validated at the code level, not left to prompt
guidance alone: `rsk.models.v1.body.Strategy._validate_value` is a live precedent for
applying a `field_validator`/regex check against a `MarkdownParagraph` field's own
`.text` (Pydantic's `Field(pattern=...)` cannot apply to a model-typed field directly).
The regex must first collapse internal whitespace before matching, since a soft-wrapped
sentence's `.text` retains its embedded line breaks (mirroring
`general.models.rasci._ROLE_ITEM_PATTERN`'s `re.DOTALL` reasoning for the same
soft-wrap issue).

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

- [ ] Task 1.1: Add the new mandatory `problem_statement: MarkdownParagraph` field to
  `prb/models/v1/body.py`'s `Prb` model, declared first among `Prb`'s own fields, with
  a `field_validator` enforcing the template skeleton `[Current state] is causing     [specific issue], for [stakeholder] because [underlying cause].` via a
  whitespace-collapsed regex fullmatch on the paragraph's `.text`, mirroring
  `rsk.models.v1.body.Strategy._validate_value`. Update the module docstring's layout
  diagram and the `Prb` class docstring's Parameters section, and reword the "no
  Root Cause section" texts per REQ-009.
- [ ] Task 1.2: Update `prb/data/prb_template.md` and `prb/data/prb_example.md` to show
  the new mandatory lead paragraph following the template; reword the example's
  `## More Information` "no root cause analysis ... by design" line per REQ-009.
- [ ] Task 1.3: Regenerate both JSON schema copies (`specmgr schema` for
  `docs/prb_schema.json`; `specmgr schema --type prb --output-dir     src/biz/dfch/specmgr/prb/data` for the packaged copy) and confirm `problem_statement`
  appears in both.
- [ ] Task 1.4: Add/update unit tests in `tests/prb/models/v1/` covering the new field
  (present + valid, absent -> actionable structural error, present but malformed
  template -> actionable field-validation error).
- [ ] Task 1.5: Sweep every hand-written PRB-body fixture across `tests/prb/`
  (`models/v1/test_parser.py`, `tools/test_integration.py`, `tools/test_parse_prb.py`,
  `tools/test_get_prb.py`, `tools/test__write.py`) to insert the new lead sentence;
  add a dedicated old-shape-rejection test asserting a pre-change-shaped body fails
  `Prb.from_text` with an actionable error (documents the REQ-008 recovery trigger).

#### Phase 2: Prompts

- [ ] Task 2.1: Update `prb/prompts/create_prb.py`'s signature to
  `create_prb(topic: str, qa_id: str | None = None)`, substituting a "(not given ...)"
  fallback when absent (the existing `update_prb` instructions pattern); update the
  module docstring (step count/flow) and the `@mcp.prompt` description to mention the
  optional QA carry-over.
- [ ] Task 2.2: Update `prb/data/prb_create_instructions.md`: when a QA id is supplied,
  instruct fetching the QA document via `get_qa` with explicit bad-id handling
  (`QaNotFoundError` -> surface + ask standalone-or-corrected-id, REQ-004); scan every
  Q&A-holding category for answers matching the PRB's 7 5W2H sub-questions under the
  one-pair-to-one-question / non-committal-counts-as-unanswered rules (REQ-003),
  pre-filling matches into `## Current State`.
- [ ] Task 2.3: Instruct the flow (same file) to use the `question` tool to ask only for
  whichever of the 7 5W2H sub-questions remain unanswered (or all 7 if no QA id given
  or it didn't resolve, skips still allowed), and to compose the lead-paragraph
  sentence: derive-then-confirm its 4 blanks from pre-filled What/Who/Why answers in
  QA-linked mode (REQ-006), or elicit all 4 as fresh questions in standalone mode.
- [ ] Task 2.4: Update the structure recap in `prb/data/prb_create_instructions.md` to
  include the new mandatory lead paragraph, and reword the "no `## Root Cause`
  section ... free of assumed causes" note per REQ-009.
- [ ] Task 2.5: Update `prb/prompts/update_prb.py` and `prb/data/prb_update_instructions.md`
  to guide recovery of old-shape PRB drafts (REQ-008): on the missing-lead-paragraph
  parse error from `get_prb`, re-read via `get_prb(id, raw=True)`, elicit/confirm or
  derive the 4 blanks, insert the sentence under the H1, then proceed.
- [ ] Task 2.6: Add/update prompt tests in `tests/prb/prompts/`: `qa_id`
  interpolation/fallback, `get_qa` mention plus bad-id handling, the
  one-pair-to-one-question rule, the derive-then-confirm flow, and old-shape recovery
  via raw re-read; rewrite `test_mentions_no_root_cause_section` per REQ-009.

#### Phase 3: Verification and Docs

- [ ] Task 3.1: Regenerate `docs/api/`/`docs/GENERATED.md` via `specmgr docs` and
  `docs/MCP.md` via `specmgr mcp-docs` (the new `qa_id` prompt parameter changes the
  generated prompt schema).
- [ ] Task 3.2: Update `server.py`'s "Problem statement prompts" docstring line and the
  `prb` bullet in `AGENTS.md` (optional `qa_id`, mandatory validated lead paragraph,
  in-place-v1 **BREAKING** note).
- [ ] Task 3.3: Add `CHANGELOG.md` `[Unreleased]` entries: **Added** (mandatory
  `problem_statement` lead paragraph + template validator; `create_prb`'s optional
  `qa_id` and QA carry-over; `update_prb`'s old-shape recovery) and **Changed
  (BREAKING)** (pre-existing PRB documents without the lead paragraph fail
  `parse_prb`/`get_prb` until it is added; `update_prb` guides the recovery).
- [ ] Task 3.4: Run the full quality gate (`ruff format --check`, `ruff check`,
  `vulture`, `pytest -n auto --cov=src`).
- [ ] Task 3.5: Final review confirming no stale references to the old (pre-change) PRB
  shape, or the old "free of assumed causes" rationale, remain in `AGENTS.md`/
  `server.py` docstrings or the instruction data files.

## Progress

### Current Status

**As of 2026-09-18**: Planning complete. The design was confirmed by the issue reporter
on GitHub (2026-09-17), and the four open implementation decisions -- code-level
template enforcement, in-place `prb/models/v1` evolution, and the `problem_statement`
field name -- were resolved 2026-09-18 (see Decisions Made) and folded into the
Requirements/Acceptance Criteria/Task List above. Implementation has not started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
