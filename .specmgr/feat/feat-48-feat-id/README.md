---
classification: null
created: '2026-09-02 10:32:05.764Z'
id: feat-48-feat-id
status: done
type: feat
updated: '2026-10-07T06:21:40.938Z'
version: 1.0.0
---

# Feature: create_feat caller-chosen id and set_feat_id rename tool

## Plan

### Overview

`create_feat` currently derives a feature's id automatically as
`feat-{max existing NNN + 1}-{slug}` and offers no way for a caller to
choose the id. This conflicts with the repo's own `feat-NNN-slug`
convention, where `NNN` is meant to be the GitHub issue number the
feature tracks — a feature for issue #28 can end up as `feat-37-...`
just because `feat-36-...` already exists. Because `feat` addresses
documents one-folder-per-id and enforces folder-name == frontmatter
`id`, there is currently no tool support for fixing this after the
fact either: it requires a manual folder rename plus a frontmatter
edit, and a half-done manual edit leaves the document unaddressable.

This feature (1) lets `create_feat` accept an optional, caller-chosen
`id` (a full `feat-NNN-slug`), defaulting to `feat-0-<slug>` (no
issue yet) when omitted, with no max+1 auto-generation fallback, and
failing before any write if the resulting id is already taken; and
(2) adds a new `set_feat_id(id, new_id)` tool to safely rename an
existing feature's id/folder afterwards (e.g. once an issue number is
known), keeping the document addressable end-to-end.

### Requirements

- REQ-001: `create_feat` must accept an optional `id` parameter carrying a full, well-formed `feat-NNN-slug` value.
- REQ-002: When `id` is omitted, `create_feat` must default the number to `0` (i.e. `feat-0-<slug-from-title>`), with no max+1 auto-generation fallback.
- REQ-003: `create_feat` must fail, before any filesystem write, if the resulting id/folder (caller-supplied or defaulted) already exists on disk.
- REQ-004: `create_feat` must validate a caller-supplied `id` against the `feat-NNN-slug` shape before accepting it.
- REQ-005: A new feat-domain tool `set_feat_id(id, new_id)` must rename an existing feature's id: validate `new_id`'s shape, refuse if the target folder already exists, rename `<base>/<id>/` to `<base>/<new_id>/`, and rewrite the README frontmatter `id` to `new_id`.
- REQ-006: `set_feat_id` must leave the body content byte-identical and must bump `updated` to the current timestamp.
- REQ-007: `set_feat_id` must perform its rename+rewrite under the feat domain's own locking so it never races with a concurrent `create_feat`/`update`/`set_status`/`delete` on the same id.
- REQ-008: `set_feat_id` must not update or search for references to the old id in any other document.
- REQ-009: The `feat` domain's packaged prompt instructions, `AGENTS.md`'s `feat/` bullet, and `server.py`'s module docstring must be reviewed and updated to describe the new `create_feat` parameter and the new `set_feat_id` tool.

### Acceptance Criteria

- [x] ACC-001: `create_feat(content)` with no `id` creates `feat-0-<slug>` when no `feat-0-*` folder exists yet.
- [x] ACC-002: `create_feat(content, id="feat-28-get-update")` creates exactly that folder/id when not already taken.
- [x] ACC-003: `create_feat` raises before writing anything when the resulting id (given or defaulted) already exists on disk.
- [x] ACC-004: `create_feat` raises `ValueError` before writing anything when a caller-supplied `id` does not match the `feat-NNN-slug` shape.
- [x] ACC-005: `set_feat_id("feat-0-get-update", "feat-42-get-update")` renames the folder, updates the frontmatter `id`, bumps `updated`, and leaves the body otherwise byte-identical.
- [x] ACC-006: `set_feat_id` raises (without renaming) when `new_id` already exists as a folder.
- [x] ACC-007: `set_feat_id` raises `FeatNotFoundError` when `id` does not resolve to an existing feature.
- [x] ACC-008: `set_feat_id` is registered as an `@mcp.tool()` and appears in `server.py`'s docstring/registration and in `docs/MCP.md` after regeneration.
- [x] ACC-009: The packaged `feat` prompt instructions, `AGENTS.md`, and `server.py`'s docstring are updated to mention the optional `id` parameter and `set_feat_id`.
- [x] ACC-010: The full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) passes, including new unit tests for `create_feat(id=...)` and `set_feat_id`.

