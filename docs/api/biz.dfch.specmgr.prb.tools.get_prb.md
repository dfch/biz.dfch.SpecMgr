# `biz.dfch.specmgr.prb.tools.get_prb`

``@mcp.tool()`` wrapper: get_prb (Task 3.8).

Mirrors ``tsk.tools.get_tsk``/``qa.tools.get_qa`` -- a thin file-I/O/id-lookup
adapter that re-reads and re-parses the current on-disk state on every call;
there is no in-memory cache of a parsed :class:`PrbDocument`: the ``.md``
file itself is always the source of truth.

Implemented as a tool, not a resource, from the start -- id-based single-
document reads for PRB never had a ``specmgr://prb/{id}`` resource in the
first place (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614: "Expose id-based
document reads as a tool, not a resource").

## Functions

### `get_prb(id: 'str') -> 'PrbDocument'`

Read and return the problem statement identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
PrbDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.PrbNotFoundError` if no problem statement has
    this id.

