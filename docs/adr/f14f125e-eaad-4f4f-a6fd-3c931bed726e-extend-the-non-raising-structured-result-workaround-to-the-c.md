---
status: accepted
date: '2026-10-08'
decision-makers: OpenCode agent + user decision
id: f14f125e-eaad-4f4f-a6fd-3c931bed726e
version: 1.0.0
---

# Extend the non-raising structured-result workaround to the create_<d>/parse_<d> content-validation cases

## Context and Problem Statement

GitHub issue #204 (https://github.com/dfch/biz.dfch.SpecMgr/issues/204) reports that the 12 `create_<d>` tools and their 12 `parse_<d>` counterparts still surface content-validation failures as raised `AssertionError`/`pydantic.ValidationError`. Through an MCP client such as OpenCode 1.18.27 those raises are truncated to a bare tool-execution error (e.g. `Error executing tool create_feat`) -- no field path, no line reference, no cause/fix hint -- even though the raised exception messages are actionable: feat-27-validation already invested in exactly that enrichment, and the generic `validate` tool already delivers it in-band via its non-raising `{valid, errors}` result (ADR 519d1206-4d2a-4500-9046-6db635209996, case 1 of the chain). Live dogfooding of this repo's own tooling on 2026-10-07 reproduced the dead-end: `create_feat` called with a body containing a soft-wrapped (multi-physical-line) list item in `## Plan > ### Requirements` -- rejected by the feat schema via feat-99-list-item's `single_line_text` guard -- returned the bare `Error executing tool create_feat`. The workaround cost one extra round-trip per failure: re-run the same content through the generic `validate` tool (`type="feat"`) to get the actionable message, fix the content, then call `create_feat` again, where it succeeded.

This is the fifth case in the ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain (client-side `isError: true` result truncation, confirmed on OpenCode 1.18.27): case 1 redesigned the generic `validate` tool to a non-raising `{valid, errors}` result; case 2 (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) extended that rationale narrowly to `set_status`'s invalid-status case, via `InvalidStatusResult`; case 3 (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c) extended it to `get_<d>`'s parse-failure case, via `ParseFailureResult`; case 4 (ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f) extended it to the four generic mutation tools' failure cases, via `ParseFailureResult`/`ValidateResult`. Each case retired the earlier case's scope sentence by reference, without editing or superseding the accepted predecessor.

519d1206's own Decision Outcome carries the scope sentence this feature retires: it held that "`create_<d>`, `update`, `set_status`, `set_classification`, `delete`, `parse_<d>`/`get_<d>` all keep raising" -- a sentence case 4's own ADR (b8c9bfea) quoted and refined in its Decision Outcome as the chain advanced. After cases 2-4, only the `create_<d>`, `delete`, and `parse_<d>` surfaces of that sentence remained live (`get_<d>` having been retired by case 3, `update`/`set_status`/`set_classification` by cases 2/4). This ADR retires the `create_<d>` and `parse_<d>` halves, leaving `delete` (plus `create_adr`, which was never part of the whole-body surface) as the sentence's remaining raise-based surfaces.

One further record this ADR must settle: case 4 (b8c9bfea) explicitly noted -- in its exclusion item 6(a), its Consequences, and its Confirmation -- that the generic `delete` tool carries the identical Bug-1 defect (raise on an existing-but-broken document) and is "recorded here as the chain's candidate case 5, not bundled into this feature." GitHub issue #204's `create_<d>`/`parse_<d>` dead-end outranks that candidate: it is the caller-submitted-content surface, exercised on every document creation and on every `parse_<d>` read, and it was reproduced live against this repo's own tooling. This ADR takes the case-5 slot for `create_<d>`/`parse_<d>`; `delete`'s raise-based Bug-1 contract remains unchanged by this ADR and becomes a later candidate (case 6) if ever addressed. No accepted ADR is edited or superseded: 519d1206 and b8c9bfea remain byte-identical, refined by reference only, per the chain's established precedent.

This ADR decides whether and how to extend the chain to case 5 -- the `create_<d>` content-validation-failure case and the `parse_<d>` existing-but-broken-file case, across all 12 whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) -- and records the concrete design FEAT feat-204-create-error's Phases 110/120 implement from.

## Decision Drivers

