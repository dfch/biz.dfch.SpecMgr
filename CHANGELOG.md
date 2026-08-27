# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- **BREAKING**: the 14 per-domain mutation MCP tools are deleted outright
  (no deprecated wrappers): `update_req`, `update_uc`, `update_tsk`,
  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
  `set_status_gol`, `set_status_rsk`. Whole-body and line-range updates
  now go through the generic `update` tool and status changes through the
  generic `set_status` tool in `general/tools/` (see "Added" below).
- **BREAKING**: ADR's own `set_status` tool is removed; the surviving
  `set_status` tool is the generic one, whose signature changes from
  `(id, status, superseded_by)` to `(id, type, status, superseded_by)` —
  `type="adr"` is now required (and the tool is accepted for all eight
  domains).

### Added

- Generic `update(id, type, content, begin=None, end=None)` MCP tool in
  `general/tools/`: whole-body and line-range replace of an existing
  document across the seven whole-body domains (`type` is one of
  `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`). With no `begin`/`end`,
  `content` is the full replacement body; with both, it replaces the
  1-based, inclusive body-line range `begin`..`end` of the current on-disk
  body (`N+1` = end-of-body sentinel: append after the last line, or
  replace through end of body). The spliced result is validated as a whole
  document before anything is written; unchanged regions stay
  byte-identical.
