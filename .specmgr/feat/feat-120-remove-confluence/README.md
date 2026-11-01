---
classification: null
created: '2026-09-10 19:09:06.111+02:00'
id: feat-120-remove-confluence
status: done
type: feat
updated: '2026-10-07T06:21:40.887Z'
version: 1.0.0
---

# Feature: Remove Confluence Tools from the MCP Server

## Plan

### Overview

The specmgr MCP server currently bundles Confluence-specific tools (`confluence_fetch`, `confluence_update`) and their prompts inside the cross-cutting `general/` package, added by feat-50-confluence (GitHub issue #50, ADR a156fdf9-052c-4f43-93a2-eeec04a91eac). Per GitHub issue #120 ("Remove confluence tools"), this mixes an unrelated domain (Confluence wiki/CMS page sync) into an MCP server whose purpose is managing system-specification artifacts (REQ/UC/TSK/QA/PRB/GOL/RSK/DEC/SOP/FEAT/VCR/SYSRS/ADR), and we do not want to mix the functionality of the MCP with different domains. This feature removes all Confluence-related source code, tests, documentation, environment variables, and the now-unused `httpx` dependency, and records the reversal as a new ADR that supersedes the original decision.

### Requirements

- REQ-001: Remove the `confluence_fetch` and `confluence_update` tool modules and their shared helper modules (`_confluence_config.py`, `_confluence_url.py`) from `general/tools/`, plus their packaged instruction data files under `general/data/`.
- REQ-002: Remove the `confluence_fetch` and `confluence_update` MCP prompt modules from `general/prompts/`.
- REQ-003: Remove all Confluence-related test files under `tests/general/tools/` and `tests/general/prompts/` (6 files, ~1774 lines).
- REQ-004: Update `general/tools/__init__.py` and `general/prompts/__init__.py` to drop the confluence imports, `__all__` entries, and docstring prose referencing them.
- REQ-005: Update `server.py`'s module docstring, `README.md`'s environment-variables section, and add a `CHANGELOG.md` `[Unreleased]` entry describing the removal, then regenerate `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/` via `specmgr docs`/`specmgr mcp-docs`, pruning any stale generated files left over from the deleted modules.
- REQ-006: Remove documentation of the `SPECMGR_CONFLUENCE_BASE_URL` and `SPECMGR_CONFLUENCE_BEARER` environment variables everywhere they are described.
- REQ-007: Remove the now-unused `httpx` dependency from `pyproject.toml`'s `mcp` extra and its corresponding `NOTICE` entry, after confirming no other module under `src/` imports it.
- REQ-008: Write a new ADR documenting this removal decision, and mark ADR a156fdf9-052c-4f43-93a2-eeec04a91eac as superseded by it using the generic `set_status` tool with `type="adr"`.

### Acceptance Criteria

- [x] ACC-001: No `confluence_fetch` or `confluence_update` tool or prompt is registered by the MCP server after startup.
- [x] ACC-002: The full quality gate is green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto` with no confluence-related test collection errors.
- [x] ACC-003: No remaining `import httpx`/`from httpx` reference exists anywhere under `src/`, and `httpx` no longer appears in `pyproject.toml` or `NOTICE`.
- [x] ACC-004: Regenerating docs (`specmgr docs`, `specmgr mcp-docs`) produces zero `git status` diff, confirming no stale confluence references remain in `docs/GENERATED.md`, `docs/MCP.md`, or `docs/api/`.
- [x] ACC-005: A new ADR documenting the removal exists, and ADR a156fdf9-052c-4f43-93a2-eeec04a91eac's status reads `superseded by <new ADR id>`.
- [x] ACC-006: `.specmgr/feat/feat-50-confluence/README.md` is left untouched as a historical record.
- [x] ACC-007: `README.md` no longer documents `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER`.

### Scope

#### Included

- Deleting `general/tools/confluence_fetch.py`, `general/tools/confluence_update.py`, `general/tools/_confluence_config.py`, `general/tools/_confluence_url.py`, `general/prompts/confluence_fetch.py`, `general/prompts/confluence_update.py`, and their `general/data/*.md` instruction files.
- Deleting `tests/general/tools/test_confluence_fetch.py`, `tests/general/tools/test_confluence_update.py`, `tests/general/tools/test__confluence_config.py`, `tests/general/tools/test__confluence_url.py`, `tests/general/prompts/test_confluence_fetch.py`, `tests/general/prompts/test_confluence_update.py`.
- Editing `general/tools/__init__.py`, `general/prompts/__init__.py`, `server.py` (docstring only), `README.md`, `CHANGELOG.md`, `pyproject.toml`, `NOTICE`.
- Regenerating `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/` and removing any now-orphaned generated files for the deleted modules.
- Writing a new ADR for this removal and superseding ADR a156fdf9-052c-4f43-93a2-eeec04a91eac.

#### Explicitly Out Of Scope

- Any other tool or prompt in `general/` (`mdformat`, the generic `update`/`set_status`/`set_classification`/`delete`/`validate` tools, `iso25010`/`dtais`/`rasci`/`version` resources) -- none of these are Confluence-specific and none are touched.
- Deleting or altering the historical `.specmgr/feat/feat-50-confluence/README.md` feature folder itself.
- The unrelated `atlassian_confluence_*` tools that come from a separate, external Atlassian MCP server -- those are not part of this codebase and are out of scope entirely.
- Introducing any replacement Confluence-sync mechanism; this feature only removes existing functionality.

### Design Notes

MCP tools in this server should stay domain-focused on system-specification artifacts (REQ/UC/TSK/QA/PRB/GOL/RSK/DEC/SOP/FEAT/VCR/SYSRS/ADR); Confluence page fetch/publish is a separate concern (wiki/CMS synchronization) that does not belong alongside spec-document management, and mixing it in blurs the server's single responsibility. The prior decision (ADR a156fdf9-052c-4f43-93a2-eeec04a91eac) is superseded rather than deleted, consistent with this repo's convention that ADRs are a permanent decision log; the new ADR should explicitly reference issue #120 as the trigger for the reversal.

### Related Decisions

- a156fdf9-052c-4f43-93a2-eeec04a91eac (ADR): original decision to rename `webfetch` to `confluence_fetch` and add `confluence_update`; to be marked superseded by this feature's new ADR once written.

### Task List

#### Phase 100: ADR

- [x] Task 100.100: Write a new ADR documenting the decision to remove the Confluence tools from the MCP server, referencing GitHub issue #120.
- [x] Task 100.110: Mark ADR a156fdf9-052c-4f43-93a2-eeec04a91eac as superseded by the new ADR via the generic `set_status` tool (`type="adr"`, `superseded_by=<new ADR id>`).

#### Phase 110: Removal

- [x] Task 110.100: Delete the confluence tool/prompt/helper/data source modules listed in Scope > Included.
- [x] Task 110.110: Delete the confluence test files listed in Scope > Included.
- [x] Task 110.120: Update `general/tools/__init__.py` and `general/prompts/__init__.py` imports, `__all__`, and docstrings to remove confluence references.
- [x] Task 110.130: Update `server.py`'s module docstring, `README.md`'s environment-variables section, and add a `CHANGELOG.md` `[Unreleased]` removal entry.
- [x] Task 110.140: Remove the `httpx` dependency from `pyproject.toml` and `NOTICE` after confirming it is unused elsewhere in `src/`.
- [x] Task 110.150: Regenerate `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/` via `specmgr docs`/`specmgr mcp-docs`, and remove any stale orphaned generated files.

#### Phase 120: Verification

- [x] Task 120.100: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`) and confirm it is green.
- [x] Task 120.110: Confirm `specmgr docs`/`specmgr mcp-docs` produce zero `git status` diff.
- [x] Task 120.120: Verify every Acceptance Criteria item, check them off, and set this feature's status to `done`.

## Progress

### Current Status

**As of 2026-09-10**: Feature complete. Phase 3 (Verification) confirmed every Acceptance Criteria item (ACC-001 through ACC-007) with concrete evidence: no `confluence_fetch`/`confluence_update` tool or prompt is registered (grep of `server.py` plus live `mcp._tool_manager._tools` introspection both confirm zero matches); the full quality gate is green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto` — 3248 tests passed, no confluence-related collection errors); no `import httpx`/`from httpx` reference remains under `src/`, and `httpx` no longer appears in `pyproject.toml` or `NOTICE`; re-running `specmgr docs`/`specmgr mcp-docs` after Phase 2 produced zero further `git status` diff; the new ADR `92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c` exists and ADR `a156fdf9-052c-4f43-93a2-eeec04a91eac`'s status reads `superseded by 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c`; `.specmgr/feat/feat-50-confluence/README.md` has zero diff and zero commits on this branch (verified via `git diff`/`git log` against the `dev` merge-base); and `README.md` no longer documents `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER`. All Acceptance Criteria and Task List items are checked off; feature status set to `done`.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-10 15:00:00.000Z - Phase 3 (Verification) complete

Ran the full quality gate from the repo root: `ruff format --check` (1644 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings), and `pytest -n auto` (3248 passed in ~21s, no confluence-related test collection errors) — all green. Re-ran `specmgr docs` and `specmgr mcp-docs`; `git status --porcelain` showed zero diff both before and after, confirming no stale confluence references remain in `docs/GENERATED.md`, `docs/MCP.md`, or `docs/api/`. Verified all seven Acceptance Criteria with concrete evidence: ACC-001 via `grep -rn "confluence" src/biz/dfch/specmgr/server.py` (zero matches) plus a live introspection of `server.mcp._tool_manager._tools` confirming neither `confluence_fetch` nor `confluence_update` is registered; ACC-002 via the quality gate above; ACC-003 via `grep -rn "import httpx\|from httpx" src/`, `grep -n httpx pyproject.toml`, and `grep -n httpx NOTICE` (all zero matches); ACC-004 via the doc-regeneration diff check above; ACC-005 via locating `docs/adr/92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c-*.md` and confirming the old ADR's frontmatter reads `status: superseded by 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c`; ACC-006 via `git diff $(git merge-base HEAD dev)...HEAD -- .specmgr/feat/feat-50-confluence/README.md` and `git log --oneline dev..HEAD -- .specmgr/feat/feat-50-confluence/README.md` (both empty); ACC-007 via `grep -n "SPECMGR_CONFLUENCE_BASE_URL\|SPECMGR_CONFLUENCE_BEARER" README.md` (zero matches). Checked off all 7 Acceptance Criteria and all 3 Phase 3 tasks, updated Current Status, and set the feature's frontmatter `status` to `done`. No `src/`/`tests/`/`docs/adr/` files were touched in this phase; `.specmgr/feat/feat-50-confluence/README.md` remains untouched.

### Related PRs / Commits

- [Issue #120](https://github.com/dfch/biz.dfch.SpecMgr/issues/120): tracking issue for this removal feature.
- [Issue #50](https://github.com/dfch/biz.dfch.SpecMgr/issues/50): original issue that added the Confluence tools now being removed.
