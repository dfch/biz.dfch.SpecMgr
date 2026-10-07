---
classification: null
created: '2026-10-07T21:21:13.282+02:00'
id: feat-126-server-json-env-drift
status: planning
type: feat
updated: '2026-10-07T21:36:15.940+02:00'
version: 1.0.0
---

# Feature: server.json Environment-Variable Drift Detection

## Plan

### Overview

GitHub issue #126: `server.json`'s `environmentVariables` array (the MCP registry manifest) has drifted from the set of `SPECMGR_*` environment variables the code actually reads — `SPECMGR_DOCS_DIR` and `SPECMGR_FEAT_DIR` were added by hand after the fact, and no regression test prevents recurrence. This feature (a) completes the manifest — the two still-missing entries `SPECMGR_SIMILARITY_DISABLED` and `SPECMGR_FEAT_WARMUP_DISABLED` — and (b) adds a bidirectional drift regression test with the source as the single source of truth: every `SPECMGR_*` environment variable read in `src/` must appear in `server.json`, and every `server.json` entry must be read in `src/`.

Verified state at planning time (2026-10-07):

- The code reads exactly 8 `SPECMGR_*` environment variables: `SPECMGR_MCP_TRANSPORT`, `SPECMGR_MCP_HOST`, `SPECMGR_MCP_PORT` (the CLI `specmgr mcp` command, read as Typer `envvar=` options in `commands/mcp.py`), `SPECMGR_ADR_DIR` (`adr/tools/_paths.py`), `SPECMGR_DOCS_DIR` (`general/tools/_doc_paths.py`), `SPECMGR_FEAT_DIR` (`feat/tools/_paths.py`) — each as a `_*_ENV_VAR = "SPECMGR_..."` string-literal constant — plus `SPECMGR_SIMILARITY_DISABLED` (the similarity feature gate) and `SPECMGR_FEAT_WARMUP_DISABLED` (the feat warmup feature gate), both presence-based.
- `server.json` lists 6 of the 8 (all except the two feature gates).
- No file under `tests/` references `server.json`.
- Nothing in `src/` (no `specmgr docs` stage, no other command) generates or edits `server.json` — it is hand-maintained, and this test will be its only guard.
- `SPECMGR_ROOT` in `src/biz/dfch/specmgr/_paths.py` is an internal variable name sharing the prefix, not an environment variable — the scan must not pick it up.

### Requirements

- REQ-001: `server.json`'s `environmentVariables` carries an entry for all 8 `SPECMGR_*` environment variables read in the source, each with a `name` and a `description` faithful to the code's behaviour, and a `default` where the code has one (the two feature gates are presence-based: no `default`, and the description states that any value set enables the gate).
- REQ-002: A new regression test, `tests/test_server_json.py`, compares the set of `SPECMGR_*` environment-variable names read in `src/` against `server.json`'s `environmentVariables` names bidirectionally: (a) every name read in the source appears in the manifest, and (b) every manifest name is read in the source; the failure message names the specific missing/extra entries.
- REQ-003: The source scan matches only environment-variable read sites — the four syntactic shapes present in the codebase: (1) string-literal assignments `= "SPECMGR_..."` (the `_*_ENV_VAR` constants), (2) `getenv("SPECMGR_..."` call sites, (3) `environ["SPECMGR_..."` / `environ.get("SPECMGR_..."` accesses, (4) Typer `envvar="SPECMGR_..."` options — and does not match docstring-prose or comment mentions nor identifiers that merely contain the prefix (e.g. `SPECMGR_ROOT`).
- REQ-004: The test runs in the default pytest suite (hence in CI and pre-commit) and requires no new dependencies (stdlib `json`, `re`, `pathlib`).
- REQ-005: `README.md`'s "Environment Variables" section is accurate for all 8 (verified at implementation time, corrected only if drifted) and `CHANGELOG.md` gains an `[Unreleased]` entry.

### Acceptance Criteria