- Generic `set_status(id, type, status, superseded_by=None)` MCP tool in
  `general/tools/`: the status change for all eight domains (`type` is one
  of `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`adr`), enforcing each
  domain's closed status vocabulary. `superseded_by` is accepted only for
  `type="adr"` (composing the status as `"superseded by {superseded_by}"`)
  and raises `ValueError` with any other `type`.
- Optional `raw: bool = False` parameter on the seven `get_<d>` tools
  (`get_req`, `get_uc`, `get_tsk`, `get_qa`, `get_prb`, `get_gol`,
  `get_rsk`): `raw=True` returns the frontmatter-stripped body text
  verbatim — the text `update`'s `begin`/`end` index into; `raw=False`
  (the default) behaves exactly as before.
- The consolidation above is recorded in ADR
  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
  status-change tools into generic type-dispatched tools").

## [0.11.0] - 2026-08-26

### Added

- **Eighth domain feature (GOL/Goal tooling)**: implemented high-level
  business-goal document tools and infrastructure (the strategic
  "what the organization wants to achieve" level that sits above
  individual requirements):
  - `gol/models/v1/`: Pydantic schema (`GolFrontmatter` with REQ's exact
    7-value status set, `Goal` body mirroring `Requirement` with exactly
    two deliberate omissions — no `## Characteristics`, no `## Level`, so
    the only mandatory body fields are statement + Source, plus optional
    Description/Priority/Tags/Related Artifacts/More Information/Notes),
    parser (`parse_gol`), `GolSummary`, and JSON schema generation, inside
    the domain package itself (not top-level `models/`).
  - `gol/tools/`: `@mcp.tool()` wrappers for the GOL lifecycle
    (`create_gol`, `update_gol`, `set_status_gol`, `parse_gol`, `list_gol`,
    `get_gol`, `get_gol_example`, `get_gol_template`, `validate_gol`),
    plus a stub for `delete_gol`. `list_gol` ships as a paged tool from day
    one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `gol/resources/`: `specmgr://gol/schema`, `specmgr://gol/example`,
    `specmgr://gol/template` (no `specmgr://gol/{id}` — id-based reads are
    `get_gol`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
    `specmgr://gol/list` — listing is the `list_gol` tool, ADR
    ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `gol/prompts/`: narrated `create_gol`/`update_gol` prompts driving a
    `TodoWrite` + `question`-tool interview flow; `create_gol` first checks
    `list_gol` for a near-duplicate goal.
  - `server.py` updated to import the new `gol` domain package; `AGENTS.md`
    updated for eight domain/cross-cutting packages.
  - Comprehensive test coverage across `tests/gol/models/`,
    `tests/gol/tools/`, `tests/gol/resources/`, and `tests/gol/prompts/`,
    including a live lifecycle integration test.

- **Ninth domain feature (RSK/Risk tooling)**: implemented risk-register
  entry document tools and infrastructure (the scenario decomposed into
  `## Cause`/`## Trigger`/`## Consequence`, a 5x5 probability/impact
  assessment before mitigation (`## Initial Assessment`) and the same 5x5
  after mitigation (`## Residual Assessment`) with the value in the H3
  heading itself, and a TARA response strategy `## Strategy` — closed
  4-value set `transfer`/`accept`/`reduce`/`avoid`):
  - `rsk/models/v1/`: Pydantic schema (`RskFrontmatter` with 6-value status
    set `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`,
    `Risk` body with computed probability/impact values and a derived risk
    `level` always computed from the 5x5 product), parser (`parse_rsk`),
    `RskSummary`, and JSON schema generation, inside the domain package
    itself (not top-level `models/`).
  - `rsk/tools/`: `@mcp.tool()` wrappers for the RSK lifecycle
    (`create_rsk`, `update_rsk`, `set_status_rsk`, `parse_rsk`, `list_rsk`,
    `get_rsk`, `get_rsk_example`, `get_rsk_template`, `validate_rsk`),
    plus a stub for `delete_rsk`. `list_rsk` ships as a paged tool from day
    one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), and its `RskSummary`
    lines carry the residual-risk coordinates so a register-wide
    risk-matrix view can be built from the listing alone.
  - `rsk/resources/`: `specmgr://rsk/schema`, `specmgr://rsk/example`,
    `specmgr://rsk/template`, plus two static domain-knowledge resources
    `specmgr://rsk/tara` (what TARA is and when/how to apply each of the
    four words) and `specmgr://rsk/risk-matrix` (the 5x5 scale anchors,
    zone table, and product thresholds) (no `specmgr://rsk/{id}` —
    id-based reads are `get_rsk`-only, ADR
    ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://rsk/list` — listing
    is the `list_rsk` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `rsk/prompts/`: `create_risk`/`update_risk` prompts (the issue's
    literal wording, not the `rsk`-prefixed convention the tools/resources
    use) driving a narrated `TodoWrite` + `question`-tool interview flow.
  - `server.py` updated to import the new `rsk` domain package; `AGENTS.md`
    updated for nine domain/cross-cutting packages.
  - Comprehensive test coverage across `tests/rsk/models/`,
    `tests/rsk/tools/`, `tests/rsk/resources/`, and `tests/rsk/prompts/`,
    including guards that keep the packaged TARA/risk-matrix domain
    knowledge consistent with the model's derived-level zone mapping.

## [0.10.0] - 2026-08-25

### Added

- **Seventh domain feature (PRB/Problem Statement tooling)**: implemented
  Six-Sigma-style problem-statement document tools and infrastructure:
  - `prb/models/v1/`: Pydantic schema (`PrbFrontmatter`, `PrbBody`,
    `PrbDocument`), parser (`parse_prb`), `PrbSummary`, and JSON schema
    generation, inside the domain package itself (not top-level `models/`).
  - `prb/tools/`: `@mcp.tool()` wrappers for the PRB lifecycle
    (`create_prb`, `update_prb`, `set_status_prb`, `parse_prb`, `list_prb`,
    `get_prb`, `get_prb_example`, `get_prb_template`, `validate_prb`),
    plus a stub for `delete_prb`.
  - `prb/resources/`: `specmgr://prb/schema`, `specmgr://prb/example`,
    `specmgr://prb/template` (no `specmgr://prb/{id}` or
    `specmgr://prb/list`, consistent with REQ/UC/TSK/QA).
  - `prb/prompts/`: narrated `create_prb`/`update_prb` prompts driving a
    `TodoWrite` + `question`-tool 5W2H interview flow.
  - `server.py` updated to import the new `prb` domain package; `AGENTS.md`
    updated for seven domain/cross-cutting packages; README.md documents
    the new Problem Statement (PRB) artifact type.
  - Comprehensive test coverage across `tests/prb/models/`, `tests/prb/tools/`,
    `tests/prb/resources/`, and `tests/prb/prompts/`, including a live
    lifecycle integration test.

## [0.9.0] - 2026-08-23

### Changed

- **BREAKING**: QA (Question and Answer) documents now use a new v2 body
  schema (`qa/models/v2/`); every QA MCP tool/resource/prompt (`create_qa`,
  `update_qa`, `set_status_qa`, `parse_qa`, `list_qa`, `get_qa`,
  `get_qa_example`, `get_qa_template`, `delete_qa` stub, `validate_qa`,
  `specmgr://qa/schema`/`/example`/`/template`, `create_qa`/`update_qa`/
  `refine` prompts) is repointed at it. v2 replaces v1's one
  `### {heading}` H3 sub-section per question/answer pair with many
  adjacent, un-headed pairs (`<!-- optional comment -->` + `> {question}`
  block quote + free-form answer prose) directly inside a category
  section, and adds a new `## Elicitation Context` section (a 10th
  `_QaCategory`-shaped section, not one of the 9 ISO/IEC 25010:2023
  characteristics) between `## General` and `## Functional Suitability`.
  This is a hard cutover with no version gate and no dual v1/v2 read
  support: a document shaped for the former v1 schema fails v2 parsing
  with a structural `AssertionError`/`pydantic.ValidationError`, not a
  migration-specific error. `qa/models/v1/` has since been removed from
  disk entirely (`QaFrontmatter`/`QaSummary` moved into `qa/models/v2/`);
  QA is once again a single-schema (v2-only) domain.

## [0.8.0] - 2026-08-19

### Changed

- **BREAKING**: Removed the five `specmgr://<domain>/list` MCP resources
  (`adr`, `req`, `uc`, `tsk`, `qa`); replaced by paged `list_<domain>`
  `@mcp.tool()`s (`list_adr`, `list_req`, `list_uc`, `list_tsk`, `list_qa`)
  accepting `max_results`/`offset` and returning a shared `PagedResult`
  wrapper (`total`, `offset`, `max_results`, `truncated`, `results`).
  Resources cannot accept parameters, so pagination required the
  resource→tool conversion (see ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13). Callers must switch from
  `resources/read --uri specmgr://<domain>/list` to `tools/call
  --tool-name list_<domain>`.

### Added

- Shared `general/models/PagedResult[T]` and `general/tools/_paging`
  (`normalize_paging`/`paginate`) infrastructure, and a shared
  `general/models/DocSummary` base for four of the five domains' summary
  models (`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary`); `AdrSummary`
  stays a deliberate, documented outlier (field-identical, not a
  subclass, since `models/adr` must stay free of the `mcp` extra).

## [0.7.0] - 2026-08-18

### Added

- **`compact_history` MCP prompt** (`general/prompts/`): New prompt for compacting
  verbose history entries, with packaged instruction data file
  (`general/data/general_compact_history_instructions.md`) and full test coverage
  (12 tests). Establishes prompts support under the `general/` domain package.
- **External prompt instruction files**: Migrated inline instruction strings from
  Python code to external markdown files in `*/data/` directories across all
  domains (adr, qa, req, tsk). Enables easier maintenance and better separation
  of concerns.
- **`refine` prompt for QA module**: New prompt to elicit additional Q&A pairs
  by quality category.

### Changed

- Prompt instruction text storage: replaced inline `str.format()` calls with
  external markdown data files and `string.Template` for placeholder substitution,
  allowing unescaped braces in markdown content. Instructions are read fresh on
  every call (no caching) via the `read_packaged_text()` helper.

## [0.6.0] - 2026-08-18

### Added

- **Fifth domain feature (QA/Q&A tooling)**: implemented question-and-answer document
  tools and infrastructure:
  - `qa/models/v1/`: Pydantic schema (`QaFrontmatter`, `QaBody`, `QaItem`, `QaDocument`),
    parser (`parse_qa`), renderer (`render_qa`), re-exported via `qa/models/__init__.py`
    and `models/__init__.py`.
  - `qa/tools/`: `@mcp.tool()` wrappers for Q&A lifecycle (`create_qa`, `update_qa`,
    `parse_qa`, `set_status_qa`), plus stub for `delete_qa`.
  - `qa/resources/`: MCP resources for Q&A read operations (`specmgr://qa/list`,
    `specmgr://qa/{id}`).
  - `qa/prompts/`: `create_qa` and `update_qa` prompts for Q&A drafting and revision
    workflows.
  - Comprehensive test coverage with 80+ passing tests across `tests/models/qa/`,
    `tests/qa/tools/`, `tests/qa/resources/`, and `tests/qa/prompts/`.
- **Markdown infrastructure improvements**: generalized `@markdown` decorator with
  enhanced merge semantics and `end_marker` support for more flexible section
  composition across document types.

### Changed

- MCP server registration in `server.py` updated to import all six domains
  (`adr`, `general`, `qa`, `req`, `tsk`, `uc`) to register their respective
  tools, resources, and prompts.

## [0.5.1] - 2026-08-18

### Fixed

- **`md` models**: `MarkdownListItem.get_extent()` now correctly handles
  continuation paragraphs in loose numbered lists (e.g., "1. Safety\n\n  Details...").
  Previously, mdformat rendered numbered lists differently from bullet lists,
  causing `get_extent()` to only capture the first paragraph and leave
  continuation paragraphs unparsed. The model's `Characteristics.Items` also
  changed from `MarkdownListItemWithNotes` back to plain `MarkdownListItem`
  per domain decision.

## [0.5.0] - 2026-08-16

### Added

- **`specmgr webfetch` MCP tool**: bearer-token-authenticated HTTP GET utility
  for fetching URL content with configurable base-URL filtering (case-insensitive
  matching via `SPECMGR_WEBFETCH_BASE_URL` and `SPECMGR_WEBFETCH_BEARER` environment
  variables). Includes custom exceptions (`WebfetchNotConfiguredError`,
  `WebfetchUrlNotAllowedError`) and comprehensive test coverage (45+ tests).
  Documented in README.md; registered in `general/tools/` with full API
  documentation auto-generated.

### Changed

- Error messages for not-found exceptions (`AdrNotFoundError`, `ReqNotFoundError`,
  `UcNotFoundError`, `TskNotFoundError`, `DocNotFoundError`) standardized across
  all domains for consistent UX when a document cannot be located. Updated all
  related tool modules (`adr/tools/_paths.py`, `req/tools/_paths.py`, etc.) and
  extended test coverage in each domain's `test_paths.py` and `test_get_<type>.py`
  to assert on message content.

## [0.4.0] - 2026-08-16

### Added

- **Third domain feature (TSK/TaskList tooling)**: implemented task-list document
  tools and infrastructure:
  - `models/tsk/v1/`: Pydantic schema (`TskFrontmatter`, `TskBody`, `TaskListItem`,
    `TskDocument`), parser (`parse_tsk`), renderer (`render_tsk`), re-exported via
    `models/tsk/__init__.py` and `models/__init__.py`.
  - `tsk/tools/`: `@mcp.tool()` wrappers for task-list lifecycle (`create_tsk`,
    `update_tsk`, `parse_tsk`, `set_status_tsk`), plus stub for `delete_tsk`.
  - `tsk/resources/`: MCP resources for task-list read operations (`specmgr://tsk/list`,
    `specmgr://tsk/{id}`).
  - `tsk/prompts/`: `create_tsk` and `update_tsk` prompts for task-list drafting
    and revision workflows.
  - Comprehensive test coverage with 70+ passing tests under `tests/models/tsk/`,
    `tests/tsk/tools/`, `tests/tsk/resources/`, `tests/tsk/prompts/`.
- **Fourth domain feature (UC/UseCase tooling)**: implemented use-case document
  tools and infrastructure:
  - `models/uc/v1/`: Pydantic schema (`UcFrontmatter`, `UcBody`, `UseCase`),
    parser (`parse_uc`), renderer (`render_uc`), re-exported via `models/uc/__init__.py`
    and `models/__init__.py`.
  - `uc/tools/`: `@mcp.tool()` wrappers for use-case lifecycle (`create_uc`,
    `update_uc`, `parse_uc`, `set_status_uc`), plus stub for `delete_uc`.
  - `uc/resources/`: MCP resources for use-case read operations (`specmgr://uc/list`,
    `specmgr://uc/{id}`).
  - `uc/prompts/`: `create_uc` and `update_uc` prompts for use-case drafting
    and revision workflows.
  - Comprehensive test coverage with 75+ passing tests under `tests/models/uc/`,
    `tests/uc/tools/`, `tests/uc/resources/`, `tests/uc/prompts/`.
- **ISO/IEC 25010:2023 quality model resource** (`iso25010`): a cross-cutting
  shared resource providing the ISO/IEC 25010:2023 software product quality
  characteristics and sub-characteristics, accessible via `specmgr://iso25010/model`.

### Changed

- Moved the top-level `resources/` package (the `specmgr://version` MCP
  resource) into `general/resources/`, since it is itself a cross-cutting,
  not domain-specific, concern — consistent with `general/tools/`. Updated
  `server.py`'s registration import accordingly (`general` now pulls in its
  own `resources`/`tools` sub-packages).

