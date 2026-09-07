---
classification: null
created: '2026-09-07 04:41:26.135+02:00'
id: feat-103-set-status-error
status: done
type: feat
updated: '2026-09-07 06:10:51.000+02:00'
version: 1.0.0
---

# Feature: Non-Raising Invalid-Status Pre-Check for set_status (#103)

## Plan

### Overview

GitHub issue #103 reports that set_status's error for an invalid status value is uninformative. Investigation found the underlying message is already complete and actionable; the real defect is the previously diagnosed OpenCode 1.18.27 client-side truncation of `isError: true` MCP results (ADR 519d1206), which that ADR deliberately left set_status exposed to. This feature narrowly extends 519d1206's non-raising workaround to set_status's single most common, easily triggered failure mode -- an out-of-vocabulary `status` for a given `type` -- returning a structured, non-raising result instead of a raised pydantic.ValidationError, so the allowed-values detail survives clients that drop error content. Every other set_status failure mode continues to raise unchanged. The drafted, unfiled upstream OpenCode bug report is also finally filed.

### Requirements

- REQ-001: set_status pre-validates `status` against the target domain's own closed status vocabulary (12 whole-body domains' `_ALLOWED_STATUSES` plus ADR's fixed set + `superseded by ...` pattern) before any file I/O, and returns a structured, non-raising result carrying the rejected value and the full allowed-values list when invalid, instead of letting pydantic.ValidationError propagate.

- REQ-002: every other set_status failure mode (unknown id, path-injection/invalid id shape, superseded_by misuse on non-adr types, any other unexpected validation failure) continues to raise exactly as today -- this is a narrow fix, not a full non-raising redesign of set_status.

- REQ-003: a new ADR is authored, referencing and narrowly extending ADR 519d1206's non-raising-workaround rationale to this one additional case, explicitly documenting why the rest of set_status stays raise-based.

- REQ-004: each domain's existing `_ALLOWED_STATUSES`/`_FIXED_STATUSES` constant remains the single source of truth for its vocabulary -- set_status's pre-check reuses it rather than duplicating the list.

- REQ-005: existing tests asserting pydantic.ValidationError is raised for invalid status are updated to assert the new structured result instead, including asserting the message/allowed-values content (closing the "type asserted, content never asserted" gap found during investigation).

- REQ-006: set_status's own tool docstring and the regenerated docs/MCP.md describe the new non-raising invalid-status result shape.

- REQ-007: the drafted, unfiled upstream bug report at `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md` is filed as a real GitHub issue against `anomalyco/opencode`.

### Acceptance Criteria

- [x] ACC-001: `set_status(id=<valid-id>, type="qa", status="closed")` returns a structured, non-raising result (not a raised exception) whose content includes the domain type, the rejected value, and the full sorted list of allowed values for `qa`.

- [x] ACC-002: set_status with an unknown id, a path-injection id, or an invalid superseded_by combination still raises exactly as before (existing tests for these paths pass unchanged).

- [x] ACC-003: a unit-level test proves the new structured result is returned instead of a raised pydantic.ValidationError for every one of the 13 domains (12 whole-body + adr), each asserting its own allowed-values list appears in the result.

- [x] ACC-004: a new ADR documenting this decision exists under `docs/adr/`, passes `validate_adr`, and appears in `docs/adr/README.md` via `specmgr adr-toc`.

- [x] ACC-005: `docs/MCP.md` (regenerated via `specmgr docs`) reflects the updated set_status behavior.

- [ ] ACC-006: the drafted upstream bug report has been filed as a real GitHub issue against `anomalyco/opencode`, its URL recorded in this feature's Related PRs / Commits. (explicitly declined by the user -- filing skipped by design, not forgotten)

- [x] ACC-007: full quality gate green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

### Scope

#### Included

- Pre-checking invalid `status` values in the generic set_status tool for all 13 domains (12 whole-body + adr), returning a structured, non-raising result instead of raising pydantic.ValidationError.

