---
classification: null
created: '2026-10-02T11:28:09.942+02:00'
id: feat-177-list-ref-feat
status: done
type: feat
updated: '2026-10-10T09:51:46.495+02:00'
version: 1.0.0
---

# Feature: Resolve FEAT Cross-References in list_references

## Plan

### Overview

`list_references` scans a source document's body for `<TYPE> <uuid>` reference tags to build a resolved cross-reference list, but its scanner only matches UUID-shaped ids. `feat` is the one domain whose ids are `feat-NNN-slug` slugs (and may be cited by their `feat-NNN` number prefix -- unique for an assigned issue number, except the sanctioned `feat-0-*` pre-issue folders), so any-domain -> FEAT references are silently missed (GitHub issue #177). This feature extends the shared reference scanner to recognize a FEAT tag carrying either a full feat id or a bare `feat-NNN` number, so FEAT references resolve to the referenced feature's title and on-disk path like every other reference type.

### Requirements

- REQ-001: `find_references` matches a FEAT tag followed by either the full feat id shape `feat-[0-9]+-[a-z0-9-]+` or the bare number form `feat-[0-9]+` (case-insensitive tag, space/tab/dash separator, matching anywhere in a line -- same semantics as the UUID tags); the FEAT id alternative carries a trailing guard in the same style as the UUID pattern's `(?![0-9a-f])` (a `(?![0-9a-z-])` lookahead) so an overlong or malformed tail such as `feat-177x` or `feat-177-` is not extracted as `feat-177`.
- REQ-002: the existing 10 reference tags keep matching UUID ids only -- zero behavior change by construction: the UUID pattern's tag group remains derived from a new `_UUID_REFERENCE_TYPES` constant (the existing 10 tags, same order), so `FEAT <uuid>`-shaped text still matches nothing (a feat's id is never a UUID).
- REQ-003: `resolve_reference` resolves a FEAT reference: a full-id-shape ref through feat's own cache-backed `load_by_id` (exact match), a bare `feat-[0-9]+$` ref through the first feature folder (lexicographically sorted folder-name order, the `iter_feat_paths`/`list_feat` order) whose name starts with `feat-NNN-` (the prefix includes the trailing hyphen, so `feat-1` never matches `feat-10-*`), with the candidate set limited to `README.md`-backed folders (the `iter_feat_paths` view -- a `feat-NNN-*` folder without a README is not a candidate), and any other feat id shape (e.g. a UUID) through the exact `load_by_id`, yielding a not-found row naturally; the row's title is the referenced feature's H1 with the `Feature: ` prefix stripped (the existing `feature_title`), and the row's `id` is the reference id as it appeared in the source body (the bare `feat-NNN` for a bare mention -- not the resolved full id).
- REQ-004: a FEAT reference whose target is absent on disk (no exact match for a full id, or no folder for a bare number) yields the same not-found row shape (title/path null, error message) as every other domain -- never raises.
- REQ-005: the `_references` module docstring (its first bullet's `:data:`_REFERENCE_PATTERN`` reference, the `find_references`/`resolve_reference` docstrings, the `_REFERENCE_PATTERN` constant docstring's tag-group derivation, the tag-vocabulary paragraphs, and the `_TARGET_RESOLVERS` comment's "nine flat target domains" wording), `REFERENCE_TYPES` (10 -> 11 tags) alongside the new `_UUID_REFERENCE_TYPES`, the `list_references` tool's module docstring, `@mcp.tool` description, and function docstring (incl. its own "nine flat target domains" wording), the `reference.py` module docstring and the `ReferenceRow` model docstring (its `type`/`id` fields), the `general/tools/__init__.py` docstring, the `server.py` docstring's reference-tag vocabulary (10 -> 11 tags), the `AGENTS.md` tag enumeration (incl. the same "space or dash" -> "space/tab/dash" separator fix), the root `README.md`'s "Referencing Artifacts" section (whose "free-form or non-uuid references are ignored" statement becomes false), the auto-generated `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`), and a `CHANGELOG.md` `[Unreleased]` entry are updated.
- REQ-006: tests cover FEAT extraction (full and bare forms, case-insensitive tag, space/tab/dash separators, mid-line, merge ordering against the UUID pattern, non-matches including the `feat-177x`/`feat-177-` trailing-guard rejections and `FEAT <uuid>` still matching nothing), resolution (exact full id, bare number, `feat-1` never matching `feat-10-*`, not-found, multi-match -> first in sorted order, broken first-match README -> not-found row), and no-regression of the existing 10 tags (the existing suite passes with one pinned exception: the vocabulary-loop test special-cases `feat`).
- REQ-007: the same feature cited in both spellings (a bare `FEAT feat-177` and the full `FEAT feat-177-list-ref-feat` in one body) yields two rows -- one per unique `(type, id)` pair, both resolved to the same title/path -- with no spelling normalization between the bare and full forms.

