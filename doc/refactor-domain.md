# Domain-first repackaging of `tools`/`prompts`/`resources`

## 1. Goal

Today, `tools/`, `resources/`, and `prompts/` are the top-level packages, and
each one has an `adr` sub-package (`tools/adr/`, `prompts/adr/`) or `adr_*`
flat files (`resources/adr_get.py`, `resources/adr_list.py`) hanging under it.
As more document types are added (`req`, `uc`, `ac`, ...), this "interface
layer first" layout means every new domain scatters its tools/prompts/
resources across three unrelated top-level packages instead of living
together.

This document plans the inverse: **the domain becomes the top-level
package**. `adr/` becomes a top-level package containing its own `tools/`,
`prompts/`, `resources/` sub-packages. Future domains (`req/`, `uc/`, `ac/`)
follow the identical shape.

`models/` is **not** part of this move — see §2's first decision.

Like `doc/adr-tool-plan.md`, this document is meant to be kept in sync with
`src/` as the refactor progresses (current-state tracking, not just a
historical design note) — §7 tracks per-item status.

## 2. Decisions

1. **`models/adr/` stays under the shared top-level `models/` package.**
   `models/` is the "schema layer" (Pydantic models, parser, renderer,
   mutations — no dependency on `tools`/`resources`/`prompts`), already
   organized internally by domain (`models/adr/`, later `models/req/`,
   `models/uc/`, `models/ac/`) and versioned via `vN` sibling packages. Only
   the "interface layer" (`tools`/`prompts`/`resources`) becomes
   domain-first. This keeps the move mechanical: nesting depth for
   `tools/adr/*.py` → `adr/tools/*.py` and `prompts/adr/*.py` →
   `adr/prompts/*.py` is unchanged, so **no import-line edits are needed
   inside those files** — pure `git mv`. It also avoids a breaking change to
   `biz.dfch.specmgr.models.Adr` and friends, which several tests and
   `CHANGELOG.md` already document as the public import path.

2. **The now-empty top-level `tools/` and `prompts/` packages are deleted
   entirely**, not kept as placeholders. Nothing else lives in them once
   `adr` moves out. `server.py` will import domain packages (`adr`, later
   `req`/`uc`/`ac`) directly instead.

3. **`resources/adr_get.py`/`adr_list.py` keep their filenames** when moved
   into the new `adr/resources/` subfolder (no rename to `get.py`/`list.py`)
   — minimal diff, and matches the unchanged `@mcp.resource(name="adr_get"/
   "adr_list")` registration names.

4. **`doc/adr-tool-plan.md` is updated in place**, not appended with a new
   section: rewrite the stale path references in §6/§8/§9a/§10/§11 to the
   new `adr/tools/`, `adr/prompts/`, `adr/resources/` locations (also fixing
   the pre-existing stale `resources/adr.py` single-file mention while
   touching those lines).

**Important**: this is a **pure Python-packaging reorganization**. No
MCP-facing name changes — tool names (`get_adr`, `create_adr`, ...), resource
URIs (`specmgr://adr/{id}`, `specmgr://adr/list`), and prompt names
(`create_adr`, `update_adr`, ...) are all unchanged. Only the Python import
paths (`biz.dfch.specmgr.tools.adr.*` etc.) move.

## 3. Target layout

```
src/biz/dfch/specmgr/
├── models/                     # UNCHANGED — stays domain-organized internally
│   ├── __init__.py
│   ├── version_info.py
│   └── adr/                    # unchanged (v1/ versioning convention preserved)
├── adr/                        # NEW top-level domain package
│   ├── __init__.py              # from . import tools, prompts, resources  (side-effect registration)
│   ├── tools/                  # git mv from tools/adr/ — content unchanged
│   ├── prompts/                # git mv from prompts/adr/ — content unchanged
│   └── resources/               # NEW subfolder — git mv adr_get.py/adr_list.py out of resources/
│       ├── __init__.py          # new: from . import adr_get, adr_list
│       ├── adr_get.py
│       └── adr_list.py
├── resources/                   # SHRINKS — only the non-domain "version" resource remains
│   ├── __init__.py               # from . import version  (drop adr_get, adr_list)
│   └── version.py
├── server.py                     # bottom import: from . import adr, resources
├── commands/, cli.py, __init__.py, __main__.py   # unchanged
# tools/ and prompts/ (top-level) — DELETED entirely
```

