---
status: accepted
id: 3bf0326f-065a-424c-a2b9-87e5d5bcfa99
version: 1.0.0
---

# Extract MCP Singleton into Its Own Module to Break Domain/Server Cyclic Imports

## Context and Problem Statement

Every domain package's tool/resource/prompt module (~80 files across `adr`, `general`, `qa`, `req`, `tsk`, `uc`) imports the shared `mcp` `MCPServer` singleton directly from `server.py` (e.g. `qa/tools/set_status_qa.py`'s `from ...server import mcp`), while `server.py` itself imports every domain package at its own bottom to trigger `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` registration. This creates a real cyclic import in the static graph, confirmed by `pylint`'s R0401 check (~90 warnings, one per file, permanently suppressed via `|| true` in CI). It does not break today only because `server.py` constructs `mcp = MCPServer(...)` textually before its bottom-of-file domain imports — a fragile ordering convention, not an enforced invariant — and it permanently drowns out any signal pylint's cyclic-import check could otherwise give for a genuinely new problem.

## Considered Options

1. Accept as-is and document only (no code change). 2. Extract the `MCPServer` construction into a new leaf module (`mcp_instance.py`) that both `server.py` and every domain file import from, removing the cycle at the graph level. 3. Defer each domain file's `mcp` import to inside its decorator call (lazy import).

## Decision Outcome

Adopt Option 2: extract `mcp_instance.py` as the single leaf module owning the `MCPServer` singleton (and its `_lifespan`); `server.py` will import `mcp` from it instead of constructing it directly, and every domain tool/resource/prompt file will import `mcp` from `mcp_instance` instead of `server`. This removes the cyclic import entirely with no behavior change. Implementation is deferred to a dedicated specmgr task list rather than performed as part of this ADR.

### Consequences

~80 files get a mechanical import-path change when the deferred task list is executed; CI's pylint step can eventually be tightened since the permanent R0401 noise disappears; no runtime behavior changes.

## More Information

The detailed, per-file implementation breakdown for executing this decision lives in specmgr task list TSK `699432f5-6f95-498e-a269-8001e4afc0e5` ("Extract `mcp_instance.py` to Break Domain/Server Cyclic Imports") — retrieve it via the `get_tsk` MCP tool. Originating context: `.specmgr/feat/feat-7-various-improvements/README.md` Task 0.22.