### Fixed

- Task-list (TSK) examples and error messages clarified for better UX.

## [0.3.1] - 2026-08-15

### Added

- **`general/tools/_packaged_data.py`**: Generic, doc-type-agnostic utility
  module providing `packaged_data_path()` and `read_packaged_text()` functions
  for accessing packaged data files (example/template/schema documents) across
  all artifact types. Eliminates per-doc-type boilerplate and reduces
  duplication.

### Changed

- REQ's packaged data files (example, template, schema) relocated from
  `req/resources/data/` to `req/data/` for consistency with future artifact
  types.
- REQ tools updated to use `general.tools._packaged_data` instead of the
  retired `req._data` module, centralizing packaged-data access.
- `pyproject.toml` package-data key updated to reflect new `req/data/` path.
- Pre-commit hook and CI step updated to reference new packaged-data location.

### Removed

- `req/_data.py`: REQ-specific packaged-data module superseded by
  `general/tools/_packaged_data.py`.

## [0.3.0] - 2026-08-15

### Added

- **`specmgr coverage-badge`**: a CLI command that reads the `.coverage`
  data file (generated by `coverage run`), extracts the total test coverage
  percentage, and renders a flat-style SVG badge with color based on
  coverage threshold (≥90% green, ≥75% yellowgreen, ≥50% yellow, else red).
  Badge written to `docs/coverage.svg` by default, with `--output`/`-o` to
  override. Wired into CI and pre-commit to enforce badge freshness on every
  change to source/test files. Coverage measurement now runs by default as
  part of the existing test suite (no separate test run); the badge itself
  is only regenerated/verified on Python 3.13 to match `docs`/`adr-toc`
  behavior.
