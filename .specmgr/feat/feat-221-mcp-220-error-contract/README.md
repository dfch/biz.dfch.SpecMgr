---
classification: null
created: '2026-10-19T13:34:10.017+02:00'
id: feat-221-mcp-220-error-contract
status: planning
type: feat
updated: '2026-10-19T13:34:10.017+02:00'
version: 1.0.0
---

# Feature: mcp ≥2.2.0 Upgrade (CVE-2026-59951) with Caller-Visible Tool Error Text Preserved (#221)

## Plan

### Overview

GitHub issue #221 / Dependabot alert #27 (GHSA-84m7-p3x7-pcfv, CVE-2026-59951, medium, CVSS 7.5): the repo's `mcp` SDK is locked at `= 2.0.0` (`uv.lock`; `mcp>=2.0.0` in the `mcp` extra of `pyproject.toml`). The vulnerability the advisory names — unbounded session accumulation in StreamableHTTP **stateful** mode — is effectively not exploitable in this repo (exposure ≈ 0): we serve `stdio` (default) and `sse` only, and the one `streamable-http` path already passes `stateless_http=True` (`src/biz/dfch/specmgr/commands/mcp.py:186`); stateful sessions, the only vulnerable path, are never created.

The patched version nonetheless cannot be adopted as-is: SDK v2.1.0 changed handler-exception surfacing (upstream #3314). Verified against the shipped source of 2.0.0 vs 2.1.0/2.2.0: in 2.0.0 a tool raising `ValueError("Invalid id: …")` returns `CallToolResult(is_error=True, text="Error executing tool get_req: Invalid id: …")` to the client; in 2.1.0+ the same raise produces `UnexpectedToolError("Error executing tool get_req")` on the wire — the original message is swallowed (by design, "nothing from an unexpected exception reaches the client") and survives only in `__cause__` and the server log. This repo has ~152 raise sites (the `_path_safety` invalid-id `ValueError`s, the 12× `XNotFoundError`s, `create_feat`'s `FileExistsError`, …) whose documented caller contract *is* that message text (the AGENTS.md tool bullets; the ADR 519d1206 non-raising chain head deliberately converted only content-validation/parse-failure errors and left usage errors raising precisely because their messages must be visible — see also open issue #211 on the client-side `isError` truncation of exactly that channel).

This feature upgrades the dependency to the patched line and restores the 2.0.0 wire contract at a single seam: a thin `SpecMgrServer(MCPServer)` subclass in `server.py` overriding the public `call_tool` to re-raise `UnexpectedToolError.__cause__`, plus a new wire-level regression test pinning the contract against future 2.x bumps.

### Requirements

- REQ-001: The `mcp` extra in `pyproject.toml` moves `mcp>=2.0.0` → `mcp>=2.2.0`, and `uv lock --upgrade-package mcp` resolves `mcp` to ≥ 2.2.0 (with lockstep `mcp-types` at the same version); no other `pyproject.toml` change.
- REQ-002: `server.py` defines `SpecMgrServer(MCPServer)` overriding only the public `call_tool(name, arguments, context=None)`: `try: return await super().call_tool(...)` / `except UnexpectedToolError as exc: raise exc.__cause__ from None` (imported from `mcp.server.mcpserver.exceptions`); the singleton becomes `mcp = SpecMgrServer(name="specmgr", instructions=..., lifespan=_lifespan)` with unchanged arguments; the override is uniform for every tool registered on the server (ADR-domain tools included — no per-domain logic).
- REQ-003: The Python-level raise contract stays byte-unchanged: every tool function called directly still raises the same exception types with the same messages (all existing raise-asserting tests pass unmodified); the `read_resource`/`get_prompt` paths are untouched (our `@mcp.resource()` functions raise nothing, and prompt error text is preserved in both SDK versions — re-raised as `ValueError(str(e))` at the dispatcher boundary); `commands/mcp.py`'s `run(transport=…)` calls are unchanged (signatures verified against the v2.2.0 overloads, incl. `stateless_http`).
- REQ-004: A new `tests/test_mcp_error_contract.py` exercises the in-memory `mcp.call_tool` (no transport): (a) malformed id → `is_error=True` with content text equal to the original `ValueError` message; (b) well-formed-but-absent id → `is_error=True` with the domain's not-found message; (c) a healthy call → success shape unchanged. This test, not the locked version number, is the behavioral guard for future 2.x bumps.
- REQ-005: A new ADR in `docs/adr/` (created via `create_adr`, accepted before/alongside the code landing, linked from this feature's Related Decisions) records: preserve 2.0.0 caller-visible exception text across mcp ≥2.1.0 by re-raising `UnexpectedToolError.__cause__` at the `call_tool` seam; rationale = the documented raise-based usage-error contract and ADR 519d1206's scoping of which errors go non-raising; and the relation to issue #211 (the shim preserves the status quo — including client-side `isError` truncation of those messages — and does not reopen the chain's scope).
- REQ-006: Docs sync: `server.py`'s module docstring (the authoritative registration list — names the subclass and why), `AGENTS.md`'s `server.py` bullet, a `CHANGELOG.md` `[Unreleased]` entry, and clean regeneration of `docs/api/` + `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`).
- REQ-007: Quality gates green: `ruff format --check` + `ruff check`, `vulture src/ whitelist.py --min-confidence 60` (whitelist entry for the override only if flagged), `pylint` advisory, full `pytest -n auto` (local 3.13; the CI matrix covers 3.11/3.12).

### Acceptance Criteria

- [ ] ACC-001: (REQ-001) `uv.lock` resolves `mcp` to ≥ 2.2.0 (the alert's `first_patched_version`) and Dependabot alert #27 reports fixed on the change.
- [ ] ACC-002: (REQ-002/REQ-004) `tests/test_mcp_error_contract.py` passes: a malformed id through `mcp.call_tool` returns `is_error=True` with the original message text (the pre-shim 2.1.0+ semantics would return the bare `Error executing tool <name>` — the test pins the post-shim behavior).
- [ ] ACC-003: (REQ-003) The full existing suite passes with zero test modifications (no raise-asserting test touched).
- [ ] ACC-004: (REQ-005/REQ-006) The ADR exists, is accepted, and is linked from this feature; `server.py`'s docstring, `AGENTS.md`, and `CHANGELOG.md` are accurate; both doc regenerations run clean.
- [ ] ACC-005: (REQ-007) All lint gates and the full test suite are green.

### Scope

#### Included

- The dependency bump: `pyproject.toml`'s `mcp` extra `>=2.2.0`, the `uv.lock` resolution (incl. lockstep `mcp-types`).
- The `SpecMgrServer(MCPServer)` subclass in `server.py` with the `call_tool` override (`UnexpectedToolError.__cause__` re-raise) and the singleton construction switch.
- The new wire-level regression test `tests/test_mcp_error_contract.py`.
- A new ADR recording the error-contract-preservation decision (accepted, linked).
- Docs sync: `server.py` module docstring, `AGENTS.md`'s `server.py` bullet, `CHANGELOG.md` `[Unreleased]`, `specmgr docs` + `specmgr mcp-docs` regeneration.
- The full quality gate (ruff, vulture, pylint advisory, pytest).

#### Explicitly Out Of Scope

- Converting any of the ~152 still-raising call sites to non-raising structured results — that is the ADR 519d1206 chain's domain; a separate future feature if the project goes that way (the shim preserves the status quo, including issue #211's client-side `isError` truncation of those messages).
- Any change to `commands/mcp.py`'s transport options or the stateless-streamable-http policy (already `stateless_http=True`; unchanged).
- Dismissing alert #27 instead of fixing it (rejected in planning: the next lock upgrade would hit the same 2.1.0 behavior change unprepared).
- The ADR domain's own tool contracts — the shim covers every tool on the server (incl. ADR's) uniformly by construction; no per-domain change.

