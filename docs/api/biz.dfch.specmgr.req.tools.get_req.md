# `biz.dfch.specmgr.req.tools.get_req`

``@mcp.tool()`` wrapper: get_req (feat-7-various-improvements Task 0.9).

Mirrors ``adr.tools.get_adr`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`ReqDocument`: the ``.md`` file itself is
always the source of truth.

This tool replaces the earlier ``specmgr://req/{id}`` resource
(``req.resources.req_get``, Task 3.17 in feat-6-requirement-artifact), which
was removed because LLM/agent clients calling this MCP server failed to
reliably invoke it. See ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose
id-based REQ document reads as a tool (get_req), not a resource") for the
full rationale, including why the equivalent ``specmgr://adr/{id}`` resource
was deliberately left untouched.

## Functions

### `get_req(id: 'str') -> 'ReqDocument'`

Read and return the requirement identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
ReqDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.ReqNotFoundError` if no requirement has this id.

