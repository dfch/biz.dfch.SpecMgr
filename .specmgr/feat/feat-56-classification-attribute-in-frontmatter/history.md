# History: Classification Attribute in Frontmatter

#### 2026-09-02 21:30:00.000Z - Phase 4 (Docs and schema regeneration) complete
Ran `uv run --frozen specmgr schema --type <d> --output-dir src/biz/dfch/specmgr/<d>/data`
for each of the 11 affected domains (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr)
followed by a plain `uv run --frozen specmgr schema` (all types, default
`docs/` output) -- mirroring the two-tier docs-copy/packaged-copy pattern
already wired into `.pre-commit-config.yaml`/`.github/workflows/ci.yml` for
every existing domain, since `specmgr schema` itself only writes to one
`--output-dir` per invocation and has no built-in fan-out to a domain's own
packaged copy. This regenerated exactly 22 JSON Schema files -- the 11
`docs/<d>_schema.json` copies and the 11 packaged
`src/biz/dfch/specmgr/<d>/data/<d>_schema.json` copies -- each now carrying
the new optional `classification` property (`anyOf` string/null,
`default: null`) inside its `<D>Frontmatter` definition (ACC-006). This is
exactly what the 4 previously-expected schema-drift test failures
(`tests/{dec,feat,sop,vcr}/resources/test_*_schema.py`, comparing the
packaged JSON against a freshly generated schema) were waiting on.
Ran `uv run --frozen specmgr docs`, regenerating `docs/GENERATED.md` and
424 files under `docs/api/`; the diff is exactly the new
`set_classification` tool/module (`docs/api/biz.dfch.specmgr.general.tools.set_classification.md`,
new file), its listing in `docs/api/README.md`/`docs/GENERATED.md`, the
`classification` field showing up in
`docs/api/biz.dfch.specmgr.models.md.frontmatter.md`, the
`set_classification` paragraph in `docs/api/biz.dfch.specmgr.server.md`
(mirroring `server.py`'s own module docstring, already written in Phase 2),
and the test-file count in `docs/GENERATED.md` bumping from 332 to 333 for
the new `tests/general/tools/test_set_classification.py`. Also ran
`uv run --frozen specmgr adr-toc`: no drift, `docs/adr/README.md` was
already current.
Updated `AGENTS.md`'s Status section: added a
", classification changes through the generic `set_classification` tool
(`type=\"<d>\"`)" clause into each of the 11 whole-body domains' own bullets
(req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr), matching each bullet's own
existing update/set_status/delete clause wording and line-wrap style
exactly (including extending sop's and feat's own "no
`update_<d>`/`set_status_<d>`" negation sentences to also name
`set_classification_<d>`, since both bullets already call out the absence
of per-domain mutation tools by name). Added a matching `set_classification`
description to the cross-cutting `general/` bullet, in the same prose
pattern as the existing `set_status`/`delete` descriptions there --
explicitly noting it covers the *eleven* whole-body domains only (`adr`
excluded, same reason as `update`/`delete`). Did not touch the `adr`
bullet, the "Still genuinely missing" list, or any other section, per the
task's explicit instructions.
Ran the full quality gate: `ruff format --check` and `ruff check` are
clean; `vulture src/ whitelist.py --min-confidence 60` is clean; the full
`unittest` suite (3029 tests) is now 100% green -- the 4 previously-expected
schema-drift failures are resolved, with no other regressions (ACC-007).
Re-ran both `specmgr schema` (all 11 packaged copies + the `docs/` copies)
and `specmgr docs` a second time after the `AGENTS.md` edit to confirm
idempotency: every schema file reported "unchanged" and `git status`
showed no further diff beyond the one new `set_classification` API doc
page already produced by the first run (ACC-006's "no unrelated diff"
requirement).

#### 2026-09-02 20:15:00.000Z - Phase 3 (Prompt instructions) complete
Updated all 20 packaged prompt-instruction data files for the 10
whole-body domains with prompts (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr
-- `uc` skipped per its own separately-filed issue #57 gap, `adr`
skipped as out of scope for classification entirely). In each
`<d>_create_instructions.md`'s "Later revisions" step (numbered
differently per domain -- e.g. req/tsk/qa/gol/rsk/dec/feat/vcr use
"## 5.", prb uses "## 10.", sop uses "## 6."), the existing parenthetical
list of generic tool calls (`update(id, type="<d>", content)` and
`set_status(id, type="<d>", status)`) now also names
`set_classification(id, type="<d>", classification)`, in each file's own
existing prose style and line-wrap width -- no section numbering,
heading text, or other wording was otherwise touched. In each
`<d>_update_instructions.md`'s "Map the requested change to the right
tool" step, a new bullet was appended directly after the existing
``- A change to `status` -> set_status(...)`` bullet: "A change to `classification` -> `set_classification(id, type="<d>", classification)` instead -- `update` never accepts or changes `classification`. Fully free-text; a blank or whitespace-only value clears it back to `None`/absent." -- worded identically across all 10 files since, unlike `status`, `classification` has no per-domain closed vocabulary to describe. sop's create-instructions step 6 additionally had its existing "`sop` has no per-domain `update_sop`/`set_status_sop` tools" sentence extended to "`update_sop`/`set_status_sop`/`set_classification_sop`" for
consistency, since sop is the one domain whose prose already calls out
the absence of per-domain mutation tools by name.
Before editing, searched `tests/` for any test asserting on the literal
content of these instructions files (`grep -rn "create_instructions\|update_instructions" tests/`) and confirmed every
`test_create_<d>.py`/`test_update_<d>.py` prompt test uses `assertIn`/
`assertLess(result.index(...))` substring checks against the rendered
prompt text, never a full-string `assertEqual` against the whole file
-- appending new sentences/bullets without removing or reordering any
existing substring could not break them, and none did.
Ran the full quality gate: `ruff format --check` and `ruff check` are
clean (these are `.md` data files, unaffected either way); `vulture src/ whitelist.py --min-confidence 60` is clean; the full `unittest`
suite (3029 tests) has exactly the same 4 known, pre-existing failures
from Phase 1 (`tests/{dec,feat,sop,vcr}/resources/test_*_schema.py`,
schema drift closed by Phase 4) -- no new regressions from Phase 3's
changes.