### Dependencies

#### Depends On

- GitHub issue #221 (tracking vehicle; this feature folder's `NNN` infix is its number).
- Verified SDK source facts: v2.0.0 `Tool.call` wraps a handler exception as `ToolError(f"Error executing tool {name}: {e}")` (message on the wire); v2.1.0/v2.2.0 `Tool.call` wraps it as `UnexpectedToolError(f"Error executing tool {name}")` (no text; `__cause__` = the original, always set via `raise … from exc`); both versions' `_handle_call_tool` return the caught exception's `str()` as `is_error` content; `get_prompt` re-raises `ValueError(str(e))` at the dispatcher boundary in both versions.

#### Blocks

- None known.

### Design Notes

- **Why a `call_tool` override (not middleware or an `Extension` interceptor):** both layers sit *outside* `_handle_call_tool`, which catches the exception into a `CallToolResult` before either can see it. Only a handler-level (`call_tool`) override can recover the original exception via `UnexpectedToolError.__cause__`.
- **Wire shape after the shim:** `_handle_call_tool`'s existing catch returns `CallToolResult(content=[TextContent(str(original))], is_error=True)` — 2.0.0's shape minus the `Error executing tool <name>: ` prefix (our messages already name the tool, e.g. `repair() received a blank id…`); logging is retained (`logger.exception` in the catch).
- **The deep import** `mcp.server.mcpserver.exceptions.UnexpectedToolError` is acceptable — the project already deep-imports `mcp.server.mcpserver.resources.base` in four test files.
- **Version drift:** the lock may resolve mcp > 2.2.0 (the latest 2.x at lock time); REQ-004's regression test is the behavioral guard, not the version number.
- **`raise exc.__cause__ from None`** avoids a doubled exception chain in the server log; `__cause__` is total (the SDK raises with `from exc`).

