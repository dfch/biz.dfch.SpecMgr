# `biz.dfch.specmgr.rsk.tools.get_rsk`

``@mcp.tool()`` wrapper: get_rsk (Task 3.8).

Mirrors ``tsk.tools.get_tsk`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`RskDocument`: the ``.md`` file itself is
always the source of truth.

Implemented as a tool, not a resource, from the start -- id-based single-
document reads for RSK never had a ``specmgr://rsk/{id}`` resource in the
first place, matching TSK's own shape (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614: "Expose id-based document reads as a
tool, not a resource").

## Functions

### `get_rsk(id: 'str') -> 'RskDocument'`

Read and return the risk identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
RskDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.RskNotFoundError` if no risk has this id.

