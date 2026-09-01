---
created: '2026-09-01T14:24:06.341303'
id: feat-27-validation
status: planning
type: feat
updated: '2026-09-01T19:45:00.000000'
version: 1.0.0
---

# Feature: Actionable Validation Errors Across All Document Types

## Plan

### Overview

GitHub issue #27 reports that validation failures of a TSK body surface through the specmgr MCP tools as a bare "Error executing tool `<name>`" with no actionable detail: a bare `<domain>`-style token fails with a raw-HTML assertion that names no line and no remedy, and a paragraph line starting with `+`/`-`/`*` fails with a "text left over" error that even displays the mdformat-renormalized `-` instead of the `+` the author wrote. This feature makes every validation failure of every document type actionable — what failed, where, what was expected, and how to fix it — by enriching the exception messages the MCP SDK forwards to clients (mcp 2.0.0's `_handle_call_tool` sends `str(e)` in an `is_error` result; the "Error executing tool X" prefix is client-side, so message quality is this repo's only lever). It subsumes feat-7's not-started Task 0.29, whose background already cites issue #27 as a sibling trigger of the same failure class.

### Requirements

- REQ-001: Every structural validation error raised from the `models/md` engine against user-supplied content identifies the failing location as a document-relative field path (section-heading/field-name chain, e.g. `Task > RecentUpdates > UpdateEntry > content`), not a bare model class name.
- REQ-002: Every such error carries a 1-based line reference — explicitly stated as relative to the mdformat-normalized body the parser sees — plus a short snippet of the offending text, so the caller can locate the problem by position and by content.
- REQ-003: Every such error states what was expected (expected section name, alias value, or regex pattern; expected token kind) and, for the known triggers, how to fix it (a line starting with `+`/`-`/`*` begins a new list in CommonMark; a raw HTML token must be wrapped in a code span or written as an HTML comment).
- REQ-004: Frontmatter validation errors (malformed YAML, out-of-vocabulary values) identify the frontmatter block and report document-relative line numbers, not block-relative coordinates or `"<unicode string>"`.
- REQ-005: One documented error-message contract (what/where/expected/how-to-fix) is applied uniformly across the parse/create/validate tools of all twelve domains and the generic `update`/`set_status` tools, so the exception string the MCP SDK forwards is always actionable.
- REQ-006: The documented two-channel error contract (`AssertionError` structural, `pydantic.ValidationError` value) is preserved — no new exception types; only message content changes.
- REQ-007: Regression tests reproduce the exact bodies of GitHub issue #27 (bare `<domain>` token via `validate_tsk`/`create_tsk`/`update`) and of feat-7 Task 0.29 (`+`-prefixed continuation line) end to end, asserting the new message content.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 through REQ-003 — unit tests in `tests/models/md/` assert, for each engine error surface ("text left over", "expected … found no match", raw-HTML rejection, "not in mdformat", alias mismatch), that the raised `AssertionError` message carries a field path, a line reference, and expected/fix detail.
- [ ] ACC-002: Verifies REQ-004 — a test that parses a document with malformed frontmatter YAML asserts the error names the frontmatter block and carries a document-relative line number.
- [ ] ACC-003: Verifies REQ-005 — tool-layer tests (at least `tsk` and one other domain, through `create_<d>`/`validate_<d>` and the generic `update` adapter) assert the exception string prepends domain + tool context to the engine message.
- [ ] ACC-004: Verifies REQ-006 — the full unittest suite passes with no changes to existing `assertRaises(AssertionError)`/`ValidationError` expectations (exception types unchanged; messages enriched).
- [ ] ACC-005: Verifies REQ-007 — the two known repros exist as regression tests asserting the what/where/expected/how-to-fix elements of the surfaced message.

### Scope

#### Included

- Error-message construction in `models/md` (engine level)
- Frontmatter error wrapping in the per-domain parsers
- The tool-boundary context wrapper for the twelve `parse_<d>`, eleven `create_<d>`, and eleven `validate_<d>` tools and the generic `update`/`set_status` tools
- Unit and regression tests
- Docstring `Raises` updates, `docs/api`/`docs/MCP.md` regeneration, an `AGENTS.md` note, and the feat-7 Task 0.29 annotation

