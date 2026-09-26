---
classification: null
created: '2026-09-25T18:10:37.035+02:00'
id: feat-159-edit
status: planning
type: feat
updated: '2026-09-26T22:29:21.223+02:00'
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

- [ ] ACC-001: A unique exact match rewrites the body and returns the frontmatter with `updated` bumped.

- [ ] ACC-002: A missing `old_str` raises the OC not-found error verbatim (`Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.`) as a plain `ValueError` with no `domain tool (channel)` prefix; the file is byte-unchanged.

- [ ] ACC-003: Multiple matches without `replace_all` raise the OC multiple-matches error verbatim (`Found multiple matches for oldString. Provide more surrounding context to make the match unique.`) as a plain `ValueError` with no `domain tool (channel)` prefix, file byte-unchanged; with `replace_all` all occurrences are rewritten.

- [ ] ACC-004: An edit that yields an invalid document raises the wrapped validation error and nothing is written — the disk write happens only after whole-document validation passes.

- [ ] ACC-005: An invalid or path-injection `id` raises `ValueError` before any filesystem access, in every domain.

- [ ] ACC-006: All 12 whole-body domains are accepted; the MCP input schema's `type` enum excludes `adr`, and a direct call with `type="adr"` (well-formed UUID `id`) raises the explicit `ValueError` before any filesystem access (pinned test, REQ-004).

- [ ] ACC-007: The `server.py` docstring, `docs/MCP.md`, and `AGENTS.md` reflect the new tool (drift checks pass).

- [ ] ACC-008: An empty `new_str` deletes the matched text: deleting an optional section succeeds and the document still validates; deleting a mandatory part (e.g. the H1) raises the wrapped validation error and the file is byte-unchanged.

- [ ] ACC-009: The identical-input guard (`No changes to apply: oldString and newString are identical.`) and the empty-`old_str` guard fire before any filesystem access — including for a non-existent document (the guard's `ValueError`, not the domain's not-found error) — in that order.

- [ ] ACC-010: Pure byte-exact matching is pinned: an `old_str` containing `\n` is *not found* in a CRLF-body document (no line-ending normalization, REQ-009).

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

- [ ] Task 3.1: Unit tests for the match stage (0/1/n occurrences, `replace_all`, `new_str == old_str` guard, empty `old_str` guard, empty `new_str` deletion, the guard-order / fire-before-file-access cases, the pure-byte-exact CRLF pin per ACC-010)

- [ ] Task 3.2: Tool tests across all 12 whole-body domains (happy path, not found, multiple matches, invalid result, invalid id) mirroring `test_update.py`'s per-domain `_Case` harness and `SPECMGR_DOCS_DIR` temp fixture

- [ ] Task 3.3: Regression: the file is byte-unchanged on every failure path (including the invalid-result path)

- [ ] Task 3.4: Registration/schema test mirroring `TestUpdateRegistration` (live `mcp.list_tools()`: `type` enum == `WHOLE_BODY_DOMAINS`, `required == [id, type, old_str, new_str]`, `replace_all` optional bool default false, no `minLength` on `new_str`) plus the pinned `type="adr"` explicit-`ValueError` test (REQ-004)

#### Phase 4: Docs & Quality Gate

