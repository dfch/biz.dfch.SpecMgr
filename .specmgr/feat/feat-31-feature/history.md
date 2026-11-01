# History: Formalize the Feature artifact type ("feat")

#### 2026-08-30T00:00:00.000Z - Update (Phase 6 recorded — frontmatter timestamp format fix)
Added a new `#### Phase 6: Frontmatter timestamp format fix` to the
  Task List, with one new task, **Task 6.1** (not-started): change
  `feat` frontmatter's `created`/`updated` fields from plain
  `YYYY-MM-DD` dates to microsecond timestamps
  (`datetime.now().isoformat(timespec="microseconds")`), matching every
  other whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/
  `dec`) already in use — reversing this feature's own earlier
  deliberate divergence documented in Design Notes' "Frontmatter"
  section and in Decisions Made. The task calls out the affected files
  (`feat/tools/create_feat.py`, `general/tools/update.py`'s
  `_update_feat` adapter, `general/tools/set_status.py`'s
  `_set_status_feat` adapter, the Design Notes prose, and the tests
  asserting the plain-date format) and requires a new Decisions Made
  entry when the reversal is actually implemented, not a silent code
  change.
Frontmatter `status` reverted from `done` to `in-progress` and
  `version` bumped from `1.11.0` to `1.12.0` to reflect this new,
  not-yet-started follow-up item.
**This is planning/recording only — no `src`/`tests` code was
  touched.** Task 6.1 remains not-started; implementation is deferred to
  a future session.

#### 2026-08-30T00:00:00.000Z - Update (Phase 5 complete — cross-cutting registration; feature done)
**`server.py` (Task 5.1)**: added `feat` to the domain import line
  (alphabetical: `adr, dec, feat, general, gol, prb, qa, req, rsk, tsk,
  uc`). Module docstring gained: a `specmgr://feat/schema`/`/example`/
  `/template` Resources block placed right after the `dec` block (same
  relative position `feat` occupies in the domain-enumeration
  elsewhere); a "FEAT has no `specmgr://feat/{id}` ... no
  `specmgr://feat/list`" sentence appended to the "DEC has no ..."
  paragraph; a new "Feature tools (`feat/tools/`)" paragraph in Tools
  mirroring "Decision tools" (verified `get_feat` does take
  `raw: bool = False`, matching every other domain, before writing this
  paragraph — checked `feat/tools/get_feat.py` directly per this task's
  own instruction), plus one extra sentence noting `feat`'s bespoke
  `_paths.py` addressing and its lack of `update_feat`/`set_status_feat`
  tools of its own; the `update`/`set_status` paragraphs' domain counts
  bumped from eight/nine to nine/ten whole-body/total domains (both
  `general/tools/update.py` and `set_status.py` had already made this
  exact bump to their own docstrings back in Phase 2, so this brought
  `server.py` in line with code that was already correct); a new
  "Feature prompts (`feat/prompts/`)" paragraph in Prompts mirroring
  "Decision prompts"; and `feat` inserted into both domain-enumeration
  sentences ("Modules are grouped domain-first ..." and "Add a new
  domain by ...") plus the final "each register `tools`, `resources`,
  and `prompts`" sentence.
**Cross-cutting config (Task 5.2)**: `pyproject.toml` gained
  `"biz.dfch.specmgr.feat" = ["data/*.md", "data/*.json"]` alphabetically
  between `dec` and `gol`. `.pre-commit-config.yaml`'s one shared
  `files:` regex glob (`^src/biz/dfch/specmgr/(dec/models/v1|gol/
  models/v1|...)/.*\.py$`) gained `feat/models/v1` between `dec/models/v1`
  and `gol/models/v1` in all 9 pre-existing occurrences (counted 9 before
  the edit, 9 after — a global find/replace, not a manual per-occurrence
  edit, so the count check was mostly a sanity confirmation) plus a new
  10th occurrence in the brand-new `specmgr-schema-feat-package` hook
  itself, which mirrors `specmgr-schema-dec-package` verbatim (id/name/
  description/entry/language/pass_filenames/files) and is placed last,
  matching this file's own insertion-order (not alphabetical) convention
  for per-domain schema-package hooks: `req, uc, tsk, rsk, qa, prb, gol,
  dec, feat`. `.github/workflows/ci.yml` gained a new
  `` `src/biz/dfch/specmgr/feat/data/feat_schema.json` `` drift-check
  step, same `if: matrix.python-version == '3.13'` guard and
  `::error::...` message format as the existing `dec` step, placed
  immediately after it; the `docs/*_schema.json` step's own comment
  prose and the `specmgr-schema` pre-commit hook's description were both
  updated to name `feat` among the registered types.
**`AGENTS.md`/root `README.md` (Task 5.3)**: added a new `**`feat/`**`
  bullet to `AGENTS.md`'s per-domain enumeration (between `dec/` and
  `general/`), at the same depth/style as `dec/`'s own, spelling out the
  addressing deviation explicitly (non-UUID `id`, folder-per-document,
  bespoke `feat/tools/_paths.py`, mandatory `SPECMGR_FEAT_DIR`, all 8
  tools, generic `update`/`set_status` dispatch, resources, prompts,
  `FeatSummary.path`). Updated every other domain-enumeration sentence in
  `AGENTS.md` that listed all current domains: the `general/` bullet's
  own whole-body/total domain counts (eight→nine, nine→ten) and `type`
  enumeration; the "Still genuinely missing" section's `validate_*`/
  `delete_*` lists and the register-all-three sentence; the "MCP server
  (server.py)" section's own domain-import-line description. Root
  `README.md`: added `Feature (FEAT)` to the active bulleted artifact
  list (alphabetically between `Decision (DEC)` and `Goal (GOL)`),
  removed the `Feature (FTR)` line from the commented-out placeholder
  block (the abbreviation was wrong there too — "FTR", not the actually-
  implemented "FEAT" — on top of being redundant now that FEAT is
  active), and, as a drive-by fix, moved `Risk (RSK)` out of the same
  placeholder into the active list since `AGENTS.md`'s own `rsk/` bullet
  confirms RSK has been a fully implemented, schema-backed domain for
  some time — only the not-yet-implemented `Acceptance Criterium (ACC)`
  stays commented out. Recorded as a new Decisions Made entry below.
