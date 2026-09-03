---
classification: null
created: '2026-09-03 08:28:23.003+02:00'
id: feat-67-70-71
status: planning
type: feat
updated: '2026-09-03 08:34:41.448+02:00'
version: 1.0.0
---

# Feature: Fix placeholder timestamps and actionable HTML-token validation errors (#67, #70, #71)

## Plan

### Overview

This feature closes three interconnected GitHub issues discovered during dogfooding of the FEAT-drafting workflow: (1) issue #67 -- every domain's `#### {timestamp} - {title}` template/example placeholder entries (and some frontmatter `created`/`updated` placeholders) use a suspiciously round, all-zero time-of-day (`00:00:00.000Z`), which invites an agent or human to copy it verbatim into a real document instead of substituting the actual current timestamp; (2) issue #71, which generalizes #67 across every domain's templates/examples/schemas and additionally flags that a malformed `####` timestamp heading in `Updates`/`Decisions Made` (e.g. missing the required `yyyy-MM-dd HH:mm:ss.fff[+HH:mm|Z]` shape) fails whole-document validation with no diagnostic detail; and (3) issue #70, which shows that a bare `<word>`-shaped token outside backticks (parsed as raw HTML by the underlying markdown parser) bypasses the actionable-error path `feat-27-validation` introduced, surfacing only a generic, undiagnosable `Error executing tool`. A preliminary investigation (see Design Notes) found that issues #70 and #71 originate in genuinely separate code paths, and that a minimal reproduction of each against the current codebase already produces a well-formed, actionable `wrap_tool_errors` message rather than the bare failure the issues describe. Each error-message topic therefore needs its own confirm-the-gap-is-real / fix-if-so / regression-test phase, not a single shared fix.

### Requirements

