---
classification: null
created: '2026-10-08T11:50:25.678+02:00'
id: feat-204-create-error
status: progress
type: feat
updated: '2026-10-08T14:44:51.000+02:00'
version: 1.0.0
---

# Feature: Non-Raising `ValidateResult` for `create_<d>`/`parse_<d>` on Content Validation Failure (#204)

## Plan

### Overview

GitHub issue #204: the 12 `create_<d>` tools (and their `parse_<d>` counterparts) still surface content validation failures as raised `AssertionError`/`pydantic.ValidationError`. Through an MCP client these are truncated to a bare tool-execution error (e.g. `Error executing tool create_feat`) -- no field path, no line reference, no cause/fix hint -- even though the raised exception message is actionable (feat-27-validation).

The non-raising structured-result chain (ADR 519d1206, extended by ADR b399f1ce -> case 2, ADR 9080b37c -> case 3, ADR b8c9bfea -> case 4) deliberately covered `validate`, `set_status`, `get_<d>`, and the four generic mutation tools (`update`, `edit`, `set_status`, `set_classification`) -- ADR 519d1206's scope statement (quoted and refined by ADR b8c9bfea) explicitly holds that `create_<d>`, ..., `parse_<d>`/`get_<d>` all keep raising, and b8c9bfea in turn recorded the generic `delete` tool's identical Bug-1 defect as "the chain's candidate case 5". This feature is the natural next (case 5) extension of that chain: give the `create_<d>` tools (and `parse_<d>`) the same non-raising `ValidateResult` channel, so an agent calling them gets the actionable message in-band instead of a truncated raise -- taking the case-5 slot for `create_<d>`/`parse_<d>` while `delete` stays raise-based (a later candidate, case 6, if ever addressed).

Observed live dogfooding this repo's own tooling (2026-10-07): `create_feat` called with a body containing a soft-wrapped (multi-physical-line) list item in `## Plan > ### Requirements` (rejected by the feat schema via feat-99's `single_line_text` guard) returned `Error executing tool create_feat` -- no message, no field path, no line, no hint. The workaround cost one extra round-trip per failure: re-run the same content through the generic `validate` tool (`type="feat"`) to get the actionable message, fix, then `create_feat` succeeded.

### Requirements