- Deliver the actionable content-validation failure detail (field path, line, cause/fix hint) for the `create_<d>`/`parse_<d>` surface host-independently, the same way 519d1206/b399f1ce/9080b37c/b8c9bfea did for `validate`, `set_status`, `get_<d>`, and the four generic mutation tools -- the 2026-10-07 live repro of issue #204 is exactly the reported case, and the truncated bare tool error is an operational dead-end.
- Reuse, not new models: the existing `ValidateResult`/`ValidationErrorEntry` (`general/models`), already exercised in production by `validate` and (since FEAT feat-170-update-edit-parse-failure) by `update`/`edit`; the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple (`AssertionError`, `pydantic.ValidationError`, `yaml.YAMLError` -- the third unreachable for body-only content, which never parses a frontmatter block, but kept so the catch shape is uniform) and `_MAX_VALIDATE_ERROR_CHARS` constant, both imported from `general/tools/validate.py` exactly as `general/tools/update.py` and `general/tools/edit.py` already do (the case-4 import precedent) -- no new result model, no new helper, one source of truth for the 300-char cap (feat-110).
- Zero change to the successful-path wire shape: the MCP SDK serializes results with `model_dump(..., exclude_none=True)`, so a new union member that only materializes on the failure path adds nothing to a healthy tool result (the 9080b37c/b8c9bfea driver).
- Keep every caller-usage error raising per the `update`/`edit` precedent (feat-170 REQ-004): no `ValueError` of any kind is caught by the new branches, and `create_feat`'s already-existing-id/folder `FileExistsError` is unchanged.
- Keep `parse_<d>`'s documented file-access contract: a truly-absent or unreadable path must continue to raise the `OSError`-family file-access error from `Path.read_text()` (`FileNotFoundError`/`PermissionError`/`OSError`) -- never intercepted.
- Do not reorder the tools' execution: `create_feat`'s existing order -- content validation before its id-shape `ValueError` guard and its already-existing-id/folder `FileExistsError` check -- is preserved, and the resulting compound-failure precedence is documented and pinned by test rather than removed by a re-order on the common path (the b8c9bfea item-4 precedent for mode-dependent precedence).
- Keep the scope narrow and explicit: `create_adr` and the ADR domain, `delete`/`set_feat_id`, `get_<d>` (already the non-raising `ParseFailureResult`, 9080b37c), the generic `validate` tool's own behavior and its 300-char cap (feat-110), `update`/`edit`'s case-4 branches (feat-170), and the client-side `isError: true` truncation defect itself (workaround only, as every prior chain link) all remain unchanged.

## Considered Options

- Option 1: Do nothing -- keep all 24 `create_<d>`/`parse_<d>` tools raise-based, relying on feat-27-validation's already-actionable-but-client-truncated exception messages.
- Option 2: Enrich the raised exception messages further (create/parse-specific framing) and/or lift the 300-char cap on the `create_<d>`/`parse_<d>` surface.
- Option 3: Introduce a new, purpose-built result model for `create_<d>`/`parse_<d>` failure (e.g. carrying the proposed id or target path alongside the capped message).
- Option 4 (chosen): Narrowly extend the non-raising, structured-result chain to case 5 -- the `create_<d>`/`parse_<d>` content-validation cases across all 12 whole-body domains -- reusing `ValidateResult` and the `validate` tool's own catch tuple and cap constant; reclassify `delete`'s candidate case-5 slot as a later candidate (case 6); no accepted ADR edited or superseded.

## Decision Outcome

