# `biz.dfch.specmgr.adr.tools.get_adr`

``@mcp.tool()`` wrapper: get_adr (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state on every call; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth.

## Functions

### `get_adr(id: 'str') -> 'Adr'`

Read and return the ADR identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier (plan §9a).

Returns
-------
Adr
    The current on-disk document, freshly re-read and re-parsed.
    Raises :class:`._paths.AdrNotFoundError` if no ADR has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a canonical
    lowercase-hex UUID (feat-38-39-41-43-44 Phase 4, REQ-009; raised
    before any filesystem access).

