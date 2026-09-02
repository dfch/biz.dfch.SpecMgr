---
created: '2026-09-02T14:59:42.990052'
id: feat-57-uc-commands
status: planning
type: feat
updated: '2026-09-02T15:02:09.712022'
version: 1.0.0
---

# Feature: Add create_uc/update_uc MCP Prompts for the Use Case Domain

## Plan

### Overview

Adds a `create_uc`/`update_uc` MCP prompt pair to the `uc` domain, mirroring the existing `req/prompts/` pattern (narrated instructions backed by packaged `uc_create_instructions.md`/`uc_update_instructions.md` data files), so an LLM has a guided workflow for drafting or revising Use Case documents -- reaching prompt parity with every other whole-body domain (req/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr).

### Requirements

- REQ-001: Add `uc/prompts/create_uc.py` registering an `@mcp.prompt()` that loads packaged `uc_create_instructions.md` via `read_packaged_text`, mirroring `req/prompts/create_req.py`.

- REQ-002: Add `uc/prompts/update_uc.py` registering an `@mcp.prompt()` that loads packaged `uc_update_instructions.md`, mirroring `req/prompts/update_req.py`.

- REQ-003: Add `uc/data/uc_create_instructions.md` and `uc/data/uc_update_instructions.md`, following the req instructions' numbered-section structure, adapted to UC-specific tools/resources, and including `set_classification(id, type="uc", classification)` references from day one, matching the pattern feat-56 will add to the other 10 whole-body domains' create/update instructions.

- REQ-004: Add `uc/prompts/__init__.py` exporting `create_uc`/`update_uc` and wire it into `uc/__init__.py` alongside the existing `resources, tools` imports.

- REQ-005: Update `server.py`'s module docstring to list the new "Use-case prompts (uc/prompts/)" entry, mirroring the existing "Requirement prompts (req/prompts/)" line.

- REQ-006: Update `AGENTS.md`'s `uc/` bullet and "Still genuinely missing" list to drop the "uc registers tools and resources only" caveat.

- REQ-007: Do not begin Phase 1 or later implementation until feat-56 (classification frontmatter field + generic `set_classification` tool) has landed and synced into this branch, since the new instructions' `set_classification` wording must match feat-56's actual tool signature/behavior exactly.

### Acceptance Criteria

- [ ] ACC-001: `create_uc`/`update_uc` prompts exist and are registered/discoverable the same way `create_req`/`update_req` are.

- [ ] ACC-002: `uc_create_instructions.md`/`uc_update_instructions.md` exist under `uc/data/`, loaded via `read_packaged_text`, matching req's structure/tone.

- [ ] ACC-003: `server.py`'s docstring and `AGENTS.md` are updated; `specmgr docs`/`docs/MCP.md` regenerate cleanly without manual edits to `docs/MCP.md`.

- [ ] ACC-004: The existing test suite passes, plus new tests cover the two new prompt functions (registration + instructions content substitution).

- [ ] ACC-005: `ruff format --check`, `ruff check`, and `vulture` all pass with the new files included.

- [ ] ACC-006: `uc_create_instructions.md` and `uc_update_instructions.md` each contain a `set_classification(id, type="uc", classification)` reference consistent with the mention pattern already present in at least one already-updated sibling domain's instructions (e.g. req) once feat-56 has landed.

### Scope

#### Included

- Adding `uc/prompts/create_uc.py`, `uc/prompts/update_uc.py`, `uc/prompts/__init__.py`.

- Adding `uc/data/uc_create_instructions.md`, `uc/data/uc_update_instructions.md`.

- Wiring the new `prompts` sub-package into `uc/__init__.py`.

- Updating `server.py`'s docstring and `AGENTS.md` to reflect the new prompts.

- Adding unit tests for the new prompt modules.

- Regenerating `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` via `specmgr docs`.

#### Explicitly Out Of Scope

- Implementing the `classification` frontmatter field or the generic `set_classification` tool itself (feat-56) -- this feature only adds references to `set_classification` in uc's new instructions, matching the mention pattern the other domains will carry once feat-56 lands; the tool's implementation is a separate feature.