#### 2026-09-02 18:30:00.000Z - Phase 2 (Generic set_classification tool) complete
Added `src/biz/dfch/specmgr/general/tools/set_classification.py`: the generic, cross-domain `set_classification(id, type, classification)` tool for the eleven whole-body document types (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr). It is an 11-way dispatch mirroring `set_status.py`'s adapter-dispatch pattern exactly (per-domain lock, `load_by_id`, `_path_safety.assert_within`, raw-body re-read via `frontmatter.loads(...).content` and verbatim re-persistence, `wrap_tool_errors(domain=..., tool="set_classification", channel=FRONTMATTER_CHANNEL)`-wrapped `XFrontmatter(**fm_data)` reconstruction, `write_<d>_file`, domain `XNotFoundError`) but replaces `classification` instead of `status`, with no `superseded_by` parameter and no `adr` adapter -- `adr`'s separate `AdrFrontmatter` model is out of scope for this feature per the plan's Scope section. The `feat` adapter diverges the same way `_update_feat`/`_set_status_feat` do (bespoke `feat.tools._paths` folder-per-document id resolution). Blank/whitespace `classification` values clear to `None` automatically via the shared `MarkdownFrontmatter` blank-to-`None` validator from Phase 1 -- no special-casing was added in `set_classification.py` itself, confirmed by a dedicated test. `_path_safety.validate_id(type, id)` runs before any dispatch, so a path-injection attempt, a wrong-format id, or a truly-unknown `type` string (e.g. `"bogus"`) raises `ValueError` before any file access, exactly matching `set_status`'s own behavior for the same misuse (REQ-004/ACC-005).
Registered the tool: added the import/`__all__` entry to `src/biz/dfch/specmgr/general/tools/__init__.py` (with a docstring paragraph describing it, alphabetically placed alongside `set_status`), and added a description paragraph to `server.py`'s module docstring immediately after the existing `set_status` description, following the same prose style. No new top-level import was needed in `server.py` itself -- the existing `general` package import at the bottom of the file already wires up the new `@mcp.tool()` registration via the side-effect import chain.
Added `tests/general/tools/test_set_classification.py`, structurally mirroring `tests/general/tools/test_set_status.py`'s fixture strategy (temp `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`, one `_Case` per domain seeded via the domain's own `create_<d>` tool) but simplified for the 11-domain (no-`adr`), no-closed-vocabulary shape of `classification`. Covers: setting a classification value, reading it back, and confirming `updated` is bumped while the raw body stays byte-identical (ACC-002); clearing via a blank/whitespace string back to `None`, verified on both the returned model and the on-disk YAML (ACC-003); an unsupported `type="bogus"` raising `ValueError` -- explicitly compared, by exception class, against `set_status`'s own error for the identical misuse (ACC-005); per-domain not-found errors for an unknown id; and `_path_safety` injection/wrong-format-id rejection plus an `assert_within`-is-actually-called spy check, both mirroring `test_set_status.py`'s own coverage.
Ran the full quality gate: `ruff format --check` and `ruff check` are clean; `vulture src/ whitelist.py --min-confidence 60` is clean (the new adapters are all reached through the `_ADAPTERS` dispatch table, so no false-positive unused-code flags); the full `unittest` suite (3029 tests) has exactly the same 4 known, pre-existing failures from Phase 1 (`tests/{dec,feat,sop,vcr}/resources/test_*_schema.py`, schema drift closed by Phase 4) -- no new regressions from Phase 2's changes.

