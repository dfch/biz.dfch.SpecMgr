---
created: '2026-09-02 09:50:23.991Z'
id: feat-56-classification-attribute-in-frontmatter
status: done
type: feat
updated: '2026-10-07T06:21:40.943Z'
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

- [x] ACC-001: A document created via any of the 11 `create_<d>` tools, then read back via `get_<d>` or `parse_<d>`, has `classification` == `None` when never set.

- [x] ACC-002: Calling `set_classification(id, type, "Confidential")` on an existing document, then reading it back, shows `classification: Confidential` in frontmatter and an updated `updated` timestamp; the body is byte-identical; the reconstruction is wrapped in `wrap_tool_errors`/`FRONTMATTER_CHANNEL` exactly like every `set_status.py` adapter.

- [x] ACC-003: Calling `set_classification(id, type, "")` (or whitespace) clears classification back to `None`/absent in the rendered YAML.

- [x] ACC-004: A pre-existing on-disk document (authored before this feature, no `classification` key) still parses successfully via `parse_<d>`/`get_<d>` with no validation error.

- [x] ACC-005: `set_classification(id, type="bogus", ...)` raises the same class of error the generic `set_status` tool raises for an unsupported type, following the same `set_status.py`-mirrored dispatch/guard structure.

- [x] ACC-006: `uv run --frozen specmgr schema` regenerates all 11 affected domain schemas with the new field and no unrelated diff; `uv run --frozen specmgr docs` regenerates docs/GENERATED.md and docs/api/ cleanly.

- [x] ACC-007: Full test suite (`uv run --frozen python -m unittest discover ...`) passes, including new unit tests for the field and the new tool across all 11 domains.

- [x] ACC-008: Each of the 10 domains' create instructions mentions optionally calling `set_classification` after creation, and each domain's update instructions gains a "change to `classification`" mapping bullet pointing at `set_classification(id, type="<d>", classification)`, matching the existing `status`/`set_status` pattern.

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

#### Phase 100: Model change

- [x] Task 100.100: Add `classification: str | None = None` field + blank-to-None validator to `MarkdownFrontmatter` (models/md/frontmatter.py), reusing `blank_to_none`.

- [x] Task 100.110: Add/update unit tests for the base frontmatter model covering classification parse, round-trip, and blank/whitespace-to-None.

- [x] Task 100.120: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) and fix any regressions before moving on.

#### Phase 110: Generic set_classification tool

- [x] Task 110.100: Implement `general/tools/set_classification.py` mirroring `set_status.py`'s structure (11 adapters, `_path_safety` guards, `wrap_tool_errors`/`FRONTMATTER_CHANNEL`).

- [x] Task 110.110: Register the new tool's import in server.py and update its module docstring.

- [x] Task 110.120: Add unit tests for `set_classification` across all 11 domains (set, clear via blank, invalid type error, path-safety rejection).

- [x] Task 110.130: Run the full test suite and fix any regressions before moving on.

#### Phase 120: Prompt instructions

- [x] Task 120.100: Update the 10 whole-body domains' (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) `<d>_create_instructions.md` files to mention `set_classification` in the "Later revisions" step.

- [x] Task 120.110: Update the same 10 domains' `<d>_update_instructions.md` files with a "change to `classification`" mapping bullet, matching the existing `status`/`set_status` bullet.

- [x] Task 120.120: Run the full test suite and fix any regressions before moving on.

#### Phase 130: Docs and schema regeneration

- [x] Task 130.100: Run `uv run --frozen specmgr schema` and commit the regenerated JSON Schemas for all 11 affected domains.

- [x] Task 130.110: Run `uv run --frozen specmgr docs` and commit the regenerated docs/GENERATED.md + docs/api/.

- [x] Task 130.120: Update AGENTS.md's per-domain bullets / general/ bullet to mention `set_classification` alongside `set_status`/`update`/`delete`.

- [x] Task 130.130: Run the full test suite and fix any regressions before moving on.

#### Phase 140: Verification

- [x] Task 140.100: Run the full test suite, `ruff format --check`, `ruff check`, and `vulture`; fix any regressions.

- [x] Task 140.110: Manually verify a pre-existing on-disk document (no classification key) still parses via `parse_<d>`/`get_<d>`.

## Progress

### Current Status

