---
classification: null
created: '2026-10-07T21:21:13.282+02:00'
id: feat-126-server-json-env-drift
status: review
type: feat
updated: '2026-10-08T13:15:10.981+02:00'
version: 1.0.0
---

# Feature: server.json Environment-Variable Drift Detection

## Plan

### Overview

GitHub issue #126: `server.json`'s `environmentVariables` array (the MCP registry manifest) has drifted from the set of `SPECMGR_*` environment variables the code actually reads — `SPECMGR_DOCS_DIR` and `SPECMGR_FEAT_DIR` were added by hand after the fact, and no regression test prevents recurrence. This feature (a) completes and corrects the manifest — the two still-missing entries `SPECMGR_SIMILARITY_DISABLED` and `SPECMGR_FEAT_WARMUP_DISABLED`, plus the three stale pre-existing `SPECMGR_MCP_*` entries — and (b) adds a bidirectional drift regression test with the source as the single source of truth: every `SPECMGR_*` environment variable read in `src/` must appear in `server.json`, and every `server.json` entry must be read in `src/`.

Verified state at planning time (2026-10-07):

- The code reads exactly 8 `SPECMGR_*` environment variables: `SPECMGR_MCP_TRANSPORT`, `SPECMGR_MCP_HOST`, `SPECMGR_MCP_PORT` (the CLI `specmgr mcp` command, read as Typer `envvar=` options in `commands/mcp.py`), `SPECMGR_ADR_DIR` (`adr/tools/_paths.py`), `SPECMGR_DOCS_DIR` (`general/tools/_doc_paths.py`), `SPECMGR_FEAT_DIR` (`feat/tools/_paths.py`) — each as a `_*_ENV_VAR = "SPECMGR_..."` string-literal constant — plus `SPECMGR_SIMILARITY_DISABLED` (the similarity feature gate) and `SPECMGR_FEAT_WARMUP_DISABLED` (the feat warmup feature gate), both presence-based.
- `server.json` lists 6 of the 8 (all except the two feature gates), and the three pre-existing `SPECMGR_MCP_*` entries are stale: `SPECMGR_MCP_TRANSPORT` declares `choices: ["stdio", "sse"]` while the code supports three transports (`stdio`/`sse`/`streamable-http`, `commands/mcp.py`), and `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT` say "SSE transport only" while the code and the root `README.md` say "SSE/streamable-http mode only".
- No file under `tests/` references `server.json`.
- Nothing in `src/` (no `specmgr docs` stage, no other command) generates or edits `server.json` — it is hand-maintained, and this test will be its only guard.
- The root `README.md`'s warmup section covers the similarity gate only; `SPECMGR_FEAT_WARMUP_DISABLED` is not mentioned anywhere in it — README drift pre-existing as of the planning date, so Task 100.110 is planned as guaranteed correction, not a possibly-no-op check.
- `_SPECMGR_ROOT` in `src/biz/dfch/specmgr/_paths.py` is an internal variable name sharing the prefix, not an environment variable — the scan must not pick it up.

### Requirements

