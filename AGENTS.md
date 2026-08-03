# AGENTS.md

Quick reference for OpenCode agents working on **biz.dfch.SpecMgr** — an artifact manager for system specifications.

## Status: first domain feature (ADR tooling) implemented

The ADR (Architecture Decision Record) feature described in
`doc/adr-tool-plan.md` is now implemented end-to-end and is the only domain
feature that exists — everything else is still scaffolding. Concretely:

- `models/adr/v1/` — Pydantic schema (`AdrFrontmatter`, `AdrBody`,
  `AdrOption`, `Adr`), parser (`parse_adr`), renderer (`render_adr`), and
  pure in-memory mutation functions (`update_section`, `set_status`,
  `option_*`), re-exported as "current" via `models/adr/__init__.py` and
  `models/__init__.py`.
- `tools/adr/` — 11 `@mcp.tool()` wrappers, one module per tool (`get_adr`,
  `create_adr`, `update_frontmatter`, `update_section`, `set_status`,
  `option_list`/`option_create`/`option_read`/`option_update`/
  `option_delete`, `validate_adr`), plus `_paths.py`/`_io.py` for the
  id → file-path resolution and file I/O (no in-memory cache — the `.md`
  file on disk is the sole source of truth, re-read on every call).
- `resources/adr_list.py`/`adr_get.py` — the `specmgr://adr/list` and
  `specmgr://adr/{id}` MCP resources (read-only counterparts of the above).
- 143 passing tests under `tests/models/adr/`, `tests/tools/adr/`,
  `tests/resources/`.

Still genuinely missing / not yet done (don't assume otherwise):
- No `commands/` CLI subcommand for ADRs yet (no `specmgr adr ...`) — the
  ADR feature is MCP-only so far.
- No CI/pre-commit hook runs `validate_adr` over the repo's own ADRs.
- No second document type (`req`/`uc`) exists yet, despite `models/adr/`'s
  layout being designed to generalize to them (see `doc/adr-tool-plan.md`
  §6).

`doc/adr-tool-plan.md` §10 ("Next steps") tracks per-item done/not-done
status and should be kept in sync with `src/` as this evolves; treat it as
current-state tracking, not just a historical design doc. Don't assume any
other `models/`, `tools/`, or `resources/` sub-package exists beyond `adr`/
`version_info` (models) and `adr`/`version` (resources/tools) — check first.

## Project Shape

- **Type**: Python library + optional CLI + optional MCP server, in one repo
- **Namespace**: `biz.dfch.specmgr` in `src/biz/dfch/specmgr/` — `biz`/`biz/dfch`
  are implicit namespace packages (no `__init__.py` in those two dirs; only the
  leaf `specmgr/` has one)
- **Package manager**: `uv` (not pip) — lockfile is committed, use `--frozen`
- **Python**: `requires-python = ">=3.11"` (3.11–3.13 tested in CI); local dev
  defaults to 3.13 via `.python-version` — two separate settings, keep in
  sync intentionally, not by accident

## Developer Commands

```bash
uv sync --all-extras                                                   # install deps
uv run --frozen ruff format --check && uv run --frozen ruff check      # lint (enforced)
uv run --frozen pylint $(git ls-files '*.py')                          # lint (advisory only; CI runs it with `|| true`)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"  # tests
uv run --frozen specmgr version                                        # run the CLI
```

`pylint` only sees files tracked by git (`git ls-files`) — new files must be
`git add`ed before it will lint them, both locally and in CI.

## Extras split (base library has no CLI/MCP deps)

`dependencies` in `pyproject.toml` is only `pydantic` + `python-dotenv`, so the
library is usable standalone. `typer`/`rich` live in the `cli` extra, `mcp` in
the `mcp` extra. **Never** import `cli.py` or `server.py` from
`src/biz/dfch/specmgr/__init__.py` — that would force those extras onto every
consumer of the base library.

## CLI (`cli.py`)

- Typer app, entry point `specmgr` (`pyproject.toml` `[project.scripts]`);
  `python -m biz.dfch.specmgr` (`__main__.py`) runs the same Typer `app()`.
- **Gotcha**: with only one `@app.command()` registered, Typer collapses to a
  single top-level command and drops subcommand dispatch (`specmgr version`
  would fail with "unexpected extra argument"). An explicit `@app.callback()`
  (see `_callback` in `cli.py`) forces Typer to keep treating it as a command
  group — keep that callback even after a second command is added, don't
  assume it becomes dead code to remove.

## MCP server (`server.py`)

- Currently just builds an `MCPServer` instance (`mcp` object) and a no-op
  `_lifespan`. **Nothing calls `mcp.run()` anywhere** — there is no working
  "start the server" command yet, despite what an entry-point name might
  suggest. Don't assume `python -m biz.dfch.specmgr` starts an MCP server —
  it runs the Typer CLI (see above).
- When adding tools/resources: follow the sibling-project convention of
  `tools/`/`resources/` sub-packages, importing them as the **last line** of
  `server.py` so their `@mcp.tool()`/`@mcp.resource()` decorators actually
  run. Forgetting that import means a new tool silently never registers.

## CI / Release

- Branches: `dev` (default, feature work) → `main` (stable) → tag.
- `.github/workflows/ci.yml`: ruff + pylint (`|| true`) + unittest, matrix
  3.11/3.12/3.13, via `uv sync --frozen --all-extras`.
- No `publish.yml` yet — PyPI/MCP-Registry publishing is deferred until
  there's a first release worth shipping (see `README.md` § "Make a Release").
- Version bumps: update `version` in `pyproject.toml` (single source) and
  move `CHANGELOG.md`'s `[Unreleased]` into a dated section, same commit.

## Code Style

- Formatter/linter: `ruff` (enforced, not black), line length 120.
- `pylint` is advisory fallback only (see pylint caveat above).
