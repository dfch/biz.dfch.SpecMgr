---
classification: null
created: '2026-09-29T15:14:11.057+02:00'
id: feat-170-update-edit-parse-failure
status: review
type: feat
updated: '2026-10-02T09:34:59.000+02:00'
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

- [x] ACC-001: (REQ-001/REQ-002) For every one of the 12 whole-body domains and all four tools (`update`, `edit`, `set_status`, `set_classification`), calling the tool against an id whose only matching on-disk file fails to parse returns a `ParseFailureResult` (never raises) whose `error` carries the same parse defect as the domain's `list_<d>` failed row for the same file (the testable consistency invariant every `get_<d>` already pins), while calling it against a genuinely absent id still raises the domain's `XNotFoundError` unchanged.

- [x] ACC-002: (REQ-003/REQ-004) For `update` and `edit`, submitting genuinely invalid new content against a healthy existing document returns `ValidateResult(valid=False, errors=[...])` (never raises) whose single `errors[].message` is capped exactly as the `validate` tool caps it (300 chars via `snippet`, feat-110), while every existing caller-usage `ValueError` path (bad id shape, unknown type, range-coordinate misuse, `edit`'s OC-parity guards -- pre-dispatch identical-input/empty-`old_str` and stage-1 match guards) still raises exactly as before.

- [x] ACC-003: (REQ-005) The `repair` skill/prompt's normative guidance (never write the repair back via `update`/`edit`) remains accurate and unchanged; the repair artifacts' stale mechanism parentheticals (the `repair` prompt's description and module docstring, its packaged instructions file, the `repair` skill, the `doc-repairer` agent) and `general/tools/_doc_paths.py`'s docstrings are reworded to name the new non-raising `ParseFailureResult` branch, and `tests/general/prompts/test_repair.py` stays green unchanged (its pinned phrases are preserved by the rewording).

- [x] ACC-004: (REQ-006/REQ-007) `update`/`edit`/`set_status`/`set_classification`'s docstrings, `@mcp.tool()` descriptions, and `AGENTS.md` accurately describe the new non-raising branches; `docs/MCP.md` regenerates cleanly via `specmgr mcp-docs` with no manual edits needed afterward.

- [x] ACC-005: (REQ-008) A new ADR exists, is linked from this feature's Related Decisions, and is accepted before or alongside the code landing.

- [x] ACC-006: (REQ-009) The full test matrix described in REQ-009 is green (`pytest -n auto`); the existing truly-missing-id regression tests in `tests/general/tools/test_update.py`/`test_edit.py`/`test_set_status.py`/`test_set_classification.py` continue to pass unchanged; and the nine existing raise-asserting content-validation tests (`test_update.py`'s whole-body and range-mode tests, `test_edit.py`'s stage-2 tests) are converted in Phase 120 (Task 120.140) to assert the new non-raising `ValidateResult(valid=False, ...)` shape with the file byte-identical, rather than a raised exception.

- [x] ACC-007: (REQ-010) The combined-failure case (broken existing document AND invalid submitted content) returns `ValidateResult(valid=False, ...)` in whole-body `update` and `ParseFailureResult` in range `update` and `edit`, with nothing written to disk in all three; the mode-dependent precedence is documented in Design Notes and in the new ADR.

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

- [x] Task 120.100: `general/tools/update.py` -- wrap the new-content validation block (whole-body: the pre-lock `wrap_tool_errors` block; range: the in-lock post-splice block) in `try`/`except` on `validate`'s own `_CAUGHT_EXCEPTIONS` tuple, returning `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])`.

- [x] Task 120.110: `general/tools/edit.py` -- same treatment around the stage-2 post-edit validation block only; leave stage-1's and the pre-dispatch OC-parity guards untouched.

- [x] Task 120.120: Widen `update`'s and `edit`'s return-type union annotations to include `ValidateResult`.

- [x] Task 120.130: Tests: the invalid-new-content -> `ValidateResult(valid=False, ...)` case for all 12 domains for `update` (whole-body and range modes) and `edit`, asserting the 300-char-capped message and no write to disk; plus the combined-failure case (broken existing document + invalid content) returning `ValidateResult` in whole-body `update` but `ParseFailureResult` in range `update` and `edit` (REQ-010/ACC-007).

- [x] Task 120.140: Convert the nine existing raise-asserting content-validation tests (`tests/general/tools/test_update.py` lines 1075/1088/1102 whole-body and 1292/1309/1319 range; `tests/general/tools/test_edit.py` lines 1207/1224/1248 stage-2) from `assertRaises(AssertionError/ValidationError)` to asserting the non-raising `ValidateResult(valid=False, ...)` return with the file byte-identical.

- [x] Task 120.150: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 130: Docs

- [x] Task 130.100: Update `update.py`/`edit.py`/`set_status.py`/`set_classification.py`'s module docstrings, `@mcp.tool()` `description=`, and function-level `Returns`/`Raises` sections for the new non-raising branches.

- [x] Task 130.110: Reword the stale mechanism parentheticals (that the adapters convert the parse failure into the domain's not-found error) in `general/prompts/repair.py` (description + module docstring), `general/data/general_repair_instructions.md`, `.opencode/skill/repair/SKILL.md`, and `.opencode/agent/doc-repairer.md` to name the new non-raising `ParseFailureResult` branch -- preserving every phrase `tests/general/prompts/test_repair.py` pins (e.g. `structurally unable to repair`) and keeping that test module green unchanged.

- [x] Task 130.120: Refresh `general/tools/_doc_paths.py`'s module docstring (the "update/delete/set_status/set_classification/validate/list_references keep raising exactly as before" sentence -- after this feature only `delete`/`validate`/`list_references` still do) and `find_parse_failure`'s docstring (now also called by the four generic mutation tools).

- [x] Task 130.130: Update `AGENTS.md`'s `general/` package bullet (and any per-domain bullet referencing `update`/`edit`/`set_status`/`set_classification` semantics, including the `repair` prompt paragraph's mechanism wording).

- [x] Task 130.140: Add the `CHANGELOG.md` `[Unreleased]` entry for the new non-raising branches (user-visible MCP tool-contract change).

- [x] Task 130.150: Regenerate `docs/MCP.md` via `specmgr mcp-docs` and `docs/api/` + `docs/GENERATED.md` via `specmgr docs`; confirm no drift (the pre-commit hooks enforce both).

- [x] Task 130.160: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest, `specmgr docs`, `specmgr mcp-docs`), then exactly one Conventional Commit for the phase (the phase's docs sync travels inside this same commit).

#### Phase 140: Final Verification

- [x] Task 140.100: Walk every Acceptance Criterion (ACC-001..ACC-007) with concrete evidence (command + output).

- [x] Task 140.110: Full quality gate green: ruff format/check, vulture, `pytest -n auto --cov=src --cov-report=`, `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` regeneration, `specmgr coverage-badge`; set this feature's frontmatter `status` to `done` and bump `updated`.

- [x] Task 140.120: Exactly one Conventional Commit for the phase.

## Progress

### Current Status

**As of 2026-10-01**: all five phases (100 ADR, 110 Bug 1, 120 Bug 2, 130 docs, 140 final
verification) done. Phase 100 created the case-4 chain ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f ("Extend the non-raising structured-result workaround to the generic mutation tools' failure cases") at `status: accepted` (listed in the regenerated `docs/adr/README.md` TOC, UUID recorded in Related Decisions). Phase 110 added the `XNotFoundError` -> `find_parse_failure`/`find_feat_parse_failure` -> `ParseFailureResult` branch to all 48 per-domain adapters (12 in each of `update` -- both whole-body and range-splice `load_by_id` sites --, `edit`, `set_status` -- the `adr` branch untouched --, and `set_classification`), widened the four tools' return-type union aliases and per-adapter annotations with `| ParseFailureResult`, and added the broken-document -> `ParseFailureResult` test coverage for all 12 domains x all four tools (plus the missing `feat` truly-missing-id regressions in `test_update.py`/`test_set_status.py` and the `test_set_classification.py` feat-entry tightening from bare `Exception` to `FeatNotFoundError`) -- 3800 tests green. Phase 120 added the Bug-2 `ValidateResult` branch: `update`'s 12 adapters' new-content validation blocks (pre-lock in whole-body mode, in-lock post-splice in range mode) and `edit`'s 12 adapters' stage-2 post-edit validation block are now wrapped in `try`/`except` on `validate`'s own imported `_CAUGHT_EXCEPTIONS` tuple, returning `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=snippet(str(ex), max_chars=300))])` (mirroring `validate` exactly; `set_status`/`set_classification` untouched); the `update`/`edit` return unions widen to `<frontmatter> | ParseFailureResult | ValidateResult`; the nine raise-asserting content-validation tests (plus six more that pinned the same old raising contract in `test_error_context.py`/`tests/regression/test_issue_27.py`/`test_issue_71.py`) are converted to the non-raising shape, and the new `TestUpdateValidateFailure`/`TestEditValidateFailure` classes cover invalid-new-content for all 12 domains (both `update` modes and `edit`'s stage 2) incl. the 300-char cap and the REQ-010/ACC-007 combined-failure precedence pins (`ValidateResult` in whole-body `update`, `ParseFailureResult` in range `update` and `edit`) -- 3813 tests green. Phase 130 (docs) done: the four generic mutation tools' module/function docstrings, `@mcp.tool()` descriptions, and the public-dispatcher `Returns`/`Raises` sections now document the new non-raising branches (REQ-006); the repair artifacts' stale mechanism parentheticals are reworded to name the new non-raising `ParseFailureResult` branch with every `tests/general/prompts/test_repair.py`-pinned phrase preserved (that module stays green unchanged -- REQ-005/ACC-003); `general/tools/_doc_paths.py`/`feat/tools/_paths.py` docstrings refreshed (Task 130.120); `AGENTS.md` and `server.py`'s module docstring synced (REQ-007); `CHANGELOG.md` `[Unreleased]` entry added; `docs/MCP.md`/`docs/api/` regenerated (idempotent). Phase 140 (final verification) done: all seven acceptance criteria walked with concrete per-ACC command + output evidence (the dated Updates entry above), every ACC checkbox ticked, and the full quality gate green -- `ruff format --check` (1775 files), `ruff check`, `vulture` (no findings), `pytest -n auto --cov=src --cov-report=` (**3813 passed**, TOTAL coverage 99%), `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` (each idempotent on second run, zero drift), `specmgr coverage-badge` (`docs/coverage.svg` byte-identical). Frontmatter `status` is `review` per the orchestrator's binding override of Task 140.110's `done` wording (PR-first closeout per the user's directive, the feat-163 precedent; `review` -> `done` happens at closeout after the PR is approved/merged); the phase's single Conventional Commit is reserved to the orchestrator; PR #175 is open
with CI green, and the round-1 post-implementation review fixes (feat-reviewer: no errors,
three non-blocking findings) are applied per the 2026-10-01T05:32:04.000Z Updates entry
below (full gate green, 3870 tests). The branch additionally merged `origin/dev`
(conflict-free, commit `a0ce76a`, 2026-10-01) bringing in feat-162-doc-cache-exception-footer
(GitHub issue #162, commit `221319d`) and, per feat-162's own plan's deliberately-deferred
Phase 900 (Task 900.100), adopted its outcome on this feature's own independently-introduced
surfaces: the four `_strip_pydantic_footer` test-helper copies deleted, the consistency
assertions tightened to plain byte-identity, the four tools' qualified docstring/description
clauses re-tightened to the byte-identical house wording, ADR
b8c9bfea-6dcf-4158-bfc5-4ec17abb842f amended in place via the ADR MCP tools, and the
CHANGELOG bullet re-tightened (3903 tests green, full gate, docs generators idempotent --
the 2026-10-01T21:42:01.000Z Updates entry below); PR #175 now also carries the feat-162
merge + Phase-900 adoption. The independent round-2 review (branch vs
`origin/dev` after the feat-162 merge + Phase-900 adoption) found no bugs with
the full gate green (3903 tests), and its single docs-only finding -- the
missing plain-`KeyError` sub-case for `update`/`set_classification`'s
`type="adr"` in AGENTS.md's `general/` bullet -- is fixed per the
2026-10-02T05:50:41.000Z Updates entry below.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-02T07:34:59.000Z - Repaired Updates entries to the feat-v1 single-paragraph schema (doc-repairer)

The round-2 verification surfaced that this plan README had been failing the feat-v1 schema
(`UpdateEntry.content: MarkdownParagraph` -- exactly one paragraph per `####` entry) since
the Phase-140 closeout (commit a5a7d4e): the Phase-140, Round-1, and Phase-900 entries
carried extra paragraphs and/or bullet lists, and the new round-2 entry inherited the
same multi-paragraph shape, so `get_feat`/`parse_feat` returned the non-raising
`ParseFailureResult` (`text left over after processing all fields`) and `list_feat`
showed the `<failed to parse>` marker for this feature. Repaired via the `repair`
skill / `doc-repairer` subagent: the four violating entries (`2026-10-02T05:50:41.000Z`,
`2026-10-01T21:42:01.000Z`, `2026-10-01T05:32:04.000Z`, `2026-10-01T02:21:39.000Z`) were
reflowed into single physical paragraphs -- blank lines removed, the Phase-900 entry's
five and the Phase-140 entry's seven `- ` bullet markers stripped with items joined by
a single space, plus one latent join in the Round-1 entry where a soft-wrapped line
starting with a `+ ` CommonMark bullet marker interrupted its Gate paragraph; every word
preserved (the three pre-existing entries verified character-identical to their pre-repair
form after whitespace normalization), all H4 headings byte-identical, newest-first order
intact, frontmatter untouched by the repair. Post-repair `get_feat` parses the full
document (10 Updates + 7 Decisions Made entries) and the `list_feat` row for this feature
carries its resolved id/title/status with `error: null`; the full gate re-ran green
(3903 tests). Observation, no action (out of scope): the worktree's feat base directory
contains 61 other pre-existing feat documents that fail to parse, several likely for the
same multi-block-entry reason -- a candidate for a separate repo-wide sweep.

#### 2026-10-02T05:50:41.000Z - Round 2 post-merge review: no bugs; AGENTS.md KeyError clause added (docs-only fix)

Round-2 independent review of the branch vs `origin/dev` (33 files, +3266/-655,
merge-base `221319d`) after the feat-162 merge + Phase-900 adoption: **no bugs
found**. Verified: the 48 per-domain adapter branch counts per tool (`update`
24 `ParseFailureResult` + 24 `ValidateResult`, `edit` 12 + 12, `set_status` 12,
`set_classification` 12); the parse-failure probe's catch set is identical to
`list_<d>`'s `DEFAULT_ERROR_TYPES` and its `read_fn` is the same cache-backed
reader, so the byte-identical-to-`list_<d>`-failed-row `error` invariant is
structural, not merely asserted; REQ-010's mode-dependent precedence placement
(whole-body `update` validates pre-lock, so `ValidateResult` wins on the
combined broken-document + invalid-content input; range `update`/`edit` load
first, so `ParseFailureResult` wins; `set_status`'s `InvalidStatusResult` check
runs pre-dispatch, first); every caller-usage `ValueError` still raises and
nothing is written on any failure path; both behavioral changes (the MCP
contract now returns non-raising structured results on previously-raised cases,
and the mode-dependent result type for that combined input) are intentional and
documented; ADR `b8c9bfea-6dcf-4158-bfc5-4ec17abb842f` is `status: accepted`
and listed in the regenerated TOC; the repair artifacts' pinned phrase
`structurally unable to repair` is preserved; zero `_strip_pydantic_footer`
copies remain repo-wide. The one low-severity, non-blocking finding, fixed this round (docs-only):
AGENTS.md's `general/` package bullet summarized the four tools' still-raising
set without the `type="adr"` sub-case for `update`/`set_classification` -- a
well-formed UUID id PASSES the id-shape validation (`validate_id` accepts `adr`
as a UUID-shaped domain), so those two tools raise the plain `KeyError` from
the dispatch-table lookup instead of a `ValueError`; the outcome is a
direct-Python-caller-only one, unreachable through the server's 12-value `type`
enum, and each tool's own `Raises` docstring and `docs/MCP.md` were already
accurate since round 1 -- the bullet now carries the clarifying clause (one
edit to AGENTS.md, zero executable-code changes). The second review item was a
process observation only: the frontmatter `status: review` with every task
checked is the recorded, binding orchestrator override for PR-first closeout
(see the 2026-10-01T02:21:39.000Z entry), not a defect. Gate (full, all green): `ruff format --check` (1780 files already formatted) +
`ruff check` (all checks passed) + `vulture src/ whitelist.py --min-confidence
60` (no findings) + `pytest -n auto --cov=src --cov-report=` (**3903 passed**
in 70.23s; coverage TOTAL 12346 statements, 121 missing, 99%) + `specmgr docs`
/ `specmgr mcp-docs` / `specmgr adr-toc` each run once, idempotent (`git
status --short` after each shows only the then-uncommitted `AGENTS.md` change
-- this README entry is written after the gate, so the final diff is exactly
`AGENTS.md` + this plan README, nothing else). No commit, no push (the work
stays uncommitted on this branch for the orchestrator).

#### 2026-10-01T21:42:01.000Z - Merged origin/dev (feat-162, issue #162) and adopted its outcome (feat-162 Phase 900 sweep)

Conflict-free merge of `origin/dev` (commit `a0ce76a`) brought in feat-162-doc-cache-exception-footer (GitHub issue #162, commit `221319d`): `DocCache`'s `_fresh_exception` exception reconstruction is now str-faithful, preserving the trailing pydantic documentation footer on warm re-raises. That converts the qualified error-text consistency invariant this feature had independently adopted (its own copy of the same language, which feat-162's sweep could not reach) into the simple byte-identical invariant, and feat-162 had re-tightened all of its own surfaces (amended ADR 9080b37c in place, the 12 `get_<d>` files, `parse_failure_result.py`, `_doc_paths.py`, `feat/tools/_paths.py`, the repair artifacts, AGENTS.md, CHANGELOG, server.py, and its 12 `_strip_pydantic_footer` test-helper copies). The auto-merged docs converged via fresh regeneration, and 3903 tests were green on the merged tree before this sweep. This entry records the sweep feat-162's own plan deliberately deferred to this branch (its Phase 900, Task 900.100 -- "Once feat-170-update-edit-parse-failure's own branch/worktree has rebased onto a `dev` that includes this feature, sweep its own, independently-introduced copy of the same qualified language"): `tests/general/tools/test_update.py`/`test_edit.py`/`test_set_status.py`/`test_set_classification.py`: the four module-local `_strip_pydantic_footer` helper copies deleted (the repo-wide convention post-feat-162 is zero copies -- these were the last four of the sixteen ever carried), every consistency assertion tightened from `assertEqual(_strip_pydantic_footer(x.error), _strip_pydantic_footer(failed[0].error))` to plain `assertEqual(x.error, failed[0].error)`, and the Option-B inline comments dropped (the re-tightened `test_get_<d>.py` comment shape the assertion now sits under already matched this module's existing `_CORE_DEFECT`-defect comment, which was kept, along with every other assertion, untouched); `test_edit.py`'s now-unused `import re` also removed (the other three modules keep `re` for their own `re.fullmatch` pins). `src/biz/dfch/specmgr/general/tools/update.py`/`edit.py`/`set_status.py`/`set_classification.py`: each module docstring's "Non-raising failure channels" clause, each `@mcp.tool()` `description=` string's ParseFailureResult clause, and each public dispatcher's `Returns` docstring clause reworded from the qualified language to the byte-identical house wording (docstrings/descriptions only -- zero executable-code changes; `ruff format` reported all eight files already unchanged). ADR `b8c9bfea-6dcf-4158-bfc5-4ec17abb842f`: amended IN PLACE via the specmgr ADR MCP tools (pre-checked: `specmgr://config` resolves `adr.base_dir` to this worktree's `docs/adr`, `list_adr` returned all 39 ADRs, `specmgr_get_adr` read the current body). Decision Outcome item 2's qualified sentence replaced by the byte-identical invariant naming feat-162/issue #162 as the fix (mirroring how feat-162 amended ADR 9080b37c's own item 3 in place, including the "not merely the same defect modulo that footer" close); Confirmation (a)'s matching clause reworded the same way (mirroring 9080b37c's amended Confirmation, cross-referencing this ADR's own Decision Outcome item 2); a new `More Information` bullet appended recording the close-out (shape/voice mirrored from the bullet feat-162 added to 9080b37c's own `More Information`, without that bullet's intentional historical "Option B, 2026-09-26" label -- the sweep grep's only-allowed-hit criterion reserves that label to 9080b37c's record). No dangling "and its qualification" cross-reference existed in the outcome text to drop. Frontmatter `status: accepted`/`version: 1.0.0` untouched (wording-precision amendment in place, not a new decision -- feat-162's own precedent); `specmgr_validate_adr` returns true afterwards. `CHANGELOG.md`: the `[Unreleased]` `### Changed` ParseFailureResult bullet's qualified clause ("identical field path and cause; the trailing pydantic documentation line may differ by read order/cache state -- Option B, 2026-09-26, follow-up issue #162") re-tightened to the house wording (byte-identical ... including the trailing pydantic documentation line -- fixed by feat-162-doc-cache-exception-footer, GitHub issue #162). feat-162's own already-re-tightened `[Unreleased]` `### Fixed` section and the `[0.34.0]` re-tightened entries untouched. `AGENTS.md`/`src/biz/dfch/specmgr/server.py`: post-merge grep showed zero retired-phrase hits in both (this feature's Phase-130 lines there carried no Option-B clause); re-verified after the sweep -- both unchanged. Retired-phrase sweep grep (`grep -rn "Option B, 2026-09-26\|follow-up issue #162\|not byte-equal\|may differ by read order" src/ tests/ docs/ .opencode/ AGENTS.md CHANGELOG.md`) now returns exactly one hit: feat-162's intentional historical bullet in ADR 9080b37c's `More Information`. `grep -rn "_strip_pydantic_footer" src/ tests/ docs/` returns zero hits repo-wide. This plan README itself still carries two qualified-language hits, both plan-time records rather than current-state text -- REQ-001 in the Requirements section (written before feat-162 existed) and the dated Phase-130 Updates entry below -- left untouched per the immutable-record convention. Gate: `ruff format` on the eight touched Python files (8 files left unchanged) + `ruff format --check` (1780 files already formatted) + `ruff check` (all checks passed) + `vulture src/ whitelist.py --min-confidence 60` (no findings) + `pytest -n auto --cov=src --cov-report=` (3903 passed in 68.90s -- the assertion swaps add/remove no tests; re-run after the sweep's final tree state) + `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` each run twice (second pass a byte-identical no-op: md5-verified against the first pass's output, `git status` unchanged; `docs/adr/README.md`'s regenerated TOC content equals the committed one) + `specmgr coverage-badge` second run byte-identical (md5-verified) and equal to the committed badge (99% coverage). No commit, no push (the work stays uncommitted on this branch for the orchestrator).

#### 2026-10-01T05:32:04.000Z - Round 1 post-implementation review fixes applied (feat-reviewer)

Round-1 post-implementation review (feat-reviewer) verdict: no errors, three non-blocking
findings -- all three fixed this round (the feat-163 round-fix convention: fixes + one
dated Updates entry + Current Status refresh, no new task phase, no renumbering,
frontmatter `status` stays `review`). **Finding 1 (GAP) -- pin the `InvalidStatusResult`-first precedence.** The documented
precedence (an out-of-vocabulary `status` against a broken existing document still
returns `InvalidStatusResult` first, since that pre-dispatch check never reaches
`load_by_id` -- `set_status.py` module docstring, this plan's Design Notes
`set_status._set_status_<d>` bullet, ADR b8c9bfea Option 4 Pros) was structurally
guaranteed but pinned by no test: the existing out-of-vocabulary tests
(`test_set_status.py` whole-body at ~line 726, ADR at ~line 897) ran only against
healthy documents. Fixed in `tests/general/tools/test_set_status.py`: two new methods
in `TestSetStatusParseFailure` --
`test_out_of_vocabulary_status_against_broken_document_returns_invalid_status_result_first`
(subTest loop over the module's existing `_CASES` data: all 11 flat-file whole-body
domains) and
`test_feat_out_of_vocabulary_status_against_broken_document_returns_invalid_status_result_first`
(the module's own separate `feat` case shape, folder + `README.md`) -- each seeds a
healthy document via the domain's own `create_<d>`, corrupts its on-disk file with the
module's existing Phase-110 `_BROKEN_BODY` constant, calls the public `set_status` with
the new universally-out-of-vocabulary constant `_UNIVERSALLY_INVALID_STATUS`
(`"not-a-status"` -- outside every domain's closed set, incl. ADR's fixed set and its
`"superseded by ..."` pattern), and asserts the non-raising `InvalidStatusResult`
(mirroring the existing out-of-vocab tests' assertion shape: `valid=False`, `type`,
`status`, `allowed_values` = the domain's own sorted closed set, exact `message`
wording, file byte-unchanged -- never asserting `ParseFailureResult`). Also added the
`feat` domain's `_FEAT_ALLOWED_STATUSES` import (the module had none). **Finding 2 (INCONSISTENCY) -- `set_classification`'s unsupported-`type` prose claimed
`ValueError`; the code raises `KeyError`.** The one unsupported `type` that passes
`validate_id` (`type="adr"`, a well-formed UUID -- `adr` is in `_path_safety`'s
UUID-shaped domain set) reaches the `_ADAPTERS` dispatch-table lookup, which has no
`adr` entry, and raises the plain `KeyError` -- exactly what the pre-existing
`test_adr_type_is_not_supported` pins (unreachable through the server: the 12-value
MCP `type` enum; a direct-Python-caller outcome only). Per-file audit of the current
`@mcp.tool()` description and public-dispatcher `Returns`/`Raises` against the code:
`edit.py` accurate (no change -- its prose already names the explicit pre-dispatch
`ValueError` for an unknown or `adr` `type`, REQ-004/D4, matching the code's own
`if type not in _ADAPTERS` guard); `set_status.py` accurate (no change -- `_ADAPTERS`
covers all 13 types incl. `adr`, so the KeyError outcome is unreachable there);
`update.py` module docstring already correct and description accurate (no
unsupported-`type` clause), but the public-dispatcher `Raises` section omitted the
`KeyError` -- fixed (new `KeyError` entry echoing the module docstring's wording);
`set_classification.py` inaccurate in three prose places -- fixed the description
(`"or an unsupported `type` is a `ValueError` raised before any file access"` ->
`"or an unknown `type` is a `ValueError` raised before any file access; `type="adr"`
passes the id validation (a well-formed UUID id) and raises the plain `KeyError`
inherited from the dispatch-table lookup instead"`), the docstring's Safety paragraph
(same correction in RST), and the `Raises` section (ValueError clause narrowed to
"unknown document type" + new `KeyError` entry) -- plus the dispatcher's adjacent
inline comment carrying the same false clause (judgment call: the audit surface was
the description/`Returns`/`Raises`, but leaving a same-file contradiction next to the
fixed paragraphs was not an option). No executable code changed. Docs regenerated:
`specmgr mcp-docs` -> `docs/MCP.md` (only the `set_classification` entry's index row +
detail section changed), `specmgr docs` -> `docs/api/` (only
`biz.dfch.specmgr.general.tools.update.md` and
`biz.dfch.specmgr.general.tools.set_classification.md` changed; `edit.py`'s
import-line change is not rendered into its module page, so `edit.md` is untouched). **Finding 3 (SMELL) -- 36x duplicated cap literal `max_chars=300` instead of
`validate`'s named constant.** The plan prescribed the literal (REQ-003: "via
`snippet(..., max_chars=300)`"), so the implementation was plan-conformant; this round
tightens the "mirror `validate` exactly" to the total without changing the contract:
`update.py` and `edit.py` now extend their existing `from .validate import
_CAUGHT_EXCEPTIONS` line with `_MAX_VALIDATE_ERROR_CHARS`, and every
`snippet(str(ex), max_chars=300)` site became
`snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)` -- grep-verified 36 sites
before (24 in `update.py` + 12 in `edit.py`), 0 `max_chars=300` left after. No
behavior change (same value, 300); `validate.py`, the test modules (they already
import the constant for their cap assertions), and the docstrings ("capped at 300
chars" -- still true) untouched. **Gate (full, all green):** `ruff format` (5 touched files left unchanged) +
`ruff format --check` (5 files already formatted) + `ruff check` (all checks passed) + `vulture src/ whitelist.py --min-confidence 60` (no findings -- the imported
constant is used in the same files, no whitelist handling needed) + `pytest -n auto
--cov=src --cov-report=` (**3870 passed** = 3868 baseline + the 2 new Finding-1 test
methods; TOTAL coverage 99%, 12336 statements / 121 missing) + `specmgr docs` +
`specmgr mcp-docs` (second runs byte-identical: md5 of the whole `docs/` *.md tree
compared before/after) + `specmgr coverage-badge` (`docs/coverage.svg` md5
`04811661ad416679c97e2396527e8c43` identical before and after both runs -- badge
unchanged at 99%, file not in the diff).

#### 2026-10-01T02:21:39.000Z - Phase 140 (Final Verification): ACC walk complete (ACC-001..ACC-007 all met); full gate green (3813 tests); status -> `review` per orchestrator override

Task 140.100 (ACC walk, concrete evidence per ACC; feature base = d2f9a57, the commit before 7257138): **ACC-001 met.** `uv run --frozen pytest tests/general/tools/test_update.py::TestUpdateParseFailure tests/general/tools/test_edit.py::TestEditParseFailure tests/general/tools/test_set_status.py::TestSetStatusParseFailure tests/general/tools/test_set_classification.py::TestSetClassificationParseFailure -v` -> `10 passed, 57 subtests passed in 7.17s` (57 = update 11 flat domains x 2 modes + feat x 2 modes, edit 12 domains, set_status 11 + feat, set_classification 12; every case asserts the `ParseFailureResult` shape, the list-row consistency invariant, and byte-identical file). Truly-absent ids still raise: the existing/new unknown-id regression methods (`TestUpdateWholeBody::test_raises_domain_not_found_for_unknown_id`, `TestUpdateRange::test_range_mode_raises_domain_not_found_for_unknown_id`, `TestUpdateParseFailure::test_feat_missing_id_still_raises_domain_not_found`, `TestEditDomainNotFound`, `TestEditInvalidId`, `TestSetStatusWholeBodyDomains::test_unknown_id_raises_domain_not_found`, `TestSetStatusAdr::test_unknown_id_raises_adr_not_found`, `TestSetStatusParseFailure::test_feat_missing_id_still_raises_domain_not_found`, `TestSetClassificationWholeBodyDomains::test_unknown_id_raises_domain_not_found` + `::test_feat_unknown_id_raises_not_found`) -> `10 passed, 128 subtests passed in 7.13s`. **ACC-002 met.** `TestUpdateValidateFailure` + `TestEditValidateFailure` + the eight converted raise-asserting methods (`TestUpdateWholeBody`'s `test_status_not_settable_through_update_returns_validate_failure_and_leaves_file_byte_identical`/`test_structural_failure_returns_validate_failure_and_leaves_file_byte_identical`/`test_field_validation_failure_returns_validate_failure_and_leaves_file_byte_identical`, `TestUpdateRange`'s `test_range_deleting_the_h1_returns_validate_failure_and_leaves_file_untouched`/`test_range_producing_out_of_vocabulary_value_returns_validate_failure_and_leaves_file_untouched` -- the last carrying 2 of the plan's nine `assertRaises` sites --, `TestEditInvalidResult`'s `test_deleting_mandatory_h1_returns_validate_failure_file_byte_unchanged`/`test_edit_producing_field_error_returns_validate_failure_file_byte_unchanged`/`test_replace_all_invalid_edit_returns_validate_failure_file_byte_unchanged`) -> `21 passed, 184 subtests passed in 17.39s`. Live cap demo through the real tool (throwaway script, `update` on a req document with a duplicate-H1 body whose unmatched remainder exceeds the parser's own snippet cap): `type=ValidateResult valid=False n_errors=1 len=315 endswith_suffix=True` -- i.e. the test's `assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))` (300 + 16) and suffix assertions hold on real output. Caller-usage `ValueError` paths unchanged and still raising: `TestUpdateRange` (incl. the five range-coordinate misuse tests), `TestMatchStageUnit`, `TestEditPublicGuards`, `TestEditUnsupportedType` -> `31 passed in 19.04s`. **ACC-003 met.** `uv run --frozen pytest tests/general/prompts/test_repair.py -v` -> `21 passed in 1.38s`. The test module is byte-unchanged across the whole feature: `git log --oneline d2f9a57..HEAD -- tests/general/prompts/test_repair.py` (no commits) and `git diff d2f9a57..HEAD -- tests/general/prompts/test_repair.py | wc -c` -> `0` (likewise `0` against 3a9743c). All four reworded repair artifacts carry the new mechanism wording (`returns the non-raising`/`non-raising ParseFailureResult` in `general/prompts/repair.py`, `general/data/general_repair_instructions.md`, `.opencode/skill/repair/SKILL.md`, `.opencode/agent/doc-repairer.md`) and preserve the phrase `test_repair.py` pins (`assertIn("structurally unable to repair", ...)` at its line 103). **ACC-004 met.** Occurrence greps in the four tool files (docstrings + `description=` + annotations): `update.py` ParseFailureResult=45/ValidateResult=46, `edit.py` 32/33, `set_status.py` 32/0, `set_classification.py` 32/0; inside the `@mcp.tool()` `description=` string itself: ParseFailureResult=1 in all four, ValidateResult=1 in update/edit, 0 in set_status/set_classification (correct -- Bug 1 only). `AGENTS.md`'s case-4 sentence is present (lines 550-552: "b8c9bfea-6dcf-4158-bfc5-4ec17abb842f, case 4 of the ADR 519d1206 ... returns the non-raising ..."). `uv run --frozen specmgr docs` + `specmgr mcp-docs` + `specmgr adr-toc` run twice each: `git status --short` empty after both passes (zero drift, no manual edits needed). **ACC-005 met.** `docs/adr/b8c9bfea-6dcf-4158-bfc5-4ec17abb842f-extend-the-non-raising-structured-result-workaround-to-the-g.md` exists with frontmatter `status: accepted` (`date: '2026-09-30'`); the UUID is recorded in this README's Related Decisions (line 178) and the regenerated `docs/adr/README.md` TOC carries the entry (lines 116-117); `specmgr adr-toc`'s second run was a no-op (idempotent, above). **ACC-006 met.** Full suite `uv run --frozen pytest -n auto --cov=src --cov-report=` -> `3813 passed in 60.58s` (exactly the Phase-130 baseline -- no test drift; TOTAL coverage 99%). The two test modules' evolution over the feature: `git diff d2f9a57..HEAD --stat -- tests/general/tools/test_update.py tests/general/tools/test_edit.py` -> `test_edit.py | 315 ++++++--`, `test_update.py | 530 ++++++++`, `2 files changed, 761 insertions(+), 84 deletions(-)`. The four modules' unknown-id regression tests and the nine converted methods are green (ACC-001/ACC-002 runs above). **ACC-007 met.** `uv run --frozen pytest tests/general/tools/test_update.py -k "combined_failure" tests/general/tools/test_edit.py -k "combined_failure" -v` -> `5 passed, 65 deselected, 34 subtests passed in 4.25s`: whole-body `update` (11 flat + feat) returns `ValidateResult(valid=False, ...)`; range `update` (11 flat + feat) and `edit` (12) return `ParseFailureResult`; nothing written in any case. The mode-dependent precedence is documented in Design Notes ("Bug-1/Bug-2 precedence (intentionally mode-dependent)") and in the ADR (Decision Outcome item 4, line 50). Task 140.110 (full gate): all green -- `uv run --frozen ruff format --check` (1775 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no findings), `uv run --frozen pytest -n auto --cov=src --cov-report=` (3813 passed, TOTAL 99%), `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` (each run twice; `git status` clean after the second pass -- idempotent), `uv run --frozen specmgr coverage-badge` (rewrote `docs/coverage.svg` at 99% coverage; md5 `04811661ad416679c97e2396527e8c43` byte-identical before and after, `git status` clean). Frontmatter `updated` bumped to `2026-10-01T04:21:39.000+02:00`. **Orchestrator override (binding):** the frontmatter `status` was set to `review`, NOT `done` as this task's text says -- the user's directive for this feature is PR-first closeout (implement -> `review` -> open PR -> `done` after approval/merge, the feat-163 precedent), so the plan record reflects what was actually done. Task 140.120: the phase's single Conventional Commit is reserved to the orchestrator (no commit made in this phase).

#### 2026-10-01T00:35:13.000Z - Phase 130 (Docs): docstrings/descriptions/AGENTS.md/server.py synced to the new non-raising branches; docs regenerated; gate green (3813 tests)

Implemented REQ-005/REQ-006/REQ-007 (Tasks 130.100..130.150) -- docs sync only, zero executable-line changes (verified by a per-line self-audit: all 319 changed lines in the four tool files are inside docstrings or `description=` string literals, and `git diff` vs `git diff -w` on every touched file shows no pure-whitespace line changes). (1) Task 130.100: `general/tools/update.py`/`edit.py`/`set_status.py`/`set_classification.py` -- each module docstring gains a "Non-raising failure channels" section (update/edit: the `ParseFailureResult` branch on the `load_by_id` `XNotFoundError` catch -- probe via `find_parse_failure`/`find_feat_parse_failure` with the domain's own `read_<d>` + `assert_within` mirroring, `error` = the same parse defect as the `list_<d>` failed row modulo the Option B 2026-09-26 trailing-pydantic-line qualification / follow-up issue #162 -- plus the `ValidateResult(valid=False, ...)` branch for content-validation failure, 300-char-capped `errors[].message` via `snippet` (feat-110), the intentional mode-dependent Bug-1/Bug-2 precedence (REQ-010), and every still-raising caller-usage `ValueError` named; set_status/set_classification: the `ParseFailureResult` branch only, with set_status noting its `InvalidStatusResult` check still runs pre-lock/pre-load first and the `adr` adapter stays raise-based); each `@mcp.tool()` `description=` extended with the same branches in the house phrasing (`get_dec`'s parse-failure wording, `set_status`'s invalid-status wording); each public dispatcher's function docstring `Returns` union widened (`| ParseFailureResult [| ValidateResult]`) with the failure shapes described, and `Raises` kept to the still-raising cases only (truly-absent id -> domain's `XNotFoundError`; caller-usage `ValueError`s) -- the now-obsolete `AssertionError`/`pydantic.ValidationError` Raises entries and the "propagate uncaught" mechanism sentences are reworded accordingly; one short failure-returns sentence added to each file's canonical `_req` adapter docstring (the one all sibling adapters cross-reference), no per-adapter changes beyond that. (2) Task 130.110: the stale mechanism parentheticals (old: the adapters "convert the parse failure into the domain's not-found error before (anything is) written"; new: they "re-parse the existing document before it can write anything and, for a broken one, return the non-raising `ParseFailureResult` instead of writing or raising -- a truly-absent id still raises the domain's not-found error") reworded in `general/prompts/repair.py`'s module docstring, `general/data/general_repair_instructions.md` (the top note AND step 5, which now also says `get_$type` with `raw=True` returns the non-raising parse-failure result instead of raw text), `.opencode/skill/repair/SKILL.md` (step 2), and `.opencode/agent/doc-repairer.md` (intro paragraph); the `repair` prompt's `@mcp.prompt(description=)` string carried no mechanism claim (only the normative "structurally unable to repair" sentence), so it is unchanged; every `tests/general/prompts/test_repair.py`-pinned phrase preserved -- `uv run --frozen pytest tests/general/prompts/test_repair.py -v`: 21 passed, test module untouched. (3) Task 130.120: `general/tools/_doc_paths.py` module docstring -- the "``update``/``delete``/``set_status``/``set_classification``/``validate``/``list_references`` keep raising exactly as before" sentence is replaced with "of the generic id-resolving tools, only ``delete``, ``validate``, and ``list_references`` keep raising exactly as before on a broken target -- ``update``/``edit``/``set_status``/``set_classification`` now return the non-raising ``ParseFailureResult`` via this probe on their own ``XNotFoundError`` catch (feat-170, issue #170, ADR b8c9bfea, case 4 of the 519d1206 chain)"; `find_parse_failure`'s docstring now also names the four generic mutation tools' per-domain adapters as callers (same `read_fn`/`assert_within` mirroring); the feat twin `feat/tools/_paths.py::find_feat_parse_failure` carried the identical get-only claim and was refreshed in the same pass (plan named `_doc_paths.py`; the twin was verified stale -- included). (4) Task 130.130: `AGENTS.md` -- the `general/` package bullet's `update` clause now carries the consolidated two-failure-channels sentence (covering all four tools: `ParseFailureResult` for existing-but-broken targets, `ValidateResult` for update/edit content-validation failures, the still-raising caller-usage `ValueError`s, set_status's pre-lock/pre-load `InvalidStatusResult`, nothing written); the `validate` sentence reworded from "unlike every other generic tool here, it never raises for a content-validation failure" to "it is the one generic tool here whose entire surface is non-raising structured results" with the four mutation tools' narrower non-raising branches noted; the `repair` prompt paragraph's mechanism parenthetical reworded to the new branch (normative "no specmgr MCP tool can return the raw content ..." / "structurally unable to repair" claims intact); sweep of the rest of `AGENTS.md` (all per-domain bullets, `get_<d>`/`list_<d>` sentences, feat-27/107 paragraphs) found no other stale raise/mechanism claim about the four tools -- per-domain bullets' "updates go through the generic `update` tool" sentences stay true unchanged. (5) Task 130.130 item 5: `server.py` module docstring -- its `validate` sentence had the same "unlike every other generic tool above, it never raises for a content-validation failure" inaccuracy (fixed identically), and its parse-failure channel paragraph (the case-3 record) now ends with the case-4 extension sentence (the four mutation tools' `ParseFailureResult` branch + update/edit's `ValidateResult` branch); the `update`/`edit`/`set_status`/`set_classification` clauses and the `repair` prompt paragraph carried no stale mechanism/raising claim (unchanged). (6) Task 130.140: `CHANGELOG.md` `[Unreleased]` gains a `### Changed` section with two bullets (the four tools' `ParseFailureResult` branch; `update`/`edit`'s `ValidateResult` branch), issue #170 + ADR b8c9bfea + chain numbering referenced, no dated release section created. (7) Task 130.150: `uv run --frozen specmgr mcp-docs` (run twice: md5-stable, no drift) -> `docs/MCP.md` picks up the four changed tool descriptions (the `repair` prompt description renders there but is unchanged); `uv run --frozen specmgr docs` (run twice: md5-stable) -> exactly the nine expected `docs/api/*.md` files changed (`general.tools.update`/`edit`/`set_status`/`set_classification`, `general.tools._doc_paths`, `feat.tools._paths`, `general.prompts.repair`, `server`) and `docs/GENERATED.md` UNCHANGED (no modules added/removed). Phase-end gate (Task 130.160): `uv run --frozen ruff format --check` (1775 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no findings), `uv run --frozen pytest -n auto --cov=src --cov-report=` (3813 passed in 61.61s -- baseline-matched, no test changes this phase; `tests/general/prompts/test_repair.py` 21/21 green unchanged), both doc generators idempotent on second run. The phase's single Conventional Commit is reserved to the orchestrator.

#### 2026-09-30T15:38:45.000Z - Phase 120 (Bug 2): ValidateResult branch added to update (24 sites) and edit (12 sites); nine raise-asserting tests converted

Implemented REQ-003 (Bug 2) per the ADR b8c9bfea Decision Outcome item 3 (+ item 4 for the precedence). In `general/tools/update.py`, each of the 12 `_update_<d>` adapters' new-content validation block is now wrapped in `try`/`except _CAUGHT_EXCEPTIONS` -- pre-lock on the submitted `content` in whole-body mode, in-lock after `splice_body` on the `spliced` result in range mode -- returning `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])` with `message = snippet(str(ex), max_chars=300)`, mirroring `validate`'s own construction exactly (same two-line shape, same cap); in `general/tools/edit.py`, the same wrap goes around each adapter's stage-2 post-edit validation block only (stage-1's OC-parity `ValueError`s and every pre-dispatch guard stay plain-raising, REQ-004). `_CAUGHT_EXCEPTIONS` is imported from the sibling `validate` module (`from .validate import _CAUGHT_EXCEPTIONS` -- the plan's preferred reuse, with an in-codebase precedent in `find_related.py`/`find_similar_text.py`'s own `from ._embedding import _similarity_availability`), not redefined; `snippet`/`ValidateResult`/`ValidationErrorEntry` imported alongside the existing `..models`/`...models.md._markdown` imports. `set_status.py`/`set_classification.py` untouched (no Bug-2 branch). Execution order per adapter is byte-identical apart from the new wrap (the Phase-110 `XNotFoundError` branches stay exactly where they were), which is what pins REQ-010's mode-dependent precedence. Return-type unions widened (Task 120.120): the `_UpdateFrontmatter`/`_EditFrontmatter` aliases gain `| ValidateResult` (end state `<frontmatter> | ParseFailureResult | ValidateResult`), every per-adapter annotation gains it too (ruff reflowed the now-longer signatures to the multi-line form already used by `_update_sysrs`). No docstrings/`@mcp.tool()` descriptions touched (Phase 130, REQ-006). Tests (Task 120.130): new `TestUpdateValidateFailure` (9 methods: whole-body structural + field-error over the 11 flat domains via the existing `_CASES` fixtures, range field-error splice, the 300-char cap via `test_validate.py`'s own duplicate-H1 repro, the combined-failure whole-body -> `ValidateResult` and range -> `ParseFailureResult` precedence pins over `_PARSE_FAILURE_CASES`, and the four feat separate-case-shape equivalents) and new `TestEditValidateFailure` (4 methods: field-error edit pair + H1-deletion edit over all 12 domains via this module's unified `_CASES`, the 300-char cap via a req duplicate-H1 edit, and the combined-failure -> `ParseFailureResult` pin over all 12) -- every case asserts the single capped `errors[].message` carries the per-domain `"<d> update|edit (body): "` `wrap_tool_errors` prefix and the on-disk file is byte-identical (nothing written, `updated` not bumped). The nine raise-asserting content-validation tests (Task 120.140) were converted in place to the non-raising shape and renamed (see the Decisions Made entry below for the full old->new mapping): the per-type `expected_error = ValidationError if ... else AssertionError` branch is dropped in the field-error conversions (both channels funnel into the same returned `ValidateResult`; the strongest surviving message assertion is the `wrap_tool_errors` prefix, which the `ValidationError` channel carries per-field rather than at the start). Six ADDITIONAL raise-pinning tests the plan's "nine" list did not anticipate -- `test_error_context.py`'s two `TestGenericUpdateToolErrorContext` tests and the `update`-surface halves of `tests/regression/test_issue_27.py` (2) and `test_issue_71.py` (2) -- also pinned the old raising contract and had to be converted to the same non-raising shape for the gate to go green (the issue-27 feat-7 Task 0.29 case and the issue-71 malformed-heading case now assert their `..._VIA_VALIDATE` substring subsets plus the `"... (truncated)"` suffix, exactly as their `validate`-sibling tests do; the issue-71 ordering case fits under the cap and keeps its full substring set). The `assertRaises(ValueError)`/`assertRaises(<D>NotFoundError)` tests (range-coordinate misuse, edit's OC-parity guards, bad id shape, unknown type, truly-missing id) are untouched and green. Phase-end gate (Task 120.150) green: `ruff format --check` (1775 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings), `pytest -n auto --cov=src --cov-report=` (3813 passed = 3800 baseline + 13 new test methods; the nine-plus-six conversions are in place, no net count change), `specmgr docs` (only `docs/api/biz.dfch.specmgr.general.tools.{update,edit}.md` changed -- the 24 per-adapter signature lines widen with `| ValidateResult`; `set_status`/`set_classification` docs and `docs/GENERATED.md` byte-unchanged; second run idempotent), `specmgr mcp-docs` (no drift -- no `@mcp.tool()` descriptions touched this phase). The phase's single Conventional Commit is reserved to the orchestrator.

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

#### 2026-09-30T15:38:45.000Z - Phase 120: the nine conversions drop the per-type exception branch; six extra raise-pinning tests converted

(1) The converted field-error tests (`test_update.py`'s whole-body and range, `test_edit.py`'s two field-error stage-2 tests) no longer branch on `case.field_error_is_validation` (`expected_error = ValidationError if ... else AssertionError`): after Bug 2 both channels funnel into the SAME returned `ValidateResult(valid=False)` -- the per-type exception distinction disappears in the RETURN shape (the flag is kept in the case data for documentation; the message content still differs per channel). The strongest surviving uniform message assertion is the `wrap_tool_errors` prefix (`"<d> update|edit (body): "`), which the `ValidationError` channel carries per-field (not at the start, because `wrap_tool_errors` prefixes each pydantic per-field message) and the structural `AssertionError` channel carries at the start -- hence `assertIn` for the field-error tests and `startswith` where the failure is always structural (the H1-deletion tests). (2) The plan's "nine" under-counted the raise-pinning surface: six MORE tests pinned `update`'s old raising content-validation contract -- `test_error_context.py::TestGenericUpdateToolErrorContext` (2), `tests/regression/test_issue_27.py` (2: `TestIssue27BareDomainTokenRegression`, `TestFeat7Task029StrayListMarkerRegression`), and `tests/regression/test_issue_71.py` (2: `TestIssue71MalformedHeadingRegression`, `TestIssue71NewestFirstOrderingRegression`) -- and they fail once Bug 2 lands, so converting them was mandatory for a green gate. They are converted to the same non-raising shape, asserting the per-domain wrap prefix against `result.errors[0].message` (the two fixtures whose raw message exceeds the 300-char cap assert their `..._VIA_VALIDATE` substring subsets plus the `"... (truncated)"` suffix, mirroring their `validate`-sibling tests; the issue-71 ordering case fits under the cap and keeps its full substring set). (3) The nine converted tests, old name -> new name: `test_update.py` `TestUpdateWholeBody`: `test_status_not_settable_through_update` -> `test_status_not_settable_through_update_returns_validate_failure_and_leaves_file_byte_identical`; `test_structural_failure_raises_and_leaves_file_byte_identical` -> `test_structural_failure_returns_validate_failure_and_leaves_file_byte_identical`; `test_field_validation_failure_raises_and_leaves_file_byte_identical` -> `test_field_validation_failure_returns_validate_failure_and_leaves_file_byte_identical`. `TestUpdateRange`: `test_range_deleting_the_h1_raises_and_leaves_file_untouched` -> `test_range_deleting_the_h1_returns_validate_failure_and_leaves_file_untouched`; `test_range_producing_out_of_vocabulary_value_raises_and_leaves_file_untouched` -> `test_range_producing_out_of_vocabulary_value_returns_validate_failure_and_leaves_file_untouched` (its if/else branches carried 2 of the plan's 9 `assertRaises` sites). `test_edit.py` `TestEditInvalidResult`: `test_deleting_mandatory_h1_raises_wrapped_assertion_error_file_byte_unchanged` -> `test_deleting_mandatory_h1_returns_validate_failure_file_byte_unchanged`; `test_edit_producing_field_error_raises_wrapped_error_file_byte_unchanged` -> `test_edit_producing_field_error_returns_validate_failure_file_byte_unchanged`; `test_replace_all_invalid_edit_raises_wrapped_error_file_byte_unchanged` -> `test_replace_all_invalid_edit_returns_validate_failure_file_byte_unchanged`. Each now asserts `isinstance(result, ValidateResult)`, `result.valid is False`, exactly one capped `errors[].message` carrying the prefix, and the file byte-identical; per-domain subTest loops, fixtures and feat-case handling unchanged; every `assertRaises(ValueError)`/`assertRaises(<D>NotFoundError)` test stays byte-untouched (REQ-004).

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
