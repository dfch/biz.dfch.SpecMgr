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

This project is an **MCP server** that you can use to manage different
specification artifacts.

At this time, we have these artifact types:

- Architecture Decision Record (ADR) (deprecated, will be phased out, use DEC instead)
- Decision (DEC)
- Feature (FEAT)
- Goal (GOL)
- Problem Statement (PRB)
- Question and Answer (QA)
- Requirement (REQ)
- Risk (RSK)
- Standard Operating Procedure (SOP)
- System Requirements Specification (SYSRS)
- Task List (TSK)
- Use Case (UC)
- Verification Case Record (VCR)

See [MCP Server](#mcp-server) and [docs/MCP.md](docs/MCP.md) for details.

The **MCP server** (and the management **CLI**) are optional. You install
them as "extras" (see [Installation](#installation)).

## Table of Contents

- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [MCP Server](#mcp-server)
- [Development](#development)
- [Testing](#testing)
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

With the CLI you can generate schema and documentation. We use these commands
in pre-commit hooks and `ci.yml`.

_No domain document-management commands (create/update/status/etc.) exist
in the CLI yet — those are currently MCP-only, see
[MCP Server](#mcp-server). The CLI covers `version`, `mcp` (below), and a
handful of cross-cutting/doc-generation commands (`specmgr --help` for the
full list)._

```bash
specmgr version
```

## MCP Server

Requires the `mcp` extra. The server exposes resources, tools, and prompts
for document management, plus cross-cutting utilities (e.g. markdown
formatting).

**The full, up-to-date list of every resource, resource template, tool, and
prompt — with parameters, MIME types, and descriptions — lives in
[docs/MCP.md](docs/MCP.md).** That document generated from the live server
registration by `specmgr mcp-docs` and kept in sync by a pre-commit hook and
a CI check.

### Environment Variables

Every document type stores its `.md` files in a base directory on disk —
the file is always the source of truth, re-read and re-parsed on every
tool call, so hand-editing a file between calls is safe.

- ADRs: base directory defaults to `docs/adr`, configurable via the
  `SPECMGR_ADR_DIR` environment variable. This is ADR-specific and not
  shared with other document types.
- Requirements (REQ) and future document types: share one root directory,
  configurable via the `SPECMGR_DOCS_DIR` environment variable (default
  `docs`), with each type's own subdirectory appended automatically (e.g.
  `docs/req` for requirements).
- Features (FEAT): base directory defaults to `.specmgr/feat`, configurable
  via the `SPECMGR_FEAT_DIR` environment variable. This is FEAT-specific,
  like ADRs above, and not shared via `SPECMGR_DOCS_DIR`.
- The `confluence_fetch` tool (renamed from `webfetch`; bearer-authenticated,
  URL-filtered HTTP GET, intended primarily for Confluence instances using
  PAT authentication) requires two environment variables:
  `SPECMGR_CONFLUENCE_BASE_URL` (the base URL requested URLs must
  case-insensitively start with) and `SPECMGR_CONFLUENCE_BEARER` (the
  bearer token sent as the `Authorization` header). Both must be set or the
  tool raises an error; there are no defaults.

All of the base directories above are resolved relative to the MCP server
process's own current working directory unless overridden by their env var
(or, for the shared `SPECMGR_DOCS_DIR` root, unless the server was started
with `--directory`/`uv run --directory` targeting your project). If that
CWD is not what you expect — e.g. after adding `specmgr` to an MCP host
per [Add to OpenCode](#add-to-opencode) below — read the `specmgr://config`
resource to see every domain's actually-resolved absolute base directory
and whether its env var is explicitly set, without needing shell access to
the server's host.

### Start the MCP Server

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

Or over the spec-current `streamable-http` transport, which replaces the
legacy/deprecated `sse` transport for HTTP deployments:

```bash
specmgr mcp --transport streamable-http --host localhost --port 8000
```

| Option | Env var | Default | Description |
| -------------------- | ------------------------ | ----------- | -------------------------------- |
| `--transport` / `-t` | `SPECMGR_MCP_TRANSPORT` | `stdio` | Transport mode: `stdio`, `sse`, or `streamable-http` |
| `--host` / `-h` | `SPECMGR_MCP_HOST` | `localhost` | Bind address (SSE/streamable-http mode only) |
| `--port` / `-p` | `SPECMGR_MCP_PORT` | `8000` | TCP port (SSE/streamable-http mode only) |

### Add to OpenCode

To add the `specmgr` MCP server to your OpenCode configuration:

1. Open your OpenCode config file (typically `~/.config/opencode/opencode.json` or `~/.config/opencode/opencode.jsonc`)

2. Add a configuration to the `mcp` section (and use it via `stdio`).

   **A bare `uvx --from biz-dfch-specmgr[mcp] specmgr mcp` command with no
   `--directory` and no `SPECMGR_*_DIR` env vars is unsafe**: the server
   resolves every base directory (`docs`, `docs/adr`, `.specmgr/feat`, ...)
   relative to its own process's current working directory, which an MCP
   host is free to launch from anywhere — not necessarily your project
   root. Pick one of the two options below instead of the plain form:

   **Option A — pin the working directory with `--directory`** (a global
   `uv`/`uvx` flag, so it must come *before* `--from`):

   ```json
   "specmgr": {
     "type": "local",
     "enabled": true,
     "command": [
       "uvx",
       "--directory",
       "<path-to-your-project>",
       "--from",
       "biz-dfch-specmgr[mcp]",
       "specmgr",
       "mcp"
     ]
   }
   ```

   **Option B — set the directory env vars explicitly** instead of (or in
   addition to) `--directory`:

   ```json
   "specmgr": {
     "type": "local",
     "enabled": true,
     "command": [
       "uvx",
       "--from",
       "biz-dfch-specmgr[mcp]",
       "specmgr",
       "mcp"
     ],
     "environment": {
       "SPECMGR_DOCS_DIR": "<path-to-your-project>/docs",
       "SPECMGR_ADR_DIR": "<path-to-your-project>/docs/adr",
       "SPECMGR_FEAT_DIR": "<path-to-your-project>/.specmgr/feat"
     }
   }
   ```

   Either option (or both together) makes the resolved base directories
   independent of wherever the MCP host happens to launch the server
   from. Whichever you choose, you can confirm it worked by reading the
   `specmgr://config` resource, which reports the actually-resolved
   absolute base directory for every domain and whether its env var is
   explicitly set.

3. Save the file and restart OpenCode

## Development

### Install dev dependencies

```bash
uv sync --all-extras
```

### Install pre-commit hooks (one-time)

```bash
uv run --frozen pre-commit install
```

`uv sync` only installs Python dependencies into the venv — it never
registers the hooks from `.pre-commit-config.yaml` with git, so run
this once per clone before your first commit.

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

## Testing

You can exercise the MCP server directly with the
[MCP Inspector](https://modelcontextprotocol.io/docs/latest/tools/inspector),
in either its CLI (scriptable) or TUI (interactive terminal) client.

### Prerequisites

- The `mcp` extra installed (see [Installation](#installation)), so
  `.venv/bin/specmgr` exists.
- [`npx`](https://docs.npmjs.com/cli/v10/commands/npx) (ships with Node.js,
  version 22.19.0 or newer) — no separate Inspector install is required, it
  runs on demand via `npx @modelcontextprotocol/inspector`.

Point the Inspector at the venv's `specmgr` binary directly (rather than at
`uv run specmgr mcp`) so none of `uv run`'s own flags (e.g. `--frozen`) are
mistaken for Inspector flags:

```bash
npx @modelcontextprotocol/inspector --tui .venv/bin/specmgr mcp
npx @modelcontextprotocol/inspector --cli .venv/bin/specmgr mcp --method tools/list
```

### CLI examples

Each CLI invocation connects, runs one request, prints the result, and
exits — useful for scripting or a quick smoke test.

Get the `specmgr://version` resource:

```bash
npx @modelcontextprotocol/inspector --cli .venv/bin/specmgr mcp \
  --method resources/read --uri specmgr://version
```

List task lists via the `list_tsk` tool:

```bash
npx @modelcontextprotocol/inspector --cli .venv/bin/specmgr mcp \
  --method tools/call --tool-name list_tsk
```

Get one task list via the `get_tsk` tool (replace `<id>` with a real task
list id from the `list_tsk` output above):

```bash
npx @modelcontextprotocol/inspector --cli .venv/bin/specmgr mcp \
  --method tools/call --tool-name get_tsk --tool-arg id=<id>
```

Add `--format json` to any of the above to get machine-readable output,
e.g. piped into `jq`.

### Connecting with the TUI

```bash
npx @modelcontextprotocol/inspector --tui .venv/bin/specmgr mcp
```

This launches the server as an ad-hoc stdio target and opens the terminal
UI with it preselected (unlike the CLI, the TUI has no `--server <name>`
flag — it lists whichever servers are available and you pick one, though
with a single ad-hoc target there is nothing else to pick). **Press `c` to
connect**, then use the tabs to explore:

- `t` — **Tools** tab: browse and call tools (e.g. `get_tsk`) with a
  form-based input.
- `r` — **Resources** tab: browse and read resources (e.g.
  `specmgr://version`, `specmgr://iso25010`).
- `m` — **Prompts** tab: list and render prompts.
- `p` — **Protocol** tab: raw JSON-RPC request/response history, useful
  for debugging.
- `o` — **Console** tab: `stderr` from the connected `specmgr mcp`
  process (tracebacks land here).
- `c` / `d` — connect / disconnect; `Esc` or `Ctrl+C` — exit.

The TUI requires a real TTY (raw-mode support) and does not run in a
headless CI job — use the CLI client there instead.

## Make a Release

The normative release procedure is the SOP
[Perform a release of biz.dfch.SpecMgr](docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md)
(SOP `98537416`). Where this section, the script, or the command ever
disagree with the SOP, the SOP wins.

### Using the OpenCode command (recommended)

```
/release [X.Y.Z | patch | minor | major] [--dry-run]
```

The command drives the staged script and performs the SOP's agent-judgment
steps: it confirms the resolved version with you, curates the changelog's
`[Unreleased]` section, pauses at the merge gate before `dev` is merged
into `main`, and triages failures without ever auto-retrying.

### Using the script directly

Each SOP step maps to a deterministic, idempotent stage (the SOP carries
a manual fallback command for every step):

```bash
scripts/release.sh resolve minor         # print the target version (e.g. 0.15.0); no mutation
scripts/release.sh precheck 0.15.0       # fail-fast pre-release checks
scripts/release.sh bump 0.15.0           # pyproject.toml + uv.lock
scripts/release.sh changelog 0.15.0      # [Unreleased] -> dated section
scripts/release.sh commit-push 0.15.0    # 3-file release commit, push dev, wait for CI
scripts/release.sh pr-create 0.15.0      # dev->main release PR, wait for checks (no merge)
scripts/release.sh pr-merge 0.15.0       # ff-only merge (after maintainer go-ahead)
scripts/release.sh tag-push 0.15.0       # tag on main, push the tag, back to dev
scripts/release.sh publish-wait 0.15.0   # the four publish.yml jobs
scripts/release.sh release-notes 0.15.0  # verify the release + set the GH release notes
scripts/release.sh status 0.15.0         # where does this release stand?
scripts/release.sh all 0.15.0            # the whole chain, TTY only (interactive merge gate)
```

Changelog *curation* (SOP step 3) is an agent or manual step: the
`changelog` stage only moves the already-curated `[Unreleased]` section
into its dated form.

### Manual fallback

Follow the SOP step by step — each step carries a *Manual fallback*
paragraph. The essentials: bump the `version` in `pyproject.toml` and
move the `[Unreleased]` section of `CHANGELOG.md` into a new dated
`## [x.y.z] - YYYY-MM-DD` section; `uv lock`; commit exactly
`pyproject.toml` + `uv.lock` + `CHANGELOG.md` as
`chore(release): bump version to vX.Y.Z` and push to `dev`; once CI is
green, open the `dev` → `main` pull request and merge it
**fast-forward-only** (`git merge --ff-only dev` — never a merge commit or
squash: `main` must stay a strict ancestor of `dev`); then create
`git tag vX.Y.Z` on `main`, push the tag, and wait for the publish
workflow.

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

## License

[AGPL-3.0-or-later](LICENSE)
