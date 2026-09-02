---
created: '2026-09-02T09:50:23.991493'
id: feat-56-classification-attribute-in-frontmatter
status: planning
type: feat
updated: '2026-09-02T16:45:00.000000'
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

- Blank/whitespace-only value normalizes to `None`, reusing the existing `blank_to_none` helper (models/md/_util.py).

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

Since feat-27-validation (closed 2026-09-01) added `wrap_tool_errors`/`FRONTMATTER_CHANNEL` (models/md/_errors.py) and already applies it to every `set_status.py` adapter around its `XFrontmatter(**fm_data)` reconstruction call, `set_classification` must wrap its own per-domain frontmatter reconstruction the same way (`domain="<d>"`, `tool="set_classification"`, `channel=FRONTMATTER_CHANNEL`). Skipping this would make `set_classification`'s errors regress to a pre-feat-27 bare/unhelpful shape while every sibling tool has the enriched (field path + line reference + fix hint) shape.

### Related Decisions

- 36905d5b-8057-4294-8665-c7eed5534db0 (ADR): establishes the generic, type-dispatched tool convention (already used by `update`/`set_status`/`delete`) that `set_classification` follows instead of adding per-domain tools.

- 9c687bb1-8ee7-41c8-84ec-07606356bc73 (ADR): enforces doc generation/lint/tests locally via pre-commit hook, relevant to Phase 4's schema/docs regeneration step.

### Task List

#### Phase 1: Model change

- [x] Task 1.1: Add `classification: str | None = None` field + blank-to-None validator to `MarkdownFrontmatter` (models/md/frontmatter.py), reusing `blank_to_none`.

- [x] Task 1.2: Add/update unit tests for the base frontmatter model covering classification parse, round-trip, and blank/whitespace-to-None.

- [x] Task 1.3: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) and fix any regressions before moving on.

#### Phase 2: Generic set_classification tool

- [ ] Task 2.1: Implement `general/tools/set_classification.py` mirroring `set_status.py`'s structure (11 adapters, `_path_safety` guards, `wrap_tool_errors`/`FRONTMATTER_CHANNEL`).

- [ ] Task 2.2: Register the new tool's import in server.py and update its module docstring.

- [ ] Task 2.3: Add unit tests for `set_classification` across all 11 domains (set, clear via blank, invalid type error, path-safety rejection).

- [ ] Task 2.4: Run the full test suite and fix any regressions before moving on.

#### Phase 3: Prompt instructions

- [ ] Task 3.1: Update the 10 whole-body domains' (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) `<d>_create_instructions.md` files to mention `set_classification` in the "Later revisions" step.

- [ ] Task 3.2: Update the same 10 domains' `<d>_update_instructions.md` files with a "change to `classification`" mapping bullet, matching the existing `status`/`set_status` bullet.

- [ ] Task 3.3: Run the full test suite and fix any regressions before moving on.

#### Phase 4: Docs and schema regeneration

- [ ] Task 4.1: Run `uv run --frozen specmgr schema` and commit the regenerated JSON Schemas for all 11 affected domains.

- [ ] Task 4.2: Run `uv run --frozen specmgr docs` and commit the regenerated docs/GENERATED.md + docs/api/.

- [ ] Task 4.3: Update AGENTS.md's per-domain bullets / general/ bullet to mention `set_classification` alongside `set_status`/`update`/`delete`.

- [ ] Task 4.4: Run the full test suite and fix any regressions before moving on.

#### Phase 5: Verification

- [ ] Task 5.1: Run the full test suite, `ruff format --check`, `ruff check`, and `vulture`; fix any regressions.

- [ ] Task 5.2: Manually verify a pre-existing on-disk document (no classification key) still parses via `parse_<d>`/`get_<d>`.

## Progress

### Current Status