- REQ-001: Investigate how the shared `models/md` parser and its `wrap_tool_errors` error-wrapping handle (a) bare `<word>`-shaped tokens outside backticks and (b) malformed `#### {timestamp} ...` headings in `Updates`/`Decisions Made`, including reproduction against a large real document and a check of whether MCP client/transport-side message handling could explain the reported bare-error symptom, before any implementation begins.
- REQ-002: Every domain's `*/data/*_template.md` and `*/data/*_example.md` file replaces round, all-zero placeholder timestamps (frontmatter `created`/`updated`, and `feat`'s body-level `#### {timestamp} - {title}` headings) with deliberately odd, non-round values in the `yyyy-MM-dd HH:mm:ss.fff[+HH:mm|Z]` format.
- REQ-003: For the bare `<word>`-shaped HTML-like token failure mode (#70): if Phase 1 confirms a real gap, the origin path in `models/md/_markdown.py` is fixed so it surfaces the same actionable detail (field path, line, cause/fix hint) `wrap_tool_errors` already provides for other structural failures; either way, an end-to-end regression test locks in the correct final behavior across affected domains.
- REQ-004: For the malformed-timestamp-heading failure mode (#71): if Phase 1 confirms a real gap, the origin path in `models/md/markdown_section.py`/`markdown_str.py`'s alias/`get_extent` matching is fixed so it surfaces the same actionable detail; either way, an end-to-end regression test locks in the correct final behavior across affected domains.
- REQ-005: Each topic (timestamp placeholders, bare HTML-token errors, malformed timestamp-heading errors) has its fix (if any) and its regression test delivered together in that topic's own phase, not split across separate global "fix everything" / "test everything" phases.

### Acceptance Criteria

- [ ] ACC-001: A repo-wide search for `00:00:00.000` (or equivalent round, all-zero time-of-day patterns) across every `*/data/*_template.md` and `*/data/*_example.md` returns zero matches.
- [ ] ACC-002: An end-to-end regression test with a bare `<word>` token outside backticks in a heading or list item, driven through `create_<d>`/`validate_<d>` for every affected domain, asserts the final `wrap_tool_errors`-enriched message is actionable (field path + line + cause/fix hint), not a bare `Error executing tool`.
- [ ] ACC-003: An end-to-end regression test with a `####` heading whose leading text is not a parseable timestamp, driven through `create_<d>`/`validate_<d>`/the generic `update` tool, asserts the same actionable-error detail, not a bare `Error executing tool`.
- [ ] ACC-004: Design Notes (or a follow-up DEC/ADR, if the investigation reveals architecture-level implications) documents the root cause of each topic, the large-document/MCP-client reproduction findings, and confirms no unintended side effects before any Phase 3/4 fix implementation starts.

### Scope

#### Included

- Auditing and fixing round, all-zero placeholder timestamps in every domain's `*/data/*_template.md`/`*/data/*_example.md`.
- Confirming whether the reported bare-HTML-token and malformed-timestamp-heading error-message gaps are real in the current codebase, including a large-document repro and an MCP-client-side message-handling check.
- Fixing the origin of either gap (if confirmed real), across every domain sharing the `models/md` parser.
- End-to-end regression tests for both failure modes, delivered alongside their own fix (or alongside confirmation that no fix was needed).

#### Explicitly Out Of Scope

- Changing the `yyyy-MM-dd HH:mm:ss.fff[+HH:mm|Z]` timestamp format itself -- that format was already decided in `feat-38-39-41-43-44`.
- Adding new document-type domains or new MCP tools.
- Wiring `validate_<d>` into CI/pre-commit over the repo's own `.specmgr`/`docs` documents -- tracked separately (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73 and the AGENTS.md "Still genuinely missing" list).

### Design Notes

Preliminary research (2026-09-03, via a research agent, read-only, no code changed) into `models/md`, kept here so a future agent does not redo it:

- `wrap_tool_errors` (`models/md/_errors.py` ~lines 156-218) catches `ValidationError`/`yaml.YAMLError`/`AssertionError` and re-prefixes the message with domain/tool/channel context; any other exception type propagates untouched.
- Issue #70 (bare `<word>` parsed as raw HTML) originates in `models/md/_markdown.py::_assert_no_raw_html`/`parse()` (~lines 246-301), a tokenizer-level guard shared by every domain. Raises `AssertionError` with a fully-formed message (`_raw_html_message`).
- Issue #71 (malformed `#### {timestamp}` heading) originates in `models/md/markdown_section.py`/`markdown_str.py`'s `@alias`/`get_extent` heading-matching machinery (`process_list_field`, `_no_match_message`/`_leftover_text_message`) -- unrelated to the tokenizer. Also raises `AssertionError` with a fully-formed message.
- Both land in the *same* `except (AssertionError, ...)` branch of `wrap_tool_errors`, so the wrapping mechanism itself needs no change for either -- but the two failures are otherwise independent code paths, so any real fix is two separate changes, not one.
- A minimal, single-substitution repro of both cases against the shipped `feat_example.md`, run directly against the current `dev`-equivalent branch, **already produced a well-formed, actionable message** -- the bug as literally reported did not reproduce minimally. Phase 1 must retry against a larger real document (the ~150-line document mentioned in issue #70) and check MCP client/transport-side message handling before assuming a code fix is needed at all.
- No existing test drives either failure mode end-to-end through `create_<d>`/`validate_<d>`/`update` and asserts on the final `wrap_tool_errors` message: `tests/models/md/test_markdown_html_rejection.py` only exercises `parse()` directly with real closed tags (not a bare `<d>`-style token, and not through `wrap_tool_errors`); `tests/feat/models/v1/test_body.py::test_rejects_malformed_headings` only asserts the boolean `match_alias()` result, not the resulting exception/message. This is exactly the regression-test gap Phases 3/4 close.
- Direct experience from this feature's own drafting session: an `update` call adding a `### Decisions Made` section failed with a bare `Error executing tool` (no field/line/hint) when two of its three new `#### {timestamp} : {title}` entries were accidentally out of newest-first order due to a `+02:00`/`Z` offset arithmetic mistake -- i.e. a *third*, previously-undocumented case of this same "bare error, no diagnostic" symptom class, this time from the newest-first ordering validator rather than the tokenizer or alias-matching path. Worth folding into Phase 1's investigation as a third sub-case alongside #70/#71.

### Task List

#### Phase 1: Investigation and Design

- [ ] Task 1.1: Reproduce the bare `<word>`-as-HTML failure (#70) against a minimal `feat` document and confirm current behavior at the `models/md/_markdown.py::_assert_no_raw_html`/`parse()` level.
- [ ] Task 1.2: Reproduce the malformed-timestamp-heading failure (#71) against a minimal `feat` document and confirm current behavior at the `models/md/markdown_section.py`/`markdown_str.py` alias/`get_extent` level.
- [ ] Task 1.3: Re-run both repros against a large (~150-line) real document, matching the scale that originally triggered the issue reports, to check for a length/complexity-specific gap not visible in the minimal repro.
- [ ] Task 1.4: Investigate whether MCP client/transport-side message truncation or discarding could explain the reported bare "Error executing tool" symptom despite `wrap_tool_errors` producing a full message server-side.
- [ ] Task 1.5: Audit every domain's `*/data/*_template.md`/`*/data/*_example.md` for round, all-zero placeholder timestamps (frontmatter and, for `feat`, body-level `#### {timestamp}` headings) and record the full list of files needing changes.
- [ ] Task 1.6: Reproduce the newest-first-ordering failure noted in Design Notes (out-of-order `#### {timestamp}` entries in `Updates`/`Decisions Made`) and confirm whether its error path also bypasses `wrap_tool_errors`'s actionable detail.
- [ ] Task 1.7: Record findings (confirmed-real gap vs. no-gap-found per topic, root cause, side-effect assessment across domains) in this feature's Design Notes, or spin off a DEC/ADR if warranted.

#### Phase 2: Placeholder Timestamp Fix and Test

- [ ] Task 2.1: Replace round, all-zero placeholder timestamps across every affected `*_template.md`/`*_example.md` (per Task 1.5's list) with deliberately odd, non-round values in the correct format.
- [ ] Task 2.2: Add/extend a regression test asserting a repo-wide search for round, all-zero timestamps returns zero matches across every domain's template/example files.
- [ ] Task 2.3: Run the full test suite to confirm no regressions from the content changes.

#### Phase 3: Bare HTML-Like Token Actionable-Error Fix and Test

- [ ] Task 3.1: Based on Phase 1 findings, fix the origin path in `models/md/_markdown.py` so a bare `<word>`-shaped token failure carries full actionable detail, only if Task 1.3/1.4 confirmed a real gap.
- [ ] Task 3.2: Add an end-to-end regression test fixture (a bare `<word>` token outside backticks in a heading/list item, driven through `create_feat`/`validate_feat`) asserting the final message is actionable.
- [ ] Task 3.3: Verify ACC-002 passes.

#### Phase 4: Malformed Timestamp-Heading Actionable-Error Fix and Test

- [ ] Task 4.1: Based on Phase 1 findings, fix the origin path in `models/md/markdown_section.py`/`markdown_str.py`'s alias/`get_extent` matching so a malformed `#### {timestamp}` heading failure carries full actionable detail, only if Task 1.3/1.4 confirmed a real gap.
- [ ] Task 4.2: Add an end-to-end regression test fixture (a malformed `#### {timestamp}` heading in `Updates`/`Decisions Made`, driven through `create_feat`/`validate_feat`/the generic `update` tool) asserting the final message is actionable.
- [ ] Task 4.3: Based on Task 1.6's findings, decide whether the newest-first-ordering failure mode also needs its own fix here or is already covered by Task 4.1/4.2's fix; add a dedicated regression test either way.
- [ ] Task 4.4: Verify ACC-003 passes.

#### Phase 5: Closeout and Final Verification

- [ ] Task 5.1: Re-run the full repo-wide round-timestamp search (ACC-001) to confirm zero remaining matches.
- [ ] Task 5.2: Re-run the full test suite to confirm no regressions across all changes.
- [ ] Task 5.3: Record the final verdict on issues #67/#70/#71 (fixed vs. confirmed-already-correct-plus-regression-test-added) in Design Notes/Decisions Made.
- [ ] Task 5.4: Update this feature's Progress section (Current Status) and close out.

## Progress

### Current Status

**As of 2026-09-03**: Design session complete -- scope, requirements, acceptance criteria, and the 5-phase task list are finalized, and the feature's id was renamed to its final `feat-67-70-71` form. No implementation has started; Phase 1's investigation tasks (large-document repro, MCP-client check, cross-domain timestamp audit, and now also the newest-first-ordering failure mode found while drafting this very document) are next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 12:03:19.442Z - Design session wrapped up

Finalized the Design Notes and added a Decisions Made log capturing the session's key calls (combining the three issues, the 5-phase per-topic fix+test structure, and the id rename). While drafting this very entry, an `update` call hit the same class of bare, undiagnosable `Error executing tool` this feature is meant to fix -- this time from the `Decisions Made` newest-first-ordering validator, not the tokenizer or alias-matching path -- and has been folded into Phase 1/Design Notes as a third sub-case. No implementation started; the feature is ready for Phase 1 to begin.

#### 2026-09-03 09:14:27.583Z - Created

Feature created from GitHub issues #67, #70, and #71, combining the placeholder-timestamp hygiene fix and the actionable-error fixes for bare HTML-like tokens and malformed timestamp headings into one feature with a 5-phase plan: shared investigation, then one confirm/fix/test phase per topic, then a closeout phase.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 11:52:07.318Z - Renamed feature id to feat-67-70-71

Renamed the feature's id/folder from `feat-67-70-71-timestamps-and-errors` to `feat-67-70-71` via `set_feat_id`, matching the `feat-38-39-41-43-44` precedent of using only the tracked issue numbers, with no descriptive slug, when a feature aggregates several GitHub issues.

#### 2026-09-03 10:41:29.955Z - Structured the Task List as 5 topic-scoped phases

Rejected an earlier 3-phase draft (Investigation, then a global fix-everything phase, then a global test-everything phase) in favor of 5 phases: a shared Investigation phase, one phase per topic bundling that topic's own fix and regression test together (timestamp placeholders; bare HTML-token errors; malformed timestamp-heading errors), and a final Closeout phase. Chosen because code research (see Design Notes) confirmed issues #70 and #71 are independent code paths, so a global fix-all/test-all split would have obscured that each topic can be implemented and verified independently.

#### 2026-09-03 09:27:03.641Z - Combined issues #67, #70, and #71 into one feature

Chose to track all three GitHub issues in a single feature rather than splitting them: #67 and #71 are literal duplicates of each other, and #70's error-message gap is what makes #67/#71-style mistakes costly to diagnose in the first place. Optional sections (Dependencies, Related Decisions, Blockers, Related PRs / Commits, More Information) were deliberately left out of the initial draft, to be filled in once Phase 1's investigation produces concrete findings.