- `vulture` dead-code detector: added to the `test` extra, wired into a new
  local `vulture` pre-commit hook (`uv run --frozen vulture src/
  whitelist.py --min-confidence 60`) and into CI's lint step across the
  full 3.11/3.12/3.13 matrix. Known framework false positives (Pydantic
  `@field_validator`/`@model_validator` methods and `model_config`, and MCP
  `@mcp.resource()`/`@mcp.tool()` entry points) are suppressed via a new
  root-level `whitelist.py`, grouped and commented by the reason each is a
  false positive rather than real dead code.
- **`specmgr unused-code`**: a CLI command wrapping `vulture`. By default,
  reports every unreferenced symbol in `--src` (plus `--whitelist`, if it
  exists) -- the same check the pre-commit hook/CI step enforce, without
  having to remember the raw `vulture` invocation. With `--test`/`-t`,
  instead reports symbols `vulture` only considers "used" because the
  test suite references them, never production code itself: compares a
  scan of `--src` alone against a scan of `--src` together with `--tests`,
  and reports the symbol names that disappear from the findings once
  tests are included -- a lead worth a manual look, since it may indicate
  an orphaned public surface. Supports `--min-confidence` and an opt-in
  `--strict` flag (exit 1 if any findings are reported, for future CI
  wiring). Requires the `test` extra, since `vulture` is only declared
  there.
