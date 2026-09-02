---
created: '2026-09-02T09:50:23.991493'
id: feat-56-classification-attribute-in-frontmatter
status: planning
type: feat
updated: '2026-09-02T21:30:00.000000'
version: 1.0.0
---

# Feature: Classification Attribute in Frontmatter

## Plan

### Overview

Add an optional, free-text `classification` attribute to the shared frontmatter model used by all document domains, so documents can be tagged with a classification label -- e.g. security classification, business-confidentiality level, or a project-specific taxonomy -- without specmgr imposing any single fixed scheme. The field is optional and defaults to absent, so every existing document on disk keeps parsing successfully unchanged.

### Requirements

- REQ-001: Add an optional `classification: str | None = None` field to the shared `MarkdownFrontmatter` model (models/md), normalizing blank/whitespace-only to `None` via the existing `blank_to_none` helper, so it is inherited by all eleven whole-body domain frontmatter classes (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr).

- REQ-002: Existing documents without a `classification` key in frontmatter must continue to parse successfully, with `classification` resolving to `None`.

- REQ-003: Add a new generic `set_classification(id, type, classification)` tool in `general/tools/` that sets or clears the `classification` frontmatter field for a document of the given type, mirroring `set_status.py`'s adapter-dispatch pattern (per-domain `XFrontmatter` reconstruction wrapped in `wrap_tool_errors`/`FRONTMATTER_CHANNEL`, `_path_safety.validate_id`/`assert_within` guards), bumping `updated`, leaving the body and all other frontmatter fields untouched.

- REQ-004: `set_classification` must reject an invalid/unsupported `type` value the same way the existing generic `set_status`/`update`/`delete` tools do.

- REQ-005: The generated JSON Schema for every affected domain (`specmgr://<d>/schema`) must reflect the new optional `classification` field after running `specmgr schema`.

- REQ-006: `docs/GENERATED.md`/`docs/api/` and `server.py`'s module docstring must be updated to document the new tool.

- REQ-007: Update the 10 whole-body domains' (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) packaged `<d>_create_instructions.md`/`<d>_update_instructions.md` files to reference `set_classification`, mirroring the existing `set_status` mentions.

### Acceptance Criteria

- [ ] ACC-001: A document created via any of the 11 `create_<d>` tools, then read back via `get_<d>` or `parse_<d>`, has `classification` == `None` when never set.

- [ ] ACC-002: Calling `set_classification(id, type, "Confidential")` on an existing document, then reading it back, shows `classification: Confidential` in frontmatter and an updated `updated` timestamp; the body is byte-identical; the reconstruction is wrapped in `wrap_tool_errors`/`FRONTMATTER_CHANNEL` exactly like every `set_status.py` adapter.

- [ ] ACC-003: Calling `set_classification(id, type, "")` (or whitespace) clears classification back to `None`/absent in the rendered YAML.

- [ ] ACC-004: A pre-existing on-disk document (authored before this feature, no `classification` key) still parses successfully via `parse_<d>`/`get_<d>` with no validation error.

- [ ] ACC-005: `set_classification(id, type="bogus", ...)` raises the same class of error the generic `set_status` tool raises for an unsupported type, following the same `set_status.py`-mirrored dispatch/guard structure.

- [ ] ACC-006: `uv run --frozen specmgr schema` regenerates all 11 affected domain schemas with the new field and no unrelated diff; `uv run --frozen specmgr docs` regenerates docs/GENERATED.md and docs/api/ cleanly.

- [ ] ACC-007: Full test suite (`uv run --frozen python -m unittest discover ...`) passes, including new unit tests for the field and the new tool across all 11 domains.

- [ ] ACC-008: Each of the 10 domains' create instructions mentions optionally calling `set_classification` after creation, and each domain's update instructions gains a "change to `classification`" mapping bullet pointing at `set_classification(id, type="<d>", classification)`, matching the existing `status`/`set_status` pattern.

### Scope

#### Included

- Optional `classification: str | None = None` field on the shared `MarkdownFrontmatter` base (models/md/frontmatter.py), inherited by all 11 whole-body domain frontmatter classes.

- Blank/whitespace-only value normalizes to `None`, reusing the existing `blank_to_none` helper (models/md/\_util.py).

