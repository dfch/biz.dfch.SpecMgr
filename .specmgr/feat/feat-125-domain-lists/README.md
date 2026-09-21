---
classification: null
created: '2026-09-21 17:06:37.403Z'
id: feat-125-domain-lists
status: planning
type: feat
updated: '2026-09-21 17:06:37.403Z'
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

- REQ-003: The domain lists inside the six `@mcp.tool(description=...)`/`@mcp.resource(description=...)` strings (`update`, `set_status`, `set_classification`, `delete`, `validate`, `specmgr://config`) are derived via f-string (`", ".join(...)`) from the shared source, so a future domain addition touches no prose copy. Function docstrings stay string literals (the `specmgr docs` generator requires them) and keep their explicit, convention-sanctioned prose domain lists.

- REQ-004: `general/tools/_path_safety.py`'s `_UUID_TYPES` becomes `frozenset(UUID_DOMAINS)` (preserving O(1) membership and behavior), the local `_TYPE_FEAT = "feat"` singleton is replaced by the shared `FEAT`, and `general/tools/set_status.py`'s local `_TYPE_ADR = "adr"` singleton is replaced by the shared `ADR` at all 6 use sites.

- REQ-005: The dead constants `general/tools/delete.py`'s `_DELETE_TYPES` and `general/tools/validate.py`'s `_VALIDATE_TYPES` (each confirmed zero-reference; `vulture` does not flag them) are removed.

- REQ-006: The five generic tools' `_ADAPTERS` dispatch tables are reordered so every domain-name artifact in the repo shares one canonical ordering (fixing the `feat`-before-`sop` deviation in `update`/`set_status`/`set_classification`), and each `_ADAPTERS` carries a module-level set-equality assert against the shared source (with an actionable message) so a future adapter add/remove that forgets the source -- or vice versa -- fails loudly at import.

- REQ-007: `general/resources/config.py`'s `config_info()` builds its 13-entry `domains` dict with a set-equality assert against `ALL_DOMAINS` (insertion order unchanged: `adr` first) and derives its resource description's domain list from `ALL_DOMAINS`.

- REQ-008: Every test-side hand-listed domain set imports the shared source instead: `test__path_safety.py`'s `_UUID_DOMAINS` (11 entries, missing `sysrs` -- closed by construction) and its local `_FEAT_TYPE`, `test_config.py`'s `_ALL_DOMAINS`/`_DOCS_DIR_DOMAINS`, the byte-identical duplicate `_NON_FEAT_DOMAINS` in `test_doc_cache_structural.py` and `test_doc_cache_delete_scan_race.py`, and the inline enum expectations in `test_delete.py`'s and `test_update.py`'s registration tests (derived from `list(WHOLE_BODY_DOMAINS)`).

