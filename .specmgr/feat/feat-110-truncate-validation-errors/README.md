---
classification: null
created: '2026-09-08 09:37:19.699+02:00'
id: feat-110-truncate-validation-errors
status: review
type: feat
updated: '2026-09-08 09:53:48.000+02:00'
version: 1.0.0
---


# Feature: Truncate `validate` Tool's Error Messages (#110)

## Plan

### Overview

GitHub issue #110 ("validation error shall only show the first n characters of the error text" / "reduce noisy output") asks that the generic `validate` MCP tool's error messages be bounded in length. Today, `general/tools/validate.py`'s exception handler builds each `ValidationErrorEntry.message` from `str(ex)` verbatim, with no length cap. Investigation before implementation found two things:

- The original hypothesis -- that `pydantic.ValidationError`'s `input_value=...` repr could embed an entire document body verbatim on a whole-model `model_validator(mode="after")` failure (e.g. VCR's duplicate `AC-NNN` check) -- turned out to be **wrong**: pydantic-core already self-limits that repr internally (empirically confirmed: a 50,000-character field still produced a fixed 282-character message). This channel is a dead end for reproducing "noisy output" and is recorded here so a future investigator doesn't re-walk the same path.
- A real, reachable source of oversized messages does exist: a structurally malformed document (e.g. an unexpected/duplicate heading, or the pre-existing "text left over after processing all fields" class of failures from `feat-27-validation`/issue #27) can produce a `str(AssertionError)`/`str(ValidationError)` several hundred characters long once the domain/tool/channel label (`wrap_tool_errors`) is prepended -- confirmed live with a real, valid REQ body (>500 chars) that has a second, duplicate H1-level heading appended: `validate(type="req", content=..., full=False)` returns a 521-character message today.
- A second, distinct, genuinely unbounded gap was found along the way: `models/md/_markdown.py::not_in_mdformat_message()`'s `line_no == 0` branch (a global `text == format_text(text)` mismatch, e.g. a missing trailing newline) embeds `text!r`/`format_text(text)!r` directly with no `snippet()` call -- unlike every sibling message-builder in that same file, which already routes offending text through the existing `snippet(text, max_lines=5, max_chars=300)` helper. This is fixed in the same feature since it is directly relevant to "noisy output" and cheap to fix alongside the primary change.

The fix reuses the existing `snippet()` convention (already designed for exactly this: "truncated ... for use in an error message", `"... (truncated)"` suffix) rather than inventing new truncation logic.

### Requirements

- REQ-001: `general/tools/validate.py`'s `validate()` function caps `ValidationErrorEntry.message`'s length by passing `str(ex)` through `models/md/_markdown.py::snippet()` with a named constant `_MAX_VALIDATE_ERROR_CHARS = 300`, instead of using `str(ex)` verbatim.

- REQ-002: This change is scoped to the generic `validate` tool only -- `validate_adr` and the shared `wrap_tool_errors` layer are explicitly left unchanged, since OpenCode's known `isError: true` client-side content-discarding bug (ADR 519d1206) means truncating raised-exception paths has no practical payoff today; `validate`'s non-raising `ValidateResult` is the one path that reliably reaches the client unbounded.

- REQ-003: Fix `models/md/_markdown.py::not_in_mdformat_message()`'s `line_no == 0` branch to route `text`/`formatted` through `snippet()` before embedding them in the message, matching every sibling message-builder in that module.

- REQ-004: Update every docstring that currently claims the message is reused "verbatim" (`validate.py`'s module docstring, `validate()`'s own docstring, its `@mcp.tool()` `description=` string, and `ValidationErrorEntry.message`'s docstring in `general/models/validate_result.py`) to describe the new truncation behavior instead.

- REQ-005: Add regression tests: (a) a real, disk-free repro -- a valid REQ body (>500 chars) with a duplicate/second H1-level heading, passed directly to `validate(type="req", content=..., full=False)` -- asserting the returned message is capped at `_MAX_VALIDATE_ERROR_CHARS` plus the `"... (truncated)"` suffix length, and ends with that suffix; (b) a short-message case confirming messages under the cap are returned unchanged, with no suffix appended; (c) a `not_in_mdformat_message()` unit test for the `line_no == 0` branch with long input, asserting the message no longer contains the full raw text.

- REQ-006: Existing tests must keep passing unmodified in behavior: `TestValidateIssue83Regressions` (substring assertions on messages) and `TestValidateYamlErrorEnrichment` (exact parity between `validate`'s and `parse_<d>`'s raw messages) -- both use short fixtures expected to remain under the cap, verified during implementation.

- REQ-007: Add a `CHANGELOG.md` `[Unreleased]` -> `### Fixed` entry referencing GitHub issue #110, covering both the `validate` truncation and the `not_in_mdformat_message` fix.

### Acceptance Criteria

- [x] ACC-001: `validate(type="req", content=<REQ body with a duplicate H1 heading>, full=False)` returns a message of at most `_MAX_VALIDATE_ERROR_CHARS + len("... (truncated)")` characters, ending in `"... (truncated)"`.

- [x] ACC-002: A short, already-under-the-cap `validate()` failure message is returned byte-identical to today (no suffix appended, no truncation applied).

- [x] ACC-003: `not_in_mdformat_message()`'s global-mismatch (`line_no == 0`) branch no longer embeds an unbounded raw `text!r`/`formatted!r` -- both are routed through `snippet()`.

- [x] ACC-004: `TestValidateIssue83Regressions` and `TestValidateYamlErrorEnrichment` still pass unmodified (or with only test-expectation adjustments, never production-behavior changes, if their fixtures turn out to exceed the cap).

- [x] ACC-005: `ruff format --check`, `ruff check`, `pytest -n auto --cov=src --cov-report=` (full suite), and `specmgr docs` (no drift) all pass.

### Scope

#### Included

- Length-capping `general/tools/validate.py`'s `ValidateResult.errors[].message`.

- Fixing `not_in_mdformat_message()`'s unbounded `repr()` gap.

- Docstring updates for both of the above.

- New/updated regression tests, `CHANGELOG.md` entry.

#### Explicitly Out Of Scope

- `validate_adr` (id-based, raises on failure -- excluded per REQ-002's rationale).

- The shared `wrap_tool_errors` layer itself (would affect every raising tool in the repo, not just `validate`; explicitly rejected as overbroad for this issue).

- `set_status`'s `InvalidStatusResult` (a different, already-bounded structured-result shape from a prior, related fix -- not touched here).

### Dependencies

#### Depends On

- feat-81-83-validation: introduced the generic `validate` tool and its `ValidateResult` shape being modified here.

- feat-27-validation: the message-enrichment machinery and `snippet()` helper being reused here.

#### Blocks

- None known.

### Design Notes

**Why `snippet()` and not a bespoke truncation function**: `models/md/_markdown.py::snippet(text, max_lines=5, max_chars=300)` already does exactly what's needed -- cut to N lines/chars and append `"... (truncated)"` -- and its own docstring literally says "for use in an error message". Reusing it keeps this fix consistent with the one existing precedent in the codebase rather than introducing a second, slightly different truncation convention.

**Why `_MAX_VALIDATE_ERROR_CHARS` is a separate constant from `snippet()`'s own default**: per `.specmgr/conventions.md`'s "Comparison Constants" rule, any new length threshold used in a comparison should be a named, `ALL_CAPS` module-level constant with a doc comment explaining its rationale -- even though its value (300) happens to match `snippet()`'s own default, making it explicit at the `validate.py` call site is clearer than relying on an imported function's default parameter value.

**The pydantic `input_value` dead end**: documented here so a future investigator doesn't re-walk this path. Live-tested: a `Vcr` document with a duplicate `AC-001` heading and a 50,000-character description field still produced a fixed 282-character `pydantic.ValidationError` message -- pydantic-core's own repr formatting for `input_value` already self-truncates internally, regardless of the actual field/model size. This ruled out "whole-model validator failure embeds the whole document" as the noisy-output source and redirected investigation toward `not_in_mdformat_message()` and generic structural-failure messages (duplicate/unexpected headings, "text left over") instead.

**Confirmed real repro** (used for REQ-005/ACC-001): a REQ body starting `# Maximum Engine Temperature` / lead paragraph / `## Description` (with filler text to exceed ~500 chars) followed by a second, duplicate `# Duplicate Invalid Heading` (also H1-level) causes `Requirement.from_text` to fail past `## Description` when the parser can't match the next expected `Characteristics` heading, producing a raw `AssertionError` around 500 characters; after `wrap_tool_errors`'s `"req validate (body): "` label prefix, the full `validate()` message is 521 characters today, comfortably exceeding a 300-character cap. A literal "wrong H1 heading level" (e.g. `##` instead of `#`) was tried first and rejected as a test fixture: it fails immediately with a short, fixed-length message ("`Requirement: expected heading h1, got h2`", 40 chars) that never scales with document size, so it cannot exercise truncation regardless of how large the surrounding document is.

### Related Decisions

- 519d1206-4d2a-4500-9046-6db635209996 (ADR): "Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation" -- the reason `validate_adr`/`wrap_tool_errors` are explicitly out of scope here (REQ-002).

- b399f1ce-ed42-4929-b01c-7a57d18e8014 (ADR): extends the above to `set_status`'s `InvalidStatusResult` -- a related but distinct non-raising-result precedent, not modified by this feature.

### Task List

#### Phase 1: Implement truncation and the `not_in_mdformat_message` fix

- [x] Task 1.1: Add `_MAX_VALIDATE_ERROR_CHARS` constant and route `str(ex)` through `snippet()` in `general/tools/validate.py`'s `validate()` exception handler.

- [x] Task 1.2: Update `validate.py`'s module docstring, `validate()`'s docstring, and its `@mcp.tool()` `description=` string to describe the truncation instead of "verbatim".

- [x] Task 1.3: Update `ValidationErrorEntry.message`'s docstring in `general/models/validate_result.py`.

- [x] Task 1.4: Fix `models/md/_markdown.py::not_in_mdformat_message()`'s `line_no == 0` branch to route `text`/`formatted` through `snippet()`; update its docstring.

#### Phase 2: Tests and verification

- [x] Task 2.1: Add the duplicate-H1-heading real repro test to `tests/general/tools/test_validate.py` (ACC-001).

- [x] Task 2.2: Add a short-message-unaffected regression test (ACC-002).

- [x] Task 2.3: Add a `not_in_mdformat_message()` long-input unit test (ACC-003).

- [x] Task 2.4: Re-run `TestValidateIssue83Regressions`/`TestValidateYamlErrorEnrichment`, adjust test expectations only if their fixtures exceed the cap (ACC-004). Also fixed 2 additional full-suite regressions discovered beyond these two named classes -- see Updates/Decisions Made below.

- [x] Task 2.5: Add `CHANGELOG.md` entry (REQ-007).

- [x] Task 2.6: Run `ruff format --check`, `ruff check`, full `pytest -n auto --cov=src --cov-report=`, `specmgr docs` (ACC-005).

## Progress

### Current Status

**As of 2026-09-08**: Phase 2 (tests and verification) complete -- this feature's implementation is now complete and ready for a final PR. Phase 1 (implementation) and Phase 2 (new regression tests, `CHANGELOG.md` entry, full-suite quality gate, including 2 extra full-suite regressions fixed beyond the plan's own named test classes) are both done; `ruff format --check`, `ruff check`, `vulture`, the full `pytest -n auto --cov=src --cov-report=` suite (3349 tests), and `specmgr docs` (drift regenerated, matches Phase 1's docstring changes only) all pass.

### Blockers

None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-08 07:53:48.000Z - Phase 2 implemented, feature complete

Implemented Task 2.1-2.6. Added `TestValidateMessageTruncation` to `tests/general/tools/test_validate.py` with two new tests: `test_duplicate_h1_heading_produces_a_truncated_message` (ACC-001 -- a valid REQ body >500 chars via `## Description` filler, followed by a second duplicate H1-level heading plus enough trailing filler that the parser's own embedded `snippet()` call also hits its cap, confirmed live to produce a 315-character message today, exactly at the `_MAX_VALIDATE_ERROR_CHARS + len("... (truncated)")` = 315 cap, ending in `"... (truncated)"`) and `test_short_message_is_returned_unchanged` (ACC-002 -- reuses the existing `_REQ_MALFORMED_BODY` fixture already used by `TestValidateAllDomains`, pinning its exact 205-character message with no truncation suffix). Added `test_trailing_newline_only_difference_with_long_text_is_truncated` to `tests/models/md/test_error_messages.py`'s existing `TestNotInMdformatMessage` class (ACC-003 -- a long (>500 char) missing-trailing-newline-only input, confirming the `line_no == 0` branch no longer embeds the full raw text verbatim and the message now ends in `"... (truncated)"`). Re-ran `TestValidateIssue83Regressions`/`TestValidateYamlErrorEnrichment` (ACC-004): both pass unmodified, their fixtures stay comfortably under the 300-char cap. Added a `CHANGELOG.md` `[Unreleased]` -> `### Fixed` entry (REQ-007) covering both the `validate` truncation and the `not_in_mdformat_message` fix, referencing GitHub issue #110. Ran the full quality gate (Task 2.6): `ruff format --check` (1659 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no output), `pytest -n auto --cov=src --cov-report=` (3349 passed), and `specmgr docs` (regenerated `docs/api/`/`docs/MCP.md`/`docs/GENERATED.md`, reflecting only Phase 1's already-landed docstring changes -- no further drift from Phase 2's own test-only/`CHANGELOG.md` edits). **Beyond the plan's own named test classes**, discovered (via the orchestrator's own pre-commit `git commit` run, which exercises the full suite rather than just the two files Phase 1 verified) and fixed 2 additional full-suite regressions of the same category: `tests/regression/test_issue_27.py::TestFeat7Task029StrayListMarkerRegression::test_validate_surfaces_an_actionable_message` and `tests/regression/test_issue_71.py::TestIssue71MalformedHeadingRegression::test_validate_surfaces_an_actionable_message` each asserted a substring that now falls past the 300-character cap for their respective fixtures' `validate()`-tool message. Fixed both by adjusting only the affected assertions (a new, narrower substring tuple dropping the now-unreachable tail substring, e.g. `_FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS_VIA_VALIDATE`/`_MALFORMED_HEADING_SUBSTRINGS_VIA_VALIDATE`, each documented with an issue-#110 comment explaining why), plus a new assertion that the message ends with `"... (truncated)"` to keep proving each original issue is still caught and reported actionably -- their sibling `create_<d>`/`update` surfaces (which raise the full, untruncated exception directly, not through `validate()`) were left untouched, since `validate.py`'s truncation is scoped to the non-raising `ValidateResult` path only (REQ-002). No production code was touched beyond Phase 1's own already-landed changes.

#### 2026-09-08 07:44:32.000Z - Phase 1 implemented

Implemented Task 1.1-1.4: added the `_MAX_VALIDATE_ERROR_CHARS = 300` module-level constant to `general/tools/validate.py` and changed `validate()`'s exception handler to build `ValidationErrorEntry.message` via `snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)` instead of `str(ex)` verbatim; updated `validate.py`'s module docstring (the "Non-raising contract" section), `validate()`'s own docstring, and its `@mcp.tool()` `description=` string to describe the new truncation behavior; updated `ValidationErrorEntry.message`'s docstring in `general/models/validate_result.py` to match; fixed `models/md/_markdown.py::not_in_mdformat_message()`'s `line_no == 0` branch to route both `text` and `formatted` through `snippet()` before embedding them (matching every sibling message-builder in that module, e.g. `_raw_html_message`) and updated its docstring. `ruff format --check`, `ruff check`, `vulture`, and `pytest -n auto tests/general/tools/test_validate.py tests/models/md/` (337 tests) all pass unmodified -- no test changes were needed or made in this phase. Phase 2 (new regression tests, `CHANGELOG.md` entry, full-suite quality gate) is next.

#### 2026-09-08 08:00:00.000Z - Created

Feature folder created after an investigation-first planning session for GitHub issue #110, including two live-verified findings that changed the original hypothesis: pydantic's `input_value` repr is already self-capped (dead end), and `not_in_mdformat_message()`'s global-mismatch branch is a genuine, separate unbounded-repr gap worth fixing in the same pass. A real, disk-free repro (duplicate-H1 REQ body) was confirmed to produce a 521-character `validate()` message today, replacing an initially-proposed VCR-duplicate-AC repro that turned out not to reproduce oversized output.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-08 07:53:48.000Z - Fix the 2 extra full-suite regressions as test-only changes, not production changes

The orchestrator's own pre-commit `git commit` run (which exercises the *full* test suite, not just the two files Phase 1's own quality gate covered) surfaced 2 additional failing tests beyond the plan's named `TestValidateIssue83Regressions`/`TestValidateYamlErrorEnrichment`: `tests/regression/test_issue_27.py::TestFeat7Task029StrayListMarkerRegression::test_validate_surfaces_an_actionable_message` and `tests/regression/test_issue_71.py::TestIssue71MalformedHeadingRegression::test_validate_surfaces_an_actionable_message`. Both are the exact same category of regression Task 2.4/ACC-004 already anticipated (a fixture's `validate()`-tool message, previously short enough to substring-match in full, now exceeds `_MAX_VALIDATE_ERROR_CHARS` and gets truncated before the asserted substring is reached) -- not a new, distinct failure mode, and not evidence of a production bug. Applying the same "adjust only the test's expectations, never production behavior" rule Task 2.4 already established for the two named classes: each test's now-unreachable trailing substring was dropped from a new, narrower substring tuple (used only for the `validate`-tool assertion; the sibling `create_<d>`/`update` tests in the same files, which raise the full untruncated exception directly rather than going through `validate()`, were left unmodified since their messages are unaffected), and a new assertion that the message ends with `"... (truncated)"` was added to keep each test proving its original issue (#27/#71) is still caught and reported actionably, just now truncated. This is a judgement call worth recording since the plan's Task 2.4 named only two specific test classes, not these two regression files -- but the underlying rule ("this is intended, in-scope, working-as-designed truncation behavior, not a bug to route around") applies identically.

#### 2026-09-08 08:00:00.000Z - Scope validate() only, not wrap_tool_errors/validate_adr

`validate_adr` raises on failure, and OpenCode's client-side `isError: true` content-discarding bug (ADR 519d1206) already reduces those messages to a bare "Error executing tool ..." regardless of server-side length -- so capping that path has no practical benefit today. Capping the shared `wrap_tool_errors` layer would additionally affect every other raising tool in the repo (`create_<d>`, `update`, etc.), a much larger blast radius than issue #110's narrow "reduce noisy output" ask. Scoped to `validate`'s non-raising `ValidateResult`, the one path confirmed to reach MCP clients unbounded today.

#### 2026-09-08 07:00:00.000Z - Reuse snippet() instead of a new truncation helper

`models/md/_markdown.py::snippet()` already implements exactly the wanted behavior (bounded lines/chars, `"... (truncated)"` suffix) and is explicitly documented as being "for use in an error message" -- reusing it keeps this fix consistent with the one existing precedent in the codebase.

### Related PRs / Commits

- Tracking GitHub issue #110.

### More Information

None.