- REQ-001: Each of the 12 `create_<d>` tools must, on a content validation failure of the caller-submitted content (the `AssertionError`/`pydantic.ValidationError` raised under `wrap_tool_errors`), return the existing non-raising `ValidateResult` (`valid=False`, single `errors[].message` capped at 300 chars exactly as the generic `validate` tool caps it via its own `_MAX_VALIDATE_ERROR_CHARS` constant -- feat-110) and write nothing to disk in that case.
- REQ-002: Each of the 12 `parse_<d>` tools must, for an existing file that fails to parse, return the same non-raising `ValidateResult` channel (its raised message today is equally actionable and equally truncated); a truly-absent or unreadable path must continue to raise the `OSError`-family file-access error from `Path.read_text()` (`FileNotFoundError`/`PermissionError`/`OSError`) unchanged -- the documented file-access contract of every `parse_<d>` -- never intercepted by the new branch.
- REQ-003: Caller-usage errors must keep raising per the `update`/`edit` precedent (feat-170 REQ-004): malformed id shape (`ValueError`), and `create_feat`'s already-existing id/folder (`FileExistsError`); the new non-raising branch must cover only the content-validation-failure channel and must not reorder the pre-dispatch guards. Because the branch wraps the `wrap_tool_errors` content-validation block exactly where it sits today (which for `create_feat` runs before its id-shape and already-existing-id/folder guards -- the existing execution order this feature does not change), a compound failure (invalid content + malformed/already-existing id) surfaces the content error first: the tool returns `ValidateResult` and the guard never runs in that call ("first-in-execution-order wins"); each guard still raises unchanged whenever the content is valid, and the precedence is documented and pinned by test following ADR b8c9bfea case 4's own handling of mode-dependent precedence.
- REQ-004: `create_adr` is out of scope (the ADR domain is excluded from the whole-body chain); `delete` and `set_feat_id` are unaffected -- `delete` takes no caller-submitted content, and although it loads and parses the target document before removal (guaranteeing a valid, parseable document), its current raise on an existing-but-broken document -- the identical Bug-1 defect ADR b8c9bfea item 6(a) records -- remains unchanged; the frontmatter-only success shape of the write tools (feat-69) is unchanged.
- REQ-005: Update the return-type union and the `@mcp.tool()` description/docstring (`Returns`/`Raises` sections) of the 12 `create_<d>` tools and the 12 `parse_<d>` tools to document the new `ValidateResult` branch.
- REQ-006: Write a new ADR recording this decision as case 5 of the non-raising structured-result chain (case 1 = 519d1206/`validate`, case 2 = b399f1ce/`set_status`, case 3 = 9080b37c/`get_<d>`, case 4 = b8c9bfea/the four generic mutation tools), referencing GitHub issue #204. The "create/parse keep raising" scope sentence this feature retires lives in ADR 519d1206's own Decision Outcome (ADR b8c9bfea merely quotes and refines it), and per the chain's established by-reference precedent -- each prior case refined the earlier scope statement in its own new ADR without editing or superseding the accepted predecessor -- the case-5 ADR refines both sentences by reference, with no dated revision or supersession of an accepted ADR. The case-5 ADR must also explicitly address ADR b8c9bfea's forward pointer (its exclusion item 6(a), Consequences, and Confirmation) recording the generic `delete` tool as "the chain's candidate case 5": this feature takes the case-5 slot for `create_<d>`/`parse_<d>`, `delete`'s raise-based Bug-1 contract remains unchanged, and `delete` becomes a later candidate (case 6) if ever addressed.
- REQ-007: Docs sync: `AGENTS.md` (the `general/` package bullet and per-domain bullets describing `create_<d>`/`parse_<d>` behavior), `server.py`'s module docstring, `docs/MCP.md` regeneration via `specmgr mcp-docs`, `docs/api/` + `docs/GENERATED.md` regeneration via `specmgr docs` (the `docs/api/` pages render the very docstrings this feature changes), and a `CHANGELOG.md` `[Unreleased]` entry.
- REQ-008: Add unit test coverage, per domain, for: (a) the create-failure channel (invalid content -> `ValidateResult(valid=False, ...)`, nothing written), (b) the parse-failure channel (existing-but-broken file -> `ValidateResult(valid=False, ...)`) plus the truly-absent-path regression guard (still raises the `OSError`-family file-access error from `Path.read_text()`), (c) guard ordering (caller-usage errors still raise when the content is valid, plus the documented compound-failure precedence), and (d) the happy path (valid content -> frontmatter-only success, unchanged shape).

### Acceptance Criteria