- **`specmgr adr-toc`**: a CLI command that generates a table of contents
  (`docs/adr/README.md`) listing all ADRs with their titles, frontmatter
  (id, status, date, decision-makers, consulted, informed), and links to
  the actual ADR files. Scans the configurable ADR base directory (default
  `docs/adr`, via `SPECMGR_ADR_DIR` environment variable). Supports
  `--output`/`-o` to write to an alternate location. Run after adding new
  ADRs and commit the result.
- **`specmgr docs`**: a single CLI command that writes `api/*.md`
  (per-module Markdown API reference, plus a `README.md` index) and
  `GENERATED.md` (implemented-domain list, per-module docstrings, and a
  static test-file count) under an `--output`/`-o` base directory,
  defaulting to the repo's `docs/` (committed, so it browses directly on
  GitHub). Replaces the previous `generate-docs`, `markdown-docs`, and
  `pydoc` commands (see "Removed" below). The `api/README.md` index now
  includes the first-line docstring for each module, improving discoverability.
- `pre-commit` adoption: `.pre-commit-config.yaml` runs `ruff format`/`ruff
  check`, the full `unittest` suite (scoped to `src/**/*.py`/`tests/**/*.py`
  changes), and a local `specmgr docs` hook (scoped to `src/**/*.py`
  changes) before every commit; `pre-commit` added to the `dev` extras.
  One-time setup: `uv run --frozen pre-commit install`.
