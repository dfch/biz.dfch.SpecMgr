---
classification: null
created: '2026-10-08T11:50:25.678+02:00'
id: feat-204-create-error
status: planning
type: feat
updated: '2026-10-08T11:50:25.678+02:00'
version: 1.0.0
---

# Feature: Non-Raising `ValidateResult` for `create_<d>`/`parse_<d>` on Content Validation Failure (#204)

## Plan

### Overview

GitHub issue #204: the 12 `create_<d>` tools (and their `parse_<d>` counterparts) still surface content validation failures as raised `AssertionError`/`pydantic.ValidationError`. Through an MCP client these are truncated to a bare tool-execution error (e.g. `Error executing tool create_feat`) -- no field path, no line reference, no cause/fix hint -- even though the raised exception message is actionable (feat-27-validation).

The non-raising structured-result chain (ADR 519d1206, extended by ADR b399f1ce -> case 2, ADR 9080b37c -> case 3, ADR b8c9bfea -> case 4) deliberately covered `validate`, `set_status`, `get_<d>`, and the four generic mutation tools (`update`, `edit`, `set_status`, `set_classification`) -- ADR b8c9bfea's scope statement explicitly holds that `create_<d>`, ..., `parse_<d>`/`get_<d>` all keep raising. This feature is the natural next (case 5) extension of that chain: give the `create_<d>` tools (and `parse_<d>`) the same non-raising `ValidateResult` channel, so an agent calling them gets the actionable message in-band instead of a truncated raise.

Observed live dogfooding this repo's own tooling (2026-10-07): `create_feat` called with a body containing a soft-wrapped (multi-physical-line) list item in `## Plan > ### Requirements` (rejected by the feat schema via feat-99's `single_line_text` guard) returned `Error executing tool create_feat` -- no message, no field path, no line, no hint. The workaround cost one extra round-trip per failure: re-run the same content through the generic `validate` tool (`type="feat"`) to get the actionable message, fix, then `create_feat` succeeded.

### Requirements