- A shared/reused source of truth for each domain's allowed-status vocabulary (no duplicated lists).

- Updated/added tests asserting the new structured result and its content for the invalid-status path.

- A new ADR documenting and scoping this narrow extension of ADR 519d1206's rationale.

- Updated set_status docstring and regenerated docs/MCP.md.

- Filing the drafted upstream OpenCode bug report.

#### Explicitly Out Of Scope

- Redesigning set_status's other failure modes (unknown id, path-injection, superseded_by misuse) to be non-raising.

- Redesigning any other raise-based tool (`update`, `create_<d>`, `delete`, `set_classification`, `parse_<d>`/`get_<d>`) to a non-raising contract.

- Fixing OpenCode's own client-side truncation bug itself (outside this repo's control) -- only filing the report is in scope.

- Any new artifact-type/domain work (e.g. the still-missing `ac` domain).

### Dependencies

#### Depends On

- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool..."): this feature explicitly extends its rationale to one additional tool/case.

- feat-27-validation (done): supplies the actionable per-domain status-vocabulary messages this feature's structured result reuses.

- feat-81-83-validation (done): original investigation and the drafted upstream bug report this feature builds on and finally files.

### Design Notes

Pre-check happens in `general/tools/set_status.py` before each adapter's `wrap_tool_errors(...)` block currently used only to enrich the constructor-retry exception: look up `status` against the domain's `_ALLOWED_STATUSES`/`_FIXED_STATUSES` constant (imported directly, no new duplication) and, on a miss, short-circuit to a new structured result model (fields still TBD in Phase 1, but shaped like `{valid: false, type, status, allowed_values, message}`, message text following the issue's own suggested wording: "Invalid status '{status}' for type '{type}'. Allowed values: {...}") instead of constructing `XFrontmatter(**fm_data)` and letting it raise. ADR needs both its fixed set and the `superseded by .+` regex reflected in `allowed_values` (likely rendered as a note rather than an exhaustive enumeration). set_status's return type annotation gains this new result type alongside the existing per-domain frontmatter/`Adr` returns.

### Related Decisions

- ADR 519d1206-4d2a-4500-9046-6db635209996: non-raising validate workaround; this feature's new ADR narrowly extends its scope to set_status's invalid-status case only.

### Task List

#### Phase 1: Design & ADR

- [x] Task 1.1: Draft and create the new ADR extending 519d1206 to set_status's invalid-status case; get sign-off; set status accepted. **(ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, reviewed and approved by the user; status set to `accepted`)**

- [x] Task 1.2: Design the shared status-vocabulary lookup (mapping type -> allowed values, incl. ADR's fixed set + pattern) without duplicating each domain's existing private constant.

- [x] Task 1.3: Design the structured invalid-status result shape and exact message wording.

#### Phase 2: Implementation

- [x] Task 2.1: Implement the pre-check in general/tools/set_status.py for all 12 whole-body domains + adr.

- [x] Task 2.2: Update set_status's docstring/description for the new return shape.

- [x] Task 2.3: Confirm every other existing failure mode is unchanged.

#### Phase 3: Tests

- [x] Task 3.1: Update test_out_of_vocabulary_status_raises_validation_error_file_untouched (whole-body + ADR) to assert the new structured, non-raising result and its content.

- [x] Task 3.2: Assert the file on disk remains untouched on rejection.

- [x] Task 3.3: Add regression tests pinning the exact message wording.

#### Phase 4: Docs & Upstream Filing

- [x] Task 4.1: Regenerate docs/api/, docs/GENERATED.md, docs/MCP.md via specmgr docs.

- [x] Task 4.2: Regenerate docs/adr/README.md via specmgr adr-toc.

- [x] Task 4.3: **DEVIATION (per explicit user instruction)**: did NOT file the drafted upstream bug report as a
  real GitHub issue -- only reviewed and updated its drafted text (see Updates below). ACC-006 remains
  unmet by explicit user choice.

#### Phase 5: Verification & Closeout

- [x] Task 5.1: Run full quality gate.

- [x] Task 5.2: Update feature status to done; final Updates entry.

## Progress

### Current Status

**As of 2026-09-07**: **Feature done.** Phase 5 (Verification & Closeout) complete: every acceptance criterion
except the explicitly-declined ACC-006 is verified and checked (ACC-001 through ACC-005 and ACC-007), the full
quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`,
`pytest -n auto --cov=src --cov-report=`) is green (3346 tests passed, zero failures), and the feature's own
frontmatter `status` is now `done`. ACC-006 remains permanently, deliberately unmet -- the drafted upstream
OpenCode bug report was reviewed and updated (Phase 4) but never filed, per the user's explicit, repeated
instruction; this is a known, accepted gap for this feature, not an oversight. All five phases (Design & ADR,
Implementation, Tests, Docs & Upstream Filing, Verification & Closeout) are now complete.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-07 19:00:00.000Z - Phase 5 (Verification & Closeout) complete -- feature done

Walked every acceptance criterion with fresh, independent evidence rather than re-checking boxes blindly.
**ACC-001**: created a temporary `qa` document in an isolated `SPECMGR_DOCS_DIR` (`tempfile.mkdtemp()`, never
touching the real `docs/` tree) and called `set_status(id=<that id>, type="qa", status="closed")` directly at the
Python level -- confirmed it returns `InvalidStatusResult(valid=False, type='qa', status='closed',
allowed_values=['active', 'cancelled', 'done', 'draft'], message="Invalid status 'closed' for type 'qa'. Allowed
values: active, cancelled, done, draft")`, i.e. a structured, non-raising result carrying the domain type, the
rejected value, and the full sorted allowed-values list, exactly as ACC-001 requires. (A first attempt to
reproduce this same check purely through the live MCP `set_status` tool call surfaced as `"Error executing tool
set_status"` in this session's own MCP client -- concrete, first-hand corroboration of the OpenCode client-side
`isError` truncation defect ADR 519d1206 and this feature's own ADR b399f1ce both discuss, not a regression in
the fix itself: a follow-up `get_qa` on the same document confirmed its `status` was still `draft`, i.e. nothing
was written, consistent with a non-raising rejection happening before any file I/O.) **ACC-002**: ran the six
specific existing tests covering set_status's still-raising failure modes --
`TestSetStatusWholeBodyDomains.test_unknown_id_raises_domain_not_found`,
`TestSetStatusAdr.test_unknown_id_raises_adr_not_found`,
`TestSetStatusWholeBodyDomains.test_superseded_by_with_non_adr_type_raises_value_error_file_untouched`,
`TestSetStatusSupersededByGuard.test_unknown_id_with_superseded_by_raises_value_error_not_not_found`,
`TestSetStatusInjection.test_injection_ids_raise_value_error_and_leave_the_seed_untouched`, and
`TestSetStatusInjection.test_adr_injection_ids_raise_value_error_and_leave_the_seed_untouched` -- all six pass.
**ACC-003**: ran `TestSetStatusWholeBodyDomains.test_out_of_vocabulary_status_raises_validation_error_file_untouched`
(all 12 whole-body domains via `subTest`) and
`TestSetStatusAdr.test_out_of_vocabulary_status_raises_validation_error_file_untouched` (adr) -- both pass.
**ACC-004**: confirmed
`docs/adr/b399f1ce-ed42-4929-b01c-7a57d18e8014-extend-the-non-raising-structured-result-workaround-to-set-s.md`
exists with frontmatter `status: accepted`, and that `docs/adr/README.md` lists it (line 92-93). **ACC-005**:
re-confirmed still checked from Phase 4, not re-verified from scratch (per the orchestrator's own instruction).
**ACC-006**: left explicitly, permanently unchecked -- the drafted upstream OpenCode bug report was never filed,
by the user's own repeated, explicit choice; this is a known, accepted scope deviation for this feature, not an
oversight, and nothing was filed against `anomalyco/opencode` during this phase either. **ACC-007**/Task 5.1: ran
the full quality gate -- `uv run --frozen ruff format --check` (1658 files already formatted), `uv run --frozen
ruff check` ("All checks passed!"), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no output,
clean), `uv run --frozen pytest -n auto --cov=src --cov-report=` (3346 passed in 43.50s, 24 workers) -- all four
green with zero regressions. Task 5.2: set this feature's own frontmatter `status` from `planning` to `done` and
bumped `updated`, via a direct file edit of this README's YAML frontmatter -- not the `specmgr_set_status` MCP
tool -- because this document's own body does not conform to the strict `feat` v1 schema `list_feat`/`get_feat`/
`set_status` parse against (a pre-existing condition, not introduced by this phase: `list_feat` independently
confirms 34 of this repo's 41 feature folders, including this one, already fail strict parsing for unrelated
free-form-prose reasons -- e.g. this file's own Task 4.3 line wraps a `[x]` marker onto a continuation line that
the strict checkbox-marker grammar rejects), so a raw, targeted frontmatter edit was the only option actually
available, consistent with how every prior phase in this same feature updated its own README. No files under
`src/` or `tests/` were touched in this phase; nothing was committed. Every checkbox in the Task List and
Acceptance Criteria sections is now checked except ACC-006, which remains deliberately unchecked.

#### 2026-09-07 18:00:00.000Z - Phase 4 (Docs & Upstream Filing) complete, Task 4.3 scope-deviated per user instruction

Ran `uv run --frozen specmgr docs` and `uv run --frozen specmgr adr-toc` (Tasks 4.1/4.2); both produced **no
diff** against the working tree, and a second immediate run of each was also diff-free, confirming Phase 2's
pre-commit hook had already regenerated `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`, and
`docs/adr/README.md` in its own commit (`d8b2077`) -- this phase's runs were a confirmation, not a fresh
regeneration. Verified ACC-005 directly: `docs/MCP.md` line 475 (tool-index table) and the full `### Tool:
set_status` section both read "an out-of-vocabulary `status` does NOT raise -- it returns a structured,
non-raising `InvalidStatusResult` (`{valid: false, type, status, allowed_values, message}`) instead, so the
allowed-values detail survives MCP clients that truncate error content" -- marked `[x]`. Per the orchestrator's
explicit, twice-repeated instruction ("do not file the issue, only draft or update the text for it"), Task 4.3
did **not** run `gh issue create` or file anything against `anomalyco/opencode` -- instead reviewed the drafted
report at `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md` and made two small,
substantive text updates given what feat-103 itself demonstrated (see Decisions Made): the status blockquote now
cross-references this feature's own ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, and the Impact section now notes
the same non-raising workaround had to be independently applied a second time, within the same week, to an
unrelated tool (`set_status`) -- concrete evidence the underlying OpenCode defect is not a one-off confined to
`validate`. ACC-006 is left unmet by explicit user choice (checkbox unchecked, annotated inline in Acceptance
Criteria) -- not forgotten, not blocked. No files under `src/` or `tests/` were touched; nothing was committed.

#### 2026-09-07 17:00:00.000Z - Phase 3 (Tests) complete

Rewrote all 18 previously-failing test methods (per Phase 2's own tracing) to assert the new `InvalidStatusResult` return value instead of a raised `pydantic.ValidationError`, while keeping every existing file-untouched-on-disk assertion: `tests/general/tools/test_set_status.py`'s `TestSetStatusWholeBodyDomains.test_out_of_vocabulary_status_raises_validation_error_file_untouched` (parameterized over all 12 whole-body `_CASES`) and `TestSetStatusAdr.test_out_of_vocabulary_status_raises_validation_error_file_untouched` (ADR, asserting `allowed_values == sorted(_ADR_ALLOWED_STATUSES) + ["superseded by <target-id>"]`, matching `_check_status_allowed`'s exact literal); `tests/general/tools/test_error_context.py`'s `TestGenericSetStatusToolErrorContext.test_set_status_tsk_out_of_vocabulary_names_domain_and_tool` (see Decisions Made below); and one test each in `tests/dec/tools/test_integration.py`, `tests/sop/tools/test_integration.py`, `tests/sysrs/tools/test_integration.py`, `tests/vcr/tools/test_integration.py`, `tests/feat/tools/test_integration.py` (each now also imports and asserts against its own domain's `_ALLOWED_STATUSES` constant for a full `result.allowed_values` check, not just presence). Added two new Task 3.3 regression tests in `test_set_status.py` (`test_invalid_status_message_wording_pinned`, `test_invalid_status_message_wording_pinned_for_adr`) that `assertEqual` the exact literal `message` string, no `assertIn`. Updated `test_set_status.py`'s module docstring (no longer says invalid status "raises `pydantic.ValidationError`") and `test_error_context.py`'s module + class docstrings to describe the new non-raising path and why it bypasses `wrap_tool_errors`. Removed the now-unused `from pydantic import ValidationError` import from `test_set_status.py` and all five integration test files (verified each had exactly one use, the rewritten test); kept it in `test_error_context.py`, which still has two legitimate, untouched uses (`TestCreateToolErrorContext`/`TestGenericUpdateToolErrorContext`'s own `req` cases). Files touched: `tests/general/tools/test_set_status.py`, `tests/general/tools/test_error_context.py`, `tests/dec/tools/test_integration.py`, `tests/sop/tools/test_integration.py`, `tests/sysrs/tools/test_integration.py`, `tests/vcr/tools/test_integration.py`, `tests/feat/tools/test_integration.py` -- no `src/` changes (tests-only phase). Quality gate: `ruff format --check`/`ruff check` on all 7 files (both clean), the 7-file targeted `pytest -n auto -v` (41 passed, 155 subtests passed), and the full `pytest -n auto` suite (3346 passed, 0 failures) -- the suite is fully green again after Phase 2's expected interim breakage.

#### 2026-09-07 16:00:00.000Z - Fixed adr+superseded_by edge case flagged after Phase 2; ADR amended

The user confirmed the edge case flagged at the end of Phase 2: when `type="adr"` and `superseded_by` is given, `_check_status_allowed` (`general/tools/set_status.py`) now skips validating `status` entirely (returns `None`/valid unconditionally), regardless of its content, instead of checking the raw, discarded `status` argument against `_ADR_FIXED_STATUSES`/`_ADR_SUPERSEDED_PATTERN`. This matches `models.adr.v1.mutations.set_status`'s own existing semantics, which ignores `status` and composes `f"superseded by {superseded_by}"` whenever `superseded_by` is given. The helper's signature grew a `superseded_by: str | None` parameter (the `adr`-branch check now short-circuits to `None`/valid when `superseded_by is not None`, before touching `status` at all); its call site in `set_status()` was updated to pass `superseded_by` through. Re-verified with an extended scratch script: `set_status(id=<adr>, type="adr", status="garbage-not-a-valid-status", superseded_by="some-other-id")` now succeeds and persists `status == "superseded by some-other-id"` (previously would have incorrectly returned `InvalidStatusResult`); the same call with `superseded_by=None` still correctly returns `InvalidStatusResult`; every other previously-verified Task 2.3 scenario (path-injection id, `superseded_by`-on-non-adr `ValueError`, unknown id, valid id+status happy path, adr with a valid fixed status) still passes unchanged. `ruff format --check`/`ruff check` on the two touched files and `vulture` on the whole `src/` tree are all clean. ADR b399f1ce-ed42-4929-b01c-7a57d18e8014's Decision Outcome (point 3) was amended via `update_section` with a short paragraph documenting this refinement; `validate_adr` still passes after the amendment.

#### 2026-09-07 15:00:00.000Z - Phase 2 (Implementation) complete

Implemented ADR b399f1ce-ed42-4929-b01c-7a57d18e8014's design in full: created `general/models/invalid_status_result.py` (new `InvalidStatusResult` Pydantic model, `valid`/`type`/`status`/`allowed_values`/`message` fields, re-exported from `general/models/__init__.py` alongside `ValidateResult`); added a private `_ALLOWED_STATUSES_BY_TYPE` mapping to `general/tools/set_status.py` built from direct imports of each of the 12 whole-body domains' own `_ALLOWED_STATUSES` constant (from each domain's `models/v{N}/frontmatter.py`, not its package `__init__.py`) plus ADR's `_FIXED_STATUSES`/`_SUPERSEDED_PATTERN`; added a `_check_status_allowed` helper implementing the pre-check (mirrors `AdrFrontmatter._validate_status`'s own in/pattern-match logic for `type="adr"`); wired the pre-check into the public `set_status()` function after the existing `validate_id`/`superseded_by` guards but before adapter dispatch, so an invalid status is now rejected before any domain lock or file I/O; updated the `@mcp.tool` description, `set_status()`'s own docstring (Returns/Raises sections), and the module docstring to describe the new non-raising case and note that no other path in this file can still raise `pydantic.ValidationError` in practice. Verified with a scratch script (not committed) that all four required failure-mode scenarios remain unaffected: path-injection/wrong-shape id still raises `ValueError` first; `superseded_by` misuse on a non-adr type still raises `ValueError` first; unknown id + valid status still raises the domain's own `XNotFoundError`; valid id + valid status still succeeds via the adapter -- for both a whole-body domain (qa) and adr (including `superseded_by` composition). `ruff format --check`, `ruff check`, and `vulture` are clean on the changed files/whole `src/` tree. Running the full test suite (informational only, not this phase's gate) confirmed exactly 18 existing test methods now fail because they still assert a raised `pydantic.ValidationError` for set_status's invalid-status case -- all in `tests/general/tools/test_set_status.py` (`TestSetStatusWholeBodyDomains`/`TestSetStatusAdr`'s `test_out_of_vocabulary_status_raises_validation_error_file_untouched`), `tests/general/tools/test_error_context.py` (`TestGenericSetStatusToolErrorContext.test_set_status_tsk_out_of_vocabulary_names_domain_and_tool`), and four domains' `test_integration.py` files (`dec`, `feat`, `sop`, `sysrs`, `vcr` each have one `test_set_status_rejects_*` test) -- all expected, Phase 3 owns fixing them.

#### 2026-09-07 14:00:00.000Z - ADR reviewed and accepted; Phase 1 fully complete

The user reviewed and approved ADR b399f1ce-ed42-4929-b01c-7a57d18e8014's design as drafted at status `proposed`; its status was then set to `accepted` via `specmgr_set_status` (type="adr"), and `specmgr_validate_adr` was re-run to confirm it still passes after the status change. This resolves Task 1.1's outstanding sign-off/accepted-status caveat -- Phase 1 (Design & ADR) is now fully complete; Phase 2 (Implementation) can begin.

#### 2026-09-07 13:00:00.000Z - Phase 1 (Design & ADR) drafted, pending sign-off

Completed Tasks 1.2/1.3 design work and drafted/created ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 at status `proposed` (not yet `accepted` -- awaiting human sign-off before that bump, per the orchestrator's explicit process deviation from Task 1.1's literal wording). The ADR narrowly extends ADR 519d1206's non-raising-workaround rationale to set_status's invalid-status case, explicitly documents why every other set_status failure mode (unknown id, path-injection, superseded_by misuse) stays raise-based, and records the concrete vocabulary-lookup and result-shape designs Phase 2 implements from. `specmgr_validate_adr` passes.

#### 2026-09-07 12:00:00.000Z - Drafted feature from GitHub issue #103

Investigated issue #103's premise (set_status error message lacks allowed values) and found the message is already complete server-side; traced the real symptom to the OpenCode 1.18.27 isError-truncation defect already diagnosed in ADR 519d1206, which had explicitly left set_status out of its non-raising workaround. Agreed with the user to scope this feature to a narrow, non-raising pre-check for set_status's invalid-status case only, plus filing the previously drafted, unfiled upstream OpenCode bug report. Posted a summary comment to GitHub issue #103.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-07 18:00:00.000Z - Updated (not left unchanged) the drafted upstream bug-report text, without filing it

Task 4.3 was explicitly scope-adjusted by the user to review-and-possibly-update the drafted upstream OpenCode
bug report's text, never to file it. On review, two small, substantive updates were judged worth making rather
than leaving the draft untouched: (1) the top status blockquote, which already cross-referenced ADR
519d1206 as the one prior instance of this repo's non-raising workaround, was extended to also cross-reference
this feature's own ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, since feat-103 is now a second, concrete,
independent instance of the same underlying OpenCode defect forcing the same kind of server-side workaround on
an otherwise-unrelated tool; (2) the Impact section gained one sentence noting the workaround had to be applied
twice within the same week, which strengthens the report's core claim (this is a systemic risk for any
raise-based MCP tool, not a one-off quirk of `validate`) with fresh, dated evidence rather than speculation.
Both edits were kept minimal and additive -- no existing claim, reproduction step, or piece of evidence in the
draft was altered or removed, since feat-103 did not contradict anything already documented there, only added
one more corroborating data point.

#### 2026-09-07 17:00:00.000Z - test_error_context.py's set_status test rewritten, not deleted or left raise-based

`TestGenericSetStatusToolErrorContext.test_set_status_tsk_out_of_vocabulary_names_domain_and_tool`'s original premise (asserting `wrap_tool_errors`'s `"{domain} {tool}"` prefix on a raised `pydantic.ValidationError`) no longer holds for this one failure mode, since Phase 2's pre-check now short-circuits before `wrap_tool_errors` is ever entered. Rather than deleting the test (its purpose -- proving an invalid status still identifies which domain rejected it -- still matters) or leaving it broken, it was rewritten to call `set_status` and assert the returned `InvalidStatusResult`'s own `type`/`message` fields carry that same identifying information (`result.type == "tsk"`, `"tsk" in result.message`), plus `isinstance`/`valid is False`. The class and method docstrings were updated to explain why this one case diverges from its sibling tests in the same file (`TestCreateToolErrorContext`, `TestGenericUpdateToolErrorContext`), which still legitimately exercise `wrap_tool_errors` for other tools/failure modes and were left untouched.

#### 2026-09-07 16:00:00.000Z - Pre-check skips status validation entirely for adr+superseded_by

Resolved, with the user's sign-off, an edge case flagged at the end of Phase 2: for `type="adr"` with `superseded_by` given, the invalid-status pre-check now skips validating `status` entirely (never rejects it, regardless of content), matching `models.adr.v1.mutations.set_status`'s own existing semantics of ignoring `status` and composing `"superseded by {superseded_by}"` in that case. Without this, the pre-check would have incorrectly rejected an otherwise-valid `superseded_by` call whenever the caller's (discarded) `status` argument happened to be out of vocabulary -- a behavior regression the original ADR text did not explicitly address. ADR b399f1ce-ed42-4929-b01c-7a57d18e8014's Decision Outcome (point 3) was amended to record this refinement.

#### 2026-09-07 12:00:00.000Z - Scoped to a narrow pre-check, not a full redesign

Chose to extend ADR 519d1206's non-raising workaround only to set_status's single most common failure mode (invalid status value), leaving every other set_status failure mode raise-based, rather than converting set_status's entire contract to non-raising -- keeps the change small and testable, and mirrors 519d1206's own "targeted workaround, not a general best practice" framing.

### More Information

- ADR 519d1206-4d2a-4500-9046-6db635209996: the prior decision this feature extends.

- `.specmgr/feat/feat-81-83-validation/README.md` and `opencode-issue-mcp-tool-error-truncated.md`: the original investigation and drafted upstream report this feature builds on.