- [ ] Task 4.1: Update the `server.py` docstring, regenerate `docs/MCP.md` and `docs/api/`, update `AGENTS.md` (the `general/tools/` paragraph names `edit`, including its deliberate `ValueError` divergence from `update`'s `KeyError` for `type="adr"`)

- [ ] Task 4.2: Run ruff/pylint/vulture and the full test suite (phase-end quality gate)

## Progress

### Current Status

**As of 2026-09-26**: Phase 2 (Implementation) complete: `general/tools/edit.py` added — public `edit` dispatcher with the pinned guard order (`validate_id` → explicit pre-dispatch `ValueError` for unknown/`adr` `type` → identical-input → empty-`old_str`, all before any filesystem access), the domain-agnostic `_match_and_replace` stage-1 helper carrying the verbatim OC messages as plain `ValueError`s, 12 per-domain adapters holding the domain lock across read → match → validate → write (stage-2 wrapped, write strictly after validation, verbatim persist, `updated` bump, cache warm), its own `_ADAPTERS` drift assert, and the `@mcp.tool` registration — plus the `general/tools/__init__.py` wiring (import, `__all__`, package-docstring enumeration). The live MCP input schema was verified against the pinned contract (`required == [id, type, old_str, new_str]`, 12-value `type` enum excluding `adr`, optional `replace_all` defaulting to `false`, no `minLength` on `new_str`), and the phase-end quality gate is green (full suite: 3440 passed). Phase 3 (Tests) not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

#### 2026-09-26T22:29:21.223+02:00 - Phase 2 implementation-level refinements (D8, D9)

D8: the `@mcp.tool` description and the `general/tools/__init__.py` package-docstring enumeration name the supported domains by the explicit list (the `', '.join(WHOLE_BODY_DOMAINS)` interpolation in the description, the prose list in the docstring) rather than a cardinal "12 whole-body domains" — per `.specmgr/conventions.md`'s docstring-style rule against restating a generic tool's supported-domain count as a cardinal in prose (hardcoded counts silently go stale; the explicit list is self-verifying). This mirrors `update.py`'s own description, which likewise interpolates the domain list without a count. D9: the two longer pinned OC stage-1 messages (the not-found and the adapted empty-`old_str` message) are written in the source as implicit string concatenations (adjacent string literals) so every physical line stays within ruff's 120-char limit — the runtime string values are byte-identical to the pinned OC-parity strings (REQ-002), verified by the Phase 2 smoke run and to be pinned by the Phase 3 tests. No other deviation from the pinned contract: guard order, messages, plain-`ValueError` stage-1 / wrapped stage-2 split, lock scope, verbatim persist, cache warm, `_ADAPTERS` drift assert, and the explicit `ValueError` for unknown/`adr` `type` are implemented exactly as pinned.

#### 2026-09-26T21:18:14.835+02:00 - Refined design decisions (D1–D7)

D1: an empty `new_str` is a pure deletion, legal iff stage 2 validates (OC parity; no `minLength` on `new_str` in the MCP schema). D2: matching is pure byte-exact over `body_text` — no OC line-ending normalization, no BOM handling. D3: the four stage-1 failures (identical input, empty `old_str`, not found, multiple matches) raise plain `ValueError`s with the verbatim OC messages and no `domain tool (channel)` prefix; guard order `validate_id` → explicit `type` check → identical → empty `old_str`, all before any filesystem access; stage 2 stays wrapped exactly like `update`. D4: an unknown or `adr` `type` is an explicit pre-dispatch `ValueError` (the generic `validate` tool's precedent) — a deliberate divergence from `update`/`delete`/`set_classification`'s inherited `KeyError`. D5: updating the 12 per-domain `update_<d>` prompt flows to mention `edit` is a follow-up feature, out of scope here. D6: no new ADR — ADR 36905d5b (dispatch-only) plus 1af6787b (path safety) and bfd76370 (doc cache) cover the design (closes Task 1.2). D7: the OC error strings are pinned to opencode dev commit `236cfcbbc31530fde6a9e65318703f40adad8455` (`packages/opencode/src/tool/edit.ts`, last touched 2026-06-05, verified verbatim on 2026-09-26); parity targets OC's *runtime* strings (OC's own tool description text promises different messages than its runtime throws).

#### 2026-09-25T16:06:51.408Z - Confirmed tool design decisions

The tool signature is `edit(id, type, old_str, new_str, replace_all=False)` — `id` first, then `type`, consistent with every existing generic tool (`update`, `set_status`, `set_classification`, and `delete` all take `id` before `type`). No server-side "read before edit" enforcement: OC's is a client session-state convention, documented in the tool description instead. The `adr` domain is excluded, like the generic `update` tool. On success the frontmatter's `updated` field is bumped, like `update`. The failure messages are the OC `edit` tool's verbatim (quoted in Design Notes), including OC's parameter names (`oldString`/`newString`); OC's fuzzy matcher chain is not replicated (exact match only). The disk write happens only after the edited body validates as a whole document — never before. Persistence is verbatim, like `update`: no mdformat reformat on write (`format_text` during validation only); the `mdformat` tool is the normalization path.

### Related PRs / Commits

- [Issue #159](https://github.com/dfch/biz.dfch.SpecMgr/issues/159): tracking issue for this feature.