**Regeneration (Task 5.4)**: ran `specmgr docs`, `specmgr mcp-docs`,
  `specmgr schema`, and `specmgr schema --type feat --output-dir
  src/biz/dfch/specmgr/feat/data`, each twice in a row. `specmgr docs`
  changed only `docs/api/biz.dfch.specmgr.server.md` (reflecting the
  Task 5.1 docstring edits) on the first run and produced zero further
  diff on the second. `specmgr mcp-docs` produced no diff on either
  run — every FEAT tool/resource/prompt was already fully registered
  against the live `mcp` instance before this phase (Phases 2-4), so
  `docs/MCP.md` was already current; this phase's `server.py` docstring
  changes only affect `docs/api/`, not `docs/MCP.md`, which is generated
  from the actual tool/resource/prompt registrations, not the module
  docstring. `specmgr schema` (all 9 registered types) and the `feat`-
  only packaged-copy invocation both reported every file "(unchanged)"
  on both runs. Confirmed idempotent across the board.
**Final verification (Task 5.5)** — ACC-001..009 walked with concrete
  evidence:
  ACC-001: `tests/feat/models/v1/test_parser.py` exercises the full
    matrix (`TestParseFeatValueViolations`/`TestParseFeatStructuralViolations`)
    — malformed status/hyphenated status/wrong `type`, malformed
    `REQ-\d{3}`/`ACC-\d{3}` items, out-of-order `Updates` entries,
    unknown H2, missing `Requirements`, malformed `Phase`/`UpdateEntry`
    headings, zero-phase/zero-entry composites, leading content before
    H1, a second H1 — all raise, all covered. `docs/feat_schema.json`/
    `specmgr://feat/schema` (via `feat/resources/feat_schema.py`) both
    exist and are exercised by `tests/feat/resources/test_feat_schema.py`.
  ACC-002: `tests/feat/tools/test__paths.py::TestFindFeatPathById`
    covers the direct-shortcut resolution, the id/folder-name-mismatch
    rejection (tool-layer, not model-layer), and the no-partial-match
    behavior; `tests/feat/tools/test_integration.py::
    TestCreateFeatConcurrencyIntegration::test_many_concurrent_create_feat_calls_never_collide`
    proves the global create-lock prevents two callers picking the same
    `NNN`.
  ACC-003: all 8 tools exist, are registered (confirmed live in
    `docs/MCP.md`'s Tools section), and are exercised by
    `tests/feat/tools/test_integration.py::TestFeatLifecycleIntegration::
    test_full_lifecycle_roundtrip` (create→get→list→...→delete-stub→
    validate against a temp `SPECMGR_FEAT_DIR`); `list_feat` returns
    `PagedResult[FeatSummary]` per `tests/feat/tools/test_list_feat.py`.
  ACC-004: the same integration test drives `update(type="feat", ...)`
    in both whole-body and line-range modes and `set_status(type="feat",
    ...)`, asserting `id`/`type`/`created`/`version` are preserved and
    only `updated`/`status` change.
  ACC-005: `docs/MCP.md`'s Resources section lists exactly
    `specmgr://feat/schema`/`/example`/`/template`, no `/{id}`, no
    `/list`; `tests/feat/resources/` exercises all three live.
  ACC-006: `tests/feat/prompts/test_create_feat.py::
    TestCreateFeatInstructionsWalkthrough`/`test_update_feat.py::
    TestUpdateFeatInstructionsWalkthrough` drive the real tools following
    the packaged instructions' own narrated steps end to end (not just
    static-text assertions), per this ACC's explicit requirement.
  ACC-007: `diff`-verified byte-identical `docs/feat_schema.json` and
    `src/biz/dfch/specmgr/feat/data/feat_schema.json` (both freshly
    regenerated this phase); `tests/feat/resources/test_feat_schema.py::
    test_matches_fresh_generate_feat_schema_output` covers the same
    invariant at the test-suite level.
  ACC-008: `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` all
    report zero drift (see Task 5.4 above); `AGENTS.md` reflects the new
    domain (this update); `feat-7-various-improvements` already carries
    Task 0.31 and its Task 0.30 background note already names `feat` as
    a fourth divergent variant (done in Phase 0, verified still present).
  ACC-009: full `unittest` suite green (2228 tests, 221 of them under
    `tests/feat/`); `ruff format --check`/`ruff check` clean; `vulture
    src/ whitelist.py --min-confidence 60` clean; `specmgr unused-code`
    clean.
  Full quality gate re-run end to end, all green (see this update's own
  Current Status entry for exact command output). Frontmatter `status`
  set from `in-progress` to `done`.
Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
**This feature is now complete.** All 5 phases and all 11 requirements
  (REQ-001..011) are implemented, tested, and cross-registered; all 9
  acceptance criteria (ACC-001..009) are verified with concrete evidence.

