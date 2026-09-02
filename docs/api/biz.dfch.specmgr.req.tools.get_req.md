# `biz.dfch.specmgr.req.tools.get_req`

``@mcp.tool()`` wrapper: get_req (feat-7-various-improvements Task 0.9).

Mirrors ``adr.tools.get_adr`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`ReqDocument`: the ``.md`` file itself is
always the source of truth.

This tool replaces the earlier ``specmgr://req/{id}`` resource
(``req.resources.req_get``, Task 3.17 in feat-6-requirement-artifact), which
was removed because LLM/agent clients calling this MCP server failed to
reliably invoke it. See ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose
id-based REQ document reads as a tool (get_req), not a resource") for the
full rationale, including why the equivalent ``specmgr://adr/{id}`` resource
was deliberately left untouched.

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same :func:`~biz.dfch.specmgr.general.tools._splice.body_text`
helper the generic ``update`` tool's range splice uses, so the line numbers
a client counts in a raw read index byte-for-byte into the text the server
splices against. With optional read-style ``offset``/``limit`` coordinates
(feat-28-get-update, Phase 2), the same raw read instead returns the window
of that text, served by the shared
:func:`~biz.dfch.specmgr.general.tools._splice.window_body` helper (clamping
out-of-range values, never erroring).

## Functions

### `get_req(id: 'str', raw: 'bool' = False, offset: 'int | None' = None, limit: 'int | None' = None) -> 'ReqDocument | str'`

Read and return the requirement identified by ``id``.

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
ReqDocument | str
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text (or its
    ``offset``/``limit`` window) as a plain string.
    Raises :class:`._paths.ReqNotFoundError` if no requirement has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a well-formed id for this domain
    (raised before any filesystem access), or ``offset``/``limit`` coordinates
    are given with ``raw=False`` (a parsed document requires the whole body;
    also raised before any file access).

