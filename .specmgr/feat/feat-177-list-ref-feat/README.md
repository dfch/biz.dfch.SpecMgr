---
classification: null
created: '2026-10-02T11:28:09.942+02:00'
id: feat-177-list-ref-feat
status: planning
type: feat
updated: '2026-10-02T11:28:09.942+02:00'
version: 1.0.0
---

# Feature: Resolve FEAT Cross-References in list_references

## Plan

### Overview

`list_references` scans a source document's body for `<TYPE> <uuid>` reference tags to build a resolved cross-reference list, but its scanner only matches UUID-shaped ids. `feat` is the one domain whose ids are `feat-NNN-slug` slugs (and may be cited by their unique `feat-NNN` number prefix), so any-domain -> FEAT references are silently missed (GitHub issue #177). This feature extends the shared reference scanner to recognize a FEAT tag carrying either a full feat id or a bare `feat-NNN` number, so FEAT references resolve to the referenced feature's title and on-disk path like every other reference type.

### Requirements

- REQ-001: `find_references` matches a FEAT tag followed by either the full feat id shape `feat-[0-9]+-[a-z0-9-]+` or the bare number form `feat-[0-9]+` (case-insensitive tag, space/tab/dash separator, matching anywhere in a line -- same semantics as the UUID tags).
- REQ-002: the existing 10 reference tags keep matching UUID ids only -- zero behavior change for them.
- REQ-003: `resolve_reference` resolves a FEAT reference: a full id through feat's own cache-backed `load_by_id` (exact match), a bare number through the first feature folder (directory order) whose name starts with `feat-NNN-`; the row's title is the referenced feature's H1 with the `Feature: ` prefix stripped.
- REQ-004: a FEAT reference whose target is absent on disk (no exact match for a full id, or no folder for a bare number) yields the same not-found row shape (title/path null, error message) as every other domain -- never raises.
- REQ-005: the `_references` module docstring, the `server.py` docstring's reference-tag vocabulary (10 -> 11 tags), the `AGENTS.md` tag enumeration, and the auto-generated `docs/MCP.md` are updated.
- REQ-006: tests cover FEAT extraction (full and bare forms), resolution (exact, prefix, not-found, multi-match), and no-regression of the existing 10 tags.

### Acceptance Criteria

- [ ] ACC-001: the issue #177 repro -- a QA document whose body mentions `FEAT feat-1-frontend-technology-decision` -- returns that reference as a resolved row (title, path) from `list_references` instead of `total: 0`.
- [ ] ACC-002: a bare-number mention (`FEAT feat-177`) resolves to the matching `feat-177-*` feature as a resolved row (title, path).
- [ ] ACC-003: all references of the existing 10 UUID tags extract and resolve exactly as before (existing tests pass unchanged).
- [ ] ACC-004: a FEAT reference (full or bare) pointing at an absent feature yields a row with null title/path and a not-found error -- no exception.
- [ ] ACC-005: when a bare number matches multiple feature folders, the first one in directory order resolves (pinned by a test).
- [ ] ACC-006: the module-scope drift guard (`set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES)`) still holds with `feat` in both.
- [ ] ACC-007: the full quality gate is green (ruff format/check, vulture, pytest -n auto, pylint).

### Scope

#### Included

- The shared scanner in `general/tools/_references.py` (a second compiled FEAT pattern, `REFERENCE_TYPES`, a `_load_feat` resolver, drift guard, module docstring).
- feat's existing `_io`/`_paths` integration reused (cache-backed `load_by_id`, `feature_title`) -- no new feat tooling.
- Doc updates: `_references` module docstring, `server.py` docstring, `AGENTS.md` tag enumeration, `docs/MCP.md` regeneration.
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

- Keep the existing 10-tag UUID pattern untouched and add a second compiled FEAT pattern, merging both `finditer` result sets by match position -- the existing tags have zero behavior change by construction (REQ-002).
- The FEAT id alternative is `feat-[0-9]+(?:-[a-z0-9-]+)?` (bare number OR full slug); the full-id shape is sourced from the same constant as `general/tools/_path_safety._FEAT_ID_PATTERN` so the two cannot drift.
- Bare-number resolution filters the feat base dir by folder-name prefix `feat-NNN-` WITHOUT parsing any document, then loads the first match in directory order through feat's cache-backed `load_by_id` (0 matches -> not-found row; the NNN-is-a-unique-GitHub-issue-number convention means multi-match should not occur -- if it does, first in dir order wins silently).
- The row's title is the feature's H1 via the existing `feat/tools/_paths.feature_title` helper (strips the `Feature: ` prefix).
- The accepted v1 caveat (the scanner matches inside fenced code / inline code spans too) now applies to FEAT tags as well.

### Related Decisions

- `feat-144-ref-artifact`: the original `list_references` design; its `_references` module docstring assumption that feat can never be a reference tag is what this feature revises.
- GitHub issue #177: the finding, repro, and suggested fix this feature implements.

### Task List

#### Phase 100: Scanner and Resolver

- [ ] Task 100.100: Add the second compiled FEAT reference pattern (`FEAT` tag + `feat-[0-9]+(?:-[a-z0-9-]+)?`) in `general/tools/_references.py`, sharing the full-id shape constant with `general/tools/_path_safety._FEAT_ID_PATTERN`; extend `find_references` to merge both result sets by match position.
- [ ] Task 100.110: Add `"feat"` to `REFERENCE_TYPES` and a `_load_feat` resolver (full id -> exact `load_by_id`; bare number -> first in directory order matching the `feat-NNN-` prefix, name-only filter; title via `feature_title`).
- [ ] Task 100.120: Update the `_references` module docstring (the "feat can never be one" statement and the tag-vocabulary paragraph) and the drift-guard assertion message.

#### Phase 110: Tests

- [ ] Task 110.100: `find_references` unit tests for FEAT extraction (case-insensitive tag, space/tab/dash separators, full vs bare id shape, non-matches, merge ordering against the UUID pattern).
- [ ] Task 110.110: `resolve_reference` tests for FEAT rows (exact full-id row, bare-number row, not-found row, multi-match -> first in dir order).
- [ ] Task 110.120: `list_references` integration test reproducing issue #177 (QA -> FEAT, full id and bare number).
- [ ] Task 110.130: Regression check that the existing 10 tags are unchanged (existing test suite passes).

#### Phase 120: Documentation and Gates

- [ ] Task 120.100: Update the `server.py` docstring's reference-tag vocabulary (10 -> 11 tags incl. FEAT) and the `AGENTS.md` tag enumeration.
- [ ] Task 120.110: Regenerate `docs/MCP.md` (`specmgr mcp-docs`).
- [ ] Task 120.120: Run the full quality gate (ruff format/check, vulture, pytest -n auto, pylint).

## Progress

### Current Status

**As of 2026-10-02**: Planning: feature drafted from GitHub issue #177; no implementation started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-02T09:24:57.000Z - Created

Feature drafted from GitHub issue #177: `list_references` does not resolve FEAT (slug-style id) cross-references. Design settled as a FEAT-scoped second scanner pattern (full id or bare `feat-NNN` number) plus a `_load_feat` resolver; multi-match bare numbers resolve first in directory order. No implementation started.

### More Information

GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/177 (finding, reproduction steps, and suggested fix).