#### 2026-08-30T00:00:00.000Z - Update (Phase 4 complete — prompts)
Implemented `feat/prompts/` in full: `create_feat.py`
  (`create_feat(topic)`), `update_feat.py`
  (`update_feat(id, instructions=None)`), `__init__.py` — each a 1:1
  mirror of `dec.prompts.create_dec`/`update_dec`: thin `string.Template`
  wrappers around `general.tools._packaged_data.read_packaged_text`
  reading the already-existing Phase-3 packaged instructions files
  (`feat_create_instructions.md`/`feat_update_instructions.md`),
  substituting `$topic` (create) and `$id`/`$instructions` (update).
  Neither calls `TodoWrite`/`question`/`list_feat`/`get_feat`/
  `create_feat`/`update`/`set_status` themselves — they only narrate that
  sequence, matching every other prompt in this codebase.
Judgment call: `update_feat`'s fallback for a missing `instructions`
  argument is the literal string `"(not given)"`, not DEC's own longer
  `"(not given -- ask the user before making any change)"` — verified
  `feat_update_instructions.md`'s step 2 checks for the literal substring
  `"(not given)"` (`If "Requested change" above says "(not given)", ask
  the user...`), so the fallback matches that check exactly rather than
  reusing DEC's wording verbatim.
Updated `feat/prompts/__init__.py` to import and export both prompts
  (mirroring `dec/prompts/__init__.py`'s one-module-per-prompt shape) and
  `feat/__init__.py`'s module docstring to reflect Phase 4 completion
  (only Phase 5 cross-cutting registration remains).
Wrote 29 new tests across `tests/feat/prompts/`
  (`test_create_feat.py`/`test_update_feat.py`) — all green: static
  string-content/ordering assertions mirroring `tests/dec/prompts/`'s own
  depth (topic/id/instructions substitution, packaged-file provenance,
  tool-call-sequence ordering, missing-file propagation), plus, per
  ACC-006's explicit requirement, one "walk the instructions end to end"
  test per prompt driving the real `create_feat`/`get_feat`/`list_feat`/
  `update`/`set_status` tools against a temporary `SPECMGR_FEAT_DIR`:
  `TestCreateFeatInstructionsWalkthrough` follows step 0 (dedup check via
  `list_feat`) and step 4 (`create_feat`) literally;
  `TestUpdateFeatInstructionsWalkthrough` creates a real document, then
  follows `get_feat` → line-range `update` → whole-body `update` →
  `set_status` exactly as the packaged update instructions narrate,
  asserting the end state. Checked `tests/dec/prompts/` first per this
  phase's own instructions — it only does static-text assertions, so this
  deeper walk-through is new depth introduced specifically for `feat`.
Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
  needed), `specmgr unused-code` (clean), full `unittest` suite (2228
  tests, green, up from 2199 after Phase 3).
Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
Next: Phase 5 (cross-cutting registration) — `server.py` domain import,
  `pyproject.toml`/`.pre-commit-config.yaml`/CI wiring, `AGENTS.md`
  updates, regenerated docs, final verification pass, and setting the
  feature status to `done`.

#### 2026-08-30T00:00:00.000Z - Update (Phase 3 complete — resources, packaged data, schema)
Implemented `feat/data/` in full: `feat_example.md` (a byte-identical
  copy of `tests/feat/models/v1/data/feat_reference.md`, confirmed via
  `diff`), `feat_template.md` (all-sections placeholder skeleton --
  `Dependencies` with both `Depends On`/`Blocks`, `Design Notes`,
  `Related Decisions`, `Blockers`, `Decisions Made`, `Related PRs /
  Commits`, `More Information` all present -- `status: planning`,
  round-trips through `parse_feat`), `feat_create_instructions.md`/
  `feat_update_instructions.md` (narrated instruction bodies mirroring
  `dec`'s/`gol`'s own two files, tailored to `feat`'s actual schema, its
  four-value hyphen-free status set, and its no-`update_feat`/
  `set_status_feat`-of-its-own generic-dispatch MCP surface), and
  `feat_schema.json` (both `docs/feat_schema.json` and the packaged
  `feat/data/feat_schema.json` copy, generated via `specmgr schema --type feat` and `specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data`, confirmed byte-identical via
  `diff`).
