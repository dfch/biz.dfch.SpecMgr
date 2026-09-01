# `biz.dfch.specmgr.feat.tools.get_feat`

``@mcp.tool()`` wrapper: get_feat (Task 2.3).

Mirrors ``dec.tools.get_dec`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`FeatDocument`: the ``README.md`` file
itself is always the source of truth.

This tool is the sole id-based read path for FEAT: there is no
``specmgr://feat/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as every other domain's own ``get_*`` tools).

``raw=True`` returns the frontmatter-stripped body text verbatim instead of
the parsed document -- produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against.

## Functions

### `get_feat(id: 'str', raw: 'bool' = False) -> 'FeatDocument | str'`

Read and return the feature identified by ``id``.

Parameters
----------
id:
    The document's ``feat-NNN-slug`` id -- also the exact name of its
    containing folder under the feature base directory.
raw:
    With ``False`` (the default), return the parsed document, exactly
    as before. With ``True``, return the frontmatter-stripped body
    text verbatim as a plain string -- the same text whose 1-based
    lines the generic ``update`` tool's ``begin``/``end`` coordinates
    address (shared body-extraction helper with the splice).

Returns
-------
FeatDocument | str
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text as a plain string.
    Raises :class:`._paths.FeatNotFoundError` if no feature has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a well-formed
    ``feat-NNN-slug`` (raised before any filesystem access).

