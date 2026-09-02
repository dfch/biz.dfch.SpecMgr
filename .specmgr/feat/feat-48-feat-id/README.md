---
created: '2026-09-02T10:32:05.764646'
id: feat-48-feat-id
status: planning
type: feat
updated: '2026-09-02T16:10:00.000000'
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
- [x] ACC-008: `set_feat_id` is registered as an `@mcp.tool()` and appears in `server.py`'s docstring/registration and in `docs/MCP.md` after regeneration.
- [x] ACC-009: The packaged `feat` prompt instructions, `AGENTS.md`, and `server.py`'s docstring are updated to mention the optional `id` parameter and `set_feat_id`.
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

- [x] Task 2.1: Add `id: str | None = None` to `create_feat`; validate shape when given.
- [x] Task 2.2: Change id derivation: `id` given -> use as-is; `id` omitted -> `feat-0-<slug-from-title>`, removing the max+1 auto-increment fallback from the default path.
- [x] Task 2.3: Add a pre-write existence check for the resulting id/folder; raise before any write side effect.
- [x] Task 2.4: Update `create_feat.py`'s docstring/description for the new parameter and failure mode.

#### Phase 3: set_feat_id tool

- [x] Task 3.1: Implement `feat/tools/set_feat_id.py`: validate `new_id` shape, resolve current id via `find_feat_path_by_id`, refuse if `new_id` folder exists, rename folder, rewrite frontmatter `id` + `updated`, preserve body byte-for-byte.
- [x] Task 3.2: Register `set_feat_id` as `@mcp.tool()` and export from `feat/tools/__init__.py`.
- [x] Task 3.3: Add `server.py` docstring entry for `set_feat_id` (feat now has 8 tools, not 7).

#### Phase 4: Prompts and documentation

- [x] Task 4.1: Review/update the `feat` create-instructions packaged text to mention the optional `id` parameter and the no-auto-increment default.
- [x] Task 4.2: Review/update the `feat` update-instructions packaged text to mention `set_feat_id` as the renumbering path.
- [x] Task 4.3: Update `AGENTS.md`'s `feat/` bullet (tool count/list, mention of `set_feat_id`).
- [x] Task 4.4: Regenerate `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md`; verify no drift.

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

