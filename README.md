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
specification artifacts — see [Concepts](#concepts) for the full list of
artifact types and how they relate, and [MCP Server](#mcp-server) /
[docs/MCP.md](docs/MCP.md) for the tool/resource/prompt reference.

The **MCP server** (and the management **CLI**) are optional. You install
them as "extras" (see [Installation](#installation)).

## Table of Contents

- [Concepts](#concepts)
- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [MCP Server](#mcp-server)
- [Usage](#usage)
- [Referencing Artifacts](#referencing-artifacts)
- [Development](#development)
- [Testing](#testing)
- [Make a Release](#make-a-release)
- [License](#license)

## Concepts

Every artifact is a plain markdown file with a YAML frontmatter block on
disk — git-friendly, diffable, and readable/editable by hand. The
filesystem is always the source of truth; the MCP server wraps it with
structured, validated read/write/list/status tools (see
[Usage](#usage)).

| Type | Purpose |
| --- | --- |
| QA — Question and Answer | Structured elicitation interview (organized by ISO/IEC 25010 characteristic) capturing stakeholder Q&A; usually where a new spec effort *starts* |
| GOL — Goal | High-level business goal — what the organization wants to achieve, above individual requirements |
| PRB — Problem Statement | Six-Sigma-style problem statement describing the problem a goal/requirement addresses |
| REQ — Requirement | A single system requirement (EARS-style phrasing), classified by ISO/IEC 25010 characteristic |
| UC — Use Case | Actor/system interaction describing a specific usage scenario |
| RSK — Risk | Risk-register entry: cause/trigger/consequence, 5x5 probability/impact assessment (initial + residual), TARA response strategy |
| DEC — Decision | General-purpose decision record (MADR-style), not limited to architecture |
| ADR — Architecture Decision Record | Architecture-specific decision record; **deprecated**, use DEC instead |
| TSK — Task List | Checklist of implementation tasks, e.g. for a requirement or feature |
| VCR — Verification Case Record | Verifies **exactly one** REQ or UC; holds a collection of `AC-NNN` acceptance criteria (each with a DTAIS verification method) plus one overall coverage outcome (full/partial/none) |
| SOP — Standard Operating Procedure | Step-by-step operational procedure with RASCI responsibility assignment and approval lifecycle |
| FEAT — Feature | Development work-unit plan/progress tracking (`.specmgr/feat/<id>/README.md`) |
| SYSRS — System Requirements Spec | Aggregates GOL/PRB/QA/UC/REQ/RSK/DEC-ADR/VCR via cross-reference lists into one navigable spec; its structure follows **ISO/IEC/IEEE 29148:2018** (Systems and software engineering — Life cycle processes — Requirements engineering), with a few specmgr-only additions (e.g. `## Decisions`, `## Risks`) |

A typical spec effort starts with a **QA** elicitation interview, which
surfaces **GOL**s (goals) and **PRB**s (problems). Those inform **REQ**s
and **UC**s, which get risk-assessed (**RSK**) and backed by
**DEC**isions, verified via one **VCR** per REQ/UC (each collecting its
acceptance criteria), and tracked via **TSK** task lists. A **SYSRS**
ties all of it together into one ISO/IEC/IEEE 29148-structured
specification. **SOP** and **FEAT** support the process itself rather
than sitting in this chain.

```
QA -> GOL / PRB -> REQ / UC -> RSK / DEC -> TSK, VCR -> SYSRS (aggregates all)
```

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

With semantic-similarity search (`find_related`/`find_similar_text`, see
[MCP Server](#mcp-server) below), add the `similarity` extra on top of `mcp`:

```bash
pip install "biz-dfch-specmgr[mcp,similarity]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add "biz-dfch-specmgr[cli,mcp,similarity]"
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

The `find_related`/`find_similar_text` tools (semantic-similarity search,
requires the `similarity` extra) load a local sentence-embedding model
(`fastembed`/`bge-small`) on first use. Set the `SPECMGR_SIMILARITY_DISABLED`
environment variable (to any non-empty value) to turn this feature off —
e.g. to skip the model download/load entirely, or if the `similarity` extra
isn't installed. Both tools stay registered either way; when disabled (or
when the backend/model fails to load), they return a structured
`{available: false, reason, message}` result instead of raising.

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

## Usage

Once connected, your AI assistant sees two kinds of tools per document
domain: **per-domain** tools (`create_<d>`, `get_<d>`, `list_<d>`,
`parse_<d>`, plus `get_<d>_example`/`get_<d>_template`), and **generic
dispatch** tools that take a `type=` parameter and behave the same way
across every domain: `update` (whole-body or line-range edits),
`set_status`, `set_classification`, `delete`, and `validate` (ADR is the
one exception, predating this pattern, with its own dedicated tools
instead). See [docs/MCP.md](docs/MCP.md) for the full list.

The server also ships **prompts** (e.g. `create_req`, `update_req`,
`implement_task`) — guided, multi-turn interview flows that are the
intended way to author documents conversationally, rather than calling
tools one by one. Most MCP hosts surface these as slash commands or a
prompt picker.

Day to day, you don't need to know any tool names at all — just ask your
connected AI assistant in plain language, e.g.:

- "Create a new goal for reducing customer onboarding time."
- "List all open risks and show me the high-severity ones."
- "Draft a task list for requirement `<id>`."

To resolve the cross-references an artifact already carries, see
[Referencing Artifacts](#referencing-artifacts).

## Referencing Artifacts

specmgr documents cross-reference each other via `<TYPE> <uuid>` lines
(VCR's `## Verifies`, SYSRS's per-section bullet lists, DEC's `## Related
Artifacts`). The `list_references` MCP tool resolves those references:
point your assistant at any artifact (`<type> <id>`) and it lists every
`<TYPE> <uuid>` cross-reference in the artifact's body, each resolved to
the referenced document's type, id, title (its H1), and on-disk path.
Results are paged like every `list_*` tool; references that do not
resolve on disk come back as rows carrying an `error` (not a failure),
and free-form or non-uuid references are ignored.

In [opencode](https://opencode.ai), the `/refs <type> <id>` slash command
(`.opencode/command/refs.md`) wraps the same tool: it delegates to the
read-only `ref-finder` subagent (`.opencode/agent/ref-finder.md`), which
calls `list_references` and reports the rows, flagging any **NOT FOUND**
references. `/refs` requires opencode — the tool itself is plain MCP,
callable directly from any MCP client.

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
uv run --frozen pytest -n auto --cov=src --cov-report=
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