- REQ-009: `feat/tools/__init__.py`'s module docstring "the eight lifecycle tools below" (actually 7) is reworded per the issue's flagged side item, using relational phrasing (no cardinal number, per feat-122's convention).

- REQ-010: Generated artifacts are regenerated and committed with zero residual drift: `docs/MCP.md` (`specmgr mcp-docs` -- enum ordering + derived descriptions), `docs/api/` + `docs/GENERATED.md` (`specmgr docs` -- new `_domains.py` module), `docs/adr/README.md` (`specmgr adr-toc` -- new ADR).

- REQ-011: A new ADR (accepted) records the shared-source decision and refines ADR 36905d5b's future-domain convention (a new domain registers its name in `_domains.py` once, in addition to the existing dispatch entries); `AGENTS.md`'s future-domain convention paragraph is updated to point to it; `.specmgr/conventions.md` gains a "Domain-List Constants" rule (import from `general/tools/_domains.py`; no hand-listed domain-name sets in `src/` or `tests/`); `CHANGELOG.md`'s `[Unreleased]` gains an entry.

- REQ-012: Zero behavior change to any MCP tool/resource beyond the derived text: no tools added/removed/renamed, no new error paths, no change to id resolution/lock/cache/dispatch semantics; the full test suite passes on the 3.11/3.12/3.13 matrix.

### Acceptance Criteria

- [ ] ACC-001: A repo-wide sweep (the issue's inventory plus the planning-time extras) confirms every hand-listed domain-name site in `src/`/`tests/` is either rewired to `general/tools/_domains.py` or removed; the only remaining hand-listed domain tuple in `src/` is `WHOLE_BODY_DOMAINS` itself.
- [ ] ACC-002: The existing registration tests pass with expected enums derived from `WHOLE_BODY_DOMAINS`; every registered `type` enum is set-equal to today's (only `set_status`'s ordering differs: `adr` first).
- [ ] ACC-003: `tests/general/tools/test__path_safety.py`'s UUID-domain loop exercises `sysrs` (via the imported `UUID_DOMAINS`), and the suite passes.
- [ ] ACC-004: `delete.py`/`validate.py` carry no `_DELETE_TYPES`/`_VALIDATE_TYPES`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60` is clean.
- [ ] ACC-005: Every `_ADAPTERS` dict's keys are in the single canonical order and each has its set-equality assert (verified by temporarily breaking one side during development: import fails with the actionable message).
- [ ] ACC-006: The six decorator description strings contain no hand-typed domain list; `specmgr mcp-docs` regenerates `docs/MCP.md` with only the intended changes.
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
- The one-line `feat/tools/__init__.py` docstring fix (issue's flagged side item, folded in).
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

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 ("dispatch-only generic tools" convention): refined by this feature's new ADR -- a new domain now also registers its name in `_domains.py`.
- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d (path-safety guards): `_UUID_TYPES` is one of its constants.
- feat-122-docstring-comments's `.specmgr/conventions.md` `### Docstring Style` rule: the prose counterpart of this feature; this feature adds a companion rule for code constants.
- (New, Phase 5): ADR "Single source of truth for the document-type domain-name set".

### Task List

#### Phase 1: Quick wins (no shared source needed)

- [ ] Task 1.1: Close the `sysrs` gap in `tests/general/tools/test__path_safety.py`'s `_UUID_DOMAINS` (issue follow-up #1; subsumed by Task 4.1 -- landed first as the minimal standalone fix)
- [ ] Task 1.2: Remove `general/tools/delete.py`'s dead `_DELETE_TYPES` (REQ-005)
- [ ] Task 1.3: Remove `general/tools/validate.py`'s dead `_VALIDATE_TYPES` (REQ-005)
- [ ] Task 1.4: Reword `feat/tools/__init__.py`'s "the eight lifecycle tools below" to relational phrasing (REQ-009)
- [ ] Task 1.5: Phase gate: `ruff format --check` + `ruff check`, `vulture`, targeted tests (`test_delete`, `test_validate`, `test__path_safety`)

#### Phase 2: The shared source

- [ ] Task 2.1: Create `general/tools/_domains.py` (REQ-001): copyright header, NumPy docstring, `__all__`, `WHOLE_BODY_DOMAINS` + the three derived tuples + `ADR`/`FEAT` singletons; `git add` so `pylint` sees it
- [ ] Task 2.2: Rewire `_path_safety.py` (REQ-004): `_UUID_TYPES = frozenset(UUID_DOMAINS)`, `_TYPE_FEAT` -> shared `FEAT`, docstring `:data:` references updated
- [ ] Task 2.3: Rewire `set_status.py`'s `_TYPE_ADR` -> shared `ADR` at all 6 sites (REQ-004)
- [ ] Task 2.4: Phase gate: server-import smoke test (`python -c "import biz.dfch.specmgr.server"`), full suite

#### Phase 3: src rewiring

- [ ] Task 3.1: `update.py` (REQ-002/003/006): `Literal[*WHOLE_BODY_DOMAINS]`, `_ADAPTERS` keys reordered (drop `feat`-before-`sop`), set-equality assert, description derived
- [ ] Task 3.2: `set_status.py`: `Literal[*ALL_DOMAINS]`, dict keys reordered, assert, description derived
- [ ] Task 3.3: `set_classification.py`: 12-domain treatment, dict keys reordered, assert, description derived
- [ ] Task 3.4: `delete.py`: `Literal[*WHOLE_BODY_DOMAINS]`, assert, description derived (dict already canonical)
- [ ] Task 3.5: `validate.py`: same as Task 3.4
- [ ] Task 3.6: `config.py` (REQ-007): set-equality assert in `config_info()`, description derived from `ALL_DOMAINS`
- [ ] Task 3.7: Phase gate: full suite; `specmgr mcp-docs` dry run to sanity-check the emitted enums

#### Phase 4: Test rewiring

- [ ] Task 4.1: `test__path_safety.py`: import `UUID_DOMAINS`/`FEAT`, replace local constants (subsumes Task 1.1) (REQ-008)
- [ ] Task 4.2: `test_config.py`: import `ALL_DOMAINS`/`WHOLE_BODY_NO_FEAT_DOMAINS` (REQ-008)
- [ ] Task 4.3: `test_doc_cache_structural.py` + `test_doc_cache_delete_scan_race.py`: import `WHOLE_BODY_NO_FEAT_DOMAINS` (REQ-008)
- [ ] Task 4.4: `test_delete.py` + `test_update.py` registration tests: expected enums derived from `list(WHOLE_BODY_DOMAINS)` (REQ-008)
- [ ] Task 4.5: Phase gate: `pytest -n auto`, full suite

#### Phase 5: Docs, ADR, conventions, quality gate

- [ ] Task 5.1: Regenerate `docs/MCP.md` (`specmgr mcp-docs`), `docs/api/` + `docs/GENERATED.md` (`specmgr docs`); review the diffs for only the intended changes (REQ-010)
- [ ] Task 5.2: Write the new ADR (status `accepted`); run `specmgr adr-toc` (REQ-011)
- [ ] Task 5.3: Add the "Domain-List Constants" rule to `.specmgr/conventions.md` (REQ-011)
- [ ] Task 5.4: Update `AGENTS.md`'s future-domain convention paragraph (name the `_domains.py` registration step); add the `CHANGELOG.md` `[Unreleased]` entry (REQ-011)
- [ ] Task 5.5: Quality gate: `ruff format --check` + `ruff check`, `vulture`, `pylint` (advisory), `pytest -n auto --cov=src --cov-report=`, `specmgr docs`/`adr-toc`/`mcp-docs`/`schema` drift checks (ACC-009/011); update this README (status -> `review`, `Updates` entry)

## Progress

### Current Status

**As of 2026-09-21**: Planned. The issue's 23-site inventory was verified against the code during planning: all sites confirmed (line numbers in the issue are approximate -- e.g. the registration-test inline lists sit at `test_delete.py:791`/`test_update.py:1351` today), plus two extra singletons found (`set_status.py`'s `_TYPE_ADR`, `_path_safety.py`'s `_TYPE_FEAT`), plus one site audited out of scope (`commands/schema.py`'s `_GENERATORS` registry). Both planning-time decisions were resolved with the issue author: the 13-domain set is adr-first (accepting `set_status`'s harmless enum reorder), and the six decorator description strings are derived from the shared source.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-21 16:56:13.772Z - Created

Planned from GitHub issue #125 ("Consolidate the ~23 independently hand-maintained domain-list constants into a shared source of truth"). The issue's full 23-site inventory, the two dead-code sites, the confirmed `sysrs` test-coverage gap, and the `feat`/`sop` ordering split were all verified against the current tree before drafting; the `feat/tools/__init__.py` "eight lifecycle tools" side item is folded into Phase 1 (Task 1.4) rather than filed separately.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-21 16:56:13.772Z - Canonical ordering: adr-first for the 13-domain set

`ALL_DOMAINS = (ADR,) + WHOLE_BODY_DOMAINS` mirrors AGENTS.md's own bullet order, `config.py`'s existing dict/description, and `test_config._ALL_DOMAINS`. The single public impact -- `set_status`'s registered JSON-schema enum reordering `adr` to the front -- is accepted: enum ordering is non-normative, no test pins it, `docs/MCP.md` regenerates, and `adr` is slated for deprecation anyway, so preserving its current last position buys nothing.

#### 2026-09-21 16:56:13.772Z - Derive the six decorator description strings

A deliberate scope addition beyond the issue's literal follow-up list (which covers only code constants/`Literal` hints): the issue's stated goal is "a new domain adding itself to a single shared source instead of ~5-6 independent hand-copies", and the six `@mcp.tool(description=...)`/resource strings are six more hand-copies. They are f-string-derived from the shared tuples; function docstrings stay literal per the doc generator's requirement and the feat-122 convention.

#### 2026-09-21 16:56:13.772Z - _ADAPTERS dicts kept as natural dispatch tables, guarded by asserts

The dicts are not replaced by comprehensions over the shared source (their per-domain function values must be enumerated anyway); instead each carries a module-level set-equality assert tying its key set to `_domains.py`, per issue follow-up #5's "audit case by case" and the repo's assert-for-invariants convention.
