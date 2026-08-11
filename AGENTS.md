# AGENTS.md

Quick reference for OpenCode agents working on **biz.dfch.SpecMgr** — an artifact manager for system specifications.

## Status: first domain feature (ADR tooling) implemented

The ADR (Architecture Decision Record) feature described in
`.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` is now implemented end-to-end and is the only domain
feature that exists — everything else is still scaffolding. Concretely:

- `models/adr/v1/` — Pydantic schema (`AdrFrontmatter`, `AdrBody`,
  `AdrOption`, `Adr`), parser (`parse_adr`), renderer (`render_adr`), and
  pure in-memory mutation functions (`update_section`, `set_status`,
  `option_*`), re-exported as "current" via `models/adr/__init__.py` and
  `models/__init__.py`.
- `adr/tools/` — 11 `@mcp.tool()` wrappers, one module per tool (`get_adr`,
  `create_adr`, `update_frontmatter`, `update_section`, `set_status`,
  `option_list`/`option_create`/`option_read`/`option_update`/
  `option_delete`, `validate_adr`), plus `_paths.py`/`_io.py` for the
  id → file-path resolution and file I/O (no in-memory cache — the `.md`
  file on disk is the sole source of truth, re-read on every call).
- `adr/resources/adr_list.py`/`adr_get.py` — the `specmgr://adr/list` and
  `specmgr://adr/{id}` MCP resources (read-only counterparts of the above).
- `adr/prompts/create_adr.py`/`update_adr.py` — two `@mcp.prompt()`s
   returning instructional text that drives the `adr/tools/` surface above
   in the right order (draft-a-new-ADR and revise-an-existing-ADR-by-id
   flows respectively); see `.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` §11.
