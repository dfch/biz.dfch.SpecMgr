---
classification: null
created: '2026-11-01T07:22:27.849+01:00'
id: feat-247-dec-outcome-blocks
status: planning
type: feat
updated: '2026-11-01T11:15:00.000+01:00'
version: 1.0.0
---

# Feature: Relax DEC Decision Outcome to Accept Multiple Blocks

## Plan

### Overview

The `dec` parser requires `## Decision Outcome` to hold exactly one lead paragraph (`DecisionOutcome.statement`) before the first `###` sub-section; any further block (a second paragraph, a bullet list of sub-decisions, a code block) is rejected with "text left over after processing all fields". ADR has no such restriction, so about 20 of the 46 ADRs in `docs/adr/` (for example `750842b2`, `92cc4ce8`, `356d8781`) cannot be converted to DEC verbatim. This feature (GitHub issue #247) relaxes `DecisionOutcome` so that further markdown blocks may follow the mandatory lead paragraph, which unblocks the UUID-preserving ADR to DEC migration of GitHub issue #46 without rewriting any decision text.

### Requirements

- REQ-001: `## Decision Outcome` MUST accept zero or more further markdown blocks after the mandatory lead paragraph and before the first `###` sub-section; the accepted block kinds are paragraphs, bullet lists, ordered lists and code blocks, and every other distinct token kind (block quotes, comments, horizontal rules, H4+ headings, raw HTML) MUST stay rejected; pipe-table content is a paragraph to the shared commonmark tokenizer (which has no table token) and is therefore accepted, consistent with the lead paragraph's existing behavior (confirmed Option A, see Decisions Made).
- REQ-002: The lead paragraph MUST stay mandatory and MUST stay the value of the first field of `DecisionOutcome`, `statement` (a `MarkdownParagraph`, position and meaning unchanged); a section whose first block is not a paragraph (a bare list, a `###` heading, nothing) MUST still be rejected.
- REQ-003: A DEC document using the extra blocks MUST round-trip byte-exact through parse and then model-to-text (DEC has no renderer, and none is introduced), and the extra blocks MUST be visible in `model_dump()` output.
- REQ-004: `### Consequences` and `### Confirmation` MUST keep their position, optionality and meaning; a document without extra blocks MUST parse to the same result as before; the schema version stays `v1` because the relaxation is additive and every previously valid document still parses.
- REQ-005: The change MUST be confined to the `dec` domain; no other domain, no shared `models/md` rule and no DEC frontmatter field changes.
- REQ-006: The generated artifacts (both copies of `dec_schema.json`, the DEC template and example if they change, `docs/api/*`, `docs/MCP.md`, `docs/GENERATED.md`) MUST be regenerated and the DEC create/update instructions MUST describe the relaxed rule.

### Acceptance Criteria

- [ ] ACC-001: A DEC whose `## Decision Outcome` has a lead paragraph followed by a second paragraph and a bullet list parses via `parse_dec` and the generic `validate` tool (`type="dec"`), and the `statement` field holds the first paragraph while the new optional `further_blocks` field (the `OutcomeBlocks` leaf) holds the remainder (REQ-001, REQ-002).
- [ ] ACC-002: A DEC whose `## Decision Outcome` starts with a bullet list, starts with `### Consequences`, or is empty is still rejected with an actionable error (REQ-002).
- [ ] ACC-003: The same document round-trips byte-exact through parse and model-to-text, and the extra blocks appear in `model_dump()` under `outcome.further_blocks.text` (REQ-003).
- [ ] ACC-004: All pre-existing `tests/dec/` tests pass unchanged, including the i18n tests that read the lead paragraph; new tests are additive only (REQ-004).
- [ ] ACC-005: `git diff` of the change touches no file outside the `dec` package, its tests, the DEC data files, the generated docs and `CHANGELOG.md` (REQ-005, REQ-006).
- [ ] ACC-006: Both copies of `dec_schema.json` are regenerated and `specmgr docs` leaves no drift (REQ-006).
- [ ] ACC-007: Committed regression fixtures derived from the outcomes of the ADRs `750842b2`, `92cc4ce8` and `356d8781` parse without "text left over" in `DecisionOutcome` (REQ-001).
- [ ] ACC-008: The DEC create and update instruction texts (`dec_create_instructions.md`, `dec_update_instructions.md`) describe that further paragraphs, lists and code blocks may follow the lead paragraph (REQ-006).
- [ ] ACC-009: A block placed after `### Consequences` or between `### Consequences` and `### Confirmation` that violates the H3 order, and a block quote, horizontal rule, comment or H4+ heading inside the outcome lead, are still rejected (REQ-001, REQ-004).

### Scope

#### Included

- Changing the `dec` body model (`dec/models/v1/body.py`) so `DecisionOutcome` accepts the extra blocks after the lead paragraph.
- Parser, model and tool-level tests, including the rejected shapes, the byte-exact round-trip, the committed ADR-derived fixtures and one translated-variant i18n test.
- Regenerating both copies of `dec_schema.json` and the generated docs, and updating the DEC create/update instruction texts, template/example and AGENTS.md wording where they state the one-paragraph rule.
- A CHANGELOG `[Unreleased]` entry.

#### Explicitly Out Of Scope

- Any change to the DEC frontmatter, to other domains or to the shared `models/md` engine.
- Accepting block quotes, comments, horizontal rules, H4+ headings or raw HTML tokens such as `<d>` in the outcome lead (pipe-table content is a paragraph to the shared commonmark tokenizer, which has no table token, and is therefore accepted as one -- confirmed Option A, see Decisions Made); the migration handles raw HTML mechanically.
- The ADR to DEC conversion itself and the removal of the ADR artifact type (GitHub issue #46).
- Relaxing any other DEC section.

### Dependencies

#### Depends On

- None.

#### Blocks

- FEAT feat-46-remove-adr (GitHub issue #46): the rollout of the ADR to DEC conversion needs this change merged first; that feature currently exists only on its own branch `feat-46-remove-adr`, not on `dev`.

### Design Notes

Today `DecisionOutcome` declares `statement: MarkdownParagraph`, then the optional `consequences` and `confirmation` H3 sections; the engine leaves the second block of the lead as leftover text. The task is to find the smallest model change that keeps `statement` as the first paragraph and absorbs the remaining blocks into a new optional field (for example a list of further blocks declared before the H3 fields), so that the existing field order, the strict section order and the generated schema stay stable. Task 100.100 decides the exact shape after a short spike against the engine; candidates are a trailing-blocks field on `DecisionOutcome` or a dedicated leaf class that consumes everything up to the next heading. Selection criteria, in order: smallest schema delta, unchanged `statement` field and field order, byte-exact text round-trip, unchanged H3 ordering rules. If neither candidate works without a `models/md` change, stop and re-plan instead of changing the shared engine. The rule that the lead must be a paragraph (REQ-002) comes from the field order itself and must not be weakened.

The change goes inside `## Decision Outcome` only, between the H2 heading and the first `###` sub-section; nothing under the H1 or in any other section changes. After the spike, update the field names in REQ-002, ACC-001 and ACC-003 if they differ from the wording above.

Every list item in this document is written as a single physical line (the soft-wrap rule of GitHub issue #99).

### Related Decisions

- None; if the spike shows that `models/md` must change, stop and re-plan.

### Task List

#### Phase 100: Spike and Design

- [x] Task 100.100: Spike the engine behaviour for a block sequence after a leaf `MarkdownParagraph` and choose the model shape (new optional field or dedicated leaf) using the selection criteria in Design Notes, recording the choice in Decisions Made; if `models/md` would have to change, stop and re-plan.
- [x] Task 100.110: After the spike, align the field names used in REQ-002, ACC-001 and ACC-003 with the chosen shape.

#### Phase 110: Implementation

- [ ] Task 110.100: Change `DecisionOutcome` in `dec/models/v1/body.py` per the chosen shape, with docstrings.
- [ ] Task 110.110: Check every consumer of the lead paragraph for assumptions about a single-paragraph lead: the i18n tests (`tests/dec/tools/test_i18n_language.py`, `test_i18n_write.py`), the DEC create/update instruction texts, the DEC prompts and resources.
- [ ] Task 110.120: Add tests in `tests/dec/models/v1/test_body.py` and `test_parser.py` for ACC-001, ACC-002, ACC-003 and ACC-009 (including the rejected shapes: bare list first, `### Consequences` first, empty, extra block after or between the H3 sections, block quote, horizontal rule, comment, H4+; and, per the confirmed Option A, a pipe-table content accepted as a paragraph), and run the existing `tests/dec/` suite for ACC-004.
- [ ] Task 110.130: Add tool-level tests in `tests/dec/tools/` for `parse_dec` and the generic `validate` (`type="dec"`) with the relaxed shape, and one i18n test with a translated variant that carries extra blocks.
- [ ] Task 110.140: Commit regression fixtures derived from the outcomes of the ADRs `750842b2`, `92cc4ce8` and `356d8781` and a test asserting they parse (ACC-007).

#### Phase 120: Generated Artifacts and Documentation

- [ ] Task 120.100: Regenerate both copies of `dec_schema.json` (`src/biz/dfch/specmgr/dec/data/` and `docs/`), the API docs, `docs/MCP.md` and `docs/GENERATED.md` with `specmgr schema`, `specmgr docs` and `specmgr mcp-docs`, update the `dec/models` and `dec/models/v1` export lists and `whitelist.py` if a new class is added, and confirm no drift.
- [ ] Task 120.110: Update `dec_create_instructions.md` (lines 28-30) and `dec_update_instructions.md` (line 50) for ACC-008, the DEC template/example (`dec_template.md`, `dec_example.md`) if they describe the one-paragraph lead, and AGENTS.md's DEC bullet if it states the rule; record in Decisions Made whether AGENTS.md needed a change.
- [ ] Task 120.120: Add the CHANGELOG `[Unreleased]` entry.

#### Phase 130: Verification

- [ ] Task 130.100: Run the local quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src --cov-report=`).
- [ ] Task 130.105: Review `git diff --stat` against ACC-005 and confirm no file outside the allowed set changed.
- [ ] Task 130.110: Run the one-off in-memory trial conversion of the 46 ADRs, record the result as a snapshot in Updates (before: 46 total, 20 blocked, 26 clean; expected after: 46 clean for this rule), and hand the result to feat-46.

## Progress

### Current Status

**As of 2026-11-01**: Planned from GitHub issue #247, the prerequisite found while reviewing the feat-46 migration plan. The plan was refined (feat-refiner) and the findings were applied; the Phase 100 engine spike is complete and the model shape is chosen (a dedicated `OutcomeBlocks` leaf used as the new optional `further_blocks` field of `DecisionOutcome`); no source code has been changed yet.

**Handover**: the next step is Phase 110, the implementation. The spike's full design record -- the exact leaf `get_extent` contract, the evidence for all four selection criteria, the rejected-candidate analysis, and the "tables are token-wise paragraphs" finding -- is in Decisions Made.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 10:15:00.000Z - Option A confirmed for the "tables" finding

The orchestrator (acting on the user's explicit choice) confirmed Option A: the rejected-kinds contract is enforced per distinct token kind, and pipe-table content -- a paragraph to the shared commonmark tokenizer, which has no table token -- is accepted, consistent with the lead paragraph's existing behavior. REQ-001, ACC-009, the Scope out-of-scope line, and Task 110.120's rejected-shape enumeration were aligned to it, and the 08:30 Decisions Made entry records the confirmation plus its supersession of the 07:45 "tables stay rejected" clause. The `OutcomeBlocks`/`further_blocks` model shape is unchanged.

#### 2026-11-01 08:30:00.000Z - Phase 100: engine spike run, model shape chosen

Ran the Task 100.100 spike as a throwaway script against the real `models/md` engine and the real `dec` body classes (52/52 checks green, baseline `tests/dec` suite 356 passed): the dedicated `dec`-local leaf `OutcomeBlocks` with a custom `get_extent`, used as a new optional `further_blocks` field on `DecisionOutcome` between `statement` and `consequences`, satisfies all four selection criteria without touching `models/md` -- byte-exact round-trip over the accepted block set, the rejected kinds rejected with actionable errors, and no-extra-blocks documents parsing to exactly today's result. Candidate C1 (existing engine types) was rejected with evidence; the "tables are token-wise paragraphs" finding was recorded. Task 100.110 aligned the field names in REQ-002, ACC-001 and ACC-003 to the chosen shape. No repo file changed other than this README.

#### 2026-11-01 07:45:00.000Z - Plan refined

Applied the feat-refiner findings: defined the accepted block set, added ACC-008 and ACC-009, made ACC-007 reproducible through committed fixtures, added the tool-level, i18n and diff-scope tasks, listed the full set of generated artifacts, aligned the round-trip wording with the absence of a DEC renderer, and fixed the `Blocks` reference to the `FEAT <id>` form.

#### 2026-11-01 06:22:27.849Z - Created

Planned from a trial conversion of the 46 ADRs through the real `parse_dec`: 20 failed only because of the single-paragraph lead rule of `## Decision Outcome`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 08:30:00.000Z - Spike (Task 100.100): chosen shape is the dedicated `dec`-local leaf `OutcomeBlocks` as the new optional `further_blocks` field

- Chosen shape (candidate C2): one new leaf class `OutcomeBlocks` in `dec/models/v1/body.py` -- a `MarkdownStr` subclass with NO `@markdown` metadata, mirroring this file's own `UpdateEntryContent` precedent -- plus one new OPTIONAL field `further_blocks: OutcomeBlocks | None = Field(default=None, ...)` on `DecisionOutcome`, declared BETWEEN `statement` and `consequences`; the final field order is `statement`, `further_blocks`, `consequences`, `confirmation`. `DecisionOutcome` itself is edited in place (its `SPACE_SEPARATED` alias derivation of "Decision Outcome" is untouched), and `OutcomeBlocks` overrides only `get_extent` and adds a `text` computed property returning `_value` verbatim (the `model_dump()` visibility, REQ-003); its `from_text`/`__str__` stay the base `MarkdownStr` leaf behaviour (store/emit the exact `mdformat`-normalized slice), which is what makes the round-trip byte-exact.
- `OutcomeBlocks.get_extent` contract: after the standard `text == format_text(text)` precondition and `parse()`, return `0` (field absent) unless the FIRST token is one of the four accepted block-start kinds (`paragraph_open`, `bullet_list_open`, `ordered_list_open`, `fence`); otherwise walk the token stream with a depth counter (shifted by every token's own `nesting`) and treat a token as a new top-level block when it has a 2-element `.map`, is seen at depth 0, and has one of the known block-start types (`paragraph_open`, `bullet_list_open`, `ordered_list_open`, `fence`, `heading_open`, `blockquote_open`, `html_block`, `code_block`, `hr`); the run STOPS at the first non-accepted top-level block -- in particular at the first heading of ANY level (h1-h6) -- by returning that block's start line (`m[0]`, exclusive), and otherwise accumulates the run extent as the max `m[1]` over all mapped tokens (end of text when the run reaches it).
- `statement` stays FIRST and mandatory; the existing field order is unchanged; "the lead must be a paragraph" (REQ-002) still falls out of field order alone -- a bare list, a `###` heading, or nothing as the first block yields the same actionable `expected MarkdownParagraph, found no match` error naming `statement` as today (spike case e1-e6, message captured in the spike output).
- Spike evidence (throwaway script over the REAL unmodified engine and the REAL `dec` classes; 52/52 checks green; baseline `tests/dec` 356 passed before the run): (a) lead + second paragraph + bullet list parses, `statement.text` is the lead, `further_blocks.text` is the remainder verbatim, `str(model) == input`; (b) lead + ordered list round-trips byte-exact, including a single item starting at 2 (mdformat-stable under the engine's `number=True` option); (c) lead + fenced code block (with and without info string) round-trips byte-exact, and a mixed paragraph + list + fence + paragraph run before `### Consequences` round-trips byte-exact; (d) a lead-only section parses to EXACTLY today's `DecisionOutcome` result (identical `statement`/`consequences`/`confirmation` values, identical `str()`, identical `model_dump()` except the new `further_blocks: None` key); (e) bare list first, `### Consequences` first, and an empty outcome body all still raise `AssertionError`; (f) a block quote, an HTML comment, and an H4 heading after the lead are all rejected with the actionable "text left over after processing all fields" error (the run stops before them, so they stay unconsumed -- also after an accepted run), and an indented code block is normalized to a fence by `format_text` before parsing (accepted as a fence, so `code_block` in the stop-set is defensive only); (g) `### Consequences`/`### Confirmation` work with and without further blocks preceding them, and the reversed-H3-order and unknown-H3 rejections are preserved; (h) a full `Decision`-level document with the extra blocks round-trips byte-exact, the H2 section extent still stops before the next H2, and `model_dump()["outcome"]["further_blocks"]["text"]` carries the extra blocks.
- Rejected candidate (C1, for the record): a plain `MarkdownStr` blob field (the `UpdateEntryContent` shape) is TOO GREEDY -- the spike showed it swallowing `### Consequences` into the blob (its position/optionality/meaning break, criterion 4) and silently absorbing a block quote (rejected-kinds break); a composite `MarkdownParagraph` subclass cannot start with a list or fence (both `get_extent` probes returned 0) and cannot express an unbounded mix of block kinds; a `list[...]` of generic leaf types matches only one kind at a time and re-parses list items (the documented tight-list non-byte-exact exception). No existing engine type consumes "a run of mixed paragraph/list/fence blocks up to the next heading of any level", which is why a dedicated `dec`-local leaf is required and is the smallest sufficient delta (criterion 1).
- Finding on "tables" (REQ-001's rejected-kinds list): the engine's `MarkdownIt("commonmark")` tokenizer has NO table token kind -- a GFM-style pipe table tokenizes as a single paragraph (`paragraph_open`/`inline`/`paragraph_close`, spike recon case "pipe 'table'"), so pipe-table content is indistinguishable from paragraph content at the level the engine operates, and a pipe table in the LEAD position is already accepted today as a `statement` paragraph. The rejected-kinds contract is therefore enforced per distinct token kind (block quote -> `blockquote_open`, comment -> `html_block`, H4+ -> `heading_open` h4-h6, raw HTML -> the `parse()` rejection itself, plus `hr`/`code_block` defensively), and pipe-table content is treated as a paragraph exactly like any other paragraph (accepted in the lead today and after this feature; after the lead only as a consequence of the paragraph relaxation). Rejecting it by text pattern instead would break criterion 4 (a no-extra-blocks document with a pipe-paragraph lead would parse to a different result than today) and has no engine precedent in any domain; implementing it would require a GFM table plugin on the shared tokenizer, i.e. a `models/md` change this feature does not make. This reading is confirmed (Option A, by the user, 2026-11-01) and is the authoritative interpretation of the rejected-kinds contract; it supersedes the "block quotes, tables, comments and H4+ headings stay rejected" clause of the 07:45:00.000Z "Refinement decisions" entry, which is kept otherwise untouched as a historical record.
- Explicit confirmation: the shared `models/md` engine was NOT changed -- the spike imported and ran it unmodified, and the entire change fits in `dec/models/v1/body.py` (one new leaf class + one new optional field), per REQ-005.

#### 2026-11-01 07:45:00.000Z - Refinement decisions

- No shared-engine fallback: if the spike shows that `models/md` must change, stop and re-plan; REQ-005 and ACC-005 stay strict and no decision record is pre-planned for it.
- Accepted further blocks are paragraphs, bullet lists, ordered lists and code blocks only; block quotes, tables, comments and H4+ headings stay rejected, which also keeps the i18n heading skeleton unaffected.
- ACC-007 is proven by committed fixtures derived from three representative ADR outcomes; the full 46-ADR run is a one-off manual check recorded as a snapshot, because it depends on the feat-46 conversion rules and on `docs/adr/`, which that feature removes.
- The schema stays at `dec/models/v1`: the relaxation is additive and non-breaking.