### Scope

#### Included

- `create_feat` signature change: optional `id: str | None = None` parameter.
- Validation of a caller-supplied `id` (mirroring `general/tools/_path_safety.assert_feat_id`) before any lock/filesystem access.
- Pre-write existence check for both caller-supplied and defaulted ids.
- New `feat/tools/set_feat_id.py` tool: validate, existence-check, rename, frontmatter `id` rewrite, `updated` bump, locking.
- Registration of `set_feat_id` in `feat/tools/__init__.py` and in `server.py`'s domain docstring.
- Review/update of the `feat` domain's packaged prompt instruction files (`create_feat`/`update_feat`) to describe both changes.
- Update of `AGENTS.md`'s `feat/` bullet (tool count/list, mention of `set_feat_id`) and `server.py`'s own module docstring.
- Regeneration of `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` as needed.
- Unit tests covering both changes (happy path + failure paths + locking).

#### Explicitly Out Of Scope

- Updating other documents' textual references to a feature's old id after a `set_feat_id` rename.
- Auto-detecting/fetching the GitHub issue number to seed `NNN` automatically (the caller must supply the full id explicitly).
- Bulk migration or renumbering of any existing `feat-*` folders.
- Any `update_feat`/`set_status_feat` tools of feat's own — id changes stay exclusively in `set_feat_id`; whole-body/line-range updates and status changes continue through the generic `update`/`set_status` tools.
- Partial-id matching or directory-scan-based id resolution in `find_feat_path_by_id` (unchanged).

### Dependencies

#### Depends On

- ADR 8cf940c5-3100-485c-a12d-14b59b631712: establishes that `feat`'s id is a chosen `feat-NNN-slug` folder name, not a server-generated UUID — this feature builds directly on that addressing convention.
- ADR e369ee2e-3353-4f92-991c-6367d76d832e: establishes the `.specmgr/feat/feat-NNN-slug/README.md` convention where `NNN` is the GitHub issue number — the motivating convention this feature lets `create_feat`/`set_feat_id` actually honor.

### Related Decisions

- ADR 8cf940c5-3100-485c-a12d-14b59b631712: feat's id genuinely deviates from every other domain's UUID convention (chosen `feat-NNN-slug` folder name).
- ADR e369ee2e-3353-4f92-991c-6367d76d832e: `.specmgr` feature-folder convention, `NNN` = GitHub issue number.

### Task List

#### Phase 100: Design & Validation Helpers

- [x] Task 100.100: Confirm `assert_feat_id` (`general/tools/_path_safety.py`) is reusable for validating both `create_feat`'s optional `id` and `set_feat_id`'s `new_id`, or decide a feat-local validator is preferable.
- [x] Task 100.110: Design `set_feat_id`'s locking strategy (`feat_lock`/`feat_create_lock` ordering) to avoid races with `create_feat` and other mutations.

#### Phase 110: create_feat optional id parameter

- [x] Task 110.100: Add `id: str | None = None` to `create_feat`; validate shape when given.
- [x] Task 110.110: Change id derivation: `id` given -> use as-is; `id` omitted -> `feat-0-<slug-from-title>`, removing the max+1 auto-increment fallback from the default path.
- [x] Task 110.120: Add a pre-write existence check for the resulting id/folder; raise before any write side effect.
- [x] Task 110.130: Update `create_feat.py`'s docstring/description for the new parameter and failure mode.

#### Phase 120: set_feat_id tool

