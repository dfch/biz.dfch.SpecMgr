---
classification: null
created: '2026-09-25T18:10:37.035+02:00'
id: feat-159-edit
status: done
type: feat
updated: '2026-09-27T11:45:34.984+02:00'
version: 1.0.0
---

# Feature: Add specmgr edit tool (as seen in OC)

## Plan

### Overview

Adds a new generic `edit` MCP tool in `general/tools/` that matches `old_str`
byte-exactly in the frontmatter-stripped body of an existing document and
rewrites it with `new_str` (an empty `new_str` deletes the match), dispatched
across all 12 whole-body domains
(`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`).
The signature/call behaviour mirrors the OpenCode `edit` tool (exact match,
optional `replace_all`, the same error messages). Internally the
implementation is 2-fold: (1) the match must succeed (old_str found; unique
unless `replace_all`), and (2) the resulting document must still validate as a
whole — the document is written to disk only if the edit result still makes a
valid document, and if either stage fails, nothing is written. Closes GitHub
issue #159.

### Requirements

- REQ-001: The `edit` tool exposes the same signature/call behaviour as the OC `edit` tool: an exact match of `old_str` rewritten to `new_str`, with an optional `replace_all` flag; `new_str` must differ from `old_str` (the identical-input guard), and `new_str` may be empty — a pure deletion of the matched text, legal iff the edited body still validates as a whole document (REQ-003 stage 2); the MCP input schema carries no `minLength` on `new_str`.

- REQ-002: The failure error messages are the same as with the OC `edit` tool (quoted verbatim in Design Notes, pinned to opencode dev commit `236cfcbbc31530fde6a9e65318703f40adad8455`): the OC "could not find oldString" message when `old_str` is not found, and the OC "found multiple matches" message when `old_str` matches more than once without `replace_all`. Parity targets OC's *runtime* error strings — OC's own tool description text promises different strings than its runtime throws. The empty-`old_str` guard message is the OC message verbatim except that OC's `write` tool reference is adapted to specmgr's `update` tool (the full adapted string is pinned in Design Notes).

- REQ-003: The implementation is 2-fold, and the document is written to disk only if both stages pass: the exact match must succeed first (old_str found; unique unless `replace_all`), then the edited body must validate as a whole document; on any failure nothing is written.

- REQ-004: The tool dispatches on `type` across the 12 whole-body domains like the generic `update` tool (per-domain adapters, same locks, same id resolution, same domain not-found errors); `adr` is excluded — unlike `update`/`delete`/`set_classification` (whose dispatch-table lookup inherits a `KeyError` for `type="adr"`), `edit` raises an explicit `ValueError` for an unknown or `adr` `type` before dispatch, following the generic `validate` tool's own precedent.

- REQ-005: `id` is validated via `_path_safety.validate_id` before any filesystem access, and the resolved path is confined to the domain's own base directory via `assert_within`.

- REQ-006: On success the existing frontmatter is carried over with only `updated` bumped, the edited body is persisted verbatim (no mdformat reformat on write — `format_text` is applied during validation only, exactly like `update`), the tool returns the updated frontmatter only, and it warms the domain doc cache, like `update`.

- REQ-007: The tool is registered in `server.py`, listed in its docstring, mirrored in the regenerated `docs/MCP.md`, and documented in `AGENTS.md`.

- REQ-008: The error contract is 2-fold: stage-1 failures (the identical-input guard, the empty-`old_str` guard, `old_str` not found, multiple matches without `replace_all`) each raise a plain `ValueError` carrying the OC message verbatim (Design Notes) with no `domain tool (channel)` prefix, and nothing is written; the checks run in the order `validate_id` → explicit `type` check → identical input → empty `old_str`, all before any filesystem access, and the match-stage checks run under the domain lock after the on-disk body is read. Stage-2 failures (the edited body does not validate as a whole document) raise the wrapped `AssertionError`/`pydantic.ValidationError` exactly like the generic `update` tool.

