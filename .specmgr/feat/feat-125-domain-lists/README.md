---
classification: null
created: '2026-09-21 17:06:37.403Z'
id: feat-125-domain-lists
status: progress
type: feat
updated: '2026-09-22 00:14:34.000Z'
version: 1.0.0
---

# Feature: Consolidate the Hand-Maintained Domain-List Constants into a Shared Source of Truth

## Plan

### Overview

At least 23 places across `src/` and `tests/` independently hand-maintain a literal
list/tuple/frozenset/`Literal[...]`/dict-key-set of the document-type domain names (the 12
whole-body domains `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/
`sysrs`, optionally plus `adr`), and none of them derive from a shared constant. Confirmed
drift already found: `tests/general/tools/test__path_safety.py`'s `_UUID_DOMAINS` (11
entries) is missing `sysrs` vs. `src/biz/dfch/specmgr/general/tools/_path_safety.py`'s
`_UUID_TYPES` (12 entries), so `assert_uuid`'s test coverage silently never exercises
`sysrs`; `general/tools/delete.py`'s `_DELETE_TYPES` and `general/tools/validate.py`'s
`_VALIDATE_TYPES` are fully dead code duplicating each file's own live `_ADAPTERS`/
`Literal[...]`; two doc-cache test files carry byte-identical duplicate
`_NON_FEAT_DOMAINS` lists; and each of the five generic tools hand-maintains its
`_ADAPTERS` dict-key list and `Literal[...]` signature independently, with inconsistent
ordering between the two even within the same file (`feat` before `sop` in the
`update`/`set_status`/`set_classification` dicts, after everywhere else). Two further
instances of the same drift vector in miniature were found during planning: the local
`_TYPE_ADR = "adr"` singleton in `set_status.py` (6 use sites) and `_TYPE_FEAT = "feat"`
in `_path_safety.py` (2 use sites).

This feature is the natural "phase 2" of the same root problem feat-122-docstring-comments
fixed in prose: no single source of truth for "which domains exist". Here it produces code
drift, not just prose drift. The goal: a new domain registers its name in one shared source
instead of ~5-6 independent hand-copies. This is NOT a prose-only feature (unlike
feat-122) -- it touches real code: constants, `Literal[...]` type hints, dead-code removal.

### Requirements

- REQ-001: A new module `src/biz/dfch/specmgr/general/tools/_domains.py` is the single source of truth for document-type domain names, exposing, in the canonical order `req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs`: `WHOLE_BODY_DOMAINS` (the 12 whole-body domains), `ALL_DOMAINS` (`adr` + the 12), `WHOLE_BODY_NO_FEAT_DOMAINS` (the 12 minus `feat`), `UUID_DOMAINS` (`WHOLE_BODY_NO_FEAT_DOMAINS` + `adr`), plus the `ADR`/`FEAT` singletons. Every derived tuple is computed from `WHOLE_BODY_DOMAINS`, never hand-listed a second time. After this feature, no other `src/` module hand-lists a literal domain-name set (the issue's 23-site inventory is the baseline, not the ceiling -- a fresh repo-wide sweep runs at implementation time per feat-122's "don't trust a prior list as exhaustive" lesson).

- REQ-002: The public `type: Literal[...]` signatures of the five generic tools (`update`, `set_status`, `set_classification`, `delete`, `validate`) are re-derived from the shared source via PEP 692 unpacking (`Literal[*WHOLE_BODY_DOMAINS]` / `Literal[*ALL_DOMAINS]`), so the MCP-registered `type` enum can no longer drift from the source. All six consumer files already carry `from __future__ import annotations`, and every registered enum stays set-equal to today's -- only `set_status`'s enum value ordering changes (`adr` moves to the front).

- REQ-003: The domain lists inside the six `@mcp.tool(description=...)`/`@mcp.resource(description=...)` strings (`update`, `set_status`, `set_classification`, `delete`, `validate`, `specmgr://config`) **and the two runtime error messages** (`_path_safety.py`'s `validate_id` unknown-type message and `validate.py`'s unsupported-type message -- neither is pinned by any test) are derived via f-string (`", ".join(...)`) from the shared source, so a future domain addition touches no prose copy. Function docstrings stay string literals (the `specmgr docs` generator requires them) and keep their explicit, convention-sanctioned prose domain lists.

- REQ-004: `general/tools/_path_safety.py`'s `_UUID_TYPES` becomes `frozenset(UUID_DOMAINS)` (preserving O(1) membership and behavior), the local `_TYPE_FEAT = "feat"` singleton is replaced by the shared `FEAT`, and `general/tools/set_status.py`'s local `_TYPE_ADR = "adr"` singleton is replaced by the shared `ADR` at all 6 use sites.

- REQ-005: The dead constants `general/tools/delete.py`'s `_DELETE_TYPES` and `general/tools/validate.py`'s `_VALIDATE_TYPES` (each confirmed zero-reference; `vulture` does not flag them) are removed.

- REQ-006: The five generic tools' `_ADAPTERS` dispatch tables are reordered so every domain-name artifact in the repo shares one canonical ordering (fixing the `feat`-before-`sop` deviation in `update`/`set_status`/`set_classification`), and each `_ADAPTERS` carries a module-level set-equality assert against the shared source (with an actionable message) so a future adapter add/remove that forgets the source -- or vice versa -- fails loudly at import. The same assert covers `set_status.py`'s own 13-key `_ALLOWED_STATUSES_BY_TYPE` dict (issue inventory item #4's second dict, initially missed by this REQ): its keys are already canonical (no reorder), and its `_TYPE_ADR` key is absorbed by the shared `ADR` in the REQ-004 pass.

- REQ-007: `general/resources/config.py`'s `config_info()` builds its 13-entry `domains` dict with a set-equality assert against `ALL_DOMAINS` (insertion order unchanged: `adr` first) and derives its resource description's domain list from `ALL_DOMAINS`.

- REQ-008: Every test-side hand-listed domain set imports the shared source instead: `test__path_safety.py`'s `_UUID_DOMAINS` (11 entries, missing `sysrs` -- closed by construction) and its local `_FEAT_TYPE`, `test_delete.py`'s own local `_TYPE_FEAT` singleton (5 use sites), `test_config.py`'s `_ALL_DOMAINS`/`_DOCS_DIR_DOMAINS`, the byte-identical duplicate `_NON_FEAT_DOMAINS` in `test_doc_cache_structural.py` and `test_doc_cache_delete_scan_race.py`, and the inline enum expectations in `test_delete.py`'s and `test_update.py`'s registration tests (derived from `list(WHOLE_BODY_DOMAINS)`).

- REQ-009: `feat/tools/__init__.py`'s module docstring "the eight lifecycle tools below" (actually 7) is reworded per the issue's flagged side item, using relational phrasing (no cardinal number, per feat-122's convention), and the same docstring's second stale sentence -- "``create_feat`` assigns the next ``feat-NNN-slug`` id" (pre-feat-48 phrasing; `create_feat.py`'s own docstring is accurate) -- is reworded in the same pass.

- REQ-010: Generated artifacts are regenerated and committed with zero residual drift: `docs/MCP.md` (`specmgr mcp-docs` -- enum ordering + derived descriptions), `docs/api/` + `docs/GENERATED.md` (`specmgr docs` -- new `_domains.py` module), `docs/adr/README.md` (`specmgr adr-toc` -- new ADR).

- REQ-011: A new ADR (accepted) records the shared-source decision and refines ADR 36905d5b's future-domain convention (a new domain registers its name in `_domains.py` once, in addition to the existing dispatch entries); `AGENTS.md`'s future-domain convention paragraph is updated to point to it; `.specmgr/conventions.md` gains a "Domain-List Constants" rule (import from `general/tools/_domains.py`; no hand-listed domain-name sets in `src/` or `tests/`); `CHANGELOG.md`'s `[Unreleased]` gains an entry.

- REQ-012: Zero behavior change to any MCP tool/resource beyond the derived text: no tools added/removed/renamed, no new error paths, no change to id resolution/lock/cache/dispatch semantics; the full test suite passes on the 3.11/3.12/3.13 matrix.

### Acceptance Criteria

- [ ] ACC-001: A repo-wide sweep (the issue's inventory plus the planning-time extras) confirms every hand-listed domain-name site in `src/`/`tests/` is either rewired to `general/tools/_domains.py`, removed, or explicitly classified as kept by the Design Notes' sweep ruling; the only remaining hand-listed domain tuple in `src/` is `WHOLE_BODY_DOMAINS` itself.
- [ ] ACC-002: The existing registration tests pass with expected enums derived from `WHOLE_BODY_DOMAINS`; every registered `type` enum is set-equal to today's (only `set_status`'s ordering differs: `adr` first).
- [ ] ACC-003: `tests/general/tools/test__path_safety.py`'s UUID-domain loop exercises `sysrs` (via the imported `UUID_DOMAINS`), and the suite passes.
- [ ] ACC-004: `delete.py`/`validate.py` carry no `_DELETE_TYPES`/`_VALIDATE_TYPES`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60` is clean.
- [ ] ACC-005: Every `_ADAPTERS` dict's keys are in the single canonical order and each has its set-equality assert (verified by temporarily breaking one side during development: import fails with the actionable message).
- [ ] ACC-006: The eight derived strings (six decorator descriptions + two error messages) contain no hand-typed domain list; `specmgr mcp-docs` regenerates `docs/MCP.md` with only the intended changes.
- [ ] ACC-007: No byte-identical duplicate domain list remains across the two doc-cache test files.
- [ ] ACC-008: `feat/tools/__init__.py`'s docstring carries no stale cardinal tool count.
- [ ] ACC-009: `specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`, and `specmgr schema` all produce zero further `git status` diff after regeneration (the feat-122 REQ-004 equivalent).
- [ ] ACC-010: The new ADR exists and is `accepted`; `AGENTS.md`'s future-domain paragraph names the `_domains.py` registration step; `.specmgr/conventions.md` carries the new rule; `CHANGELOG.md` `[Unreleased]` carries the entry.
- [ ] ACC-011: `uv run --frozen pytest -n auto --cov=src --cov-report=` passes; `ruff format --check` + `ruff check` clean; `pylint` advisory run clean.

### Scope

#### Included

- The new `general/tools/_domains.py` module.
- Rewiring of `_path_safety.py`, `update.py`, `set_status.py`, `set_classification.py`, `delete.py`, `validate.py`, and `general/resources/config.py`.
- Dead-code removal (`_DELETE_TYPES`, `_VALIDATE_TYPES`).
- Test-side rewiring of six files (`test__path_safety.py`, `test_config.py`, `test_doc_cache_structural.py`, `test_doc_cache_delete_scan_race.py`, `test_delete.py`, `test_update.py`).
- The `feat/tools/__init__.py` docstring fixes (issue's flagged side item -- stale cardinal tool count -- plus the second stale `create_feat` id sentence, folded in).
- New ADR, `AGENTS.md` future-domain paragraph, `.specmgr/conventions.md` rule, `CHANGELOG.md` entry, and regeneration of all generated docs.

#### Explicitly Out Of Scope

- `server.py`'s `from . import adr, dec, feat, ...` line -- Python import statements cannot be built from a runtime list (issue follow-up #8, flagged for awareness only).
- Function docstrings' prose domain lists -- feat-122 just normalized them, the convention sanctions explicit prose lists, and the doc generator requires string literals.
- `commands/schema.py`'s `_GENERATORS` registry -- a natural dispatch registry that intentionally may lag the domain set (no `adr` generator exists yet; its own docstring says to add entries as generators land). Audited and left as-is.
- Any tool/resource behavior change (pure refactor + dead-code removal + text derivation).
- ADR's eventual phase-out (tracked separately) -- until then `adr` is an ordinary member of `ALL_DOMAINS`/`UUID_DOMAINS`; removing it later is also a one-line edit to `_domains.py`.
- The reserved future `ac` domain -- when it arrives it follows the refined convention.

### Dependencies

#### Depends On

- feat-122-docstring-comments (closed 2026-09-11): this feature is the "phase 2" of its root problem (code constants instead of prose); its `.specmgr/conventions.md` Docstring Style rule constrains how new prose (REQ-009, ADR text) is written.
- Python >= 3.11 (PEP 692), pydantic >= 2.11, mcp >= 2.0.0 -- all already pinned; no dependency changes.

#### Blocks

- None known.

### Design Notes

- **Location** -- `general/tools/_domains.py`: the domain names are a tool-layer concern (`type` dispatch of the five generic tools, `_path_safety`'s id-format dispatch); the models layer has no domain-name vocabulary; `general/resources/config.py` already imports from `general/tools` (`DOCS_DIR_ENV_VAR`), so the dependency direction is established. The module follows the private-underscore convention of `_path_safety`/`_doc_cache`/`_doc_paths`.
- **Derived, not repeated** -- `WHOLE_BODY_DOMAINS` is the only hand-listed tuple: `WHOLE_BODY_NO_FEAT_DOMAINS = tuple(d for d in WHOLE_BODY_DOMAINS if d != FEAT)`, `UUID_DOMAINS = WHOLE_BODY_NO_FEAT_DOMAINS + (ADR,)`, `ALL_DOMAINS = (ADR,) + WHOLE_BODY_DOMAINS`.
- **Canonical ordering** -- the 12-domain order is `req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs` (AGENTS.md's bullet order; already the dominant ordering in the repo). The 13-domain set is adr-first, matching AGENTS.md, `config.py`'s dict/description, and `test_config._ALL_DOMAINS`. Accepted public impact: `set_status`'s registered enum reorders `adr` to the front (JSON-schema enum ordering is non-normative; no test pins it; ADR is slated for deprecation anyway).
- **PEP 692** -- `type: Literal[*WHOLE_BODY_DOMAINS]` with `from __future__ import annotations`: the string annotation is lazily resolved by the MCP SDK's pydantic schema builder in the module namespace, where the imported name lives. Python 3.11+ supports the runtime unpack; the existing registration tests (ACC-002) verify the emitted enum across the 3.11/3.12/3.13 CI matrix.
- **`_ADAPTERS` stays a natural dispatch table** -- the dicts are not replaced by comprehensions over the shared source (their values are per-domain functions that must be enumerated anyway); instead each is tied to the shared source by a module-level `assert set(_ADAPTERS) == set(<TUPLE>), <actionable message>` (import-time guard, per the repo's "asserts express invariants" convention), and its keys are reordered to the canonical order.
- **`config_info()`** keeps its explicit per-domain `DomainConfig` entries (each domain has distinct env-var semantics: `adr`/`feat` dedicated vars, the rest shared `SPECMGR_DOCS_DIR`) -- what is derived is the membership check (assert) and the description text, not the construction.
- **Test strategy** -- the existing `update`/`delete` registration tests become the drift canaries (their expected enums derive from the shared source); the `assert_uuid` loop gains `sysrs` coverage by construction.
- **`whitelist.py`** -- the dead tuples carry no vulture whitelist entries today; removal needs none.
- **Sweep classification (2026-09-21 audit)** -- the fresh repo-wide sweep (REQ-001's baseline-not-ceiling) classified every remaining hand-listed domain-name site as explicitly kept, not rewired: prose docstrings (``general/tools/__init__.py``, ``_listing.py``, ``models/config_info.py``, ``server.py``'s own registration docstring) stay string literals per the feat-122 Docstring Style rule and the ``specmgr docs`` generator's requirement; the per-domain ``_Case``/``_InjectionCase`` dataclass rows in ``test_update.py``/``test_delete.py``/``test_set_status.py``/``test_set_classification.py``/``test_validate.py`` are per-domain fixture data, not sets; ``test_mcp_docs.py``'s 7-value enum is a ``_schema_type_str`` render fixture, not a domain list; and inline single-domain ``"feat"`` comparisons (``test_set_status.py``/``test_set_classification.py``/``test_update.py``) are single-name, not set-level -- ``test_delete.py``'s *named* ``_TYPE_FEAT`` constant is the one that gets rewired (REQ-008), since a named local constant is the drift vector. ``commands/schema.py``'s ``_GENERATORS`` stays audited-out per Scope.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 ("dispatch-only generic tools" convention): refined by this feature's new ADR -- a new domain now also registers its name in `_domains.py`.
- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d (path-safety guards): `_UUID_TYPES` is one of its constants.
- feat-122-docstring-comments's `.specmgr/conventions.md` `### Docstring Style` rule: the prose counterpart of this feature; this feature adds a companion rule for code constants.
- (New, Phase 5): ADR "Single source of truth for the document-type domain-name set".

### Task List

#### Phase 1: Quick wins (no shared source needed)

- [x] Task 1.1: Close the `sysrs` gap in `tests/general/tools/test__path_safety.py`'s `_UUID_DOMAINS` (issue follow-up #1; subsumed by Task 4.1 -- landed first as the minimal standalone fix)
- [x] Task 1.2: Remove `general/tools/delete.py`'s dead `_DELETE_TYPES` (REQ-005)
- [x] Task 1.3: Remove `general/tools/validate.py`'s dead `_VALIDATE_TYPES` (REQ-005)
- [x] Task 1.4: Reword `feat/tools/__init__.py`'s "the eight lifecycle tools below" to relational phrasing and its stale "assigns the next `feat-NNN-slug` id" sentence (REQ-009)
- [x] Task 1.5: Phase gate: `ruff format --check` + `ruff check`, `vulture`, targeted tests (`test_delete`, `test_validate`, `test__path_safety`)

#### Phase 2: The shared source

- [x] Task 2.1: Create `general/tools/_domains.py` (REQ-001): copyright header, NumPy docstring, `__all__`, `WHOLE_BODY_DOMAINS` + the three derived tuples + `ADR`/`FEAT` singletons; `git add` so `pylint` sees it
- [x] Task 2.2: Rewire `_path_safety.py` (REQ-004): `_UUID_TYPES = frozenset(UUID_DOMAINS)`, `_TYPE_FEAT` -> shared `FEAT`, docstring `:data:` references updated, unknown-type error message derived (REQ-003)
- [x] Task 2.3: Rewire `set_status.py`'s `_TYPE_ADR` -> shared `ADR` at all 6 sites (REQ-004)
- [x] Task 2.4: Phase gate: server-import smoke test (`python -c "import biz.dfch.specmgr.server"`), full suite

#### Phase 3: src rewiring

- [x] Task 3.1: `update.py` (REQ-002/003/006): `Literal[*WHOLE_BODY_DOMAINS]`, `_ADAPTERS` keys reordered (drop `feat`-before-`sop`), set-equality assert, description derived
- [x] Task 3.2: `set_status.py`: `Literal[*ALL_DOMAINS]`, `_ADAPTERS` keys reordered, set-equality asserts on `_ADAPTERS` and (already-canonical) `_ALLOWED_STATUSES_BY_TYPE`, description derived
- [x] Task 3.3: `set_classification.py`: 12-domain treatment, dict keys reordered, assert, description derived
- [x] Task 3.4: `delete.py`: `Literal[*WHOLE_BODY_DOMAINS]`, assert, description derived (dict already canonical)
- [x] Task 3.5: `validate.py`: same as Task 3.4, plus unsupported-type error message derived (REQ-003)
- [x] Task 3.6: `config.py` (REQ-007): set-equality assert in `config_info()`, description derived from `ALL_DOMAINS`
- [x] Task 3.7: Phase gate: full suite; `specmgr mcp-docs` dry run to sanity-check the emitted enums

#### Phase 4: Test rewiring

- [ ] Task 4.1: `test__path_safety.py`: import `UUID_DOMAINS`/`FEAT`, replace local constants (subsumes Task 1.1) (REQ-008)
- [ ] Task 4.2: `test_config.py`: import `ALL_DOMAINS`/`WHOLE_BODY_NO_FEAT_DOMAINS` (REQ-008)
- [ ] Task 4.3: `test_doc_cache_structural.py` + `test_doc_cache_delete_scan_race.py`: import `WHOLE_BODY_NO_FEAT_DOMAINS` (REQ-008)
- [ ] Task 4.4: `test_delete.py` + `test_update.py` registration tests: expected enums derived from `list(WHOLE_BODY_DOMAINS)`; `test_delete.py`'s local `_TYPE_FEAT` -> shared `FEAT` (REQ-008)
- [ ] Task 4.5: Phase gate: `pytest -n auto`, full suite

#### Phase 5: Docs, ADR, conventions, quality gate

- [ ] Task 5.1: Regenerate `docs/MCP.md` (`specmgr mcp-docs`), `docs/api/` + `docs/GENERATED.md` (`specmgr docs`); review the diffs for only the intended changes (REQ-010)
- [ ] Task 5.2: Write the new ADR (status `accepted`); run `specmgr adr-toc` (REQ-011)
- [ ] Task 5.3: Add the "Domain-List Constants" rule to `.specmgr/conventions.md` (REQ-011)
- [ ] Task 5.4: Update `AGENTS.md`'s future-domain convention paragraph (name the `_domains.py` registration step); add the `CHANGELOG.md` `[Unreleased]` entry (REQ-011)
- [ ] Task 5.5: Quality gate: `ruff format --check` + `ruff check`, `vulture`, `pylint` (advisory), `pytest -n auto --cov=src --cov-report=`, `specmgr docs`/`adr-toc`/`mcp-docs`/`schema` drift checks (ACC-009/011); update this README (status -> `review`, `Updates` entry)

## Progress

### Current Status

**As of 2026-09-22**: Implementation in progress -- Phases 1-3 are complete and gate-green. Phase 1 (quick wins: the `sysrs` test gap, the two dead-constant removals, the `feat` docstring rewording), Phase 2 (the shared `general/tools/_domains.py` source, with `_path_safety.py`'s `_UUID_TYPES`/`_TYPE_FEAT` and `set_status.py`'s `_TYPE_ADR` rewired onto it and `validate_id`'s unknown-type error message derived from it), and Phase 3 (src rewiring: the five generic tools' `type` signatures PEP 692 re-derived from the shared source, the `_ADAPTERS`/`_ALLOWED_STATUSES_BY_TYPE` key sets normalized and guarded by set-equality asserts, the eight derived description/error-message strings, and `config.py`'s membership assert plus derived description) are done. The issue's 23-site inventory was verified against the code during planning: all sites confirmed (line numbers in the issue are approximate -- e.g. the registration-test inline lists sit at `test_delete.py:791`/`test_update.py:1351` today), plus two extra singletons found (`set_status.py`'s `_TYPE_ADR`, `_path_safety.py`'s `_TYPE_FEAT`), plus one site audited out of scope (`commands/schema.py`'s `_GENERATORS` registry). Both planning-time decisions were resolved with the issue author: the 13-domain set is adr-first (accepting `set_status`'s harmless enum reorder), and the six decorator description strings are derived from the shared source. A 2026-09-21 pre-implementation audit (full tree + issue #125 text) verified the plan against the current code and folded in four deltas -- see Updates/Decisions Made.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-22 00:14:34.000Z - Phase 3 complete

Phase 3 (src rewiring) is implemented and gate-green. The five generic tools' public `type: Literal[...]` signatures are now PEP 692 re-derivations from the shared source: `update`/`set_classification`/`delete`/`validate` use `Literal[*WHOLE_BODY_DOMAINS]` and `set_status` uses `Literal[*ALL_DOMAINS]` (Tasks 3.1-3.5, REQ-002) -- every emitted JSON-schema enum verified live against `mcp.list_tools()` as set-equal to today's, the only ordering change anywhere being `set_status`'s `adr` moving to the front (the plan's accepted public impact). The `feat`-before-`sop` `_ADAPTERS` key-order deviation was fixed in `update.py`, `set_status.py`, and `set_classification.py` (`delete.py`/`validate.py`'s dicts were already canonical), with `set_status`'s `ADR` key staying last in both `_ADAPTERS` and `_ALLOWED_STATUSES_BY_TYPE` -- the internal dispatch tables keep their established shape; adr-first applies to the derived tuple/enum/description, not to them. Six new set-equality asserts guard the key sets: one per `_ADAPTERS` (vs `WHOLE_BODY_DOMAINS`, or vs `ALL_DOMAINS` for `set_status`) plus `set_status`'s `_ALLOWED_STATUSES_BY_TYPE` (vs `ALL_DOMAINS`; its keys were already canonical, so no reorder), each with an actionable message naming the shared `general.tools/_domains.py` source and the fix (feat-125, REQ-006); ACC-005 verified them by temporarily breaking one side during development -- dropping `update.py`'s `_ADAPTERS` `req` entry failed the module import with `AssertionError: _ADAPTERS keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- add or remove the domain in both places (feat-125-domain-lists, REQ-006)`, and dropping `set_status.py`'s `_ALLOWED_STATUSES_BY_TYPE` `req` entry failed with the matching `_ALLOWED_STATUSES_BY_TYPE ... ALL_DOMAINS` message; both were restored and clean re-imports confirmed. All eight derived strings now carry no hand-typed domain list: the five decorator descriptions are f-string-derived via `", ".join(...)` (byte-identical final text for `update`/`set_classification`/`delete`/`validate`, verified programmatically against the `git HEAD` originals; `set_status`'s text is the only one that changed -- its domain list now runs adr-first), `validate`'s unsupported-type error message is derived with the sanctioned `/` -> `, ` separator change, and `specmgr://config`'s resource description is derived from `ALL_DOMAINS` (byte-identical) with a new function-level set-equality assert on its 13-entry `domains` dict inside `config_info()` (insertion order kept, adr first; Tasks 3.5/3.6, REQ-003/007). Gate (Task 3.7): `uv run --frozen ruff format --check` (1695 files already formatted), `uv run --frozen ruff check` (All checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (clean), the `--all-extras` server-import smoke test (exit 0, no output), `uv run --frozen pytest -n auto --cov=src --cov-report=` (3365 passed), and `uv run --frozen --all-extras specmgr mcp-docs` (the `docs/MCP.md` diff is exactly the sanctioned `set_status` scope: the registered `type` enum reordered with `adr` first plus its two description occurrences now listing the domains adr-first; every other tool/resource's enum and description is byte-identical) -- `uv run --frozen --all-extras specmgr docs` then re-rendered only the five tool modules' function-signature headings in `docs/api/` (the PEP 692 annotation form, e.g. `type: 'Literal[*WHOLE_BODY_DOMAINS,]'`; CPython stores the raw annotation text including the subscript's trailing comma, and the raw form was verified to evaluate to the identical `Literal` as the clean form, so runtime behavior is unchanged), with `docs/GENERATED.md` byte-identical and no module docstrings touched.

#### 2026-09-21 21:18:05.000Z - Phase 2 complete

Phase 2 (the shared source) is implemented and gate-green. `general/tools/_domains.py` now carries the canonical domain names: `WHOLE_BODY_DOMAINS` (the 12 whole-body domains in the canonical order, the only hand-listed tuple) plus the derived `WHOLE_BODY_NO_FEAT_DOMAINS` (without `feat`), `UUID_DOMAINS` (those plus `adr`), `ALL_DOMAINS` (`adr` prefixed to the whole-body domains), and the `ADR`/`FEAT` singletons (Task 2.1, REQ-001). `_path_safety.py`'s `_UUID_TYPES` is now `frozenset(UUID_DOMAINS)` (name and O(1) membership kept), its local `_TYPE_FEAT` singleton -- 2 occurrences (definition + 1 use site) -- is deleted in favor of the shared `FEAT`, and `validate_id`'s unknown-type error message now lists the UUID domains via `', '.join(UUID_DOMAINS)`: the same 12 members as before (`req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs, adr`), only the derivation and separator changed (Tasks 2.2, REQ-003/004). `set_status.py`'s local `_TYPE_ADR` singleton -- 6 occurrences (definition + 5 use sites: the `_ALLOWED_STATUSES_BY_TYPE` key, the `_check_status_allowed` comparison, the `_ADAPTERS` key, and both `superseded_by`-guard sites) -- is deleted in favor of the shared `ADR`; the `Literal[...]` signature, `_ADAPTERS` key order, and tool description are untouched (Phase 3, Task 3.2) (Task 2.3, REQ-004). Gate (Task 2.4): `uv run --frozen ruff format --check` (1694 files already formatted), `uv run --frozen ruff check` (All checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (clean), the `--all-extras` server-import smoke test (exit 0, no output), and `uv run --frozen pytest -n auto --cov=src --cov-report=` (3365 passed) -- all green. `specmgr docs` produced only the new `_domains` API page plus its one index entry in `docs/GENERATED.md`/`docs/api/README.md` (the `_path_safety`/`set_status` pages are byte-identical -- their module and public docstrings were untouched), and `specmgr mcp-docs` left `docs/MCP.md` unchanged.

#### 2026-09-21 19:59:42.000Z - Phase 1 complete

Phase 1 (quick wins) is implemented and gate-green. `tests/general/tools/test__path_safety.py`'s local `_UUID_DOMAINS` now includes `sysrs` (between `vcr` and `adr`, matching `src`'s own `_UUID_TYPES` order), so `validate_id`'s two per-domain loop tests actually exercise the `sysrs` domain (Task 1.1; fully subsumed by Task 4.1's shared-source rewire). `general/tools/delete.py`'s dead `_DELETE_TYPES` and `general/tools/validate.py`'s dead `_VALIDATE_TYPES` were removed after a repo-wide grep confirmed zero code references for each (only prose mentions in historical `.specmgr/` feature docs, which stay untouched) (Tasks 1.2/1.3). `feat/tools/__init__.py`'s module docstring was reworded in one pass (Task 1.4): "underpins the eight lifecycle tools below" became the cardinal-free "underpins the lifecycle tools below" (relational phrasing per the feat-122 Docstring Style rule), and the pre-feat-48 sentence "``create_feat`` assigns the next ``feat-NNN-slug`` id" now states the real behavior -- optional caller-chosen ``id`` validated against the ``feat-NNN-slug`` shape before any lock/filesystem access, ``feat-0-<slug-from-title>`` default when omitted (no max+1 auto-generation), and a pre-write existence check raising ``FileExistsError`` if the resulting id/folder already exists -- mirroring ``create_feat.py``'s own docstring facts. Gate (Task 1.5): `uv run --frozen ruff format --check` (1693 files already formatted), `uv run --frozen ruff check` (All checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (clean, no findings), and `uv run --frozen pytest -n auto tests/general/tools/test_delete.py tests/general/tools/test_validate.py tests/general/tools/test__path_safety.py` (53 passed) -- all green.

#### 2026-09-21 18:32:15.287Z - Plan audit: four deltas folded in

Pre-implementation audit of this plan against the current tree and the issue #125 text (implementation itself starts separately via the phase orchestrator). Verified correct: all 23 inventory sites, the `sysrs` test-coverage gap, the zero-reference dead tuples, the byte-identical `_NON_FEAT_DOMAINS` duplicate, the `feat`-before-`sop` deviation (exactly the `update`/`set_status`/`set_classification` dicts), the 6-site/2-site singleton counts, that only `set_status`'s registered enum reorders (no test pins it; `test_delete.py:790`/`test_update.py:1350` are the only enum asserts), and that 5 of the 6 description derivations are byte-identical while only `set_status`'s text changes (adr-first). Core PEP 692 mechanism test-run on the pinned stack (pydantic 2.13.4, mcp 2.0.0): `Literal[*T]` under `from __future__ import annotations` emits the enum in tuple order through the MCP SDK's `TypeAdapter`-over-function schema path. Four deltas folded in, each decided with the plan author as recommended: (1) `set_status.py`'s 13-key `_ALLOWED_STATUSES_BY_TYPE` dict (issue item #4's second dict) joins REQ-006's assert scope -- keys already canonical, no reorder; (2) `test_delete.py:101`'s local `_TYPE_FEAT` singleton (5 use sites) joins REQ-008/Task 4.4; (3) `feat/tools/__init__.py`'s second stale sentence ("``create_feat`` assigns the next ``feat-NNN-slug`` id", pre-feat-48 phrasing) joins REQ-009/Task 1.4; (4) REQ-003's derived-string scope grows from six to eight, adding `_path_safety.py`'s `validate_id` unknown-type message and `validate.py`'s unsupported-type message (no test pins either; ACC-006 updated to match). Design Notes gains a sweep-classification ruling for every remaining hand-listed site.

#### 2026-09-21 16:56:13.772Z - Created

Planned from GitHub issue #125 ("Consolidate the ~23 independently hand-maintained domain-list constants into a shared source of truth"). The issue's full 23-site inventory, the two dead-code sites, the confirmed `sysrs` test-coverage gap, and the `feat`/`sop` ordering split were all verified against the current tree before drafting; the `feat/tools/__init__.py` "eight lifecycle tools" side item is folded into Phase 1 (Task 1.4) rather than filed separately.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-21 18:32:15.287Z - Audit deltas: _ALLOWED_STATUSES_BY_TYPE assert, test_delete _TYPE_FEAT rewire, second feat docstring sentence, eight derived strings

The 2026-09-21 pre-implementation audit found four plan gaps, each resolved with the plan author by taking the recommended option. `set_status.py`'s `_ALLOWED_STATUSES_BY_TYPE` (13-key dict with literal domain keys -- issue inventory item #4's "dict keys x2") gets the same module-level set-equality assert vs `ALL_DOMAINS` as the `_ADAPTERS` tables (REQ-006): its keys are already canonical so no reorder is needed, and its `_TYPE_ADR` key is absorbed by the shared `ADR` in the REQ-004 pass. `test_delete.py`'s local `_TYPE_FEAT` singleton (5 use sites) is rewired to the shared `FEAT` (REQ-008) -- the same miniature drift vector the planning pass already caught on the `src/` side (`_TYPE_ADR`/`_TYPE_FEAT`). `feat/tools/__init__.py`'s second stale sentence ("``create_feat`` assigns the next ``feat-NNN-slug`` id" -- predates feat-48-feat-id's caller-chosen-`id`/`feat-0-<slug>`-default behavior) is reworded in the same pass as the "eight lifecycle tools" fix (REQ-009). REQ-003's derived-string scope grows from six decorator descriptions to eight, adding the two runtime error messages (`_path_safety.py`'s `validate_id` unknown-type, `validate.py`'s unsupported-type): runtime f-strings carry no doc-generator constraint and no test pins their text, so deriving them kills the last code-level drift vector at zero test impact. The remaining hand-listed sites are classified as explicitly kept (Design Notes sweep ruling): prose docstrings, per-domain `_Case`/`_InjectionCase` fixture rows, `test_mcp_docs.py`'s render fixture, and inline single-domain comparisons.

#### 2026-09-21 16:56:13.772Z - Canonical ordering: adr-first for the 13-domain set

`ALL_DOMAINS = (ADR,) + WHOLE_BODY_DOMAINS` mirrors AGENTS.md's own bullet order, `config.py`'s existing dict/description, and `test_config._ALL_DOMAINS`. The single public impact -- `set_status`'s registered JSON-schema enum reordering `adr` to the front -- is accepted: enum ordering is non-normative, no test pins it, `docs/MCP.md` regenerates, and `adr` is slated for deprecation anyway, so preserving its current last position buys nothing.

#### 2026-09-21 16:56:13.772Z - Derive the six decorator description strings

A deliberate scope addition beyond the issue's literal follow-up list (which covers only code constants/`Literal` hints): the issue's stated goal is "a new domain adding itself to a single shared source instead of ~5-6 independent hand-copies", and the six `@mcp.tool(description=...)`/resource strings are six more hand-copies. They are f-string-derived from the shared tuples; function docstrings stay literal per the doc generator's requirement and the feat-122 convention.

#### 2026-09-21 16:56:13.772Z - _ADAPTERS dicts kept as natural dispatch tables, guarded by asserts

The dicts are not replaced by comprehensions over the shared source (their per-domain function values must be enumerated anyway); instead each carries a module-level set-equality assert tying its key set to `_domains.py`, per issue follow-up #5's "audit case by case" and the repo's assert-for-invariants convention.