`commands/schema.py` gained `generate_feat_schema()` (mirroring
  `generate_dec_schema()` exactly) and a `"feat"` entry in `_GENERATORS`,
  inserted alphabetically between the existing `"dec"` and `"gol"` keys.
Implemented `feat/resources/`: `feat_schema.py`/`feat_example.py`/
  `feat_template.py`/`__init__.py`, each a 1:1 mirror of
  `dec.resources`' own three modules plus its `__init__.py`, registering
  `specmgr://feat/schema`/`specmgr://feat/example`/
  `specmgr://feat/template` (no `/{id}` -- id-based reads are
  `get_feat`-only; no `/list` -- listing is the `list_feat` tool).
  Updated `feat/__init__.py`'s module docstring to reflect Phase 3
  completion (data/resources populated, only `prompts` still empty).
Replaced the two Phase-2-deferred tests
  (`tests/feat/tools/test_get_feat_example.py`/
  `test_get_feat_template.py`) with real "returns the packaged file"
  happy-path assertions (mirroring `test_get_dec_example.py`/
  `test_get_dec_template.py`), now that the packaged files they read
  actually exist on disk.
Wrote 20 new tests across `tests/feat/resources/`
  (`test_feat_schema.py`/`test_feat_example.py`/`test_feat_template.py`)
  -- all green, including: `feat_schema` matches a fresh
  `generate_feat_schema()` output; `feat_example` is byte-identical to
  both the packaged file and the Phase-1 reference fixture, and
  round-trips through `parse_feat` byte-exact (re-verifying ACC-001 at
  this layer too, per this phase's own instructions) while exercising
  every optional section (`Dependencies` with both children,
  `Design Notes`, `Related Decisions`, `Blockers`, `Decisions Made`,
  `Related PRs / Commits`, `More Information`); `feat_template`
  successfully parses via `parse_feat` (structurally valid, `status: planning`) while exercising the same set of optional sections, without
  being required to be a "realistic" document.
Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
  needed), `specmgr unused-code` (clean), full `unittest` suite (2199
  tests, green, up from 2179 after Phase 2).
Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** -- that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
Next: Phase 4 (`feat/prompts/`) -- `create_feat.py`
  (`create_feat(topic)`), `update_feat.py`
  (`update_feat(id, instructions=None)`), `__init__.py`, and
  `tests/feat/prompts/` (ACC-006).

