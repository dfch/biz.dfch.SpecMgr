# `biz.dfch.specmgr.tsk.tools.get_tsk`

``@mcp.tool()`` wrapper: get_tsk (Task 3.8).

Mirrors ``req.tools.get_req`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`TskDocument`: the ``.md`` file itself is
always the source of truth.

Implemented as a tool, not a resource, from the start -- id-based single-
document reads for TSK never had a ``specmgr://tsk/{id}`` resource in the
first place, matching REQ's own revisited conclusion (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614: "Expose id-based REQ document reads as
a tool (get_req), not a resource").

## Functions

### `get_tsk(id: 'str') -> 'TskDocument'`

Read and return the task list identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
TskDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.TskNotFoundError` if no task list has this id.

