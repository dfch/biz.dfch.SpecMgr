---
created: '2026-09-01T14:24:06.341303'
id: feat-27-validation
status: planning
type: feat
updated: '2026-09-01T14:42:47.209799'
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

- [ ] Task 1.1: Field-path threading (`_path` parameter + `PrivateAttr`) through `from_text`/`process_field`/`process_list_field` and the `MarkdownSection`/`MarkdownParagraph` overrides — depends on: Phase 0
- [ ] Task 1.2: Enrich the "text left over" message with field path, line reference in the normalized text, snippet, and a likely-cause hint — depends on: Task 1.1
- [ ] Task 1.3: Enrich the "expected …, found no match" messages to name the expected section for the missing-mandatory-section case — depends on: Task 1.1
- [ ] Task 1.4: Add a line number (token `.map`) and a fix hint (code span / HTML comment) to the raw-HTML rejection — depends on: Task 1.1
- [ ] Task 1.5: Replace the bare "text is not in 'mdformat'." message with a line reference plus first-differing-line detail — depends on: Task 1.1
- [ ] Task 1.6: Print the expected heading text (derived literal / space-separated value, or the regex pattern) on alias mismatch — depends on: Task 1.1
- [ ] Task 1.7: Add line numbers to the item-regex computed-field raises (TaskItem, REQ/ACC items, RSK assessment, VCR AC method, feat entries) — depends on: Task 1.1
- [ ] Task 1.8: Unit tests in `tests/models/md/` for every new message shape — depends on: Tasks 1.2 through 1.7

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

**As of 2026-09-01**: Created for GitHub issue #27. Investigation complete: both failure classes re-verified on the current HEAD, the full misleading-error catalog recorded in Design Notes, and the MCP-SDK error-forwarding behavior confirmed (the server sends `str(e)`; the "Error executing tool" prefix is client-side). All three planning decisions confirmed with the user: messages-only (no new exception channel), strict rejection with clear errors (no content-acceptance changes), and the id `feat-27-validation` (rename after `create_feat`). No implementation started yet — this document is the design and plan only.

### Updates

#### 2026-09-01 12:39:10.000Z — Phase 0 completed

Phase 0 (Decide and Record) is complete: Task 0.1 (this feature was created via `create_feat` and renamed to `feat-27-validation`), Task 0.2 (feat-7's Task 0.29 was annotated as subsumed, with a Recent Updates entry added to that file), and Task 0.3 (the three planning decisions were recorded in the Decisions Made section below). Per user direction, no implementation (Phases 1–4) has been started — this document remains the design and plan only.

#### 2026-09-01 11:56:45.000Z — Created

Created for GitHub issue #27; subsumes feat-7's not-started Task 0.29. Investigation and planning complete; decisions confirmed with the user.

### Decisions Made

#### 2026-09-01 11:56:45.000Z — Messages only; strict rejection; id feat-27-validation

Kept the documented two-channel error contract (`AssertionError` structural / `pydantic.ValidationError` value) and changed message content only — rationale: the MCP SDK forwards `str(e)` to the client, so message quality fully solves the user-visible problem without touching the ~40 parser/tool docstrings, the eight list-tool catch tuples, `_doc_paths`, or the existing `assertRaises(AssertionError)` tests; a typed structural channel (mirroring the ADR domain's `AdrParseError`) remains available as a future ADR if ever needed (e.g. for `python -O` deployments). Retained strict rejection of bare `<word>` tokens and `+`/`-`/`*`-prefixed paragraph continuations — rationale: writes persist the caller's body byte-for-byte and REQ-005 intentionally rejects raw HTML, so auto-escaping or absorbing such content would change persisted text; the error instead names the documented workaround. Chose the id `feat-27-validation` (the GitHub issue number per the ADR e369ee2e convention) over `create_feat`'s auto-assigned `max(NNN)+1`, renamed immediately after creation, following the feat-21/feat-30/feat-33/feat-36 precedent.

### Related PRs / Commits

None yet.
