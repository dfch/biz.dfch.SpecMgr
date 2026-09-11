---
classification: null
created: '2026-09-11 06:58:07.735+02:00'
id: feat-122-docstring-comments
status: planning
type: feat
updated: '2026-09-11 06:58:07.735+02:00'
version: 1.0.0
---

# Feature: Stop Restating Hardcoded Domain/Type Counts in Prose Docstrings and Comments

## Plan

### Overview

While verifying feat-120-remove-confluence, stale prose was found in `src/biz/dfch/specmgr/general/tools/__init__.py` claiming "the eleven whole-body document types" when the current count is twelve (missing `sysrs`, added by feat-32-sysrs). A repo-wide search showed this is a systemic pattern: many docstrings, comments, and MCP tool description strings restate "how many domains does this tool/concept apply to" as a cardinal number word (`ten`/`eleven`/`twelve`/`thirteen`), duplicating information already fully and authoritatively expressed by the code itself (a `Literal[...]` type hint, a `frozenset`/tuple of domain names, or an explicit `req/uc/tsk/.../sysrs` list right next to the number). Every time a domain is added (most recently `sysrs`; `AGENTS.md` already reserves a future spot for `ac`), every one of these manually-written count words has to be found and bumped by hand, with no test or lint rule catching a miss -- and the drift has already produced inconsistent counts describing the identical set of domains across different files. This feature removes the bare cardinal-number pattern from `src/` (and, at full priority, `tests/`) prose, and adds a convention to `.specmgr/conventions.md` so the pattern is not reintroduced.

### Requirements

- REQ-001: No `src/` docstring, comment, or MCP tool description string states a bare cardinal number (`ten`/`eleven`/`twelve`/`thirteen`, in word or digit form) as a domain/type count.

- REQ-002: Where a docstring/comment already lists the actual domains explicitly (e.g. `req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs`), the list is kept as-is but the redundant cardinal-number adjective in front of it is dropped.

- REQ-003: Where a comment describes a domain set by contrast to another (e.g. "every domain except `feat`", "every domain except `adr`"), it is phrased relationally instead of restating a count that then has to be kept in sync separately.

- REQ-004: `specmgr docs` and `specmgr mcp-docs` produce zero further `git status` diff after the wording edits, since some of the edited strings feed generated documentation (`docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`).

- REQ-005: `.specmgr/conventions.md` documents the new "don't restate a domain/type count as a cardinal number" rule in its Documentation Requirements/Docstring Style section.

- REQ-006: The same count-word cleanup identified in `src/` is also applied to the identified `tests/` docstrings/comments (non-assertion text only), tracked at the same priority as the `src/` cleanup.

- REQ-007: No `Literal[...]` type hint, `frozenset`/tuple constant, or dispatch table that defines which domains a tool supports is changed by this feature -- the change is prose-only.

### Acceptance Criteria

- [ ] ACC-001: No `src/` docstring/comment/description string states a bare cardinal number (`ten`/`eleven`/`twelve`/`thirteen`, or their digit forms) as a domain/type count; explicit domain lists and relational phrasing ("except `feat`"/"except `adr`") are used instead.

- [ ] ACC-002: `specmgr docs`/`specmgr mcp-docs` produce zero further `git status` diff after the edits.

