---
classification: null
created: '2026-09-10 19:09:06.111+02:00'
id: feat-120-remove-confluence
status: planning
type: feat
updated: '2026-09-10 19:09:06.111+02:00'
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

- [ ] ACC-001: No `confluence_fetch` or `confluence_update` tool or prompt is registered by the MCP server after startup.
- [ ] ACC-002: The full quality gate is green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto` with no confluence-related test collection errors.
- [ ] ACC-003: No remaining `import httpx`/`from httpx` reference exists anywhere under `src/`, and `httpx` no longer appears in `pyproject.toml` or `NOTICE`.
- [ ] ACC-004: Regenerating docs (`specmgr docs`, `specmgr mcp-docs`) produces zero `git status` diff, confirming no stale confluence references remain in `docs/GENERATED.md`, `docs/MCP.md`, or `docs/api/`.
- [ ] ACC-005: A new ADR documenting the removal exists, and ADR a156fdf9-052c-4f43-93a2-eeec04a91eac's status reads `superseded by <new ADR id>`.
- [ ] ACC-006: `.specmgr/feat/feat-50-confluence/README.md` is left untouched as a historical record.
- [ ] ACC-007: `README.md` no longer documents `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER`.

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

#### Phase 1: ADR

- [x] Task 1.1: Write a new ADR documenting the decision to remove the Confluence tools from the MCP server, referencing GitHub issue #120.
- [x] Task 1.2: Mark ADR a156fdf9-052c-4f43-93a2-eeec04a91eac as superseded by the new ADR via the generic `set_status` tool (`type="adr"`, `superseded_by=<new ADR id>`).

#### Phase 2: Removal

- [x] Task 2.1: Delete the confluence tool/prompt/helper/data source modules listed in Scope > Included.
- [x] Task 2.2: Delete the confluence test files listed in Scope > Included.
- [x] Task 2.3: Update `general/tools/__init__.py` and `general/prompts/__init__.py` imports, `__all__`, and docstrings to remove confluence references.
- [x] Task 2.4: Update `server.py`'s module docstring, `README.md`'s environment-variables section, and add a `CHANGELOG.md` `[Unreleased]` removal entry.
- [x] Task 2.5: Remove the `httpx` dependency from `pyproject.toml` and `NOTICE` after confirming it is unused elsewhere in `src/`.
- [x] Task 2.6: Regenerate `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/` via `specmgr docs`/`specmgr mcp-docs`, and remove any stale orphaned generated files.

#### Phase 3: Verification

- [ ] Task 3.1: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`) and confirm it is green.
- [ ] Task 3.2: Confirm `specmgr docs`/`specmgr mcp-docs` produce zero `git status` diff.
- [ ] Task 3.3: Verify every Acceptance Criteria item, check them off, and set this feature's status to `done`.

## Progress

### Current Status

**As of 2026-09-10**: Phase 2 (Removal) is complete. All Confluence-specific source, test, prompt, and packaged-data modules (`confluence_fetch`/`confluence_update` tools and prompts, `_confluence_config.py`/`_confluence_url.py` helpers, their instruction data files, and their 6 test files) were deleted; `general/tools/__init__.py`, `general/prompts/__init__.py`, and `general/__init__.py` had their imports/`__all__`/docstrings updated to drop confluence references; `server.py`'s module docstring, `README.md`'s environment-variables section, and `CHANGELOG.md`'s `[Unreleased]` section were updated; the now-unused `httpx` dependency was removed from `pyproject.toml`'s `mcp` extra, `NOTICE`'s corresponding license block, and `uv.lock` (via `uv lock`/`uv sync --all-extras`); and `docs/GENERATED.md`/`docs/MCP.md`/`docs/api/` were regenerated, auto-pruning the 6 orphaned `docs/api/*confluence*.md` pages. The full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, 3248 tests) is green, and re-running `specmgr docs`/`specmgr mcp-docs` produces no further diff. `.specmgr/feat/feat-50-confluence/README.md` was left untouched. Phase 3 (Verification) is next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-10 14:00:00.000Z - Phase 2 (Removal) complete

Deleted all Confluence-specific source modules (`general/tools/confluence_fetch.py`, `general/tools/confluence_update.py`, `general/tools/_confluence_config.py`, `general/tools/_confluence_url.py`, `general/prompts/confluence_fetch.py`, `general/prompts/confluence_update.py`, and their two `general/data/*.md` instruction files) and all 6 corresponding test files under `tests/general/tools/` and `tests/general/prompts/`. Updated `general/tools/__init__.py` and `general/prompts/__init__.py` (imports, `__all__`, docstrings) and `general/__init__.py`'s own docstring to drop confluence mentions. Removed the confluence-related docstring paragraphs from `server.py` (tools and prompts sections) without touching any executable code. Removed the `confluence_fetch` environment-variables bullet from `README.md`. Added a `### Removed` entry under `CHANGELOG.md`'s `[Unreleased]` heading referencing GitHub issue #120 and ADR 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c. Confirmed via `grep -rn "httpx" src/ --include=*.py` that no remaining module imports `httpx` after the deletions, then removed `"httpx>=0.27",` from `pyproject.toml`'s `mcp` extra and the entire `httpx (optional "mcp" extra)` BSD-3-Clause block from `NOTICE`. Ran `uv lock` (network-accessible in this environment) followed by `uv sync --all-extras`, which removed `httpx`/`httpcore` from `uv.lock` and the local environment. Regenerated `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/` via `specmgr docs`/`specmgr mcp-docs`; the doc generator auto-pruned the 6 now-orphaned `docs/api/*confluence*.md` pages, and re-running both commands afterward produced no further diff. Quality gate: `ruff format --check` (1644 files formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings, no confluence-related whitelist entries existed), and `pytest -n auto` (3248 passed) all green. Left `.specmgr/feat/feat-50-confluence/README.md` untouched.

#### 2026-09-10 13:00:00.000Z - Phase 1 (ADR) complete

Created a new ADR, "Remove the Confluence tools (`confluence_fetch`, `confluence_update`) from the MCP server" (id `92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c`), documenting the decision to remove the Confluence-specific MCP tools per GitHub issue #120, and explicitly superseding ADR a156fdf9-052c-4f43-93a2-eeec04a91eac. Marked the old ADR's status as `superseded by 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c` via the generic `set_status` tool. Regenerated `docs/adr/README.md` via `specmgr adr-toc`. No `src/`/`tests/` files were touched (Phase 2's job).

#### 2026-09-10 12:00:00.000Z - Created

Drafted the feature plan for removing the Confluence tools (`confluence_fetch`, `confluence_update`) and their supporting code, tests, docs, and dependency from the MCP server, per GitHub issue #120. A prior codebase inventory confirmed all Confluence-specific code lives in `general/tools/` and `general/prompts/`, added by feat-50-confluence (issue #50, ADR a156fdf9-052c-4f43-93a2-eeec04a91eac). No implementation work has started yet.

### Related PRs / Commits

- [Issue #120](https://github.com/dfch/biz.dfch.SpecMgr/issues/120): tracking issue for this removal feature.
- [Issue #50](https://github.com/dfch/biz.dfch.SpecMgr/issues/50): original issue that added the Confluence tools now being removed.
