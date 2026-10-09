---
classification: null
created: '2026-10-09T09:58:41.413+02:00'
id: feat-208-env-var
status: planning
type: feat
updated: '2026-10-09T09:58:41.413+02:00'
version: 1.0.0
---

# Feature: Consolidate Environment Variable Definitions into a Central Registry

## Plan

### Overview

GitHub issue #208: multiple parts of the program read `SPECMGR_*` environment variables directly (12 at planning time), which has repeatedly led to documentation errors and gaps (the root `README.md` was already missing variables, and the `server.json` manifest drifted before being caught after the fact by feat-126's drift test). This feature introduces a central environment-variable registry: a cross-cutting module under `general/` where each domain/feature registers the env var names it reads, with their defaults, descriptions, and owners. The registry centrally handles value loading and default insertion and becomes the single source of truth for documentation tracking -- tests pin that every env var read in `src/` is registered and documented (README "Environment Variables" section + `server.json`'s `environmentVariables`), and that every registered var is read in `src/`. Existing read sites migrate to the registry accessor with no change to var names, defaults, or read-time semantics -- no domain is broken.

Verified state at planning time (2026-10-09):

- The code reads exactly 12 `SPECMGR_*` env vars: `SPECMGR_ADR_DIR`, `SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR` (base-dir overrides with defaults), `SPECMGR_MCP_TRANSPORT`/`SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT` (Typer `envvar=` options with defaults), `SPECMGR_SIMILARITY_DISABLED`/`SPECMGR_FEAT_WARMUP_DISABLED` (presence-based gates), `SPECMGR_PLANTUML_JAR`/`SPECMGR_PLANTUML_BIN`/`SPECMGR_PLANTUML_URL` (first-set-wins sources, no defaults), and `SPECMGR_TESTS_NO_DOTENV` (test/CI sentinel, presence-based) -- the set pinned by feat-126-server-json-env-drift's drift test (status: review).
- One third-party env var is also read: `FASTEMBED_CACHE_PATH` (the model cache dir reported by `specmgr://config`).
- The README's "Environment Variables" section is hand-maintained prose (repo precedent since feat-7) and `server.json` is a hand-maintained manifest guarded by feat-126's bidirectional source-scan drift test.
- The `plantuml/` package is import-free (no `biz.dfch.specmgr.*` imports; the dependency direction is always specmgr -> `plantuml`), so the `SPECMGR_PLANTUML_*` trio's read sites in `plantuml/chain.py` cannot go through the registry accessor (see Design Notes, "The plantuml carve-out").

### Requirements

