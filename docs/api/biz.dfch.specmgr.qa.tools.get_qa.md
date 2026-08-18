# `biz.dfch.specmgr.qa.tools.get_qa`

``@mcp.tool()`` wrapper: get_qa (Phase 4, Task 4.1).

Mirrors ``adr.tools.get_adr``/``req.tools.get_req`` -- a thin
file-I/O/id-lookup adapter that re-reads and re-parses the current on-disk
state on every call; there is no in-memory cache of a parsed
:class:`QaDocument`: the ``.md`` file itself is always the source of truth.

There is no ``specmgr://qa/{id}`` resource -- id-based reads go through
this tool only, mirroring REQ's own choice; see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource") for the full rationale.

## Functions

### `get_qa(id: 'str') -> 'QaDocument'`

Read and return the Question and Answer (QA) document identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
QaDocument
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.QaNotFoundError` if no QA document has this id.