- [x] Task 120.100: Implement `feat/tools/set_feat_id.py`: validate `new_id` shape, resolve current id via `find_feat_path_by_id`, refuse if `new_id` folder exists, rename folder, rewrite frontmatter `id` + `updated`, preserve body byte-for-byte.
- [x] Task 120.110: Register `set_feat_id` as `@mcp.tool()` and export from `feat/tools/__init__.py`.
- [x] Task 120.120: Add `server.py` docstring entry for `set_feat_id` (feat now has 8 tools, not 7).

#### Phase 130: Prompts and documentation

- [x] Task 130.100: Review/update the `feat` create-instructions packaged text to mention the optional `id` parameter and the no-auto-increment default.
- [x] Task 130.110: Review/update the `feat` update-instructions packaged text to mention `set_feat_id` as the renumbering path.
- [x] Task 130.120: Update `AGENTS.md`'s `feat/` bullet (tool count/list, mention of `set_feat_id`).
- [x] Task 130.130: Regenerate `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md`; verify no drift.

#### Phase 140: Tests

- [x] Task 140.100: Unit tests for `create_feat(id=...)` happy path, shape-validation failure, and existing-id collision (before any write).
- [x] Task 140.110: Unit tests for `create_feat()` default `feat-0-<slug>` path with no auto-increment.
- [x] Task 140.120: Unit tests for `set_feat_id` happy path (rename + frontmatter rewrite + `updated` bump + byte-identical body).
- [x] Task 140.130: Unit tests for `set_feat_id` failure paths (target exists, source not found, invalid `new_id` shape).
- [x] Task 140.140: Run full test suite, ruff, vulture, pylint per `AGENTS.md` developer commands.

#### Phase 150: Release

- [x] Task 150.100: Update `CHANGELOG.md`'s `[Unreleased]` section.
- [x] Task 150.110: Open PR referencing issue #48, ensure pre-commit hooks pass.

## Progress

### Current Status

**As of 2026-09-02**: All 6 phases complete. Every acceptance criterion
(ACC-001 through ACC-010) is verified and checked off. PR #58
(<https://github.com/dfch/biz.dfch.SpecMgr/pull/58>, branch `feat-48-feat-id`
→ `dev`) is open, referencing issue #48, with every commit on the branch
having passed its pre-commit hooks (ruff format/check, vulture, full
unittest suite, `specmgr docs`/`mcp-docs`/coverage-badge). The feature is
now awaiting external PR review/CI; nothing further remains in this
document's own scope.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 18:00:00.000Z - Phase 6: Release (Task 6.2, PR opened)
Completed Task 6.2. PR #58
(<https://github.com/dfch/biz.dfch.SpecMgr/pull/58>) is now open for branch
`feat-48-feat-id` → `dev`, referencing GitHub issue #48; every commit on
the branch passed its pre-commit hooks (ruff format/check, vulture, the
full unittest suite, `specmgr docs`/`mcp-docs`/coverage-badge). Checked
off ACC-001 (re-confirmed genuinely covered by the pre-existing
`test_id_defaults_to_feat_0_when_base_dir_is_empty` in
`tests/feat/tools/test_create_feat.py`, per Phase 5's Updates entry below)
and Task 6.2 itself. This closes out this feature's own plan-tracking —
implementation, tests, and documentation are all complete; only external
PR review/merge remains, which is outside this document's own scope.

### Decisions Made

#### 2026-09-02 00:00:00.000Z : Task 1.1

`assert_feat_id` (`general/tools/_path_safety.py`)
#### 2026-09-02 00:00:00.000Z : Task 1.2

`set_feat_id(id, new_id)` acquires
#### 2026-09-02 00:00:00.000Z : Task 2.3, Phase 2

The pre-write existence check tests
#### 2026-09-02 00:00:00.000Z : Task 3.1, Phase 3

`set_feat_id` obtains the exact,
