---
classification: null
created: '2026-10-02T11:28:09.942+02:00'
id: feat-177-list-ref-feat
status: planning
type: feat
updated: '2026-10-02T12:15:59.212+02:00'
version: 1.0.0
---

# Feature: Resolve FEAT Cross-References in list_references

## Plan

### Overview

`list_references` scans a source document's body for `<TYPE> <uuid>` reference tags to build a resolved cross-reference list, but its scanner only matches UUID-shaped ids. `feat` is the one domain whose ids are `feat-NNN-slug` slugs (and may be cited by their unique `feat-NNN` number prefix), so any-domain -> FEAT references are silently missed (GitHub issue #177). This feature extends the shared reference scanner to recognize a FEAT tag carrying either a full feat id or a bare `feat-NNN` number, so FEAT references resolve to the referenced feature's title and on-disk path like every other reference type.

### Requirements

- REQ-001: `find_references` matches a FEAT tag followed by either the full feat id shape `feat-[0-9]+-[a-z0-9-]+` or the bare number form `feat-[0-9]+` (case-insensitive tag, space/tab/dash separator, matching anywhere in a line -- same semantics as the UUID tags); the FEAT id alternative carries a trailing guard in the same style as the UUID pattern's `(?![0-9a-f])` (a `(?![0-9a-z-])` lookahead) so an overlong or malformed tail such as `feat-177x` or `feat-177-` is not extracted as `feat-177`.
- REQ-002: the existing 10 reference tags keep matching UUID ids only -- zero behavior change by construction: the UUID pattern's tag group remains derived from a new `_UUID_REFERENCE_TYPES` constant (the existing 10 tags, same order), so `FEAT <uuid>`-shaped text still matches nothing (a feat's id is never a UUID).
- REQ-003: `resolve_reference` resolves a FEAT reference: a full-id-shape ref through feat's own cache-backed `load_by_id` (exact match), a bare `feat-[0-9]+$` ref through the first feature folder (lexicographically sorted folder-name order, the `iter_feat_paths`/`list_feat` order) whose name starts with `feat-NNN-` (the prefix includes the trailing hyphen, so `feat-1` never matches `feat-10-*`), and any other feat id shape (e.g. a UUID) through the exact `load_by_id`, yielding a not-found row naturally; the row's title is the referenced feature's H1 with the `Feature: ` prefix stripped (the existing `feature_title`).
- REQ-004: a FEAT reference whose target is absent on disk (no exact match for a full id, or no folder for a bare number) yields the same not-found row shape (title/path null, error message) as every other domain -- never raises.
- REQ-005: the `_references` module docstring (including the `find_references`/`resolve_reference` docstrings and the tag-vocabulary paragraphs), `REFERENCE_TYPES` (10 -> 11 tags) alongside the new `_UUID_REFERENCE_TYPES`, the `list_references` tool's module docstring, `@mcp.tool` description, and function docstring, the `ReferenceRow` model docstring (its `type`/`id` fields), the `general/tools/__init__.py` docstring, the `server.py` docstring's reference-tag vocabulary (10 -> 11 tags), the `AGENTS.md` tag enumeration, the auto-generated `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`), and a `CHANGELOG.md` `[Unreleased]` entry are updated.
- REQ-006: tests cover FEAT extraction (full and bare forms, case-insensitive tag, space/tab/dash separators, mid-line, merge ordering against the UUID pattern, non-matches including the `feat-177x`/`feat-177-` trailing-guard rejections and `FEAT <uuid>` still matching nothing), resolution (exact full id, bare number, `feat-1` never matching `feat-10-*`, not-found, multi-match -> first in sorted order, broken first-match README -> not-found row), and no-regression of the existing 10 tags (the existing suite passes with one pinned exception: the vocabulary-loop test special-cases `feat`).

### Acceptance Criteria

- [ ] ACC-001: the issue #177 repro as a test fixture -- a QA document whose body mentions `FEAT feat-1-frontend-technology-decision` (the feature folder seeded in a temp `SPECMGR_FEAT_DIR` -- the issue's original repro folder lives in the demo repo, not this one) -- returns that reference as a resolved row (title, path) from `list_references` instead of `total: 0`.
- [ ] ACC-002: a bare-number mention (`FEAT feat-177`) resolves to the matching `feat-177-*` feature as a resolved row (title, path).
- [ ] ACC-003: all references of the existing 10 UUID tags extract and resolve exactly as before, and `FEAT <uuid>`-shaped text still matches nothing; the existing test suite passes with exactly one pinned exception -- the vocabulary-loop test in `test__references.py` special-cases `feat` (its UUID form is not a feat reference), with a separate FEAT-form loop added.
- [ ] ACC-004: a FEAT reference (full or bare) pointing at an absent feature yields a row with null title/path and a not-found error -- no exception.
- [ ] ACC-005: when a bare number matches multiple feature folders, the first one in lexicographically sorted folder-name order (the `list_feat` order) resolves (pinned by a test).
- [ ] ACC-006: the module-scope drift guard (`set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES)`) still holds with `feat` in both.
- [ ] ACC-007: the full quality gate is green (ruff format/check, vulture, pylint, pytest -n auto, and the `specmgr docs` + `specmgr mcp-docs` regenerations leave no uncommitted drift).

