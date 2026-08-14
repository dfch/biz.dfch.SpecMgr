# `biz.dfch.specmgr.req.resources.req_get`

Resource: specmgr://req/{id} (Task 3.17).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``adr.resources.adr_get``/``specmgr://adr/{id}``. Per Task 3.9's design
discussion, id-based single-document read is a resource only, everywhere in
the REQ lifecycle surface -- there is no ``get_req`` tool.

## Functions

### `req_get(id: 'str') -> 'ReqDocument'`

Return the requirement identified by ``id`` as a template resource.

Same id-resolution and no-cache, re-read-per-call design as every other
REQ tool/resource -- the ``.md`` file on disk is always re-read and
re-parsed, never cached in memory.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
ReqDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`~biz.dfch.specmgr.req.tools._paths.ReqNotFoundError`
    if no requirement has this id.

