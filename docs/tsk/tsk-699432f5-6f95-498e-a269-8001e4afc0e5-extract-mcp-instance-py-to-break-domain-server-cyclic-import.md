---
created: '2026-08-19 08:50:55.251Z'
id: 699432f5-6f95-498e-a269-8001e4afc0e5
status: draft
type: tsk
updated: '2026-08-19 08:50:55.251Z'
version: 1.0.0
---

# Extract `mcp_instance.py` to Break Domain/Server Cyclic Imports

<!-- Implements the decision recorded in ADR 3bf0326f-065a-424c-a2b9-87e5d5bcfa99 ("Extract MCP Singleton into Its Own Module to Break Domain/Server Cyclic Imports"). Mechanical refactor: no behavior change, ~80 files touched. -->

- [ ] Task 1: Create a new leaf module `src/biz/dfch/specmgr/mcp_instance.py` holding the `_lifespan` async context manager and the `mcp = MCPServer(...)` construction, moved verbatim out of `server.py`
- [ ] Task 2: Update `server.py` to `from .mcp_instance import mcp` instead of constructing `MCPServer(...)` itself; keep its bottom-of-file `from . import adr, general, qa, req, tsk, uc` domain registration imports unchanged, in the same relative position
- [ ] Task 3: Mechanically update every domain tool/resource/prompt file's `from ...server import mcp` to `from ...mcp_instance import mcp` (same relative import depth) across `adr/`, `general/`, `qa/`, `req/`, `tsk/`, `uc/` (~80 files) — a scripted/sed-style find-and-replace is acceptable given the mechanical, identical nature of every occurrence
- [ ] Task 4: Grep `tests/` for any direct `from biz.dfch.specmgr.server import mcp` (or equivalent) references and update them to import from `biz.dfch.specmgr.mcp_instance` instead
- [ ] Task 5: Update `server.py`'s module docstring and `AGENTS.md`'s description of the tool/resource/prompt registration pattern to mention `mcp_instance.py` as the module owning the `MCPServer` singleton
- [ ] Task 6: Regenerate `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13; verify `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite all pass; confirm via `pylint $(git ls-files '*.py') --disable=all --enable=R0401` that the cyclic-import warning count drops from ~90 to 0
- [ ] Task 7: Update `.specmgr/feat/feat-7-various-improvements/README.md`'s Decisions Made / Recent Updates logs and mark the originating Task 0.22 done

## Recent Updates

### 2026-08-19 - Created

Created from feat-7-various-improvements Task 0.22, following ADR 3bf0326f-065a-424c-a2b9-87e5d5bcfa99's decision to extract the `MCPServer` singleton into a leaf module. No implementation started yet.