- [ ] ACC-001: `server.json`'s `environmentVariables` names are exactly the 8 read in the source; the two feature-gate entries have no `default` and presence-based descriptions.
- [ ] ACC-002: The drift test is green against the committed source and manifest.
- [ ] ACC-003: Manual mutation of `server.json` (remove one entry → the test fails naming the missing variable; add a bogus `SPECMGR_BOGUS` → the test fails naming the extra variable) is verified during Phase 120 and reverted.
- [ ] ACC-004: The scan does not report `SPECMGR_ROOT` (`src/biz/dfch/specmgr/_paths.py`) and does not report docstring-prose mentions (pinned by the test's own negative fixture cases).
- [ ] ACC-005: The full quality gate is green: `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`.
- [ ] ACC-006: `README.md`'s "Environment Variables" section and the `CHANGELOG.md` `[Unreleased]` entry are committed inside their phase's commit.

### Scope

#### Included

- The 2 missing manifest entries (`SPECMGR_SIMILARITY_DISABLED`, `SPECMGR_FEAT_WARMUP_DISABLED`) in `server.json`.
- The bidirectional drift regression test `tests/test_server_json.py` and its source scan (test-local; no new production code path).
- `README.md` "Environment Variables" completeness correction (only if drift is found at implementation time) and the `CHANGELOG.md` entry.

#### Explicitly Out Of Scope

- Any change to how environment variables are read in `src/` (the code is the source of truth; no refactor into a shared registry module — if the scan approach proves brittle, that is a follow-up feature).
- Adding new environment variables, or changing any existing default or behaviour.
- Publishing the manifest change to the MCP Registry (release process's job).
- Generating `server.json` via `specmgr docs` or any other stage (verified absent; deliberately not introduced here).
- Any other open issue (only #126).

### Dependencies

#### Depends On

- feat-134-related-artifact-similarity (done): origin of the `SPECMGR_SIMILARITY_DISABLED` gate the manifest entry documents.
- feat-187-list-feat-timeout (done): origin of the `SPECMGR_FEAT_WARMUP_DISABLED` gate the manifest entry documents.

#### Blocks

- None known.

### Design Notes

**Source-true bidirectional scan, not an allowlist.** The issue's own fix note acknowledges the two prior additions were made by hand and that "no drift detection is in place." An expected-list inside the test would be a third hand-maintained copy — the same failure mode. Hence the test derives the expected set from `src/` read sites and compares it bidirectionally: missing entries (in code, not in manifest) and stale entries (in manifest, not in code) both fail, each naming the specific entries.

**Scan precision.** The four syntactic shapes of REQ-003 suffice for the current corpus: the five `_*_ENV_VAR` constants are plain string-literal assignments; `commands/mcp.py` declares its three variables as Typer `envvar="SPECMGR_..."` options. A line-regex over raw source text is adequate; the false-positive risk is a docstring or comment line that happens to contain one of the shapes (e.g. a docstring quoting an assignment). Phase 120 pins this with explicit negative fixture cases — `SPECMGR_ROOT` in `_paths.py` plus a synthetic docstring-quoting case — and tightens the regex if the corpus yields any false positive. Non-`SPECMGR_` environment reads in `commands/mcp.py` (`KUBERNETES_SERVICE_HOST`, `RAILWAY_PROJECT_ID`, `RENDER`) are outside the manifest's scope and never match the prefix-anchored patterns.

**Presence gates in the manifest.** Existing entries use `name`/`description` plus `default` where applicable and `choices`/`format` where useful. The two gates have no default; the manifest's shape does not require one. Hence: `name` + `description` only, with the description stating "presence-based — set to any value to …; unset by default", mirroring what `specmgr://config` reports (`similarity.disabled`, `feat_warmup_disabled`).

**Phase discipline.** Every phase ends with the full quality gate — `ruff format --check`, `ruff check`, `vulture`, the full test suite `pytest -n auto --cov=src`, plus every doc-drift check the phase touches (`specmgr docs` / `specmgr adr-toc` / `specmgr mcp-docs`; expected no-op for this feature, since no `src/` module changes) — and exactly one Conventional Commit; the phase's docs sync travels inside the same commit (repo convention, see AGENTS.md).

### Related Decisions

- feat-51-mcp-cwd (GitHub issue #51): the `specmgr://config` resource that resolves the same environment variables — the manifest descriptions stay faithful to what `specmgr://config` reports.
- ADR 750842b2-aca4-4649-ba0c-855ec8e1f505 (feat-134): semantics of `SPECMGR_SIMILARITY_DISABLED`.
- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (feat-187): semantics of `SPECMGR_FEAT_WARMUP_DISABLED`.

### Task List

#### Phase 100: Manifest completion

- [ ] Task 100.100: Add the `SPECMGR_SIMILARITY_DISABLED` and `SPECMGR_FEAT_WARMUP_DISABLED` entries to `server.json`'s `environmentVariables` (name + presence-based description, no `default`).
- [ ] Task 100.110: Verify `README.md`'s "Environment Variables" section (and the `specmgr mcp` section for the transport/host/port entries) against all 8; correct only if drifted.
- [ ] Task 100.120: `CHANGELOG.md` `[Unreleased]` entry.
- [ ] Task 100.130: Phase-end gate (full quality gate, per Design Notes): `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, and every doc-drift check the phase touches (expected no-op: no `src/` module changes) green; exactly one Conventional Commit.

#### Phase 120: Drift regression test

- [ ] Task 120.100: Implement `tests/test_server_json.py`: parse `server.json` (stdlib `json`), scan `src/` for environment-variable read sites per the four syntactic shapes of the Design Notes, assert set equality in both directions, failure message naming the specific missing/extra entries.
- [ ] Task 120.110: Pin the false-positive guards (ACC-004): `SPECMGR_ROOT` in `_paths.py` must not be reported; add the docstring-quoting negative fixture; tighten the regex if the corpus yields false positives.
- [ ] Task 120.120: Manually verify ACC-003 (mutate `server.json` both directions, observe the naming failure messages, revert).
- [ ] Task 120.130: Phase-end gate (full quality gate, per Design Notes): `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, and every doc-drift check the phase touches (expected no-op: no `src/` module changes) green; exactly one Conventional Commit.

## Progress

### Current Status

**As of 2026-10-07**: Feature created (status: planning). Manifest and scan state verified (see Overview): 6 of 8 environment variables present in `server.json`, no test coverage. Implementation pending.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T12:00:00.000Z - Created

Feature created for GitHub issue #126 (server.json environment-variable drift detection). Manifest completion (the two presence gates) is planned as Phase 100, the bidirectional source-true drift test as Phase 120.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T12:00:00.000Z - Source-true bidirectional scan, no allowlist in the test

Rather than keep an expected environment-variable list inside the test (a third hand-maintained copy), the drift test scans `src/` for environment-variable read sites (the four syntactic shapes: `_*_ENV_VAR` string-literal assignments, `getenv`, `environ` access, Typer `envvar=` options) and compares bidirectionally against `server.json`. The two missing presence gates are added to the manifest itself, not special-cased in the test.
