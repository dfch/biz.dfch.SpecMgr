---
created: '2026-09-02T10:32:05.764646'
id: feat-48-feat-id
status: planning
type: feat
updated: '2026-09-02T13:15:00.000000'
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

- [ ] ACC-001: `create_feat(content)` with no `id` creates `feat-0-<slug>` when no `feat-0-*` folder exists yet.
- [ ] ACC-002: `create_feat(content, id="feat-28-get-update")` creates exactly that folder/id when not already taken.
- [ ] ACC-003: `create_feat` raises before writing anything when the resulting id (given or defaulted) already exists on disk.
- [ ] ACC-004: `create_feat` raises `ValueError` before writing anything when a caller-supplied `id` does not match the `feat-NNN-slug` shape.
- [ ] ACC-005: `set_feat_id("feat-0-get-update", "feat-42-get-update")` renames the folder, updates the frontmatter `id`, bumps `updated`, and leaves the body otherwise byte-identical.
- [ ] ACC-006: `set_feat_id` raises (without renaming) when `new_id` already exists as a folder.
- [ ] ACC-007: `set_feat_id` raises `FeatNotFoundError` when `id` does not resolve to an existing feature.
- [ ] ACC-008: `set_feat_id` is registered as an `@mcp.tool()` and appears in `server.py`'s docstring/registration and in `docs/MCP.md` after regeneration.
- [ ] ACC-009: The packaged `feat` prompt instructions, `AGENTS.md`, and `server.py`'s docstring are updated to mention the optional `id` parameter and `set_feat_id`.
- [ ] ACC-010: The full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) passes, including new unit tests for `create_feat(id=...)` and `set_feat_id`.

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

#### Phase 1: Design & Validation Helpers

- [x] Task 1.1: Confirm `assert_feat_id` (`general/tools/_path_safety.py`) is reusable for validating both `create_feat`'s optional `id` and `set_feat_id`'s `new_id`, or decide a feat-local validator is preferable.
- [x] Task 1.2: Design `set_feat_id`'s locking strategy (`feat_lock`/`feat_create_lock` ordering) to avoid races with `create_feat` and other mutations.

#### Phase 2: create_feat optional id parameter

- [ ] Task 2.1: Add `id: str | None = None` to `create_feat`; validate shape when given.
- [ ] Task 2.2: Change id derivation: `id` given -> use as-is; `id` omitted -> `feat-0-<slug-from-title>`, removing the max+1 auto-increment fallback from the default path.
- [ ] Task 2.3: Add a pre-write existence check for the resulting id/folder; raise before any write side effect.
- [ ] Task 2.4: Update `create_feat.py`'s docstring/description for the new parameter and failure mode.

#### Phase 3: set_feat_id tool

- [ ] Task 3.1: Implement `feat/tools/set_feat_id.py`: validate `new_id` shape, resolve current id via `find_feat_path_by_id`, refuse if `new_id` folder exists, rename folder, rewrite frontmatter `id` + `updated`, preserve body byte-for-byte.
- [ ] Task 3.2: Register `set_feat_id` as `@mcp.tool()` and export from `feat/tools/__init__.py`.
- [ ] Task 3.3: Add `server.py` docstring entry for `set_feat_id` (feat now has 8 tools, not 7).

#### Phase 4: Prompts and documentation

- [ ] Task 4.1: Review/update the `feat` create-instructions packaged text to mention the optional `id` parameter and the no-auto-increment default.
- [ ] Task 4.2: Review/update the `feat` update-instructions packaged text to mention `set_feat_id` as the renumbering path.
- [ ] Task 4.3: Update `AGENTS.md`'s `feat/` bullet (tool count/list, mention of `set_feat_id`).
- [ ] Task 4.4: Regenerate `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md`; verify no drift.

#### Phase 5: Tests

