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

### Changed

- Moved each CLI command into its own module under
  `src/biz/dfch/specmgr/commands/` (`version.py`, `mcp.py`), registered
  on the Typer `app` in `cli.py` via `app.command()(fn)`, mirroring the
  `commands/` package layout used by sibling projects (e.g.
  `biz-dfch-asdste100vocab`).
