# [Bug] MCP tool call failures (`isError: true`) reach the model as a bare `"Error executing tool <name>"`, discarding the full `CallToolResult` message

> **Status**: Drafted, not filed. Prepared while investigating GitHub issues #81/#83 of `biz.dfch.SpecMgr`
> (see `.specmgr/feat/feat-81-83-validation/README.md`), saved here for reference/reuse. File this against
> `anomalyco/opencode` once reviewed. See also ADR 519d1206-4d2a-4500-9046-6db635209996, which records
> `biz.dfch.SpecMgr`'s own `validate` tool design as a workaround for the defect described here.

## Environment

- OpenCode version: **1.18.27**
- MCP server: a local `stdio` Python server built on the `mcp`/FastMCP SDK (`biz-dfch-specmgr`'s `specmgr mcp`
  command), but the bug is not specific to this server -- see "Why this looks like an OpenCode-side issue" below.
- OS: Linux

## Summary

When an MCP tool call fails and the server returns a `CallToolResult` with `isError: true`, the model (the LLM
driving the OpenCode session) only ever receives a short, contentless `"Error executing tool <name>"` string.
The actual error detail -- which the MCP server places in full inside `content[].text` -- never reaches the
model's context. A tool call that *succeeds* (`isError: false`), by contrast, has its full `content` -- of any
size we tested -- forwarded to the model intact.

This makes any MCP tool that reports failures by raising/returning `isError: true` effectively useless for
communicating *why* it failed to the agent, even when the tool author did the work of producing a detailed,
actionable message.

## Steps to Reproduce

1. Configure an MCP server (stdio or otherwise) that exposes a tool which, on invalid input, returns
   `CallToolResult(isError=True, content=[TextContent(type="text", text="Error executing tool <name>: <long, detailed message>")])` -- this is exactly what a Python FastMCP tool produces by default when the tool
   function raises an exception.
2. In an OpenCode session, call that tool with input that triggers the failure.
3. Observe the tool result surfaced to the model.

### Minimal concrete repro used during investigation

Any of the following calls into `biz-dfch-specmgr`'s MCP server (`specmgr mcp`) reproduce it:

- `validate_req` with body-only content whose `created`/`updated` frontmatter fields use a naive ISO-8601
  timestamp instead of the required `yyyy-MM-dd HH:mm:ss.fff` + `Z`/offset variant.
- `validate_dec` with an `## Updates` sub-heading using an em dash (`—`) instead of a hyphen (`-`).
- `validate_feat` with a `feat` document body whose `Updates`/`Decisions Made` heading timestamp doesn't match
  the required regex.

All three are ordinary Python tool functions that raise `pydantic.ValidationError`/`AssertionError` on invalid
input; the MCP/FastMCP framework wraps that exception into `CallToolResult(isError=True, content=[...])`
automatically.

## Expected Behavior

The model receives the full `content[].text` of the `CallToolResult`, e.g.:

```
Error executing tool validate_req: 2 validation errors for ReqFrontmatter
created
  req validate_req: req frontmatter block, field 'created' (document line 2): Value error, created/updated
  '2026-08-05T08:15:42' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed
  '+HH:mm'/'-HH:mm' offset [...]
updated
  req validate_req: req frontmatter block, field 'updated' (document line 6): Value error, created/updated
  '2026-08-06T03:27:27' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed
  '+HH:mm'/'-HH:mm' offset [...]
```

## Actual Behavior

The model receives only:

```
Error executing tool validate_req
```

Nothing after the tool name -- no colon, no validation detail, no indication of which field or line failed.

## Evidence That the Full Message Exists on the Wire (Ruling Out the MCP Server)

A standalone script using the `mcp` Python SDK's `stdio_client`/`ClientSession` was used to call the exact same
tool with the exact same input, bypassing OpenCode's tool-calling layer entirely and inspecting the raw
`CallToolResult` returned by the server process:

```python
result = await session.call_tool("validate_req", {"content": REQ_REPRO, "full": True})
print("isError:", result.is_error)  # -> True
print(result.content[0].model_dump())  # -> full text below
```

