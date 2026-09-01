# `biz.dfch.specmgr.gol.tools.get_gol`

``@mcp.tool()`` wrapper: get_gol (Task 3.8).

Mirrors ``prb.tools.get_prb`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`GolDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for GOL: there is no
``specmgr://gol/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against.

## Functions

### `get_gol(id: 'str', raw: 'bool' = False) -> 'GolDocument | str'`

Read and return the goal identified by ``id``.

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
GolDocument | str
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text as a plain string.
    Raises :class:`._paths.GolNotFoundError` if no goal has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a well-formed id for this domain
    (raised before any filesystem access).