#### 2026-09-02 16:45:00.000Z - Phase 1 (Model change) complete
Added `classification: str | None = None` to `MarkdownFrontmatter` (`src/biz/dfch/specmgr/models/md/frontmatter.py`), immediately after `version`, documented in the class docstring's Parameters section, and normalized via the existing `blank_to_none` helper by adding `classification` to the existing `_optional_blank_to_none` `field_validator("created", "updated", ..., mode="before")` field list rather than adding a separate validator -- it needs the exact same blank-to-None behavior as `created`/`updated` and no other validation, so extending the existing validator's field tuple was the more idiomatic fit for this file. Added 5 new test cases to `tests/models/md/test_frontmatter.py` (`TestMarkdownFrontmatter`): default-to-`None`, explicit-value round-trip, blank-string-to-`None`, whitespace-only-to-`None`, and a pre-existing (no `classification` key) frontmatter dict still parsing with `classification is None` (ACC-004 at the base-model level). Added a `classification` entry to `whitelist.py`'s "Pydantic model fields read only via (de)serialization/rendering" section, since nothing in `src/` accesses `.classification` as a plain attribute yet (Phase 2's `set_classification` tool will add real usage, mirroring `set_status.py`'s `.status` access) -- without it, `vulture` flagged the new field as a false-positive unused variable. Ran the full quality gate: `ruff format --check` and `ruff check` are clean; `vulture src/ whitelist.py --min-confidence 60` is clean; the full `unittest` suite has 4 known failures (`tests/dec/resources/test_dec_schema.py`, `tests/feat/resources/test_feat_schema.py`, `tests/sop/resources/test_sop_schema.py`, `tests/vcr/resources/test_vcr_schema.py`), all comparing the packaged static schema JSON against a freshly generated schema that now includes `classification` -- this is the expected, Phase-4-owned consequence of the model change (Task 4.1 regenerates and commits these schemas) and was left unresolved here per this phase's explicit scope boundary (no `specmgr schema` run in Phase 1).

#### 2026-09-02 12:00:00.000Z - Feature drafted
Feature drafted from GitHub issue #56, covering the shared MarkdownFrontmatter classification field and a new generic set_classification tool; ADR's separate frontmatter model is explicitly out of scope. A related uc-prompts gap discovered during drafting was filed as a separate GitHub issue (#57) rather than folded into this feature's scope.
