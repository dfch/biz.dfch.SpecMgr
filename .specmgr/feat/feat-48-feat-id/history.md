# History: create_feat caller-chosen id and set_feat_id rename tool

#### 2026-09-02 17:40:00.000Z - Phase 6: Release (Task 6.1)
Completed Task 6.1. Added a new bullet to `CHANGELOG.md`'s
`## [Unreleased]` → `### Added` section (prepended above the existing
"Windowed raw reads..." entry) describing both of this feature's changes
at the same prose density as the file's other entries (e.g.
`confluence_update`): `create_feat`'s optional caller-chosen
`id: str | None = None` parameter, its `feat-0-<slug-from-title>` default
(no more max+1 auto-increment), its `FileExistsError`/`ValueError`
failure modes, and the new `set_feat_id(id, new_id)` `@mcp.tool()`
(validation, `FileExistsError`/`FeatNotFoundError` failure modes, byte-
identical body preservation, `feat_create_lock()`/`feat_lock(id)` locking
order) — cited as "GitHub issue #48", no new ADR (this feature builds on
the two pre-existing ADRs already listed under Dependencies/Related
Decisions). No other file touched. Quality gate: full `unittest discover`
suite reconfirmed green (3023 tests, unchanged from Phase 5's count, as
expected for a docs-only change). Task 6.2 (open PR) left unchecked and
deferred to the orchestrator/user, per this task's explicit scope
boundary.