**As of 2026-09-02**: Phase 1 (Model change) is done. The shared `MarkdownFrontmatter` model now has an optional, free-text `classification: str | None = None` field that normalizes blank/whitespace-only input to `None` via the existing `blank_to_none` helper, inherited by all eleven whole-body domain frontmatter classes. New unit tests cover default-to-`None`, round-trip, blank/whitespace normalization, and pre-existing (no-`classification`-key) frontmatter dicts still parsing (ACC-004 at the base-model level). `ruff format --check`, `ruff check`, and `vulture` are clean. The full test suite has 4 known, expected failures in `tests/{dec,feat,sop,vcr}/resources/test_*_schema.py` -- these compare the packaged static JSON Schema files against a fresh `generate_*_schema()` call and now diverge because the model gained a field; this drift is exactly what Phase 4 Task 4.1 (`specmgr schema` regeneration) is designed to close, and Phase 1 was explicitly scoped to not run `specmgr schema`. Phase 2 (generic `set_classification` tool) has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 16:45:00.000Z — Phase 1 (Model change) complete

Added `classification: str | None = None` to `MarkdownFrontmatter` (`src/biz/dfch/specmgr/models/md/frontmatter.py`), immediately after `version`, documented in the class docstring's Parameters section, and normalized via the existing `blank_to_none` helper by adding `classification` to the existing `_optional_blank_to_none` `field_validator("created", "updated", ..., mode="before")` field list rather than adding a separate validator -- it needs the exact same blank-to-None behavior as `created`/`updated` and no other validation, so extending the existing validator's field tuple was the more idiomatic fit for this file. Added 5 new test cases to `tests/models/md/test_frontmatter.py` (`TestMarkdownFrontmatter`): default-to-`None`, explicit-value round-trip, blank-string-to-`None`, whitespace-only-to-`None`, and a pre-existing (no `classification` key) frontmatter dict still parsing with `classification is None` (ACC-004 at the base-model level). Added a `classification` entry to `whitelist.py`'s "Pydantic model fields read only via (de)serialization/rendering" section, since nothing in `src/` accesses `.classification` as a plain attribute yet (Phase 2's `set_classification` tool will add real usage, mirroring `set_status.py`'s `.status` access) -- without it, `vulture` flagged the new field as a false-positive unused variable. Ran the full quality gate: `ruff format --check` and `ruff check` are clean; `vulture src/ whitelist.py --min-confidence 60` is clean; the full `unittest` suite has 4 known failures (`tests/dec/resources/test_dec_schema.py`, `tests/feat/resources/test_feat_schema.py`, `tests/sop/resources/test_sop_schema.py`, `tests/vcr/resources/test_vcr_schema.py`), all comparing the packaged static schema JSON against a freshly generated schema that now includes `classification` -- this is the expected, Phase-4-owned consequence of the model change (Task 4.1 regenerates and commits these schemas) and was left unresolved here per this phase's explicit scope boundary (no `specmgr schema` run in Phase 1).

#### 2026-09-02 12:00:00.000Z — Feature drafted

Feature drafted from GitHub issue #56, covering the shared MarkdownFrontmatter classification field and a new generic set_classification tool; ADR's separate frontmatter model is explicitly out of scope. A related uc-prompts gap discovered during drafting was filed as a separate GitHub issue (#57) rather than folded into this feature's scope.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 12:00:00.000Z — Locked scope, API shape, and validation for classification

Three key decisions were made while drafting this feature: (1) the new `classification` field is added only to the shared `MarkdownFrontmatter` base used by the 11 whole-body domains -- ADR's separate `AdrFrontmatter` model is explicitly excluded; (2) rather than adding a `classification` parameter to each of the 11 `create_<d>` tools, a single new generic `set_classification(id, type, classification)` tool is added instead, mirroring the existing `set_status` tool's dispatch pattern, so it can be used both right after creation and for later changes; (3) `classification` stays fully free-text with blank/whitespace normalized to `None` -- no closed vocabulary or enum, per the source issue's explicit requirement.

### Related PRs / Commits

- [Issue #56](https://github.com/dfch/biz.dfch.SpecMgr/issues/56): source GitHub issue for this feature ("Classificatoin in frontmatter").

- [Issue #57](https://github.com/dfch/biz.dfch.SpecMgr/issues/57): related but separately-scoped gap discovered during drafting -- `uc` domain has no `create_uc`/`update_uc` prompts.
