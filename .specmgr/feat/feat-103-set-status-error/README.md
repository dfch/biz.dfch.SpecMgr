---
classification: null
created: '2026-09-07 04:41:26.135+02:00'
id: feat-103-set-status-error
status: done
type: feat
updated: '2026-10-07T06:21:40.881Z'
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

- [x] ACC-006: the drafted upstream bug report has been filed as a real GitHub issue against `anomalyco/opencode`, its URL recorded in this feature's Related PRs / Commits. Filed later, in a follow-up session, as [anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740).

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

#### Phase 100: Design & ADR

- [x] Task 100.100: Draft and create the new ADR extending 519d1206 to set_status's invalid-status case; get sign-off; set status accepted. **(ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, reviewed and approved by the user; status set to `accepted`)**

- [x] Task 100.110: Design the shared status-vocabulary lookup (mapping type -> allowed values, incl. ADR's fixed set + pattern) without duplicating each domain's existing private constant.

- [x] Task 100.120: Design the structured invalid-status result shape and exact message wording.

#### Phase 110: Implementation

- [x] Task 110.100: Implement the pre-check in general/tools/set_status.py for all 12 whole-body domains + adr.

- [x] Task 110.110: Update set_status's docstring/description for the new return shape.

- [x] Task 110.120: Confirm every other existing failure mode is unchanged.

#### Phase 120: Tests

- [x] Task 120.100: Update test_out_of_vocabulary_status_raises_validation_error_file_untouched (whole-body + ADR) to assert the new structured, non-raising result and its content.

- [x] Task 120.110: Assert the file on disk remains untouched on rejection.

- [x] Task 120.120: Add regression tests pinning the exact message wording.

#### Phase 130: Docs & Upstream Filing

- [x] Task 130.100: Regenerate docs/api/, docs/GENERATED.md, docs/MCP.md via specmgr docs.

- [x] Task 130.110: Regenerate docs/adr/README.md via specmgr adr-toc.

- [x] Task 130.120: **DEVIATION (per explicit user instruction)**: did NOT file the drafted upstream bug report as a real GitHub issue -- only reviewed and updated its drafted text (see Updates below). ACC-006 remains unmet by explicit user choice.

#### Phase 140: Verification & Closeout

- [x] Task 140.100: Run full quality gate.

- [x] Task 140.110: Update feature status to done; final Updates entry.

## Progress

### Current Status

**As of 2026-09-07**: **Feature done.** Phase 5 (Verification & Closeout) complete: every acceptance criterion,
including ACC-006, is now verified and checked, the full quality gate (`ruff format --check`, `ruff check`,
`vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src --cov-report=`) is green (3346 tests
passed, zero failures), and the feature's own frontmatter `status` is `done`. ACC-006 was left deliberately
unmet at original closeout time (the drafted upstream OpenCode bug report was reviewed/updated in Phase 4 but
not filed, per the user's explicit, repeated instruction at the time), then filed in a later session as
[anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740) -- see Updates below. All five
phases (Design & ADR, Implementation, Tests, Docs & Upstream Filing, Verification & Closeout) are complete.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-07 20:00:00.000Z - ACC-006 closed: upstream bug report filed as anomalyco/opencode#47740

The drafted upstream bug report (`.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md`)
was revised further in a later session (tighter, template-conforming wording per `anomalyco/opencode`'s own
`CONTRIBUTING.md`/`bug-report.yml` guidance against "AI-generated walls of text": internal ADR/feature
cross-references moved out of the filed body into an HTML comment, the reproduction table's example id changed
from a sensitive-looking `../../../etc/passwd` path to a clearly-benign, confirmed-non-existent
`./non-existing-file.txt`, and the "unknown id" UUID changed from the nil UUID to an obviously-fake
`deadbeef-dead-...-deadbeefdead` pattern), then filed via `gh issue create` as
[anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740). ACC-006 is now checked; this
feature's frontmatter `updated` timestamp was bumped accordingly. No `src/`/`tests/` files were touched.

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

- [anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740): the upstream bug report (ACC-006), filed in a later session after this feature's own closeout.
