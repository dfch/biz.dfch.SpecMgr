---
classification: null
created: '2026-09-29T15:14:11.057+02:00'
id: feat-170-update-edit-parse-failure
status: planning
type: feat
updated: '2026-09-29T15:14:11.057+02:00'
version: 1.0.0
---

# Feature: Non-Raising Structured Results for update/edit/set_status/set_classification Parse Failures

## Plan

### Overview

GitHub issue #170: `update` and `edit` (reported for `type="dec"`, but structurally affecting
every whole-body domain) crash with a bare, undifferentiated tool-execution error in three
related situations, even when `validate` independently confirms the submitted content is valid,
and nothing is ever written to disk in any case. Root-cause investigation found two distinct,
already-partially-addressed defects colliding in the reporter's test corpus (every `dec` document
there happened to be broken):

- **Bug 1 (all four generic mutation tools -- `update`, `edit`, `set_status`,
  `set_classification`)**: every per-domain adapter's first step under the domain lock is
  `load_<d>_by_id()`, which resolves via `general.tools._doc_paths.find_doc_path_by_id`. That
  resolver silently skips any file that fails to parse (by design, so one broken file never
  blocks lookup of a different id) -- so when the *target* id's only matching file is itself
  broken, the scan raises the domain's raw `XNotFoundError`. This is an already-documented,
  intentional limitation (the `repair` skill/prompt states verbatim that "the generic `update`
  (or `edit`) tool cannot repair it"), but the resulting raised exception is exactly what the
  client-side MCP `isError: true` truncation (ADR 519d1206-4d2a-4500-9046-6db635209996) reduces to
  a generic, undifferentiated string. `get_<d>` already solved this identical problem for reads
  (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c), via a `find_parse_failure`/`find_feat_parse_failure`
  helper already wired into every `get_<d>` tool, returning a non-raising `ParseFailureResult`
  instead of raising. The four generic mutation tools were never given the same treatment.
- **Bug 2 (`update`/`edit` only)**: a genuine content-validation failure on the *new* content
  submitted by the caller (e.g. `Decision.from_text(...)` under `wrap_tool_errors`) is a raised
  `AssertionError`/`pydantic.ValidationError` -- the exact class of problem the generic `validate`
  tool already solved (same ADR 519d1206), but `update`/`edit` were explicitly excluded from that
  fix at the time (ADR 9080b37c's own decision drivers list `update` as a tool that "must keep
  raising exactly as today"). `set_status`/`set_classification` do not need this half of the fix:
  `set_status` already has its own `InvalidStatusResult` for its one failure mode, and
  `set_classification`'s free-text `classification` field cannot fail validation.

This feature extends the non-raising, structured-result workaround chain
(519d1206 -> b399f1ce-ed42-4929-b01c-7a57d18e8014 -> 9080b37c-82b3-4f63-81f1-79641d0bf14c) to cover
both bugs, across all four generic mutation tools, for all 12 whole-body domains
(req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs). It deliberately does **not** change the
documented invariant that `update`/`edit` cannot repair a document whose existing body fails to
parse -- it only replaces the resulting crash with a clear, non-raising, actionable result. See
Decisions Made for the scope choices already locked in during triage.

### Requirements

- REQ-001: For each of `update`, `edit`, `set_status`, and `set_classification`, every per-domain adapter must, on catching the domain's own `XNotFoundError` from `load_<d>_by_id`, probe the domain's existing parse-failure lookup helper (`general.tools._doc_paths.find_parse_failure` for the 11 flat-file domains, `feat.tools._paths.find_feat_parse_failure` for `feat`) and return the existing `ParseFailureResult` model instead of letting the raw `XNotFoundError` propagate, whenever that probe finds a name-matching file that fails to parse.

- REQ-002: A truly-absent id (no file on disk matches at all) must continue to raise the domain's own `XNotFoundError` unchanged in all four tools -- REQ-001's new branch must only intercept the specific "the file exists but fails to parse" case, never the general not-found case.

- REQ-003: For `update` and `edit` only, a content-validation failure on the caller-submitted new content (or, for `edit`, on the post-edit result) -- an `AssertionError` or `pydantic.ValidationError` caught around the existing `wrap_tool_errors(...)` block -- must return a `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=...)])` instead of letting the exception propagate, reusing the exact model the generic `validate` tool already returns.

- REQ-004: `edit`'s existing stage-1 OC-parity guards (identical-input, empty-`old_str`, not-found, multiple-matches) and every tool's pre-dispatch caller-usage `ValueError`s (invalid id shape, unknown `type`, range-coordinate misuse, `superseded_by` misuse) must remain unchanged, plain, raising `ValueError`s -- REQ-003 only covers the structural/field content-validation failure channel, not caller-usage errors, mirroring `validate`'s own established convention of never catching a shape-mismatch `ValueError`.

- REQ-005: This feature must not change the documented invariant that `update`/`edit` cannot write a fix over a document whose existing body fails to parse -- the `repair` skill/prompt's guidance stays correct and unmodified; only the failure's presentation changes (a clear, structured, non-raising result instead of a generic crash).

- REQ-006: Update the return-type union and the `@mcp.tool()` description / docstring (`Returns`/`Raises` sections) of `update`, `edit`, `set_status`, and `set_classification` to document the new `ParseFailureResult` (and, for `update`/`edit`, `ValidateResult`) branches.

- REQ-007: Update `AGENTS.md`'s `general/` package bullet (and any per-domain bullet text describing `update`/`edit`/`set_status`/`set_classification` behavior) to reflect the new non-raising branches, and regenerate `docs/MCP.md` via `specmgr docs`.

- REQ-008: Write a new ADR recording this decision as the fourth extension of the ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain (after 519d1206 itself, b399f1ce-ed42-4929-b01c-7a57d18e8014, and 9080b37c-82b3-4f63-81f1-79641d0bf14c), referencing GitHub issue #170, and explicitly recording the two out-of-scope non-goals: no repair capability added to `update`/`edit`, and no change to `find_doc_path_by_id`'s documented skip-on-parse-failure behavior.

- REQ-009: Add unit test coverage, per tool x domain, for: (a) an existing-but-broken document under the target id returns the expected `ParseFailureResult` (correct `error`/`path`/`id`) with no write to disk; (b) for `update`/`edit` only, invalid new content against a healthy existing document returns `ValidateResult(valid=False, ...)` with no write to disk; (c) a truly-missing id still raises the domain's own `XNotFoundError` (regression guard); (d) the happy path (healthy document, valid content) is unchanged in shape and still writes/bumps `updated` as before.

### Acceptance Criteria

- [ ] ACC-001: (REQ-001/REQ-002) For every one of the 12 whole-body domains and all four tools (`update`, `edit`, `set_status`, `set_classification`), calling the tool against an id whose only matching on-disk file fails to parse returns a `ParseFailureResult` (never raises), while calling it against a genuinely absent id still raises the domain's `XNotFoundError` unchanged.

- [ ] ACC-002: (REQ-003/REQ-004) For `update` and `edit`, submitting genuinely invalid new content against a healthy existing document returns `ValidateResult(valid=False, errors=[...])` (never raises), while every existing caller-usage `ValueError` path (bad id shape, unknown type, range-coordinate misuse, `edit`'s OC-parity stage-1 guards) still raises exactly as before.

- [ ] ACC-003: (REQ-005) No existing test or documented behavior asserting that `update`/`edit` cannot repair a document whose existing body fails to parse is broken or contradicted by this change -- the `repair` skill/prompt's guidance remains accurate without edits to its own text.

- [ ] ACC-004: (REQ-006/REQ-007) `update`/`edit`/`set_status`/`set_classification`'s docstrings, `@mcp.tool()` descriptions, and `AGENTS.md` accurately describe the new non-raising branches; `docs/MCP.md` regenerates cleanly via `specmgr docs` with no manual edits needed afterward.

- [ ] ACC-005: (REQ-008) A new ADR exists, is linked from this feature's Related Decisions, and is accepted before or alongside the code landing.

- [ ] ACC-006: (REQ-009) The full test matrix described in REQ-009 is green (`pytest -n auto`), and the existing `not_found_error=...`-parametrized regression tests in `tests/general/tools/test_update.py`/`test_edit.py`/`test_set_status.py`/`test_delete.py`-adjacent `set_classification` tests continue to pass unchanged.

### Scope

#### Included

- `general/tools/update.py`: every `_update_<d>` adapter (12 domains), both whole-body and range-splice branches.

- `general/tools/edit.py`: every `_edit_<d>` adapter (12 domains).

- `general/tools/set_status.py`: every `_set_status_<d>` adapter (12 whole-body domains only -- the `adr` branch is out of scope, matching every prior ADR in this chain's exclusion of `adr`).

- `general/tools/set_classification.py`: every `_set_classification_<d>` adapter (12 domains).

- Reuse of the existing `general.models.ParseFailureResult` and `general.models.ValidateResult`/`ValidationErrorEntry` models -- no new result model is introduced.

- A new ADR documenting this decision.

- Docstring/description updates on all four tool files, `AGENTS.md`, and `docs/MCP.md` regeneration.

- Test coverage across all four tools x 12 domains for both new branches plus the two regression guards (truly-missing id, happy path).

#### Explicitly Out Of Scope

- Giving `update`/`edit` the ability to actually repair (write a fix over) a document whose existing body fails to parse -- explicitly decided against during triage (see Decisions Made). The `repair` skill/`doc-repairer` subagent remain the only path to fix a broken document.

- Changing `general.tools._doc_paths.find_doc_path_by_id`'s documented skip-on-parse-failure scanning behavior, or `list_references`'s/`find_related`'s/`find_similar_text`'s own failure handling.

- `adr`'s own `set_status` branch, `update_frontmatter`, `update_section`, and the `option_*` tools -- ADR has no whole-body replace/parse-failure-lookup mechanism by design and stays fully out of this feature.

- Fixing the underlying, out-of-this-repo's-control MCP client-side `isError: true` truncation defect itself -- this feature is a workaround within this repo's own tool contracts, same as every prior link in the 519d1206 chain.

### Dependencies

#### Depends On

- ADR 519d1206-4d2a-4500-9046-6db635209996 (the original non-raising-structured-result workaround decision).

- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (`set_status`'s `InvalidStatusResult` precedent).

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (`get_<d>`'s `ParseFailureResult` precedent and the `find_parse_failure`/`find_feat_parse_failure` helpers this feature reuses unchanged).

### Design Notes

**Reuse, not new models.** `ParseFailureResult` (`error`/`path`/`id`) and `ValidateResult`/`ValidationErrorEntry` (`valid`/`errors`) already exist and are exercised in production by `get_<d>` and `validate` respectively. This feature is purely a matter of catching the right exception at the right point in each of the 48 adapter functions (4 tools x 12 domains) and returning the existing model -- no new pydantic model, no new MCP result shape.

**Where each branch goes, per tool:**

- `update._update_<d>`: Bug 1's catch wraps `load_<d>_by_id(...)` (both the whole-body branch and the range-splice branch each have their own `load_<d>_by_id` call site). Bug 2's catch wraps the pre-lock `wrap_tool_errors(...)` block that validates the caller's new `content` (whole-body mode) or the spliced result (range mode) -- this block already runs before any lock/file-write, so wrapping it in `try`/`except` costs nothing extra.

- `edit._edit_<d>`: Bug 1's catch wraps `load_<d>_by_id(...)` (single call site per adapter, since `edit` holds the lock across the whole read -> match -> validate -> write sequence). Bug 2's catch wraps the stage-2 `wrap_tool_errors(...)` block that validates the edited body -- stage 1's OC-parity guards (`_match_and_replace`'s not-found/multiple-matches `ValueError`s) are untouched per REQ-004.

- `set_status._set_status_<d>`: Bug 1 only. Catch wraps `load_<d>_by_id(...)`. The existing pre-dispatch `_check_status_allowed`/`InvalidStatusResult` check is unaffected -- it already runs before any lock/load, so it composes cleanly with this feature's `load_by_id`-catch addition (an out-of-vocabulary status against a broken existing document still returns `InvalidStatusResult` first, since that check never reaches `load_by_id`).

- `set_classification._set_classification_<d>`: Bug 1 only. Catch wraps `load_<d>_by_id(...)`, mirroring `set_status`'s shape exactly.

**`feat`'s divergent helper.** `feat.tools._paths.find_feat_parse_failure(base_dir, id_)` takes no `read_fn` (the folder name IS the id, so there is exactly one candidate path to check), unlike the shared `general.tools._doc_paths.find_parse_failure(base_dir, id_, read_fn)` the other 11 domains use. Each `_..._feat` adapter's catch block calls the feat-specific helper, exactly mirroring `get_feat.py`'s own existing branch.

**Implementation style: follow the existing per-adapter convention, not a shared abstraction.** Every adapter in `update.py`/`edit.py`/`set_status.py`/`set_classification.py` is already a largely verbatim, per-domain copy (explicitly called out as "verbatim port" in each file's own module docstring) rather than a shared parametrized helper. This feature follows that same convention: the `try`/`except XNotFoundError: ... find_parse_failure(...) ...` block is repeated per adapter (48 times total), not factored into a cross-cutting helper, to stay consistent with the codebase's established style and keep each domain's adapter independently readable/portable. A tiny, purely mechanical helper for the repeated 4-line catch-and-probe pattern may be considered during implementation if the duplication proves error-prone, but is not required by this plan.

**Interaction with feat-107-doc-cache.** No change to any cache-warming/invalidation call site -- the new branches only ever return early on a *failure* path, before any write or `read_<d>(path)` cache-warm call, so the cache-warming contract feat-107 established is untouched.

### Related Decisions

- 519d1206-4d2a-4500-9046-6db635209996 (ADR): the original decision to redesign `validate` as a non-raising, structured-result tool.

- b399f1ce-ed42-4929-b01c-7a57d18e8014 (ADR): extended the workaround to `set_status`'s invalid-status case via `InvalidStatusResult`.

- 9080b37c-82b3-4f63-81f1-79641d0bf14c (ADR): extended the workaround to `get_<d>`'s parse-failure case via `ParseFailureResult`, and the `find_parse_failure`/`find_feat_parse_failure` helpers this feature reuses unchanged.

### Task List

#### Phase 100: ADR

- [ ] Task 100.100: Draft and create the new ADR (fourth link in the 519d1206 chain) recording this decision, referencing GitHub issue #170, explicitly naming the two locked-in scope decisions (no repair capability; bundle all four generic mutation tools together) and the non-goals from the Scope section above.

- [ ] Task 100.110: Get the ADR to `accepted` status before or alongside the Phase 110/120 code landing.

#### Phase 110: Bug 1 -- ParseFailureResult reuse (update, edit, set_status, set_classification x 12 domains)

- [ ] Task 110.100: `general/tools/update.py` -- add the `XNotFoundError` -> `find_parse_failure`/`find_feat_parse_failure` -> `ParseFailureResult` branch to all 12 `_update_<d>` adapters (both whole-body and range-splice `load_by_id` call sites in each).

- [ ] Task 110.110: `general/tools/edit.py` -- same branch, all 12 `_edit_<d>` adapters.

- [ ] Task 110.120: `general/tools/set_status.py` -- same branch, all 12 whole-body `_set_status_<d>` adapters (the `adr` branch stays untouched).

- [ ] Task 110.130: `general/tools/set_classification.py` -- same branch, all 12 `_set_classification_<d>` adapters.

- [ ] Task 110.140: Widen each tool's return-type union annotation (`_UpdateFrontmatter | ParseFailureResult`, etc.) accordingly.

#### Phase 120: Bug 2 -- ValidateResult reuse (update, edit only)

- [ ] Task 120.100: `general/tools/update.py` -- wrap the pre-lock new-content validation block (both whole-body and post-splice) in `try`/`except (AssertionError, ValidationError)`, returning `ValidateResult(valid=False, errors=[...])`.

- [ ] Task 120.110: `general/tools/edit.py` -- same treatment around the stage-2 post-edit validation block only; leave stage-1's OC-parity guards untouched.

- [ ] Task 120.120: Widen `update`'s and `edit`'s return-type union annotations to include `ValidateResult`.

#### Phase 130: Docs

- [ ] Task 130.100: Update `update.py`/`edit.py`/`set_status.py`/`set_classification.py`'s module docstrings, `@mcp.tool()` `description=`, and function-level `Returns`/`Raises` sections.

- [ ] Task 130.110: Update `AGENTS.md`'s `general/` package bullet (and any per-domain bullet referencing `update`/`edit`/`set_status`/`set_classification` semantics).

- [ ] Task 130.120: Regenerate `docs/MCP.md` via `specmgr docs` and confirm no drift.

#### Phase 140: Tests

- [ ] Task 140.100: Add the existing-broken-document -> `ParseFailureResult` test case for all 12 domains, for each of `update`/`edit`/`set_status`/`set_classification` (mirroring the existing `not_found_error=...` parametrized test shape already present in each tool's test module).

- [ ] Task 140.110: Add the invalid-new-content -> `ValidateResult(valid=False, ...)` test case for all 12 domains, for `update` and `edit` only.

- [ ] Task 140.120: Confirm/extend the existing truly-missing-id regression tests (`not_found_error=...` parametrizations) still pass unchanged for all four tools.

- [ ] Task 140.130: Confirm/extend happy-path tests (healthy doc + valid content) for all four tools are unchanged in shape.

#### Phase 150: Quality Gate

- [ ] Task 150.100: `ruff format`/`ruff check`, `vulture`, `pylint` (advisory).

- [ ] Task 150.110: `pytest -n auto --cov=src --cov-report=` full suite green.

- [ ] Task 150.120: `specmgr docs` / `specmgr adr-toc` regeneration, `specmgr coverage-badge`.

## Progress

### Current Status

**As of 2026-09-29**: Feature plan created from GitHub issue #170 triage. Root cause fully
diagnosed and confirmed by reading the relevant source (`general/tools/update.py`, `edit.py`,
`set_status.py`, `set_classification.py`, `general/tools/_doc_paths.py`, the `dec` domain's
`_io.py`/`_paths.py`, the existing `get_dec.py` precedent, and the three prior ADRs in the
519d1206 chain). No implementation has started yet -- this feature was deliberately created as a
plan-only artifact per explicit instruction; implementation is a separate, later step.

### Blockers

- None currently. Implementation has not been authorized to start yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-29T13:09:04.000Z - Created

Created this feature from GitHub issue #170 triage. The issue's three reported repro cases
(dec-only) were diagnosed as two independent, cross-domain defects (a `load_by_id`-against-a-
broken-existing-document case affecting all four generic mutation tools, and a new-content
validation-failure case affecting `update`/`edit` only), both instances of the same client-side
MCP error-truncation problem `validate`/`set_status`/`get_<d>` already worked around via their own
non-raising structured results. This plan reuses those exact existing models (`ParseFailureResult`,
`ValidateResult`) rather than introducing new ones.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-29T13:09:04.000Z - Bundle set_status/set_classification into the same pass

Although GitHub issue #170 only reported `update`/`edit`, `set_status` and `set_classification`
share the identical `load_by_id`-against-a-broken-existing-document defect (Bug 1). Decided to fix
all four generic mutation tools together in this one feature, rather than filing a separate
follow-up issue for `set_status`/`set_classification`, since the fix is mechanically identical and
splitting it would only duplicate the ADR/design-review overhead.

#### 2026-09-29T13:09:04.000Z - No repair capability added to update/edit

Explicitly decided against making `update`/`edit` able to write a fix over a document whose
existing body fails to parse (e.g. by recovering just the frontmatter independently of body
validity). That would contradict the `repair` skill/prompt's documented assumption ("the generic
`update` (or `edit`) tool cannot repair it") and enlarge the blast radius considerably for a
bug report that is really about error *presentation*, not missing functionality. The scope stays
narrow: replace the crash with a clear, non-raising, structured result; the `repair`
skill/`doc-repairer` subagent remain the only path to actually fix a broken document.

### Related PRs / Commits

- [Issue #170](https://github.com/dfch/biz.dfch.SpecMgr/issues/170): the triggering bug report.

### More Information

See the three prior links in the workaround chain for full background:
ADR 519d1206-4d2a-4500-9046-6db635209996, ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c. The `repair` skill (`.opencode/skill/repair/SKILL.md`) and
`doc-repairer` subagent remain the canonical path for actually fixing a document that fails to
parse; this feature does not change or duplicate that workflow.
