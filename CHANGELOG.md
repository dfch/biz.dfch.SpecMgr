# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Changed

- Moved each CLI command into its own module under
  `src/biz/dfch/specmgr/commands/` (`version.py`, `mcp.py`), registered
  on the Typer `app` in `cli.py` via `app.command()(fn)`, mirroring the
  `commands/` package layout used by sibling projects (e.g.
  `biz-dfch-asdste100vocab`).
