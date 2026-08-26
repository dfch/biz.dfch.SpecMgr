# `biz.dfch.specmgr.gol.tools.get_gol`

``@mcp.tool()`` wrapper: get_gol (Task 3.8).

Mirrors ``prb.tools.get_prb`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`GolDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for GOL: there is no
``specmgr://gol/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

## Functions

### `get_gol(id: 'str') -> 'GolDocument'`

Read and return the goal identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
GolDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.GolNotFoundError` if no goal has this id.

