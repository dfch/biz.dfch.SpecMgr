---
created: '2026-08-19T07:40:25.811099'
id: aaf70093-8a7c-4565-9985-3beaa85e1d3d
status: done
type: tsk
updated: '2026-08-19T07:45:21.344355'
version: 1.0.0
---

# Add `streamable-http` MCP Transport Option

<!-- Implementation plan backing feat-7-various-improvements Phase 0's "add a third MCP transport" task. Adds the SDK's `streamable-http` transport (mcp>=2.0.0's spec-current HTTP transport, replacing the legacy/deprecated `sse` transport for HTTP deployments) as a third `specmgr mcp --transport` choice, alongside the existing `stdio`/`sse`. Purely a transport-wiring change in `commands/mcp.py`; no changes to `server.py`, tools, resources, or prompts, since MCP transport is orthogonal to protocol-era/tool logic. -->

- [x] Task 1: Extend `commands/mcp.py`'s `--transport`/`-t` Typer option to accept `"streamable-http"` in addition to the existing `"stdio"`/`"sse"` (help text, `show_default`, and the `SPECMGR_MCP_TRANSPORT` envvar description all mention the new value) — depends on: none.

- [x] Task 2: Add a `streamable-http` branch in the `mcp()` command function, calling `_warn_on_public_binding(host)` (same as the existing `sse` branch) and then `mcp_server.run(transport="streamable-http", host=host, port=port, stateless_http=True)`. Set `stateless_http=True` explicitly — matches this server's already-stateless `_lifespan` (`server.py`) and aligns with the 2026-07-28 modern protocol era's stateless-per-request session model — depends on: Task 1.

- [x] Task 3: Update `commands/mcp.py`'s module docstring — add a third bullet describing `streamable-http` (spec-current HTTP transport, replaces the legacy/deprecated `sse` transport for HTTP deployments; binds a TCP port like `sse` does) alongside the existing `stdio`/`sse` bullets, plus a `specmgr mcp --transport streamable-http --host localhost --port 8000` usage example line — depends on: Task 2.

- [x] Task 4: Update `README.md`'s MCP section — add `streamable-http` to the `--transport` table row's allowed values, and add a short usage example mirroring the existing `sse` example (`specmgr mcp --transport sse --host localhost --port 8000`) — depends on: Task 3.

- [x] Task 5: Extend `tests/commands/test_mcp.py` with coverage for the new branch: mock `biz.dfch.specmgr.server.mcp.run` (or the imported name inside `commands/mcp.py`) and assert that invoking the `mcp()` command with `--transport streamable-http` calls `run` with `transport="streamable-http"`, the given `host`/`port`, and `stateless_http=True`. If no equivalent assertion-on-`run`-call test exists yet for `sse`/`stdio`, add matching ones for those two as well so all three branches have symmetric coverage — depends on: Task 2.

- [x] Task 6: Regenerate `docs/api/`/`docs/GENERATED.md` (`uv run --frozen specmgr docs`, Python 3.13) to pick up the `commands/mcp.py` docstring change — depends on: Task 3.

- [x] Task 7: Verify — `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, and the full `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` suite, all clean/passing — depends on: Task 1 through Task 6.

- [x] Task 8: Update `feat-7-various-improvements/README.md`'s Decisions Made / Recent Updates logs and mark the parent Phase 0 task (and this task list) done — depends on: Task 1 through Task 7.

## Recent Updates

### 2026-08-19 - Created

Created to back a new Phase 0 task in `feat-7-various-improvements` for adding the `mcp` SDK's `streamable-http` transport as a third `specmgr mcp --transport` option, alongside the existing `stdio`/`sse`.

### 2026-08-19 - Implemented and verified

All 8 tasks completed: extended `commands/mcp.py`'s `--transport`/`-t` option (help text, `show_default`, envvar description) and added a `streamable-http` branch calling `_warn_on_public_binding(host)` then `mcp_server.run(transport="streamable-http", host=host, port=port, stateless_http=True)`; updated the module docstring and `README.md`'s MCP section with a third bullet/table entry and usage example; added a new `TestMcpCommand` test class in `tests/commands/test_mcp.py` asserting `run` is called correctly for all three branches (`stdio`, `sse`, `streamable-http`); regenerated `docs/api/`/`docs/GENERATED.md`; verified `ruff format --check`/`ruff check`/`vulture src/ whitelist.py --min-confidence 60` (all clean) and the full `unittest` suite (1195 tests, all passing, up from 1192); updated `feat-7-various-improvements/README.md`'s Recent Updates/Decisions Made logs and marked Task 0.23 done.
