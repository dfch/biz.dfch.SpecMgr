# `biz.dfch.specmgr.adr.resources.adr_get`

Resource: specmgr://adr/{id}.

Implemented as an MCP resource rather than an ``@mcp.tool()``,
matching this repo's existing ``specmgr://version`` convention.

## Functions

### `adr_get(id: 'str') -> 'Adr'`

Return the ADR identified by ``id`` as a template resource.

Same id-resolution and no-cache, re-read-per-call design as
``adr.tools.get_adr.get_adr`` -- this is simply that same
read exposed as an MCP resource (``specmgr://adr/{id}``) instead of a
``@mcp.tool()``, for a host that wants to address a specific ADR as
context without an explicit tool call.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
Adr
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`~biz.dfch.specmgr.adr.tools._paths.AdrNotFoundError`
    if no ADR has this id.

