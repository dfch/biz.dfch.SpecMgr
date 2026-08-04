# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