- REQ-001: `server.json`'s `environmentVariables` carries an entry for all 8 `SPECMGR_*` environment variables read in the source (8 = the planning-time count; the merged tree reads 12 and the drift test pins exact set equality, so the criterion holds as delivered), each with a `name` and a `description` faithful to the code's behaviour, and a `default` where the code has one (the two feature gates are presence-based: no `default`, and the description states that any value set enables the gate); the three pre-existing `SPECMGR_MCP_*` entries are corrected to be equally faithful (`SPECMGR_MCP_TRANSPORT`'s `choices` list all three transports the code supports; `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`'s descriptions name SSE/streamable-http mode only, not SSE only).
- REQ-002: A new regression test, `tests/test_server_json.py`, compares the set of `SPECMGR_*` environment-variable names read in `src/` against `server.json`'s `environmentVariables` names bidirectionally: (a) every name read in the source appears in the manifest, and (b) every manifest name is read in the source; the failure message names the specific missing/extra entries. The test additionally asserts the manifest's structural invariants: `name`s are unique, every entry carries a non-empty `description`, and `default` is present on an entry iff the code reads that variable with a default.
- REQ-003: The source scan covers `src/**/*.py` (verified at planning time: no non-`.py` file under `src/` mentions `SPECMGR_`) and matches only environment-variable read sites — four syntactic shapes, of which (1) string-literal assignments `= "SPECMGR_..."` (the `_*_ENV_VAR` constants) and (4) Typer `envvar="SPECMGR_..."` options are present in the corpus for `SPECMGR_` names today, while (2) `getenv("SPECMGR_..."` call sites and (3) `environ["SPECMGR_..."` / `environ.get("SPECMGR_..."` accesses are carried for robustness (the only quoted `os.environ.get` literals in the corpus are the three non-`SPECMGR_` hosting variables, which the prefix-anchored patterns never match) — and does not match docstring-prose or comment mentions nor identifiers that merely contain the prefix (e.g. `_SPECMGR_ROOT`).
- REQ-004: The test runs in the default pytest suite (hence in CI and pre-commit) and requires no new dependencies (stdlib `json`, `re`, `pathlib`).
- REQ-005: `README.md`'s "Environment Variables" section is accurate for all 8 (known to require correction: `SPECMGR_FEAT_WARMUP_DISABLED` is missing from the root `README.md`'s warmup section) and `CHANGELOG.md` gains an `[Unreleased]` entry.

### Acceptance Criteria

- [x] ACC-001: `server.json`'s `environmentVariables` names are exactly the 8 read in the source (the planning-time count; the merged tree reads 12 and the drift test pins exact set equality); the two feature-gate entries have no `default` and presence-based descriptions; the three pre-existing `SPECMGR_MCP_*` entries are faithful to the code (`SPECMGR_MCP_TRANSPORT`'s `choices` cover all three supported transports; `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`'s descriptions name SSE/streamable-http mode only); `name`s are unique, every `description` non-empty, and `default` present iff the code has one.
- [x] ACC-002: The drift test is green against the committed source and manifest.
- [x] ACC-003: Manual mutation of `server.json` (remove one entry → the test fails naming the missing variable; add a bogus `SPECMGR_BOGUS` → the test fails naming the extra variable) is verified during Phase 120 and reverted.
- [x] ACC-004: The scan does not report `_SPECMGR_ROOT` (`src/biz/dfch/specmgr/_paths.py`) — the fixture asserts the bare `SPECMGR_ROOT` substring too, since the guard's purpose is identifiers that merely contain the prefix — and does not report docstring-prose mentions (pinned by the test's own negative fixture cases).
- [x] ACC-005: The full quality gate is green: `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`.
- [x] ACC-006: `README.md`'s "Environment Variables" section and the `CHANGELOG.md` `[Unreleased]` entry are committed inside their phase's commit.

### Scope

#### Included