- New generic `set_classification(id, type, classification)` tool in general/tools/, dispatch-mirroring `set_status.py`'s 11 whole-body adapters (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr), including `_path_safety.validate_id`/`assert_within` guards and `wrap_tool_errors`/`FRONTMATTER_CHANNEL` wrapping.

- Registration of the new tool in server.py's import/docstring.

- Regenerated JSON Schemas (`specmgr <d>/schema` resources) and docs (`specmgr docs`) for all 11 affected domains.

- Unit tests covering the new field (parse/round-trip, blank-to-None) and the new tool (happy path, invalid type, clearing) across all 11 domains.

- Updated `<d>_create_instructions.md`/`<d>_update_instructions.md` packaged data files for the 10 whole-body domains with prompts, referencing `set_classification` alongside the existing `set_status` mentions.

#### Explicitly Out Of Scope

- ADR's separate `AdrFrontmatter` model (models/adr/) -- not touched by this feature.

- Any closed vocabulary / enum for classification values -- it stays fully free-text per the issue, no validation beyond blank-to-None.

- Any UI/reporting feature that filters or groups documents by classification (e.g. a `list_<d>` filter) -- out of scope, may be a future feature.

- Adding `classification` as a settable parameter directly on the 11 `create_<d>` tools -- explicitly rejected in favor of the single generic `set_classification` tool.

- Any per-domain `set_classification_<d>` tools -- only the one generic dispatch tool is added, consistent with ADR 36905d5b-8057-4294-8665-c7eed5534db0's "generic tool, not per-domain" convention.

- Adding `uc/prompts/create_uc.py`/`update_uc.py` -- `uc` has no prompts sub-package at all yet; this pre-existing gap was discovered while drafting this feature and was filed separately as GitHub issue #57 rather than folded into this feature's scope.

### Design Notes

Before this feature, a REQ document's frontmatter looks like:

```yaml
---
id: 3fa1c2e4-9b7d-4e2a-8c1f-1a2b3c4d5e6f
type: req
status: draft
created: 2026-09-02T10:00:00.000000
updated: 2026-09-02T10:00:00.000000
version: 1.0.0
---
```

After a caller calls `set_classification(id, type="req", classification="Confidential")`, the same document's frontmatter becomes:

```yaml
---
id: 3fa1c2e4-9b7d-4e2a-8c1f-1a2b3c4d5e6f
type: req
status: draft
created: 2026-09-02T10:00:00.000000
updated: 2026-09-02T11:30:00.000000
version: 1.0.0
classification: Confidential
---
```

Only `updated` and `classification` change; the body is untouched.

Since feat-27-validation (closed 2026-09-01) added `wrap_tool_errors`/`FRONTMATTER_CHANNEL` (models/md/\_errors.py) and already applies it to every `set_status.py` adapter around its `XFrontmatter(**fm_data)` reconstruction call, `set_classification` must wrap its own per-domain frontmatter reconstruction the same way (`domain="<d>"`, `tool="set_classification"`, `channel=FRONTMATTER_CHANNEL`). Skipping this would make `set_classification`'s errors regress to a pre-feat-27 bare/unhelpful shape while every sibling tool has the enriched (field path + line reference + fix hint) shape.

### Related Decisions

- 36905d5b-8057-4294-8665-c7eed5534db0 (ADR): establishes the generic, type-dispatched tool convention (already used by `update`/`set_status`/`delete`) that `set_classification` follows instead of adding per-domain tools.

- 9c687bb1-8ee7-41c8-84ec-07606356bc73 (ADR): enforces doc generation/lint/tests locally via pre-commit hook, relevant to Phase 4's schema/docs regeneration step.

### Task List

#### Phase 1: Model change

- [x] Task 1.1: Add `classification: str | None = None` field + blank-to-None validator to `MarkdownFrontmatter` (models/md/frontmatter.py), reusing `blank_to_none`.

- [x] Task 1.2: Add/update unit tests for the base frontmatter model covering classification parse, round-trip, and blank/whitespace-to-None.

- [x] Task 1.3: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) and fix any regressions before moving on.

#### Phase 2: Generic set_classification tool

- [x] Task 2.1: Implement `general/tools/set_classification.py` mirroring `set_status.py`'s structure (11 adapters, `_path_safety` guards, `wrap_tool_errors`/`FRONTMATTER_CHANNEL`).

- [x] Task 2.2: Register the new tool's import in server.py and update its module docstring.

