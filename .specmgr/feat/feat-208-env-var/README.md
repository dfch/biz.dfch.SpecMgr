---
classification: null
created: '2026-10-09T09:58:41.413+02:00'
id: feat-208-env-var
status: planning
type: feat
updated: '2026-10-10T15:05:05.904+02:00'
version: 1.0.0
---

# Feature: Consolidate Environment Variable Definitions into a Central Registry

## Plan

### Overview

GitHub issue #208: multiple parts of the program read `SPECMGR_*` environment variables directly (12 at planning time), which has repeatedly led to documentation errors and gaps (the root `README.md`'s "Environment Variables" section currently documents only 8 of the 12 `SPECMGR_*` vars -- the three `SPECMGR_MCP_*` live in the CLI options table, `SPECMGR_TESTS_NO_DOTENV` appears nowhere, and `FASTEMBED_CACHE_PATH` only in the "Semantic Similarity Search" section -- and the `server.json` manifest, which lists only the 12 `SPECMGR_*` vars, drifted before being caught after the fact by feat-126's drift test). This feature introduces a central environment-variable registry: a top-level cross-cutting module (`biz.dfch.specmgr._envregistry`, sibling of `_paths.py`) where each domain/feature registers the env var names it reads, with their defaults, descriptions, and owners. The registry centrally handles value loading and default insertion and becomes the single source of truth for documentation tracking -- tests pin that every env var read in `src/` is registered and documented (README "Environment Variables" section + `server.json`'s `environmentVariables`), and that every registered var is read in `src/`. Existing read sites migrate to the registry accessor with no change to var names, defaults, or read-time semantics -- no domain is broken.

Verified state at planning time (2026-10-09):

- The code reads exactly 12 `SPECMGR_*` env vars: `SPECMGR_ADR_DIR`, `SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR` (base-dir overrides with defaults), `SPECMGR_MCP_TRANSPORT`/`SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT` (Typer `envvar=` options with defaults), `SPECMGR_SIMILARITY_DISABLED`/`SPECMGR_FEAT_WARMUP_DISABLED` (presence-based gates), `SPECMGR_PLANTUML_JAR`/`SPECMGR_PLANTUML_BIN`/`SPECMGR_PLANTUML_URL` (first-set-wins sources, no defaults), and `SPECMGR_TESTS_NO_DOTENV` (test/CI sentinel, presence-based) -- the set pinned by feat-126-server-json-env-drift's drift test (status: review).
- One third-party env var is also read: `FASTEMBED_CACHE_PATH` (the model cache dir reported by `specmgr://config`).
- The README's "Environment Variables" section is hand-maintained prose (repo precedent since feat-7) and `server.json` is a hand-maintained manifest guarded by feat-126's bidirectional source-scan drift test.
- The `plantuml/` package is import-free (no `biz.dfch.specmgr.*` imports; the dependency direction is always specmgr -> `plantuml`), so the `SPECMGR_PLANTUML_*` trio's read sites in `plantuml/chain.py` cannot go through the registry accessor (see Design Notes, "The plantuml carve-out").

### Requirements