```json
{
  "type": "text",
  "text": "Error executing tool validate_req: 2 validation errors for ReqFrontmatter\ncreated\n  req validate_req: req frontmatter block, field 'created' (document line 2): Value error, created/updated '2026-08-05T08:15:42' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset [type=tool_boundary_error, input_value='2026-08-05T08:15:42', input_type=str]\nupdated\n  req validate_req: req frontmatter block, field 'updated' (document line 6): Value error, created/updated '2026-08-06T03:27:27' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset [type=tool_boundary_error, input_value='2026-08-06T03:27:27', input_type=str]",
  "annotations": null,
  "meta": null
}
```

This confirms the MCP server sends the complete, detailed message. The truncation happens strictly between the
wire response and what the model sees inside the OpenCode-driven session.

## Why This Looks Like an OpenCode-Side Issue (Not the MCP Server's)

A shallow clone of `anomalyco/opencode` (`dev` branch) was inspected. The code path that handles a failed MCP
tool call does not appear to discard the message -- if anything, it goes out of its way to preserve it:

```ts
// packages/opencode/src/mcp/catalog.ts:68-74 (dynamicTool execute(), used for direct MCP tool calls)
if (result.isError)
  throw new Error(
    result.content
      .flatMap((item) => (item.type === "text" ? [item.text] : []))
      .filter((text) => text.trim())
      .join("\n\n") || "MCP tool returned an error",
  )
```

The identical pattern also exists in the "Code Mode" sandboxed tool-calling path:

```ts
// packages/opencode/src/tool/code-mode.ts:161-167 (invokeChildTool)
if (raw.isError)
  throw new Error(
    raw.content
      .flatMap((item) => (item.type === "text" ? [item.text] : []))
      .filter((text) => text.trim())
      .join("\n\n") || "MCP tool returned an error",
  )
```

Both join every `text` content block into the thrown `Error`'s `.message`, so the full detail should survive at
least this point. Yet the observed behavior in this session (OpenCode 1.18.27) is a bare
`"Error executing tool <name>"` with nothing else -- inconsistent with this code, as read.

Two possibilities, in order of likelihood based on available evidence:

1. Something further downstream of `catalog.ts`/`code-mode.ts` -- possibly in how the underlying LLM/tool-calling
   SDK (e.g. the `ai` package's own tool-error-to-model-message serialization, which was not available to inspect
   in this source-only clone) formats a thrown tool error before it is placed into the model's context -- discards
   everything but a short summary.
2. A different/older code path than the one inspected on `dev` is active in 1.18.27, or some wrapping
   layer/config in this particular deployment reformats tool errors before they reach the model.

This report intentionally does not claim a single, pinpointed line as root cause -- only that the symptom is
real, reproducible, and inconsistent with the mainline `dev`-branch code inspected.

## Impact

Any MCP tool author who puts effort into producing an actionable, detailed failure message (field path, line
number, cause/fix hint, etc.) has that work silently discarded whenever they signal failure via `isError: true` --
the standard, spec-compliant way to report a tool failure. The only reliable way found so far to get a detailed
message to the model is to avoid the error channel entirely and return the detail as normal, successful
(`isError: false`) tool output instead -- which is not a fix, only a workaround available to server authors who
can afford to redesign their tool's contract around it.

## Suggested Next Steps for Investigation

- Confirm whether `dynamicTool`'s thrown `Error` (`catalog.ts`) is what actually reaches the model, or whether
  the underlying LLM/tool SDK's own error handling replaces/truncates `error.message` before it is included in
  the conversation history sent to the provider.
- Check whether there is a deliberate, but overly aggressive, message-length or content sanitization step
  specifically for tool-call *errors* (as opposed to tool-call *results*), given that large *successful* tool
  outputs were observed to pass through this same session without truncation.
- If reproducible outside this specific deployment, add a regression test asserting that a `CallToolResult` with
  `isError: true` and a multi-line `content[].text` payload is fully preserved in the message/context passed to
  the model.