#### 2026-08-30T00:00:00.000Z - Update (Phase 2 complete — tools, bespoke addressing)
Implemented `feat/tools/` in full per Design Notes' Addressing section:
  `_paths.py` — hand-rolled, ADR-style (not built on
    `general/tools/_doc_paths.py`): `feat_base_dir()`/`ensure_feat_base_dir()`
    (`SPECMGR_FEAT_DIR`, falling back to `.specmgr/feat`), `iter_feat_paths(base_dir)` (globs `<base>/*/README.md`), `find_feat_path_by_id(base_dir, id_)` (the no-scan `<base>/<id_>/README.md` shortcut — no partial-id
    matching), `FeatNotFoundError`, plus `feature_title()` (strips the
    literal `"Feature: "` prefix off `Feature.text`, needed because
    `Feature` declares no `title` computed field of its own, unlike
    `Phase`/`UpdateEntry`/`DecisionEntry`) and `FEAT_FOLDER_PATTERN`.
  `_lock.py` — per-id `feat_lock(id_)` (identical shape to
    `dec_lock`/`adr_lock`) plus the new **global** `feat_create_lock()`
    (a single module-level `threading.Lock`, no per-id registry needed).
  `_io.py`/`_write.py` — `read_feat`/`load_by_id` (mirrors `dec.tools._io`
    file-for-file) and `write_feat_file` (mirrors `dec.tools._write`, plus
    `path.parent.mkdir(parents=True, exist_ok=True)` since `feat` is
    folder-per-document).
  The 8 lifecycle tools + `tools/__init__.py`: `create_feat` (derives
    `feat-NNN-slug` under the global create lock, plain-date
    `created`/`updated`), `parse_feat`, `list_feat`
    (`PagedResult[FeatSummary]`, `path`/`ref` populated from the real
    resolved path), `get_feat(id, raw=False)`, `get_feat_example`/
    `get_feat_template` (wired to the shared packaged-data reader, though
    the packaged files themselves are Phase 3's job), `delete_feat` (stub),
    `validate_feat`.
`general/tools/update.py`/`set_status.py` gained `_update_feat`/
  `_set_status_feat` adapters and `"feat"` dispatch table entries (REQ-006)
  — `feat` is now included in both tools' `type` `Literal`/dispatch table,
  with the same plain-`YYYY-MM-DD`-date `updated` divergence `create_feat`
  established (not the other domains' microsecond timestamp). Updated both
  modules' module-level docstrings' domain-count prose (8→9 for `update`,
  9→10 for `set_status`).
Updated one pre-existing test,
  `tests/general/tools/test_update.py::TestUpdateRegistration`, whose
  hardcoded 8-value `type` enum assertion against the live `mcp` tool
  registration needed `"feat"` added (now 9 values).
Wrote 73 new tests across `tests/feat/tools/` (`test__paths.py`,
  `test__lock.py`, `test__io.py`, `test__write.py`, `test_create_feat.py`,
  `test_get_feat.py`, `test_list_feat.py`, `test_parse_feat.py`,
  `test_validate_feat.py`, `test_delete_feat.py`,
  `test_get_feat_example.py`, `test_get_feat_template.py`,
  `test_integration.py`) — all green, including a live full
  create→get→list→update(whole-body)→update(line-range)→set_status→get→
  list→validate→delete(stub) round-trip and a 20-thread concurrent-`create_feat` collision test (ACC-002/ACC-003/ACC-004).
Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
  needed), `specmgr unused-code` (clean), full `unittest` suite (2179
  tests, green, up from 2106 after Phase 1).
Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
Next: Phase 3 (`feat/resources/` + `feat/data/` + schema command) —
  `feat_example.md`/`feat_template.md` (byte-identical copy of
  `feat_reference.md` / all-sections placeholder skeleton),
  `feat_create_instructions.md`/`feat_update_instructions.md`,
  `generate_feat_schema()`, and the three `specmgr://feat/*` resources.
  `get_feat_example`/`get_feat_template` are already wired to read the
  packaged files that Phase 3 ships — no further tool-layer changes needed
  once those files exist, only the two currently-deferred tests
  (`test_get_feat_example.py`/`test_get_feat_template.py`) need their
  "real packaged file" happy-path test added back in.

#### 2026-08-30T00:00:00.000Z - Update (Phase 1 complete — models + parser)
Implemented `feat/models/v1/` in full: `_util.py`
  (`SCHEMA_COMMENT_VERSION = "v1"`), `frontmatter.py` (`FeatFrontmatter`,
  closed 4-set status, `"planning"` default overriding the base's
  `"draft"`, mirroring `rsk.RskFrontmatter`'s `_default_blank_status_to_open`
  pattern), `body.py` (`Feature`/`Plan`/`Progress` and all 20 child section
  classes per Design Notes, including the `RequirementItem`/
  `AcceptanceCriterionItem` computed-field regexes, `Phase`'s
  `number`/`title` computed fields, `UpdateEntry`/`DecisionEntry`'s shared
  ISO8601 `timestamp`/`title` computed fields and `@alias` regex, and the
  newest-first `@model_validator` on `Updates`/`DecisionsMade`),
  `document.py` (`FeatDocument`), `parser.py` (`parse_feat`), `summary.py`
  (`FeatSummary(DocSummary)` + `path: str`), and the `models/v1/__init__.py`/
  `models/__init__.py` exports.
Verified, live, that the "no `LITERAL` needed" claims in Design Notes for
  `Plan`/`Progress`/`RelatedDecisions`/`ExplicitlyOutOfScope`/`DependsOn`
  all hold against the real `space_separated_name()` engine function before
  writing any code — only `RelatedPrsCommits` needed the documented
  `LITERAL` override.
Seeded `tests/feat/models/v1/data/feat_reference.md` from
  `.specmgr/feat/feat-31-feature/example.md` per Task 1.5, with two small,
  content-preserving adjustments needed to satisfy the generic `models/md`
  engine's own existing constraints (both recorded as Decisions Made
  entries below, not schema changes): every bullet/checklist list became a
  loose list (blank line between items), and Task 0.1's item text dropped
  its wrapped `— status: completed (2026-08-30)` suffix.
Added one design decision beyond Design Notes' literal text:
  `Requirements`/`AcceptanceCriteria`/`Phase` each gained an eager-
  computed-field-validation `@model_validator`, mirroring
  `tsk.models.v1.body.Task._validate_items_eagerly` exactly, so a malformed
  item raises immediately at parse time (see Decisions Made).
Wrote 99 new tests across `test_frontmatter.py` (11)/`test_body.py`
  (70)/`test_parser.py` (18); all green.
Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, after adding
  `feat`'s new pydantic-field/validator names to `whitelist.py`, same
  false-positive pattern already documented there for every other
  domain), `specmgr unused-code` (clean), full `unittest` suite (2106
  tests, green).
Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
Next: Phase 2 (`feat/tools/`) — bespoke addressing (`_paths.py`,
  `_lock.py`, `_io.py`, `_write.py`), the 8 MCP tool modules, and the
  generic `update`/`set_status` dispatch adapters.

