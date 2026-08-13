# biz.dfch.SpecMgr

<!-- mcp-name: io.github.dfch/biz-dfch-specmgr -->

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
[![Lint and Test](https://github.com/dfch/biz.dfch.SpecMgr/actions/workflows/ci.yml/badge.svg)](https://github.com/dfch/biz.dfch.SpecMgr/actions/workflows/ci.yml)
![Coverage](docs/coverage.svg)
[![TestPyPI version](https://img.shields.io/badge/dynamic/json?url=https://test.pypi.org/pypi/biz-dfch-specmgr/json&label=TestPyPI&query=$.info.version&color=orange)](https://test.pypi.org/project/biz-dfch-specmgr/)
[![PyPI version](https://img.shields.io/badge/dynamic/json?url=https://pypi.org/pypi/biz-dfch-specmgr/json&label=PyPI&query=$.info.version&color=blue)](https://pypi.org/project/biz-dfch-specmgr/)
[![PyPI downloads](https://img.shields.io/pypi/dm/biz-dfch-specmgr.svg)](https://pypistats.org/packages/biz-dfch-specmgr)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.dfch%2Fbiz--dfch--specmgr-8A2BE2.svg)](https://registry.modelcontextprotocol.io/?q=io.github.dfch/biz-dfch-specmgr)

An artifact manager for system specifications.

This project is a **library**, a **CLI**, and an **MCP server**, all in one
repository. The CLI and MCP server are optional — install only what you
need via extras (see [Installation](#installation)).

_Status: first domain feature shipped. Architecture Decision Record (ADR)
management — creating, reading, and editing MADR 4.0.0-derived ADRs — is
implemented end-to-end as MCP tools/resources (see
[MCP Server](#mcp-server) below and `.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` for the full
design). It is MCP-only so far: there is no `specmgr adr ...` CLI command
yet, and no second document type beyond ADRs._

## Table of Contents

- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [MCP Server](#mcp-server)
- [Development](#development)
- [Make a Release](#make-a-release)
- [License](#license)

## Installation

As a library only (no CLI, no MCP server):

```bash
pip install biz-dfch-specmgr
```

With the CLI:

```bash
pip install "biz-dfch-specmgr[cli]"
```

With the MCP server:

```bash
pip install "biz-dfch-specmgr[mcp]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add "biz-dfch-specmgr[cli,mcp]"
```

## CLI Usage

_No ADR (or other domain) commands exist yet — only `version` and `mcp`
(below). ADR management is currently MCP-only, see [MCP Server](#mcp-server)._

```bash
specmgr version
```

## MCP Server

Requires the `mcp` extra. In addition to the `specmgr://version` resource,
the server exposes a full set of Architecture Decision Record (ADR) tools
and resources, implementing the MADR 4.0.0-derived schema described in
`.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md`:

| Kind     | Name(s)                                                                                                                                   | Description                                                     |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Resource | `specmgr://version`                                                                                                                         | Installed `biz-dfch-specmgr` package version                      |
| Resource | `specmgr://adr/list`                                                                                                                        | Id/title/status/filename of every ADR                             |
| Resource | `specmgr://adr/{id}`                                                                                                                        | Full ADR document (frontmatter + body) by id                      |
| Tool     | `get_adr`, `create_adr`, `update_frontmatter`, `update_section`, `set_status`, `option_list`, `option_create`, `option_read`, `option_update`, `option_delete`, `validate_adr` | Structured create/read/update operations over one ADR, by id |

ADRs live as `.md` files in a base directory (default `docs/adr`,
configurable via the `SPECMGR_ADR_DIR` environment variable) — the file on
disk is always the source of truth, re-read and re-parsed on every tool
call, so hand-editing a file between calls is safe.

Start the server with the `mcp` command:

```bash
specmgr mcp
```

By default it runs over `stdio`, for MCP hosts that launch it as a
subprocess (see [Add to OpenCode](#add-to-opencode) below). It can also
run over SSE/network:

```bash
specmgr mcp --transport sse --host localhost --port 8000
```

| Option              | Env var                 | Default     | Description                     |
| -------------------- | ------------------------ | ----------- | -------------------------------- |
| `--transport` / `-t` | `SPECMGR_MCP_TRANSPORT` | `stdio`     | Transport mode: `stdio` or `sse` |
| `--host` / `-h`      | `SPECMGR_MCP_HOST`      | `localhost` | Bind address (SSE mode only)     |
| `--port` / `-p`      | `SPECMGR_MCP_PORT`      | `8000`      | TCP port (SSE mode only)         |

### Add to OpenCode

To add the `specmgr` MCP server to your OpenCode configuration:

1. Open your OpenCode config file (typically `~/.config/opencode/opencode.json` or `~/.config/opencode/opencode.jsonc`)

2. Add the following configuration to the `mcp` section (and use it via `stdio`):

```json
"specmgr": {
  "type": "local",
  "enabled": true,
  "command": ["uvx", "--from", "biz-dfch-specmgr[mcp]", "python", "-m", "biz.dfch.specmgr", "mcp"]
}
```

3. Save the file and restart OpenCode

## Development

### Install dev dependencies

```bash
uv sync --all-extras
```

### Run linters

```bash
uv run --frozen ruff format --check
uv run --frozen ruff check
uv run --frozen pylint $(git ls-files '*.py')
```

### Run tests

```bash
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"
```

## Make a Release

### 1. Make sure all tests pass

Before releasing, make sure the CI pipeline is green on the `dev` branch:

```bash
uv run --frozen ruff format --check
uv run --frozen ruff check
uv run --frozen pylint $(git ls-files '*.py')
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"
```

### 2. Increase the version

Update the version in `pyproject.toml`:

```toml
version = "x.y.z"
```

Move the `[Unreleased]` section in `CHANGELOG.md` into a new dated
`## [x.y.z] - YYYY-MM-DD` section.

Also update both `version` fields in `server.json` (the top-level one and
the one under `packages[0]`) to match — the MCP Registry manifest must
stay in lockstep with `pyproject.toml`.

### 3. Commit and push to `dev`

```bash
git add pyproject.toml CHANGELOG.md server.json
git commit -m "chore: bump version to vx.y.z"
git push origin dev
```

### 4. Merge `dev` into `main`

```bash
git checkout main
git merge dev
git push origin main
```

### 5. Create and push a version tag

```bash
export VERSION=x.y.z
git tag v${VERSION}
git push origin v${VERSION}
```

_Note: `.github/workflows/publish.yml` handles the rest of the release
automatically once the tag above is pushed — it builds and publishes the
`sdist`/wheel to TestPyPI then PyPI via Trusted Publishing (OIDC, no
stored token), creates the matching GitHub Release with the built
artifacts attached, and publishes `server.json` (repo root, the MCP
Registry publisher manifest — see the
[server.json format spec](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md))
to the [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)
via `mcp-publisher`/GitHub OIDC. `biz-dfch-specmgr` is live on
[PyPI](https://pypi.org/project/biz-dfch-specmgr/) and in the
[MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)
as of `v0.1.0`._

Then switch back to `dev` to continue work:

```bash
git checkout dev
```

## License

[AGPL-3.0-or-later](LICENSE)