- [ ] Task 5.1: Unit tests for `create_feat(id=...)` happy path, shape-validation failure, and existing-id collision (before any write).
- [ ] Task 5.2: Unit tests for `create_feat()` default `feat-0-<slug>` path with no auto-increment.
- [ ] Task 5.3: Unit tests for `set_feat_id` happy path (rename + frontmatter rewrite + `updated` bump + byte-identical body).
- [ ] Task 5.4: Unit tests for `set_feat_id` failure paths (target exists, source not found, invalid `new_id` shape).
- [ ] Task 5.5: Run full test suite, ruff, vulture, pylint per `AGENTS.md` developer commands.

#### Phase 6: Release

- [ ] Task 6.1: Update `CHANGELOG.md`'s `[Unreleased]` section.
- [ ] Task 6.2: Open PR referencing issue #48, ensure pre-commit hooks pass.

## Progress

### Current Status

**As of 2026-09-02**: Phase 1 (Design & Validation Helpers) done. Both design
questions the plan flagged are settled and recorded below; no `src/` code
changes yet — implementation starts in Phase 2.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 13:15:00.000Z — Phase 1: Design & Validation Helpers

Completed Task 1.1 and Task 1.2 (design-only, no `src/` changes). Confirmed
`general/tools/_path_safety.assert_feat_id` is directly reusable, unchanged,
for validating both `create_feat`'s optional `id` and `set_feat_id`'s
`new_id` — no feat-local validator needed. Designed `set_feat_id`'s locking
order (`feat_create_lock()` outermost, `feat_lock(id)` nested inside) and
noted that `create_feat`'s Phase 2 change must also hold `feat_create_lock()`
around its existence-check for a caller-supplied id. See Decisions Made below
for the full rationale.

#### 2026-09-02 12:00:00.000Z — Drafted feature plan from issue #48

Captured the two changes issue #48 asks for (`create_feat`'s optional caller-chosen id with no auto-increment fallback, and a new `set_feat_id` rename tool) into a Plan with requirements, acceptance criteria, scope, and a six-phase task list. No code changes made yet.

### Decisions Made

- **2026-09-02 (Task 1.1)**: `assert_feat_id` (`general/tools/_path_safety.py`)
  is reused directly, unchanged, for validating both `create_feat`'s optional
  `id` parameter and `set_feat_id`'s `new_id` parameter — no feat-local
  validator is introduced. Rationale: both values must satisfy the exact same
  `feat-NNN-slug` shape (`^feat-[0-9]+-[a-z0-9-]+$`) this function already
  enforces; `feat/tools/create_feat.py` and the future
  `feat/tools/set_feat_id.py` will import it via
  `from ...general.tools._path_safety import assert_feat_id`.
- **2026-09-02 (Task 1.2)**: `set_feat_id(id, new_id)` acquires
  `feat_create_lock()` first (outermost), then `feat_lock(id)` nested inside
  it, wrapping the whole "resolve `id` -> check `new_id` doesn't already
  exist -> rename folder -> rewrite frontmatter" sequence. Rationale:
  `feat_create_lock()` is already the outermost (and only) lock
  `create_feat` acquires today (confirmed by reading `create_feat.py`, and by
  grepping every `feat_lock`/`feat_create_lock` call site in
  `general/tools/update.py`, `set_status.py`, and `delete.py` — none of those
  acquire `feat_lock` before `feat_create_lock`, so no other tool establishes
  a conflicting lock order), so nesting `feat_lock(id)` inside it for
  `set_feat_id` keeps a single, consistent acquisition order project-wide and
  avoids any inconsistent-ordering deadlock risk. `feat_create_lock()`
  serializes `set_feat_id` against a concurrent `create_feat` call that might
  race on the same `new_id` folder path (covering both the existence check
  and the actual rename); `feat_lock(id)` serializes it against a concurrent
  `update`/`set_status`/`delete` targeting the same existing (old) id. As a
  consequence, `create_feat`'s own Phase 2 change (accepting a
  caller-supplied `id`) must extend its existing `with feat_create_lock():`
  block to cover the existence-check for a caller-supplied id too (not just
  the default-id derivation path), so both tools consistently serialize on
  the same global lock for their respective "check existence, then
  create/rename" sequences — flagged here for Phase 2/3 to follow.