Future domains repeat the same shape: `req/{tools,prompts,resources}/`,
`uc/{...}`, `ac/{...}`, each with `models/req/`, `models/uc/`, `models/ac/`
staying under the shared `models/` package.

## 4. Source moves (`git mv`, preserves blame)

| From | To | Import-line edits needed |
|---|---|---|
| `tools/adr/*.py` (14 files incl. `_io.py`, `_paths.py`, `_lock.py`) | `adr/tools/*.py` | **None** — same relative-import depth |
| `prompts/adr/*.py` (4 files) | `adr/prompts/*.py` | **None** — same relative-import depth |
| `resources/adr_get.py` | `adr/resources/adr_get.py` | `..server`→`...server`; `..models.adr`→`...models.adr`; `..tools.adr._io`→`..tools._io`; `..tools.adr._paths`→`..tools._paths`; docstring's `~biz.dfch.specmgr.tools.adr._paths.AdrNotFoundError` → `~biz.dfch.specmgr.adr.tools._paths.AdrNotFoundError` |
| `resources/adr_list.py` | `adr/resources/adr_list.py` | same pattern (`..server`, `..models.adr`, `..tools.adr._io/_paths` → one dot deeper / drop `.adr` segment) |

New/changed files:
- **New** `src/biz/dfch/specmgr/adr/__init__.py`: `from . import prompts, resources, tools  # noqa: F401` + docstring mirroring `tools/__init__.py`'s current style.
- **New** `src/biz/dfch/specmgr/adr/resources/__init__.py`: `from . import adr_get, adr_list  # noqa: F401`.
- **Edit** `resources/__init__.py`: drop `adr_get`, `adr_list` from the import/`__all__`, keep only `version`.
- **Edit** `server.py`: line 73 becomes `from . import adr, resources  # noqa: E402, F401`; rewrite docstring lines 22–44 (resource/tool/prompt inventory + the "add further modules" guidance) to describe the domain-package convention.
- **Delete** `tools/__init__.py`, `tools/` directory entirely (after the `adr` subfolder moves out, nothing remains).
- **Delete** `prompts/__init__.py`, `prompts/` directory entirely.

`models/`, `pyproject.toml` (auto package discovery via `find:`, confirmed no explicit package list), `.github/workflows/*.yml`, `README.md` — **no changes required** (verified zero path/module references).

## 5. Test moves

| From | To | Import edits |
|---|---|---|
| `tests/tools/adr/*.py` (16 files incl. `_helpers.py`) | `tests/adr/tools/*.py` | `biz.dfch.specmgr.tools.adr.X` → `biz.dfch.specmgr.adr.tools.X` (mechanical rename, `models.adr` imports untouched) |
| `tests/prompts/adr/*.py` (4 files) | `tests/adr/prompts/*.py` | `biz.dfch.specmgr.prompts.adr.X` → `biz.dfch.specmgr.adr.prompts.X` |
| `tests/resources/test_adr.py` | `tests/adr/resources/test_adr.py` | `biz.dfch.specmgr.resources.adr_get/adr_list` → `biz.dfch.specmgr.adr.resources.adr_get/adr_list`; `biz.dfch.specmgr.tools.adr._paths` → `biz.dfch.specmgr.adr.tools._paths` |
| — | new `tests/adr/__init__.py` | license header only, matching sibling `__init__.py` style |
| `tests/tools/`, `tests/prompts/` dirs | deleted (nothing left) | — |
| `tests/resources/test_version.py`, `tests/resources/__init__.py` | **stay put** | no change |
| `tests/models/adr/**` | **stays put** | no change |

## 6. Documentation updates