- [x] Task 2.3: Add unit tests for `set_classification` across all 11 domains (set, clear via blank, invalid type error, path-safety rejection).

- [x] Task 2.4: Run the full test suite and fix any regressions before moving on.

#### Phase 3: Prompt instructions

- [x] Task 3.1: Update the 10 whole-body domains' (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) `<d>_create_instructions.md` files to mention `set_classification` in the "Later revisions" step.

- [x] Task 3.2: Update the same 10 domains' `<d>_update_instructions.md` files with a "change to `classification`" mapping bullet, matching the existing `status`/`set_status` bullet.

- [x] Task 3.3: Run the full test suite and fix any regressions before moving on.

#### Phase 4: Docs and schema regeneration

- [x] Task 4.1: Run `uv run --frozen specmgr schema` and commit the regenerated JSON Schemas for all 11 affected domains.

- [x] Task 4.2: Run `uv run --frozen specmgr docs` and commit the regenerated docs/GENERATED.md + docs/api/.

- [x] Task 4.3: Update AGENTS.md's per-domain bullets / general/ bullet to mention `set_classification` alongside `set_status`/`update`/`delete`.

- [x] Task 4.4: Run the full test suite and fix any regressions before moving on.

#### Phase 5: Verification

- [ ] Task 5.1: Run the full test suite, `ruff format --check`, `ruff check`, and `vulture`; fix any regressions.

- [ ] Task 5.2: Manually verify a pre-existing on-disk document (no classification key) still parses via `parse_<d>`/`get_<d>`.

## Progress

### Current Status