### Acceptance Criteria

- [ ] ACC-001: the issue #177 repro as a test fixture -- a QA document whose body carries a `FEAT`-tagged reference to the fixture feature `feat-1-frontend-technology-decision` (the feature folder seeded in a temp `SPECMGR_FEAT_DIR` -- the issue's original repro folder lives in the demo repo, not this one) -- returns that reference as a resolved row (title, path) from `list_references` instead of `total: 0`.
- [ ] ACC-002: a bare-number mention (`FEAT feat-177`) resolves to the matching `feat-177-*` feature as a resolved row (title, path) whose `id` stays the bare `feat-177` as it appeared in the source body.
- [ ] ACC-003: all references of the existing 10 UUID tags extract and resolve exactly as before, and `FEAT <uuid>`-shaped text still matches nothing; the existing test suite passes with exactly one pinned exception -- the vocabulary-loop test in `test__references.py` special-cases `feat` (its UUID form is not a feat reference), with a separate FEAT-form loop added.
- [ ] ACC-004: a FEAT reference (full or bare) pointing at an absent feature yields a row with null title/path and a not-found error -- no exception.
- [ ] ACC-005: when a bare number matches multiple feature folders, the first one in lexicographically sorted folder-name order (the `list_feat` order) resolves, and a `feat-NNN-*` folder without a README is not a candidate (both pinned by tests).
- [ ] ACC-006: the module-scope drift guard (`set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES)`) still holds with `feat` in both.
- [ ] ACC-007: the full quality gate is green (ruff format/check, vulture, pylint, pytest -n auto, and the `specmgr docs` + `specmgr mcp-docs` regenerations leave no uncommitted drift).
- [ ] ACC-008: the same feature cited in both the bare and the full spelling yields two resolved rows (one per spelling, same title/path) -- no normalization (pinned by a test).

### Scope

#### Included

- The shared scanner in `general/tools/_references.py` (the new `_UUID_REFERENCE_TYPES` constant, `REFERENCE_TYPES` rebuilt as the 11-tag vocabulary, a second compiled FEAT pattern with trailing guard, a `_load_feat` resolver, the merge by match position, module/function docstrings, the drift guard).
- feat's existing `_io`/`_paths` integration reused (cache-backed `load_by_id`, `feature_title`, `iter_feat_paths`'s sorted order) -- no new feat tooling.
- Doc updates: `_references` docstrings (module, `_REFERENCE_PATTERN` constant, `_TARGET_RESOLVERS` comment), `list_references` (module docstring + `@mcp.tool` description + function docstring), `reference.py` (module docstring + `ReferenceRow` model docstring), `general/tools/__init__.py` docstring, `server.py` docstring, `AGENTS.md` tag enumeration, root `README.md` "Referencing Artifacts" section, `docs/MCP.md` + `docs/api/` + `docs/GENERATED.md` regeneration, `CHANGELOG.md` `[Unreleased]` entry.
- Unit + integration tests.

#### Explicitly Out Of Scope

