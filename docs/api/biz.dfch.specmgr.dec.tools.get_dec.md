# `biz.dfch.specmgr.dec.tools.get_dec`

``@mcp.tool()`` wrapper: get_dec (Task 2.2).

Mirrors ``gol.tools.get_gol`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`DecDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for DEC: there is no
``specmgr://dec/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as GOL/REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

## Functions

### `get_dec(id: 'str') -> 'DecDocument'`

Read and return the decision identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
DecDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.DecNotFoundError` if no decision has this id.