- The 2 missing manifest entries (`SPECMGR_SIMILARITY_DISABLED`, `SPECMGR_FEAT_WARMUP_DISABLED`) in `server.json`.
- The correction of the 3 stale pre-existing `SPECMGR_MCP_*` manifest entries (`SPECMGR_MCP_TRANSPORT`'s `choices`; `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`'s descriptions) so the whole manifest is faithful to the code.
- The bidirectional drift regression test `tests/test_server_json.py` and its source scan (test-local; no new production code path).
- The `README.md` "Environment Variables" completeness correction (known to be required: `SPECMGR_FEAT_WARMUP_DISABLED` is already missing from the root `README.md`'s warmup section) and the `CHANGELOG.md` entry.

#### Explicitly Out Of Scope

- Any change to how environment variables are read in `src/` (the code is the source of truth; no refactor into a shared registry module — if the scan approach proves brittle, that is a follow-up feature).
- Adding new environment variables, or changing any existing default or behaviour.
- Publishing the manifest change to the MCP Registry (release process's job).
- The manifest's own top-level `version` field (currently `0.1.0`, stale against the released `0.35.0`): it is managed by the release SOP, is not part of `environmentVariables`, and the name-only drift test deliberately ignores it.
- Generating `server.json` via `specmgr docs` or any other stage (verified absent; deliberately not introduced here).
- Any other open issue (only #126).

### Dependencies

#### Depends On

- FEAT feat-134-related-artifact-similarity (done): origin of the `SPECMGR_SIMILARITY_DISABLED` gate the manifest entry documents.
- FEAT feat-187-list-feat-timeout (done): origin of the `SPECMGR_FEAT_WARMUP_DISABLED` gate the manifest entry documents.

#### Blocks

- None known.

### Design Notes

**Source-true bidirectional scan, not an allowlist.** The issue's own fix note acknowledges the two prior additions were made by hand and that "no drift detection is in place." An expected-list inside the test would be a third hand-maintained copy — the same failure mode. Hence the test derives the expected set from `src/` read sites and compares it bidirectionally: missing entries (in code, not in manifest) and stale entries (in manifest, not in code) both fail, each naming the specific entries.

**Scan precision.** All four syntactic shapes of REQ-003 are recognised, though only shapes (1) and (4) are present in the corpus for `SPECMGR_` names today: the five `_*_ENV_VAR` constants are plain string-literal assignments, and `commands/mcp.py` declares its three variables as Typer `envvar="SPECMGR_..."` options. There are no `os.getenv` call sites anywhere in `src/`, and the only quoted `os.environ.get` literals are the three non-`SPECMGR_` hosting variables — so shapes (2) and (3) are kept for robustness, so a future read style is caught by the test rather than silently untracked. The scan covers `src/**/*.py` (verified at planning time: no non-`.py` file under `src/` mentions `SPECMGR_`; post-merge, feat-185's packaged rulebook `src/biz/dfch/specmgr/uc/data/uc_plantuml.md` mentions the plantuml names in prose — the `.py`-only scope is unaffected, since only code can carry a read site). A line-regex over raw source text is adequate; the false-positive risk is a docstring or comment line that happens to contain one of the shapes (e.g. a docstring quoting an assignment). Phase 120 pins this with explicit negative fixture cases — `_SPECMGR_ROOT` in `_paths.py` plus a synthetic docstring-quoting case — and tightens the regex if the corpus yields any false positive. Non-`SPECMGR_` environment reads in `commands/mcp.py` (`KUBERNETES_SERVICE_HOST`, `RAILWAY_PROJECT_ID`, `RENDER`) are outside the manifest's scope and never match the prefix-anchored patterns.

**Presence gates in the manifest.** Existing entries use `name`/`description` plus `default` where applicable and `choices`/`format` where useful. The two gates have no default; the manifest's shape does not require one. Hence: `name` + `description` only, with the description stating "presence-based — set to any value to …; unset by default", mirroring what `specmgr://config` reports (`similarity.disabled`, `feat_warmup_disabled`).

**Phase discipline.** Every phase ends with the full quality gate — `ruff format --check`, `ruff check`, `vulture`, the full test suite `pytest -n auto --cov=src`, plus every doc-drift check the phase touches (`specmgr docs` / `specmgr adr-toc` / `specmgr mcp-docs`; expected no-op for this feature, since no `src/` module changes) — and exactly one Conventional Commit; the phase's docs sync travels inside the same commit (repo convention, see AGENTS.md).

### Related Decisions

- FEAT feat-51-mcp-cwd (GitHub issue #51): the `specmgr://config` resource that resolves the same environment variables — the manifest descriptions stay faithful to what `specmgr://config` reports.
- ADR 750842b2-aca4-4649-ba0c-855ec8e1f505 (feat-134): semantics of `SPECMGR_SIMILARITY_DISABLED`.
- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (feat-187): semantics of `SPECMGR_FEAT_WARMUP_DISABLED`.

### Task List

#### Phase 100: Manifest completion

- [x] Task 100.100: Add the `SPECMGR_SIMILARITY_DISABLED` and `SPECMGR_FEAT_WARMUP_DISABLED` entries to `server.json`'s `environmentVariables` (name + presence-based description, no `default`), and correct the 3 stale pre-existing `SPECMGR_MCP_*` entries per REQ-001/ACC-001: `SPECMGR_MCP_TRANSPORT`'s `choices` to all three transports the code supports (`stdio`/`sse`/`streamable-http`), and `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`'s descriptions to name SSE/streamable-http mode only.
- [x] Task 100.110: Verify `README.md`'s "Environment Variables" section (and the `specmgr mcp` section for the transport/host/port entries) against all 8 and correct: the root `README.md`'s warmup section already omits `SPECMGR_FEAT_WARMUP_DISABLED` (known drift recorded in the Verified state), so this task is planned as guaranteed correction, not a possibly-no-op check.
- [x] Task 100.120: `CHANGELOG.md` `[Unreleased]` entry.
- [x] Task 100.130: Phase-end gate (full quality gate, per Design Notes): `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, and every doc-drift check the phase touches (expected no-op: no `src/` module changes) green; exactly one Conventional Commit.

#### Phase 120: Drift regression test

- [x] Task 120.100: Implement `tests/test_server_json.py`: parse `server.json` (stdlib `json`), scan `src/**/*.py` for environment-variable read sites per the four syntactic shapes of the Design Notes, assert set equality in both directions plus the structural invariants of REQ-002 (unique `name`s, non-empty `description`s, `default` present iff the code has one), failure message naming the specific missing/extra entries.
- [x] Task 120.110: Pin the false-positive guards (ACC-004): `_SPECMGR_ROOT` in `_paths.py` (and the bare `SPECMGR_ROOT` substring) must not be reported; add the docstring-quoting negative fixture; tighten the regex if the corpus yields false positives.
- [x] Task 120.120: Manually verify ACC-003 (mutate `server.json` both directions, observe the naming failure messages, revert).
- [x] Task 120.130: Phase-end gate (full quality gate, per Design Notes): `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, and every doc-drift check the phase touches (expected no-op: no `src/` module changes) green; exactly one Conventional Commit.

## Progress

### Current Status

**As of 2026-10-08**: All phases complete, including the post-merge manifest extension (the origin/dev merge brought feat-185-uc-diagrams into the source): `server.json`'s `environmentVariables` now covers the twelve `SPECMGR_*` variables the merged source reads, the drift test's default-presence classifier was refined for the post-merge corpus, and the `CHANGELOG.md` manifest bullet was extended to the six previously-undocumented variables; all six acceptance criteria (ACC-001 through ACC-006) verified; status is review, pending final review.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-08T11:15:10.000Z - Round-1 post-implementation review (feat-reviewer): ship as-is

The feat-reviewer review of the delivered diff (origin/dev...HEAD) verdicted **ship as-is** — all six acceptance criteria pass with independently re-verified evidence, no errors or scope gaps, and the post-merge additions (the four manifest entries and the default-classifier refinement) were traced faithful to the code. Applied from the review: D1 (REQ-001/ACC-001 wording now notes the 8→12 planning-time vs merged count), D2 (the Design Notes non-`.py`-file premise clarified post-merge), D3 (the CHANGELOG Changed bullet now scopes its "eight" claim to the point of change). Deferred as follow-up candidates (all fail loudly by design, none affect the delivered tree): I1 (the classifier's assignment-context pattern is exact-whole-line only; a same-line `or`-fallback or multi-line read would classify no-default), I2 (a triple-quoted f-string whose expression reads an env var would be a false negative), I3 (a Typer option declaring `default=` inside `typer.Option(...)` rather than the corpus' Annotated-close style would classify no-default).

#### 2026-10-08T09:19:56.000Z - Post-merge manifest completion (origin/dev merge, feat-185 content)

Merging origin/dev into this branch brought feat-185-uc-diagrams into the source, adding four `SPECMGR_*` read sites: the three PlantUML validation-source selectors (`SPECMGR_PLANTUML_JAR`, `SPECMGR_PLANTUML_BIN`, `SPECMGR_PLANTUML_URL` — first-set-wins, no public default) and the `SPECMGR_TESTS_NO_DOTENV` test/CI sentinel (skips the CLI's module-level default `.env` load). The new drift test flagged all four as read in `src/` but missing from the manifest — the feature working as designed. Completed in this feature: `server.json` gained the four entries (`name` + description only, no `default`, mirroring the code's presence-based reads); the test's default-presence classifier was refined (the former substring plain-`get` pattern replaced by a line-anchored assignment-context pattern, plus a new line-anchored conditional-truthiness presence pattern in the no-default group), so `SPECMGR_TESTS_NO_DOTENV` now classifies no-default like the other presence reads; the `CHANGELOG.md` manifest bullet was extended to all six previously-undocumented variables; and the root `README.md` needed no change — feat-185 already documents the plantuml trio in its "Environment Variables" bullet and "UC → PlantUML Diagrams" section, and the sentinel is deliberately test/CI-internal, staying documented in `cli.py`'s `NO_DOTENV_SENTINEL` docstring and `tests/conftest.py`.

#### 2026-10-08T08:05:22.000Z - Status set to review

All acceptance criteria (ACC-001 through ACC-006) verified with evidence: the drift test is green 7/7 against the committed source and manifest (ACC-001/ACC-002); ACC-003's manual mutation of `server.json` was verified in both directions — removing `SPECMGR_FEAT_DIR` failed the suite naming the variable missing from the manifest, adding a bogus `SPECMGR_BOGUS` failed it naming that entry extra — and reverted; ACC-004's negative fixtures pin the `_SPECMGR_ROOT`/bare-`SPECMGR_ROOT` and docstring-prose guards; the full quality gate is green (ACC-005; `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src` — 4095 passed); and the root `README.md` correction plus the `CHANGELOG.md` `[Unreleased]` entry are committed inside their phase's commits (ACC-006). The feature is ready for review.

#### 2026-10-08T07:20:43.000Z - Phase 120 (Drift regression test) implemented

Task 120.100: `tests/test_server_json.py` scans `src/**/*.py` for the four read-site shapes (string-literal assignment, `getenv`, `environ` access, Typer `envvar=` option — prefix-anchored on a quoted `SPECMGR_[A-Z0-9_]+` name, with `#`-comment and triple-quoted docstring regions blanked so prose/shape-quoting in docstrings and comments cannot be reported), asserts the bidirectional set equality against `server.json`'s `environmentVariables` with a failure message naming the specific missing (read in `src/`, absent from the manifest) and extra (in the manifest, never read in `src/`) entries, and pins the REQ-002 structural invariants (unique `name`s, non-empty `description`s, and `default` present iff the code-side classification says the variable has a default — shape-(1) constants are followed to their whole-tree read sites, Typer options to their Annotated close + assignment line). Task 120.110: the false-positive guards are pinned — an explicit assert that the bare `SPECMGR_ROOT` substring (from `_SPECMGR_ROOT` in `src/biz/dfch/specmgr/_paths.py`) is not reported, plus two synthetic fixture trees proving that docstring prose, comment mentions, and even docstring/comment lines quoting a full shape verbatim are not reported while real sites still are. Task 120.120: ACC-003 verified by mutation — removing `SPECMGR_FEAT_DIR` from `server.json` fails the suite naming it as missing from the manifest, adding a bogus `SPECMGR_BOGUS` entry fails it naming that entry as extra in the manifest; `server.json` was reverted to the committed state (suite green again, `git status` clean for it). Task 120.130: full quality gate green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`); `docs/GENERATED.md` regenerated for the new test file (test-file count 383 → 384 — the one doc-drift check this phase is not a no-op on), `specmgr adr-toc` and `specmgr mcp-docs` verified no-op; `CHANGELOG.md` `[Unreleased]` gained the test bullet.

#### 2026-10-08T05:32:41.000Z - Phase 100 (Manifest completion) implemented

Task 100.100: `server.json`'s `environmentVariables` gained the two missing presence-based feature-gate entries (`SPECMGR_SIMILARITY_DISABLED`, `SPECMGR_FEAT_WARMUP_DISABLED` — `name` + description only, no `default`, mirroring the gating the code performs and what `specmgr://config` reports) and the three stale `SPECMGR_MCP_*` entries were corrected (`SPECMGR_MCP_TRANSPORT`'s `choices` now `stdio`/`sse`/`streamable-http`; `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT`'s descriptions now "SSE/streamable-http mode only", matching the code and the root `README.md`'s `specmgr mcp` table). Task 100.110: the root `README.md`'s "Background warmup at server startup" paragraph now describes the unified `specmgr-startup-warmup` thread's three ordered phases (feat frontmatter, feat full-parse, similarity) and both per-phase opt-out flags (both set = no thread starts at all); the "Environment Variables", "Opt-out", and "Introspection" paragraphs name `SPECMGR_FEAT_WARMUP_DISABLED` too, so all 8 variables are covered. Task 100.120: `CHANGELOG.md` `[Unreleased]` gained an `### Added` entry (the 2 new manifest entries) and an `### Changed` entry (the 3 corrections + the README fix), citing feat-126-server-json-env-drift, GitHub issue #126. Task 100.130: full quality gate green (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src`, and the doc-drift checks as no-ops — no `src/` module changes).

#### 2026-10-08T04:59:17.000Z - Plan refined (round-1 feat-refiner review)

Round-1 refinement of the plan (no implementation). Applied: D1 corrected the scan-shape inventory in REQ-003/Design Notes (shapes (2)+(3) absent for `SPECMGR_` names today, kept for robustness); G2 pinned the scan scope to `src/**/*.py` (REQ-003/Task 120.100); D2/G1 brought the 3 stale pre-existing `SPECMGR_MCP_*` manifest entries into scope for correction in Phase 100 (REQ-001/ACC-001/Task 100.100 — recorded in Decisions Made); G3 recorded the known root-README drift so REQ-005/Task 100.110 are planned as guaranteed correction; D3/I1 renamed `SPECMGR_ROOT` to `_SPECMGR_ROOT` everywhere (Verified state/ACC-004/Design Notes/Task 120.110, with a bare-substring negative assert); D4 tagged the three feature references with `FEAT` so `list_references` resolves them (Depends On/Related Decisions); I2 strengthened the drift test with structural invariants (REQ-002/ACC-001/Task 120.100); I3 noted the manifest's stale top-level `version` as release-SOP-managed and out of scope. Left as-is per user decision: ACC-005's missing matching REQ (repo-convention coverage; I4 disposition).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-08T09:19:56.000Z - Complete the four post-merge variables into the manifest in this feature; keep the sentinel manifest-only

The origin/dev merge (feat-185-uc-diagrams content) added four `SPECMGR_*` read sites the manifest did not yet carry. They are completed into `server.json` in THIS feature rather than deferred: the drift test's invariant is manifest ⇄ source on the merged tree, so deferring would leave the suite (and CI) red on this branch. The `SPECMGR_TESTS_NO_DOTENV` sentinel is manifest-only — it gains no root-`README.md` section, since it is test/CI-internal by feat-185's own documentation choice (documented in `cli.py`'s `NO_DOTENV_SENTINEL` docstring and `tests/conftest.py`, honoured by the `specmgr coverage-badge` hook's source-less re-run).

#### 2026-10-08T04:59:17.000Z - Correct the stale pre-existing `SPECMGR_MCP_*` manifest entries in this feature

The round-1 refinement found that the three pre-existing `SPECMGR_MCP_*` entries in `server.json` are not faithful to the code (`SPECMGR_MCP_TRANSPORT` declares 2 of the 3 supported transports; `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT` say "SSE transport only" instead of "SSE/streamable-http mode only"). Since REQ-001 promises entries "faithful to the code's behaviour", correcting them in Phase 100 (Task 100.100, asserted by ACC-001) keeps the manifest honest as soon as the guard lands, rather than leaving a known-unfaithful gap for a follow-up feature. (User decision, 2026-10-08: fix in this feature, not defer.)

#### 2026-10-07T12:00:00.000Z - Source-true bidirectional scan, no allowlist in the test

Rather than keep an expected environment-variable list inside the test (a third hand-maintained copy), the drift test scans `src/` for environment-variable read sites (the four syntactic shapes: `_*_ENV_VAR` string-literal assignments, `getenv`, `environ` access, Typer `envvar=` options) and compares bidirectionally against `server.json`. The two missing presence gates are added to the manifest itself, not special-cased in the test.
