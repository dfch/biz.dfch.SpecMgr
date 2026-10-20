---
status: accepted
date: '2026-10-19'
decision-makers: OpenCode agent + user decision
id: 80305c52-102e-4833-a233-3468bef29e11
version: 1.0.0
---

# Preserve caller-visible tool error text across mcp >= 2.1.0 via a call_tool seam

## Context and Problem Statement

GitHub issue #221 / Dependabot alert #27 (GHSA-84m7-p3x7-pcfv, CVE-2026-59951, medium, CVSS 7.5): the repo pins `mcp>=2.0.0` in the `mcp` extra of `pyproject.toml`, with the lock at `= 2.0.0`. The advisory names unbounded session accumulation in StreamableHTTP **stateful** mode, which this repo is effectively not exposed to (it serves `stdio` (default) and `sse` only, and the one `streamable-http` path already passes `stateless_http=True`), but the patched line (from v2.2.0) nonetheless has to be adopted -- and it cannot be adopted as-is, for the reason below.

SDK v2.1.0 (upstream modelcontextprotocol/python-sdk#3314) changed how a tool handler's raised exception is surfaced. Verified against the shipped source of 2.0.0 vs 2.1.0/2.2.0: in v2.0.0 a tool raising `ValueError("…")` is wrapped by the SDK's `Tool.run` as `ToolError(f"Error executing tool {name}: {exc}")` and reaches the client as `CallToolResult(is_error=True, text="Error executing tool <name>: <original message>")`; in v2.1.0+ the same crash is wrapped instead as `UnexpectedToolError(f"Error executing tool {name}")` -- by design, "nothing from an unexpected exception reaches the client" -- with the original message surviving only in `__cause__` (which the SDK always sets, via `raise … from exc`) and in the server log.

This repo has ~127 raise sites whose documented caller contract *is* that message text: the `_path_safety` invalid-id `ValueError`s, the 12× `XNotFoundError`s, `create_feat`'s `FileExistsError`, and so on -- enumerated in `AGENTS.md`'s tool bullets and deliberately left raising by ADR 519d1206-4d2a-4500-9046-6db635209996 (case 1 of the non-raising structured-result chain), which converted only content-validation/parse-failure errors to non-raising results and left usage errors raising precisely because their messages must be visible to the caller. A bare bump to `mcp >= 2.2.0` would therefore silently strip the actionable message text off the wire for all of those paths (and would leave open issue #211 -- the client-side `isError` truncation of exactly that channel -- with nothing actionable left to truncate), so the feature must restore the caller-visible text. The ~152 figure as literally written at the time this ADR was authored was a rough estimate; it was re-derived and corrected to ~127 on 2026-10-20 (feat-221-mcp-220-error-contract's review pass) by a multiline-aware grep over `src/**/*.py` (excluding `__pycache__`) for the usage-error family this sentence names -- `raise ValueError` (95), `raise FileExistsError` (2), and the `raise *NotFoundError` family (30) -- and this ADR's other occurrences of the figure (Decision Drivers, Decision Outcome, Option 4's cons) were amended in place to the same value.

## Decision Drivers

- Adopt the patched `mcp` line (`>= 2.2.0` -- fixing CVE-2026-59951 / GHSA-84m7-p3x7-pcfv, Dependabot alert #27) without breaking the documented raise-based usage-error contract of the ~127 still-raising call sites.
- A single uniform seam -- one `SpecMgrServer(MCPServer)` subclass in `server.py` overriding only the public `call_tool` -- with no per-domain logic; the `adr` domain's tools are covered by construction.
- Zero change to the Python-level raise contract: every tool function called directly still raises the same exception types with the same messages (all existing raise-asserting tests pass unmodified), and the `read_resource`/`get_prompt` paths are untouched.
- The behavioral guard for future 2.x bumps is a wire-level regression test, not the locked version number (the lock may resolve > 2.2.0 -- it resolved 2.3.0).
- Server logging is preserved (the SDK's own catch still logs the exception), and the ADR 519d1206 chain's scope is NOT reopened: converting raise sites to non-raising structured results stays explicitly out of scope.

## Considered Options

- Option 1 (chosen): the `call_tool` seam re-raise -- `server.py` defines a `SpecMgrServer(MCPServer)` subclass overriding only the public `call_tool`, re-raising `UnexpectedToolError.__cause__` (`from None`); the SDK's own `_handle_call_tool` catch then stringifies the original into the `is_error=True` result -- v2.0.0's wire shape minus the `Error executing tool <name>: ` prefix, uniform for every tool.
- Option 2: a middleware or `Extension` interceptor around tool calls -- rejected: both layers sit outside `_handle_call_tool`, which catches the exception into a `CallToolResult` before either can see it, so the original message is already swallowed at that point.
- Option 3: the shim re-prepending `Error executing tool {name}: ` when the original message does not self-identify -- rejected: it adds per-exception text inspection to a seam meant to be uniform, and the only lost piece is the tool name, which the client already knows from its own `call_tool` request.
- Option 4: converting the still-raising call sites to non-raising structured results -- rejected: out of scope; that is the ADR 519d1206 chain's domain, a separate future feature if the project goes that way.

## Decision Outcome

Option 1: `server.py` defines `SpecMgrServer(MCPServer)` overriding only the public `call_tool(name, arguments, context=None)`: `try: result = await super().call_tool(...); return result` / `except UnexpectedToolError as exc: raise exc.__cause__ from None`. `UnexpectedToolError` is imported from `mcp.server.mcpserver.exceptions` -- a deep import, acceptable because the project already deep-imports `mcp.server.mcpserver.resources.base` in four test files, and because the SDK's own `UnexpectedToolError` docstring points at exactly this seam ("Catch it around `MCPServer.call_tool()` to tell a crash from a deliberate `ToolError`"). The override is selective by construction: it catches only `UnexpectedToolError` -- the SDK's crash wrapper, whose message is the bare `Error executing tool <name>` and which swallows the original -- and never the SDK's deliberate `ToolError`/`ResourceError` failures, which already carry their own text after the prefix and pass through unchanged. The re-raised `__cause__` is total: the SDK always wraps with `raise … from exc` (for a nested tool or resource crash, per the SDK's own docstring, `__cause__` is the nested `Unexpected…Error` wrapper); `from None` avoids a doubled exception chain in the server log. The SDK's own `_handle_call_tool` catch (which invokes `self.call_tool` inside its `try` block) then stringifies the re-raised original -- a plain `ValueError`/`NotFoundError`, never an `MCPError` -- into `CallToolResult(content=[TextContent(str(original))], is_error=True)`: v2.0.0's shape minus the `Error executing tool <name>: ` prefix. The server singleton becomes `mcp = SpecMgrServer(name="specmgr", instructions=…, lifespan=_lifespan)` with unchanged arguments, and the override is uniform for every tool registered on the server (the `adr` domain's tools included) -- no per-domain logic.

The post-shim wire is v2.0.0's shape minus the prefix, accepted but not uniform: some messages already self-identify, while the `_path_safety` id-validation `ValueError`s and the 12× `XNotFoundError`s do not name the tool, so their post-shim client-visible text is strictly less informative than 2.0.0's -- the failing id/value and base path remain, so the messages stay actionable; the only lost piece is the tool name, which the client already knows from its own `call_tool` request.

The shim preserves the status quo -- including the client-side `isError` truncation of those messages tracked by open issue #211 (the very defect the ADR 519d1206 chain works around on the content-validation/parse-failure channels) -- and does NOT reopen the chain's scope: converting any of the ~127 still-raising call sites to non-raising structured results is explicitly out of scope for this decision and a separate future feature if the project goes that way.

### Consequences

- Good: the patched `mcp` line (`>= 2.2.0` -- fixing CVE-2026-59951 / GHSA-84m7-p3x7-pcfv, Dependabot alert #27) is adopted while the documented caller-visible error text of every still-raising call site is preserved: no security papering-over, no contract break.
- Good: a single uniform seam (`SpecMgrServer` overriding only `call_tool`) -- no per-domain logic, zero change to the Python-level raise contract (all existing raise-asserting tests pass unmodified), the `read_resource`/`get_prompt` paths untouched, and server logging retained (the re-raised original still reaches `_handle_call_tool`'s catch, which logs it with its traceback).
- Good: the behavioral guard for future 2.x bumps is `tests/test_mcp_error_contract.py` -- the in-process, wire-level regression over anyio memory streams -- rather than the locked version number; the lock may resolve > 2.2.0 (it resolved 2.3.0) and that is safe as long as that test stays green.
- Bad: the post-shim wire is v2.0.0's shape minus the `Error executing tool <name>: ` prefix -- accepted but not uniform: the `_path_safety` id-validation and not-found messages do not name the tool, so their client-visible text is strictly less informative than 2.0.0's (the failing id/value and base path remain, so it stays actionable).
- Bad: the shim couples to two SDK internals -- the deep import `mcp.server.mcpserver.exceptions.UnexpectedToolError` and the SDK's `raise … from exc` behavior (`__cause__` total) -- pinned by the regression test, but a future 2.x that changes the wrapping or the `_handle_call_tool` catch breaks the contract silently unless that test is run.
- Bad (tracked, not blocking): the client-side `isError: true` truncation defect (issue #211) is preserved as-is -- the shim restores the message on the wire but does not fix a client that truncates it, exactly like every prior link in the ADR 519d1206 chain (a workaround within this repo's own server, not a client fix).

### Confirmation

Confirmed during feat-221-mcp-220-error-contract's Phase 100 (the fix): `tests/test_mcp_error_contract.py` (4 tests) drives an in-process client session over anyio memory streams (no transport) and pins the restored wire shape -- (a) `get_req` with a malformed id (`id="not-a-uuid"`) returns `is_error=True` with the content text equal to the original `_path_safety` `ValueError` message; (b) a well-formed-but-absent id returns `is_error=True` with the domain's not-found message; (c) a healthy call returns the unchanged success shape. Verified against the installed 2.3.0 source: `Tool.run` still wraps a handler crash as `UnexpectedToolError(f"Error executing tool {name}") from exc` (`__cause__` total), and `_handle_call_tool` still stringifies the caught non-`MCPError` exception into the `is_error=True` result. The full suite (4695 passed / 18 skipped / 5955 subtests) is green with zero existing-test modifications (the feature's REQ-003).

## Pros and Cons of the Options

### Option 1: the call_tool seam re-raise (chosen)

#### Pros

- The only layer that can recover the original exception: `_handle_call_tool` -- the SDK layer that converts a raised handler exception into the `CallToolResult` the client receives -- invokes `self.call_tool` inside its own `try` block, so the wrapping `UnexpectedToolError` (with the original in `__cause__`) is still observable exactly at the public `call_tool` boundary, and nowhere above it; the SDK's own `UnexpectedToolError` docstring points at this seam ("Catch it around `MCPServer.call_tool()`…").
- Selective by construction: only the crash wrapper (the one that swallows the message) is re-raised to its `__cause__`; the SDK's deliberate `ToolError`/`ResourceError` failures (which already carry their own text after the prefix) pass through unchanged.
- Zero change to the Python-level raise contract: every tool function called directly still raises the same exception types with the same messages, all existing raise-asserting tests pass unmodified, and the override is uniform for every tool (the `adr` domain's included) with no per-domain logic.
- Logging is retained: the re-raised original still reaches `_handle_call_tool`'s catch, which logs it with its traceback (`logger.exception`).

#### Cons

- The post-shim wire is v2.0.0's shape minus the `Error executing tool <name>: ` prefix -- accepted but not uniform (the id-validation and not-found messages do not name the tool; see the Decision Outcome's Consequences).
- Couples to two SDK internals -- the deep import `mcp.server.mcpserver.exceptions.UnexpectedToolError` and the SDK's `raise … from exc` behavior -- pinned by `tests/test_mcp_error_contract.py` rather than by the locked version number.

### Option 2: a middleware or Extension interceptor

#### Pros

- A framework-provided extension point (the SDK's own middleware/`Extension` API) without subclassing the server.

#### Cons

- Both layers sit OUTSIDE `_handle_call_tool`, which catches the handler exception into a `CallToolResult` before either can see it: by the time the middleware/`Extension` chain observes the call, the original message is already swallowed and only the prefix-less `UnexpectedToolError` (or the constructed `is_error=True` result) remains -- the `__cause__` chain is no longer recoverable through that API.
- It therefore cannot deliver the decision at all: only the handler-level (`call_tool`) override can recover the original via `__cause__`.

### Option 3: the shim re-prepending `Error executing tool {name}: ` when the original message does not self-identify

#### Pros

- The client-visible text would be byte-identical to v2.0.0's for every message -- including the `_path_safety` id-validation and not-found messages that do not name the tool.

#### Cons

- Adds per-exception text inspection ("does this message already self-identify?") to a seam meant to be uniform -- a heuristic that must be re-litigated for every new raise site, where the self-identification classification is itself a judgment call.
- The only lost piece is the tool name, which the client already knows from its own `call_tool` request -- marginal benefit against the mechanism cost.
- Risks double-prefixing or colliding with a message the author already framed to name the tool.

### Option 4: converting the still-raising call sites to non-raising structured results

#### Pros

- Would eliminate the raised-exception channel (and with it the client-side `isError` truncation defect, issue #211) for every site, making the error contract independent of the SDK version's exception surfacing.

#### Cons

- Out of scope for this decision: it is the ADR 519d1206 chain's domain -- whose cases 1-5 converted only the content-validation/parse-failure surfaces and deliberately left usage errors raising because their messages must be visible -- and converting ~127 raise sites is a program, not a CVE fix.
- Would change the documented Python-level contract (all raise-asserting tests), `AGENTS.md`'s tool bullets, and every prompt/skill that names the raising behavior -- a far larger change surface than the security bump justifies.
- It does not unblock the immediate need: the CVE-2026-59951 bump has to happen regardless, with or without this conversion.

## More Information

- GitHub issue #221: https://github.com/dfch/biz.dfch.SpecMgr/issues/221.
- Dependabot alert #27: https://github.com/dfch/biz.dfch.SpecMgr/security/dependabot/27.
- Advisory: GHSA-84m7-p3x7-pcfv (CVE-2026-59951, medium, CVSS 7.5 -- unbounded session accumulation in StreamableHTTP stateful mode; this repo is effectively not exposed: `stdio`/`sse` only, and the one `streamable-http` path already passes `stateless_http=True`).
- Upstream behavior change: modelcontextprotocol/python-sdk#3314 (v2.1.0 release notes -- a tool handler's raised exception reaches the client wrapped as `UnexpectedToolError("Error executing tool <name>")`, the original message surviving only in `__cause__` and the server log).
- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation"): case 1 of the non-raising structured-result chain; its scoping -- which tool errors stay raise-based (usage errors) and which go non-raising (content-validation/parse-failure) -- is what this ADR preserves across the bump rather than reopening.
- GitHub issue #211: the client-side `isError` truncation the shim preserves the status quo on (tracked, not blocking).
- Feature plan and progress: `.specmgr/feat/feat-221-mcp-220-error-contract/README.md` (Phase 100 implements the seam and the regression test this ADR records; its Design Notes carry the full verified SDK facts).
- Behavioral guard: `tests/test_mcp_error_contract.py`.
- Raise-site count correction (feat-221-mcp-220-error-contract review pass, 2026-10-20): the ~152 figure as literally written at the time of authoring was a rough estimate; re-derived over `src/**/*.py` (multiline-aware, excluding `__pycache__`) as 127 sites in the usage-error family this ADR's Context names (`raise ValueError` 95 + `raise FileExistsError` 2 + `raise *NotFoundError` 30). The four occurrences were amended in place to ~127 (see Context and Problem Statement for the full correction note).
