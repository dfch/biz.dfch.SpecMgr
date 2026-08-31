# `biz.dfch.specmgr.sop.tools.get_sop`

``@mcp.tool()`` wrapper: get_sop (Task 2.2).

Mirrors ``dec.tools.get_dec`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`SopDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for SOP: there is no
``specmgr://sop/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as GOL/DEC/REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

``raw=True`` returns the frontmatter-stripped body text verbatim instead of
the parsed document -- produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against.

## Functions

### `get_sop(id: 'str', raw: 'bool' = False) -> 'SopDocument | str'`

Read and return the SOP identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
raw:
    With ``False`` (the default), return the parsed document, exactly
    as before. With ``True``, return the frontmatter-stripped body
    text verbatim as a plain string -- the same text whose 1-based
    lines the generic ``update`` tool's ``begin``/``end`` coordinates
    address (shared body-extraction helper with the splice).

Returns
-------
SopDocument | str
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text as a plain string.
    Raises :class:`._paths.SopNotFoundError` if no SOP has this id.

