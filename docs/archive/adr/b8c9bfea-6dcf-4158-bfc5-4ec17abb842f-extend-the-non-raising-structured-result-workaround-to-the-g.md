---
status: accepted
date: '2026-09-30'
decision-makers: OpenCode agent + user decision
id: b8c9bfea-6dcf-4158-bfc5-4ec17abb842f
version: 1.0.0
---

# Extend the non-raising structured-result workaround to the generic mutation tools' failure cases

## Context and Problem Statement

GitHub issue #170 (https://github.com/dfch/biz.dfch.SpecMgr/issues/170) reports that the generic `update` and `edit` tools (reported for `type="dec"`, but structurally affecting every whole-body domain) crash with a bare, undifferentiated tool-execution error in two related situations, and that nothing is ever written to disk in either. Root-cause investigation during triage found two distinct, already-partially-addressed defects colliding in the reporter's test corpus (every `dec` document there happened to be broken):

**Bug 1 (all four generic mutation tools -- `update`, `edit`, `set_status`, `set_classification`)**: every per-domain adapter's first step under the domain lock is `load_<d>_by_id()`, which resolves via `general.tools._doc_paths.find_doc_path_by_id` -- the shared id-to-path scan that silently skips any file that fails to parse (by design, so one broken file never blocks lookup of a different id). So when the *target* id's only matching file is itself broken, the scan raises the domain's raw `XNotFoundError` -- an already-documented, intentional limitation (the `repair` skill/prompt states verbatim that "the generic `update` (or `edit`) tool cannot repair it") -- but the resulting raised exception is exactly what the client-side MCP `isError: true` truncation (ADR 519d1206-4d2a-4500-9046-6db635209996) reduces to a generic, undifferentiated string: no parse cause, no path, no line. `get_<d>` already solved this identical problem for reads (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c), via the `find_parse_failure`/`find_feat_parse_failure` helpers wired into every `get_<d>` tool, returning a non-raising `ParseFailureResult` instead of raising. The four generic mutation tools were never given the same treatment.