Option 4: each of the 12 `create_<d>` tools (`create_req`, `create_uc`, `create_tsk`, `create_qa`, `create_prb`, `create_gol`, `create_rsk`, `create_dec`, `create_sop`, `create_feat`, `create_vcr`, `create_sysrs`) gets a narrow, non-raising branch on a content-validation failure of the caller-submitted body: the `AssertionError`/`pydantic.ValidationError` raised under the tool's existing `wrap_tool_errors(...)` block is caught, and the tool returns the existing `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS))])` in place of the exception, writing nothing to disk. Each of the 12 `parse_<d>` tools gets the same branch on the parse of an existing file that fails to parse; a truly-absent or unreadable path keeps raising the `OSError`-family file-access error from `Path.read_text()` unchanged. This ADR refines, by reference, 519d1206's own Decision Outcome scope sentence -- which held that "`create_<d>`, `update`, `set_status`, `set_classification`, `delete`, `parse_<d>`/`get_<d>` all keep raising" (quoted and refined by case 4's own ADR, b8c9bfea): after this ADR, the `create_<d>` and `parse_<d>` halves of that sentence are retired, and only `delete` (plus `create_adr`, which was never part of the whole-body surface) remains raise-based among the surfaces it named. Per the chain's established by-reference precedent -- each prior case retired the earlier case's scope sentence in its own new ADR without editing or superseding the accepted predecessor -- the accepted predecessors (519d1206, b399f1ce, 9080b37c, b8c9bfea) are left unedited, and no supersession or dated revision of an accepted ADR is recorded.

It also explicitly resolves ADR b8c9bfea's forward pointer: b8c9bfea recorded the generic `delete` tool's identical Bug-1 defect (raise on an existing-but-broken document) in its exclusion item 6(a), its Consequences, and its Confirmation as "the chain's candidate case 5." This ADR takes the case-5 slot for `create_<d>`/`parse_<d>` -- the surface GitHub issue #204 reports, reproduced live against this repo's own tooling on 2026-10-07; `delete`'s raise-based Bug-1 contract remains unchanged by this ADR; and `delete` becomes a later candidate (case 6) if ever addressed. b8c9bfea itself is not edited.

The concrete mechanism (implemented in FEAT feat-204-create-error's Phases 110/120):

1. `create_<d>` branch (all 12 tools): wrap the existing `with wrap_tool_errors(domain=<d>, tool="create_<d>", channel=BODY_CHANNEL):` content-validation block in place, exactly where it sits today; catch `_CAUGHT_EXCEPTIONS` -- the generic `validate` tool's own tuple (`AssertionError`, `pydantic.ValidationError`, `yaml.YAMLError`; the third unreachable for body-only content, which never parses a frontmatter block, but kept so the catch shape is uniform across the surface, per b8c9bfea's item-3 precedent) -- imported from `general/tools/validate.py` together with `_MAX_VALIDATE_ERROR_CHARS`, exactly as `general/tools/update.py` and `general/tools/edit.py` already do (the case-4 import precedent, one source of truth for the cap); return `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS))])`, mirroring `validate` exactly including feat-110's 300-char cap, so the bounded-message contract the chain has kept since feat-110 is not re-opened on the create/parse surface. Nothing is written to disk on that path.

2. `parse_<d>` branch (all 12 tools): the same catch around the existing-file parse (`with wrap_tool_errors(domain=<d>, tool="parse_<d>"): return _parse_<d>(text)`); the `OSError`-family file-access errors (`FileNotFoundError`/`PermissionError`/`OSError`) raised by `Path(path).read_text(...)` for a truly-absent or unreadable path are never intercepted -- that documented file-access contract is the only remaining raise on the `parse_<d>` surface, unchanged.

3. The `create_feat` execution-order subtlety (intentional, FEAT feat-204-create-error REQ-003): in the existing execution order, `create_feat`'s content validation runs BEFORE its id-shape `ValueError` guard (`assert_feat_id`) and its already-existing-id/folder `FileExistsError` check; this feature does NOT reorder that. Consequence: a compound failure (invalid content + a malformed or already-existing id) returns `ValidateResult(valid=False, ...)` first and the guard never runs in that call -- "first-in-execution-order wins." Each guard still raises unchanged whenever the content is valid (malformed id shape -> `ValueError`; valid content + already-existing id/folder -> `FileExistsError`). The precedence is documented in the feature plan (REQ-003) and pinned by test (Task 110.130), following ADR b8c9bfea case 4's own mode-dependent-precedence handling (its item 4).

4. Caller-usage errors keep raising per the `update`/`edit` precedent (feat-170 REQ-004): no `ValueError` of any kind is caught by the new branches, and `create_feat`'s `FileExistsError` (valid content + already-existing id/folder) is unchanged; the new branches cover only the content-validation-failure channel.

5. Return-type unions: every `create_<d>` widens from its bare `<d>Frontmatter` to `<d>Frontmatter | ValidateResult`; every `parse_<d>` from its bare `<d>Document` to `<d>Document | ValidateResult`. Every success path keeps its current shape byte-identical -- the frontmatter-only write-tool success shape (feat-69-update-context) is unchanged, and the SDK's `exclude_none` means the new union members only materialize on the failure paths (the 9080b37c/b8c9bfea driver).

6. Exclusions, recorded for the chain's auditability: (a) `create_adr` and the rest of the ADR domain stay fully out -- the ADR domain is not a whole-body domain and has no `validate`-adjacent generic surface; `validate_adr` remains its own standalone tool. (b) `delete` and `set_feat_id` are unaffected: `delete` takes no caller-submitted content, and its raise on an existing-but-broken document -- the identical Bug-1 defect b8c9bfea's item 6(a) records -- remains unchanged (a later candidate, case 6); `set_feat_id` is a rename operation with no content-validation channel. (c) `get_<d>`'s parse-failure handling is unchanged -- already the non-raising `ParseFailureResult` via ADR 9080b37c, a different, already-locked channel. (d) The generic `validate` tool's own behavior and its 300-char cap (feat-110), and `update`/`edit`'s case-4 branches (feat-170), are unchanged. (e) The client-side `isError: true` truncation defect itself is NOT fixed -- this is a workaround within this repo's own tool contracts, same as every prior link in the chain.

### Consequences

- Good: the actionable content-validation failure now reaches the calling agent host-independently for 24 tools x 12 domains -- an invalid caller-submitted body on `create_<d>` and an existing-but-broken file on `parse_<d>` each return `ValidateResult(valid=False)` with the 300-char-capped cause (field path, line, cause/fix hint per feat-27-validation) as a successful (`isError: false`) structured result, the exact channel 519d1206's wire-level proof showed the client preserves -- closing issue #204's reported dead-end and the 2026-10-07 live repro (a soft-wrapped list item on `create_feat` -> the bare `Error executing tool create_feat`).
- Good: no new model, no new helper, no new MCP result shape -- `ValidateResult`/`ValidationErrorEntry` are already exercised in production by `validate` and (since feat-170) by `update`/`edit`, and the branches reuse the `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple and `_MAX_VALIDATE_ERROR_CHARS` constant imported from `general/tools/validate.py` (the case-4 import precedent of `update.py`/`edit.py`), keeping the 300-char cap at one source of truth.
- Good: zero change to the successful-path wire shape (the SDK's `exclude_none` means the new union members only materialize on the failure paths); the frontmatter-only write-tool success shape (feat-69) is unchanged; `parse_<d>`'s `OSError`-family file-access contract and every caller-usage-error contract (malformed id shape `ValueError`, `create_feat`'s `FileExistsError`) stay unchanged.
- Good: ADR b8c9bfea's "candidate case 5" forward pointer is explicitly resolved -- the case-5 slot is taken by `create_<d>`/`parse_<d>`, `delete` stays raise-based as a later candidate (case 6), and no accepted ADR is edited or superseded (519d1206 and b8c9bfea remain byte-identical, refined by reference only).
- Bad: this is the fifth documented asymmetric tool contract in this repo (519d1206's `validate`, b399f1ce's `set_status`, 9080b37c's `get_<d>`, b8c9bfea's four generic mutation tools, now `create_<d>`/`parse_<d>`) -- a future contributor must know the chain rather than assume a single universal error-reporting convention across the whole tool surface.
- Bad: the return unions widen across 24 tools (every `create_<d>` to `<d>Frontmatter | ValidateResult`, every `parse_<d>` to `<d>Document | ValidateResult`) -- a caller must check for the new failure shape on every non-exception return.
- Bad: the `create_feat` compound-failure precedence (invalid content + malformed/already-existing id -> `ValidateResult`, the guard never runs in that call) is a deliberate asymmetry that must be documented and pinned by test, per b8c9bfea item 4's precedent.
- Bad: the generic `delete` tool's identical Bug-1 defect (raise on an existing-but-broken document) remains raise-based (now the chain's candidate case 6).
- Bad (tracked, not blocking): as with 519d1206/b399f1ce/9080b37c/b8c9bfea, a live MCP-client round-trip cannot be automated; verification is unit-level only. The workaround remains harmless and correct if/when a client fixes its `isError: true` handling.

### Confirmation

To be confirmed during FEAT feat-204-create-error's Phases 110/120 at the unit level (direct Python calls through the tools' own test modules, mirroring the confirmations 519d1206/b399f1ce/9080b37c/b8c9bfea record), per tool x domain: (a) the create-failure channel -- submitting genuinely invalid content returns `ValidateResult(valid=False, errors=[...])` (never raises), its `errors[].message` capped at 300 chars via the imported `_MAX_VALIDATE_ERROR_CHARS`, and nothing is written to disk; (b) the parse-failure channel -- an existing file that fails to parse returns `ValidateResult(valid=False, errors=[...])` (never raises), while a truly-absent or unreadable path still raises the `OSError`-family file-access error from `Path.read_text()` unchanged (regression guard); (c) guard ordering -- every caller-usage error (malformed id shape, `create_feat`'s already-existing id/folder) still raises exactly as before when the content is valid, plus the documented `create_feat` compound-failure precedence (invalid content + malformed/already-existing id -> `ValidateResult`, not `ValueError`/`FileExistsError`); and (d) the happy path -- valid content returns the same frontmatter-only success shape as before (feat-69), unchanged. As with the four prior ADRs, no live MCP-client/OpenCode-session round-trip is attempted or recorded as an outstanding commitment, for the same automation-limitation reasons they document.

## Pros and Cons of the Options

### Option 1: Do nothing -- keep all 24 `create_<d>`/`parse_<d>` tools raise-based

#### Pros

- No new work, no return-union widening, no fifth asymmetric tool contract to document or maintain beyond the four 519d1206/b399f1ce/9080b37c/b8c9bfea already introduced.
- Matches the remaining write/id-resolving tools' (`delete`, `create_adr`, `set_feat_id`) raise-based convention.

#### Cons

- Known to fail on at least one real, current, widely-used MCP client (OpenCode 1.18.27) for exactly the same reason the chain fixed four times: the 2026-10-07 live repro (a soft-wrapped list item on `create_feat` -> the bare `Error executing tool create_feat`) is the documented case, and the `parse_<d>` surface has the identical dead-end for existing-but-broken files.
- Leaves the documented workaround -- re-running the same content through the generic `validate` tool to get the actionable message -- as the only in-band recovery: one extra round-trip per failure, for every caller, for the exact class of error `validate` already made non-raising.

### Option 2: Enrich the raised exception messages / lift the cap on the `create_<d>`/`parse_<d>` surface

#### Pros

- A smaller, message-only change: benefits every consumer of the raised exception (e.g. direct Python callers), not just MCP clients.
- Could carry create/parse-specific framing (the proposed id on `create_feat`, the target path on `parse_<d>`) in the exception text.

#### Cons

- Still rides the lossy `isError: true` channel: 519d1206's wire-level proof showed the client truncates any raised exception to a bare "Error executing tool ..." -- enriching the message does not sidestep the truncation; only a successful (`isError: false`) structured result does.
- Lifting the 300-char cap on the create/parse surface would re-open the bounded-message contract the chain has kept since feat-110 across four cases.

### Option 3: Introduce a new, purpose-built result model for `create_<d>`/`parse_<d>` failure

#### Pros

- Could carry create/parse-specific context (the proposed id on `create_feat`, the target path on `parse_<d>`) alongside the capped message.
- Would make the failure channel self-describing per tool family, without callers inferring which surface failed from the shared `ValidateResult` shape.

#### Cons

- A new pydantic model and a new MCP result shape where the existing `ValidateResult`/`ValidationErrorEntry` already carry exactly the fields the defect needs -- issue #204 is about message *delivery*, not result typing.
- Widens the set of failure shapes a caller must handle across the chain (a fifth distinct model alongside `ValidateResult`, `InvalidStatusResult`, `ParseFailureResult`) with no user-visible benefit over reusing `ValidateResult`.

### Option 4: Narrowly extend the chain to case 5 -- the `create_<d>`/`parse_<d>` content-validation cases (chosen)

#### Pros

- Directly fixes issue #204's reported dead-end for 24 tools x 12 domains, using a rationale and pattern already proven four times (519d1206, b399f1ce, 9080b37c, b8c9bfea).
- Fully within this repo's own control; immediately effective without waiting on a third-party client fix.
- No new model, no new helper: reuses `ValidateResult`/`ValidationErrorEntry` already exercised in production, and the `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple and `_MAX_VALIDATE_ERROR_CHARS` constant imported from `general/tools/validate.py` (the case-4 import precedent of `update.py`/`edit.py`).
- Zero change to the successful-path wire shape -- the SDK's `exclude_none` means the new union members only materialize on the failure paths.
- Keeps every other contract unchanged: the caller-usage `ValueError`s, `create_feat`'s `FileExistsError`, `parse_<d>`'s `OSError`-family file-access errors, `delete`'s Bug-1 raise, the frontmatter-only success shape (feat-69), and `create_feat`'s existing execution order (not re-ordered).
- Explicitly resolves b8c9bfea's forward pointer: this feature takes the case-5 slot, `delete` becomes a later candidate (case 6), and no accepted ADR is edited or superseded.

#### Cons

- Introduces a fifth documented asymmetric tool contract -- a future contributor must know the chain.
- Widens the return unions across 24 tools (every `create_<d>` to `<d>Frontmatter | ValidateResult`, every `parse_<d>` to `<d>Document | ValidateResult`).
- The `create_feat` compound-failure precedence (invalid content + malformed/already-existing id -> `ValidateResult`) is a deliberate asymmetry that must be documented and pinned by test.
- The generic `delete` tool's identical Bug-1 defect stays raise-based (now recorded as the chain's candidate case 6).
- Same tracked-but-unresolved limitation as 519d1206/b399f1ce/9080b37c/b8c9bfea: no live MCP-client round-trip can be automated; verification stays unit-level.

