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

### `get_prb(id: 'str', raw: 'bool' = False, offset: 'int | None' = None, limit: 'int | None' = None) -> 'PrbDocument | str'`

Read and return the problem statement identified by ``id``.

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
PrbDocument | str
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text (or its
    ``offset``/``limit`` window) as a plain string.
    Raises :class:`._paths.PrbNotFoundError` if no problem statement has
    this id.

Raises
------
ValueError
    ``offset``/``limit`` coordinates with ``raw=False`` -- a parsed
    document requires the whole body; raised before any file access.

