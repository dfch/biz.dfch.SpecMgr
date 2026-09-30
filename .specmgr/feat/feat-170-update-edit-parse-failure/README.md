---
classification: null
created: '2026-09-29T15:14:11.057+02:00'
id: feat-170-update-edit-parse-failure
status: progress
type: feat
updated: '2026-09-30T12:01:02.296+02:00'
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

- REQ-001: For each of `update`, `edit`, `set_status`, and `set_classification`, every per-domain adapter must, on catching the domain's own `XNotFoundError` from `load_<d>_by_id`, probe the domain's existing parse-failure lookup helper (`general.tools._doc_paths.find_parse_failure` for the 11 flat-file domains, `feat.tools._paths.find_feat_parse_failure` for `feat`) and return the existing `ParseFailureResult` model instead of letting the raw `XNotFoundError` propagate, whenever that probe finds a name-matching file that fails to parse. The flat-file probe must be called with the domain's own cache-backed `read_<d>` as `read_fn` (the same reader `list_<d>` reads with -- the probed file's `ParseFailureResult.error` therefore carries the same parse defect as the `list_<d>` failed row for the same file, identical field path and cause, modulo the trailing pydantic documentation line qualification every `get_<d>` already documents), and the probed path must pass the same `_path_safety.assert_within(base_dir, path)` defense-in-depth guard the primary load path applies, mirroring every `get_<d>`'s own branch.

- REQ-002: A truly-absent id (no file on disk matches at all) must continue to raise the domain's own `XNotFoundError` unchanged in all four tools -- REQ-001's new branch must only intercept the specific "the file exists but fails to parse" case, never the general not-found case.

- REQ-003: For `update` and `edit` only, a content-validation failure on the caller-submitted new content (or, for `edit`, on the post-edit result) -- the `AssertionError`/`pydantic.ValidationError`/`yaml.YAMLError` caught around the existing `wrap_tool_errors(...)` block on the generic `validate` tool's own `_CAUGHT_EXCEPTIONS` tuple (`yaml.YAMLError` is unreachable for body-only content, which never parses a frontmatter block, but is kept so the catch shape is uniform across the surface) -- must return a `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=...)])` instead of letting the exception propagate, reusing the exact model the generic `validate` tool already returns. The single `errors[].message` must be `str(exception)` capped exactly as `validate` caps it (via `snippet(..., max_chars=300)`, feat-110), so the bounded-message contract `validate` established is not re-opened on the `update`/`edit` surface; no other exception -- in particular the plain caller-usage `ValueError`s of REQ-004 -- is ever caught.

- REQ-004: `edit`'s existing OC-parity guards (the pre-dispatch identical-input and empty-`old_str` checks, and stage-1's `_match_and_replace` not-found/multiple-matches `ValueError`s) and every tool's pre-dispatch caller-usage `ValueError`s (invalid id shape, unknown `type`, range-coordinate misuse, `superseded_by` misuse) must remain unchanged, plain, raising `ValueError`s -- REQ-003 only covers the structural/field content-validation failure channel, not caller-usage errors, mirroring `validate`'s own established convention of never catching a shape-mismatch `ValueError`.

- REQ-005: This feature must not change the documented invariant that `update`/`edit` cannot write a fix over a document whose existing body fails to parse -- the `repair` skill/prompt's normative guidance (never write the repair back via `update`/`edit`) stays correct; only the failure's presentation changes (a clear, structured, non-raising result instead of a generic crash). The mechanism parentheticals in the repair artifacts (`general/prompts/repair.py`'s description and module docstring, `general/data/general_repair_instructions.md`, `.opencode/skill/repair/SKILL.md`, `.opencode/agent/doc-repairer.md`) that describe the old behavior (that the adapters convert the parse failure into the domain's not-found error) become inaccurate and are reworded in Phase 130 to name the new non-raising `ParseFailureResult` branch instead, preserving every phrase `tests/general/prompts/test_repair.py` pins; `general/tools/_doc_paths.py`'s module and `find_parse_failure` docstrings are refreshed in the same task.

- REQ-006: Update the return-type union and the `@mcp.tool()` description / docstring (`Returns`/`Raises` sections) of `update`, `edit`, `set_status`, and `set_classification` to document the new `ParseFailureResult` (and, for `update`/`edit`, `ValidateResult`) branches.

- REQ-007: Update `AGENTS.md`'s `general/` package bullet (and any per-domain bullet text describing `update`/`edit`/`set_status`/`set_classification` behavior) to reflect the new non-raising branches, and regenerate `docs/MCP.md` via `specmgr mcp-docs` (NOT `specmgr docs` -- that command regenerates `docs/api/` + `docs/GENERATED.md` only); the `CHANGELOG.md` `[Unreleased]` entry for the new branches lands in the same docs phase.

