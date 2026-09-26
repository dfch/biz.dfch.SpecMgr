---
classification: null
created: '2026-09-25T18:10:37.035+02:00'
id: feat-159-edit
status: planning
type: feat
updated: '2026-09-26T17:43:18.660+02:00'
version: 1.0.0
---

# Feature: Add specmgr edit tool (as seen in OC)

## Plan

### Overview

Adds a new generic `edit` MCP tool in `general/tools/` that matches `old_str`
exactly in the frontmatter-stripped body of an existing document and rewrites
it with `new_str`, dispatched across all 12 whole-body domains
(`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`).
The signature/call behaviour mirrors the OpenCode `edit` tool (exact match,
optional `replace_all`, the same error messages). Internally the
implementation is 2-fold: (1) the match must succeed (old_str found; unique
unless `replace_all`), and (2) the resulting document must still validate as a
whole — the document is written to disk only if the edit result still makes a
valid document, and if either stage fails, nothing is written. Closes GitHub
issue #159.

### Requirements

- REQ-001: The `edit` tool exposes the same signature/call behaviour as the OC `edit` tool: an exact match of `old_str` rewritten to `new_str`, with an optional `replace_all` flag; `new_str` must differ from `old_str`.

- REQ-002: The failure error messages are the same as with the OC `edit` tool (quoted verbatim in Design Notes): the OC "could not find oldString" message when `old_str` is not found, and the OC "found multiple matches" message when `old_str` matches more than once without `replace_all`.

- REQ-003: The implementation is 2-fold, and the document is written to disk only if both stages pass: the exact match must succeed first (old_str found; unique unless `replace_all`), then the edited body must validate as a whole document; on any failure nothing is written.

- REQ-004: The tool dispatches on `type` across the 12 whole-body domains like the generic `update` tool (per-domain adapters, same locks, same id resolution, same domain not-found errors); `adr` is excluded.

- REQ-005: `id` is validated via `_path_safety.validate_id` before any filesystem access, and the resolved path is confined to the domain's own base directory via `assert_within`.

- REQ-006: On success the existing frontmatter is carried over with only `updated` bumped, the edited body is persisted verbatim (no mdformat reformat on write — `format_text` is applied during validation only, exactly like `update`), the tool returns the updated frontmatter only, and it warms the domain doc cache, like `update`.

- REQ-007: The tool is registered in `server.py`, listed in its docstring, mirrored in the regenerated `docs/MCP.md`, and documented in `AGENTS.md`.

### Acceptance Criteria

- [ ] ACC-001: A unique exact match rewrites the body and returns the frontmatter with `updated` bumped.

- [ ] ACC-002: A missing `old_str` raises the OC not-found error verbatim (`Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.`); the file is byte-unchanged.

- [ ] ACC-003: Multiple matches without `replace_all` raise the OC multiple-matches error verbatim (`Found multiple matches for oldString. Provide more surrounding context to make the match unique.`), file byte-unchanged; with `replace_all` all occurrences are rewritten.

- [ ] ACC-004: An edit that yields an invalid document raises the wrapped validation error and nothing is written — the disk write happens only after whole-document validation passes.

- [ ] ACC-005: An invalid or path-injection `id` raises `ValueError` before any filesystem access, in every domain.

- [ ] ACC-006: All 12 whole-body domains are accepted; `type="adr"` is rejected as out of vocabulary.

- [ ] ACC-007: The `server.py` docstring, `docs/MCP.md`, and `AGENTS.md` reflect the new tool (drift checks pass).

### Scope

#### Included

- The new generic `edit` tool in `general/tools/` (dispatch-only, 12 whole-body domains)

- Exact-match semantics with an optional `replace_all` flag; OC-parity signature and error messages

- The 2-fold validation (match stage, then whole-document validation of the edited body)

- Path safety, domain lock, frontmatter carry-over with `updated` bump, doc-cache warming

