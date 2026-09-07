---
classification: null
created: '2026-09-07 04:41:26.135+02:00'
id: feat-103-set-status-error
status: planning
type: feat
updated: '2026-09-07 04:41:26.135+02:00'
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

- [ ] ACC-001: `set_status(id=<valid-id>, type="qa", status="closed")` returns a structured, non-raising result (not a raised exception) whose content includes the domain type, the rejected value, and the full sorted list of allowed values for `qa`.

- [ ] ACC-002: set_status with an unknown id, a path-injection id, or an invalid superseded_by combination still raises exactly as before (existing tests for these paths pass unchanged).

- [ ] ACC-003: a unit-level test proves the new structured result is returned instead of a raised pydantic.ValidationError for every one of the 13 domains (12 whole-body + adr), each asserting its own allowed-values list appears in the result.

- [ ] ACC-004: a new ADR documenting this decision exists under `docs/adr/`, passes `validate_adr`, and appears in `docs/adr/README.md` via `specmgr adr-toc`.

- [ ] ACC-005: `docs/MCP.md` (regenerated via `specmgr docs`) reflects the updated set_status behavior.

- [ ] ACC-006: the drafted upstream bug report has been filed as a real GitHub issue against `anomalyco/opencode`, its URL recorded in this feature's Related PRs / Commits.

- [ ] ACC-007: full quality gate green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

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

- [ ] Task 1.1: Draft and create the new ADR extending 519d1206 to set_status's invalid-status case; get sign-off; set status accepted.

- [ ] Task 1.2: Design the shared status-vocabulary lookup (mapping type -> allowed values, incl. ADR's fixed set + pattern) without duplicating each domain's existing private constant.

- [ ] Task 1.3: Design the structured invalid-status result shape and exact message wording.

#### Phase 2: Implementation

- [ ] Task 2.1: Implement the pre-check in general/tools/set_status.py for all 12 whole-body domains + adr.

- [ ] Task 2.2: Update set_status's docstring/description for the new return shape.

- [ ] Task 2.3: Confirm every other existing failure mode is unchanged.

#### Phase 3: Tests

- [ ] Task 3.1: Update test_out_of_vocabulary_status_raises_validation_error_file_untouched (whole-body + ADR) to assert the new structured, non-raising result and its content.

- [ ] Task 3.2: Assert the file on disk remains untouched on rejection.

- [ ] Task 3.3: Add regression tests pinning the exact message wording.

#### Phase 4: Docs & Upstream Filing

- [ ] Task 4.1: Regenerate docs/api/, docs/GENERATED.md, docs/MCP.md via specmgr docs.

- [ ] Task 4.2: Regenerate docs/adr/README.md via specmgr adr-toc.

- [ ] Task 4.3: File the drafted upstream bug report against anomalyco/opencode; record the resulting issue URL.

#### Phase 5: Verification & Closeout

- [ ] Task 5.1: Run full quality gate.

- [ ] Task 5.2: Update feature status to done; final Updates entry.

## Progress

### Current Status

**As of 2026-09-07**: Feature drafted from GitHub issue #103. Root cause investigated and confirmed as the previously diagnosed OpenCode 1.18.27 client-side isError truncation bug (ADR 519d1206). Scope agreed: a narrow, non-raising pre-check for set_status's invalid-status failure mode only, plus filing the drafted upstream OpenCode bug report. No implementation started yet. A brief explanatory comment was posted to GitHub issue #103.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-07 12:00:00.000Z - Drafted feature from GitHub issue #103

Investigated issue #103's premise (set_status error message lacks allowed values) and found the message is already complete server-side; traced the real symptom to the OpenCode 1.18.27 isError-truncation defect already diagnosed in ADR 519d1206, which had explicitly left set_status out of its non-raising workaround. Agreed with the user to scope this feature to a narrow, non-raising pre-check for set_status's invalid-status case only, plus filing the previously drafted, unfiled upstream OpenCode bug report. Posted a summary comment to GitHub issue #103.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-07 12:00:00.000Z - Scoped to a narrow pre-check, not a full redesign

Chose to extend ADR 519d1206's non-raising workaround only to set_status's single most common failure mode (invalid status value), leaving every other set_status failure mode raise-based, rather than converting set_status's entire contract to non-raising -- keeps the change small and testable, and mirrors 519d1206's own "targeted workaround, not a general best practice" framing.

### More Information

- ADR 519d1206-4d2a-4500-9046-6db635209996: the prior decision this feature extends.

- `.specmgr/feat/feat-81-83-validation/README.md` and `opencode-issue-mcp-tool-error-truncated.md`: the original investigation and drafted upstream report this feature builds on.
