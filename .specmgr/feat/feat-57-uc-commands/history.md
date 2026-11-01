# History: Add create_uc/update_uc MCP Prompts for the Use Case Domain

#### 2026-09-02 00:00:00.000Z - Phase 3: Documentation & registration
Updated `src/biz/dfch/specmgr/server.py`'s module docstring: added a
"Use-case prompts (``uc/prompts/``)" paragraph to the "Prompts" section,
placed right after the ADR paragraph and before the Requirement paragraph
(matching the "Tools" section's own ADR-then-UC-then-REQ ordering), and
removed the now-stale closing sentence claiming `uc` "registers `tools`
and `resources` only -- it has no `prompts` sub-package yet" (added `uc`
to the list of domains that register `tools`/`resources`/`prompts`
instead). Updated `AGENTS.md`: added a `` `uc/prompts/`
(`create_uc`/`update_uc`)`` clause to the `uc/` bullet (same phrasing
pattern as the `req/` bullet's own `req/prompts/` mention), and removed
the now-false "Still genuinely missing" bullet claiming uc has no
prompts sub-package (REQ-006). Regenerated `docs/api/`,
`docs/GENERATED.md` (via `specmgr docs`), and `docs/MCP.md` (via
`specmgr mcp-docs`) -- `docs/MCP.md`/`docs/GENERATED.md` showed no diff
(already reflected the Phase 2 prompt registration), only
`docs/api/biz.dfch.specmgr.server.md` changed, mirroring the docstring
edit exactly. Verified: `ruff format --check`/`ruff check` on
`server.py` both pass; `from biz.dfch.specmgr import server` imports
without raising; running `specmgr docs`/`specmgr mcp-docs` a second time
produced no further `git status` changes (idempotent). No test files
were added (Phase 4's job). Nothing committed.

#### 2026-09-02 00:00:00.000Z - Phase 2: Prompt modules implemented
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

#### 2026-09-02 00:00:00.000Z - Phase 1: Instructions content drafted
Added `src/biz/dfch/specmgr/uc/data/uc_create_instructions.md` and `uc_update_instructions.md`, ported from `req/data/req_create_instructions.md`/`req_update_instructions.md`'s structure (numbered-step flow, `$topic`/`$id`/`$instructions` `string.Template` placeholders) and adapted to UC's actual tool/resource surface: `list_uc`, `create_uc`, `get_uc`/`get_uc(raw=True)`, `validate_uc`, `specmgr://uc/template`/`example`/`schema`, the generic `update`/`set_status`/`set_classification` tools with `type="uc"`, and UC's narrower 5-value status vocabulary (draft/proposed/accepted/deprecated/superseded, no "implemented"/"rejected"). The structure recap in both files was verified directly against `uc/models/v2/use_case.py`'s Pydantic field definitions (mandatory vs. optional `Characteristic Information` sub-sections, `Extensions`/`Sub-Variations` being fully optional with regex-constrained `### Extension {step}{letter}. ...`/`### Step {N}: ...` headings and the step-reference cross-check `model_validator`) rather than assumed from the issue's summary. No `uc/data/__init__.py` was needed and no `pyproject.toml` change was needed -- `uc/data/` already existed (holding `uc_example.md`/`uc_template.md`/`uc_schema.json`) and `[tool.setuptools.package-data]` already declares `"biz.dfch.specmgr.uc" = ["data/*.md", "data/*.json"]`, which already covers the two new files. `ruff format --check`/`ruff check` pass (no-op on `.md` files; confirms nothing else was touched). Nothing committed.

#### 2026-09-02 00:00:00.000Z - Created
Feature created from GitHub issue #57 ("uc domain has no create_uc/update_uc prompts"), scoping the addition of a create_uc/update_uc MCP prompt pair to bring the uc domain to parity with every other whole-body domain. Implementation is explicitly gated on feat-56 (classification) landing first.