- REQ-009: Matching is pure byte-exact over the frontmatter-stripped body text the shared `body_text` helper returns (the same text `get_<d>(id, raw=True)` returns): no line-ending normalization (OC's file-dominant-EOL conversion is not replicated), no BOM handling, no fuzzy/regex fallback; `replace_all` rewrites every exact occurrence.

### Acceptance Criteria

- [x] ACC-001: A unique exact match rewrites the body and returns the frontmatter with `updated` bumped. Verified in `TestEditHappyPath` (unique-match rewrite + `updated` bump to the patched timestamp, all other frontmatter carried over).

- [x] ACC-002: A missing `old_str` raises the OC not-found error verbatim (`Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.`) as a plain `ValueError` with no `domain tool (channel)` prefix; the file is byte-unchanged. Verified in `TestEditMatchStageOnDisk` + `TestMatchStageUnit` (OC not-found message by full-message equality, plain `ValueError`, byte-unchanged).

- [x] ACC-003: Multiple matches without `replace_all` raise the OC multiple-matches error verbatim (`Found multiple matches for oldString. Provide more surrounding context to make the match unique.`) as a plain `ValueError` with no `domain tool (channel)` prefix, file byte-unchanged; with `replace_all` all occurrences are rewritten. Verified in `TestEditMatchStageOnDisk` (multiple-matches verbatim, byte-unchanged; `replace_all` full-text-equality success).

- [x] ACC-004: An edit that yields an invalid document raises the wrapped validation error and nothing is written — the disk write happens only after whole-document validation passes. Verified in `TestEditInvalidResult` (wrapped stage-2 error, per-domain channel, nothing written).

- [x] ACC-005: An invalid or path-injection `id` raises `ValueError` before any filesystem access, in every domain. Verified in `TestEditInvalidId` + `TestEditDomainNotFound`.

- [x] ACC-006: All 12 whole-body domains are accepted; the MCP input schema's `type` enum excludes `adr`, and a direct call with `type="adr"` (well-formed UUID `id`) raises the explicit `ValueError` before any filesystem access (pinned test, REQ-004). Verified in `TestEditRegistration` (live schema: 12-value enum, `required`, `replace_all`, no `minLength`) + `TestEditUnsupportedType` (pinned `type="adr"` explicit `ValueError` before filesystem access).

- [x] ACC-007: The `server.py` docstring, `docs/MCP.md`, and `AGENTS.md` reflect the new tool (drift checks pass). Verified in this phase (Task 4.1): the `server.py` docstring + `docs/MCP.md` + `AGENTS.md`, plus the Task 4.2 drift checks (a second generation run changed nothing).

- [x] ACC-008: An empty `new_str` deletes the matched text: deleting an optional section succeeds and the document still validates; deleting a mandatory part (e.g. the H1) raises the wrapped validation error and the file is byte-unchanged. Verified in `TestEditHappyPath` (empty `new_str` optional-section deletion) + `TestEditInvalidResult` (mandatory H1 deletion → wrapped error, byte-unchanged).

- [x] ACC-009: The identical-input guard (`No changes to apply: oldString and newString are identical.`) and the empty-`old_str` guard fire before any filesystem access — including for a non-existent document (the guard's `ValueError`, not the domain's not-found error) — in that order. Verified in `TestEditPublicGuards` (both guards fire before file access, incl. non-existent document, in pinned order).

- [x] ACC-010: Pure byte-exact matching is pinned: an `old_str` containing `\n` is *not found* in a CRLF-body document (no line-ending normalization, REQ-009). Verified in `TestMatchStageUnit` (the CRLF pin at the `_match_and_replace` level per D10, plus the positive CRLF control).

### Scope

#### Included

- The new generic `edit` tool in `general/tools/` (dispatch-only, 12 whole-body domains), wired into `general/tools/__init__.py` (import, `__all__`, package-docstring enumeration)

- Exact-match semantics with an optional `replace_all` flag; OC-parity signature and error messages

- The 2-fold validation (match stage, then whole-document validation of the edited body)

- Path safety, domain lock, frontmatter carry-over with `updated` bump, doc-cache warming

- Unit/tool tests and documentation (`server.py` docstring, `docs/MCP.md`, `AGENTS.md`)

#### Explicitly Out Of Scope

- Fuzzy/regex/partial string matching (exact match only; OC's 9-stage fallback matcher chain — and its `isDisproportionateMatch` refusal guard, which exists only to police those fuzzy stages — is not replicated)

- Addressing or mutating the YAML frontmatter (body only)

- The `adr` domain (excluded, like the generic `update` tool)

- Server-side "read before edit" enforcement (OC's is a client session-state convention; documented only)

- `offset`/`limit` line-range addressing (the generic `update` tool's territory)

- Line-ending normalization of `old_str`/`new_str` (OC converts them to the file's dominant EOL before matching; `edit` is pure byte-exact — REQ-009)

- Updating the 12 per-domain `update_<d>` prompt flows to mention `edit` (follow-up feature)

### Design Notes

The tool mirrors the generic `update` adapter shape (`general/tools/update.py`): the public dispatcher validates `id` via `_path_safety.validate_id`, then rejects an unknown or `adr` `type` with an explicit `ValueError` (the generic `validate` tool's own precedent — a deliberate divergence from `update`/`delete`/`set_classification`, whose dispatch-table lookup inherits a `KeyError` for `type="adr"`), then runs the identical-input and empty-`old_str` guards — all four checks before any filesystem access — and dispatches to private per-domain `_edit_<d>` adapters. Unlike `update`'s whole-body mode (which validates client-supplied content *before* taking the lock), each `edit` adapter holds the domain lock across the entire read → match → validate → write sequence — the match is against on-disk content, so reading it outside the lock would be a TOCTOU race — and resolves the document via the domain's `load_by_id`, confines the path with `assert_within`, and reads the on-disk body via the shared `body_text` — the same frontmatter-stripped text `get_<d>(id, raw=True)` returns, consistent with `update`'s range-coordinate contract.

Stage 1 (match) counts exact `old_str` occurrences in that raw body: 0 → the OC not-found error; >1 without `replace_all` → the OC multiple-matches error. Matching is **pure byte-exact** (REQ-009): no line-ending normalization (OC converts `oldString`/`newString` to the file's dominant EOL before matching — deliberately not replicated), no BOM handling (UTF-8, like every other tool), no fuzzy/regex fallback. The two verbatim OC error strings (quoted from opencode's `packages/opencode/src/tool/edit.ts` `replace()`, dev branch, commit `236cfcbbc31530fde6a9e65318703f40adad8455` — the last commit touching that file, 2026-06-05; verified verbatim against dev on 2026-09-26) are:

```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
Found multiple matches for oldString. Provide more surrounding context to make the match unique.
```

The identical-input guard uses OC's verbatim string `No changes to apply: oldString and newString are identical.`, and the empty-`old_str` guard is the OC message verbatim except that OC's `write` tool reference is adapted to specmgr's `update` tool: `oldString cannot be empty when editing an existing file. Provide the exact text to replace, or use update for an intentional full-file replacement.` The verbatim strings deliberately retain OC's parameter names (`oldString`/`newString`), per the issue's "same error message" ask; both guards fire before any filesystem access. Parity targets OC's *runtime* strings: OC's own tool description text promises different messages ("oldString not found in content", "Found multiple matches for oldString. Provide more surrounding lines in oldString to identify the correct match.") that its runtime never throws. An empty `new_str` (a pure deletion, REQ-001) passes both guards and is legal iff stage 2 validates the result. OC's 9-stage fuzzy matcher chain — and its `isDisproportionateMatch` refusal guard, which exists only to police those fuzzy stages — is deliberately not replicated: this tool is exact-match only. The four stage-1 failures each raise a **plain `ValueError`** with the message verbatim and no `domain tool (channel)` prefix (the conventions' user-controlled-input rule; `update`'s coordinate-guard precedent) — `wrap_tool_errors` applies to stage 2 only, exactly as in `update`.

Stage 2 (validate) applies the edit (single or all occurrences) and validates the edited body as a whole document via `<Domain>.from_text(format_text(edited))` under `wrap_tool_errors(domain=..., tool="edit", channel=BODY_CHANNEL)`; the disk write via the domain's `write_<d>_file` happens strictly after that validation succeeds — the document is only written to disk if the result of the edit still makes a valid document. On success the frontmatter is carried over with only `updated` bumped, the edited body is persisted verbatim — no mdformat reformat on write, exactly like `update` (`write_<d>_file` embeds the body verbatim and never reformats/re-renders it; `format_text` is applied during validation only) — and the cache is warmed via the domain's `read_<d>`. The on-disk document is therefore mdformat-normalized after a successful edit iff it was normalized before and `new_str` is itself mdformat-normalized text; the dedicated `mdformat` tool/CLI remains the normalization path. "Verbatim" is additionally modulo the python-frontmatter `YAMLHandler`'s trailing-whitespace strip on serialization (the inherited `_write.py` caveat, identical to `update`) — the read-back comparisons in the tests follow `test_update.py`'s own convention. On any failure (either stage) nothing is written and the file is byte-unchanged.

edit.py carries its own module-level `assert set(_ADAPTERS) == set(WHOLE_BODY_DOMAINS)` drift guard (the feat-125-domain-lists pattern, cf. `update.py`'s own) — the same pattern, not the same literal, since each dispatch table guards itself; no change to the shared domain vocabulary is needed. OC's read-before-edit session-state enforcement is deliberately not replicated server-side (no enforcement) and is instead documented as a client convention in the tool description, alongside guidance on when to use `edit` (surgical string replacement) vs the generic `update` (whole-body or line-range replacement) and the statement that the YAML frontmatter is never addressable (body only).

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 (dispatch-only): `edit` is one generic tool with per-domain adapters, not per-domain `edit_<d>` tools.

- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d (path safety): `validate_id` before any filesystem access and `assert_within` base-directory confinement apply to the new tool.

- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d (doc cache): the write path warms the domain cache after a successful edit.

- feat-22-consolidate-mutation-tools: precedent for the generic whole-body mutation tool (`update`) that this tool mirrors.

- ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6 (feat-81-83-validation): the generic `validate` tool's explicit `type not in _ADAPTERS` `ValueError` is the precedent for `edit`'s own unknown/`adr`-type rejection (REQ-004).

### Task List

#### Phase 1: Design

- [x] Task 1.1: Draft the tool contract (signature, OC error parity, 2-fold behaviour) into this feature — status: done (2026-09-25)

- [x] Task 1.2: Decide whether a full ADR is required or the dispatch-only convention (ADR 36905d5b) suffices; record in Decisions Made — status: done (2026-09-26, no new ADR; see Decisions Made)

#### Phase 2: Implementation

- [x] Task 2.1: Add `general/tools/edit.py` — public dispatcher (guard order per REQ-008, explicit `type` check per REQ-004) plus 12 per-domain adapters, `_ADAPTERS` dispatch table with its own module-level drift assert, the `@mcp.tool(description=...)` text (read-before-edit client convention; `edit` vs `update` guidance; body-only; 2-fold behaviour; byte-exact/no-EOL-normalization note; nothing written on failure), and the `general/tools/__init__.py` wiring (import, `__all__`, package-docstring enumeration) — status: done (2026-09-26)

- [x] Task 2.2: Implement stage-1 exact-match logic with the pinned verbatim OC error messages (identical; empty `old_str` adapted; not found; multiple matches) as plain `ValueError`s with no wrap prefix (REQ-008/REQ-009) — status: done (2026-09-26)

- [x] Task 2.3: Implement stage-2 whole-document validation with the disk write strictly after validation passes (the domain lock held across read → match → validate → write), frontmatter carry-over (`updated` bump), verbatim persist (incl. the empty-`new_str` deletion case), cache warm — status: done (2026-09-26)

#### Phase 3: Tests

- [x] Task 3.1: Unit tests for the match stage (0/1/n occurrences, `replace_all`, `new_str == old_str` guard, empty `old_str` guard, empty `new_str` deletion, the guard-order / fire-before-file-access cases, the pure-byte-exact CRLF pin per ACC-010) — status: done (2026-09-27)

- [x] Task 3.2: Tool tests across all 12 whole-body domains (happy path, not found, multiple matches, invalid result, invalid id) mirroring `test_update.py`'s per-domain `_Case` harness and `SPECMGR_DOCS_DIR` temp fixture — status: done (2026-09-27)

- [x] Task 3.3: Regression: the file is byte-unchanged on every failure path (including the invalid-result path) — status: done (2026-09-27)

- [x] Task 3.4: Registration/schema test mirroring `TestUpdateRegistration` (live `mcp.list_tools()`: `type` enum == `WHOLE_BODY_DOMAINS`, `required == [id, type, old_str, new_str]`, `replace_all` optional bool default false, no `minLength` on `new_str`) plus the pinned `type="adr"` explicit-`ValueError` test (REQ-004) — status: done (2026-09-27)

#### Phase 4: Docs & Quality Gate

- [x] Task 4.1: Update the `server.py` docstring, regenerate `docs/MCP.md` and `docs/api/`, update `AGENTS.md` (the `general/tools/` paragraph names `edit`, including its deliberate `ValueError` divergence from `update`'s `KeyError` for `type="adr"`) — status: done (2026-09-27)

- [x] Task 4.2: Run ruff/pylint/vulture and the full test suite (phase-end quality gate) — status: done (2026-09-27)

#### Phase 5: External-Review Hardening (found during an external `feat-reviewer` review pass after Phase 4, not part of GitHub issue #159's original request)

- [x] Task 5.1: `CHANGELOG.md` — `[Unreleased]` gains an `### Added` entry for the new `edit` tool (the feat-144 `list_references` entry's own shape): the generic, cross-domain, surgical exact-match body-replacement tool in `general/tools/` across the 12 whole-body domains, `adr` excluded via an explicit pre-dispatch `ValueError` (the generic `validate` tool's precedent, unlike `update`'s inherited `KeyError`), the OC-parity contract (byte-exact matching, no line-ending normalization, `replace_all`, the verbatim stage-1 messages), the 2-fold contract (written only if the match succeeds and the edited body still validates as a whole document; byte-unchanged on any failure), an empty `new_str` as a pure deletion, the frontmatter-only return with `updated` bumped, the domain lock held across the entire read/match/validate/write sequence, and the shared `_path_safety` guards. — status: done (2026-09-27)

- [x] Task 5.2: `src/biz/dfch/specmgr/general/tools/edit.py` — port the feat-addressing paragraph from `update.py`'s module docstring (`feat` is the one domain whose adapter resolves `id` via `feat.tools._paths`'s bespoke folder-per-document shortcut, not a flat-file directory scan) into `edit.py`'s own module docstring, so `_edit_feat`'s "(see the module docstring)" reference is valid in its own file. — status: done (2026-09-27)

- [x] Task 5.3: `src/biz/dfch/specmgr/general/tools/edit.py` — document the explicit pre-dispatch `type` check's actual reach: the edit-specific message is reachable only for `type="adr"` (a well-formed UUID id passes `validate_id` first); any other unknown type is rejected by `validate_id`'s own message (which lists the UUID domains, `adr` included). The code comment at the check and the tool docstring's `Raises` section say so; behavior and the pinned guard order (REQ-008, `validate_id` first) are unchanged. — status: done (2026-09-27)

- [x] Task 5.4: `tests/general/tools/test_edit.py` — pylint parity with the `test_update.py` mirror: `# pylint: disable=protected-access` on the `_match_and_replace` alias (the repo's own 13-site convention), one-line docstrings on the 23 test methods that lack one (the mirror is 22/22), and a docstring on `test_unknown_type_raises_value_error` explaining the deliberate containment assert (the message comes from the shared `validate_id`, not `edit`'s own explicit check, which is reachable for `adr` only and pinned by full equality in the adjacent test). — status: done (2026-09-27)

- [x] Task 5.5: `tests/general/tools/test_edit.py` — close the one untested 2-fold corner: a new `TestEditInvalidResult` test running the per-domain field-error edit with `replace_all=True`, asserting the wrapped validation error (per-domain channel) and the file byte-unchanged, exactly mirroring the single-match path's test. — status: done (2026-09-27)

- [x] Task 5.6: `.specmgr/feat/feat-159-edit/README.md` — fix the Current Status pylint sentence (the 23x C0116 + 1x W0212 findings do not share their classes with the `test_update.py` mirror; after Task 5.4 the residual findings do) and refresh the gate-evidence numbers to this phase's own runs. — status: done (2026-09-27)

- [x] Task 5.7: Regenerate `docs/api/` + `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`) for the docstring changes; run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src`, per-file `pylint`); update Progress (Current Status, a dated Updates entry, a Decisions Made entry noting the phase originated from the external `feat-reviewer` pass); the feature stays in `status: review`. — status: done (2026-09-27)

## Progress

### Current Status

**As of 2026-09-27**: All five phases implemented and the phase-end quality gate is green. Phase 2 shipped the tool (`src/biz/dfch/specmgr/general/tools/edit.py` + the `general/tools/__init__.py` wiring), Phase 3 shipped the tests (`tests/general/tools/test_edit.py` — 29 test methods, 264 per-domain subtests, `edit.py` at 100% statement coverage), and Phase 4 shipped the documentation (the `server.py` module-docstring `edit` entry in the "General tools" paragraph, the matching `AGENTS.md` entries — `general/` bullet and the future-domain convention sentence — and the regenerated `docs/api/` + `docs/GENERATED.md`, with `docs/MCP.md` proven a byte-identical no-op and a second generation run changing nothing, i.e. converged drift), and Phase 5 addressed the external `feat-reviewer` pass (the `CHANGELOG.md` `[Unreleased]` Added entry, the `edit.py` module-docstring feat-addressing paragraph, the explicit-`type`-check reach documentation, `test_edit.py`'s pylint parity with its mirror plus the `replace_all` stage-2 corner test, and the regenerated `docs/api/` entry). ACC-001…ACC-010 are all verified — see the per-ACC evidence annotations in the Acceptance Criteria section above (ACC-007 pinned to this phase's docs edits + the Task 4.2 drift checks). Gate evidence (Phase 5 run): `ruff format --check` (1722 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean), full suite `pytest -n auto --cov=src` (3481 passed, 2305 subtests; `edit.py` at 100% statement coverage, overall 99%), and the advisory per-file `pylint` runs (`edit.py` 10.00/10; `test_edit.py` 9.84/10 — every residual finding in a class its `test_update.py` mirror also carries: C0301/C0302/R0902/R1732/C0415). The feature is in `status: review`, awaiting re-review/merge.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-27T11:45:48.349+02:00 - Feature closeout (author review approved, status set to `done`)

The author reviewed the feature, including the Phase 5 (external `feat-reviewer`) fixes, and approved it for merge. Frontmatter `status` set to `done` via the generic `set_status` tool (`type="feat"`); the feature merges to `dev` via PR #161.

#### 2026-09-27T10:46:29.504+02:00 - Phase 5 implemented (external-review hardening, Tasks 5.1–5.7 done)

Phase 5 (External-Review Hardening) remediated the findings of an external `feat-reviewer` pass on the closed feature (the review found no blocking defects; all gate evidence below is this phase's own independent re-run). Task 5.1: `CHANGELOG.md`'s `[Unreleased]` gained the `### Added` entry for the new `edit` tool (the feat-144 `list_references` entry's own shape) — the merge-blocking gap: without it the next release would have shipped the tool with no changelog record. Task 5.2: `edit.py`'s module docstring gained the feat-addressing paragraph ported from `update.py`'s (the `feat` adapter resolves `id` via `feat.tools._paths`'s bespoke folder-per-document shortcut, not a flat-file directory scan), making `_edit_feat`'s "(see the module docstring)" reference valid in its own file. Task 5.3: the code comment at the explicit pre-dispatch `type` check and the tool docstring's `Raises` section now document the check's actual reach — the edit-specific message is reachable only for `type="adr"` (a well-formed UUID id passes `validate_id` first); any other unknown type is rejected by `validate_id`'s own message (which lists the UUID domains, `adr` included); behavior and the REQ-008-pinned guard order are unchanged. Task 5.4: `test_edit.py`'s pylint parity with its mirror — `# pylint: disable=protected-access` on the `_match_and_replace` alias (the repo's 13-site convention), one-line docstrings on the 23 test methods that lacked one (the mirror is 22/22), and a docstring on `test_unknown_type_raises_value_error` explaining the deliberate containment assert. Task 5.5: a new `TestEditInvalidResult` test closing the one untested 2-fold corner — the per-domain field-error edit run with `replace_all=True`, asserting the wrapped validation error (per-domain channel) and the file byte-unchanged. Task 5.6: the Current Status note's inaccurate pylint-parity sentence and stale gate numbers corrected to this phase's own runs. Task 5.7: `specmgr docs` regenerated `docs/api/biz.dfch.specmgr.general.tools.edit.md` (the module + tool docstring changes); `specmgr mcp-docs` was a byte-identical no-op on `docs/MCP.md` (it documents the tool description only, not the `Raises` section); full gate green — `ruff format --check` (1722 files), `ruff check`, `vulture` clean, `pytest -n auto --cov=src` 3481 passed / 2305 subtests (`edit.py` still 100% statement coverage; overall 99%), per-file pylint `edit.py` 10.00 / `test_edit.py` 9.84 (residual findings only in classes the mirror also carries). The feature stays in `status: review`.

#### 2026-09-27T02:19:10.688+02:00 - Phase 4 implemented + feature closeout (Tasks 4.1–4.2 done, ACC-001…ACC-010 verified)

Phase 4 (Docs & Quality Gate) and the feature closeout. Docs (Task 4.1): the `server.py` module docstring's "General tools" paragraph now carries the `edit` entry immediately after `update` — surgical exact-match replacement of the frontmatter-stripped body across the 12 whole-body domains, `adr` excluded via an explicit pre-dispatch `ValueError` (unlike `update`'s inherited `KeyError`, the generic `validate` tool's precedent, ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6), byte-exact matching with no line-ending normalization (an `old_str` containing `\n` will not match a CRLF body), no BOM handling, no fuzzy/regex fallback, unique unless `replace_all` rewrites every exact occurrence, the 2-fold contract (the *edited* body must still validate as a whole document; written only if both stages pass, nothing written on any failure), an empty `new_str` as a pure deletion legal iff the edited body validates, frontmatter-only return with `updated` bumped, and an invalid `id` a `ValueError` before any file access; the feat-38-39-41-43-44 path-safety note below the enumeration was left untouched (the `edit` entry carries its own safety statement). `AGENTS.md`'s `general/` bullet gained the matching `edit` entry right after `update`, and the "Still genuinely missing / not yet done" future-domain convention sentence now also names one `edit` adapter in the generic `edit` tool (the `edit.py` module-level `_ADAPTERS` drift assert makes a missed entry fail at import); the per-domain bullets were not touched (their "updates go through the generic `update` tool" sentences remain true; per-domain prompt-flow updates are a follow-up feature per D5). Regeneration: `specmgr docs` updated `docs/api/biz.dfch.specmgr.server.md` (the docstring) and `docs/GENERATED.md` (test-file count 362 → 363, converging the Phase-3 delta); `specmgr mcp-docs` was a byte-identical no-op on `docs/MCP.md` (already regenerated by the Phase-2 pre-commit hook); `git status` shows exactly the four intended files; a second full generation run of both commands changed nothing (drift converged). Quality gate (Task 4.2): `uv run --frozen ruff format --check` — 1719 files already formatted; `uv run --frozen ruff check` — all checks passed; `uv run --frozen vulture src/ whitelist.py --min-confidence 60` — clean (exit 0); `uv run --frozen pylint $(git ls-files '*.py')` — advisory score 8.92/10 (previous run 8.92/10, +0.00, exit 30): zero findings on `edit.py` and `general/tools/__init__.py`, and `server.py`'s only findings (the C0413 + 14× W0611 on the intentional trailing side-effect import line) verified identical against the pre-phase file — none on any line this phase touched; `test_edit.py` (Phase 3) carries only same-class findings its `test_update.py` mirror also has (missing test-method docstrings, one line-too-long, too-many-lines, protected-access, consider-using-with, import-outside-toplevel); full suite `uv run --frozen pytest -n auto --cov=src --cov-report=` — 3468 passed (31.12s); docs drift check — a second `specmgr docs` + `specmgr mcp-docs` run left every regenerated file byte-identical. Closeout: all ten acceptance criteria marked done with the test-class evidence annotations above (each verified against `tests/general/tools/test_edit.py`'s actual class/method names), Tasks 4.1/4.2 marked done, and Current Status rewritten as the final awaiting-review state. The frontmatter `status` is deliberately left as-is here — the orchestrator flips it to `review` via the generic `set_status` tool immediately after this phase's commit; only the frontmatter `updated` timestamp was bumped in this phase.

#### 2026-09-27T00:55:06.845+02:00 - Phase 3 implemented (Tasks 3.1–3.4 done)

Added `tests/general/tools/test_edit.py` (single file, 28 test methods; the 12 per-domain tool/guard classes each loop all whole-body domains in `subTest`s, 252 of them on top) mirroring `test_update.py`'s organization: the same per-domain `_Case` frozen-dataclass harness (ported to edit-specific fields: `edit_marker`/`edit_replacement`, `h1_line`, `deletable_suffix`, `multi_marker`/`multi_replacement`/`multi_seed_suffix`, `field_error_*` + `field_error_is_validation`, `missing_id`/`wrong_format_id`), the same temp `SPECMGR_DOCS_DIR` fixture (extended with `SPECMGR_FEAT_DIR` so `feat` — unlike `test_update.py`, where feat only appears in the injection class — gets the full happy/not-found/multiple/invalid/invalid-id treatment), the same `now_timestamp`-patching (`_FIXED_TIMESTAMP`) and `_MISSING_UUID` conventions, and the same wrapped-prefix assertion style (`"<d> edit (body): "`, exact for the structural `AssertionError` channel, containment for the per-field-prefixed `pydantic.ValidationError` channel). Coverage per ACC: ACC-001 (unique-match rewrite + frontmatter carry-over with `updated` bumped to the patched timestamp, body read back via `body_text`); ACC-002/ACC-003 (OC not-found / multiple-matches messages pinned by full-message equality — which also pins the plain-`ValueError`-no-wrap-prefix contract — file byte-unchanged, plus `replace_all` full-text-equality success); ACC-004 (H1 deletion → wrapped `AssertionError` in all 12 domains, per-domain field-error edit → the pinned channel, nothing written); ACC-005 (traversal + wrong-format ids in every domain, seeded file byte-unchanged; well-formed non-existent id → the domain's own `XNotFoundError`); ACC-006 (live `mcp.list_tools()`: `edit` registered once, `type` enum == `WHOLE_BODY_DOMAINS` (12 values, no `adr`), `required == [id, type, old_str, new_str]`, `replace_all` optional bool defaulting to `false`, no `minLength` on `new_str`; pinned `type="adr"` explicit `ValueError` with the exact message, before any filesystem access — both temp dirs verified empty afterwards); ACC-008 (empty `new_str` deleting a valid optional section succeeds per domain; deleting the mandatory H1 fails wrapped, byte-unchanged); ACC-009 (identical-input and empty-`old_str` guards pinned verbatim, firing for a non-existent document — the guard's `ValueError`, not the not-found error — with the order `validate_id` → explicit `type` → identical → empty `old_str` pinned by cross-firing calls); ACC-010 (the CRLF pin at the `_match_and_replace` unit level, per D10, plus a positive CRLF-match control). Two derivation notes from the per-domain schema work (recorded as D10/D11): `prb`'s multi-occurrence case seeds a dedicated optional `## More Information` section because its template-validated lead paragraph must not be rewritten, and the `replace_all` success asserts full-text equality against `before.replace(marker, replacement)` — stronger than a replacement-count assertion, which misfires when the replacement occurs as a substring elsewhere (e.g. `gol`: `"that are"` contains `"at "`). `edit.py` reaches 100% statement coverage (290/290) from this file alone. Phase-end quality gate green: `ruff format --check` (1719 files), `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full suite `pytest -n auto --cov=src` — 3468 passed (3440 pre-existing + 28 new).

#### 2026-09-26T22:29:21.223+02:00 - Phase 2 implemented (Tasks 2.1–2.3 done)

Implemented `src/biz/dfch/specmgr/general/tools/edit.py` per the pinned contract: the public `edit(id, type, old_str, new_str, replace_all=False)` dispatcher runs the guard order `validate_id` → explicit `type not in _ADAPTERS` `ValueError` (pinned message `unknown document type {type!r}; expected one of ... ('adr' is not supported)`, the deliberate REQ-004/D4 divergence from `update`'s inherited `KeyError`) → identical-input guard → empty-`old_str` guard, all before any filesystem access (REQ-008/ACC-009); stage 1 is factored into one domain-agnostic `_match_and_replace(body, old_str, new_str, replace_all)` helper (pure byte-exact over `body_text(path)`, the verbatim OC not-found/multiple-matches messages as plain `ValueError`s with no wrap prefix); the 12 per-domain `_edit_<d>` adapters mirror `update.py`'s import set and adapter shape exactly (same lock/`load_by_id`/`assert_within`/`write_<d>_file`/frontmatter carry-over with only `updated` bumped via `now_timestamp()`/cache-warm `read_<d>` — feat's `read_feat` from `...feat.tools._cache` like `update.py`), holding the domain lock across read → match → validate → write with the disk write strictly after the stage-2 `<Domain>.from_text(format_text(edited))` validation under `wrap_tool_errors(domain=..., tool="edit", channel=BODY_CHANNEL)` (REQ-003); `_ADAPTERS` carries its own module-level drift assert referencing feat-159-edit. `general/tools/__init__.py` now imports `edit` (alphabetical), lists it in `__all__`, and enumerates it in the package docstring in the existing prose style. Verified in this phase (proper unit/tool tests are Phase 3): the live `mcp.list_tools()` schema matches the pinned contract, and an end-to-end smoke run against a temp `SPECMGR_DOCS_DIR` confirmed all pinned behaviours — guard firing before file access (incl. for a non-existent id), the `type="adr"` explicit `ValueError`, traversal-`id` rejection, byte-unchanged file on every failure path (not-found, multiple-match, stage-2 invalid-result incl. H1 deletion), `replace_all`, empty-`new_str` deletion of optional sections, the CRLF byte-exact pin (a `\n` `old_str` is not found in a CRLF body), frontmatter carry-over with `updated` bump, and the wrapped `req edit (body):` stage-2 error prefix. Two implementation-level refinements recorded in Decisions Made (D8/D9): no cardinal domain count in the description/docstring prose (conventions.md rule; explicit list instead), and the two longer pinned OC messages written as implicit string concatenations to stay within ruff's 120-char line limit (runtime values byte-identical to the pinned strings). Phase-end quality gate green: `ruff format --check` (1717 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no dead code), `pytest -n auto --cov=src --cov-report=` (3440 passed, no regressions).

#### 2026-09-26T21:18:14.835+02:00 - Refined the plan after a full review pass

Independent plan-review cross-checked every codebase claim against `general/tools/update.py`, `_path_safety.py`, `_domains.py`, `_splice.py`, the `_write.py` verbatim-persist caveat, `test_update.py`'s harness, and the feat-125/feat-56/feat-81-83 precedents, and verified the pinned OC error strings against opencode dev's `packages/opencode/src/tool/edit.ts` `replace()` (commit `236cfcbbc`, last change 2026-06-05) — all confirmed. The refinements are recorded as decisions D1–D7 (Decisions Made): empty `new_str` is a legal deletion (REQ-001/ACC-008); matching is pure byte-exact with no OC EOL normalization (REQ-009/ACC-010); stage-1 failures raise plain verbatim `ValueError`s without the wrap prefix (REQ-008, ACC-002/003); `type="adr"` is an explicit pre-dispatch `ValueError` per the `validate` tool's precedent, a deliberate divergence from `update`'s inherited `KeyError` (REQ-004/ACC-006); the domain lock is held across read → match → validate → write (TOCTOU); `edit.py` carries its own feat-125 drift assert; the OC citation now pins the commit SHA and declares parity against OC's *runtime* strings (OC's own description text promises different messages). New tasks: the `general/tools/__init__.py` wiring (the silent-registration gotcha) and a registration/schema test (Task 3.4); the per-domain prompt-flow updates are a follow-up feature. Phase 1 closed: no new ADR required (ADR 36905d5b suffices).

#### 2026-09-26T17:32:00.000+02:00 - Renamed the feature and tool to `edit` throughout

The feature was renamed `feat-159-replace` to `feat-159-edit` (via `set_feat_id`) and every plan-section reference to the earlier draft name was rewritten to `edit`, matching issue #159's own title and signature; the `replace_all` parameter name is retained because it is part of the issue's signature and the OC `edit` tool's own API (REQ-001 parity). The historical entries below are preserved unchanged.

#### 2026-09-25T18:34:14.067+02:00 - Clarified OC tool name and mdformat contract

The OC counterpart is the `edit` tool, not a `replace` tool (opencode's `packages/opencode/src/tool/edit.ts` registers it via `Tool.define("edit", ...)`); issue #159's "replace" wording refers to its exact-match string-replacement behaviour, and this document now names OC's tool `edit` throughout (Overview, REQ-001, REQ-002, Decisions Made). The persistence contract is also now explicit (REQ-006, Design Notes): the replaced body is persisted verbatim with no mdformat reformat on write — exactly like `update`, which applies `format_text` during validation only; the `mdformat` tool remains the normalization path.

#### 2026-09-25T16:06:51.408Z - Created

Feature drafted for GitHub issue #159 (specmgr replace tool with OC parity). Mandatory plan sections populated from the issue; design decisions (signature, error parity, 2-fold validation, adr exclusion) confirmed with the author. The OC failure messages were pinned verbatim from opencode's `packages/opencode/src/tool/edit.ts` `replace()` (dev branch) rather than from the tool description text.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-27T10:46:29.504+02:00 - Phase 5 review-remediation decisions (D12, D13; the phase itself originated from an external `feat-reviewer` pass, not part of GitHub issue #159's original request)

Phase 5 (Tasks 5.1–5.7) is review remediation, not original-scope work: the external `feat-reviewer` pass found no blocking defects, one merge-blocking gap (the missing `CHANGELOG.md` `[Unreleased]` entry — the repo's consistent convention per feat-144/feat-132/feat-125/feat-120), and documentation-precision/test-coverage refinements. D12: the explicit pre-dispatch `type` check's documented reach — the edit-specific message is reachable only for `type="adr"` (other unknown types are rejected first by the shared `validate_id`, whose message lists the UUID domains, `adr` included); documented in the code comment and the tool docstring's `Raises` section, with behavior deliberately unchanged (the REQ-008-pinned `validate_id`-first order stands; the test pinning the edit-specific message stays scoped to `adr`, and the unknown-type test documents its containment assert). D13: `test_edit.py`'s pylint parity was achieved by *adding* the 23 missing test-method docstrings (matching the mirror's 22/22) and the one `protected-access` disable (matching the repo's 13-site convention) rather than softening the Progress note to match the code. No ACC was re-scoped and no contract changed.

#### 2026-09-27T00:55:06.845+02:00 - Phase 3 test-derivation decisions (D10, D11)

D10: the ACC-010 pure-byte-exact CRLF pin is asserted at the `_match_and_replace` unit level (a CRLF body string does not match an `old_str` containing `\n`), not through the public `edit` tool against a CRLF file on disk. Empirically confirmed while deriving the tests: a CRLF body is persisted verbatim to disk by the `create_<d>` write path, but the shared `body_text` read helper — the single definition of "the body text", the same text `get_<d>(id, raw=True)` returns — reads it back as LF text (python-frontmatter's `loads` goes through `Path.read_text`'s universal-newline translation). REQ-009's byte-exactness claim is therefore about the *matcher* performing no OC-style dominant-EOL conversion of `old_str`/`new_str`, and the unit-level pin tests exactly that; a tool-level CRLF test would instead pin `body_text`'s own read contract (shared with `update`/`get_<d>`), which is outside this feature's scope. D11: `prb`'s multi-occurrence test case seeds a dedicated optional `## More Information` section carrying the marker three times (`"The gap"` → `"The wider gap"`), because `prb`'s mandatory lead paragraph is template-validated by a `field_validator` (`[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].`) and a natural whole-body marker (e.g. `" is "`) would break it. Both decisions refine, not deviate from, the pinned contract; no `src/` change was needed.

#### 2026-09-26T22:29:21.223+02:00 - Phase 2 implementation-level refinements (D8, D9)

D8: the `@mcp.tool` description and the `general/tools/__init__.py` package-docstring enumeration name the supported domains by the explicit list (the `', '.join(WHOLE_BODY_DOMAINS)` interpolation in the description, the prose list in the docstring) rather than a cardinal "12 whole-body domains" — per `.specmgr/conventions.md`'s docstring-style rule against restating a generic tool's supported-domain count as a cardinal in prose (hardcoded counts silently go stale; the explicit list is self-verifying). This mirrors `update.py`'s own description, which likewise interpolates the domain list without a count. D9: the two longer pinned OC stage-1 messages (the not-found and the adapted empty-`old_str` message) are written in the source as implicit string concatenations (adjacent string literals) so every physical line stays within ruff's 120-char limit — the runtime string values are byte-identical to the pinned OC-parity strings (REQ-002), verified by the Phase 2 smoke run and to be pinned by the Phase 3 tests. No other deviation from the pinned contract: guard order, messages, plain-`ValueError` stage-1 / wrapped stage-2 split, lock scope, verbatim persist, cache warm, `_ADAPTERS` drift assert, and the explicit `ValueError` for unknown/`adr` `type` are implemented exactly as pinned.

#### 2026-09-26T21:18:14.835+02:00 - Refined design decisions (D1–D7)

D1: an empty `new_str` is a pure deletion, legal iff stage 2 validates (OC parity; no `minLength` on `new_str` in the MCP schema). D2: matching is pure byte-exact over `body_text` — no OC line-ending normalization, no BOM handling. D3: the four stage-1 failures (identical input, empty `old_str`, not found, multiple matches) raise plain `ValueError`s with the verbatim OC messages and no `domain tool (channel)` prefix; guard order `validate_id` → explicit `type` check → identical → empty `old_str`, all before any filesystem access; stage 2 stays wrapped exactly like `update`. D4: an unknown or `adr` `type` is an explicit pre-dispatch `ValueError` (the generic `validate` tool's precedent) — a deliberate divergence from `update`/`delete`/`set_classification`'s inherited `KeyError`. D5: updating the 12 per-domain `update_<d>` prompt flows to mention `edit` is a follow-up feature, out of scope here. D6: no new ADR — ADR 36905d5b (dispatch-only) plus 1af6787b (path safety) and bfd76370 (doc cache) cover the design (closes Task 1.2). D7: the OC error strings are pinned to opencode dev commit `236cfcbbc31530fde6a9e65318703f40adad8455` (`packages/opencode/src/tool/edit.ts`, last touched 2026-06-05, verified verbatim on 2026-09-26); parity targets OC's *runtime* strings (OC's own tool description text promises different messages than its runtime throws).

#### 2026-09-25T16:06:51.408Z - Confirmed tool design decisions

The tool signature is `edit(id, type, old_str, new_str, replace_all=False)` — `id` first, then `type`, consistent with every existing generic tool (`update`, `set_status`, `set_classification`, and `delete` all take `id` before `type`). No server-side "read before edit" enforcement: OC's is a client session-state convention, documented in the tool description instead. The `adr` domain is excluded, like the generic `update` tool. On success the frontmatter's `updated` field is bumped, like `update`. The failure messages are the OC `edit` tool's verbatim (quoted in Design Notes), including OC's parameter names (`oldString`/`newString`); OC's fuzzy matcher chain is not replicated (exact match only). The disk write happens only after the edited body validates as a whole document — never before. Persistence is verbatim, like `update`: no mdformat reformat on write (`format_text` during validation only); the `mdformat` tool is the normalization path.

### Related PRs / Commits

- [Issue #159](https://github.com/dfch/biz.dfch.SpecMgr/issues/159): tracking issue for this feature.