## More Information

- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation"): case 1 of the chain; its own Decision Outcome carries the "`create_<d>`, `update`, `set_status`, `set_classification`, `delete`, `parse_<d>`/`get_<d>` all keep raising" scope sentence this ADR refines by reference; its Context/Consequences/Confirmation carry the full original investigation this ADR does not repeat.
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 ("Extend the non-raising structured-result workaround to set_status's invalid-status case"): case 2; the `InvalidStatusResult` precedent and the narrow-extension driver this ADR follows.
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c ("Extend the non-raising structured-result workaround to get_<d>'s parse-failure case"): case 3; the `ParseFailureResult` channel `get_<d>` already uses -- a different, already-locked channel this ADR leaves unchanged.
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f ("Extend the non-raising structured-result workaround to the generic mutation tools' failure cases"): case 4; it quotes the scope sentence this ADR refines and records the generic `delete` tool as "the chain's candidate case 5" (exclusion item 6(a), Consequences, Confirmation) -- the forward pointer this ADR resolves (the case-5 slot goes to `create_<d>`/`parse_<d>`; `delete` becomes a later candidate, case 6); b8c9bfea remains unedited.
- ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 ("Author and edit ADRs only through MCP structured tools, never raw markdown"): the authoring mandate this ADR itself follows -- created and status-changed only through the specmgr MCP `create_adr`/`set_status` structured tools, never hand-written or hand-edited.
- Feature plan and progress: `.specmgr/feat/feat-204-create-error/README.md` (Phases 110/120 implement the mechanism this ADR records; Phase 130 syncs the docs surface; Phase 140 walks the acceptance criteria).
- GitHub issue #204: https://github.com/dfch/biz.dfch.SpecMgr/issues/204 (including the 2026-10-07 live dogfooding repro: `create_feat` with a soft-wrapped list item -> the bare `Error executing tool create_feat`).
- FEAT feat-27-validation (actionable exception messages -- the content this chain protects), FEAT feat-110-truncate-validation-errors (the 300-char capping convention), FEAT feat-69-update-context (the frontmatter-only write-tool success shape), FEAT feat-170-update-edit-parse-failure (case 4 -- the `update.py`/`edit.py` import precedent for `_CAUGHT_EXCEPTIONS`/`_MAX_VALIDATE_ERROR_CHARS` and the caller-usage-keeps-raising contract), FEAT feat-99-list-item (the soft-wrap `single_line_text` guard that produced the 2026-10-07 live repro).
