# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