**`AGENTS.md`**:
- Rewrite the bulleted file inventory under "Status" to the new paths:
  `tools/adr/` → `adr/tools/`; `resources/adr_list.py`/`adr_get.py` →
  `adr/resources/adr_list.py`/`adr_get.py`; `prompts/adr/*` →
  `adr/prompts/*`; test path list `tests/models/adr/`, `tests/tools/adr/`,
  `tests/resources/`, `tests/prompts/adr/` → `tests/models/adr/`,
  `tests/adr/tools/`, `tests/adr/resources/`, `tests/adr/prompts/` (plus
  `tests/resources/test_version.py` staying separate).
- Rewrite the **MCP server** section's guidance: replace "follow the
  sibling-project convention of `tools/`/`resources/` sub-packages,
  importing them as the last line of `server.py`" with the new
  domain-first convention — each domain package (`adr/`, future
  `req/`/`uc/`/`ac/`) owns its own `tools/`/`prompts/`/`resources/`
  sub-packages and self-registers them via its own `__init__.py`;
  `server.py` imports the domain package itself (plus top-level
  `resources/` for cross-cutting resources like `specmgr://version`).
- Keep the "models/adr/'s layout being designed to generalize" bullet —
  still accurate (models stays flat/shared).

**`doc/adr-tool-plan.md`** (in-place edits):
- §6 "Module layout": update to state tools/prompts/resources are now
  domain-nested (`adr/tools/`, `adr/prompts/`, `adr/resources/`) while
  `models/` remains the shared, internally-domain-organized schema layer;
  clarify this is now the template for `req`/`uc`/`ac`.
- §8/§9a: fix path references, including the pre-existing stale
  `resources/adr.py` single-file mention (correct to
  `adr/resources/adr_get.py`/`adr_list.py` while touching those lines
  anyway).
- §10 "Next steps" and §11 "Prompts": update the done-item path references
  (`tools/adr/*` → `adr/tools/*`, `tests/tools/adr` → `tests/adr/tools`,
  etc.).

**`CHANGELOG.md`**: add a new `## [Unreleased]` entry (`### Changed`,
flagged as a breaking internal-API move) describing:
`biz.dfch.specmgr.tools.adr.*` → `biz.dfch.specmgr.adr.tools.*`,
`biz.dfch.specmgr.prompts.adr.*` → `biz.dfch.specmgr.adr.prompts.*`,
`biz.dfch.specmgr.resources.adr_get/adr_list` →
`biz.dfch.specmgr.adr.resources.adr_get/adr_list`; explicitly note
`models.adr` is unchanged, and that **no MCP-facing names/URIs change**
(tool names, resource URIs like `specmgr://adr/{id}`, prompt names are all
identical — this is a pure Python-packaging reorg).

## 7. Verification

1. `uv run --frozen ruff format --check && uv run --frozen ruff check`
2. `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
   (expect all ~175 tests to still pass, now under `tests/adr/...`)
3. Repo-wide grep sweep for stragglers: `specmgr\.tools\.adr`,
   `specmgr\.prompts\.adr`, `specmgr\.resources\.adr`, `tools/adr`,
   `prompts/adr`, `resources/adr_` — should return zero hits in `src/`,
   `tests/`, `AGENTS.md`, `doc/adr-tool-plan.md`, `CHANGELOG.md` outside
   historical/superseded notes.
4. `uv run --frozen pylint $(git ls-files '*.py')` (advisory) — re-run after
   `git add` of all moved files, since pylint only sees tracked files.
5. Clear/ignore stale `.mypy_cache` (unrelated to source correctness, will
   regenerate).

## 8. Commit strategy

Do this as its own commit, separate from any pending release-prep changes
(version bumps, `server.json`/`CHANGELOG.md`/`README.md` release-note
edits) — it's an unrelated structural change and mixing it in would make
the release diff harder to review. Suggested conventional-commit message:
`refactor(structure): move adr's tools/prompts/resources under a domain-first adr/ package`.

## 9. Status tracking

- [x] Source moves (§4)
- [x] Test moves (§5)
- [x] `AGENTS.md` updated
- [x] `doc/adr-tool-plan.md` updated in place
- [x] `CHANGELOG.md` entry added
- [x] Verification (§7) passes
- [ ] Committed