- CI backstop: `.github/workflows/ci.yml` now regenerates `docs/` and
  fails the build on drift, catching anyone who bypassed or never
  installed the pre-commit hook. The `specmgr docs` drift check is pinned
  to Python 3.13 (the project's default dev version) since Python's
  `inspect` module formats docstrings differently across versions, causing
  false drift reports on Python 3.12 (see AGENTS.md for details).
- `docs/api/` committed-to-repo policy: the Markdown API reference is
  version-controlled, not generated on demand, so it renders on GitHub
  without a build step.
- **Developer experience**: documented Python version handling in AGENTS.md.
  When using a non-default Python version (e.g., 3.12 instead of 3.13),
  both `uv sync` and `uv run` require `--python X.Y` and `--all-extras` flags
  to ensure CLI/MCP dependencies are installed correctly.
- **Second domain feature (REQ tooling)**: implemented requirement/specification
  document tools and infrastructure:
  - `models/req/v1/`: Pydantic schema (`ReqFrontmatter`, `ReqBody`, `Requirement`),
    parser (`parse_req`), renderer (`render_req`), re-exported via `models/req/__init__.py`
    and `models/__init__.py`.
  - `req/tools/`: 5 `@mcp.tool()` wrappers for requirement lifecycle (`create_req`,
    `update_req`, `delete_req` stub, `set_status_req`, `parse_req`).
  - `req/resources/`: MCP resources for requirement read operations (`specmgr://req/list`,
    `specmgr://req/{id}`).
  - `req/prompts/`: `create_req` and `update_req` prompts for requirement drafting
    and revision workflows.
  - Comprehensive test coverage with 120+ passing tests under `tests/models/req/`,
    `tests/req/tools/`, `tests/req/resources/`, `tests/req/prompts/`.
- **Markdown infrastructure improvements**:
  - `models/md/`: New markdown section models (`MarkdownSection1`, `MarkdownSection2`,
    ..., `MarkdownSection6`) and optional comment mixins
    (`MarkdownSection1WithComment`, etc.) for modular document building.
  - `MarkdownComment` model for structured comment blocks within document sections.
  - Full test coverage for markdown models (25+ tests).
- **Shared cross-domain utilities**:
  - `general/tools/`: Expanded with `mdformat` tool (format markdown in place,
    preserving YAML frontmatter).
  - `general/lookup/`: New shared document path and id lookup module for consistent
    id→file-path resolution across all document types (adr, req, uc, etc.).

### Removed

- The `generate-docs`, `markdown-docs`, and `pydoc` CLI commands (and
  `docs/pydoc/` HTML output) — superseded by `specmgr docs` above. HTML
  pydoc output didn't render usefully in GitHub's file browser and
  duplicated the Markdown output.
- 6 fabricated ADRs and a stray duplicate file that had been written into
  `docs/adr/`/`doc/` by mistake.

### Fixed

- `AGENTS.md`'s auto-generated internals replaced with a short, permanent,
  hand-written pointer to `docs/GENERATED.md` — eliminates the fragile
  regex-splice logic that had produced a duplicate section.
- Corrected a stale "no `publish.yml` yet" note in `AGENTS.md`'s "CI /
  Release" section; `publish.yml` exists and has shipped `v0.1.0`,
  `v0.2.0`, `v0.2.1`.

### Changed

- **Breaking (internal-API only):** repackaged the ADR domain's interface
  layer to be domain-first (`doc/refactor-domain.md`): `tools/adr/`,
  `prompts/adr/`, and `resources/adr_get.py`/`adr_list.py` all moved under a
  new top-level `adr/` package, becoming `adr/tools/`, `adr/prompts/`, and
  `adr/resources/adr_get.py`/`adr_list.py` respectively. The now-empty
  top-level `tools/` and `prompts/` packages were removed entirely.
  `biz.dfch.specmgr.models.adr` is unchanged. No MCP-facing names change:
  tool names (`get_adr`, `create_adr`, ...), resource URIs
  (`specmgr://adr/{id}`, `specmgr://adr/list`), and prompt names
  (`create_adr`, `update_adr`, ...) are all identical -- only the Python
  import paths move. Test modules moved correspondingly:
  `tests/tools/adr/` → `tests/adr/tools/`, `tests/prompts/adr/` →
  `tests/adr/prompts/`, `tests/resources/test_adr.py` →
  `tests/adr/resources/test_adr.py`.

## [0.2.1] - 2026-08-04

### Changed

- `server.json`: corrected the MCP Registry server `name` from
  `io.github.dfch/biz.dfch.specmgr` to `io.github.dfch/biz-dfch-specmgr`,
  matching the `mcp-name` HTML comment convention (package identifier with
  hyphens, not the repo/namespace name with dots).
- `README.md`: updated the MCP Registry badge and registry search links to
  match the corrected `io.github.dfch/biz-dfch-specmgr` server name.

## [0.2.0] - 2026-08-04

### Added

- `prompts/adr/` MCP prompts module with two main workflows and two experimental variants:
  - `create_adr.py`: Prompt-driven workflow for drafting new Architecture Decision Records,
    sequencing tool calls in the correct order (context → decision drivers → options → outcome).
  - `update_adr.py`: Prompt-driven workflow for revising existing ADRs by id, supporting
    frontmatter updates, section edits, and option management.
  - `create_adr_test.py` and `update_adr_test.py`: Experimental step-gated variants with
    explicit gates (`GATE 0`…`GATE N`), exit conditions, and stricter phrasing to test
    compliance under more rigorous constraints (side-by-side A/B comparison, not yet
    recommended for production).
- `tools/adr/_lock.py`: File-locking mechanism for safe concurrent access to ADR files
  during tool operations, preventing race conditions when multiple clients modify the
  same ADR simultaneously.
- Comprehensive test coverage for all new prompts and the lock mechanism with 175 passing
  tests across `tests/prompts/adr/`, `tests/tools/adr/`, `tests/resources/`, and
  `tests/models/adr/`.
- Updated `AGENTS.md` to document the new prompt surface, experimental test variants,
  and finalized ADR tooling status (§11 in `doc/adr-tool-plan.md`).
- Updated `doc/adr-tool-plan.md` (§8 and §11) to finalize prompt design, document
  experimental variants, and mark the implementation as complete.

### Fixed

- `models/adr/v1/parser.py`: rewrote the ADR body parser to build a proper
  heading *outline tree* (`_Node`/`_build_outline`, standard table-of-contents
  nesting rules) instead of a flat H1/H2/H3 token list. Headings nested inside
  a "leaf" section (e.g. `### Postgres` under `## Considered Options`, `####
  Good`/`#### Bad` under `### Consequences`, or any heading under `## More
  Information`) are now correctly preserved as opaque section content instead
  of being misparsed or rejected with a spurious "heading level is not part
  of the ADR schema" error. Added regression tests in
  `tests/models/adr/v1/test_parser.py` covering nested headings under
  Considered Options, Consequences, Confirmation, More Information, and a
  full-document round trip.

## [0.1.0] - 2026-08-03

### Added

- Initial project scaffolding: namespace package layout
  (`src/biz/dfch/specmgr/`), `setuptools` build backend, `cli`/`mcp`/`test`/`dev`
  extras, placeholder CLI (`specmgr version`) and MCP server skeleton, CI
  workflow (`.github/workflows/ci.yml`), and governance documents
  (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `NOTICE`).
- `specmgr mcp` CLI command to start the MCP server, with `--transport`/
  `--host`/`--port` options (and matching `SPECMGR_MCP_TRANSPORT`/
  `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT` env vars), mirroring
  `biz-dfch-asdste100mcp`'s dual-transport entry point.
- `specmgr://version` MCP resource returning the installed
  `biz-dfch-specmgr` package version, plus the backing `VersionInfo` model.
- ADR (Architecture Decision Record) schema, version 1, under
  `src/biz/dfch/specmgr/models/adr/v1/` (see `doc/adr-tool-plan.md` for the
  full design): Pydantic models `AdrFrontmatter`, `AdrBody`, `AdrOption`,
  and `Adr`, covering the MADR 4.0.0-derived frontmatter block and body
  sections, including the dynamic `### Option N: {title}` collection
  backing the derived `## Pros and Cons of the Options` section.
- `parse_adr`/`AdrParseError` (`models/adr/v1/parser.py`): parses an
  on-disk ADR `.md` file's frontmatter and body into an `Adr`, using
  `python-frontmatter` for the YAML block and a `markdown-it-py` token
  walk to map fixed headings onto model fields.
- `render_adr` (`models/adr/v1/renderer.py`): renders an `Adr` back into
  the canonical MADR-derived markdown text, completing the
  parse → validate → render pipeline — always regenerating the full file
  deterministically, omitting optional sections whose field is unset, and
  emitting the derived `## Pros and Cons of the Options` container iff at
  least one option exists.
- `models/adr/v1/mutations.py`: pure, in-memory edit operations on an `Adr`
  (`update_section`, `set_status`, `option_list`, `option_create`,
  `option_read`, `option_update`, `option_delete`), implementing the §4/§5/§8
  update semantics — deletion-sentinel handling (blank or `"REMOVE"`) with
  mandatory-section rejection (`AdrSectionError`), and option lookup-by-title
  with not-found reporting (`AdrOptionNotFoundError`) — ahead of the
  file-I/O-backed MCP tool wrappers.
- Server-assigned `id` field on `AdrFrontmatter` (`models/adr/v1/frontmatter.py`,
  rendered by `renderer.py` immediately before `version`) and the new
  `AdrSummary` model (`models/adr/v1/summary.py`: id/title/status/filename),
  re-exported through `models/adr/__init__.py` and `models/__init__.py`
  (plan §9a).
- `tools/adr/` MCP tool wrappers (plan §8, §9a), each doing a
  re-read/re-parse/mutate/re-render/re-write cycle against the on-disk `.md`
  file (no in-memory cache): `get_adr`, `create_adr`, `update_frontmatter`,
  `update_section`, `set_status`, `option_list`, `option_create`,
  `option_read`, `option_update`, `option_delete`, and `validate_adr`.
  Backed by `tools/adr/_paths.py` (`SPECMGR_ADR_DIR` env var, default
  `docs/adr`; id → file-path resolution via directory scan, `slugify`,
  `AdrNotFoundError`) and `tools/adr/_io.py` (`read_adr`/`write_adr`/
  `load_by_id`).
- `specmgr://adr/list` and `specmgr://adr/{id}` MCP resources
  (`resources/adr_list.py`, `resources/adr_get.py`) — read-only,
  no-tool-round-trip counterparts of the ADR listing/`get_adr` tool,
  matching the existing `specmgr://version` resource convention. A file
  that fails to parse is skipped by `adr_list` rather than failing the
  whole listing.
- `server.json` (repo root): the MCP Registry publisher manifest, modeling
  the `biz-dfch-specmgr` `pypi` package and its `uvx --from
  biz-dfch-specmgr[mcp] python -m biz.dfch.specmgr mcp` invocation (see
  `README.md`'s "Add to OpenCode" section). Not yet publishable to the
  official registry — that requires a first PyPI release (see "Make a
  Release" in `README.md`).
- `.github/workflows/publish.yml`: release automation triggered on `v*`
  tags — builds and publishes the `sdist`/wheel to TestPyPI then PyPI via
  Trusted Publishing (OIDC, no stored token), creates the matching GitHub
  Release with the built artifacts attached, and publishes `server.json`
  to the MCP Registry via `mcp-publisher`/GitHub OIDC.
- `README.md` badges: `mcp-name` HTML comment
  (`io.github.dfch/biz.dfch.specmgr`, matching `server.json`) plus
  TestPyPI/PyPI version, PyPI downloads, and MCP Registry badges.

### Changed

- Moved each CLI command into its own module under
  `src/biz/dfch/specmgr/commands/` (`version.py`, `mcp.py`), registered
  on the Typer `app` in `cli.py` via `app.command()(fn)`, mirroring the
  `commands/` package layout used by sibling projects (e.g.
  `biz-dfch-asdste100vocab`).
- Split `tools/adr/tools.py`'s 11 `@mcp.tool()` wrappers into one module
  per tool (`get_adr.py`, `create_adr.py`, `update_frontmatter.py`,
  `update_section.py`, `set_status.py`, `option_create.py`,
  `option_update.py`, `option_read.py`, `option_delete.py`,
  `option_list.py`, `validate_adr.py`), re-exported unchanged through
  `tools/adr/__init__.py`.