### Related Decisions

- ADR 519d1206-4d2a-4500-9046-6db635209996 (case 1 of the non-raising structured-result chain): scopes which tool errors stay raise-based (usage errors do — their messages must be visible to the caller); this feature preserves that scope across the mcp 2.1.0+ upgrade rather than reopening it.
- New ADR (to be created in Phase 110, Task 110.100): records the `SpecMgrServer.call_tool` seam decision — preserving 2.0.0 caller-visible exception text across mcp ≥2.1.0, citing CVE-2026-59951 / upstream #3314 and the relation to issue #211.

### Task List

#### Phase 100: The fix

- [ ] Task 100.100: Bump the `mcp` extra to `>=2.2.0` in `pyproject.toml`; run `uv lock --upgrade-package mcp`; verify `uv.lock` resolves `mcp` to ≥ 2.2.0 (and lockstep `mcp-types`); `uv sync --all-extras --frozen` (REQ-001, ACC-001).
- [ ] Task 100.110: Add the `UnexpectedToolError` import, the `SpecMgrServer(MCPServer)` subclass with the `call_tool` override (`__cause__` re-raise, `from None`), and the singleton switch in `server.py`; update the module docstring (REQ-002, REQ-006).
- [ ] Task 100.120: Write `tests/test_mcp_error_contract.py` — (a) malformed id → `is_error=True` + original message, (b) well-formed-but-absent id → not-found text, (c) healthy call → unchanged shape (REQ-004, ACC-002).
- [ ] Task 100.130: Run the full suite + quality gates; confirm every existing raise-asserting test passes unmodified (REQ-003, REQ-007, ACC-003/ACC-005).

#### Phase 110: Decision record and docs

- [ ] Task 110.100: Create the ADR via `create_adr` (2.0.0 error-text parity via the `call_tool` seam; cite the CVE, SDK #3314, the ADR 519d1206 chain's scoping, and #211); accept it; link it in this feature's Related Decisions (REQ-005, ACC-004).
- [ ] Task 110.110: Update `AGENTS.md`'s `server.py` bullet and add the `CHANGELOG.md` `[Unreleased]` entry; regenerate `specmgr docs` + `specmgr mcp-docs` and confirm clean diffs (REQ-006, ACC-004).
- [ ] Task 110.120: Final verification — full `pytest -n auto`, ruff/vulture/pylint gates, and confirm Dependabot alert #27 is resolved by the lock change (ACC-001/ACC-005).

## Progress

### Current Status

**As of 2026-10-19**: Created in `planning` state; the approach was settled in the planning session (bump to `mcp>=2.2.0` + the `call_tool` error-contract shim + the wire-level regression test + the ADR), with implementation deliberately not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-19T13:27:10.000+02:00 - Created

Feature created to track GitHub issue #221 (Dependabot alert #27, CVE-2026-59951): the `mcp` upgrade to ≥ 2.2.0 plus the `SpecMgrServer.call_tool` shim preserving caller-visible tool error text across the SDK's 2.1.0 exception change. Plan settled (approach chosen over dismiss-as-not-affected after the exposure analysis); implementation deliberately not started at creation.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-19T13:27:10.000+02:00 - Approach: bump to `mcp>=2.2.0` plus the `call_tool` error-contract shim (not dismiss-as-not-affected, not a bare bump)

Three options were considered for alert #27: (1) bump plus the shim preserving the documented raise-based usage-error contract (chosen, per the maintainer decision in the planning session); (2) a bare bump — rejected, because the SDK 2.1.0 #3314 behavior change would silently strip the actionable message text off the wire for the ~152 still-raising call paths, breaking the contract the ADR 519d1206 chain's scoping and the AGENTS.md tool bullets document; (3) dismiss as not affected (valid on its own: stdio/SSE-only plus `stateless_http=True`) — rejected, because the next lock upgrade would land on 2.1.0+ unprepared for the same behavior change, papering over the alert instead of resolving it.

### Related PRs / Commits

- None yet.

### More Information

- Advisory: https://github.com/advisories/GHSA-84m7-p3x7-pcfv (CVE-2026-59951); Dependabot alert #27: https://github.com/dfch/biz.dfch.SpecMgr/security/dependabot/27.
- Upstream behavior change: modelcontextprotocol/python-sdk#3314 (v2.1.0 release notes); the patched line from v2.2.0 (its release notes' #3395 adds the `session_idle_timeout`/`max_sessions` knobs — moot for us, stateless).
- Related tracking: issue #211 (client-side `isError` truncation — the reason the non-raising chain exists; this feature's shim preserves the status quo on that front).