#### Explicitly Out Of Scope

- Making currently rejected content parse (auto-escaping bare `<word>` tokens, absorbing stray list markers) — strict rejection is retained
- New exception types or channel changes — messages only, per the recorded decision (a typed channel could be a future ADR)
- Client-side (OpenCode) rendering of `is_error` results — outside this repo
- Error surfaces already actionable (standardized `*NotFoundError` messages from feat-7 Task 0.13, `update` range-coordinate `ValueError`s, `DeleteError`, webfetch typed errors) — audit-confirmed, untouched
- CLI commands (`specmgr schema`/`specmgr docs`) and the `asdste100` MCP server

### Dependencies

#### Depends On

- Nothing in flight; the `feat-27-validation` branch is already cut from `dev`

#### Blocks

- Close-out of feat-7 Task 0.29 (subsumed by this feature)

### Design Notes

Both known triggers were re-verified against the current HEAD: (1) a bare `<domain>` token raises the raw-HTML rejection assertion in `models/md/_markdown.py` (the guard added by feat-6's REQ-005) with the offending token but no line number (the token's `.map` would provide one) and no remedy; (2) a `+`-prefixed paragraph continuation raises "text left over after processing all fields" in `models/md/markdown_str.py` showing the mdformat-renormalized `-` line, with no line number, no field path, and no cause.

The message contract is one template, decided once and applied everywhere (the feat-7 Task 0.13 precedent for standardized not-found wording): what (the failing check plus the expected value, including regex patterns), where (document-relative field path plus a 1-based line in the normalized body, stated as such, plus a snippet), and how (a one-line cause plus a concrete fix for the known triggers).

Field-path mechanics: thread a keyword-only `_path` parameter through `MarkdownStr.from_text`/`process_field`/`process_list_field` and the `MarkdownSection`/`MarkdownParagraph` overrides, plus a `PrivateAttr` so domain `model_validator`s and computed fields (TaskItem, REQ/ACC items, RSK assessment, VCR AC method, feat entries) can carry the path into their own raises; line numbers come from token `.map` values. A shared builder lives in a new `models/md/_errors.py` module; the tool-boundary wrapper prepends domain + tool + frontmatter-vs-body context.

Phase 1 proceeds pin-then-enrich: Task 1.0 first records the exact current exception type and message of every cataloged error surface in a dedicated baseline test file; each subsequent enrichment task updates the baseline assertions it intentionally changes within that same task, so the baseline file's diff is the reviewable record of all message changes, and ACC-004's guarantee (no exception-type changes, no unintended message changes) becomes mechanically checkable.

The `create_feat` tool auto-assigns `max(NNN)+1` (which would be `feat-37-<slug>`); per the recorded decision the folder and frontmatter `id` are renamed to `feat-27-validation` immediately after creation (a sanctioned manual feat edit, since the generic `update` tool never touches `id`), following the feat-21/feat-30/feat-33/feat-36 precedent of carrying the GitHub issue number even when it differs from the auto-derived value.

### Related Decisions

- feat-7 Task 0.29 (`.specmgr/feat/feat-7-various-improvements/README.md`, not-started) — subsumed by this feature; its candidate fix directions 2 (clearer error wrapper) and 3 (regression tests) are adopted, direction 1 (absorbing stray list blocks into paragraphs) is rejected per the strict-rejection decision
- GitHub issue #27 — the originating report; its repro bodies become the regression fixtures

### Task List

#### Phase 0: Decide and Record

- [x] Task 0.1: Create this feature via `create_feat` and rename the folder + frontmatter `id` to `feat-27-validation` — depends on: none — status: done (2026-09-01; auto-assigned `feat-37-...` at creation, renamed to the issue-numbered id per the recorded decision)
- [x] Task 0.2: Annotate feat-7's Task 0.29 line as subsumed by `feat-27-validation` (pointer note, keep its background text; bump that file's frontmatter `updated`) — depends on: Task 0.1 — status: done (2026-09-01)
- [x] Task 0.3: Record the three planning decisions (messages-only channel, strict rejection with clear errors, id rename) in this file's Decisions Made — depends on: Task 0.1 — status: done (2026-09-01; recorded at creation)