- [ ] ACC-003: Full quality gate green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`.

- [ ] ACC-004: `.specmgr/conventions.md` documents the new rule.

- [ ] ACC-005: The same cleanup is applied to the identified `tests/` files (Phase 2), tracked at full priority rather than deferred.

### Scope

#### Included

- Rewording docstrings/comments/MCP tool description strings in the 18 confirmed `src/` files: the issue's original 16 (`general/tools/__init__.py`, `general/tools/set_classification.py`, `general/tools/set_status.py`, `general/tools/update.py`, `general/tools/delete.py`, `general/tools/validate.py`, `general/tools/_path_safety.py`, `server.py`, `general/resources/config.py`, `general/resources/__init__.py`, `feat/models/v1/summary.py`, `feat/tools/list_feat.py`, `models/config_info.py`, `models/md/_frontmatter_parse.py`, `adr/tools/validate_adr.py`, `adr/tools/create_adr.py`), plus 2 more found via a repo-wide `grep -rn -iE "\b(ten|eleven|twelve|thirteen)\b" --include="*.py" src/` audit that the issue's own list missed: `general/tools/_splice.py` and `rsk/tools/_sentinel.py`.

- Rewording the same count-word pattern in the 10 confirmed `tests/` files: `tests/sysrs/models/v1/test_parser.py`, `tests/general/resources/test_config.py`, `tests/general/models/test_summary.py`, `tests/general/tools/test_set_classification.py`, `tests/general/tools/test_validate.py`, `tests/general/tools/test__path_safety.py`, `tests/general/tools/test_set_status.py`, `tests/general/tools/test_delete.py`, `tests/general/tools/test_update.py`, `tests/feat/tools/test_list_feat.py`.

- Adding a new rule to `.specmgr/conventions.md`'s Documentation Requirements/Docstring Style section.

- Regenerating `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` where the edited strings feed generated docs, confirmed via a clean `git status` diff.

- A full quality-gate run (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) after each phase's edits, as a safety net.

#### Explicitly Out Of Scope

- Any change to the actual `Literal[...]` type hints, `frozenset`/tuple constants, or dispatch tables that define which domains a tool supports -- this feature is prose-only.

- feat-120-remove-confluence itself; this issue's trigger was discovered during that feature's verification but is unrelated to Confluence in subject matter.

- Adding an automated lint/CI rule that catches a reintroduced cardinal-number count word; only a documented convention in `.specmgr/conventions.md` is in scope.

### Design Notes

The rule exists because manually-maintained count words have already drifted: `delete.py`/`update.py` describe "the ten UUID domains" while `set_classification.py` describes "the eleven UUID domains" for the identical set, and `tests/general/tools/test_update.py` alone mixes "ten whole-body document types", "twelve domains", and "eleven whole-body domains" in different docstrings. Dropping the redundant cardinal number -- keeping only explicit domain lists or relational phrasing -- removes the drift vector entirely, since there is no longer a count to fall out of sync whenever a domain (e.g. `sysrs`, and later `ac`) is added.

A fresh `grep -rn -iE "\b(ten|eleven|twelve|thirteen)\b" --include="*.py" src/` confirmed 80 total occurrences across these 18 files (not the issue's original 16) -- each a small, one-word/one-phrase edit inside an existing docstring paragraph, comparable in scale to (and smaller than) precedent single-phase/single-task batches already completed in this repo (feat-38-39-41-43-44's Phase 3: 44 call sites across ~13 files in one task; Phase 5: one line added to 39 files in one task), which is why this feature keeps three phases rather than subdividing further by file count.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: establishes that a new document domain adds one dispatch entry to each generic tool (`update`/`set_status`/etc.) rather than a new per-domain tool; this feature applies the same anti-duplication spirit to prose, replacing hand-maintained domain counts with the domain list or dispatch table that already exists in code.

### Task List

#### Phase 1: Reword src/ docstrings, comments, and MCP tool description strings

- [ ] Task 1.1: Reword the four paragraphs (`update`, `set_status`, `set_classification`, `delete`) in `general/tools/__init__.py`.

- [ ] Task 1.2: Reword `general/tools/set_classification.py`.

- [ ] Task 1.3: Reword `general/tools/set_status.py`.

- [ ] Task 1.4: Reword `general/tools/update.py`.

- [ ] Task 1.5: Reword `general/tools/delete.py`.

- [ ] Task 1.6: Reword `general/tools/validate.py`.

- [ ] Task 1.7: Reword `general/tools/_path_safety.py`.

- [ ] Task 1.8: Reword `server.py`.

- [ ] Task 1.9: Reword `general/resources/config.py`.

- [ ] Task 1.10: Reword `general/resources/__init__.py`.

- [ ] Task 1.11: Reword `feat/models/v1/summary.py`.

- [ ] Task 1.12: Reword `feat/tools/list_feat.py`.

- [ ] Task 1.13: Reword `models/config_info.py`.

- [ ] Task 1.14: Reword `models/md/_frontmatter_parse.py`.

- [ ] Task 1.15: Reword `adr/tools/validate_adr.py`.

- [ ] Task 1.16: Reword `adr/tools/create_adr.py`.

- [ ] Task 1.17: Reword `general/tools/_splice.py` and `rsk/tools/_sentinel.py` -- 2 files the issue's own audit missed, found via a fresh repo-wide grep.

- [ ] Task 1.18: Regenerate `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` via `specmgr docs`/`specmgr mcp-docs`; confirm a clean `git status` diff.

- [ ] Task 1.19: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`).