**Bug 2 (`update`/`edit` only)**: a genuine content-validation failure on the *new* content submitted by the caller (e.g. `Decision.from_text(...)` under `wrap_tool_errors`) is a raised `AssertionError`/`pydantic.ValidationError` -- the exact class of problem the generic `validate` tool already solved with a non-raising `{valid, errors}` result (same ADR 519d1206), but `update`/`edit` were explicitly excluded from that fix at the time (ADR 9080b37c's own decision drivers list `update` among the tools that "must keep raising exactly as today"). `set_status`/`set_classification` do not need this half of the fix: `set_status` already carries its own `InvalidStatusResult` (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) for its one non-raising failure mode, and `set_classification`'s free-text `classification` field cannot fail validation.

This is the fourth case in the ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain (client-side `isError: true` result truncation, confirmed on OpenCode 1.18.27): case 1 redesigned the generic `validate` tool to a non-raising `{valid, errors}` result; case 2 (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) extended that rationale narrowly to `set_status`'s invalid-status case, via `InvalidStatusResult`; case 3 (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c) extended it to `get_<d>`'s parse-failure case, via `ParseFailureResult`. This ADR decides whether and how to extend the chain to case 4 -- the four generic mutation tools' failure cases, across all 12 whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) -- and records the concrete design that feat-170-update-edit-parse-failure's Phases 110/120 implement from.

## Decision Drivers

- Deliver the actionable failure detail (parse cause / validation cause, path, line) for the four generic mutation tools' failure cases host-independently, the same way 519d1206/b399f1ce/9080b37c did for `validate`, `set_status`, and `get_<d>` -- a broken existing document or invalid new content is exactly what issue #170 reports, and the truncated generic error is an operational dead-end.
- Reuse the existing `ParseFailureResult` (`error`/`path`/`id`) and `ValidateResult`/`ValidationErrorEntry` (`valid`/`errors`) models, already exercised in production by `get_<d>` and `validate` respectively -- no new result model, no new MCP result shape -- and reuse the `find_parse_failure`/`find_feat_parse_failure` helpers 9080b37c built for `get_<d>`, unchanged.
- Zero change to the successful-path wire shape: the MCP SDK serializes results with `model_dump(..., exclude_none=True)`, so a new union member that only materializes on the failure path adds nothing to a healthy tool result (the 9080b37c driver).
- Keep the documented invariant that `update`/`edit` cannot *repair* a document whose existing body fails to parse -- the `repair` skill/`doc-repairer` subagent remain the only fix path; only the failure's presentation changes (a clear, structured, non-raising result instead of a generic crash).
- Bundle all four generic mutation tools in this one pass: the fix is mechanically identical per adapter (the same catch-and-probe), and splitting it across separate features/ADRs would only duplicate the ADR/design-review overhead (decided during triage).
- Keep every other contract unchanged: a truly-absent id still raises the domain's own `XNotFoundError`; the caller-usage `ValueError`s (invalid id shape, unknown `type`, range-coordinate misuse, `edit`'s OC-parity guards, `set_status`'s `superseded_by` misuse) stay plain-raising; `find_doc_path_by_id`'s documented skip-on-parse-failure behavior is untouched.
- Do not reorder the adapters' execution: the resulting mode-dependent Bug-1/Bug-2 precedence (whole-body `update` returns `ValidateResult`; range `update` and `edit` return `ParseFailureResult`) is intentional, documented, and pinned by test, rather than removed by a lock-timing change on the common path.

## Considered Options

- Option 1: Do nothing -- keep all four generic mutation tools raise-based, relying on feat-27-validation's already-actionable exception messages.
- Option 2: Enrich the raised `XNotFoundError`/validation exception messages so the parse/validation cause rides in the exception text.
- Option 3: Give `update`/`edit` the ability to actually repair a broken document (recover the frontmatter independently of body validity, write the fix).
- Option 4 (chosen): Narrowly extend the non-raising, structured-result chain to the four generic mutation tools' failure cases -- on `XNotFoundError` from `load_<d>_by_id`, probe the domain's existing parse-failure lookup and return `ParseFailureResult` when a name-matching broken file is found (a truly-absent id still raises); for `update`/`edit` only, catch the new-content validation failure and return `ValidateResult(valid=False, ...)` mirroring `validate` exactly.

## Decision Outcome

Option 4: each of the four generic mutation tools (`update`, `edit`, `set_status`, `set_classification`) gets, per whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs` -- 12 domains), a narrow, non-raising failure branch that returns an existing structured model in place of the exception. This ADR refines 519d1206's own scope statement -- which held that "`create_<d>`, `update`, `set_status`, `set_classification`, `delete`, `parse_<d>`/`get_<d>` all keep raising" -- and 9080b37c's get-only driver: after this ADR, the four generic mutation tools are the next narrow extensions of the chain, and only the `delete`/`validate`-adjacent surfaces and `list_references` still keep their raise-based contracts among the id-resolving tools.

The concrete mechanism (implemented in feat-170-update-edit-parse-failure's Phases 110/120):

1. Bug 1 -- the existing document fails to parse (all four tools): on the `XNotFoundError` raised by the adapter's `load_<d>_by_id(...)` call, the adapter probes the domain's existing parse-failure lookup -- `general.tools._doc_paths.find_parse_failure(base_dir, id_, read_fn)` for the 11 flat-file domains, called with the domain's own cache-backed `read_<d>` as `read_fn` (the same reader `list_<d>` reads with), or `feat.tools._paths.find_feat_parse_failure(base_dir, id_)` for `feat` (no `read_fn` -- the folder name IS the id, so there is exactly one candidate path to check). If the probe yields `(path, error)`, the adapter applies the same `assert_within(base_dir, path)` defense-in-depth guard the primary load path uses (mirroring every `get_<d>` branch) and returns the existing `ParseFailureResult` (`error`/`path`/`id`, `general/models/parse_failure_result.py`); otherwise it re-raises the original `XNotFoundError` unchanged (REQ-002). Placement per tool: `update._update_<d>` wraps both `load_by_id` call sites (the whole-body branch and the range-splice branch, each inside the domain lock); `edit._edit_<d>` wraps its single `load_by_id` (the lock is held across the whole read -> match -> validate -> write sequence); `set_status._set_status_<d>` and `set_classification._set_classification_<d>` wrap their single `load_by_id` each.

2. Error-text consistency (a testable invariant, the 9080b37c precedent): `ParseFailureResult.error` carries the same parse defect as the `error` field of the domain's `list_<d>` failed row for the same broken file -- identical field path and cause, because both are `str()` of the domain's own parse exception captured through the same cache-backed `read_<d>` reader; the two are now byte-identical regardless of read order or cache state: feat-162-doc-cache-exception-footer (GitHub issue #162) fixed `DocCache`'s exception reconstruction (`general/tools/_doc_cache.py::_fresh_exception`) to preserve the trailing pydantic documentation-link footer on a warm re-raise, so `ParseFailureResult.error` and `list_<d>`'s failed-row `error` for the same broken file are exactly equal, not merely the same defect modulo that footer.

3. Bug 2 -- the caller-submitted new content fails validation (`update`/`edit` only): the `AssertionError`/`pydantic.ValidationError`/`yaml.YAMLError` caught around the existing `wrap_tool_errors(...)` new-content validation block -- the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple (`yaml.YAMLError` is unreachable for body-only content, which never parses a frontmatter block, but is kept so the catch shape is uniform across the surface) -- returns the existing `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])` instead of letting the exception propagate, mirroring `validate` exactly including feat-110's 300-char cap, so the bounded-message contract `validate` established is not re-opened on the `update`/`edit` surface. Placement: `update` wraps the new-content validation block (pre-lock in whole-body mode; inside the lock, after `load_by_id` and `splice_body`, in range mode); `edit` wraps the stage-2 post-edit validation block only -- stage-1's `_match_and_replace` not-found/multiple-matches `ValueError`s and every pre-dispatch caller-usage `ValueError` (REQ-004) stay plain-raising, and no plain `ValueError` is ever caught. `set_status`/`set_classification` get no Bug-2 branch (see Context).

4. Mode-dependent Bug-1/Bug-2 precedence (intentional, REQ-010): when both conditions hold at once (the target's on-disk file fails to parse AND the submitted content fails validation), the returned result follows each adapter's existing execution order, which this feature does not reorder: whole-body `update` validates the submitted content before taking the lock or loading the existing document, so it returns `ValidateResult(valid=False, ...)`; range `update` and `edit` load the existing document first, so they return `ParseFailureResult` (the invalid content is never reached). Reordering whole-body `update` to load-first would change lock timing on the common path for no user benefit, so the asymmetry is documented and pinned by test (ACC-007) instead of removed.

5. Return-type unions: `update` and `edit` widen from their 12-way per-domain frontmatter unions to `<frontmatter> | ParseFailureResult | ValidateResult`; `set_status` widens to `<frontmatter> | InvalidStatusResult | ParseFailureResult`; `set_classification` to `<frontmatter> | ParseFailureResult`. Every successful-path wire shape stays byte-identical -- the SDK's `exclude_none` means the new union members only materialize on the failure paths. This item describes `update`/`edit`'s success member as it stood when this ADR was authored (bare per-domain frontmatter, feat-69-update-context's precedent). ADR 19ff316b-cd11-41a7-a616-ffd84917da51 (feat-153-off-by-n), landed on the same branch afterward, independently revises `update`'s success member alone from bare frontmatter to the `UpdateResult` wrapper (`frontmatter` + `snippet`); the two changes compose, so `update`'s true return type is `UpdateResult | ParseFailureResult | ValidateResult`, not `<frontmatter> | ParseFailureResult | ValidateResult` as literally written above. `edit` is unaffected by that revision (out of scope for ADR 19ff316b) and keeps the `<frontmatter> | ParseFailureResult | ValidateResult` union exactly as stated.

6. Exclusions, recorded for the chain's auditability: (a) the generic `delete` tool has the identical Bug-1 defect but keeps raising exactly as today -- consistent with every prior link in the chain's explicit `delete` exclusion; it is recorded here as the chain's candidate case 5, not bundled into this feature. (b) `adr` stays fully out: `set_status`'s `adr` branch and all ADR tools have no whole-body replace/parse-failure-lookup mechanism by design. (c) `find_doc_path_by_id`'s documented skip-on-parse-failure behavior, and `list_references`'s/`find_related`'s/`find_similar_text`'s own failure handling, are unchanged. (d) The client-side `isError: true` truncation defect itself is NOT fixed -- this is a workaround within this repo's own tool contracts, same as every prior link in the chain.

### Consequences

- Good: the actionable failure now reaches the calling agent host-independently for all four generic mutation tools x 12 domains -- an existing-but-broken target document returns `ParseFailureResult` with the parse cause (the same defect as the `list_<d>` failed row for the same file), and invalid new content on `update`/`edit` returns `ValidateResult(valid=False)` with the 300-char-capped cause -- both as successful (`isError: false`) structured results, the exact channel 519d1206's wire-level proof showed the client preserves.
- Good: no new model, no new MCP result shape -- `ParseFailureResult` and `ValidateResult`/`ValidationErrorEntry` are already exercised in production by `get_<d>` and `validate` respectively, and the flat-file probe reuses the `find_parse_failure`/`find_feat_parse_failure` helpers unchanged.
- Good: zero change to the successful-path wire shape (the SDK's `exclude_none` means the new union members only materialize on the failure paths); a truly-absent id and every caller-usage `ValueError` contract stay unchanged (REQ-002/REQ-004); the documented no-repair invariant for `update`/`edit` is preserved -- the `repair` skill/`doc-repairer` subagent remain the only fix path.
- Good: no change to the feat-107-doc-cache contract -- the new branches only ever return early on a failure path, before any write or cache-warming `read_<d>(path)` call.
- Good: `feat` and the 11 flat-file domains are unified under one failure-delivery shape for all four tools, as 9080b37c already did for the `get_<d>` surface.
- Bad: this is the fourth documented asymmetric tool contract in this repo (519d1206's `validate`, b399f1ce's `set_status`, 9080b37c's `get_<d>`, now the four generic mutation tools) -- a future contributor must know the chain rather than assume a single universal error-reporting convention across the whole tool surface.
- Bad: the return unions widen -- `update`/`edit` from a 12-way frontmatter union to `<frontmatter> | ParseFailureResult | ValidateResult`, `set_status` to `<frontmatter> | InvalidStatusResult | ParseFailureResult`, `set_classification` to `<frontmatter> | ParseFailureResult` -- a caller must check for the new failure shapes on every non-exception return.
- Bad: the mode-dependent Bug-1/Bug-2 precedence means the same combined input (broken existing document + invalid submitted content) returns different result types on the three surfaces (`ValidateResult` in whole-body `update`, `ParseFailureResult` in range `update` and `edit`) -- deliberate, documented, and pinned by test (REQ-010/ACC-007), but an asymmetry a caller must know.
- Bad: the generic `delete` tool's identical Bug-1 defect remains raise-based (the chain's candidate case 5).
- Bad (tracked, not blocking): as with 519d1206/b399f1ce/9080b37c, a live MCP-client round-trip cannot be automated; verification is unit-level only. The workaround remains harmless and correct if/when a client fixes its `isError: true` handling.

### Confirmation

To be confirmed during feat-170-update-edit-parse-failure's Phases 110/120 at the unit level (direct Python calls through the four tools' own test modules, mirroring the confirmations 519d1206/b399f1ce/9080b37c record), per tool x domain (the REQ-009 matrix): (a) a target id whose only matching on-disk file fails to parse returns `ParseFailureResult` (never raises) with the correct `error`/`path`/`id` and no write to disk, its `error` text is byte-identical to the same file's `list_<d>` failed-row `error` (identical field path and cause, including the trailing pydantic documentation line -- fixed by feat-162-doc-cache-exception-footer, GitHub issue #162, see Decision Outcome item 2); (b) for `update` (whole-body and range modes) and `edit`, genuinely invalid new content against a healthy existing document returns `ValidateResult(valid=False, errors=[...])` with the 300-char-capped message and no write to disk; (c) a truly-missing id still raises the domain's own `XNotFoundError` unchanged (regression guard); (d) the happy path (healthy document, valid content) is unchanged in shape and still writes/bumps `updated` as before; and (e) the combined-failure case (broken existing document AND invalid submitted content) returns `ValidateResult` in whole-body `update` but `ParseFailureResult` in range `update` and `edit`, with nothing written to disk in all three (REQ-010/ACC-007). As with the three prior ADRs, no live MCP-client/OpenCode-session round-trip is attempted or recorded as an outstanding commitment, for the same automation-limitation reasons they document.

## Pros and Cons of the Options

### Option 1: Do nothing -- keep all four generic mutation tools raise-based

#### Pros

- No new work, no result-type union widening, no fourth asymmetric tool contract to document or maintain beyond the three 519d1206/b399f1ce/9080b37c already introduced.
- Matches the remaining id-resolving tools' (`delete`, `list_references`) raise-based convention.

#### Cons

- Known to fail on at least one real, current, widely-used MCP client (OpenCode 1.18.27) for exactly the same reason the chain fixed for `validate`, `set_status`, and `get_<d>`: the parse cause feat-27-validation invested in is discarded before it reaches the agent, leaving issue #170's reported bare, undifferentiated "Error executing tool ..." dead-end on all four tools x 12 domains.
- Leaves Bug 2's dead-end in place too: a genuine new-content validation failure on `update`/`edit` -- the exact class `validate` already made non-raising -- still surfaces as a truncated generic error.

### Option 2: Enrich the raised exception messages (XNotFoundError / validation exceptions)

#### Pros

- A smaller, message-only change: the `XNotFoundError` raised for a broken target could carry the parse cause, and the `update`/`edit` validation exceptions already carry feat-27-validation's enriched text.
- Benefits every consumer of the raised exception (e.g. direct Python callers), not just MCP clients.

#### Cons

- Still rides the lossy `isError: true` channel: 519d1206's wire-level proof showed the client truncates any raised exception to a bare "Error executing tool ..." -- enriching the message does not sidestep the truncation; only a successful (`isError: false`) structured result does.
- Broadens the failure-message behavior of every id-resolving tool that shares the `load_by_id` path (`delete`, `list_references` included), a wider change surface than this feature's four-tool scope.

### Option 3: Give update/edit the ability to actually repair a broken document

#### Pros

- Would eliminate the root dead-end for the write surface: a broken document could be fixed through the very tool that failed, without routing to the `repair` skill/`doc-repairer` subagent.
- Would make the Bug-1 `ParseFailureResult` branch unnecessary on the `update`/`edit` surface (the tool simply succeeds).

#### Cons

- Contradicts the `repair` skill/prompt's documented normative assumption ("the generic `update` (or `edit`) tool cannot repair it") and the repair workflow's load-bearing invariant that no specmgr MCP tool can return the raw content of a document that fails to parse -- rewording or retiring that workflow is a much larger change.
- Enlarges the blast radius considerably (independent frontmatter recovery, partial-write semantics, new failure modes on the write path) for a bug report that is about error *presentation*, not missing functionality -- explicitly decided against during triage.

### Option 4: Extend the non-raising structured-result chain to the four generic mutation tools' failure cases (chosen)

#### Pros

- Directly fixes issue #170's reported dead-end for all four generic mutation tools x 12 domains, using a rationale and pattern already proven three times (519d1206, b399f1ce, 9080b37c).
- Fully within this repo's own control; immediately effective without waiting on a third-party client fix.
- No new model, no new result shape: reuses the `ParseFailureResult` and `ValidateResult`/`ValidationErrorEntry` already exercised in production, and the `find_parse_failure`/`find_feat_parse_failure` helpers 9080b37c built for `get_<d>`, unchanged.
- Zero change to the successful-path wire shape -- the SDK's `exclude_none` means the new union members only materialize on the failure paths.
- Keeps every other contract unchanged: the truly-absent-id `XNotFoundError` raise, the caller-usage `ValueError`s, `find_doc_path_by_id`'s skip behavior, `set_status`'s own `InvalidStatusResult` pre-check (which runs before any lock/load, so an out-of-vocabulary status against a broken existing document still returns `InvalidStatusResult` first), and the documented no-repair invariant for `update`/`edit`.
- Bundling all four tools in one pass is mechanically identical per adapter (the same catch-and-probe), so one ADR/design review covers the whole surface.

#### Cons

- Introduces a fourth documented asymmetric tool contract -- a future contributor must know the chain.
- Widens the return unions (`update`/`edit`: `<frontmatter> | ParseFailureResult | ValidateResult`; `set_status`: `<frontmatter> | InvalidStatusResult | ParseFailureResult`; `set_classification`: `<frontmatter> | ParseFailureResult`).
- The mode-dependent Bug-1/Bug-2 precedence (whole-body `update` -> `ValidateResult`; range `update`/`edit` -> `ParseFailureResult`) is a deliberate asymmetry that must be documented and pinned by test.
- The generic `delete` tool's identical Bug-1 defect stays raise-based (recorded as the chain's candidate case 5).
- Same tracked-but-unresolved limitation as 519d1206/b399f1ce/9080b37c: no live MCP-client round-trip can be automated; verification stays unit-level.

## More Information

- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation"): case 1 of the chain; its Context/Consequences/Confirmation carry the full original investigation this ADR does not repeat.
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 ("Extend the non-raising structured-result workaround to set_status's invalid-status case"): case 2; the `InvalidStatusResult` precedent and the narrow-extension driver this ADR follows.
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c ("Extend the non-raising structured-result workaround to get_<d>'s parse-failure case"): case 3; the `ParseFailureResult` model and the `find_parse_failure`/`find_feat_parse_failure` helpers this ADR reuses unchanged.
- Feature plan and progress: `.specmgr/feat/feat-170-update-edit-parse-failure/README.md` (Phases 110/120 implement the mechanism this ADR records; Phase 130 syncs the docs surface).
- GitHub issue #170: https://github.com/dfch/biz.dfch.SpecMgr/issues/170.
- feat-162-doc-cache-exception-footer (GitHub issue #162): implemented the str-faithful `DocCache` exception reconstruction this ADR's Decision Outcome item 2 and Confirmation section originally flagged as a qualified, upgrade-ready interim state -- both sections were amended in place to drop the qualification, on this ADR's own feature branch (feat-170-update-edit-parse-failure) once it had merged onto a `dev` carrying feat-162, per feat-162's plan Phase 900 (Task 900.100).
- ADR 19ff316b-cd11-41a7-a616-ffd84917da51 ("Revise the generic update tool's success return to frontmatter plus an optional before/after snippet"): feat-153-off-by-n, composed onto the same `update` surface after this ADR, independently revises `update`'s success member from bare frontmatter to the `UpdateResult` wrapper -- see this ADR's Decision Outcome item 5 for how the two changes compose.