#### 2026-08-30T00:00:00.000Z - Update (design review complete — Blocker resolved, Phase 1 authorized)
**Design review declared complete** after five rounds spanning
  body-modeling depth, addressing scheme, frontmatter semantics, MCP
  surface scope, ordering/comment/hyperlink questions, LITERAL-alias
  elimination, and partial-match/env-var/FeatSummary-path questions — no
  open questions remain in Design Notes.
Frontmatter `status` changed from `planning` to `in-progress`; version
  bumped to `1.6.0`.
Blockers: "Design review pending" marked resolved (`[x]`), recording
  the five-round history and confirming Phase 0's committed scaffold
  (`31c5c30`, `164182e`) stays untouched.
Recorded as a new Decisions Made entry.
**Implementation was explicitly not started in this session** —
  user-directed: Phase 1 (and every later phase) is to be carried out by
  a separate implementing session/agent (e.g. a Phase-Orchestrator-style
  agent working through the Task List), not as a continuation of this
  design-review conversation. Nothing under `src`/`tests` was touched.
Next: a separate agent starts at Task 1.1 (`feat/models/v1/_util.py`).

#### 2026-08-30T00:00:00.000Z - Update (fifth design-review round — partial-match rejected, env var confirmed mandatory, FeatSummary gains path)
Resolved three more follow-up questions and updated Design Notes/Task
  List/Decisions Made accordingly:
  **Partial-id matching rejected**: verified an agent can already
    resolve a bare `"feat-31"` to the real id via `list_feat` +
    `get_feat` composition, so no boundary-matching/ambiguous-match/scan
    logic is being added to `find_feat_path_by_id`.
  **`SPECMGR_FEAT_DIR` confirmed mandatory**: checked the actual
    precedent (`adr/tools/_paths.py`'s `SPECMGR_ADR_DIR`,
    `general/tools/_doc_paths.py`'s shared `SPECMGR_DOCS_DIR`) — every
    existing domain has an equivalent env var for test isolation; `feat`
    keeps its own, made explicit in REQ-004/Design Notes rather than
    just a parenthetical.
  **`FeatSummary` gains `path: str`**: checked `general/models/ summary.py`'s `DocSummary` and confirmed its `ref` field is
    deliberately *not* a path, specifically to discourage direct file
    access (same policy `AdrSummary` enforces, backed by an ADR requiring
    ADRs be edited only through MCP tools). `feat` is the opposite case
    by design — direct hand/agent editing of `.specmgr/feat/<id>/ README.md` is the intended, sanctioned workflow — so `FeatSummary`
    adds a real `path` field alongside the inherited `id`/`ref`, not in
    place of them.
Nothing under `src`/`tests` was touched.

#### 2026-08-30T00:00:00.000Z - Update (removed superseded example drafts; closed the "does Phase 1 know to use it" gap)
Removed `.specmgr/feat/feat-31-feature/example-initial.md` and
  `example-revised.md` — both superseded review-process drafts, now that
  `example.md` has absorbed everything useful from them across four
  review rounds. `example.md` is the only example file left in this
  feature's folder.
Caught and fixed a real gap: `example.md` had only ever been marked
  "canonical" in narrative Current Status/Decisions Made/Recent Updates
  text — Task 1.5 (the actionable Task List item an implementing agent
  actually follows in Phase 1) never mentioned it at all. Updated Task
  1.5 to explicitly instruct seeding `feat_reference.md` from
  `example.md`, and updated Current Status to reflect the same.
Nothing under `src`/`tests` was touched.

#### 2026-08-30T00:00:00.000Z - Update (fourth design-review round — eliminated all remaining LITERAL aliases except one)
Per explicit user direction to minimize `LITERAL` alias use, replaced
  three headings with spellings that match the implicit `SPACE_SEPARATED`
  derivation exactly, eliminating the need for a `LITERAL` override on
  each (verified against the live engine, same as the previous round):
  `"Related ADRs"` → **`"Related Decisions"`** (`RelatedAdrs` →
    `RelatedDecisions`) — also a deliberate terminology change: phases
    out "ADR" in favor of "Decision"/`dec`, per user direction, since
    this codebase intends to retire ADR terminology over time. Entries
    may still reference either an ADR id or a `dec` id.
  `"Explicitly out of scope"` → **`"Explicitly Out Of Scope"`**
    (`ExplicitlyOutOfScope` unchanged) — accepted as consistent with this
    codebase's existing Start-Case multi-word headings.
  `"Depends on"` → **`"Depends On"`** (`DependsOn` unchanged) — reusing
    the parent's own name "Dependencies" for this child was considered
    and rejected (confusing tautology, awkward `Dependencies.dependencies`
    field name).
  `RelatedPrsCommits`/`"Related PRs / Commits"` keeps its `LITERAL`
    alias — no casing-only fix exists for a heading containing a slash.
Updated the ASCII diagram, Model classes prose, REQ-001, and Task 1.3
  in Design Notes; recorded as a new Decisions Made entry. `example.md`
  needed no content changes beyond the "Related ADRs" → "Related
  Decisions" heading rename itself.
Nothing under `src`/`tests` was touched.

#### 2026-08-30T00:00:00.000Z - Update (example.md verified and marked canonical)
Cross-checked every implicit `SPACE_SEPARATED` heading alias in the
  design against the live engine (`models.md.alias_match. space_separated_name`) instead of assuming the derivation matched the
  intended heading text. Found and fixed 3 real bugs that would have
  broken `parse_feat` in Phase 1: `RelatedAdrs` (pre-existing since round
  1), `ExplicitlyOutOfScope`, `DependsOn` — all three now get an explicit
  `@alias(..., type=AliasType.LITERAL)`, added to Design Notes and
  recorded as a new Decisions Made entry. `example.md` itself needed no
  changes (its heading text was already the intended natural-English
  form); only the model-class documentation was wrong.
Marked `.specmgr/feat/feat-31-feature/example.md` as the canonical,
  implementation-ready worked example in Current Status above.
  `example-initial.md`/`example-revised.md` are superseded review-process
  artifacts — flagged as safe to remove, not yet deleted (awaiting
  explicit confirmation).
Nothing under `src`/`tests` was touched. Next: remove the two
  superseded example files once confirmed, then this feature is ready to
  come off the design-review Blocker and resume at Phase 1.

#### 2026-08-30T00:00:00.000Z - Update (third design-review round — ordering/comment/hyperlink questions)
Resolved three follow-up design questions and updated the Design Notes/
  Decisions Made accordingly:
  `### Related PRs / Commits`: confirmed it stays free-form, not
    regex-enforced as hyperlinks (the existing "no PR yet" placeholder
    idiom would otherwise break).
  `### Updates`/`### Decisions Made` both gain an optional `comment`
    field (`MarkdownSection3WithComment`, `req`'s `Level`/`Priority`
    precedent) to host a machine-readable ordering hint in
    `feat_template.md`/`feat_example.md`, rather than a bare editorial
    comment.
  `### Decisions Made` entries switch to the same full ISO8601
    timestamp as `### Updates` (not date-only), and both sections gain a
    real `@model_validator`-enforced newest-first ordering invariant —
    discovered along the way that `tsk_example.md` (newest-first) and
    `dec_example.md` (oldest-first) already disagree on direction with no
    enforcement either way; confirmed via
    `general/data/general_compact_history_instructions.md` that
    "newest first" is the existing, already-tool-supported convention for
    the ad hoc `### Recent Updates` this feature formalizes, so that's
    what both new sections enforce.
Nothing under `src`/`tests` was touched. Next: continue design review,
  or unblock and resume Phase 1 once the user confirms the design is
  final.

#### 2026-08-30T00:00:00.000Z - Update (second design-review round — Task List/Scope/Dependencies/Decisions Made structure)
The user drafted `example-revised.md` (annotated with review comments/
  open questions) building on the first `example.md`. Resolved every open
  question raised in it:
  `### Requirements`/`### Acceptance Criteria` become regex-validated
    lists (`REQ-\d{3}: ...`/checkbox `ACC-\d{3}: ...`), not opaque leaves.
  `### Scope` becomes a composite with mandatory `#### Included`/
    `#### Explicitly out of scope` leaves (both required).
  `### Dependencies` becomes a composite with optional `#### Depends on`/
    `#### Blocks` leaves (both optional).
  `### Task List` becomes a composite of `#### Phase N: ...` entries
    (regex-validated heading, unpadded numbering), each phase reusing
    `tsk.TaskItem` for its own flat checklist — a partial reversal of the
    original "Task List stays opaque" decision (per-item metadata still
    stays unparsed).
  `### Decisions Made` becomes a composite of dated
    `#### {yyyy-MM-dd} — {title}` entries, chosen over a formalized-flat-
    list alternative for consistency with `### Updates`.
  A new optional `### More Information` leaf is added under
    `## Progress`.
  Recorded all of the above as a new Decisions Made entry, explicitly
    superseding the earlier "mostly opaque leaves"/"Task List stays a
    single opaque leaf" decisions.
Updated this plan's REQ-001, the Design Notes' ASCII structure diagram
  and "Model classes" prose, Task 1.3, ACC-001, and the Scope section's
  "explicitly out of scope" bullet on Task List to match.
Nothing under `src`/`tests` was touched — the Blocker (design review
  pending before Phase 1) still applies; this round only revised the
  design itself, per explicit user instruction not to remove/change
  anything else yet.
Next: continue the design review (any further structural questions),
  then unblock and resume at Phase 1 once the user confirms.

#### 2026-08-30T00:00:00.000Z - Update (paused for design review after Phase 0)
Corrected: implementing Phase 0's package skeleton was premature — the
  user had asked for the design to be planned and reviewed, not for
  implementation to start. Nothing from Phase 0 is reverted (both commits,
  `31c5c30` and `164182e`, stay on the branch as-is); instead, this feature
  is explicitly paused here, recorded as a Blocker above, until the user
  completes a review pass over this plan's Design Notes and either confirms
  it or requests adjustments.
Also noted and resolved as a non-issue: an earlier "fyi, `sop` is still
  in development and not pushed yet" flag from the user turned out not to
  affect this branch — `git fetch origin dev` confirmed the `feat(sop): …`
  commits this branch's base (`c8f8a87`) sits on are already present on
  `origin/dev`, so `feat-31-feature`'s branch point is clean; no rebase
  needed.
Next: wait for the user's design review/adjustments before touching any
  further code or advancing the Task List.

#### 2026-08-30T00:00:00.000Z - Update (Phase 0: Scaffolding — complete)
Completed Tasks 0.1–0.4, the final tasks of Phase 0.
  Task 0.2: package skeleton — `feat/__init__.py` (docstring + `from . import prompts, resources, tools`), empty `feat/models/__init__.py` +
    `feat/models/v1/__init__.py`, `feat/tools/__init__.py`,
    `feat/resources/__init__.py`, `feat/prompts/__init__.py` (each with a
    docstring pointing at the phase that populates it), and the matching
    `tests/feat/{__init__,models/__init__,models/v1/__init__,tools/__init__, resources/__init__,prompts/__init__}.py` (all empty, mirroring
    `tests/dec/`'s exact convention). `feat/data/` deferred to Phase 3.
  Task 0.3: added Task 0.31 to `feat-7-various-improvements`'s Phase 0
    task list (migrate the 17 existing feature folders once this schema
    ships and Task 0.30's consolidation decision is made) plus a matching
    Recent Updates entry; extended Task 0.30's own background note to name
    `feat`'s planned `### Updates`/`#### {timestamp} — {title}` shape as a
    fourth divergent variant alongside `tsk`/`dec`/`sop`.
  Task 0.4: full quality gate green (`ruff format --check`/`ruff check`
    clean, `vulture src/ whitelist.py --min-confidence 60` clean, full
    `unittest` suite 2007 tests OK); committed as `31c5c30` ("docs(feat):
    plan the Feature (feat) artifact type feature"); commit hash posted to
    issue #31.
Next: Phase 1 (models + parser) — `feat/models/v1/{_util,frontmatter, body,document,parser,summary}.py`, `feat_reference.md`, and
  `tests/feat/models/v1/`.
Notes: `sop` (feat-30) is still unimplemented (planning only, no
  `src/biz/dfch/specmgr/sop/` package exists yet) — this feature's
  `Updates`/`UpdateEntry` design cites `feat-30-sop`'s **plan**, not its
  code, as precedent. `git status` after Task 0.4's commit shows a clean
  tree on branch `feat-31-feature`.

#### 2026-08-30T00:00:00.000Z - Update (planning)
Completed: Full design discussion with the user across two planning
  rounds: (1) extracted the common structure from all 17 existing
  `.specmgr/feat/*/README.md` files plus ADR e369ee2e and the two most
  recent "add artifact type" features (`feat-18-goal`, `feat-21-decision`)
  and the in-flight `feat-30-sop`; (2) resolved every open design question
  (body-modeling depth → mostly opaque leaves with a structured `Updates`
  section; addressing → keep `feat-NNN-slug` + folder + `README.md`,
  bespoke path resolution; `version` semantics → schema-version-only, drop
  the hand-bumped plan-revision meaning; status vocabulary → closed 4-set
  with no hyphens, `planning`/`progress`/`review`/`done`; MCP surface →
  full sop-style generic-dispatch lifecycle; `Updates` naming/shape →
  renamed from "Recent Updates" to "Updates", ISO8601-enforced heading
  regex copied from `feat-30-sop`'s plan one level deeper; migration of
  existing files → explicitly out of scope, tracked as a new
  `feat-7-various-improvements` backlog task instead; implementation
  branch → `feat-31-feature`).
Filed GitHub issue #31 ("Formalize the Feature artifact type ("feat")"),
  created branch `feat-31-feature` off `dev`, wrote this plan file.
Next: Phase 0 — package skeleton (`feat/__init__.py` + empty
  `models/v1`/`tools`/`resources`/`prompts`/`data` packages + `tests/feat/`
  skeleton), add Task 0.31 to `feat-7-various-improvements` and extend its
  Task 0.30 background note, then the Phase 0 quality gate + baseline
  commit.
Notes: `sop` (feat-30) is still unimplemented (planning only, no
  `src/biz/dfch/specmgr/sop/` package exists yet) — this feature's
  `Updates`/`UpdateEntry` design cites `feat-30-sop`'s **plan**, not its
  code, as precedent.