- [ ] ACC-001: (REQ-001/REQ-003) For every one of the 12 `create_<d>` tools, submitting genuinely invalid content returns `ValidateResult(valid=False, errors=[...])` (never raises) with nothing written to disk, while every caller-usage error (malformed id shape, `create_feat`'s already-existing id/folder) still raises exactly as before when the content is valid.
- [ ] ACC-002: (REQ-002) For every one of the 12 `parse_<d>` tools, an existing file that fails to parse returns `ValidateResult(valid=False, errors=[...])` (never raises), while a truly-absent or unreadable path still raises the `OSError`-family file-access error (`FileNotFoundError`/`PermissionError`/`OSError`) from `Path.read_text()` unchanged.
- [ ] ACC-003: (REQ-001/REQ-002) The `errors[].message` of every new branch is `str(exception)` capped at exactly 300 chars via the same `snippet(..., max_chars=_MAX_VALIDATE_ERROR_CHARS)` call the generic `validate` tool makes (feat-110) -- the imported constant, not a literal `300`, so the cap keeps one source of truth -- and the bounded-message contract is not re-opened on the create/parse surface.
- [ ] ACC-004: (REQ-004) `create_adr`, `delete` (including its unchanged raise on an existing-but-broken document), `set_feat_id`, and the generic `validate` tool are behaviorally unchanged; every `create_<d>`/`parse_<d>` success path returns the same frontmatter-only shape as before (feat-69).
- [ ] ACC-005: (REQ-005/REQ-007) The docstrings, `@mcp.tool()` descriptions, `AGENTS.md`, and `server.py`'s module docstring accurately describe the new non-raising branches; `docs/MCP.md` regenerates cleanly via `specmgr mcp-docs` and `docs/api/` + `docs/GENERATED.md` regenerate cleanly via `specmgr docs`, both with no manual edits needed afterward; the `CHANGELOG.md` `[Unreleased]` entry lands.
- [ ] ACC-006: (REQ-006) The new ADR (case 5) exists, is linked from this feature's Related Decisions, is accepted before or alongside the code landing, refines the "create/parse keep raising" scope sentence (ADR 519d1206's own Decision Outcome, quoted by ADR b8c9bfea) by reference per the chain's precedent, and explicitly addresses b8c9bfea's `delete` "candidate case 5" forward pointer (`delete` stays raise-based, a later candidate).
- [ ] ACC-007: (REQ-008) Per-domain unit tests exist and pass for all four sub-cases -- (a) the create-failure channel, (b) the parse-failure channel plus the truly-absent-path regression guard, (c) guard ordering incl. the compound-failure precedence, and (d) the happy path -- and every existing raise-asserting `create_<d>`/`parse_<d>` test is converted to the new non-raising shape.

### Scope

#### Included