- Unit/tool tests and documentation (`server.py` docstring, `docs/MCP.md`, `AGENTS.md`)

#### Explicitly Out Of Scope

- Fuzzy/regex/partial string matching (exact match only; OC's 9-stage fallback matcher chain is not replicated)

- Addressing or mutating the YAML frontmatter (body only)

- The `adr` domain (excluded, like the generic `update` tool)

- Server-side "read before edit" enforcement (OC's is a client session-state convention; documented only)

- `offset`/`limit` line-range addressing (the generic `update` tool's territory)

### Design Notes

The tool mirrors the generic `update` adapter shape (`general/tools/update.py`): the public dispatcher validates `id` via `_path_safety.validate_id` and guards `new_str != old_str` before any filesystem access, then dispatches to private per-domain `_edit_<d>` adapters. Each adapter takes the domain lock, resolves the document via the domain's `load_by_id`, confines the path with `assert_within`, and reads the on-disk body — the same frontmatter-stripped text `get_<d>(id, raw=True)` returns, consistent with `update`'s range-coordinate contract.

Stage 1 (match) counts exact `old_str` occurrences in that raw body: 0 → the OC not-found error; >1 without `replace_all` → the OC multiple-matches error. The two verbatim OC error strings (quoted from opencode's `packages/opencode/src/tool/edit.ts`, dev branch, 2026-09-25) are:

```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
Found multiple matches for oldString. Provide more surrounding context to make the match unique.
```

The identical-input guard uses OC's verbatim string `No changes to apply: oldString and newString are identical.`, and the empty-`old_str` guard follows OC's `oldString cannot be empty...` message, adapted to name specmgr's `update` tool instead of OC's `write` tool. The verbatim strings deliberately retain OC's parameter names (`oldString`/`newString`), per the issue's "same error message" ask; both guards fire before any filesystem access. OC's 9-stage fuzzy matcher chain is deliberately not replicated — this tool is exact-match only.

Stage 2 (validate) applies the edit (single or all occurrences) and validates the edited body as a whole document via `<Domain>.from_text(format_text(edited))` under `wrap_tool_errors(domain=..., tool="edit", channel=BODY_CHANNEL)`; the disk write via the domain's `write_<d>_file` happens strictly after that validation succeeds — the document is only written to disk if the result of the edit still makes a valid document. On success the frontmatter is carried over with only `updated` bumped, the edited body is persisted verbatim — no mdformat reformat on write, exactly like `update` (`write_<d>_file` embeds the body verbatim and never reformats/re-renders it; `format_text` is applied during validation only) — and the cache is warmed via the domain's `read_<d>`. The on-disk document is therefore mdformat-normalized after a successful edit iff it was normalized before and `new_str` is itself mdformat-normalized text; the dedicated `mdformat` tool/CLI remains the normalization path. On any failure (either stage) nothing is written and the file is byte-unchanged.

The `set(_ADAPTERS) == set(WHOLE_BODY_DOMAINS)` drift guard (feat-125-domain-lists) is reused as-is; no change to the shared domain vocabulary is needed. OC's read-before-edit session-state enforcement is deliberately not replicated server-side (no enforcement) and is instead documented as a client convention in the tool description.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 (dispatch-only): `edit` is one generic tool with per-domain adapters, not per-domain `edit_<d>` tools.

- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d (path safety): `validate_id` before any filesystem access and `assert_within` base-directory confinement apply to the new tool.

- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d (doc cache): the write path warms the domain cache after a successful edit.

- feat-22-consolidate-mutation-tools: precedent for the generic whole-body mutation tool (`update`) that this tool mirrors.

### Task List

#### Phase 1: Design

- [ ] Task 1.1: Draft the tool contract (signature, OC error parity, 2-fold behaviour) into this feature

- [ ] Task 1.2: Decide whether a full ADR is required or the dispatch-only convention (ADR 36905d5b) suffices; record in Decisions Made

#### Phase 2: Implementation

- [ ] Task 2.1: Add `general/tools/edit.py` — public dispatcher plus 12 per-domain adapters

- [ ] Task 2.2: Implement stage-1 exact-match logic with the verbatim OC error messages (not found; multiple matches; identical/empty guards)

- [ ] Task 2.3: Implement stage-2 whole-document validation with the disk write strictly after validation passes, frontmatter carry-over (`updated` bump), verbatim persist, cache warm

#### Phase 3: Tests

- [ ] Task 3.1: Unit tests for the match stage (0/1/n occurrences, `replace_all`, `new_str == old_str` guard, empty `old_str` guard)

- [ ] Task 3.2: Tool tests across all 12 whole-body domains (happy path, not found, multiple matches, invalid result, invalid id)

- [ ] Task 3.3: Regression: the file is byte-unchanged on every failure path (including the invalid-result path)

#### Phase 4: Docs & Quality Gate

- [ ] Task 4.1: Update the `server.py` docstring, regenerate `docs/MCP.md` and `docs/api/`, update `AGENTS.md`

- [ ] Task 4.2: Run ruff/pylint/vulture and the full test suite (phase-end quality gate)

## Progress

### Current Status

**As of 2026-09-25**: Feature drafted for GitHub issue #159; design decisions confirmed with the author (including the verbatim OC error strings pinned from opencode's source); implementation not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26T17:32:00.000+02:00 - Renamed the feature and tool to `edit` throughout

The feature was renamed `feat-159-replace` to `feat-159-edit` (via `set_feat_id`) and every plan-section reference to the earlier draft name was rewritten to `edit`, matching issue #159's own title and signature; the `replace_all` parameter name is retained because it is part of the issue's signature and the OC `edit` tool's own API (REQ-001 parity). The historical entries below are preserved unchanged.

#### 2026-09-25T18:34:14.067+02:00 - Clarified OC tool name and mdformat contract

The OC counterpart is the `edit` tool, not a `replace` tool (opencode's `packages/opencode/src/tool/edit.ts` registers it via `Tool.define("edit", ...)`); issue #159's "replace" wording refers to its exact-match string-replacement behaviour, and this document now names OC's tool `edit` throughout (Overview, REQ-001, REQ-002, Decisions Made). The persistence contract is also now explicit (REQ-006, Design Notes): the replaced body is persisted verbatim with no mdformat reformat on write — exactly like `update`, which applies `format_text` during validation only; the `mdformat` tool remains the normalization path.

#### 2026-09-25T16:06:51.408Z - Created

Feature drafted for GitHub issue #159 (specmgr replace tool with OC parity). Mandatory plan sections populated from the issue; design decisions (signature, error parity, 2-fold validation, adr exclusion) confirmed with the author. The OC failure messages were pinned verbatim from opencode's `packages/opencode/src/tool/edit.ts` `replace()` (dev branch) rather than from the tool description text.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-25T16:06:51.408Z - Confirmed tool design decisions

The tool signature is `edit(id, type, old_str, new_str, replace_all=False)` — `id` first, then `type`, consistent with every existing generic tool (`update`, `set_status`, `set_classification`, and `delete` all take `id` before `type`). No server-side "read before edit" enforcement: OC's is a client session-state convention, documented in the tool description instead. The `adr` domain is excluded, like the generic `update` tool. On success the frontmatter's `updated` field is bumped, like `update`. The failure messages are the OC `edit` tool's verbatim (quoted in Design Notes), including OC's parameter names (`oldString`/`newString`); OC's fuzzy matcher chain is not replicated (exact match only). The disk write happens only after the edited body validates as a whole document — never before. Persistence is verbatim, like `update`: no mdformat reformat on write (`format_text` during validation only); the `mdformat` tool is the normalization path.

### Related PRs / Commits

- [Issue #159](https://github.com/dfch/biz.dfch.SpecMgr/issues/159): tracking issue for this feature.