### Scope

#### Included

- The shared scanner in `general/tools/_references.py` (the new `_UUID_REFERENCE_TYPES` constant, `REFERENCE_TYPES` rebuilt as the 11-tag vocabulary, a second compiled FEAT pattern with trailing guard, a `_load_feat` resolver, the merge by match position, module/function docstrings, the drift guard).
- feat's existing `_io`/`_paths` integration reused (cache-backed `load_by_id`, `feature_title`, `iter_feat_paths`'s sorted order) -- no new feat tooling.
- Doc updates: `_references` docstrings, `list_references` (module docstring + `@mcp.tool` description + function docstring), `reference.py` (`ReferenceRow` model docstring), `general/tools/__init__.py` docstring, `server.py` docstring, `AGENTS.md` tag enumeration, `docs/MCP.md` + `docs/api/` + `docs/GENERATED.md` regeneration, `CHANGELOG.md` `[Unreleased]` entry.
- Unit + integration tests.

#### Explicitly Out Of Scope

- Adding `SOP` or `TSK` reference tags (still explicitly deferred, per the module docstring).
- Changing the SYSRS/VCR structured reference patterns (their type-tagged H3 lists deliberately do not accept FEAT).
- `find_related`/`find_similar_text`.
- The feat document schema itself.
- Generalizing per-tag id shapes to all 11 tags (issue #177's alternative suggestion) -- a minimal FEAT-scoped change instead.

### Dependencies

#### Depends On

- `feat-144-ref-artifact` (the `list_references` tool and the `_references` scanner this feature extends -- shipped).

#### Blocks

- None known.

### Design Notes

- The existing 10-tag UUID pattern stays byte-unchanged: its tag group remains derived from a new `_UUID_REFERENCE_TYPES` constant (the existing 10 tags, same order); `REFERENCE_TYPES` becomes `_UUID_REFERENCE_TYPES + ("feat",)` -- still the 11-tag vocabulary for the module-scope drift guard and the `ReferenceRow.type` contract -- and the second compiled FEAT pattern carries its own literal `FEAT` tag plus the id alternative `feat-[0-9]+(?:-[a-z0-9-]+)?` with a trailing `(?![0-9a-z-])` guard (the same style as the UUID pattern's `(?![0-9a-f])`, so `feat-177x` is not extracted as `feat-177`). A feat's id is never a UUID, so `FEAT <uuid>`-shaped text matches nothing under either pattern; the existing `FEAT <uuid>` -> `[]` subtest of `test_tags_outside_the_vocabulary_do_not_match` keeps passing unchanged and becomes the regression pin for this. Both `finditer` result sets are merged by stable sort on `(start, end)` -- the match spans are provably disjoint (a UUID cannot contain `t`; a feat id cannot be a UUID), so no overlap handling is needed.
- The full-id shape is sourced from the same constant as `general/tools/_path_safety._FEAT_ID_PATTERN` (private import with alias -- the established convention, cf. `set_status.py`'s own `_ALLOWED_STATUSES` import) so the two cannot drift; the anchored form doubles as the resolver's full/bare classifier.
- Bare-number resolution filters the feat base dir by folder-name prefix `feat-NNN-` WITHOUT parsing any document (the prefix includes the trailing hyphen, so `feat-1` never matches `feat-10-*`), then loads the first match in lexicographically sorted folder-name order (the `iter_feat_paths`/`list_feat` order) through feat's cache-backed `load_by_id` (0 matches -> not-found row; the NNN-is-a-unique-GitHub-issue-number convention means multi-match should not occur -- if it does, first in sorted order wins silently). If the first name match's README fails to parse, the collapsed `FeatNotFoundError` yields a not-found row -- the resolver does not skip on to the next match.
- The row's title is the feature's H1 via the existing `feat/tools/_paths.feature_title` helper (strips the `Feature: ` prefix).
- The accepted v1 caveat (the scanner matches inside fenced code / inline code spans too) now applies to FEAT tags as well.

### Related Decisions

- `feat-144-ref-artifact`: the original `list_references` design; its `_references` module docstring assumption that feat can never be a reference tag is what this feature revises.
- GitHub issue #177: the finding, repro, and suggested fix this feature implements.

### Task List

#### Phase 100: Scanner and Resolver

- [ ] Task 100.100: Add `_UUID_REFERENCE_TYPES` (the existing 10 tags, same order) in `general/tools/_references.py`, rebuild `REFERENCE_TYPES` as `_UUID_REFERENCE_TYPES + ("feat",)`, add the second compiled FEAT reference pattern (literal `FEAT` tag + `feat-[0-9]+(?:-[a-z0-9-]+)?` + trailing `(?![0-9a-z-])` guard, sharing the full-id shape with `general/tools/_path_safety._FEAT_ID_PATTERN` via a private import with alias), and extend `find_references` to merge both `finditer` result sets by stable sort on `(start, end)` -- the UUID pattern stays byte-unchanged.
- [ ] Task 100.110: Add a `_load_feat` resolver (full-id shape -> exact `load_by_id`; bare `feat-[0-9]+$` -> first in sorted order matching the `feat-NNN-` prefix, name-only filter; any other shape -> exact `load_by_id` -> not-found row; title via `feature_title`) and register it in `_TARGET_RESOLVERS`.
- [ ] Task 100.120: Update the `_references` module docstring (the "feat can never be one" statement, the tag-vocabulary paragraph, and the UUID-only id wording in the `find_references`/`resolve_reference` docstrings) and the drift-guard assertion message.

#### Phase 110: Tests

- [ ] Task 110.100: `find_references` unit tests for FEAT extraction (case-insensitive tag, space/tab/dash separators, full vs bare id shape, mid-line, merge ordering against the UUID pattern, non-matches: `feat-177x`, `feat-177-`, `FEAT <uuid>` still matching nothing, SOP/TSK still matching nothing); update the existing vocabulary-loop test to special-case `feat` (its UUID form does not match) and add a separate FEAT-form loop.
- [ ] Task 110.110: `resolve_reference` tests for FEAT rows (exact full-id row, bare-number row, `feat-1` never matching `feat-10-*`, not-found row, multi-match -> first in sorted order, broken first-match README -> not-found row, UUID-shaped feat id -> not-found row); seed the feature folders via `create_feat(..., id=...)` in the existing `TempRefDirTestCase` `SPECMGR_FEAT_DIR` fixture.
- [ ] Task 110.120: `list_references` integration test reproducing issue #177 as a temp-dir fixture (QA -> FEAT, full id and bare number).
- [ ] Task 110.130: Regression check that the existing 10 tags are unchanged (existing test suite passes, modulo the pinned vocabulary-loop update).

#### Phase 120: Documentation and Gates

- [ ] Task 120.100: Update the `list_references` tool's module docstring, `@mcp.tool` description (incl. the in-passing "space or dash" -> "space/tab/dash" fix), and function docstring, the `ReferenceRow` model docstring (its `type`/`id` fields), the `general/tools/__init__.py` docstring, the `server.py` docstring's reference-tag vocabulary (10 -> 11 tags incl. FEAT), and the `AGENTS.md` tag enumeration.
- [ ] Task 120.110: Regenerate `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`).
- [ ] Task 120.120: Add a `CHANGELOG.md` `[Unreleased]` entry (`### Changed`: the `list_references` tag vocabulary gains FEAT -- a FEAT tag references a feat's full `feat-NNN-slug` id or bare `feat-NNN` number, resolved to the feature's title/path).
- [ ] Task 120.130: Run the full quality gate (ruff format/check, vulture, pylint, pytest -n auto, `specmgr docs` + `specmgr mcp-docs` no-drift).

## Progress

### Current Status

**As of 2026-10-02**: Planning: feature drafted from GitHub issue #177, refined after a code-level review; no implementation started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-02T10:15:59.000Z - Refined after review

Reviewed the plan against the code (`_references.py`, `_path_safety.py`, `list_references.py`, `reference.py`, the existing test suite) and GitHub issue #177's wording; refined: (1) resolved the self-contradiction between "keep the UUID pattern untouched" and "add feat to REFERENCE_TYPES" -- the UUID pattern's tag group now stays derived from a new `_UUID_REFERENCE_TYPES` (the existing 10 tags), so `FEAT <uuid>`-shaped text still matches nothing (a feat's id is never a UUID) and `REFERENCE_TYPES` remains the 11-tag vocabulary for the drift guard; (2) added a trailing `(?![0-9a-z-])` guard to the FEAT id alternative (so `feat-177x` is not extracted as `feat-177`, matching the UUID pattern's guard style); (3) pinned the `resolve_reference` fallback for a feat id shape that is neither full nor bare (exact `load_by_id` -> not-found row); (4) replaced the non-deterministic "directory order" with lexicographically sorted folder-name order (the `iter_feat_paths`/`list_feat` order) and pinned the `feat-NNN-` prefix's trailing hyphen (`feat-1` never matches `feat-10-*`); (5) expanded the doc-update scope to the `list_references` tool's module/`@mcp.tool`/function docstrings, the `ReferenceRow` model docstring, the `general/tools/__init__.py` docstring, `docs/api/` regeneration (`specmgr docs`), and a `CHANGELOG.md` `[Unreleased]` entry; (6) reworded ACC-001 as a temp-dir fixture (the issue's original repro folder lives in the demo repo, not this one) and corrected ACC-003 (one pinned test exception: the vocabulary-loop test special-cases `feat`).

#### 2026-10-02T09:24:57.000Z - Created

Feature drafted from GitHub issue #177: `list_references` does not resolve FEAT (slug-style id) cross-references. Design settled as a FEAT-scoped second scanner pattern (full id or bare `feat-NNN` number) plus a `_load_feat` resolver; multi-match bare numbers resolve first in directory order. No implementation started.

### More Information

GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/177 (finding, reproduction steps, and suggested fix).