- All 12 `create_<d>` tools (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs): the content-validation-failure -> `ValidateResult` branch.
- All 12 `parse_<d>` tools: the existing-but-broken-file -> `ValidateResult` branch.
- Reuse of the existing `ValidateResult`/`ValidationErrorEntry` models and the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple and its `_MAX_VALIDATE_ERROR_CHARS` 300-char message capping -- no new result model, no new helper.
- A new ADR (case 5 of the 519d1206 chain) plus the by-reference refinement of the "create/parse keep raising" scope sentence (ADR 519d1206's own, quoted by ADR b8c9bfea).
- Docstring/description updates on all 24 tools, `AGENTS.md`, `server.py`'s module docstring, `docs/MCP.md` regeneration (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` regeneration (`specmgr docs`).
- A `CHANGELOG.md` `[Unreleased]` entry.
- Test coverage across all 12 domains for both new branches plus the guard-ordering (incl. compound-failure precedence) and happy-path regression guards.

#### Explicitly Out Of Scope

- `create_adr` (and the rest of the ADR domain) -- the ADR domain is excluded from the whole-body non-raising chain; `validate_adr` remains its own standalone tool.
- `delete` and `set_feat_id` -- they take no caller-submitted document content and cannot fail caller-content validation. Deliberately named beyond that half of the rationale: `delete` loads and parses the target document before removal, so an existing-but-broken document currently raises a parse error there -- the identical Bug-1 defect ADR b8c9bfea item 6(a) records as the chain's candidate case 5 -- and that raise behavior remains unchanged by this feature too.
- `get_<d>`'s parse-failure handling -- already solved by ADR 9080b37c/feat-150 via the non-raising `ParseFailureResult` (a different, already-locked channel).
- Changing the generic `validate` tool's behavior or its 300-char error cap (feat-110), or `update`/`edit`'s case-4 branches (feat-170).
- Fixing the underlying, out-of-this-repo's-control MCP client-side `isError: true` truncation defect itself -- this feature is a workaround within this repo's own tool contracts, same as every prior link in the 519d1206 chain.
- Changing the frontmatter-only success return shape of the write tools (feat-69).

### Dependencies

#### Depends On

- ADR 519d1206-4d2a-4500-9046-6db635209996 (case 1: `validate` as a non-raising structured-result tool; its Decision Outcome holds the "create/parse keep raising" scope sentence this feature refines).
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (case 2: `set_status`'s `InvalidStatusResult`).
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (case 3: `get_<d>`'s `ParseFailureResult`).
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (case 4: FEAT feat-170-update-edit-parse-failure/issue #170 -- the four generic mutation tools; it quotes the scope sentence this feature refines and records `delete` as the chain's candidate case 5, which the case-5 ADR addresses).
- FEAT feat-110-truncate-validation-errors (the 300-char capping convention), FEAT feat-27-validation (actionable exception messages -- the content this chain protects), FEAT feat-69-update-context (frontmatter-only success shape).

#### Blocks

- None known.

### Design Notes

**Reuse, not new models.** `ValidateResult`/`ValidationErrorEntry` already exist and are exercised in production by the generic `validate` tool and (since feat-170) by `update`/`edit`. This feature is purely a matter of catching the right exception at the right point in each of the 24 tool functions and returning the existing model -- no new pydantic model, no new MCP result shape.

**Where each branch goes.** `create_<d>`: wrap the `wrap_tool_errors(...)` block that validates the caller-submitted body exactly where it sits today; catch the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple (`AssertionError`, `pydantic.ValidationError`, `yaml.YAMLError` -- the third unreachable for body-only content but kept so the catch shape is uniform); return `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS))])` -- the constant imported from `.validate`, not a literal `300` (the `update.py` case-4 import precedent, one source of truth for the cap). For `create_feat`, the wrapped block is its content-validation call, which in the existing execution order runs *before* the id-shape `ValueError` guard and the already-existing-id/folder `FileExistsError` check (the feature does not reorder that -- REQ-003); consequently a compound failure (invalid content + malformed/already-existing id) returns `ValidateResult` first and the guard never runs in that call -- "first-in-execution-order wins" -- while each guard still raises unchanged whenever the content is valid; the precedence is documented here, in REQ-003, and pinned by test (Task 110.130), following ADR b8c9bfea case 4's own mode-dependent-precedence handling. `parse_<d>`: the same catch around the parse of the existing file; the `OSError`-family file-access errors (`FileNotFoundError`/`PermissionError`/`OSError`) from `Path.read_text()` for a truly-absent/unreadable path are never intercepted.

**Caller-usage errors keep raising.** Per the `update`/`edit` precedent (feat-170 REQ-004), only the structural/field content-validation-failure channel becomes non-raising; no `ValueError` of any kind is caught by the new branches.

**ADR shape.** A new ADR recording case 5 of the chain (consistent with cases 1-4 each having their own ADR). The "keep raising" scope sentence lives in ADR 519d1206's own Decision Outcome (ADR b8c9bfea quotes and refines it in its Option 4); per the chain's established by-reference precedent -- each prior case refined the earlier scope statement in its own new ADR without editing or superseding the accepted predecessor -- the case-5 ADR refines both sentences by reference, with no dated revision or supersession of an accepted ADR. It also explicitly addresses b8c9bfea's forward pointer (exclusion item 6(a), Consequences, Confirmation) recording the generic `delete` tool as "the chain's candidate case 5": this feature takes the case-5 slot for `create_<d>`/`parse_<d>`, `delete` stays raise-based, and it becomes a later candidate (case 6) if ever addressed. The form is finalized in Phase 100 (Task 100.100).

**Phase discipline (standing user requirement, 2026-09-24; the identical text carried by feat-150/feat-167 as instances).** Every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches) and exactly one Conventional Commit; the new/converted tests travel with their code phase (Phase 110/120), Phase 130 is the docs-sync phase, and Phase 140 is the final ACC-walk verification.

### Related Decisions

- ADR 519d1206-4d2a-4500-9046-6db635209996: case 1 -- the original decision to redesign `validate` as a non-raising, structured-result tool; its Decision Outcome holds the "create/parse keep raising" scope sentence this feature refines.
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014: case 2 -- extended the workaround to `set_status`'s invalid-status case via `InvalidStatusResult`.
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c: case 3 -- extended the workaround to `get_<d>`'s parse-failure case via `ParseFailureResult`.
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f: case 4 -- the non-raising `ParseFailureResult`/`ValidateResult` branches for the four generic mutation tools (FEAT feat-170-update-edit-parse-failure, GitHub issue #170); it quotes the scope sentence this feature refines and records `delete` as the chain's candidate case 5, which the case-5 ADR addresses.
- ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e: case 5 -- the non-raising `ValidateResult` branches for the 12 `create_<d>` tools and 12 `parse_<d>` tools (this feature, GitHub issue #204); refines the 'create/parse keep raising' scope sentence of ADR 519d1206 by reference and resolves ADR b8c9bfea's `delete` 'candidate case 5' forward pointer (`delete` stays raise-based, a later candidate).

### Task List

#### Phase 100: ADR

- [x] Task 100.100: Draft the case-5 ADR recording this decision, referencing GitHub issue #204, naming the locked scope (12 `create_<d>` + 12 `parse_<d>` tools), the out-of-scope items (`create_adr`, `delete`/`set_feat_id` -- incl. `delete`'s unchanged raise on an existing-but-broken document, `get_<d>`), the reuse-not-new-models design, refining the "create/parse keep raising" scope sentence (ADR 519d1206's own Decision Outcome, quoted by ADR b8c9bfea) by reference per the chain's precedent, and explicitly addressing b8c9bfea's `delete` "candidate case 5" forward pointer (this feature takes the case-5 slot; `delete` stays raise-based, a later candidate).
- [x] Task 100.110: Get the ADR to `accepted` status before or alongside the Phase 110/120 code landing, and record its UUID in this README's Related Decisions.
- [x] Task 100.120: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest, `specmgr adr-toc`), then exactly one Conventional Commit for the phase.

#### Phase 110: `create_<d>` ValidateResult channel (12 domains)

- [ ] Task 110.100: Add the content-validation-failure branch (catch the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple around the `wrap_tool_errors` block; return `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS))])` -- the constant imported from `.validate`, not a literal `300`; nothing written) to the 11 flat-domain `create_<d>` tools.
- [ ] Task 110.110: Same for `create_feat`, wrapping its existing content-validation block in place -- the current execution order (content validation before the id-shape `ValueError` and already-existing-id/folder `FileExistsError` guards, both of which keep raising per REQ-003) is not reordered, so a compound failure (invalid content + malformed/already-existing id) returns `ValidateResult` first ("first-in-execution-order wins"); document that precedence in the tool's docstring per the design note.
- [ ] Task 110.120: Widen the 12 `create_<d>` tools' return-type union annotations to include `ValidateResult`.
- [ ] Task 110.130: Tests: the per-domain create-failure channel (invalid content -> `ValidateResult(valid=False, ...)`, nothing written), guard tests (malformed id / already-existing id still raise when the content is valid), compound-failure precedence tests for `create_feat` (invalid content + already-existing id => `ValidateResult`, not `FileExistsError`; invalid content + malformed id => `ValidateResult`, not `ValueError`), happy-path regression tests; convert any existing raise-asserting create tests to the new non-raising shape.
- [ ] Task 110.140: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 120: `parse_<d>` ValidateResult channel (12 domains)

- [ ] Task 120.100: Add the existing-but-broken-file branch to the 12 `parse_<d>` tools (same catch tuple, same `ValidateResult` shape); a truly-absent/unreadable path keeps raising the `OSError`-family file-access error from `Path.read_text()` (`FileNotFoundError`/`PermissionError`/`OSError`) unchanged.
- [ ] Task 120.110: Widen the 12 `parse_<d>` tools' return-type union annotations to include `ValidateResult`.
- [ ] Task 120.120: Tests: the per-domain parse-failure channel, the truly-absent-path regression guard (still raises `FileNotFoundError`/`OSError` -- the documented file-access contract, never a not-found error), happy-path regression tests; convert any existing raise-asserting parse tests to the new non-raising shape.
- [ ] Task 120.130: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 130: Docs sync

- [ ] Task 130.100: Update the `@mcp.tool()` description/docstring (`Returns`/`Raises` sections) of all 24 `create_<d>`/`parse_<d>` tools to document the new `ValidateResult` branches.
- [ ] Task 130.110: Update `AGENTS.md` (the `general/` package bullet and the per-domain bullets describing `create_<d>`/`parse_<d>` behavior) and `server.py`'s module docstring.
- [ ] Task 130.120: Regenerate `docs/MCP.md` via `specmgr mcp-docs` and `docs/api/` + `docs/GENERATED.md` via `specmgr docs` (the `docs/api/` pages render the very docstrings Task 130.100 changes, so both regenerations are needed or the drift check at 130.130 fails), and land the `CHANGELOG.md` `[Unreleased]` entry.
- [ ] Task 130.130: Phase-end gate (including the doc-drift checks), then exactly one Conventional Commit for the phase.

#### Phase 140: Final verification

- [ ] Task 140.100: Walk every ACC-001..007 and confirm each is satisfied with concrete evidence; run the full quality gate end-to-end (ruff format/check, vulture, pytest, `specmgr mcp-docs`/`specmgr docs`/`specmgr adr-toc` drift checks) one last time; update this README's Progress section and set the feature status to `done`.

## Progress

### Current Status

**As of 2026-10-08**: Phase 100 (ADR) complete -- case-5 ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e drafted through the specmgr MCP structured tools, validated, and `accepted` ahead of the Phase 110/120 code landing (Tasks 100.100/100.110); its UUID recorded in Related Decisions; phase-end quality gate green (Task 100.120 -- the Conventional Commit itself is the orchestrator's). Phase 110 (`create_<d>` ValidateResult channel, 12 domains) is next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-08T14:44:51.000+02:00 - Phase 100 (ADR) complete

Case-5 ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e ("Extend the non-raising structured-result workaround to the create_<d>/parse_<d> content-validation cases") drafted through the specmgr MCP `create_adr` structured tool (per ADR 898bfcd0's authoring mandate -- no hand-written markdown), validated via `validate_adr`, and set to `accepted` via the generic `set_status` tool (`type="adr"`) ahead of the Phase 110/120 code landing. The ADR records GitHub issue #204 (incl. the 2026-10-07 live `create_feat` dogfooding repro: soft-wrapped list item -> the bare `Error executing tool create_feat`), the locked scope (the 12 `create_<d>` tools' content-validation-failure branch and the 12 `parse_<d>` tools' existing-but-broken-file branch, `parse_<d>`'s `OSError`-family file-access contract never intercepted), all out-of-scope items (`create_adr`/the ADR domain, `delete`/`set_feat_id` incl. `delete`'s unchanged raise on an existing-but-broken document, `get_<d>`, the generic `validate` tool's own behavior/cap, `update`/`edit`'s case-4 branches, the client-side `isError` truncation defect itself), the reuse-not-new-models design (`ValidateResult`/`ValidationErrorEntry` plus the `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple and `_MAX_VALIDATE_ERROR_CHARS` constant imported from `general/tools/validate.py` per the case-4 `update.py`/`edit.py` import precedent), and the `create_feat` execution-order subtlety (content validation runs before its id-shape `ValueError` guard and its `FileExistsError` check -- not re-ordered; a compound failure returns `ValidateResult` first, "first-in-execution-order wins", documented per REQ-003 and pinned by test per ADR b8c9bfea item 4's precedent). Per the chain's by-reference precedent, the ADR refines the "create/parse keep raising" scope sentence of ADR 519d1206's own Decision Outcome by reference (accepted predecessors left unedited; no supersession, no dated revision) and explicitly resolves ADR b8c9bfea's `delete` "candidate case 5" forward pointer: feat-204 takes the case-5 slot for `create_<d>`/`parse_<d>`, `delete`'s raise-based Bug-1 contract stays unchanged, and `delete` becomes a later candidate (case 6) if ever addressed. Applied to this README: Related Decisions placeholder replaced with the tag-first ADR entry; Tasks 100.100/100.110/100.120 marked done in place; frontmatter `status` moved `planning` -> `progress`. Phase-end gate: full quality gate green (ruff format/check, vulture, pytest ~4414 passed/16 skipped, `specmgr adr-toc` -- the regenerated TOC picking up the new ADR is expected drift that travels with the orchestrator's single phase commit).

#### 2026-10-08T13:08:11.717+02:00 - Plan refined (feat-refiner pass)

Refinement pass over the plan and its reference graph (13 nodes visited, all tag-form references resolved, zero unresolved; one harmless `b8c9bfea`<->`19ff316b` citation cycle). Applied to this README: E1 -- compound-failure precedence resolved by option (a): the `create_feat` execution order (content validation before its id-shape/`FileExistsError` guards) is kept, "first-in-execution-order wins" is documented and pinned by test per the ADR b8c9bfea case-4 precedent; G1 -- the case-5 ADR must address b8c9bfea's `delete` "candidate case 5" forward pointer; G2 -- new ACC-007 restores REQ-008 -> ACC traceability; G3 -- `specmgr docs` regeneration added to Phase 130 (`docs/api/` renders the changed docstrings); D1 -- `parse_<d>`'s absent-path contract reworded to the `OSError`-family file-access error from `Path.read_text()` (never a not-found error); D2 -- the "keep raising" sentence attributed to ADR 519d1206's own Decision Outcome (b8c9bfea quotes it), refined by reference per the chain's precedent, no supersession of an accepted ADR; D3 -- `delete`'s unchanged broken-document raise named in REQ-004/out-of-scope/ACC-004; D4 -- phase-discipline authority restated as the standing user requirement with feat-150/feat-167 as instances; I1 -- `_MAX_VALIDATE_ERROR_CHARS` constant instead of a literal `300`; I2 -- compound-failure precedence tests in Task 110.130; I3 -- Related Decisions rewritten tag-first (`ADR <uuid>`); I4 -- prose feat references tagged `FEAT`. Positives P1-P4 noted, no action.

#### 2026-10-08T08:22:11.000Z - Created from planning conversation

Feature drafted from GitHub issue #204 -- case 5 of the ADR 519d1206 non-raising structured-result chain: the 12 `create_<d>` tools and their 12 `parse_<d>` counterparts return the existing non-raising `ValidateResult` on content validation failure instead of a raised `AssertionError`/`pydantic.ValidationError` that MCP clients truncate to a bare tool error. Plan locked in this session: 8 requirements, 6 acceptance criteria, 5 phases (100 ADR, 110 `create_<d>` channel, 120 `parse_<d>` channel, 130 docs sync, 140 final verification).

### More Information

References from GitHub issue #204:

- ADR 519d1206-4d2a-4500-9046-6db635209996 (`validate` as a non-raising structured-result tool).
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (case 4 -- FEAT feat-170-update-edit-parse-failure / issue #170; it quotes the scope sentence this feature refines and records `delete` as the chain's candidate case 5, which the case-5 ADR addresses).
- FEAT feat-27-validation (actionable exception messages -- the content lost to client-side truncation).
- FEAT feat-99-list-item (the soft-wrap guard that produced the 2026-10-07 live repro).
- https://github.com/dfch/biz.dfch.SpecMgr/issues/204