- Adding `SOP` or `TSK` reference tags (still explicitly deferred, per the module docstring).
- Changing the SYSRS/VCR structured reference patterns (their type-tagged H3 lists deliberately do not accept FEAT).
- `find_related`/`find_similar_text`.
- The feat document schema itself.
- The `.opencode/command/refs.md`/`.opencode/agent/ref-finder.md` descriptions (their `<TYPE> <uuid>` cross-reference wording is cosmetically stale once FEAT resolves; `ref-finder` already documents feat's slug-id exception for its `id` parameter -- a one-line polish at most, no behavior).
- Generalizing per-tag id shapes to all 11 tags (issue #177's alternative suggestion) -- a minimal FEAT-scoped change instead.

### Dependencies

#### Depends On

- `feat-144-ref-artifact` (the `list_references` tool and the `_references` scanner this feature extends -- shipped).

#### Blocks

- None known.

### Design Notes

- The existing 10-tag UUID pattern stays byte-unchanged: its tag group remains derived from a new `_UUID_REFERENCE_TYPES` constant (the existing 10 tags, same order); `REFERENCE_TYPES` becomes `_UUID_REFERENCE_TYPES + ("feat",)` -- still the 11-tag vocabulary for the module-scope drift guard and the `ReferenceRow.type` contract -- and the second compiled FEAT pattern carries its own literal `FEAT` tag plus the id alternative `feat-[0-9]+(?:-[a-z0-9-]+)?` with a trailing `(?![0-9a-z-])` guard (the same style as the UUID pattern's `(?![0-9a-f])`, so `feat-177x` is not extracted as `feat-177`). A feat's id is never a UUID, so `FEAT <uuid>`-shaped text matches nothing under either pattern; the existing `FEAT <uuid>` -> `[]` subtest of `test_tags_outside_the_vocabulary_do_not_match` keeps passing unchanged and becomes the regression pin for this. Both `finditer` result sets are merged by stable sort on `(start, end)` -- the match spans are NOT provably disjoint: a FEAT match can never start inside a UUID span (a UUID cannot contain `t`), but a feat slug CAN embed a `<TAG>-<uuid>`-shaped substring (the hyphen doubling as the separator), in which case the merge keeps both spans -- the outer FEAT row plus the inner phantom UUID-tag row, which resolves like any other reference (typically a not-found row) -- pinned by a dedicated test (feat-177 review round).
- The full-id shape is sourced from the same constant as `general/tools/_path_safety._FEAT_ID_PATTERN` (private import with alias -- the established convention, cf. `set_status.py`'s own `_ALLOWED_STATUSES` import) so the two cannot drift; the anchored constant is the source of the derived shapes (the pattern's id alternative and the bare-number classifier), not the resolver's runtime classifier.
- Bare-number resolution filters the feat base dir by folder-name prefix `feat-NNN-` WITHOUT parsing any document (the prefix includes the trailing hyphen, so `feat-1` never matches `feat-10-*`), then loads the first match in lexicographically sorted folder-name order (the `iter_feat_paths`/`list_feat` order) through feat's cache-backed `load_by_id` (0 matches -> not-found row; multi-match is exceptional for an assigned issue number but legitimate for the sanctioned `feat-0-*` pre-issue folders -- first in sorted order wins silently). The candidate set is the `iter_feat_paths` view (folders backed by a `README.md` only), so a `feat-NNN-*` folder without a README is not a candidate and cannot shadow a later, valid match. If the first name match's README fails to parse, the collapsed `FeatNotFoundError` yields a not-found row -- the resolver does not skip on to the next match.
- The row's title is the feature's H1 via the existing `feat/tools/_paths.feature_title` helper (strips the `Feature: ` prefix); the row's `id` is the extracted reference id verbatim (lowercased) -- a bare mention stays bare, a full mention stays full (no normalization between spellings).
- The accepted v1 caveat (the scanner matches inside fenced code / inline code spans too) now applies to FEAT tags as well.

### Related Decisions

- `feat-144-ref-artifact`: the original `list_references` design; its `_references` module docstring assumption that feat can never be a reference tag is what this feature revises.
- GitHub issue #177: the finding, repro, and suggested fix this feature implements.

### Task List

#### Phase 100: Scanner and Resolver

- [x] Task 100.100: Add `_UUID_REFERENCE_TYPES` (the existing 10 tags, same order) in `general/tools/_references.py`, rebuild `REFERENCE_TYPES` as `_UUID_REFERENCE_TYPES + ("feat",)`, add the second compiled FEAT reference pattern (literal `FEAT` tag + `feat-[0-9]+(?:-[a-z0-9-]+)?` + trailing `(?![0-9a-z-])` guard, sharing the full-id shape with `general/tools/_path_safety._FEAT_ID_PATTERN` via a private import with alias), and extend `find_references` to merge both `finditer` result sets by stable sort on `(start, end)` -- the UUID pattern stays byte-unchanged.
- [x] Task 100.110: Add a `_load_feat` resolver (full-id shape -> exact `load_by_id`; bare `feat-[0-9]+$` -> first in sorted order matching the `feat-NNN-` prefix, name-only filter over the `iter_feat_paths` view (README-backed folders only); any other shape -> exact `load_by_id` -> not-found row; title via `feature_title`; the row's `id` is the extracted id verbatim) and register it in `_TARGET_RESOLVERS`.
- [x] Task 100.120: Update the `_references` module docstring (its first bullet's `:data:`_REFERENCE_PATTERN`` reference, the "feat can never be one" statement, the tag-vocabulary paragraph, the UUID-only id wording in the `find_references`/`resolve_reference` docstrings, and the `_TARGET_RESOLVERS` comment's "nine flat target domains" wording) and the `_REFERENCE_PATTERN` constant docstring (tag-group derivation -> `_UUID_REFERENCE_TYPES`); the drift-guard assertion stays as-is (its domain-agnostic message remains accurate -- no edit).

#### Phase 110: Tests

- [x] Task 110.100: `find_references` unit tests for FEAT extraction (case-insensitive tag, space/tab/dash separators, full vs bare id shape, mid-line, merge ordering against the UUID pattern, dual spelling -> two pairs, non-matches: `feat-177x`, `feat-177-`, `FEAT <uuid>` still matching nothing, SOP/TSK still matching nothing); update the existing vocabulary-loop test (its "10 vocabulary tags" docstring, special-casing `feat` since its UUID form does not match) and add a separate FEAT-form loop; reword `test_tags_outside_the_vocabulary_do_not_match`'s docstring and the `FEAT <uuid>` subtest's framing (FEAT is now in the vocabulary -- the subtest stays as the uuid-form regression pin, but is no longer a tag outside the vocabulary).
- [x] Task 110.110: `resolve_reference` tests for FEAT rows (exact full-id row, bare-number row with the bare `id` retained, `feat-1` never matching `feat-10-*`, not-found row, multi-match -> first in sorted order, broken first-match README -> not-found row, README-less `feat-NNN-*` folder not a candidate, UUID-shaped feat id -> not-found row); seed the feature folders via `create_feat(..., id=...)` in the existing `TempRefDirTestCase` `SPECMGR_FEAT_DIR` fixture (the broken-README and README-less-folder cases are written directly to the temp dir -- `create_feat` validates its input).
- [x] Task 110.120: `list_references` integration test reproducing issue #177 as a temp-dir fixture (QA -> FEAT, full id and bare number), plus the dual-spelling case (bare + full in one body -> two resolved rows, same title/path).
- [x] Task 110.130: Regression check that the existing 10 tags are unchanged (existing test suite passes, modulo the pinned vocabulary-loop update).

#### Phase 120: Documentation and Gates

- [x] Task 120.100: Update the `list_references` tool's module docstring, `@mcp.tool` description (incl. the in-passing "space or dash" -> "space/tab/dash" fix), and function docstring (incl. its "nine flat target domains" -> "ten"), the `reference.py` module docstring and the `ReferenceRow` model docstring (its `type`/`id` fields -- `id` is a canonical lowercase-hex UUID or, for `feat`, the full `feat-NNN-slug` id or the bare `feat-NNN` number as it appeared), the `general/tools/__init__.py` docstring, the `server.py` docstring's reference-tag vocabulary (10 -> 11 tags incl. FEAT), the `AGENTS.md` tag enumeration (incl. the same "space or dash" -> "space/tab/dash" fix), and the root `README.md`'s "Referencing Artifacts" section (its "free-form or non-uuid references are ignored" statement -> FEAT references carry feat's own id shapes and resolve like every other tag).
- [x] Task 120.110: Regenerate `docs/MCP.md` (`specmgr mcp-docs`) and `docs/api/` + `docs/GENERATED.md` (`specmgr docs`).
- [x] Task 120.120: Add a `CHANGELOG.md` `[Unreleased]` entry (`### Changed`: the `list_references` tag vocabulary gains FEAT -- a FEAT tag references a feat's full `feat-NNN-slug` id or bare `feat-NNN` number, resolved to the feature's title/path).
- [x] Task 120.130: Run the full quality gate (ruff format/check, vulture, pylint, pytest -n auto, `specmgr docs` + `specmgr mcp-docs` no-drift).

## Progress

### Current Status

**As of 2026-10-03**: Feature in review (PR #181 open against `dev`); the merge conflict with `dev` is RESOLVED -- `origin/dev` (`776c13d`) has been merged into the branch (everything auto-merged and staged except one content conflict), and the single `AGENTS.md` conflict (the `list_references` sentence in the `general/tools/` bullet) was resolved by taking dev's normalized text and re-applying feat-177's sentence (reference-tag vocabulary incl. FEAT, space/tab/dash separator, per-tag id shapes, no hardcoded counts) -- verified the diff against `origin/dev` is exactly that one sentence (3 lines removed, 5 added). Dev brought in feat-153 (`numbered=True` raw reads on every `get_<d>` tool, the generic `update` tool's new `UpdateResult` success return = `frontmatter` + `snippet`), a uv dependency bump, feat-plan README repairs across `.specmgr/feat/`, and the new ADR 19ff316b. The final read-only feat-reviewer verdict remains **ship** (no errors or functional gaps). Post-merge gate state: fully green (ruff format --check -- 1786 files already formatted, ruff check, vulture, pytest -n auto -- 4015 passed in 37.74s, 0 failed, and the `specmgr docs`/`specmgr mcp-docs` regenerations byte-identical to the auto-merged doc mirrors with a second `specmgr docs` run idempotent). The resolved merge landed as commit `242ce1d` and was pushed. The pre-merge post-review rounds (the four doc rounds) and the merge itself are recorded in the dated Updates entries below, with their own gate states. Since that entry, the final review's one optional, unpinned follow-up has landed (the FEAT resolver's branch coverage is now closed): a new `TestResolveReference` test pins feat's `load_by_id` frontmatter-id/folder-name mismatch guard (`feat/tools/_paths.py:331-336`) as a not-found row -- zero `src/` changes, full gate green (4016 passed), see the newest Updates entry.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T07:36:53.000Z - Deferred optional review follow-up landed: mismatched-frontmatter-id not-found branch pinned

The final read-only feat-review (verdict: ship) flagged exactly one OPTIONAL, unpinned gap: the third `FeatNotFoundError` branch of feat's `load_by_id` path (`feat/tools/_paths.py:331-336`) -- the folder exists AND its README parses fine, BUT the parsed frontmatter `id` does not match the containing folder's own name -- had no test pinning it. That branch is now pinned by exactly one new test method, `test_a_feat_folder_with_a_mismatching_frontmatter_id_is_a_not_found_row`, placed with the other FEAT not-found tests in `tests/general/tools/test__references.py::TestResolveReference`. Construction (written directly by mutating the created document's frontmatter id, since `create_feat` enforces id == folder name): (1) `create_feat(_feat_body("Mismatch Feature"), id="feat-5-mismatch")` writes a fully valid feat document at `self.feat_dir/feat-5-mismatch/README.md`; (2) the test reads that file back, asserts the frontmatter `id:` line's value (`id: feat-5-mismatch`, unquoted) occurs exactly once, and replaces it with a different well-formed feat id (`id: feat-9-other`), leaving the body and every other frontmatter field byte-identical; (3) `resolve_reference("feat", "feat-5-mismatch")` (the full-id ref to the folder name) must yield the not-found row -- never raises, no resolution, no skipping: a `ReferenceRow` with `(type, id) == ("feat", "feat-5-mismatch")`, `title=None`, `path=None`, and `error` set to the mismatch branch's own message (the test asserts it contains `does not match the containing folder's own name` plus both ids -- a parse-failure or missing-folder message would NOT contain that phrase). Zero `src/` changes (tests-only). Gate state: fully green -- the isolated test passes (`uv run --frozen pytest tests/general/tools/test__references.py -k mismatching -v` -- 1 passed, 32 deselected), ruff format --check (1786 files already formatted), ruff check (All checks passed), vulture (no output), `uv run --frozen pytest -n auto` -- 4016 passed in 34.83s (the prior 4015 + the 1 new test), and `uv run --frozen specmgr docs` produces no doc drift (`git status --short` shows only the test file and this plan README).

### Decisions Made

#### 2026-10-02T15:29:24.000Z - Root README rewording keeps the structured-vs-free-form split explicit, and two unpinned accuracy tweaks land in `ReferenceRow`/`CHANGELOG`

Three Phase 120 wording/placement choices the plan left open: (1) the root `README.md` "Referencing Artifacts" rewording keeps the section's original structured/free-form split explicit rather than generalizing the opening sentence -- the opening `<TYPE> <uuid>` clause now names the three structured locations (VCR/SYSRS/DEC) as remaining uuid-only, and a separate "and, in free-form prose, via a `FEAT` tag" clause carries feat's own id shapes (matching the plan's intent that FEAT appears in free-form prose like the other 10 tags, which the structured patterns do not accept); the now-false "free-form or non-uuid references are ignored" becomes "any other free-form or non-conforming text is ignored", keeping the remaining intent true; (2) the `ReferenceRow.title` field docstring (not in the task's pinned anchor list) gains the same one-clause ``feat`` accuracy note as the `list_references` function docstring (the title is the feature's H1 with the ``Feature: `` prefix stripped, via ``feature_title``) -- without it the "``doc.body.text`` for the flat target domains" derivation would be false for ``feat``; (3) the `CHANGELOG.md` `[Unreleased]` bullet is appended at the END of the existing `### Changed` list (after the two #170 entries), following the file's observed oldest-first / ascending-issue-number within-section convention (#135, #170, #170) rather than a blanket newest-first, and the `list_references` tool's `@mcp.tool` description drops the leading `<TYPE> <uuid>` placeholder phrase in favor of "reference tags (the shared 11-tag reference vocabulary ...)" -- a plain-text MCP description cannot carry the per-tag id-shape nuance in a placeholder, so the vocabulary parenthetical is the carrier.

#### 2026-10-02T14:09:41.000Z - The QA->FEAT integration test's mention sits in the opaque `### Introduction` section, and the `FEAT <uuid>` pin stays an in-place subtest

Two Phase 110 fixture/framing choices the plan left open: (1) ACC-001's QA source document places its `FEAT <id>` mention in `## General` / `### Introduction` -- QA v2's only section whose body is opaque markdown of any shape -- rather than in `## Elicitation Context` or a characteristic category section (those accept only `> **<d>.<NNNN>**: {question}` Q&A pairs, so a bare prose mention would fail to parse); (2) the `FEAT <uuid>` regression pin (REQ-002/ACC-003) stays as the in-place subtest of `test_tags_outside_the_vocabulary_do_not_match` -- the task pinned "the subtest stays" -- with an inline comment carrying the reworded framing (FEAT is now in the vocabulary; the case exercises the uuid-form non-match, not an out-of-vocabulary tag), rather than being split into a new standalone test.

#### 2026-10-02T12:47:50.000Z - The ACC-003 pinned vocabulary-loop special-case lands with Phase 100, not Phase 110

The plan parked the `test_each_vocabulary_tag_matches_a_well_formed_reference` update in Phase 110 (Task 110.100) after pinning it as the one expected red test of Phase 100, but the repo's pre-commit contract runs the full pytest suite on every commit touching `src/`/`tests/` (`.pre-commit-config.yaml`), so no commit can land while the suite is red; the orchestrator therefore pulled the minimal ACC-003 special-case into Phase 100 -- a pinned `continue` (with a comment citing the pin) that skips `feat` in the UUID vocabulary loop, since `feat`'s UUID form is deliberately not a feat reference (a feat's id is never a UUID). Behavior and end state are exactly as the plan pinned: the remaining Task 110.100 work (the loop's docstring reword, the separate FEAT-form loop, and the `test_tags_outside_the_vocabulary_do_not_match` rewording) stays in Phase 110.

#### 2026-10-02T12:08:18.000Z - The FEAT pattern's id shapes are derived from the shared full-id constant, not re-typed

The plan pinned the FEAT reference pattern's id alternative (`feat-[0-9]+(?:-[a-z0-9-]+)?`) and that it "share the full-id shape" with `general/tools/_path_safety._FEAT_ID_PATTERN` via a private import with alias, but left the sharing mechanism open; it was implemented as: import the constant aliased `_FEAT_FULL_ID_PATTERN`, strip its `^`/`$` anchors to get the full-id shape, and split that shape at the hyphen preceding its final character class into the number prefix (`feat-[0-9]+`) and the slug class with quantifier (`[a-z0-9-]+`), composing the id alternative as `<prefix>(?:-<slug>)?` and the resolver's bare classifier as `^<prefix>$` -- module-scope tripwire assertions (the split yields exactly two parts, AND the number prefix is exactly `feat-` plus ONE character class with a `+` quantifier) make a shape change of the shared constant that would move the bare/full boundary fail loudly at import time instead of silently drifting the classifier. The resolver classifies via `_FEAT_BARE_ID_PATTERN.match(ref_id)` with an else-fallback to the exact `load_by_id` (a full-id ref and any other shape both go there); the anchored constant itself is used only as the SOURCE of the derived shapes (the pattern's id alternative and the bare classifier), not as a runtime classifier, the `"feat"` entry is registered last in `_TARGET_RESOLVERS` (mirroring `REFERENCE_TYPES`' order), and the bare-number zero-match not-found message names the id, the `feat-NNN-*` folder expectation, and the `README.md` requirement.

### More Information

GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/177 (finding, reproduction steps, and suggested fix).
