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

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against. With optional read-style ``offset``/``limit`` coordinates
(feat-28-get-update, Phase 2), the same raw read instead returns the window
of that text, served by the shared
:func:`~biz.dfch.specmgr.general.tools._splice.window_body` helper (clamping
out-of-range values, never erroring).

## Functions

### `get_qa(id: 'str', raw: 'bool' = False, offset: 'int | None' = None, limit: 'int | None' = None) -> 'QaDocument | str'`

Read and return the Question and Answer (QA) document identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
raw:
    With ``False`` (the default), return the parsed document, exactly
    as before. With ``True``, return the frontmatter-stripped body
    text verbatim as a plain string -- the same text whose 1-based
    lines the generic ``update`` tool's ``offset``/``limit``
    coordinates address (shared body-extraction helper with the
    splice) -- optionally windowed by ``offset``/``limit`` (see below).
offset:
    With ``raw=True`` only: the 1-based first body line of the window
    to return (default 1; values below 1 floor to 1, values past the
    last body line return the empty string).
limit:
    With ``raw=True`` only: the number of body lines the window spans
    (default through the end of the body; capped at the remaining
    lines, a negative value returns the empty string).

Returns
-------
QaDocument | str
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text (or its
    ``offset``/``limit`` window) as a plain string.
    Raises :class:`._paths.QaNotFoundError` if no QA document has this id.

Raises
------
ValueError
    ``offset``/``limit`` coordinates with ``raw=False`` -- a parsed
    document requires the whole body; raised before any file access.