- REQ-001: A central environment-variable registry (cross-cutting private module under `general/`, no `mcp` dependency) in which every env var is registered by name with its default (or a presence-based marker), a description, and an owner (domain/feature); duplicate registration of the same name with conflicting metadata fails loudly.
- REQ-002: A single registry-backed accessor used by every current `SPECMGR_*` read site in `src/` (and `FASTEMBED_CACHE_PATH`), except the import-free `plantuml/` package (which keeps its own direct `os.environ` reads behind its injectable `env` mapping): it reads the process environment at call time, inserts the registered default when unset, and preserves today's exact semantics (set-but-empty treated as set, except the documented `FASTEMBED_CACHE_PATH` empty-fallback).
- REQ-003: Completeness: a test asserts that every env var read in `src/` is registered (scan-based, extending feat-126's read-site shapes) and that every registered env var is read in `src/` (no stale registrations).
- REQ-004: Documentation tracking: a test asserts that every registered env var is documented in the root `README.md`'s "Environment Variables" section and in `server.json`'s `environmentVariables` with a faithful default (presence-based vars carry none), so "is every env var documented?" is a test result, not a manual audit.
- REQ-005: No domain breakage: no env var name, default, or observable behaviour change; `specmgr://config` output unchanged; the existing test suite stays green; the registry is additive.
- REQ-006: `CHANGELOG.md` gains an `[Unreleased]` entry and `docs/` is regenerated (`specmgr docs`) without drift.

### Acceptance Criteria

- [ ] ACC-001: The registry module exists under `general/` and all 12 `SPECMGR_*` vars (plus `FASTEMBED_CACHE_PATH`) are registered with defaults faithful to the code (presence-based vars carry no default).
- [ ] ACC-002: Every env var read site in `src/` reads through the registry accessor, except the import-free `plantuml/` package (its trio registered by its uc-domain consumer, read sites unchanged); the Typer MCP options source their defaults from the registry, verified by test and/or source scan.
- [ ] ACC-003: The registry-to-source completeness test is green: every read var registered, every registered var read; a manual mutation (register a bogus var / unregister a read one) fails it naming the var, then is reverted.
- [ ] ACC-004: The documentation-coverage test is green: every registered var appears in the README "Environment Variables" section and in `server.json` with a faithful default; a manual mutation fails it naming the var, then is reverted.
- [ ] ACC-005: Behaviour unchanged: the full quality gate is green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`) and `specmgr://config`'s JSON output is byte-identical before and after the migration.
- [ ] ACC-006: The `CHANGELOG.md` `[Unreleased]` entry and regenerated `docs/` are committed inside the feature's commits.

### Scope

#### Included

- The central registry module and accessor under `general/` (cross-cutting, no `mcp` import).
- Registration of all 12 `SPECMGR_*` env vars plus `FASTEMBED_CACHE_PATH` (name, default/presence marker, description, owner) -- the plantuml trio registered by its uc-domain consumer.
- Migration of every env var read site in `src/` except the import-free `plantuml/` package to the registry-backed accessor (including the three Typer `envvar=` options' defaults).
- New tests: registry-to-source completeness drift and documentation coverage (README "Environment Variables" + `server.json` manifest, default fidelity).
- Corrections to any documentation gaps the new tests surface.
- The `CHANGELOG.md` entry and `docs/` regeneration.

#### Explicitly Out Of Scope

- Adding new env vars, or renaming/changing any existing default or semantics (pure consolidation).
- Migrating the `SPECMGR_PLANTUML_*` trio's read sites in `plantuml/chain.py` to the registry accessor -- impossible while `plantuml/` stays import-free (the dependency-direction invariant, ADR 7a626b12); those read sites keep their own direct `os.environ` reads.
- The hosting-platform probe vars (`KUBERNETES_SERVICE_HOST`, `RAILWAY_PROJECT_ID`, `RENDER` in `commands/mcp.py`) -- not specmgr-defined, already declared out of scope by feat-126.
- Auto-generating the README "Environment Variables" prose or the `server.json` manifest (both stay hand-maintained, now test-checked against the registry); introducing a new doc-generation stage.
- Changes to `.env`/dotenv loading behaviour (`cli.py`'s module-level `load_dotenv`, the `SPECMGR_TESTS_NO_DOTENV` sentinel semantics).
- Publishing `server.json` changes to the MCP Registry (release process's job).
- Any other open issue (only #208).

### Dependencies

#### Depends On

- FEAT feat-126-server-json-env-drift (GitHub issue #126, status: review): the `server.json` manifest state and read-site scan shapes this feature extends; this feature's branch should include it.
- ADR 750842b2-aca4-4649-ba0c-855ec8e1f505 (feat-134): `SPECMGR_SIMILARITY_DISABLED` semantics.
- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (feat-187): `SPECMGR_FEAT_WARMUP_DISABLED` semantics.
- ADR 7a626b12-b189-4561-a51d-ffb2e9e193b4 (feat-185): the plantuml trio's first-set-wins policy and `plantuml/`'s import-free invariant.

#### Blocks

- None known.

### Design Notes

**Registry placement.** A new private module `general/tools/_envregistry.py`. The registry is not itself an MCP tool, but `general/tools/` is the established home for the package's shared, private, non-MCP support modules: `_domains.py` (feat-125/feat-134 -- the per-domain adapter registry in exactly the "any domain can register" shape issue #208 asks for, explicitly documented as "no `mcp` dependency here, like every other private `general/tools/` support module"), `_doc_paths.py`, `_doc_cache.py`, `_lock.py`, `_path_safety.py`, `_startup_warmup.py`, `_embedding*.py`. Non-tool code already imports from there (`general/resources/config.py` imports env-var name constants from `tools/_doc_paths.py`, `tools/_embedding.py`, `tools/_startup_warmup.py`), and the migrated base-dir resolvers live there too, so the diffs stay local. The `general/` root has no private-module precedent (subpackages only), `general/models/` is for pydantic data models, not behaviour, and a single-module subpackage (e.g. `general/envvar/`) would be heavier than the convention.

**The plantuml carve-out.** `plantuml/` is import-free (no `biz.dfch.specmgr.*` imports anywhere; the dependency direction is always specmgr-domain -> `plantuml`, ADR 7a626b12), so `plantuml/chain.py`'s own read sites of `SPECMGR_PLANTUML_JAR`/`_BIN`/`_URL` keep their direct `os.environ` reads (behind the existing injectable `env` mapping). The trio is still registered in the registry -- by its uc-domain consumer (e.g. `uc/tools/validate_plantuml.py`, importing `plantuml/chain.py`'s own `ENV_VAR_*` constants), with owner `plantuml`/`uc` -- so the registry stays complete for documentation tracking and the Phase 150 scan-based completeness test covers the `plantuml/` read sites like any others. No behaviour change: the trio is presence-based with no defaults, so the registry adds nothing to its selection semantics (first-set-wins, no fall-through).

**Record shape.** A frozen dataclass `EnvVar`: `name` (str), `default` (str | None; None = presence-based/no default), `description` (str, non-empty), `owner` (str, the registering domain/feature), plus optional `choices` (tuple, for manifest `choices` fidelity) and `empty_falls_back_to_default` (bool, the documented `FASTEMBED_CACHE_PATH` micro-deviation).

**Accessor.** `get(name) -> str | None` (raw environment read, at call time) and `get_with_default(name) -> str` (environment read, registered default when unset). Today's read sites keep their exact semantics: set-but-empty stays set, except where the code already falls back (`FASTEMBED_CACHE_PATH`). Registration happens at import time of each owning module (each domain's `_paths.py`/gate module registers its own vars), so the registry is complete by the time any server/CLI entry point runs -- no new central import wiring. Typer options: the `envvar=` wiring stays Typer's, but the Python-side `default=` values are sourced from the registry, so the manifest/README default-fidelity tests have one code-side authority.

**Documentation tracking.** Two new tests, both registry-anchored: (1) completeness -- reusing feat-126's read-site scan shapes, asserting the scanned name set equals the registry name set (catches unregistered reads and stale registrations, failures naming the specific var in both directions); (2) coverage -- every registry name appears in the README's "Environment Variables" section and in `server.json`'s `environmentVariables` (with default/`choices` fidelity). The README prose and the manifest stay hand-maintained (repo precedent, feat-7 note) -- the registry is the authority the tests check against, not a generator.

**Phase discipline.** Every phase ends with the full quality gate -- `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, plus the doc-drift checks the phase touches (`specmgr docs` expected no-op except the final phase) -- and exactly one Conventional Commit. Phases are deliberately small (the 8-phase split) so each fits one implementer session with bounded context.

### Related Decisions

- FEAT feat-126-server-json-env-drift (GitHub issue #126): the `server.json` env-drift detection this feature extends (registry-anchored).
- FEAT feat-51-mcp-cwd (GitHub issue #51): the `specmgr://config` resource that reports the same vars' presence.
- ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc (feat-125): the single-source-of-truth registry pattern this feature applies to env vars.
- ADR 750842b2-aca4-4649-ba0c-855ec8e1f505 (feat-134): `SPECMGR_SIMILARITY_DISABLED` semantics.
- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (feat-187): `SPECMGR_FEAT_WARMUP_DISABLED` semantics.
- ADR 7a626b12-b189-4561-a51d-ffb2e9e193b4 (feat-185): the plantuml trio's first-set-wins policy and `plantuml/`'s import-free invariant.

### Task List

#### Phase 100: Registry core

- [ ] Task 100.100: Implement the registry module `general/tools/_envregistry.py` (`EnvVar` record, `register`, `get`, `get_with_default`, duplicate/conflict detection) per Design Notes (REQ-001/REQ-002).
- [ ] Task 100.110: Unit tests for the registry (default insertion, presence-based, set-but-empty, unknown name, conflicting re-registration).
- [ ] Task 100.120: Phase-end gate (full quality gate per Design Notes) plus exactly one Conventional Commit.

#### Phase 110: Register all env vars

- [ ] Task 110.100: Register all 12 `SPECMGR_*` vars at their owning modules with faithful defaults/descriptions/owners (`SPECMGR_ADR_DIR` in `adr/tools/_paths.py`, `SPECMGR_DOCS_DIR` in `general/tools/_doc_paths.py`, `SPECMGR_FEAT_DIR` in `feat/tools/_paths.py`, the three Typer MCP vars in `commands/mcp.py`, `SPECMGR_SIMILARITY_DISABLED` in `general/tools/_embedding.py`, `SPECMGR_FEAT_WARMUP_DISABLED` in `general/tools/_startup_warmup.py`, the plantuml trio in the uc-domain consumer, `SPECMGR_TESTS_NO_DOTENV` in `cli.py`) (REQ-001, ACC-001).
- [ ] Task 110.110: Register `FASTEMBED_CACHE_PATH` at its read site in `general/resources/config.py` (owner: general/similarity, with the `empty_falls_back_to_default` flag) (REQ-001, ACC-001).
- [ ] Task 110.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 120: Migrate the base-dir read sites

- [ ] Task 120.100: Migrate the base-dir read sites (`SPECMGR_ADR_DIR`, `SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR`) to the registry accessor (REQ-002, ACC-002).
- [ ] Task 120.110: Regression tests: base-dir resolution behaviour unchanged for default/override/set-but-empty.
- [ ] Task 120.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 130: Migrate the presence-gate read sites

- [ ] Task 130.100: Migrate the presence-gate read sites (`SPECMGR_SIMILARITY_DISABLED`, `SPECMGR_FEAT_WARMUP_DISABLED`, `SPECMGR_TESTS_NO_DOTENV`) to the registry accessor (REQ-002, ACC-002).
- [ ] Task 130.110: Verify `plantuml/chain.py`'s trio read sites are untouched (the import-free carve-out per Design Notes) and their registrations (Task 110.100) are complete.
- [ ] Task 130.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 140: Typer defaults + config read + identity check

- [ ] Task 140.100: Source the three Typer MCP option defaults (`SPECMGR_MCP_TRANSPORT`/`HOST`/`PORT` in `commands/mcp.py`) from the registry; keep the `envvar=` wiring.
- [ ] Task 140.110: Route `FASTEMBED_CACHE_PATH`'s `specmgr://config` read in `general/resources/config.py` through the registry accessor (preserving the empty-value-to-default fallback and the no-`mkdir` side effect).
- [ ] Task 140.120: Verify `specmgr://config`'s JSON output is byte-identical before and after (ACC-005 evidence).
- [ ] Task 140.130: Phase-end gate plus exactly one Conventional Commit.

#### Phase 150: Registry-to-source completeness test

- [ ] Task 150.100: Implement the completeness test (feat-126 read-site scan shapes; the set of read names in `src/` equals the registry name set; failures name the specific vars in both directions) (REQ-003, ACC-003).
- [ ] Task 150.110: Mutation verification: register a bogus var -> the test fails naming it; unregister a read var -> the test fails naming it; revert.
- [ ] Task 150.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 160: Documentation coverage test

- [ ] Task 160.100: Implement the coverage test (every registered var appears in the README "Environment Variables" section and in `server.json`'s `environmentVariables`, with default/`choices` fidelity) (REQ-004, ACC-004).
- [ ] Task 160.110: Fix any documentation gaps the test surfaces in `README.md`/`server.json`.
- [ ] Task 160.120: Mutation verification: remove a var from the README/manifest -> the test fails naming it; revert.
- [ ] Task 160.130: Phase-end gate plus exactly one Conventional Commit.

#### Phase 170: Finalization

- [ ] Task 170.100: `CHANGELOG.md` `[Unreleased]` entry (REQ-006).
- [ ] Task 170.110: Regenerate `docs/` (`specmgr docs`), confirming no drift (REQ-006).
- [ ] Task 170.120: Final full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, doc-drift checks); tick ACC-001 through ACC-006 against the evidence; exactly one Conventional Commit.

## Progress

### Current Status

**As of 2026-10-09**: planning -- feature created from GitHub issue #208 (the issue body is an explicit draft/rough idea; the registry design above, including the `general/tools/` placement decision and the `plantuml/` import-free carve-out, is the planning interpretation to be confirmed with the maintainer). No implementation has started.

### Blockers

- None known.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-09T07:15:29.000Z - Created

Feature plan created from GitHub issue #208 ("Consolidate ENV VAR definitions"): a central env-var registry under `general/` (name + default + description + owner), every env var read site migrating to the registry accessor (except the import-free `plantuml/` package), and new registry-anchored tests pinning completeness (every read var registered) and documentation coverage (every registered var documented in the README + `server.json` with a faithful default). The task list is split into 8 small phases so each fits one implementer session, with a full quality gate at the end of every phase.

### Related PRs / Commits

- [GitHub issue #208](https://github.com/dfch/biz.dfch.SpecMgr/issues/208): the tracking issue.
