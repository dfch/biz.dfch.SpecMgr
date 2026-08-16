# `biz.dfch.specmgr.uc.tools.get_uc`

``@mcp.tool()`` wrapper: get_uc (Task 3.1.5).

Mirrors ``req.tools.get_req`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`UcDocument`: the ``.md`` file itself is
always the source of truth. The sole id-based read path for UC.

## Functions

### `get_uc(id: 'str') -> 'UcDocument'`

Read and return the use case identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
UcDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.UcNotFoundError` if no use case has this id.