- REQ-001: A central environment-variable registry (top-level private module `biz.dfch.specmgr._envregistry`, sibling of `_paths.py`; stdlib-only, importable without triggering the `server`/third-party-`mcp` import chain) in which every env var is registered by name with its default (or a presence-based marker), a description, and an owner (domain/feature); duplicate registration of the same name with conflicting metadata fails loudly.
- REQ-002: A single registry-backed accessor used by every current `SPECMGR_*` read site in `src/` (and `FASTEMBED_CACHE_PATH`), except the import-free `plantuml/` package (which keeps its own direct `os.environ` reads behind its injectable `env` mapping): it reads the process environment at call time, inserts the registered default when unset, and preserves today's exact semantics (set-but-empty treated as set, except the four empty-fallback variables -- `SPECMGR_ADR_DIR`, `SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR`, and `FASTEMBED_CACHE_PATH`, whose read sites already fall back to the default on an empty value; the user-approved Option A decision, 2026-10-10 update entry, which supersedes the original single-variable wording).
- REQ-003: Completeness: a test asserts that every env var read in `src/` is registered (scan-based on the shared read-site scanner extracted from feat-126's drift test, generalized beyond its hardcoded `SPECMGR_` prefix) and that every registered env var is read in `src/` (no stale registrations).
- REQ-004: Documentation tracking: a test asserts that every registered env var is documented in the root `README.md`'s "Environment Variables" section and in `server.json`'s `environmentVariables` with faithful `default`/`choices`/`format` (presence-based vars carry no default), so "is every env var documented?" is a test result, not a manual audit.
- REQ-005: No domain breakage: no env var name, default, or observable behaviour change; `specmgr://config` output unchanged; the existing test suite stays green; the registry is additive.
- REQ-006: `CHANGELOG.md` gains an `[Unreleased]` entry, `docs/` is regenerated (`specmgr docs`) without drift, and `AGENTS.md`'s structural notes are updated to name the registry module (hand-maintained, so this needs an explicit task).

### Acceptance Criteria

- [ ] ACC-001: The registry module exists at `biz/dfch/specmgr/_envregistry.py` (stdlib-only, import-graph-pinned) and all 12 `SPECMGR_*` vars (plus `FASTEMBED_CACHE_PATH`) are registered with defaults faithful to the code (presence-based vars carry no default).
- [ ] ACC-002: Every env var read site in `src/` reads through the registry accessor, except the import-free `plantuml/` package (its trio registered by its uc-domain consumer, read sites unchanged); the Typer MCP options source their defaults from the registry, verified by the Phase 160 coverage test, which reuses the shared helper's Typer `Annotated` default-literal extraction to compare the three options' `default=` values against the registry.
- [ ] ACC-003: The registry-to-source completeness test is green: every read var registered, every registered var read; a manual mutation (register a bogus var / unregister a read one) fails it naming the var, then is reverted.
- [ ] ACC-004: The documentation-coverage test is green: every registered var appears in the README "Environment Variables" section and in `server.json`'s `environmentVariables` with faithful `default` (presence-based vars carry none), `choices`, and `format`; a manual mutation fails it naming the var, then is reverted.
- [ ] ACC-005: Behaviour unchanged: the full quality gate is green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`) and `specmgr://config`'s JSON output is byte-identical before and after the migration (pinned by the golden-fixture comparison test, Tasks 110.115/140.120).
- [ ] ACC-006: The `CHANGELOG.md` `[Unreleased]` entry, the regenerated `docs/`, and the `AGENTS.md` structural-notes update are committed inside the feature's commits.

### Scope

#### Included

- The central registry module and accessor at top level (`biz.dfch.specmgr._envregistry`, sibling of `_paths.py`; cross-cutting, stdlib-only, no `mcp` import).
- Registration of all 12 `SPECMGR_*` env vars plus `FASTEMBED_CACHE_PATH` (name, default/presence marker, description, owner, manifest `format` where present) -- the plantuml trio registered by its uc-domain consumer.
- Migration of every env var read site in `src/` except the import-free `plantuml/` package to the registry-backed accessor (including the three Typer `envvar=` options' defaults).
- New tests: registry-to-source completeness drift and documentation coverage (README "Environment Variables" + `server.json` manifest, `default`/`choices`/`format` fidelity).
- The shared read-site scanner extracted from feat-126's drift test (`tests/test_server_json.py`), which the new completeness test uses and feat-126's own test refactors onto.
- The pre-migration `specmgr://config` golden fixture (Task 110.115) and its byte-comparison test (Task 140.120).
- Corrections to any documentation gaps the new tests surface (the Overview's known set first).
- The `CHANGELOG.md` entry, the `docs/` regeneration, and the `AGENTS.md` structural-notes update.

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

**Registry placement.** A new top-level private module `biz.dfch.specmgr/_envregistry.py` (sibling of `_paths.py`, the existing top-level private-module precedent). The deciding constraint is import-chain safety in a `[cli]`-only install (no `mcp` extra): the registry must be importable at module level from `cli.py` and `commands/mcp.py` (import-time registration of their own vars, Typer option defaults sourced from it), and neither of those modules may trigger the `server`/third-party-`mcp` chain. The originally drafted home, `general/tools/_envregistry.py`, fails this: `general/tools/__init__.py` eagerly imports all ten `@mcp.tool()` modules, each of which imports `server`, which imports the third-party `mcp` package -- so any module-level `from ...general.tools._envregistry import ...` in the CLI path would pull the whole chain in and crash every CLI command (`specmgr version` included) in a `[cli]`-only install, and would defeat the deliberate lazy `server` import + friendly "install the `mcp` extra" error in `commands/mcp.py`. The `_domains.py` "no `mcp` dependency here" precedent is true only in the file-level sense (that file never imports `mcp`), which is exactly the sense that fails here -- and CI (`--all-extras`) and the test suite cannot catch the breakage, since it surfaces only for `[cli]`-only consumers. The top-level `__init__.py` intentionally carries no imports (its docstring says so), so `biz.dfch.specmgr._envregistry`'s import chain is just itself: the module is therefore stdlib-only, and an AST import-graph test pins that (mirroring `plantuml/`'s import-free pin). Registration sites (the domain `_paths.py`/gate modules, `general/resources/config.py`, `cli.py`, `commands/mcp.py`) import it the same way in every context.

**The plantuml carve-out.** `plantuml/` is import-free (no `biz.dfch.specmgr.*` imports anywhere; the dependency direction is always specmgr-domain -> `plantuml`, ADR 7a626b12), so `plantuml/chain.py`'s own read sites of `SPECMGR_PLANTUML_JAR`/`_BIN`/`_URL` keep their direct `os.environ` reads (behind the existing injectable `env` mapping). The trio is still registered in the registry -- by its uc-domain consumer (e.g. `uc/tools/validate_plantuml.py`, importing `plantuml/chain.py`'s own `ENV_VAR_*` constants), with owner `plantuml`/`uc` -- so the registry stays complete for documentation tracking and the Phase 150 scan-based completeness test covers the `plantuml/` read sites like any others. No behaviour change: the trio is presence-based with no defaults, so the registry adds nothing to its selection semantics (first-set-wins, no fall-through).

**Record shape.** A frozen dataclass `EnvVar`: `name` (str), `default` (str | None; None = presence-based/no default), `description` (str, non-empty), `owner` (str, the registering domain/feature), plus optional `format` (str | None, mirroring the manifest's `format` -- `number` on `SPECMGR_MCP_PORT`, `filepath` on the three base-dir vars and on `FASTEMBED_CACHE_PATH`; None = absent), `choices` (tuple, for manifest `choices` fidelity), and `empty_falls_back_to_default` (bool, the four-variable empty-fallback set: `SPECMGR_ADR_DIR`, `SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR`, `FASTEMBED_CACHE_PATH` -- the user-approved Option A decision, 2026-10-10 update entry).

**Accessor.** `get(name) -> str | None` (raw environment read, at call time) and `get_with_default(name) -> str` (environment read, registered default when unset). Today's read sites keep their exact semantics: set-but-empty stays set, except where the code already falls back to the default on an empty value -- the four empty-fallback variables `SPECMGR_ADR_DIR`/`SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR` (`Path(value) if value else DEFAULT`) and `FASTEMBED_CACHE_PATH` (`value or default`); separately, `cli.py`'s dotenv-sentinel check is a truthiness test (`if os.environ.get(NO_DOTENV_SENTINEL):`), so a set-but-empty `SPECMGR_TESTS_NO_DOTENV` behaves as absent there (presence-based, no default -- the flag does not apply to it). Registration happens at import time of each owning module (each domain's `_paths.py`/gate module registers its own vars), so the registry is complete by the time any server/CLI entry point runs -- no new central import wiring. Typer options: the `envvar=` wiring stays Typer's, but the Python-side `default=` values are sourced from the registry, so the manifest/README default-fidelity tests have one code-side authority.

**Documentation tracking.** Two new tests, both registry-anchored, on top of a shared read-site scanner extracted from feat-126's drift test (Task 150.100; feat-126's test refactors onto it with unchanged behaviour): (1) completeness -- read-site discovery generalized from feat-126's hardcoded `SPECMGR_` prefix to the quoted form of every registered name (so the third-party `FASTEMBED_CACHE_PATH` is visible to the scan) union the `SPECMGR_` prefix net (so unregistered specmgr vars are still caught), minus the documented hosting-probe exclusion set; asserting the scanned name set equals the registry name set (catches unregistered reads and stale registrations, failures naming the specific var in both directions); (2) coverage -- every registry name appears in the README's "Environment Variables" section and in `server.json`'s `environmentVariables` (with `default`/`choices`/`format` fidelity), and the three Typer MCP options' `default=` values equal the registry's (the shared helper's Annotated default-literal extraction). A third, identity-pinning anchor: the pre-migration `specmgr://config` golden fixture (Task 110.115) that Task 140.120 compares byte-for-byte (temp-dir prefix normalized) against the post-migration output. The README prose and the manifest stay hand-maintained (repo precedent, feat-7 note) -- the registry is the authority the tests check against, not a generator.

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

- [x] Task 100.100: Implement the registry module `biz/dfch/specmgr/_envregistry.py` (top-level, stdlib-only per Design Notes; `EnvVar` record with `name`/`default`/`description`/`owner`/`format`/`choices`/`empty_falls_back_to_default`, `register`, `get`, `get_with_default`, duplicate/conflict detection) per Design Notes (REQ-001/REQ-002).
- [x] Task 100.110: Unit tests for the registry (default insertion, presence-based, set-but-empty, unknown name, conflicting re-registration), plus the import-graph pin: an AST test that `_envregistry.py` imports stdlib only (mirroring `plantuml/`'s import-free pin), so a `[cli]`-only import cannot reach `mcp`/`server` (REQ-001, ACC-001).
- [ ] Task 100.120: Phase-end gate (full quality gate per Design Notes) plus exactly one Conventional Commit.

#### Phase 110: Register all env vars

- [x] Task 110.100: Register all 12 `SPECMGR_*` vars at their owning modules with faithful defaults/descriptions/owners and the manifest's `format`s (`number` on `SPECMGR_MCP_PORT`, `filepath` on the three base-dir vars) (`SPECMGR_ADR_DIR` in `adr/tools/_paths.py`, `SPECMGR_DOCS_DIR` in `general/tools/_doc_paths.py`, `SPECMGR_FEAT_DIR` in `feat/tools/_paths.py`, the three Typer MCP vars in `commands/mcp.py`, `SPECMGR_SIMILARITY_DISABLED` in `general/tools/_embedding.py`, `SPECMGR_FEAT_WARMUP_DISABLED` in `general/tools/_startup_warmup.py`, the plantuml trio in the uc-domain consumer, `SPECMGR_TESTS_NO_DOTENV` in `cli.py`) (REQ-001, ACC-001).
- [x] Task 110.110: Register `FASTEMBED_CACHE_PATH` at its read site in `general/resources/config.py` (owner: general/similarity, with the `empty_falls_back_to_default` flag) (REQ-001, ACC-001).
- [x] Task 110.115: Capture the pre-migration `specmgr://config` golden: build the resource payload under a controlled environment (temp-dir CWD, none of the 13 registered vars set, the standard all-extras install so the `fastembed` spec lookup is stable) and commit the JSON as a test fixture under `tests/fixtures/` (the `base_dir`/`cache_dir` fields are absolute -- the comparison normalizes the temp-dir prefix); the capture must predate Phase 120's base-dir migration (REQ-005, ACC-005).
- [ ] Task 110.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 120: Migrate the base-dir read sites

- [ ] Task 120.100: Migrate the base-dir read sites (`SPECMGR_ADR_DIR`, `SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR`) to the registry accessor (REQ-002, ACC-002).
- [ ] Task 120.110: Regression tests: base-dir resolution behaviour unchanged for default/override/set-but-empty.
- [ ] Task 120.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 130: Migrate the presence-gate read sites

- [ ] Task 130.100: Migrate the presence-gate read sites (`SPECMGR_SIMILARITY_DISABLED`, `SPECMGR_FEAT_WARMUP_DISABLED`, `SPECMGR_TESTS_NO_DOTENV`) to the registry accessor, keeping `cli.NO_DOTENV_SENTINEL` a module-level constant of its current value (it is drift-pinned against `conftest.NO_DOTENV_SENTINEL` in `tests/plantuml/test_source_gate.py`'s `test_cli_and_conftest_sentinel_names_agree`); the registry's `SPECMGR_TESTS_NO_DOTENV` entry sources its name from the constant (the constant stays the authority), and `tests/conftest.py`'s own copy stays unchanged (tests/ are outside the registry's scope) (REQ-002, ACC-002).
- [ ] Task 130.110: Verify `plantuml/chain.py`'s trio read sites are untouched (the import-free carve-out per Design Notes) and their registrations (Task 110.100) are complete.
- [ ] Task 130.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 140: Typer defaults + config read + identity check

- [ ] Task 140.100: Source the three Typer MCP option defaults (`SPECMGR_MCP_TRANSPORT`/`HOST`/`PORT` in `commands/mcp.py`) from the registry; keep the `envvar=` wiring.
- [ ] Task 140.110: Route `FASTEMBED_CACHE_PATH`'s `specmgr://config` read in `general/resources/config.py` through the registry accessor (preserving the empty-value-to-default fallback and the no-`mkdir` side effect).
- [ ] Task 140.120: Test that `specmgr://config`'s post-migration JSON output is byte-identical to the Phase 110 golden fixture (temp-dir prefix normalized) (ACC-005 evidence).
- [ ] Task 140.130: Phase-end gate plus exactly one Conventional Commit.

#### Phase 150: Registry-to-source completeness test

- [ ] Task 150.100: Extract the read-site scanner from feat-126's drift test (`tests/test_server_json.py`: the four read shapes, the docstring/comment blanking, the default-presence classifier, the Typer `Annotated` default scan) into a shared test helper (e.g. `tests/_env_scan.py`), parameterizing the name pattern (default: today's `SPECMGR_` prefix net, so feat-126's test keeps byte-identical behaviour) and extending the Annotated scan to also capture the default literal; refactor `tests/test_server_json.py` onto the helper -- regression: feat-126's suite is green before and after with unchanged assertions (REQ-003, ACC-003).
- [ ] Task 150.105: Implement the completeness test on the shared helper: read-site discovery = the quoted form of every registered name (so `FASTEMBED_CACHE_PATH` is visible) union the `SPECMGR_` prefix net, minus the documented hosting-probe exclusion set; assert the discovered set equals the registry name set, failures naming the specific vars in both directions (REQ-003, ACC-003).
- [ ] Task 150.110: Mutation verification: register a bogus var -> the test fails naming it; unregister a read var -> the test fails naming it; revert.
- [ ] Task 150.120: Phase-end gate plus exactly one Conventional Commit.

#### Phase 160: Documentation coverage test

- [ ] Task 160.100: Implement the coverage test (every registered var appears in the README "Environment Variables" section and in `server.json`'s `environmentVariables`, with `default`/`choices`/`format` fidelity; plus the three Typer MCP options' `default=` values equal the registry's, via the shared helper's Annotated default-literal extraction) (REQ-004, ACC-002/ACC-004).
- [ ] Task 160.110: Fix the documentation gaps -- the Overview's known set first (the README section gains `SPECMGR_MCP_TRANSPORT`/`SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`, `SPECMGR_TESTS_NO_DOTENV`, and `FASTEMBED_CACHE_PATH`; a registered third-party var is intended in both the section and the manifest, so `server.json`'s `environmentVariables` gains `FASTEMBED_CACHE_PATH`), plus anything else the test surfaces (REQ-004, ACC-004).
- [ ] Task 160.120: Mutation verification: remove a var from the README/manifest -> the test fails naming it; revert.
- [ ] Task 160.130: Phase-end gate plus exactly one Conventional Commit.

#### Phase 170: Finalization

- [ ] Task 170.100: `CHANGELOG.md` `[Unreleased]` entry (REQ-006).
- [ ] Task 170.110: Regenerate `docs/` (`specmgr docs`), confirming no drift (REQ-006).
- [ ] Task 170.115: Update `AGENTS.md`'s structural notes: name `biz.dfch.specmgr._envregistry` (top-level, sibling of `_paths.py`) as the single source of truth for env-var names/defaults, and adjust the `general/tools/` private-module enumeration accordingly (REQ-006).
- [ ] Task 170.120: Final full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, doc-drift checks); tick ACC-001 through ACC-006 against the evidence; exactly one Conventional Commit.