#### Phase 2: Reword tests/ docstrings and comments

- [ ] Task 2.1: Reword `tests/sysrs/models/v1/test_parser.py`.

- [ ] Task 2.2: Reword `tests/general/resources/test_config.py`.

- [ ] Task 2.3: Reword `tests/general/models/test_summary.py`.

- [ ] Task 2.4: Reword `tests/general/tools/test_set_classification.py`.

- [ ] Task 2.5: Reword `tests/general/tools/test_validate.py`.

- [ ] Task 2.6: Reword `tests/general/tools/test__path_safety.py`.

- [ ] Task 2.7: Reword `tests/general/tools/test_set_status.py`.

- [ ] Task 2.8: Reword `tests/general/tools/test_delete.py`.

- [ ] Task 2.9: Reword `tests/general/tools/test_update.py`, reconciling the three different counts ("ten", "twelve", "eleven") mixed across its docstrings.

- [ ] Task 2.10: Reword `tests/feat/tools/test_list_feat.py`.

- [ ] Task 2.11: Run the full quality gate again after the Phase 2 edits.

#### Phase 3: Codify the convention

- [ ] Task 3.1: Add a rule to `.specmgr/conventions.md`'s Documentation Requirements/Docstring Style section stating that a generic tool's supported-domain count must not be restated as a cardinal number in prose; use explicit domain lists or relational phrasing instead.

- [ ] Task 3.2: Run a final full quality-gate pass and confirm `specmgr docs`/`specmgr adr-toc` produce zero diff.

## Progress

### Current Status

**As of 2026-09-11**: Feature just drafted from GitHub issue #122; no code changes have been made yet. The Phase 1 (18 files) and Phase 2 (10 test files) lists are taken from the issue's own `grep -rn -iE "\b(ten|eleven|twelve|thirteen)\b"` audit plus 2 additional `src/` files found via a follow-up grep the issue's own audit missed. Phase 2 is tracked at full priority, not as an optional lower-priority addendum, since the full test suite must run in any case.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-11 00:00:00.000Z - Created

Feature drafted from GitHub issue #122 ("Stop restating hardcoded domain/type counts in prose docstrings and comments"), discovered during feat-120-remove-confluence verification. Scope mirrors the issue's three phases, with Phase 2 (tests/ cleanup) tracked at full priority rather than as an optional lower-priority addendum, per user direction. Phase 1 scope expanded from the issue's 16 files to 18 after a follow-up grep found 2 more matching files (`general/tools/_splice.py`, `rsk/tools/_sentinel.py`) the issue's own audit missed. Kept the 3-phase structure rather than splitting further by file count, since the measured scope (80 occurrences across 18 files, mechanical one-word/one-phrase edits) is smaller than precedent single-phase/single-task batches already completed successfully in this repo (feat-38-39-41-43-44's Phase 3: 44 sites across ~13 files; Phase 5: 39 files), and no code changes made this a candidate for a heavier phase-implementer context load.