**As of 2026-09-02**: Phases 1 (Model change), 2 (Generic `set_classification` tool), 3 (Prompt instructions), and 4 (Docs and schema regeneration) are done. The shared `MarkdownFrontmatter` model has an optional, free-text `classification: str | None = None` field that normalizes blank/whitespace-only input to `None`, inherited by all eleven whole-body domain frontmatter classes. The new generic `set_classification(id, type, classification)` tool in `general/tools/` dispatches to one adapter per whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr -- `adr` deliberately excluded), each shaped exactly like `set_status.py`'s corresponding adapter (same domain lock, `load_by_id`, `_path_safety.assert_within` guard, raw-body re-read/re-persistence, `wrap_tool_errors`/`FRONTMATTER_CHANNEL`-wrapped `XFrontmatter` reconstruction) but replacing `classification` instead of `status`, with no `superseded_by`-style parameter. It is registered in `server.py`'s module docstring and `general/tools/__init__.py`. New unit tests (`tests/general/tools/test_set_classification.py`) cover setting a value (ACC-002), clearing via blank/whitespace (ACC-003), an unsupported `type="bogus"` raising `ValueError` matching `set_status`'s own behavior for the same misuse (ACC-005), `type="adr"` raising `KeyError` (matching the generic `update` tool's own real, if undocumented, behavior for a UUID-shaped-but-out-of-dispatch type), per-domain not-found errors, and `_path_safety` injection/wrong-format-id rejection. All 10 whole-body domains' (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) packaged `<d>_create_instructions.md`/`<d>_update_instructions.md` prompt files now reference `set_classification` alongside the existing `set_status` mentions (ACC-008); `uc` and `adr` remain untouched by design. All 11 affected domains' JSON Schemas (`docs/<d>_schema.json` and each domain's packaged `src/biz/dfch/specmgr/<d>/data/<d>_schema.json`) have been regenerated via `specmgr schema` and now include `classification` (ACC-006); `docs/GENERATED.md`/`docs/api/` have been regenerated via `specmgr docs` (including a new `docs/api/biz.dfch.specmgr.general.tools.set_classification.md`); `AGENTS.md`'s per-domain bullets and the cross-cutting `general/` bullet now mention `set_classification` alongside `set_status`/`update`/`delete`. The 4 previously-expected schema-drift failures in `tests/{dec,feat,sop,vcr}/resources/test_*_schema.py` are now resolved -- the full test suite (3029 tests) is 100% green (ACC-007). `ruff format --check`, `ruff check`, and `vulture` are clean, and both `specmgr schema` and `specmgr docs` were confirmed idempotent by a second run after the `AGENTS.md` edit producing no further diff. Only Phase 5 (Verification) remains.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 21:30:00.000Z — Phase 4 (Docs and schema regeneration) complete

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

#### 2026-09-02 20:15:00.000Z — Phase 3 (Prompt instructions) complete

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
`- A change to \`status\` -> set_status(...)`bullet: "A change to`classification`->`set_classification(id, type="<d>",
classification)`instead --`update`never accepts or changes`classification`. Fully free-text; a blank or whitespace-only value clears it back to `None`/absent." -- worded identically across all 10 files since, unlike `status`, `classification` has no per-domain closed vocabulary to describe. sop's create-instructions step 6 additionally had its existing "`sop`has no per-domain`update_sop`/`set_status_sop` tools" sentence extended to "`update_sop`/`set_status_sop`/`set_classification_sop\`" for
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

#### 2026-09-02 18:30:00.000Z — Phase 2 (Generic set_classification tool) complete

Added `src/biz/dfch/specmgr/general/tools/set_classification.py`: the generic, cross-domain `set_classification(id, type, classification)` tool for the eleven whole-body document types (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr). It is an 11-way dispatch mirroring `set_status.py`'s adapter-dispatch pattern exactly (per-domain lock, `load_by_id`, `_path_safety.assert_within`, raw-body re-read via `frontmatter.loads(...).content` and verbatim re-persistence, `wrap_tool_errors(domain=..., tool="set_classification", channel=FRONTMATTER_CHANNEL)`-wrapped `XFrontmatter(**fm_data)` reconstruction, `write_<d>_file`, domain `XNotFoundError`) but replaces `classification` instead of `status`, with no `superseded_by` parameter and no `adr` adapter -- `adr`'s separate `AdrFrontmatter` model is out of scope for this feature per the plan's Scope section. The `feat` adapter diverges the same way `_update_feat`/`_set_status_feat` do (bespoke `feat.tools._paths` folder-per-document id resolution). Blank/whitespace `classification` values clear to `None` automatically via the shared `MarkdownFrontmatter` blank-to-`None` validator from Phase 1 -- no special-casing was added in `set_classification.py` itself, confirmed by a dedicated test. `_path_safety.validate_id(type, id)` runs before any dispatch, so a path-injection attempt, a wrong-format id, or a truly-unknown `type` string (e.g. `"bogus"`) raises `ValueError` before any file access, exactly matching `set_status`'s own behavior for the same misuse (REQ-004/ACC-005).

Registered the tool: added the import/`__all__` entry to `src/biz/dfch/specmgr/general/tools/__init__.py` (with a docstring paragraph describing it, alphabetically placed alongside `set_status`), and added a description paragraph to `server.py`'s module docstring immediately after the existing `set_status` description, following the same prose style. No new top-level import was needed in `server.py` itself -- the existing `general` package import at the bottom of the file already wires up the new `@mcp.tool()` registration via the side-effect import chain.

Added `tests/general/tools/test_set_classification.py`, structurally mirroring `tests/general/tools/test_set_status.py`'s fixture strategy (temp `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`, one `_Case` per domain seeded via the domain's own `create_<d>` tool) but simplified for the 11-domain (no-`adr`), no-closed-vocabulary shape of `classification`. Covers: setting a classification value, reading it back, and confirming `updated` is bumped while the raw body stays byte-identical (ACC-002); clearing via a blank/whitespace string back to `None`, verified on both the returned model and the on-disk YAML (ACC-003); an unsupported `type="bogus"` raising `ValueError` -- explicitly compared, by exception class, against `set_status`'s own error for the identical misuse (ACC-005); per-domain not-found errors for an unknown id; and `_path_safety` injection/wrong-format-id rejection plus an `assert_within`-is-actually-called spy check, both mirroring `test_set_status.py`'s own coverage.

Ran the full quality gate: `ruff format --check` and `ruff check` are clean; `vulture src/ whitelist.py --min-confidence 60` is clean (the new adapters are all reached through the `_ADAPTERS` dispatch table, so no false-positive unused-code flags); the full `unittest` suite (3029 tests) has exactly the same 4 known, pre-existing failures from Phase 1 (`tests/{dec,feat,sop,vcr}/resources/test_*_schema.py`, schema drift closed by Phase 4) -- no new regressions from Phase 2's changes.

#### 2026-09-02 16:45:00.000Z — Phase 1 (Model change) complete

Added `classification: str | None = None` to `MarkdownFrontmatter` (`src/biz/dfch/specmgr/models/md/frontmatter.py`), immediately after `version`, documented in the class docstring's Parameters section, and normalized via the existing `blank_to_none` helper by adding `classification` to the existing `_optional_blank_to_none` `field_validator("created", "updated", ..., mode="before")` field list rather than adding a separate validator -- it needs the exact same blank-to-None behavior as `created`/`updated` and no other validation, so extending the existing validator's field tuple was the more idiomatic fit for this file. Added 5 new test cases to `tests/models/md/test_frontmatter.py` (`TestMarkdownFrontmatter`): default-to-`None`, explicit-value round-trip, blank-string-to-`None`, whitespace-only-to-`None`, and a pre-existing (no `classification` key) frontmatter dict still parsing with `classification is None` (ACC-004 at the base-model level). Added a `classification` entry to `whitelist.py`'s "Pydantic model fields read only via (de)serialization/rendering" section, since nothing in `src/` accesses `.classification` as a plain attribute yet (Phase 2's `set_classification` tool will add real usage, mirroring `set_status.py`'s `.status` access) -- without it, `vulture` flagged the new field as a false-positive unused variable. Ran the full quality gate: `ruff format --check` and `ruff check` are clean; `vulture src/ whitelist.py --min-confidence 60` is clean; the full `unittest` suite has 4 known failures (`tests/dec/resources/test_dec_schema.py`, `tests/feat/resources/test_feat_schema.py`, `tests/sop/resources/test_sop_schema.py`, `tests/vcr/resources/test_vcr_schema.py`), all comparing the packaged static schema JSON against a freshly generated schema that now includes `classification` -- this is the expected, Phase-4-owned consequence of the model change (Task 4.1 regenerates and commits these schemas) and was left unresolved here per this phase's explicit scope boundary (no `specmgr schema` run in Phase 1).

#### 2026-09-02 12:00:00.000Z — Feature drafted

Feature drafted from GitHub issue #56, covering the shared MarkdownFrontmatter classification field and a new generic set_classification tool; ADR's separate frontmatter model is explicitly out of scope. A related uc-prompts gap discovered during drafting was filed as a separate GitHub issue (#57) rather than folded into this feature's scope.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 18:30:00.000Z — type="adr" surfaces as KeyError, not ValueError

While implementing Task 2.1, discovered that `_path_safety.validate_id` treats `adr` as one of its known UUID-shaped types (it is in `_UUID_TYPES` for use by `get_<d>`/`update`/`set_status`), so a well-formed UUID id with `type="adr"` passes `validate_id` even though `set_classification`'s own dispatch table has no `"adr"` entry -- the rejection then surfaces as a `KeyError` from the `_ADAPTERS[type]` lookup itself, not a `ValueError`. Verified this is not a bug introduced here but the same pre-existing, real (if undocumented) behavior the generic `update` tool already has for `type="adr"` (`update` also excludes `adr` from its own dispatch table for the same reason -- ADR's section-level mutation contract has no whole-body replace). Rather than adding special-case `adr` rejection logic to `set_classification` that `update` itself does not have, `set_classification` was left to inherit the identical `KeyError` behavior for `type="adr"`, with a test (`test_adr_type_is_not_supported`) pinning and documenting this precedent instead of asserting a `ValueError` that would diverge from `update`'s own established pattern.

#### 2026-09-02 12:00:00.000Z — Locked scope, API shape, and validation for classification

Three key decisions were made while drafting this feature: (1) the new `classification` field is added only to the shared `MarkdownFrontmatter` base used by the 11 whole-body domains -- ADR's separate `AdrFrontmatter` model is explicitly excluded; (2) rather than adding a `classification` parameter to each of the 11 `create_<d>` tools, a single new generic `set_classification(id, type, classification)` tool is added instead, mirroring the existing `set_status` tool's dispatch pattern, so it can be used both right after creation and for later changes; (3) `classification` stays fully free-text with blank/whitespace normalized to `None` -- no closed vocabulary or enum, per the source issue's explicit requirement.

### Related PRs / Commits

- [Issue #56](https://github.com/dfch/biz.dfch.SpecMgr/issues/56): source GitHub issue for this feature ("Classificatoin in frontmatter").

- [Issue #57](https://github.com/dfch/biz.dfch.SpecMgr/issues/57): related but separately-scoped gap discovered during drafting -- `uc` domain has no `create_uc`/`update_uc` prompts.