## Progress

### Current Status

**As of 2026-10-10**: Phase 110 (Register all env vars) done and gate-green, pending its commit -- all 13 env vars (the 12 `SPECMGR_*` vars plus `FASTEMBED_CACHE_PATH`) registered at import time in their nine owning modules, with the three base-dir modules deriving their pre-existing `DEFAULT_*` constants from the registry records (registry = single authority for the default), the user-approved Option A decision in force (the four empty-fallback vars carry `empty_falls_back_to_default=True`, the registry docstrings and this plan's REQ-002/Design Notes corrected to name them), and the pre-migration `specmgr://config` golden captured at `tests/fixtures/config-golden/specmgr-config.pre-migration.json` (temp-dir CWD, none of the 13 vars set, all-extras install; the Phase 140 byte-comparison contract is documented in the fixture's sibling README). The full phase-end quality gate is green (4456 passed, 16 skipped vs. the 4453/16 baseline after Phase 100; `ruff format --check`/`ruff check`/`vulture` clean, no whitelist additions; `specmgr docs` regenerated, `docs/MCP.md` untouched). No read site changed in this phase -- the migration is Phases 120-140, and `specmgr://config`'s output is byte-identical to the golden.

### Blockers

- None known.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-10T15:05:05.904+02:00 - Phase 110: Register all env vars (Option A in force)