- Any change to `uc`'s tools, resources, or models themselves (this is prompts-only parity work).

- Reviewing or refactoring existing prompt modules across other domains for consistency (tracked separately under issue #7).

### Dependencies

#### Depends On

- feat-56 (classification frontmatter field + generic `set_classification` tool) -- confirmed not yet implemented (zero "classification" references anywhere in `src/`, no `.specmgr/feat/feat-56*` folder exists). This feature SHOULD NOT start implementation (Phase 1 onward) before feat-56 is synced into this branch, since the new `uc_create_instructions.md`/`uc_update_instructions.md` must reference `set_classification` consistent with feat-56's actual tool signature and the mention pattern already rolled out to the other 10 domains.

### Design Notes

This feature mirrors the `req/prompts/` pattern exactly: each prompt function is an `@mcp.prompt()`-decorated function that loads a packaged instructions `.md` file via `general.tools._packaged_data.read_packaged_text` (convention: `{type}/data/{type}_{kind}.{ext}`) and performs `string.Template(...).substitute(...)` (not `str.format`, to avoid collisions with literal `{...}` markdown headings) with parameters like `topic` (create) or `id`/`instructions` (update). Per the issue's classification note, the new `uc_create_instructions.md`/`uc_update_instructions.md` must include `set_classification(id, type="uc", classification)` references from day one, matching what feat-56 is expected to add to the other 10 domains' instructions -- this is why implementation is deliberately sequenced to start only after feat-56 lands (see Dependencies), even though this feature's own scope never touches the classification field/tool implementation itself.

### Task List

#### Phase 0: Pre-requisite -- feat-56 sync gate

- [ ] Task 0.1: Confirm feat-56 (classification frontmatter field + generic `set_classification` tool) has been implemented and merged; do not proceed to Phase 1 until confirmed.

- [ ] Task 0.2: Review one already-updated sibling domain's create/update instructions (e.g. req) for the exact `set_classification` mention wording/pattern to mirror.

#### Phase 1: Instructions content

- [x] Task 1.1: Draft `uc_create_instructions.md` mirroring `req_create_instructions.md`'s structure, adapted for UC-specific tool names/resources, including the `set_classification` reference.

- [x] Task 1.2: Draft `uc_update_instructions.md` mirroring `req_update_instructions.md`'s structure, adapted for UC-specific tool names/resources, including the `set_classification` reference.

#### Phase 2: Prompt modules

- [x] Task 2.1: Implement `uc/prompts/create_uc.py` (`@mcp.prompt()`, `read_packaged_text`, `string.Template` substitution), mirroring `req/prompts/create_req.py`.

- [x] Task 2.2: Implement `uc/prompts/update_uc.py` mirroring `req/prompts/update_req.py`.

- [x] Task 2.3: Add `uc/prompts/__init__.py` and update `uc/__init__.py` to import `prompts` alongside `resources, tools`.

#### Phase 3: Documentation & registration

- [ ] Task 3.1: Update `server.py`'s module docstring to add the "Use-case prompts (uc/prompts/)" entry.

- [ ] Task 3.2: Update `AGENTS.md`'s `uc/` bullet and "Still genuinely missing" list.

- [ ] Task 3.3: Regenerate `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` via `specmgr docs`.

#### Phase 4: Tests & verification

- [ ] Task 4.1: Add unit tests for `create_uc`/`update_uc` prompt registration and content substitution, mirroring existing req prompt tests.

- [ ] Task 4.2: Run the full lint/test suite (`ruff format --check`, `ruff check`, `vulture`, `unittest discover`) and fix any failures.

## Progress

### Current Status

**As of 2026-09-02**: Phase 0 (feat-56 sync gate), Phase 1 (instructions content), and Phase 2 (prompt modules) are done. `uc/prompts/create_uc.py`/`update_uc.py`/`__init__.py` now exist, mirroring `req/prompts/`'s shape exactly, and `uc/__init__.py` imports/re-exports `prompts` alongside `resources, tools`. Both prompts are confirmed registered on the shared `mcp` app (`await mcp.list_prompts()` includes `create_uc`/`update_uc`). Phase 3 (documentation & registration) is next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 00:00:00.000Z — Phase 2: Prompt modules implemented

Added `src/biz/dfch/specmgr/uc/prompts/create_uc.py`, `update_uc.py`, and
`__init__.py`, 1:1 ports of `req/prompts/create_req.py`/`update_req.py`/
`__init__.py` (same `@mcp.prompt()` decorator shape, `string.Template`
substitution via `read_packaged_text("uc", "create_instructions"/
"update_instructions", "md")`, `id`/`instructions` parameters with the
`pylint: disable=redefined-builtin` comment on `update_uc`), with
docstrings adapted to UC's own tool/resource names (`list_uc`,
`create_uc`, `validate_uc`, `get_uc`/`get_uc(raw=True)`,
`specmgr://uc/template`/`example`/`schema`, and the generic
`update`/`set_status`/`set_classification` tools with `type="uc"`, noting
UC has no `specmgr://uc/{id}` resource -- id-based reads are
`get_uc`-only). Updated `uc/__init__.py` to import `prompts` alongside
`resources, tools` (alphabetical), added `"prompts"` to `__all__`, and
replaced the outdated "There is no `prompts` sub-package yet" sentence in
its module docstring with a description of the new `create_uc`/`update_uc`
prompts, matching `req/__init__.py`'s docstring tone. Verified:
`ruff format --check`/`ruff check` on `src/biz/dfch/specmgr/uc/` both
pass with zero issues; `vulture src/ whitelist.py --min-confidence 60`
produces no output (no new dead-code warnings); importing
`biz.dfch.specmgr.server` (which imports `uc`) does not raise; and an ad
hoc `await server.mcp.list_prompts()` check confirms both `create_uc` and
`update_uc` are registered on the shared `mcp` app. No tests were added
(Phase 4's job) and no `specmgr docs`/`server.py`/`AGENTS.md` edits were
made (Phase 3's job). Nothing committed.

#### 2026-09-02 00:00:00.000Z — Phase 1: Instructions content drafted

Added `src/biz/dfch/specmgr/uc/data/uc_create_instructions.md` and `uc_update_instructions.md`, ported from `req/data/req_create_instructions.md`/`req_update_instructions.md`'s structure (numbered-step flow, `$topic`/`$id`/`$instructions` `string.Template` placeholders) and adapted to UC's actual tool/resource surface: `list_uc`, `create_uc`, `get_uc`/`get_uc(raw=True)`, `validate_uc`, `specmgr://uc/template`/`example`/`schema`, the generic `update`/`set_status`/`set_classification` tools with `type="uc"`, and UC's narrower 5-value status vocabulary (draft/proposed/accepted/deprecated/superseded, no "implemented"/"rejected"). The structure recap in both files was verified directly against `uc/models/v2/use_case.py`'s Pydantic field definitions (mandatory vs. optional `Characteristic Information` sub-sections, `Extensions`/`Sub-Variations` being fully optional with regex-constrained `### Extension {step}{letter}. ...`/`### Step {N}: ...` headings and the step-reference cross-check `model_validator`) rather than assumed from the issue's summary. No `uc/data/__init__.py` was needed and no `pyproject.toml` change was needed -- `uc/data/` already existed (holding `uc_example.md`/`uc_template.md`/`uc_schema.json`) and `[tool.setuptools.package-data]` already declares `"biz.dfch.specmgr.uc" = ["data/*.md", "data/*.json"]`, which already covers the two new files. `ruff format --check`/`ruff check` pass (no-op on `.md` files; confirms nothing else was touched). Nothing committed.

#### 2026-09-02 00:00:00.000Z — Created

Feature created from GitHub issue #57 ("uc domain has no create_uc/update_uc prompts"), scoping the addition of a create_uc/update_uc MCP prompt pair to bring the uc domain to parity with every other whole-body domain. Implementation is explicitly gated on feat-56 (classification) landing first.

### Related PRs / Commits

- [Issue #57](https://github.com/dfch/biz.dfch.SpecMgr/issues/57): uc domain has no create_uc/update_uc prompts (unlike every other whole-body domain) -- the source issue for this feature.