**As of 2026-09-02**: Phase 4 (prompts and documentation) done. The
packaged `feat_create_instructions.md`/`feat_update_instructions.md`
prompt text and `AGENTS.md`'s `feat/` bullet now describe `create_feat`'s
optional `id` parameter, the `feat-0-<slug>` no-auto-increment default,
and `set_feat_id` as the dedicated renumbering path (distinct from the
generic `update`/`set_status` tools). `specmgr docs` and `specmgr
mcp-docs` were re-run and produced no drift beyond these prompt-text/
`AGENTS.md` edits themselves -- confirming Phase 3's commit had already
regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` faithfully.
Full test suite green (3015 tests, unchanged). ACC-008 and ACC-009 are
now satisfied end-to-end. Implementation continues with Phase 5 (tests).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 16:10:00.000Z — Phase 4: Prompts and documentation

Completed Task 4.1-4.4 (REQ-009). `feat/data/feat_create_instructions.md`:
reworded the opening paragraph to state that `create_feat` now accepts an
optional `id` (a full, well-formed `feat-NNN-slug`, pass it explicitly
once the GitHub issue number is known) and, when omitted, defaults to
`feat-0-<slug-from-title>` -- not an auto-incrementing number -- with a
one-line rationale (`NNN` is meant to be the GitHub issue number,
`feat-0-...` signals "no issue yet"); step 2 of "## 4. Tool call
sequence" now shows both call shapes
(`create_feat(content, id="feat-42-my-slug")` vs. `create_feat(content)`)
and documents both new failure modes (`ValueError` for a malformed
caller-supplied `id`, `FileExistsError` for an existing id/folder
collision), each before any write; "## 5. Later revisions" gained a
closing sentence naming `set_feat_id(id, new_id)` as the dedicated path
for an id/renumbering change, distinct from `update_feat`/generic
`update`/`set_status`. `feat/data/feat_update_instructions.md`: "## 4.
Map the requested change to the right tool" gained a third bullet (after
the existing body-change and status-change bullets) for an `id` change,
naming `set_feat_id(id, new_id)` explicitly, noting `update` never
accepts/changes `id`, the `new_id` shape requirement, the byte-for-byte
body preservation, and explicitly calling `set_feat_id` a "bespoke
`feat`-only tool" distinct from the generic `update`/`set_status
(type="feat")` dispatch pattern -- so as not to imply it is itself a
generic dispatch tool. The opening paragraph's existing "no
`update_feat`/`set_status_feat` tool of its own" sentence was left
unchanged (still true; `set_feat_id` is a new, distinct kind of tool, not
an `update_feat`/`set_status_feat` equivalent). `AGENTS.md`'s `feat/`
bullet: "All 7 tools" -> "All 8 tools", `set_feat_id` added to the tool
list (right after `create_feat`), plus two new clauses describing (a)
`create_feat`'s optional `id` parameter and `feat-0-<slug>` default (no
max+1 auto-generation), and (b) `set_feat_id`'s role as the one tool that
renames an existing feature's id (folder rename + frontmatter rewrite),
explicitly called out as distinct from the generic `update`/`set_status`
dispatch tools the same bullet already describes `feat` as using; the
existing "no `update_feat`/`set_status_feat` of its own" sentence later
in the same bullet was left unchanged (still accurate) and the "Still
genuinely missing" paragraph at the end of the Status section was left
untouched (nothing there became inaccurate). Ran `specmgr docs` and
`specmgr mcp-docs`: `git diff --stat` afterward showed changes to only
the three files above -- zero diff under `docs/`, confirming Phase 3's
commit had already regenerated `docs/api/`/`docs/GENERATED.md`/
`docs/MCP.md` to a faithful fixed point and there was no lingering drift
to pick up here. Full quality gate green: `specmgr docs`, `specmgr
mcp-docs` (both no-op on `docs/`), and the full `unittest discover` suite
(3015 tests, all passing, unchanged from Phase 3's count -- no test
asserts on exact packaged-instruction-text content that this phase's
wording changes broke).

#### 2026-09-02 15:20:00.000Z — Phase 3: set_feat_id tool

Completed Task 3.1-3.3. New file
`src/biz/dfch/specmgr/feat/tools/set_feat_id.py`: `set_feat_id(id, new_id)`
validates `new_id` via `general.tools._path_safety.assert_feat_id` before
any lock/filesystem access (a malformed `new_id` raises a bare
`ValueError`); acquires `feat_create_lock()` first (outermost), then
`feat_lock(id)` nested inside it, per Phase 1's Decision; resolves `id` via
`feat.tools._io.load_by_id` (propagating `FeatNotFoundError` naturally, no
catch/re-raise needed); refuses with `FileExistsError` before any rename if
`<base>/<new_id>/` already exists; reads the raw on-disk body via the
existing `general.tools._splice.body_text` helper *before* renaming so the
body is preserved byte-for-byte; renames the folder
(`old_path.parent.rename(new_path.parent)`); rebuilds `FeatFrontmatter`
from `existing.frontmatter.model_dump()` with only `id` and `updated`
(via `now_timestamp()`) changed; and rewrites the file via
`write_feat_file(new_path, new_frontmatter, raw_body)`. Satisfies REQ-005,
REQ-006, REQ-007, REQ-008. Registered as `@mcp.tool(name="set_feat_id",
...)` and exported from `feat/tools/__init__.py` (its module docstring's
"seven lifecycle tools" language updated to "eight", plus a short
description of `set_feat_id`'s role, mirroring the existing
create_feat/update/set_status/delete prose). `server.py`'s module
docstring's feat-domain tool listing extended with `set_feat_id`'s
description. No dedicated unit tests added yet (Phase 5's job); ran a
throwaway manual smoke test under `/tmp` (not committed) against a
`SPECMGR_FEAT_DIR`-scoped temp directory: happy-path rename
(`feat-0-get-update` -> `feat-42-get-update`, verified byte-identical body,
`updated` bumped, other frontmatter fields unchanged, old folder gone, new
folder present), `FeatNotFoundError` for an unresolvable `id`, and
`FileExistsError` for a `new_id` collision (verified no rename/write
happened), plus a bad-shape `new_id` `ValueError` case -- all four passed.
Full quality gate green: `ruff format --check`, `ruff check`, `vulture`
(clean), and the full `unittest discover` suite (3015 tests, all passing,
unchanged from Phase 2's count since no existing test needed adjustment).

#### 2026-09-02 14:30:00.000Z — Phase 2: create_feat optional id parameter

Completed Task 2.1-2.4. `src/biz/dfch/specmgr/feat/tools/create_feat.py`:
added `id: str | None = None` (validated via
`general.tools._path_safety.assert_feat_id` before any lock/filesystem
access, per Phase 1's Decision); id derivation now branches on whether
`id` was given (used verbatim) or omitted (`feat-0-<slug-from-title>`,
REQ-002 -- no more `_next_feat_number` max+1 scan); a pre-write existence
check (`target_path.parent.exists()`) raises `FileExistsError` before
`write_feat_file` runs for either branch (REQ-003), inside the existing
`feat_create_lock()` block, per Phase 1's Decision that this lock must
cover the caller-supplied-id existence-check too. Removed the now-fully-
dead `_next_feat_number` helper and its `FEAT_FOLDER_PATTERN`/`re` imports
from `create_feat.py`; `FEAT_FOLDER_PATTERN` itself (and the now-unused
`re` import) were also removed from `feat/tools/_paths.py` after `vulture`
flagged it as dead once `create_feat.py` stopped importing it. Updated the
module/function docstrings and the `@mcp.tool()` `description=` string to
describe both `id` branches and the two new failure modes (`ValueError`
for a malformed `id`, `FileExistsError` for a collision). Satisfies
REQ-001, REQ-002, REQ-003, REQ-004 and ACC-001 through ACC-004. Adjusted
five existing tests that asserted the removed max+1 auto-increment
behavior (`tests/feat/tools/test_create_feat.py`,
`tests/feat/prompts/test_create_feat.py`,
`tests/feat/tools/test_integration.py`) to expect `feat-0-<slug>` instead
of an incrementing number; no new test cases were added (Phase 5 owns
that). Full quality gate green: `ruff format --check`, `ruff check`,
`vulture` (clean after the `_paths.py` cleanup), and the full
`unittest discover` suite (3015 tests, all passing).

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
- **2026-09-02 (Task 2.3, Phase 2)**: The pre-write existence check tests
  `target_path.parent.exists()` (i.e. `<base>/<new_id>/`, the folder),
  not just `target_path.exists()` (the `README.md` file itself), and
  raises the builtin `FileExistsError` on a hit. Rationale: no other
  domain tool in this codebase has an established "id/folder already
  exists" collision exception to mirror (grepped for `FileExistsError`/
  "already exist" across `src/`; none found as a raised-collision
  pattern), so `FileExistsError` was chosen as the most semantically
  correct builtin for this condition, per the task instructions.
  Checking the folder rather than just the file also correctly rejects a
  half-written/collided folder that exists without a `README.md` yet
  (e.g. left over from an interrupted create), consistent with
  `find_feat_path_by_id`'s own folder-is-the-unit-of-identity treatment
  of `feat` ids elsewhere in this domain.
- **2026-09-02 (Task 3.1, Phase 3)**: `set_feat_id` obtains the exact,
  byte-identical raw body content via the already-existing
  `general/tools/_splice.body_text(path)` helper -- the same helper the
  generic `update`/`get_<d>(raw=True)` tools already use to extract a
  document's frontmatter-stripped body text -- called against the *old*
  path before the folder rename happens. Rationale: this is the
  established, single definition of "the body text" in this codebase (see
  `_splice.py`'s own "raw/splice invariant" docstring section); reusing it
  avoids inventing a second, parallel body-extraction mechanism, and
  calling it before the rename (rather than trying to re-derive the raw
  text from the parsed `Feature` model, which `feat` never renders back
  out to markdown -- see `_write.py`'s "content embedded verbatim" note)
  is what makes REQ-006 (byte-identical body) and REQ-008 (no
  reference-updating) trivially true: the exact same string that was on
  disk is written back out unchanged, just under new frontmatter.