Tasks 110.100/110.110/110.115: all 13 env vars (the 12 `SPECMGR_*` vars plus `FASTEMBED_CACHE_PATH`) are now registered at import time in their nine owning modules, with `default`/`format`/`choices` pinned verbatim to `server.json`'s `environmentVariables` (verified by a scripted comparison) and the three base-dir modules deriving their pre-existing constants from the registry records -- `adr/tools/_paths.py` (`SPECMGR_ADR_DIR`, `owner="adr"`, `format="filepath"`, `DEFAULT_ADR_DIR = Path(_adr_dir_var.default)`), `general/tools/_doc_paths.py` (`SPECMGR_DOCS_DIR`, `owner="general"`, `format="filepath"`, `DEFAULT_DOCS_ROOT = Path(_docs_dir_var.default)`), `feat/tools/_paths.py` (`SPECMGR_FEAT_DIR`, `owner="feat"`, `format="filepath"`, `DEFAULT_FEAT_DIR = Path(_feat_dir_var.default)`; each derivation carries a program-invariant type-narrowing assert, conventions Rule 2, mirroring `_envregistry.get_with_default`'s own), `commands/mcp.py` (the three Typer MCP vars, `owner="cli"`, `SPECMGR_MCP_PORT` with `format="number"` and the str default `"8000"` -- Phase 140 converts it), `general/tools/_embedding.py` (`SPECMGR_SIMILARITY_DISABLED`, presence-based), `general/tools/_startup_warmup.py` (`SPECMGR_FEAT_WARMUP_DISABLED`, presence-based), `uc/tools/validate_plantuml.py` (the plantuml trio via its own `plantuml.chain` `ENV_VAR_JAR`/`ENV_VAR_BIN`/`ENV_VAR_URL` constants, `owner="plantuml/uc"`, presence-based -- `validate_plantuml.py` is the one uc-domain consumer that imports `plantuml.chain`; the trio's read sites in `plantuml/chain.py` are untouched per the import-free carve-out), `cli.py` (`SPECMGR_TESTS_NO_DOTENV` sourced from the existing `NO_DOTENV_SENTINEL` constant, which stays the authority, registered next to the constant and before the `_load_default_dotenv()` call as today), and `general/resources/config.py` (`FASTEMBED_CACHE_PATH` at its read site, `owner="general/similarity"`, `format="filepath"`, default = the code's own fallback expression `str(Path(tempfile.gettempdir()) / "fastembed_cache")` evaluated at registration). **Option A (user-approved, supersedes the plan's letter):** the plan's REQ-002 parenthetical named only `FASTEMBED_CACHE_PATH` as the empty-fallback deviation, but the verified code semantics make it a four-variable set -- the three base-dir vars read `Path(value) if value else DEFAULT` (set-but-empty falls back to the default, same shape as `FASTEMBED_CACHE_PATH`'s `value or default`), `cli.py`'s sentinel check is a truthiness test (`if os.environ.get(NO_DOTENV_SENTINEL):` -- set-but-empty behaves as absent, a presence-based var with no default so the flag does not apply to it), and everything else (`_embedding`/`_startup_warmup` gates, the plantuml trio, `config.py`'s presence checks) is `os.environ.get(name) is not None` (set-but-empty stays set). `empty_falls_back_to_default=True` is therefore set on exactly `SPECMGR_ADR_DIR`/`SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`/`FASTEMBED_CACHE_PATH`; the registry's `EnvVar.empty_falls_back_to_default` field docstring, `get_with_default`'s docstring, and this plan's REQ-002 + Design Notes ("Record shape", "Accessor") bullets are corrected to name the four-variable set. `commands/mcp.py` registers its three vars with the same quoted literals the `envvar=` options carry (no name constant introduced: the `envvar=` literal is the feat-126 drift test's shape-4 read-site anchor, and a shape-1 constant assignment would change that test's scanned output; the register call itself is invisible to all four of the drift test's read shapes, verified). Tests: `tests/test_envregistry.py`'s five full-registry-content assertions (incl. the flagged `test_is_empty_for_a_fresh_registry` landmine) now clear the registry after `_IsolatedRegistry`'s snapshot (Phase 110's real import-time registrations are present in the process once any owning module imports during collection; `tearDown` restores them), and the new `tests/test_envregistry_registration.py` (3 tests) explicitly imports all nine owning modules, pins the registry to exactly the 13 names (documented assumption: no other test module leaks test-only registrations -- `_IsolatedRegistry` cleans up), pins each record's `default`/`format`/`choices`/`empty_falls_back_to_default`/`owner` against the Phase 110 table, and pins the three derived `DEFAULT_*` constants byte-identical (`Path("docs/adr")`/`Path("docs")`/`Path(".specmgr/feat")`). Golden (Task 110.115): the pre-migration `specmgr://config` payload captured through the mcp SDK's own resource serialization path (`pydantic_core.to_json(result, fallback=str, indent=2).decode()`) under a fresh temp-dir CWD with none of the 13 vars set (the eight non-`cli` owning modules imported first so the registry is full; `cli` deliberately not imported -- no dotenv side effects; `SPECMGR_TESTS_NO_DOTENV` popped by its literal name) and committed as `tests/fixtures/config-golden/specmgr-config.pre-migration.json` (2329 bytes, T0's absolute paths raw, `cache_dir` = the process temp dir's `<tempdir>/fastembed_cache` as today, `env_var_set`/`disabled`/`set` all `false`, `selected: "none"`, `feat_warmup_disabled: false`), with a sibling `tests/fixtures/config-golden/README.md` documenting the capture conditions and the Phase 140 byte-comparison contract (Task 140.120 normalizes the temp-dir prefixes). No read site changed in this phase (the migration is Phases 120-140); `specmgr docs` regenerated (`docs/api/biz.dfch.specmgr._envregistry.md` for the docstring corrections, `docs/GENERATED.md`'s test-file count 419 -> 420), `docs/MCP.md` untouched; the full gate is green (4456 passed, 16 skipped vs. the 4453/16 baseline; `ruff format --check`/`ruff check`/`vulture` clean, no whitelist additions), pending the phase's Conventional Commit.

#### 2026-10-10T12:19:20.168+02:00 - Phase 100: Registry core implemented

Tasks 100.100/100.110: the stdlib-only registry module `src/biz/dfch/specmgr/_envregistry.py` (top-level, sibling of `_paths.py`, per the Design Notes "Registry placement" decision): the frozen `EnvVar` record (`name`/`default`/`description`/`owner`/`format`/`choices`/`empty_falls_back_to_default`, with `__post_init__` invariants incl. flag-requires-non-None-default), `register` (idempotent for identical metadata; a conflicting re-registration fails loudly with an `AssertionError` naming the var and every conflicting field, leaving the stored record unchanged), `get(name) -> str | None` (raw environment read at call time, no default insertion -- the presence-based accessor; an unknown name is a loud failure naming it), `get_with_default(name) -> str` (environment read at call time, the registered default inserted only when unset; a set-but-empty value stays set unless the entry's `empty_falls_back_to_default` flag carries the documented `FASTEMBED_CACHE_PATH` micro-deviation; a presence-based var read while unset fails loudly directing the caller to `get`), and `all_vars()` (the registration-order snapshot, the read surface for the Phase 150/160 registry-backed tests). `tests/test_envregistry.py` adds 25 tests covering default insertion, presence-based, set-but-empty (both flag states), unknown-name loud failures, idempotent and conflicting re-registration, the record invariants, and the import-graph pin: an AST walk asserting every import in `_envregistry.py` (top-level and nested) resolves to a stdlib module via `sys.stdlib_module_names` (dotted imports by top-level package, relative imports resolved against the module's own package), mirroring `plantuml/`'s import-free pin in `tests/plantuml/test_structure.py` (REQ-001, ACC-001). The phase is purely additive (REQ-005): the registry starts empty, nothing in `src/` calls it yet, and the full quality gate is green (4453 passed, 16 skipped vs. the 4428/16 baseline; `ruff format --check`/`ruff check`/`vulture` clean, no whitelist additions -- every `EnvVar` field is attribute-read in `src/`). Adding the module/test file does drift `specmgr docs` (the new `docs/api/biz.dfch.specmgr._envregistry.md` page, its `docs/api/README.md` index entry, and `docs/GENERATED.md`'s test-file count 418 -> 419), so the regeneration is part of this phase's change set (the Design Notes' "expected no-op except the final phase" predates the first module's arrival); `docs/MCP.md` is byte-identical. Task 100.120's commit is pending (the orchestrator performs it).

#### 2026-10-10T05:59:36.000Z - Plan refined

Planning review (feat-refiner) folded into the plan: (E1) the registry is relocated from the drafted `general/tools/_envregistry.py` to top-level `biz.dfch.specmgr/_envregistry.py` -- `general/tools/__init__.py`'s eager imports of the ten `@mcp.tool()` modules would pull the `server`/third-party-`mcp` chain into `cli.py`/`commands/mcp.py`'s module level and crash every CLI command in a `[cli]`-only install; the module is stdlib-only with an AST import-graph pin (REQ-001, ACC-001, Tasks 100.100/100.110). (G1/G2) the Phase 150 completeness test is built on a shared read-site scanner extracted from feat-126's drift test (Task 150.100; that test refactors onto it with unchanged assertions), generalized from the hardcoded `SPECMGR_` prefix to registered-name-driven discovery plus the `SPECMGR_` net (Task 150.105). (G3) a pre-migration `specmgr://config` golden fixture is captured in Task 110.115 (predating Phase 120's base-dir migration) and compared byte-for-byte in Task 140.120 (ACC-005). (G4) `AGENTS.md`'s structural notes gain an explicit update task (Task 170.115; REQ-006/ACC-006). (G5) Phase 130 keeps `cli.NO_DOTENV_SENTINEL` a module-level constant of its current value, honouring the drift pin in `tests/plantuml/test_source_gate.py` (Task 130.100). (I1) the `EnvVar` record gains a `format` field mirroring the manifest (`number`/`filepath`), and the documentation fidelity becomes `default`/`choices`/`format` (REQ-004, ACC-004, Tasks 110.100/160.100). (I2) the Overview now enumerates the known README/manifest documentation gaps, and Task 160.110 is a check-off of that set. (I3) ACC-002's Typer-default verification names its mechanism (the shared helper's Annotated default-literal extraction, Task 160.100). The review also surfaced one defect outside this plan, noted here for tracking only: feat-177-list-ref-feat references a non-existent `FEAT feat-1-frontend-technology-decision` (no edit in this feature).

#### 2026-10-09T07:15:29.000Z - Created

Feature plan created from GitHub issue #208 ("Consolidate ENV VAR definitions"): a central env-var registry under `general/` (name + default + description + owner), every env var read site migrating to the registry accessor (except the import-free `plantuml/` package), and new registry-anchored tests pinning completeness (every read var registered) and documentation coverage (every registered var documented in the README + `server.json` with a faithful default). The task list is split into 8 small phases so each fits one implementer session, with a full quality gate at the end of every phase.

### Related PRs / Commits

- [GitHub issue #208](https://github.com/dfch/biz.dfch.SpecMgr/issues/208): the tracking issue.