**As of 2026-09-02**: **Feature complete.** All five phases -- 1 (Model change), 2 (Generic
`set_classification` tool), 3 (Prompt instructions), 4 (Docs and schema regeneration), and 5
(Verification) -- are done, and all eight Acceptance Criteria (ACC-001 through ACC-008) are
confirmed met against the current state of the repo. Phase 5's re-run of the full quality gate
(`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the
full `unittest` suite) is clean end to end, with the suite at **3029 tests, 0 failures**. A
disk-free-script-based ACC-004 end-to-end re-check (a hand-crafted, no-`classification`-key REQ
markdown file parsed directly via `req.tools.parse_req.parse_req`) confirmed the whole pipeline,
not just the Pydantic model, still parses a pre-existing document successfully with
`frontmatter.classification is None`. `specmgr schema` and `specmgr docs` (plus `specmgr adr-toc`)
were re-run and produced zero diff, confirming Phase 4's regeneration was already idempotent and
complete. No code changes were needed in this phase -- Phase 5 was a clean pass-through, exactly
as expected given Phases 1-4 already left the suite green.

The shared `MarkdownFrontmatter` model has an optional, free-text `classification: str | None = None` field that normalizes blank/whitespace-only input to `None`, inherited by all eleven whole-body domain frontmatter classes. The new generic `set_classification(id, type, classification)` tool in `general/tools/` dispatches to one adapter per whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr -- `adr` deliberately excluded), each shaped exactly like `set_status.py`'s corresponding adapter (same domain lock, `load_by_id`, `_path_safety.assert_within` guard, raw-body re-read/re-persistence, `wrap_tool_errors`/`FRONTMATTER_CHANNEL`-wrapped `XFrontmatter` reconstruction) but replacing `classification` instead of `status`, with no `superseded_by`-style parameter. It is registered in `server.py`'s module docstring and `general/tools/__init__.py`. New unit tests (`tests/general/tools/test_set_classification.py`) cover setting a value (ACC-002), clearing via blank/whitespace (ACC-003), an unsupported `type="bogus"` raising `ValueError` matching `set_status`'s own behavior for the same misuse (ACC-005), `type="adr"` raising `KeyError` (matching the generic `update` tool's own real, if undocumented, behavior for a UUID-shaped-but-out-of-dispatch type), per-domain not-found errors, and `_path_safety` injection/wrong-format-id rejection. All 10 whole-body domains' (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) packaged `<d>_create_instructions.md`/`<d>_update_instructions.md` prompt files now reference `set_classification` alongside the existing `set_status` mentions (ACC-008); `uc` and `adr` remain untouched by design. All 11 affected domains' JSON Schemas (`docs/<d>_schema.json` and each domain's packaged `src/biz/dfch/specmgr/<d>/data/<d>_schema.json`) have been regenerated via `specmgr schema` and now include `classification` (ACC-006); `docs/GENERATED.md`/`docs/api/` have been regenerated via `specmgr docs` (including a new `docs/api/biz.dfch.specmgr.general.tools.set_classification.md`); `AGENTS.md`'s per-domain bullets and the cross-cutting `general/` bullet now mention `set_classification` alongside `set_status`/`update`/`delete`. The 4 previously-expected schema-drift failures in `tests/{dec,feat,sop,vcr}/resources/test_*_schema.py` are now resolved -- the full test suite (3029 tests) is 100% green (ACC-007). `ruff format --check`, `ruff check`, and `vulture` are clean, and both `specmgr schema` and `specmgr docs` were confirmed idempotent by a second run after the `AGENTS.md` edit producing no further diff. Only Phase 5 (Verification) remains.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 22:15:00.000Z - Phase 5 (Verification) complete -- feature done
Ran the full Task 5.1 quality gate exactly as specified: `uv run --frozen ruff format --check`
(1517 files already formatted, clean), `uv run --frozen ruff check` ("All checks passed!"),
`uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no output, clean), and
`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (**3029 tests, 0
failures**, `OK`). No regressions found -- nothing needed fixing, so no `src/`/`tests/` files
were touched by this phase.
For Task 5.2 (ACC-004 end-to-end), wrote a throwaway script under `/tmp/opencode/` (never inside
the git worktree) that hand-crafted a minimal, valid REQ markdown file with a pre-feat-56-style
frontmatter block -- `id`/`type`/`status`/`created`/`updated`/`version` only, no `classification`
key at all -- and called `biz.dfch.specmgr.req.tools.parse_req.parse_req` directly on that file's
path. Result: `parse_req` raised no exception, and
`document.frontmatter.classification is None`, printed as a clear PASS. This proves the whole
parse pipeline (frontmatter YAML load -> `ReqFrontmatter` validation -> `ReqDocument` assembly),
not just the base Pydantic model exercised by Phase 1's unit tests, still accepts documents
written before this feature existed. The script and its log output were deleted afterward; `git
status --porcelain` before and after this phase shows no diff outside this README.
Re-read all eight Acceptance Criteria one by one against the current codebase (not just re-running
existing tests) and confirmed each is genuinely met:
**ACC-001**: confirmed via `tests/models/md/test_frontmatter.py`'s
  `test_classification_defaults_to_none` (base-model level) and the natural absence of any
  `classification` argument on any `create_<d>` tool (grepped signatures) -- a freshly created
  document never gets a `classification` key, so parsing it back always yields `None`.
**ACC-002**: grepped `general/tools/set_classification.py` directly (not just trusted the test)
  and found `wrap_tool_errors(domain="<d>", tool="set_classification", channel=FRONTMATTER_CHANNEL)`
  wrapping the frontmatter reconstruction call for all 11 dispatch adapters
  (req/uc/tsk/qa/prb/gol/rsk/dec/feat/sop/vcr); `tests/general/tools/test_set_classification.py`'s
  `test_sets_classification_bumps_updated_leaves_body_untouched` confirms the value, the `updated`
  bump, and byte-identical body.
**ACC-003**: `test_blank_classification_clears_back_to_none` (both the returned model and the
  on-disk YAML) plus the base-model `test_classification_blank_normalizes_to_none`/
  `test_classification_whitespace_only_normalizes_to_none` tests, spot-checked and green.
**ACC-004**: this phase's Task 5.2 e2e script (see above) -- PASS.
**ACC-005**: `test_unsupported_type_raises_value_error` and
  `test_unsupported_type_matches_set_status_error_class` (asserts the exact same exception class
  as `set_status`'s own `type="bogus"` misuse) both green; `test_adr_type_is_not_supported` pins
  the documented `KeyError`-for-`type="adr"` precedent from the Decisions Made log.
**ACC-006**: re-ran `uv run --frozen specmgr schema --type <d> --output-dir
  src/biz/dfch/specmgr/<d>/data` for all 11 domains plus a plain `uv run --frozen specmgr schema`,
  then `uv run --frozen specmgr docs` and `uv run --frozen specmgr adr-toc` -- `git status
  --porcelain` showed **zero diff** after every one of these regenerations, confirming Phase 4's
  output was already complete and idempotent.
**ACC-007**: Task 5.1's run (3029 tests, 0 failures) confirms this; counted the dispatch table in
  `tests/general/tools/test_set_classification.py` (`_CASES`, lines ~389-399) and confirmed all 11
  whole-body domains (req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/feat) are represented.
**ACC-008**: grepped all 20 packaged instruction files under
  `src/biz/dfch/specmgr/{req,tsk,qa,prb,gol,rsk,dec,sop,feat,vcr}/data/*_{create,update}_instructions.md`
  for `set_classification` -- every one of the 20 files has at least one match (`sop`'s
  create-instructions file has two, matching its extended "no per-domain mutation tools" sentence
  from Phase 3).
No code changes were required in this phase; Phase 5 was verification-only, exactly as the plan
anticipated. The feature is now complete end to end.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 18:30:00.000Z - type="adr" surfaces as KeyError, not ValueError
While implementing Task 2.1, discovered that `_path_safety.validate_id` treats `adr` as one of its known UUID-shaped types (it is in `_UUID_TYPES` for use by `get_<d>`/`update`/`set_status`), so a well-formed UUID id with `type="adr"` passes `validate_id` even though `set_classification`'s own dispatch table has no `"adr"` entry -- the rejection then surfaces as a `KeyError` from the `_ADAPTERS[type]` lookup itself, not a `ValueError`. Verified this is not a bug introduced here but the same pre-existing, real (if undocumented) behavior the generic `update` tool already has for `type="adr"` (`update` also excludes `adr` from its own dispatch table for the same reason -- ADR's section-level mutation contract has no whole-body replace). Rather than adding special-case `adr` rejection logic to `set_classification` that `update` itself does not have, `set_classification` was left to inherit the identical `KeyError` behavior for `type="adr"`, with a test (`test_adr_type_is_not_supported`) pinning and documenting this precedent instead of asserting a `ValueError` that would diverge from `update`'s own established pattern.
#### 2026-09-02 12:00:00.000Z - Locked scope, API shape, and validation for classification
Three key decisions were made while drafting this feature: (1) the new `classification` field is added only to the shared `MarkdownFrontmatter` base used by the 11 whole-body domains -- ADR's separate `AdrFrontmatter` model is explicitly excluded; (2) rather than adding a `classification` parameter to each of the 11 `create_<d>` tools, a single new generic `set_classification(id, type, classification)` tool is added instead, mirroring the existing `set_status` tool's dispatch pattern, so it can be used both right after creation and for later changes; (3) `classification` stays fully free-text with blank/whitespace normalized to `None` -- no closed vocabulary or enum, per the source issue's explicit requirement.
### Related PRs / Commits

- [Issue #56](https://github.com/dfch/biz.dfch.SpecMgr/issues/56): source GitHub issue for this feature ("Classificatoin in frontmatter").

- [Issue #57](https://github.com/dfch/biz.dfch.SpecMgr/issues/57): related but separately-scoped gap discovered during drafting -- `uc` domain has no `create_uc`/`update_uc` prompts.