- REQ-008: Write a new ADR recording this decision as the fourth extension of the ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain (after 519d1206 itself, b399f1ce-ed42-4929-b01c-7a57d18e8014, and 9080b37c-82b3-4f63-81f1-79641d0bf14c), referencing GitHub issue #170, and explicitly recording the two out-of-scope non-goals: no repair capability added to `update`/`edit`, and no change to `find_doc_path_by_id`'s documented skip-on-parse-failure behavior.

- REQ-009: Add unit test coverage, per tool x domain, for: (a) an existing-but-broken document under the target id returns the expected `ParseFailureResult` (correct `error`/`path`/`id`) with no write to disk; (b) for `update`/`edit` only, invalid new content against a healthy existing document returns `ValidateResult(valid=False, ...)` with no write to disk; (c) a truly-missing id still raises the domain's own `XNotFoundError` (regression guard); (d) the happy path (healthy document, valid content) is unchanged in shape and still writes/bumps `updated` as before.

- REQ-010: When both new-branch conditions hold at once (the target document's on-disk file fails to parse AND the caller-submitted content fails validation), the returned result follows each adapter's existing execution order, which this feature does not reorder: whole-body `update` validates the submitted content before taking the lock or loading the existing document, so it returns `ValidateResult(valid=False, ...)`; range `update` and `edit` load the existing document first, so they return `ParseFailureResult` (the invalid content is never reached). This mode-dependent precedence is intentional and is pinned by test (ACC-007).

### Acceptance Criteria

- [ ] ACC-001: (REQ-001/REQ-002) For every one of the 12 whole-body domains and all four tools (`update`, `edit`, `set_status`, `set_classification`), calling the tool against an id whose only matching on-disk file fails to parse returns a `ParseFailureResult` (never raises) whose `error` carries the same parse defect as the domain's `list_<d>` failed row for the same file (the testable consistency invariant every `get_<d>` already pins), while calling it against a genuinely absent id still raises the domain's `XNotFoundError` unchanged.

- [ ] ACC-002: (REQ-003/REQ-004) For `update` and `edit`, submitting genuinely invalid new content against a healthy existing document returns `ValidateResult(valid=False, errors=[...])` (never raises) whose single `errors[].message` is capped exactly as the `validate` tool caps it (300 chars via `snippet`, feat-110), while every existing caller-usage `ValueError` path (bad id shape, unknown type, range-coordinate misuse, `edit`'s OC-parity guards -- pre-dispatch identical-input/empty-`old_str` and stage-1 match guards) still raises exactly as before.

- [ ] ACC-003: (REQ-005) The `repair` skill/prompt's normative guidance (never write the repair back via `update`/`edit`) remains accurate and unchanged; the repair artifacts' stale mechanism parentheticals (the `repair` prompt's description and module docstring, its packaged instructions file, the `repair` skill, the `doc-repairer` agent) and `general/tools/_doc_paths.py`'s docstrings are reworded to name the new non-raising `ParseFailureResult` branch, and `tests/general/prompts/test_repair.py` stays green unchanged (its pinned phrases are preserved by the rewording).

- [ ] ACC-004: (REQ-006/REQ-007) `update`/`edit`/`set_status`/`set_classification`'s docstrings, `@mcp.tool()` descriptions, and `AGENTS.md` accurately describe the new non-raising branches; `docs/MCP.md` regenerates cleanly via `specmgr mcp-docs` with no manual edits needed afterward.

- [ ] ACC-005: (REQ-008) A new ADR exists, is linked from this feature's Related Decisions, and is accepted before or alongside the code landing.

- [ ] ACC-006: (REQ-009) The full test matrix described in REQ-009 is green (`pytest -n auto`); the existing truly-missing-id regression tests in `tests/general/tools/test_update.py`/`test_edit.py`/`test_set_status.py`/`test_set_classification.py` continue to pass unchanged; and the nine existing raise-asserting content-validation tests (`test_update.py`'s whole-body and range-mode tests, `test_edit.py`'s stage-2 tests) are converted in Phase 120 (Task 120.140) to assert the new non-raising `ValidateResult(valid=False, ...)` shape with the file byte-identical, rather than a raised exception.

- [ ] ACC-007: (REQ-010) The combined-failure case (broken existing document AND invalid submitted content) returns `ValidateResult(valid=False, ...)` in whole-body `update` and `ParseFailureResult` in range `update` and `edit`, with nothing written to disk in all three; the mode-dependent precedence is documented in Design Notes and in the new ADR.

### Scope

#### Included

- `general/tools/update.py`: every `_update_<d>` adapter (12 domains), both whole-body and range-splice branches.

- `general/tools/edit.py`: every `_edit_<d>` adapter (12 domains).

- `general/tools/set_status.py`: every `_set_status_<d>` adapter (12 whole-body domains only -- the `adr` branch is out of scope, matching every prior ADR in this chain's exclusion of `adr`).

- `general/tools/set_classification.py`: every `_set_classification_<d>` adapter (12 domains).

- Reuse of the existing `general.models.ParseFailureResult` and `general.models.ValidateResult`/`ValidationErrorEntry` models -- no new result model is introduced.

- A new ADR documenting this decision.

- Docstring/description updates on all four tool files, `AGENTS.md`, and `docs/MCP.md` regeneration (via `specmgr mcp-docs`).

- Wording updates to the stale mechanism parentheticals in `general/prompts/repair.py` (description + module docstring), `general/data/general_repair_instructions.md`, `.opencode/skill/repair/SKILL.md`, `.opencode/agent/doc-repairer.md`, and `general/tools/_doc_paths.py` (module + `find_parse_failure` docstrings) -- preserving every phrase `tests/general/prompts/test_repair.py` pins.

- A `CHANGELOG.md` `[Unreleased]` entry (user-visible MCP tool-contract change).

- Test coverage across all four tools x 12 domains for both new branches plus the two regression guards (truly-missing id, happy path).

#### Explicitly Out Of Scope

- Giving `update`/`edit` the ability to actually repair (write a fix over) a document whose existing body fails to parse -- explicitly decided against during triage (see Decisions Made). The `repair` skill/`doc-repairer` subagent remain the only path to fix a broken document.

- Changing `general.tools._doc_paths.find_doc_path_by_id`'s documented skip-on-parse-failure scanning behavior, or `list_references`'s/`find_related`'s/`find_similar_text`'s own failure handling.

- The generic `delete` tool's identical `load_by_id`-against-a-broken-document crash -- it keeps raising exactly as today, consistent with every prior link in the 519d1206 chain that explicitly excluded `delete`; recorded as the chain's candidate case 5 in the new ADR rather than bundled into this feature.

- `adr`'s own `set_status` branch, `update_frontmatter`, `update_section`, and the `option_*` tools -- ADR has no whole-body replace/parse-failure-lookup mechanism by design and stays fully out of this feature.

- Fixing the underlying, out-of-this-repo's-control MCP client-side `isError: true` truncation defect itself -- this feature is a workaround within this repo's own tool contracts, same as every prior link in the 519d1206 chain.

### Dependencies

#### Depends On

- ADR 519d1206-4d2a-4500-9046-6db635209996 (the original non-raising-structured-result workaround decision).

- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (`set_status`'s `InvalidStatusResult` precedent).

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (`get_<d>`'s `ParseFailureResult` precedent and the `find_parse_failure`/`find_feat_parse_failure` helpers this feature reuses unchanged).

#### Blocks

- None known.

### Design Notes

**Phase discipline (standing user requirement, feat-150 2026-09-24, restated in feat-167).** Every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches) and exactly one Conventional Commit; the phase's docs sync travels inside that same commit. The new/converted tests travel with their code phase (Phase 110/120), and Phase 140 is the final ACC-walk verification. This replaces the original plan's single monolithic Phase 150 quality gate.

**Reuse, not new models.** `ParseFailureResult` (`error`/`path`/`id`) and `ValidateResult`/`ValidationErrorEntry` (`valid`/`errors`) already exist and are exercised in production by `get_<d>` and `validate` respectively. This feature is purely a matter of catching the right exception at the right point in each of the 48 adapter functions (4 tools x 12 domains) and returning the existing model -- no new pydantic model, no new MCP result shape.

**Where each branch goes, per tool:**

- `update._update_<d>`: Bug 1's catch wraps `load_<d>_by_id(...)` (both the whole-body branch and the range-splice branch each have their own `load_by_id` call site, inside the domain lock). Bug 2's catch wraps the `wrap_tool_errors(...)` block that validates the caller's new `content` -- pre-lock in whole-body mode, but INSIDE the lock, after `load_by_id` and `splice_body`, in range mode -- a pure presentation change in both modes; the resulting mode-dependent Bug-1/Bug-2 precedence is documented below and pinned by test (REQ-010).

- `edit._edit_<d>`: Bug 1's catch wraps `load_<d>_by_id(...)` (single call site per adapter, since `edit` holds the lock across the whole read -> match -> validate -> write sequence). Bug 2's catch wraps the stage-2 `wrap_tool_errors(...)` block that validates the edited body -- stage 1's OC-parity guards (`_match_and_replace`'s not-found/multiple-matches `ValueError`s) are untouched per REQ-004.

- `set_status._set_status_<d>`: Bug 1 only. Catch wraps `load_<d>_by_id(...)`. The existing pre-dispatch `_check_status_allowed`/`InvalidStatusResult` check is unaffected -- it already runs before any lock/load, so it composes cleanly with this feature's `load_by_id`-catch addition (an out-of-vocabulary status against a broken existing document still returns `InvalidStatusResult` first, since that check never reaches `load_by_id`).

- `set_classification._set_classification_<d>`: Bug 1 only. Catch wraps `load_<d>_by_id(...)`, mirroring `set_status`'s shape exactly.

**Bug-1/Bug-2 precedence (intentionally mode-dependent).** When both failure conditions hold at once (the target document's on-disk file fails to parse AND the submitted content fails validation), the observable result follows each adapter's existing execution order, which this feature does not reorder: whole-body `update` validates the submitted content before it takes the lock or loads the existing document, so it returns `ValidateResult(valid=False, ...)`; range `update` and `edit` load the existing document first, so they return `ParseFailureResult` (the invalid content is never reached). Reordering whole-body `update` to load-first would change lock timing on the common path for no user benefit, so the asymmetry is documented and pinned by tests instead of removed (REQ-010/ACC-007).

**`ValidateResult` is mirrored from `validate` exactly, not re-derived.** The Bug-2 branch catches `validate`'s own `_CAUGHT_EXCEPTIONS` tuple (`AssertionError`, `pydantic.ValidationError`, `yaml.YAMLError` -- the third unreachable for body-only content, which never parses a frontmatter block, but kept so the catch shape is uniform) and returns `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])` -- the same 300-char cap feat-110 established for `validate`, so the bounded-message contract is not re-opened on the `update`/`edit` surface. The plain caller-usage `ValueError`s (range coordinates, `edit`'s OC-parity guards) are never caught (REQ-004).

**`feat`'s divergent helper.** `feat.tools._paths.find_feat_parse_failure(base_dir, id_)` takes no `read_fn` (the folder name IS the id, so there is exactly one candidate path to check), unlike the shared `general.tools._doc_paths.find_parse_failure(base_dir, id_, read_fn)` the other 11 domains use. Each `_..._feat` adapter's catch block calls the feat-specific helper, exactly mirroring `get_feat.py`'s own existing branch.

**Implementation style: follow the existing per-adapter convention, not a shared abstraction.** Every adapter in `update.py`/`edit.py`/`set_status.py`/`set_classification.py` is already a largely verbatim, per-domain copy (explicitly called out as "verbatim port" in each file's own module docstring) rather than a shared parametrized helper. This feature follows that same convention: the `try`/`except XNotFoundError: ... find_parse_failure(...) ...` block is repeated per adapter (48 times total), not factored into a cross-cutting helper, to stay consistent with the codebase's established style and keep each domain's adapter independently readable/portable. A tiny, purely mechanical helper for the repeated 4-line catch-and-probe pattern may be considered during implementation if the duplication proves error-prone, but is not required by this plan.

**Interaction with feat-107-doc-cache.** No change to any cache-warming/invalidation call site -- the new branches only ever return early on a *failure* path, before any write or `read_<d>(path)` cache-warm call, so the cache-warming contract feat-107 established is untouched.

**Repair-artifact wording.** The `repair` MCP prompt (description + module docstring), its packaged instructions (`general/data/general_repair_instructions.md`), the `repair` OpenCode skill (`.opencode/skill/repair/SKILL.md`), and the `doc-repairer` agent (`.opencode/agent/doc-repairer.md`) all carry a mechanism parenthetical (that the adapters convert the parse failure into the domain's not-found error before anything is written) that this feature makes inaccurate -- the failure is now returned as a non-raising `ParseFailureResult`, not converted into the domain's not-found error. The normative claims those artifacts contain (`update`/`edit` cannot repair a broken document; never write the repair back through them) stay true and are the phrases `tests/general/prompts/test_repair.py` pins; Phase 130 (Task 130.110/130.120) rewords only the mechanism part. `general/tools/_doc_paths.py`'s module docstring (the "update/delete/set_status/set_classification/validate/list_references keep raising exactly as before" sentence -- after this feature only `delete`/`validate`/`list_references` still do) and `find_parse_failure`'s own docstring (now also called by the four generic mutation tools) are refreshed in the same task.

### Related Decisions

- 519d1206-4d2a-4500-9046-6db635209996 (ADR): the original decision to redesign `validate` as a non-raising, structured-result tool.

- b399f1ce-ed42-4929-b01c-7a57d18e8014 (ADR): extended the workaround to `set_status`'s invalid-status case via `InvalidStatusResult`.

- 9080b37c-82b3-4f63-81f1-79641d0bf14c (ADR): extended the workaround to `get_<d>`'s parse-failure case via `ParseFailureResult`, and the `find_parse_failure`/`find_feat_parse_failure` helpers this feature reuses unchanged.

- b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (ADR): case 4 of the 519d1206 chain -- the non-raising `ParseFailureResult`/`ValidateResult` branches for the four generic mutation tools (feat-170, GitHub issue #170).

### Task List

#### Phase 100: ADR

- [x] Task 100.100: Draft and create the new ADR (case 4 of the 519d1206 chain, after case 1 = 519d1206/`validate`, case 2 = b399f1ce/`set_status`, case 3 = 9080b37c/`get_<d>`) recording this decision, referencing GitHub issue #170, explicitly naming the two locked-in scope decisions (no repair capability; bundle all four generic mutation tools together), the `delete` exclusion (candidate case 5), the non-goals from the Scope section, and the mode-dependent Bug-1/Bug-2 precedence (REQ-010), and noting that it refines 519d1206's own "all keep raising" scope statement.

- [x] Task 100.110: Get the ADR to `accepted` status before or alongside the Phase 110/120 code landing, and record its UUID in this README's Related Decisions.

- [x] Task 100.120: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest, `specmgr adr-toc`), then exactly one Conventional Commit for the phase.

#### Phase 110: Bug 1 -- ParseFailureResult reuse (update, edit, set_status, set_classification x 12 domains)

- [x] Task 110.100: `general/tools/update.py` -- add the `XNotFoundError` -> `find_parse_failure`/`find_feat_parse_failure` -> `ParseFailureResult` branch to all 12 `_update_<d>` adapters (both whole-body and range-splice `load_by_id` call sites in each; the flat-file probe passes the domain's own `read_<d>` as `read_fn`, and the probed path passes `assert_within`, mirroring `get_<d>`'s branch).

- [x] Task 110.110: `general/tools/edit.py` -- same branch, all 12 `_edit_<d>` adapters.

- [x] Task 110.120: `general/tools/set_status.py` -- same branch, all 12 whole-body `_set_status_<d>` adapters (the `adr` branch stays untouched).

- [x] Task 110.130: `general/tools/set_classification.py` -- same branch, all 12 `_set_classification_<d>` adapters.

- [x] Task 110.140: Widen each tool's return-type union annotation (`_UpdateFrontmatter | ParseFailureResult`, etc.).

- [x] Task 110.150: Tests: the existing-broken-document -> `ParseFailureResult` case for all 12 domains x all four tools (per module's existing shape -- `test_update.py`/`test_set_status.py` carry `feat` in a separate case shape, and `test_set_classification.py`'s feat entry may be tightened from bare `Exception` to `FeatNotFoundError`), asserting the `error` text carries the same parse defect as the domain's `list_<d>` failed row (the `get_<d>` precedent) and that nothing is written to disk; confirm the existing truly-missing-id regression tests pass unchanged.

- [x] Task 110.160: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 120: Bug 2 -- ValidateResult reuse (update, edit only)

- [ ] Task 120.100: `general/tools/update.py` -- wrap the new-content validation block (whole-body: the pre-lock `wrap_tool_errors` block; range: the in-lock post-splice block) in `try`/`except` on `validate`'s own `_CAUGHT_EXCEPTIONS` tuple, returning `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])`.

- [ ] Task 120.110: `general/tools/edit.py` -- same treatment around the stage-2 post-edit validation block only; leave stage-1's and the pre-dispatch OC-parity guards untouched.

- [ ] Task 120.120: Widen `update`'s and `edit`'s return-type union annotations to include `ValidateResult`.

- [ ] Task 120.130: Tests: the invalid-new-content -> `ValidateResult(valid=False, ...)` case for all 12 domains for `update` (whole-body and range modes) and `edit`, asserting the 300-char-capped message and no write to disk; plus the combined-failure case (broken existing document + invalid content) returning `ValidateResult` in whole-body `update` but `ParseFailureResult` in range `update` and `edit` (REQ-010/ACC-007).

- [ ] Task 120.140: Convert the nine existing raise-asserting content-validation tests (`tests/general/tools/test_update.py` lines 1075/1088/1102 whole-body and 1292/1309/1319 range; `tests/general/tools/test_edit.py` lines 1207/1224/1248 stage-2) from `assertRaises(AssertionError/ValidationError)` to asserting the non-raising `ValidateResult(valid=False, ...)` return with the file byte-identical.

- [ ] Task 120.150: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 130: Docs

- [ ] Task 130.100: Update `update.py`/`edit.py`/`set_status.py`/`set_classification.py`'s module docstrings, `@mcp.tool()` `description=`, and function-level `Returns`/`Raises` sections for the new non-raising branches.

- [ ] Task 130.110: Reword the stale mechanism parentheticals (that the adapters convert the parse failure into the domain's not-found error) in `general/prompts/repair.py` (description + module docstring), `general/data/general_repair_instructions.md`, `.opencode/skill/repair/SKILL.md`, and `.opencode/agent/doc-repairer.md` to name the new non-raising `ParseFailureResult` branch -- preserving every phrase `tests/general/prompts/test_repair.py` pins (e.g. `structurally unable to repair`) and keeping that test module green unchanged.

- [ ] Task 130.120: Refresh `general/tools/_doc_paths.py`'s module docstring (the "update/delete/set_status/set_classification/validate/list_references keep raising exactly as before" sentence -- after this feature only `delete`/`validate`/`list_references` still do) and `find_parse_failure`'s docstring (now also called by the four generic mutation tools).

- [ ] Task 130.130: Update `AGENTS.md`'s `general/` package bullet (and any per-domain bullet referencing `update`/`edit`/`set_status`/`set_classification` semantics, including the `repair` prompt paragraph's mechanism wording).

- [ ] Task 130.140: Add the `CHANGELOG.md` `[Unreleased]` entry for the new non-raising branches (user-visible MCP tool-contract change).

- [ ] Task 130.150: Regenerate `docs/MCP.md` via `specmgr mcp-docs` and `docs/api/` + `docs/GENERATED.md` via `specmgr docs`; confirm no drift (the pre-commit hooks enforce both).

- [ ] Task 130.160: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest, `specmgr docs`, `specmgr mcp-docs`), then exactly one Conventional Commit for the phase (the phase's docs sync travels inside this same commit).

#### Phase 140: Final Verification

- [ ] Task 140.100: Walk every Acceptance Criterion (ACC-001..ACC-007) with concrete evidence (command + output).

- [ ] Task 140.110: Full quality gate green: ruff format/check, vulture, `pytest -n auto --cov=src --cov-report=`, `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` regeneration, `specmgr coverage-badge`; set this feature's frontmatter `status` to `done` and bump `updated`.

- [ ] Task 140.120: Exactly one Conventional Commit for the phase.

## Progress

### Current Status

**As of 2026-09-30**: Phases 100 (ADR) and 110 (Bug 1) done. Phase 100 created the case-4 chain ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f ("Extend the non-raising structured-result workaround to the generic mutation tools' failure cases") at `status: accepted` (listed in the regenerated `docs/adr/README.md` TOC, UUID recorded in Related Decisions). Phase 110 added the `XNotFoundError` -> `find_parse_failure`/`find_feat_parse_failure` -> `ParseFailureResult` branch to all 48 per-domain adapters (12 in each of `update` -- both whole-body and range-splice `load_by_id` sites --, `edit`, `set_status` -- the `adr` branch untouched --, and `set_classification`), widened the four tools' return-type union aliases and per-adapter annotations with `| ParseFailureResult`, and added the broken-document -> `ParseFailureResult` test coverage for all 12 domains x all four tools (plus the missing `feat` truly-missing-id regressions in `test_update.py`/`test_set_status.py` and the `test_set_classification.py` feat-entry tightening from bare `Exception` to `FeatNotFoundError`) -- 3800 tests green. Phases 120-140 (Bug-2 `ValidateResult` branch, docs sync, final ACC-walk) are pending.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-30T10:01:02.000Z - Phase 110 (Bug 1): ParseFailureResult branch added to all 48 adapters of the four generic mutation tools

Implemented REQ-001/REQ-002 (Bug 1) per the ADR b8c9bfea Decision Outcome items 1-2. In `general/tools/update.py` (24 `load_by_id` call sites -- both the whole-body branch and the range-splice branch of each of the 12 `_update_<d>` adapters, each inside its domain lock), `edit.py` (12 -- the single `load_by_id` per `_edit_<d>`, lock held across read -> match -> validate -> write), `set_status.py` (12 whole-body `_set_status_<d>`; the `adr` adapter stays byte-untouched), and `set_classification.py` (12 `_set_classification_<d>`): the `load_<d>_by_id(...)` call is now wrapped in `try`/`except <D>NotFoundError` (the domain's OWN not-found class); on catch the adapter probes `general.tools._doc_paths.find_parse_failure(base_dir, id_, read_fn=<domain's cache-backed read_<d>>)` for the 11 flat-file domains or `feat.tools._paths.find_feat_parse_failure(base_dir, id_)` (no `read_fn` -- the folder name IS the id) for `feat`, exactly mirroring each `get_<d>`'s own branch; a probe hit applies the same `_path_safety.assert_within(base_dir, failure_path)` defense-in-depth guard and returns `ParseFailureResult(error=..., path=str(failure_path.resolve()), id=id_)` (the existing `general.models` model, no new shape); a `None` probe re-raises the original `XNotFoundError` unchanged (REQ-002). Per the plan's Design Notes the catch-and-probe block is repeated per adapter (no shared cross-cutting helper). Return-type unions widened (Task 110.140): the `_UpdateFrontmatter`/`_EditFrontmatter`/`_SetStatusFrontmatter`/`_SetClassificationFrontmatter` aliases each gain `| ParseFailureResult` (so the `_ADAPTERS` dict and dispatcher annotations follow automatically), and every per-adapter annotation becomes `-> <D>Frontmatter | ParseFailureResult` (12 per tool file; `set_status`'s `adr` adapter and dispatcher stay as-is apart from the alias). No docstrings/`@mcp.tool()` descriptions were touched (Phase 130, REQ-006); no cache-warming/invalidation call site changed (Design Notes: feat-107 interaction). Tests (Task 110.150): each of the four general-tools test modules gained a module-local `_strip_pydantic_footer` copy (the 12-local-copies convention), a `_BROKEN_BODY` corruption constant (the `get_<d>` precedent's "no headings at all" body) plus its pinned `_CORE_DEFECT` substring, a dedicated `_ParseFailureCase` dataclass/case list, and a new test class -- `test_update.py`: `TestUpdateParseFailure` (5 methods; the 11 flat-file domains in a subTest loop over both whole-body and range modes, `feat` in its own separate case shape for both modes, plus the `feat` truly-missing-id regression this module lacked), `test_edit.py`: `TestEditParseFailure` (1 method, all 12 domains unified -- `feat`'s missing-id regression already existed here), `test_set_status.py`: `TestSetStatusParseFailure` (3 methods; 11-domain loop with a valid in-vocabulary status distinct from the created default so execution reaches `load_by_id` past the pre-dispatch `InvalidStatusResult` check, `feat` separate, plus the `feat` truly-missing-id regression this module lacked), `test_set_classification.py`: `TestSetClassificationParseFailure` (1 method, all 12 domains unified; the module's existing `feat` `_CASES` entry tightened from bare `Exception` to `FeatNotFoundError` as the plan allows, with the loop's dead `is Exception` guard replaced by an explicit `doc_type == "feat"` skip -- `feat`'s not-found needs a `feat-NNN-slug` id, covered by the dedicated test, now asserting `FeatNotFoundError`). Every broken-document case asserts `isinstance(result, ParseFailureResult)`, `result.id` == the document id, `result.path` == the resolved on-disk path, non-empty `result.error`, the list-row consistency invariant (`_strip_pydantic_footer(result.error) == _strip_pydantic_footer(list_<d>() failed row .error)` plus the `_CORE_DEFECT` substring present in both), and byte-identical on-disk file after the call (nothing written; the valid submitted content does not overwrite the corruption). All pre-existing regression tests (truly-missing id, raise-asserting content-validation, happy path, injection, `assert_within` spy) pass unchanged. Phase-end gate green: `ruff format --check` (1775 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings, no whitelist change needed), `pytest -n auto --cov=src --cov-report=` (3800 passed, up from 3790 baseline -- the 10 new test methods), `specmgr docs` (regenerated the four `docs/api/biz.dfch.specmgr.general.tools.{update,edit,set_status,set_classification}.md` files whose signature lines widened with the annotations -- this phase's docs sync; `docs/GENERATED.md` unchanged), `specmgr mcp-docs` (no drift -- no `@mcp.tool()` description/input schema changed). The phase's single Conventional Commit is reserved to the orchestrator (Task 110.160).

#### 2026-09-30T04:18:09.000Z - Phase 100 (ADR): case-4 chain ADR created and accepted

Created the new ADR through the MCP `create_adr` tool (per ADR 898bfcd0): UUID b8c9bfea-6dcf-4158-bfc5-4ec17abb842f, title "Extend the non-raising structured-result workaround to the generic mutation tools' failure cases", `status: accepted` from the start (all scope decisions were already locked in during triage -- no open design question). The ADR records the two locked-in scope decisions (no repair capability for `update`/`edit`; all four generic mutation tools bundled in this one feature), the `delete` exclusion (recorded as the chain's candidate case 5), the non-goals from the Scope section, the mode-dependent Bug-1/Bug-2 precedence (REQ-010), and that it refines 519d1206's own "all keep raising" scope statement. `specmgr adr-toc` regenerated `docs/adr/README.md` (the new ADR is listed with its id/title/status; a second run is a no-op -- no drift). The ADR's UUID is recorded in Related Decisions above, and the frontmatter `status` moved from `planning` to `progress` (implementation has started). Phase-end gate green: `ruff format --check` (1775 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings), `pytest -n auto --cov=src --cov-report=` (3790 passed), `specmgr adr-toc` (regenerated, no drift). The phase's single Conventional Commit is reserved to the orchestrator (Task 100.120).

#### 2026-09-29T19:51:28.000Z - Refined after plan review

Reviewed the plan against the source (`general/tools/update.py`/`edit.py`/`set_status.py`/`set_classification.py`/`_doc_paths.py`/`_splice.py`/`validate.py`, `feat/tools/_paths.py`/`_io.py`, `dec/tools/_io.py`, `get_dec.py`/`get_feat.py`, the three prior ADRs in the 519d1206 chain, the four general-tools test modules, `tests/general/prompts/test_repair.py`, `.pre-commit-config.yaml`, and the feat-150/163/167 plan conventions). Findings: two factual errors (the `docs/MCP.md` regeneration command; the claimed pre-lock placement of `update`'s range-mode validation block), six gaps (the nine existing raise-asserting tests Phase 120 breaks; the stale repair-artifact mechanism wording; the missing `CHANGELOG.md` entry; the missing per-phase gate/commit discipline; the undeclared `delete` exclusion; the unpinned `ValidateResult` message cap/caught tuple), and several precision items (mode-dependent Bug-1/Bug-2 precedence, probe `read_fn`/`assert_within` mirroring, chain numbering, test-shape notes, `edit` guard attribution, the new ADR's UUID record-back). All findings and their user-confirmed resolutions are recorded in the Requirements/Acceptance Criteria/Scope/Design Notes/Task List edits above and in the four new Decisions Made entries below.

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

#### 2026-09-29T19:51:28.000Z - Phase discipline: per-phase gate + one Conventional Commit, tests folded into code phases

Adopted the standing convention (feat-150 user requirement 2026-09-24, restated in feat-167) over the original single monolithic Phase 150: every phase ends with the full quality gate and exactly one Conventional Commit (docs sync inside that commit), the new/converted tests travel with their code phase (110/120), and Phase 140 is the final ACC-walk verification. The old Phase 150's checks are absorbed into the per-phase gates.

#### 2026-09-29T19:51:28.000Z - Repair-artifact mechanism wording updated in Phase 130 (normative guidance unchanged)

The `repair` prompt, its packaged instructions, the `repair` skill, and the `doc-repairer` agent all describe the pre-feature mechanism (the adapters convert the parse failure into the domain's not-found error) that this feature makes inaccurate. Decision: reword only that mechanism part (Task 130.110/130.120) to name the new non-raising `ParseFailureResult` branch, preserving every phrase `tests/general/prompts/test_repair.py` pins (the normative no-repair claims stay byte-identical), rather than leaving stale text or accepting the inaccuracy in the ADR. `general/tools/_doc_paths.py`'s docstrings are refreshed in the same task.

#### 2026-09-29T19:51:28.000Z - ValidateResult mirrored from validate exactly (caught tuple + 300-char cap)

The Bug-2 branch catches `validate`'s own `_CAUGHT_EXCEPTIONS` (`AssertionError`, `pydantic.ValidationError`, `yaml.YAMLError` -- the third unreachable for body-only content) and caps the single `errors[].message` via `snippet(..., max_chars=300)` exactly as `validate` does (feat-110), so the bounded-message contract is not re-opened on the `update`/`edit` surface; caller-usage `ValueError`s are never caught (REQ-003/REQ-004).

#### 2026-09-29T19:51:28.000Z - Accept and document the mode-dependent Bug-1/Bug-2 precedence (no reordering)

When the target document is broken AND the submitted content is invalid, whole-body `update` returns `ValidateResult` (it validates content pre-lock, before loading), while range `update` and `edit` return `ParseFailureResult` (they load first). Reordering whole-body `update` to load-first would change lock timing on the common path for no user benefit; the asymmetry is pinned by REQ-010/ACC-007 and tests instead of removed.

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