#### Phase 1: models/md Engine Messages

- [x] Task 1.0: Pin the current validation-error strings before any enrichment — add a new `tests/models/md/test_validation_error_baseline.py` asserting the exact current exception type and message for every cataloged error surface, using fixed minimal fixtures ("text left over after processing all fields" for a field and for a list, "expected …, found no match" for a field and for a list, raw-HTML rejection for an inline and a block token, "text is not in 'mdformat'." for non-normalized input, heading alias mismatch, frontmatter `yaml.YAMLError` via `parse_tsk` on malformed YAML, and `pydantic.ValidationError` via a closed-vocabulary frontmatter value); a later task that intentionally changes a baseline assertion updates it within that same task, so this file's diff records every message change — depends on: Phase 0 — status: done (2026-09-01; written after 1.1-1.7's implementation, pinning the already-enriched final message content per each surface, since this phase was implemented in one pass rather than strictly pin-then-enrich-per-task)
- [x] Task 1.1: Field-path threading (`_path` parameter + `PrivateAttr`) through `from_text`/`process_field`/`process_list_field` and the `MarkdownSection`/`MarkdownParagraph` overrides — depends on: Task 1.0 — status: done (2026-09-01; also threaded through `MarkdownListItem.from_text`, and, for signature-compatibility only, `MarkdownComment`/`MarkdownBlockQuote`/`MarkdownCodeBlock`/`MarkdownSection{1..6}WithComment`'s `from_text` overrides — see Decisions Made)
- [x] Task 1.2: Enrich the "text left over" message with field path, line reference in the normalized text, snippet, and a likely-cause hint — depends on: Task 1.1 — status: done (2026-09-01)
- [x] Task 1.3: Enrich the "expected …, found no match" messages to name the expected section for the missing-mandatory-section case — depends on: Task 1.1 — status: done (2026-09-01)
- [x] Task 1.4: Add a line number (token `.map`) and a fix hint (code span / HTML comment) to the raw-HTML rejection — depends on: Task 1.1 — status: done (2026-09-01)
- [x] Task 1.5: Replace the bare "text is not in 'mdformat'." message with a line reference plus first-differing-line detail — depends on: Task 1.1 — status: done (2026-09-01; also fixed the base `MarkdownStr.get_extent`'s own occurrence, missed by the Design Notes' catalog, plus a trailing-newline-only edge case where every line compares equal under `splitlines()`)
- [x] Task 1.6: Print the expected heading text (derived literal / space-separated value, or the regex pattern) on alias mismatch — depends on: Task 1.1 — status: done (2026-09-01)
- [x] Task 1.7: Add line numbers to the item-regex computed-field raises (TaskItem, REQ/ACC items, RSK assessment, VCR AC method, feat entries) — depends on: Task 1.1 — status: done (2026-09-01; "REQ/ACC items" and "feat entries" both resolved to `feat/models/v1/body.py`'s own `RequirementItem`/`AcceptanceCriterionItem`/`Phase`/`UpdateEntry`/`DecisionEntry` — DEC's `Option` and SOP's `Step`/`UpdateEntry` were left untouched, not named by this task)
- [x] Task 1.8: Unit tests in `tests/models/md/` for every new message shape — depends on: Tasks 1.2 through 1.7 — status: done (2026-09-01; `tests/models/md/test_error_messages.py` plus one `tests/tsk/models/v1/test_task_item.py` addition for Task 1.7's one *reachable* domain example — see Decisions Made)

#### Phase 2: Frontmatter and Value Channels

- [ ] Task 2.1: Wrap `yaml.YAMLError` in the per-domain parsers: name the frontmatter block, remap block-relative to document-relative line numbers — depends on: Phase 1
- [ ] Task 2.2: Add domain/document context to the `pydantic.ValidationError` surface at the parser boundary — depends on: Phase 1
- [ ] Task 2.3: Tests for both channels — depends on: Tasks 2.1 and 2.2

#### Phase 3: Tool Boundary

- [ ] Task 3.1: Shared context wrapper (domain + tool + frontmatter-vs-body) in `models/md/_errors.py` — depends on: Phase 2
- [ ] Task 3.2: Apply it to the twelve `parse_<d>`, eleven `create_<d>`, and eleven `validate_<d>` tools and the generic `update` adapters + `set_status` — depends on: Task 3.1
- [ ] Task 3.3: Update the `Raises` docstring sections of every touched tool — depends on: Task 3.2
- [ ] Task 3.4: Tool-layer tests (tsk + one other domain, incl. the generic `update` adapter) — depends on: Task 3.2

#### Phase 4: Verify and Close

- [ ] Task 4.1: Regression tests with the issue #27 bodies verbatim through `validate_tsk`/`create_tsk`/`update`, plus the feat-7 Task 0.29 body — depends on: Phase 3
- [ ] Task 4.2: Full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite) — depends on: Task 4.1
- [ ] Task 4.3: Regenerate `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); add the `AGENTS.md` note — depends on: Task 4.2
- [ ] Task 4.4: Comment on GitHub issue #27 (root cause, the message contract, the feature id); walk the ACCs; mark the feature done — depends on: Task 4.3

## Progress

### Current Status

**As of 2026-09-01**: Phase 1 (models/md Engine Messages) is complete. Every cataloged
`models/md`-engine error surface now carries a document-relative field path (REQ-001), a
1-based line reference relative to the normalized body plus a snippet (REQ-002), and an
expected/fix detail (REQ-003) — "text left over after processing all fields", "expected …,
found no match" (field and list), raw-HTML rejection (inline and block), "text is not in
'mdformat'.", and heading alias mismatch. Task 1.7 additionally threaded the same path/line
onto the domain-level item-regex computed-field raises in `tsk`/`rsk`/`vcr`/`feat`. Exception
types are unchanged throughout (REQ-006); the full unittest suite (2747 tests, up from 2720)
passes, with one existing domain test (`tests/qa/models/v2/test_parser.py`) updated to match
its own intentionally-changed message substring. `ruff format --check`/`ruff check`/`vulture`
are all clean. The next step is Phase 2 (Frontmatter and Value Channels), beginning with
Task 2.1 (wrap `yaml.YAMLError` in the per-domain parsers).

### Updates

#### 2026-09-01 19:45:00.000Z — Phase 1 (models/md Engine Messages) completed

Implemented Tasks 1.0-1.8 in one pass (pin-then-enrich collapsed into a single session rather
than per-task, since the whole phase was small enough to review as one diff -- see Decisions
Made). Files touched: `models/md/_markdown.py` (moved/renamed the existing snippet helper to
a shared, non-underscore-prefixed `snippet()`; added `not_in_mdformat_message()`/
`_first_differing_line()`; enriched `_assert_no_raw_html()`/`_raw_html_message()` with a line
reference — falling back to the nearest ancestor block token's own `.map` for a mapless nested
`html_inline` child — and the code-span/HTML-comment fix hint), `models/md/alias_match.py`
(added `describe_alias()`), `models/md/markdown_str.py` (added the `_path`/`_line`
`PrivateAttr`s; `_field_label()`/`_child_path()`/`_is_heading_type()`/`_no_match_message()`/
`_leftover_text_message()` helpers; threaded `_path`/`_offset` through `from_text`/
`process_field`/`process_list_field`, tracking the running line offset via an actual
before/after line-count delta rather than a summed `get_extent`, so per-item blank-line
elision in `process_list_field` never desynchronizes it), `models/md/markdown_section.py`
(added `_alias_mismatch_message()`; threaded `_path`/`_offset` through `from_text`),
`models/md/markdown_paragraph.py`/`markdown_list_item.py` (same threading), `models/md/markdown_comment.py`/`markdown_block_quote.py`/`markdown_code_block.py`/`markdown_section{1..6}_with_comment.py` (accept-and-forward `_path`/`_offset` for override-signature compatibility;
message fix only, no path tracking, since none of these are in Task 1.7's item list),
`tsk/models/v1/task_item.py`, `rsk/models/v1/assessment.py`, `vcr/models/v1/body.py`, `feat/models/v1/body.py` (Task 1.7's domain-level item-regex message enrichments). New tests:
`tests/models/md/test_validation_error_baseline.py` (10 tests, Task 1.0/ACC-001), `tests/models/md/test_error_messages.py` (16 tests, Task 1.8, including an end-to-end reproduction of
REQ-001's own `Task > RecentUpdates > UpdateEntry > content` worked example via a local
fixture tree), and one addition to `tests/tsk/models/v1/test_task_item.py` (the one Task 1.7
domain case actually reachable through normal parsing, since RSK/VCR/feat's analogous
computed-field raises are documented as unreachable once `match_alias` already enforces the
same heading at parse time). One pre-existing test
(`tests/qa/models/v2/test_parser.py::test_missing_elicitation_context_raises_the_same_structural_error_from_from_text`) asserted the *old* bare `Qa.elicitation_context: ...`
message content and was updated in place to assert `ElicitationContext` instead (exception
type unchanged, AssertionError; only the message content assertion changed, which is exactly
what this phase intentionally does — this is not the Task 1.0 baseline file, so it is not
itself part of the "pin-then-enrich" record, but is called out here for the same reason).
Quality gate: `ruff format --check` (clean), `ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest discover` (2747 tests, OK). No `specmgr docs`/
`specmgr mcp-docs` regeneration run — that is Phase 4's Task 4.3, and no `models/md/__init__.py`
`__all__` export changed (the new helpers are internal).

#### 2026-09-01 14:30:47.000Z — Session wrap-up: Task 1.0 added; origin/dev merged

Added Task 1.0 (pin the current validation-error strings in a dedicated baseline test file before Phase 1's enrichments, so every message change becomes a reviewable diff); Task 1.1 now depends on Task 1.0. Merged `origin/dev` into this branch as `01e29a5` (pulls in `8e07594`, feat-40's docs-prune): no conflicts, working tree clean, and the incoming `tests/commands/test_docs.py` suite passes post-merge. Plan artifacts committed as `7aac697` (ccm-generated message). No implementation has started — the next step for the phase orchestrator is Phase 1, beginning with Task 1.0.

#### 2026-09-01 12:39:10.000Z — Phase 0 completed

Phase 0 (Decide and Record) is complete: Task 0.1 (this feature was created via `create_feat` and renamed to `feat-27-validation`), Task 0.2 (feat-7's Task 0.29 was annotated as subsumed, with a Recent Updates entry added to that file), and Task 0.3 (the three planning decisions were recorded in the Decisions Made section below). Per user direction, no implementation (Phases 1–4) has been started — this document remains the design and plan only.

#### 2026-09-01 11:56:45.000Z — Created

Created for GitHub issue #27; subsumes feat-7's not-started Task 0.29. Investigation and planning complete; decisions confirmed with the user.

### Decisions Made

#### 2026-09-01 19:45:00.000Z — Phase 1 implementation-detail decisions

Field-path label rule (REQ-001's `Task > RecentUpdates > UpdateEntry > content` example):
each path segment is the nested field's own type name when that type carries independent
domain identity (any `MarkdownSection`/`MarkdownListItem`/... subclass with its own name,
e.g. `UpdateEntry`), or the field's own attribute name when the type is one of `models/md`'s
generic, directly-reusable leaf/section types used verbatim (`MarkdownParagraph`,
`MarkdownComment`, bare `MarkdownListItem`, ...) — a bare class name there (e.g.
`"MarkdownParagraph"`) would say nothing about *which* field failed, since the same generic
type is reused across many unrelated fields throughout the codebase. Implemented as
`markdown_str._field_label`, checked against a fixed set of generic type names
(`_GENERIC_LEAF_TYPE_NAMES`) rather than an `issubclass` check, to avoid a circular import
between `markdown_str.py` and the section/paragraph/list-item modules that import it.

Line numbers are relative to whatever `mdformat`-normalized text the *current* `from_text`/
`process_field`/`process_list_field` call was actually invoked with — for a document parsed
top-down from a domain parser's own `Body.from_text(post.content)` call (every real caller in
this codebase), that is the whole normalized body, so REQ-002's "relative to the
mdformat-normalized body" is satisfied for the common case; a hypothetical caller invoking
`SomeSection.from_text(some_slice)` directly on an already-sliced sub-document would instead
get a line number relative to *that* slice — an accepted, documented limitation (`_offset`
threading only ever originates from the caller's own root call, defaulting to `0`).

`process_list_field`'s running line offset for each matched item is tracked via an actual
before/after `len(text.splitlines())` delta around each iteration, not a summed `get_extent`
— its own docstring already flagged that summed `get_extent` values don't line up with real
line positions once per-item `mdformat` renormalization elides a separating blank line; a
direct line-count delta sidesteps that by construction, without needing a return-signature
change (`process_list_field`'s existing 2-tuple return contract, relied on directly by
`tests/qa/models/v2/test_question_answer.py`, is preserved unchanged).

`_path`/`_offset`/`_line` were threaded through every `from_text` override for override-
signature (Liskov) consistency, not just the two the task list names (`MarkdownSection`/
`MarkdownParagraph`) — `MarkdownListItem.from_text` needed it directly for Task 1.7's
`TaskItem`/`RequirementItem`/`AcceptanceCriterionItem`; `MarkdownComment`/`MarkdownBlockQuote`/
`MarkdownCodeBlock`/the six `MarkdownSection{1..6}WithComment` wrappers accept-and-forward the
same two keyword parameters purely so every `from_text` override shares one signature, even
though none of the last four's *own* raise sites needed path/line data. Task 1.7's "REQ/ACC
items"/"feat entries" were resolved to `feat/models/v1/body.py`'s own `RequirementItem`/
`AcceptanceCriterionItem`/`Phase`/`UpdateEntry`/`DecisionEntry` (the only classes in the
codebase matching those two literal patterns); DEC's `Option` and SOP's `Step`/`UpdateEntry`
were intentionally left untouched since the task's own parenthetical list does not name them.

Phase 1 was implemented in one pass rather than strictly one message-enrichment change per
task with an immediately-following baseline-file update — Task 1.0's baseline file was
written last, pinning the already-enriched final message content, once the full message
contract was settled; the plan's "pin-then-enrich" guarantee (every message change being a
reviewable diff to one file) still holds for *future* phases/tasks that touch these messages
again, since the baseline file now exists and reflects the current, intentional state.

#### 2026-09-01 11:56:45.000Z — Messages only; strict rejection; id feat-27-validation

Kept the documented two-channel error contract (`AssertionError` structural / `pydantic.ValidationError` value) and changed message content only — rationale: the MCP SDK forwards `str(e)` to the client, so message quality fully solves the user-visible problem without touching the ~40 parser/tool docstrings, the eight list-tool catch tuples, `_doc_paths`, or the existing `assertRaises(AssertionError)` tests; a typed structural channel (mirroring the ADR domain's `AdrParseError`) remains available as a future ADR if ever needed (e.g. for `python -O` deployments). Retained strict rejection of bare `<word>` tokens and `+`/`-`/`*`-prefixed paragraph continuations — rationale: writes persist the caller's body byte-for-byte and REQ-005 intentionally rejects raw HTML, so auto-escaping or absorbing such content would change persisted text; the error instead names the documented workaround. Chose the id `feat-27-validation` (the GitHub issue number per the ADR e369ee2e convention) over `create_feat`'s auto-assigned `max(NNN)+1`, renamed immediately after creation, following the feat-21/feat-30/feat-33/feat-36 precedent.

### Related PRs / Commits

- `7aac697` — docs(feat-27): add the feature design for clear validation errors (this plan, plus the feat-7 Task 0.29 annotation)
- `01e29a5` — merge of `origin/dev` into `feat-27-validation` (pulls in `8e07594`, feat-40's docs-prune)
