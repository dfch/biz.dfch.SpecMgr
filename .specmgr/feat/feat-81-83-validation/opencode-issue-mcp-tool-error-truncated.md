# MCP tool errors (`isError: true`) reach the model as a bare `Error executing tool <name>`, discarding the full error message

<!-- Internal note, not part of the filed issue: filed as anomalyco/opencode#47740
(https://github.com/anomalyco/opencode/issues/47740). Searched anomalyco/opencode issues for duplicates first;
found none matching this symptom (closest: #15041, #25098, both unrelated). Body below mirrors their
bug-report.yml form fields as headings, and is what was actually submitted (H1 title above became the issue
title; this comment was stripped before filing). -->

## Description

When an MCP tool call fails with `isError: true`, the model only receives a bare `Error executing tool <name>` --
the real error text the server put in `content[].text` is dropped. A successful call (`isError: false`) forwards
its full content fine.

Proof: the same MCP server, tool, and input, called two ways -- via the MCP Inspector (raw MCP protocol, no
OpenCode) and via a live OpenCode session. The Inspector always returns the full error; OpenCode always truncates
it to the bare tool name, across every failure mode tested on two unrelated tools of the same server.

| # | Tool call | Failure mode | Inspector | OpenCode |
| - | --- | --- | --- | --- |
| 1 | `get_req(id="./non-existing-file.txt")` | path-like id, `isError:true` | full message | `Error executing tool get_req` |
| 2 | `set_status(id=<uuid>, type=req, status="bogus-status")` | invalid status, `isError:false` (control) | full JSON | full JSON (not truncated) |
| 3 | `set_status(id="deadbeef-dead-dead-dead-deadbeefdead", type=req, status=draft)` | unknown id, `isError:true` | full message | `Error executing tool set_status` |
| 4 | `set_status(id="./non-existing-file.txt", type=req, status=draft)` | path-like id, `isError:true` | full message | `Error executing tool set_status` |
| 5 | `set_status(id=<uuid>, type=req, status=draft, superseded_by="x")` | `superseded_by` misuse, `isError:true` | full message | `Error executing tool set_status` |

Row 2 is a control: the one failure mode that doesn't raise comes through OpenCode intact, so the bug is
specifically about `isError: true`, not the tool or server.

Worked example (row 1):

```bash
npx @modelcontextprotocol/inspector --cli specmgr mcp \
  --method tools/call --tool-name get_req --tool-arg id="./non-existing-file.txt" --format json
```

```json
{"result":{"content":[{"type":"text","text":"Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected"}],"isError":true}}
```

(the check rejects either condition; this id only has the path separator, not `..` -- the message text is the same
either way)

Same call, live in OpenCode, returns only:

```
Error executing tool get_req
```

Where that message comes from, in the MCP server:

```python
# src/biz/dfch/specmgr/req/tools/get_req.py:109 (inside the @mcp.tool()-decorated get_req)
validate_id("req", id)

# src/biz/dfch/specmgr/general/tools/_path_safety.py:106-111 (assert_no_traversal, called by validate_id)
if not id_.strip():
    raise ValueError(f"id {id_!r} is empty; a non-empty id is required")
if _TRAVERSAL_SEQUENCE in id_ or any(separator in id_ for separator in _PATH_SEPARATORS):
    raise ValueError(f"id {id_!r} contains a path separator or a '..' traversal sequence; a bare id is expected")
```

Plain `raise ValueError`, nothing MCP-specific -- the `mcp` Python SDK (FastMCP) is what turns an uncaught
exception from inside a `@mcp.tool()` function into
`CallToolResult(isError=True, content=[TextContent(text=f"Error executing tool {name}: {exc}")])` automatically;
the server itself never constructs that envelope.

- [get_req.py#L109](https://github.com/dfch/biz.dfch.SpecMgr/blob/v0.23.0/src/biz/dfch/specmgr/req/tools/get_req.py#L109)
- [\_path_safety.py#L106-L111](https://github.com/dfch/biz.dfch.SpecMgr/blob/v0.23.0/src/biz/dfch/specmgr/general/tools/_path_safety.py#L106-L111)

## Plugins

None -- this is an MCP server (`biz-dfch-specmgr`), not a plugin.

## OpenCode version

1.18.29

## Steps to reproduce

1. Add an MCP server whose tool raises a plain exception on invalid input (default FastMCP behavior):
   ```json
   {
     "mcp": {
       "specmgr": {
         "type": "local",
         "enabled": true,
         "command": ["uvx", "--from", "biz-dfch-specmgr[mcp]==0.23.0", "specmgr", "mcp"]
       }
     }
   }
   ```
2. Call a tool with input that triggers the failure, e.g. `get_req(id="./non-existing-file.txt")`
   -- any str containing a path separator is rejected, the file doesn't need to exist.
3. Compare against calling the same tool/args through the MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector --cli <server-command> \
     --method tools/call --tool-name <tool> --tool-arg <name>=<value> --format json
   ```

`biz-dfch-specmgr[mcp]==0.23.0` = tag `v0.23.0` (commit `89484c4`) of `github.com/dfch/biz.dfch.SpecMgr`, `main`
branch. Tool versions: `uv`/`uvx` 0.12.1, `npx` 9.2.0 (Node v22.22.1), Python `3.13.13 (main, May 10 2026, 19:26:54) [Clang 22.1.3]`.

## Screenshot and/or share link

None. This is only about tool-result content.

## Operating System

Ubuntu 26.04 LTS

## Terminal

OpenCode TUI with bash.