- `adr/prompts/create_adr_test.py`/`update_adr_test.py` — step-gated
   (`GATE 0`..`GATE N`, explicit exit conditions, "never fabricate a
   value") experimental variants of the two prompts above, registered
   under distinct names for side-by-side A/B comparison; neither
   supersedes the narrated originals. See `.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` §11.
- 186 passing tests under `tests/models/adr/`, `tests/adr/tools/`,
  `tests/adr/resources/`, `tests/adr/prompts/`.

`adr/` (`adr/tools/`, `adr/prompts/`, `adr/resources/`) is a top-level,
domain-first package — see `.specmgr/feat/feat-0-doc-in-specmgr/refactor-domain.md` for the rationale and
migration record (ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain: domain-first hierarchy for tools/prompts/resources, shared versioned models"). The ADR *schema* layer, `models/adr/`, deliberately stays
under the shared top-level `models/` package instead of moving into `adr/`,
since it has no dependency on `mcp`/`tools`/`resources`/`prompts` and is
meant to stay importable standalone.

Still genuinely missing / not yet done (don't assume otherwise):
- **`specmgr adr-toc`** — a CLI command that generates a table of contents
  (`docs/adr/README.md`) listing all ADRs with their titles, frontmatter
  (id, status, date, decision-makers, consulted, informed), and links to the
  actual ADR files. Integrated into pre-commit hooks and CI (Python 3.13 only,
  consistent with `specmgr docs`). (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73)
- No `validate_adr` tool runs over the repo's own ADRs yet via pre-commit or CI.
  (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI")
- No second document type (`req`/`uc`) exists yet, despite `adr/`'s
   domain-first layout and `models/adr/`'s internal layout being designed to
   generalize to them (see `.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` §6, `.specmgr/feat/feat-0-doc-in-specmgr/refactor-domain.md`).

`.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` §10 ("Next steps") tracks per-item done/not-done
status and should be kept in sync with `src/` as this evolves; treat it as
current-state tracking, not just a historical design doc. Don't assume any
other domain package exists beyond `adr` (with its `tools`/`prompts`/
`resources` sub-packages), or any other `models/` sub-package beyond
`adr`/`version_info`, or anything in the top-level `resources/` package
beyond `version` — check first.

## Project Shape

- **Type**: Python library + optional CLI + optional MCP server, in one repo
- **Namespace**: `biz.dfch.specmgr` in `src/biz/dfch/specmgr/` — `biz`/`biz/dfch`
  are implicit namespace packages (no `__init__.py` in those two dirs; only the
  leaf `specmgr/` has one)
- **Package manager**: `uv` (not pip) — lockfile is committed, use `--frozen`
- **Python**: `requires-python = ">=3.11"` (3.11–3.13 tested in CI); local dev
  defaults to 3.13 via `.python-version` — two separate settings, keep in
  sync intentionally, not by accident

## Development Artifacts (`.specmgr/`)

Per ADR e369ee2e-3353-4f92-991c-6367d76d832e ("Organize development
artifacts in `.specmgr` with feature-driven work units"), development
planning/progress artifacts live under `.specmgr/`, separate from published
documentation in `docs/`:

```
.specmgr/
├── _template/
│   └── v1/
│       └── README.md              # Versioned feature template (plan + progress)
└── feat/
    └── feat-NNN-slug/              # One folder per GitHub issue
        ├── README.md               # Feature plan + progress (mandatory)
        └── history.md              # Archived older "Recent Updates" entries (optional)
```

- **Naming convention**: `feat-NNN-slug`, where `NNN` is the GitHub issue
  number. Work started without an issue yet uses `feat-0-slug` (issue number
  `0`) until/unless an issue is later opened for it.
- **Single `README.md` per feature** combines the plan (requirements,
  acceptance criteria, scope, dependencies, design notes) and progress
  (current status, blockers, recent updates, decisions made) — there is no
  separate `progress.md`; status lives inline on each task line, edited in
  place rather than duplicated.
- **Template**: `.specmgr/_template/v1/README.md` is the versioned,
  reusable template (copy it when starting a new feature folder). It is
  hand-copied, not scaffolded by any tool — no automation exists for this
  yet, and none is currently planned.
- **Frontmatter**: every feature `README.md` starts with a minimal YAML
  frontmatter block — `id` (the `feat-NNN-slug` folder name itself, not a
  generated UUID), `version` (semver, starts at `1.0.0`), `status`
  (`planning` | `in-progress` | `review` | `done`), and `created`/`updated`
  (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no
  separate `GitHub Issue` field/body-line: the issue number is the `NNN`
  infix already embedded in `id`/the folder name (`feat-NNN-slug`) — `0`
  means no issue yet — so it is never duplicated elsewhere in the file. See
  ADR e369ee2e-3353-4f92-991c-6367d76d832e's Option 1 for the full
  rationale.
- **`doc/` has been migrated** into this structure — development planning docs
   now live in `.specmgr/feat/` with their respective feature folders.
- **No CI/pre-commit enforcement** exists for `.specmgr/` content — unlike
  `docs/adr/`, there is no `validate_adr`-equivalent check and no `adr-toc`-
  equivalent generation step wired into hooks or CI for feature folders.
- **ADR vs. feature-level "Decisions Made" log**: a decision belongs in a
  full ADR (`docs/adr/`) if it's architecture/structure-level, affects more
  than one feature or the repo as a whole, or reverses/supersedes a previous
  ADR. It belongs in the feature's own "Decisions Made" log instead if it's
  scoped entirely to that feature's implementation details. When in doubt,
  write the ADR.
- Existing feature folders: `.specmgr/feat/feat-0-doc-in-specmgr/`
   (development artifacts migration), `.specmgr/feat/feat-4-use-cases/` (use-case
   modeling and examples), `.specmgr/feat/feat-5-md-model-parser/` (markdown
   parsing infrastructure).

## Developer Commands

```bash
uv sync --all-extras                                                   # install deps
uv run --frozen pre-commit install                                     # one-time: enable pre-commit hooks
uv run --frozen ruff format --check && uv run --frozen ruff check      # lint (enforced)
uv run --frozen pylint $(git ls-files '*.py')                          # lint (advisory only; CI runs it with `|| true`)
uv run --frozen vulture src/ whitelist.py --min-confidence 60          # dead-code check (enforced)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"  # tests
uv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md
uv run --frozen specmgr adr-toc                                        # regenerate docs/adr/README.md (ADR table of contents)
uv run --frozen specmgr unused-code                                    # report unused code in src/ (same check as the vulture hook)
uv run --frozen specmgr unused-code --test                             # report symbols only referenced from tests/, never src/
uv run --frozen specmgr version                                        # run the CLI
```

### Using a different Python version

The project defaults to Python 3.13 (see `.python-version`). To use a different version (e.g., 3.12), add `--python X.Y` to **both** `uv sync` and `uv run` commands, and include `--all-extras` on the `uv run` call:

```bash
uv sync --all-extras --frozen --python 3.12
uv run --frozen --all-extras --python 3.12 specmgr docs
```

Without `--all-extras` on `uv run`, only base dependencies are installed, causing `ModuleNotFoundError` for CLI/MCP extras like `typer`.

`pylint` only sees files tracked by git (`git ls-files`) — new files must be
`git add`ed before it will lint them, both locally and in CI.

`pre-commit install` is one-time per clone (see `.pre-commit-config.yaml`):
runs `ruff format`/`ruff check`, the full `unittest` suite (scoped to
`src/**/*.py`/`tests/**/*.py` changes), a local `specmgr docs` hook (scoped to
`src/**/*.py` changes), and a local `specmgr adr-toc` hook (scoped to
`docs/adr/**/*.md` changes) before every commit, so a broken test or drift in
`docs/api/`/`docs/GENERATED.md`/`docs/adr/README.md` gets caught locally instead
of failing later in CI. (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI")

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
- `.github/workflows/ci.yml`: ruff + pylint (`|| true`) + vulture + unittest
  run on matrix 3.11/3.12/3.13 via `uv sync --frozen --all-extras`, but
  `specmgr docs` and `specmgr adr-toc` drift checks run **only on Python
  3.13** (pinned, since different Python versions generate different
  docstring formatting in the API docs, and we want consistent ADR TOC
  generation).
- `.github/workflows/publish.yml` exists and has shipped `v0.1.0`, `v0.2.0`,
  `v0.2.1` to PyPI/the MCP Registry, triggered on `v*` tags.
- Version bumps: update `version` in `pyproject.toml` (single source) and
  move `CHANGELOG.md`'s `[Unreleased]` into a dated section, same commit.

## Coding Standards

See `.specmgr/conventions.md` for detailed coding requirements and conventions:
- Python version and type notation
- Assert statement guidelines
- Variable naming (use `result` for return values)
- Comparison constants
- Mandatory type hints
- Documentation requirements for classes, attributes, and functions

- Formatter/linter: `ruff` (enforced, not black), line length 120.
- `pylint` is advisory fallback only (see pylint caveat above).

## Generated Documentation

See [`docs/GENERATED.md`](docs/GENERATED.md), auto-generated by `specmgr
docs` (implemented-domain list, per-module docstrings, and test-file count).
This pointer is permanent and hand-written — it is never regex-spliced or
otherwise auto-edited; only `docs/GENERATED.md` itself is regenerated.