#### 2026-09-02 17:05:00.000Z - Phase 5: Tests
Completed Task 5.1-5.5. `tests/feat/tools/test_create_feat.py`: added a new
`TestCreateFeatWithExplicitId` class (4 new tests) covering the *new*
`id=` parameter behavior Phase 2 did not already have dedicated coverage
for --
`test_explicit_id_creates_exact_folder_and_id` (ACC-002: a caller-supplied
`id="feat-28-get-update"` is used verbatim against a body whose own
title-derived slug, `"zzz-unrelated-title"`, deliberately differs, proving
the slug plays no role in this branch);
`test_invalid_explicit_id_raises_value_error_and_writes_nothing` (ACC-004:
three malformed shapes -- `"not-a-valid-id"`, `"feat-abc-slug"` (non-numeric
NNN), `"Feat-1-Slug"` (uppercase) -- each raise `ValueError` with
`feat_base_dir().exists()` still `False` afterward, i.e. before even the
base dir is touched, let alone `feat_create_lock()`);
`test_explicit_id_collision_raises_and_leaves_existing_untouched` (ACC-003,
caller-supplied path: a second `create_feat(..., id="feat-28-get-update")`
call raises `FileExistsError` and the first document's on-disk bytes and
frontmatter id/title are re-verified unchanged afterward); and
`test_defaulted_id_collision_raises` (ACC-003, default path: a
`feat-0-example-widget` folder is pre-seeded directly on disk, mirroring
`test_id_number_derivation_ignores_other_feat_folders`'s existing
pre-seeding style, then a default-id `create_feat(_MINIMAL_BODY)` call
whose title derives that exact slug raises `FileExistsError`, and no
`README.md` was written into the pre-seeded folder). Confirmed (no
duplicate added) that ACC-001 is already covered by the pre-existing
`test_id_defaults_to_feat_0_when_base_dir_is_empty`, and that Task 5.2's
"no auto-increment" requirement is already covered by the pre-existing
`test_id_number_stays_0_across_creates_with_distinct_titles` and
`test_id_number_derivation_ignores_other_feat_folders`.
New file `tests/feat/tools/test_set_feat_id.py` (4 tests, new
`TestSetFeatId` class): mirrors `test_create_feat.py`'s exact
structure/style/license header, with a locally duplicated
`TempFeatDirTestCase` fixture (grepped `tests/dec/tools/`,
`tests/rsk/tools/`, and `tests/feat/prompts/` first -- every existing test
file in this codebase that needs this fixture shape duplicates it locally
rather than importing a shared helper, so the same precedent was followed
here rather than introducing a new `tests/feat/tools/_helpers.py`).
`test_happy_path_renames_updates_frontmatter_and_preserves_body` (ACC-005,
REQ-006: creates `feat-0-get-update`, captures its raw body via
`general.tools._splice.body_text` and its pre-rename `updated` timestamp,
calls `set_feat_id("feat-0-get-update", "feat-42-get-update")`, then
asserts `frontmatter.id == "feat-42-get-update"`, `type`/`status`/
`created`/`version` unchanged, `updated` changed and re-matches the
standard timestamp regex, the old folder is gone, the new
`README.md` exists and round-trips via `parse_feat` to the new id, and the
post-rename raw body text -- read the same way via `body_text` -- is
byte-identical to the pre-rename capture);
`test_target_id_already_exists_raises_and_leaves_both_untouched` (ACC-006:
two features `feat-0-a`/`feat-1-b`, then
`set_feat_id("feat-0-a", "feat-1-b")` raises `FileExistsError` with both
files' raw bytes and parsed frontmatter ids re-verified unchanged
afterward -- no partial rename); `test_source_id_not_found_raises_feat_not_found_error`
(ACC-007: `set_feat_id("feat-999-does-not-exist", "feat-100-whatever")`
raises `FeatNotFoundError`, imported from `feat.tools._paths`, with the
`new_id` folder confirmed never created); and
`test_invalid_new_id_shape_raises_value_error_and_leaves_source_untouched`
(the same three malformed shapes as `create_feat`'s equivalent test,
each raising `ValueError` against an existing source id, with the source's
raw bytes and frontmatter id re-verified unchanged after each attempt).
Did not add the optional concurrency smoke test mentioned in the phase
instructions -- `set_feat_id`'s own module docstring already states its
lock order was designed for consistency with `create_feat`'s existing
`feat_create_lock()`-based concurrency coverage
(`TestCreateFeatConcurrency`/`TestCreateFeatConcurrencyIntegration`), and
`test__lock.py` already exercises `feat_lock`/`feat_create_lock`'s
serialization primitives directly; a dedicated concurrent-`set_feat_id`
test was judged to add no material signal beyond that existing coverage.
No implementation bugs found in Phases 2/3's code while writing these
tests -- every ACC/REQ behavior documented in `create_feat.py`'s and
`set_feat_id.py`'s own docstrings held up exactly as described.
Full quality gate green: `ruff format --check`/`ruff check` (both new/
changed test files clean), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), `pylint` on the two test files (9.81/10, advisory-only
per `AGENTS.md` -- two pre-existing-style `R1732`/`W0718`/`R0801` notes,
the same kind already present elsewhere in this test suite, e.g. the
`TempFeatDirTestCase` fixture duplicated verbatim across
`test_create_feat.py`/`test_integration.py`/`test_set_feat_id.py` itself
triggering `R0801` similar-lines), the two new test files individually
(15 tests in `test_create_feat.py`, 4 in `test_set_feat_id.py`, all
passing), and the full `unittest discover` suite (3023 tests, up from
3015 -- the 8 new tests above, all passing, no existing test needed
adjustment).

#### 2026-09-02 16:10:00.000Z - Phase 4: Prompts and documentation
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

#### 2026-09-02 15:20:00.000Z - Phase 3: set_feat_id tool
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

#### 2026-09-02 14:30:00.000Z - Phase 2: create_feat optional id parameter
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

#### 2026-09-02 13:15:00.000Z - Phase 1: Design & Validation Helpers
Completed Task 1.1 and Task 1.2 (design-only, no `src/` changes). Confirmed
`general/tools/_path_safety.assert_feat_id` is directly reusable, unchanged,
for validating both `create_feat`'s optional `id` and `set_feat_id`'s
`new_id` — no feat-local validator needed. Designed `set_feat_id`'s locking
order (`feat_create_lock()` outermost, `feat_lock(id)` nested inside) and
noted that `create_feat`'s Phase 2 change must also hold `feat_create_lock()`
around its existence-check for a caller-supplied id. See Decisions Made below
for the full rationale.

#### 2026-09-02 12:00:00.000Z - Drafted feature plan from issue #48
Captured the two changes issue #48 asks for (`create_feat`'s optional caller-chosen id with no auto-increment fallback, and a new `set_feat_id` rename tool) into a Plan with requirements, acceptance criteria, scope, and a six-phase task list. No code changes made yet.