- REQ-001: Each of the 12 `create_<d>` tools must, on a content validation failure of the caller-submitted content (the `AssertionError`/`pydantic.ValidationError` raised under `wrap_tool_errors`), return the existing non-raising `ValidateResult` (`valid=False`, single `errors[].message` capped at 300 chars exactly as the generic `validate` tool caps it -- feat-110) and write nothing to disk in that case.
- REQ-002: Each of the 12 `parse_<d>` tools must, for an existing file that fails to parse, return the same non-raising `ValidateResult` channel (its raised message today is equally actionable and equally truncated); a truly-absent path must continue to raise the domain's not-found error unchanged.
- REQ-003: Caller-usage errors must keep raising per the `update`/`edit` precedent (feat-170 REQ-004): malformed id shape (`ValueError`), and `create_feat`'s already-existing id/folder (`FileExistsError`); the new non-raising branch must cover only the content-validation-failure channel and must not reorder or mask the pre-dispatch guards.
- REQ-004: `create_adr` is out of scope (the ADR domain is excluded from the whole-body chain); `delete`/`set_feat_id` take no document content and are unaffected; the frontmatter-only success shape of the write tools (feat-69) is unchanged.
- REQ-005: Update the return-type union and the `@mcp.tool()` description/docstring (`Returns`/`Raises` sections) of the 12 `create_<d>` tools and the 12 `parse_<d>` tools to document the new `ValidateResult` branch.
- REQ-006: Write a new ADR recording this decision as case 5 of the ADR 519d1206 chain (after case 1 = 519d1206/`validate`, case 2 = b399f1ce/`set_status`, case 3 = 9080b37c/`get_<d>`, case 4 = b8c9bfea/the four generic mutation tools), referencing GitHub issue #204, and updating ADR b8c9bfea's scope statement (which currently holds that `create_<d>`/`parse_<d>` keep raising) -- as a dated revision of b8c9bfea or a new ADR that explicitly supersedes that sentence.
- REQ-007: Docs sync: `AGENTS.md` (the `general/` package bullet and per-domain bullets describing `create_<d>`/`parse_<d>` behavior), `server.py`'s module docstring, `docs/MCP.md` regeneration via `specmgr mcp-docs`, and a `CHANGELOG.md` `[Unreleased]` entry.
- REQ-008: Add unit test coverage, per domain, for: (a) the create-failure channel (invalid content -> `ValidateResult(valid=False, ...)`, nothing written), (b) the parse-failure channel (existing-but-broken file -> `ValidateResult(valid=False, ...)`) plus the truly-absent-path regression guard (still raises the domain's not-found error), (c) guard ordering (caller-usage errors still raise), and (d) the happy path (valid content -> frontmatter-only success, unchanged shape).

### Acceptance Criteria

- [ ] ACC-001: (REQ-001/REQ-003) For every one of the 12 `create_<d>` tools, submitting genuinely invalid content returns `ValidateResult(valid=False, errors=[...])` (never raises) with nothing written to disk, while every caller-usage error (malformed id shape, `create_feat`'s already-existing id/folder) still raises exactly as before.
- [ ] ACC-002: (REQ-002) For every one of the 12 `parse_<d>` tools, an existing file that fails to parse returns `ValidateResult(valid=False, errors=[...])` (never raises), while a truly-absent path still raises the domain's own not-found error unchanged.
- [ ] ACC-003: (REQ-001/REQ-002) The `errors[].message` of every new branch is `str(exception)` capped at exactly 300 chars via the same `snippet(..., max_chars=300)` helper the generic `validate` tool uses (feat-110), so the bounded-message contract is not re-opened on the create/parse surface.
- [ ] ACC-004: (REQ-004) `create_adr`, `delete`, `set_feat_id`, and the generic `validate` tool are behaviorally unchanged; every `create_<d>`/`parse_<d>` success path returns the same frontmatter-only shape as before (feat-69).
- [ ] ACC-005: (REQ-005/REQ-007) The docstrings, `@mcp.tool()` descriptions, `AGENTS.md`, and `server.py`'s module docstring accurately describe the new non-raising branches; `docs/MCP.md` regenerates cleanly via `specmgr mcp-docs` with no manual edits needed afterward; the `CHANGELOG.md` `[Unreleased]` entry lands.
- [ ] ACC-006: (REQ-006) The new ADR (case 5) exists, is linked from this feature's Related Decisions, is accepted before or alongside the code landing, and updates ADR b8c9bfea's "create/parse keep raising" scope statement.

### Scope

#### Included

- All 12 `create_<d>` tools (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs): the content-validation-failure -> `ValidateResult` branch.
- All 12 `parse_<d>` tools: the existing-but-broken-file -> `ValidateResult` branch.
- Reuse of the existing `ValidateResult`/`ValidationErrorEntry` models and the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple and 300-char capping -- no new result model, no new helper.
- A new ADR (case 5 of the 519d1206 chain) plus ADR b8c9bfea's scope-statement update.
- Docstring/description updates on all 24 tools, `AGENTS.md`, `server.py`'s module docstring, `docs/MCP.md` regeneration.
- A `CHANGELOG.md` `[Unreleased]` entry.
- Test coverage across all 12 domains for both new branches plus the guard-ordering and happy-path regression guards.

#### Explicitly Out Of Scope

- `create_adr` (and the rest of the ADR domain) -- the ADR domain is excluded from the whole-body non-raising chain; `validate_adr` remains its own standalone tool.
- `delete` and `set_feat_id` -- they take no document content and cannot fail content validation.
- `get_<d>`'s parse-failure handling -- already solved by ADR 9080b37c/feat-150 via the non-raising `ParseFailureResult` (a different, already-locked channel).
- Changing the generic `validate` tool's behavior or its 300-char error cap (feat-110), or `update`/`edit`'s case-4 branches (feat-170).
- Fixing the underlying, out-of-this-repo's-control MCP client-side `isError: true` truncation defect itself -- this feature is a workaround within this repo's own tool contracts, same as every prior link in the 519d1206 chain.
- Changing the frontmatter-only success return shape of the write tools (feat-69).

### Dependencies

#### Depends On

- ADR 519d1206-4d2a-4500-9046-6db635209996 (case 1: `validate` as a non-raising structured-result tool).
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (case 2: `set_status`'s `InvalidStatusResult`).
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (case 3: `get_<d>`'s `ParseFailureResult`).
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (case 4: feat-170/issue #170 -- the four generic mutation tools; its scope statement is the sentence this feature updates).
- feat-110 (the 300-char capping convention), feat-27-validation (actionable exception messages -- the content this chain protects), feat-69 (frontmatter-only success shape).

#### Blocks

- None known.

### Design Notes

**Reuse, not new models.** `ValidateResult`/`ValidationErrorEntry` already exist and are exercised in production by the generic `validate` tool and (since feat-170) by `update`/`edit`. This feature is purely a matter of catching the right exception at the right point in each of the 24 tool functions and returning the existing model -- no new pydantic model, no new MCP result shape.

**Where each branch goes.** `create_<d>`: wrap the `wrap_tool_errors(...)` block that validates the caller-submitted body; catch the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple (`AssertionError`, `pydantic.ValidationError`, `yaml.YAMLError` -- the third unreachable for body-only content but kept so the catch shape is uniform); return `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])`. For `create_feat`, the branch sits strictly after the id-shape `ValueError` guard and the already-existing-id/folder `FileExistsError` check (both keep raising per REQ-003) and before any folder/file write. `parse_<d>`: the same catch around the parse of the existing file; the domain's not-found error for a truly-absent path is never intercepted.

**Caller-usage errors keep raising.** Per the `update`/`edit` precedent (feat-170 REQ-004), only the structural/field content-validation-failure channel becomes non-raising; no `ValueError` of any kind is caught by the new branches.

**ADR shape.** A new ADR recording case 5 of the chain (consistent with cases 1-4 each having their own ADR); ADR b8c9bfea's scope statement ("`create_<d>`, ..., `parse_<d>`/`get_<d>` all keep raising") is updated/referenced from it so the chain's documentation stays consistent. A dated revision of b8c9bfea remains an acceptable alternative; the form is finalized in Phase 100 (Task 100.100).

**Phase discipline (standing requirement, feat-150/feat-167).** Every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches) and exactly one Conventional Commit; the new/converted tests travel with their code phase (Phase 110/120), Phase 130 is the docs-sync phase, and Phase 140 is the final ACC-walk verification.

### Related Decisions

- 519d1206-4d2a-4500-9046-6db635209996 (ADR): case 1 -- the original decision to redesign `validate` as a non-raising, structured-result tool.
- b399f1ce-ed42-4929-b01c-7a57d18e8014 (ADR): case 2 -- extended the workaround to `set_status`'s invalid-status case via `InvalidStatusResult`.
- 9080b37c-82b3-4f63-81f1-79641d0bf14c (ADR): case 3 -- extended the workaround to `get_<d>`'s parse-failure case via `ParseFailureResult`.
- b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (ADR): case 4 -- the non-raising `ParseFailureResult`/`ValidateResult` branches for the four generic mutation tools (feat-170, GitHub issue #170); its scope statement is what this feature revises.
- (The case-5 ADR for this feature will be recorded here once created in Phase 100.)

### Task List

#### Phase 100: ADR

- [ ] Task 100.100: Draft the case-5 ADR recording this decision, referencing GitHub issue #204, naming the locked scope (12 `create_<d>` + 12 `parse_<d>` tools), the out-of-scope items (`create_adr`, `delete`/`set_feat_id`, `get_<d>`), the reuse-not-new-models design, and updating ADR b8c9bfea's "create/parse keep raising" scope sentence.
- [ ] Task 100.110: Get the ADR to `accepted` status before or alongside the Phase 110/120 code landing, and record its UUID in this README's Related Decisions.
- [ ] Task 100.120: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest, `specmgr adr-toc`), then exactly one Conventional Commit for the phase.

#### Phase 110: `create_<d>` ValidateResult channel (12 domains)

- [ ] Task 110.100: Add the content-validation-failure branch (catch the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple around the `wrap_tool_errors` block; return `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])`; nothing written) to the 11 flat-domain `create_<d>` tools.
- [ ] Task 110.110: Same for `create_feat`, ordered strictly after the id-shape `ValueError` and already-existing-id/folder `FileExistsError` guards (both keep raising) and before any write.
- [ ] Task 110.120: Widen the 12 `create_<d>` tools' return-type union annotations to include `ValidateResult`.
- [ ] Task 110.130: Tests: the per-domain create-failure channel (invalid content -> `ValidateResult(valid=False, ...)`, nothing written), guard-ordering tests (malformed id / already-existing id still raise), happy-path regression tests; convert any existing raise-asserting create tests to the new non-raising shape.
- [ ] Task 110.140: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 120: `parse_<d>` ValidateResult channel (12 domains)

- [ ] Task 120.100: Add the existing-but-broken-file branch to the 12 `parse_<d>` tools (same catch tuple, same `ValidateResult` shape); a truly-absent path keeps raising the domain's not-found error.
- [ ] Task 120.110: Widen the 12 `parse_<d>` tools' return-type union annotations to include `ValidateResult`.
- [ ] Task 120.120: Tests: the per-domain parse-failure channel, the truly-absent-path regression guard (still raises), happy-path regression tests; convert any existing raise-asserting parse tests to the new non-raising shape.
- [ ] Task 120.130: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 130: Docs sync

- [ ] Task 130.100: Update the `@mcp.tool()` description/docstring (`Returns`/`Raises` sections) of all 24 `create_<d>`/`parse_<d>` tools to document the new `ValidateResult` branches.
- [ ] Task 130.110: Update `AGENTS.md` (the `general/` package bullet and the per-domain bullets describing `create_<d>`/`parse_<d>` behavior) and `server.py`'s module docstring.
- [ ] Task 130.120: Regenerate `docs/MCP.md` via `specmgr mcp-docs` (NOT `specmgr docs`), and land the `CHANGELOG.md` `[Unreleased]` entry.
- [ ] Task 130.130: Phase-end gate (including the doc-drift checks), then exactly one Conventional Commit for the phase.

#### Phase 140: Final verification

- [ ] Task 140.100: Walk every ACC-001..006 and confirm each is satisfied with concrete evidence; run the full quality gate end-to-end (ruff format/check, vulture, pytest, `specmgr mcp-docs`/`specmgr adr-toc` drift checks) one last time; update this README's Progress section and set the feature status to `done`.

## Progress

### Current Status

**As of 2026-10-08**: Feature created from GitHub issue #204 via the planning conversation; no implementation started. Phase 100 (ADR) is the next actionable step, starting with Task 100.100.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-08T08:22:11.000Z - Created from planning conversation

Feature drafted from GitHub issue #204 -- case 5 of the ADR 519d1206 non-raising structured-result chain: the 12 `create_<d>` tools and their 12 `parse_<d>` counterparts return the existing non-raising `ValidateResult` on content validation failure instead of a raised `AssertionError`/`pydantic.ValidationError` that MCP clients truncate to a bare tool error. Plan locked in this session: 8 requirements, 6 acceptance criteria, 5 phases (100 ADR, 110 `create_<d>` channel, 120 `parse_<d>` channel, 130 docs sync, 140 final verification).

### More Information

References from GitHub issue #204:

- ADR 519d1206-4d2a-4500-9046-6db635209996 (`validate` as a non-raising structured-result tool).
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (case 4 -- feat-170 / issue #170; its scope statement is what this feature revises).
- feat-27-validation (actionable exception messages -- the content lost to client-side truncation).
- feat-99-list-item (the soft-wrap guard that produced the 2026-10-07 live repro).
- https://github.com/dfch/biz.dfch.SpecMgr/issues/204
