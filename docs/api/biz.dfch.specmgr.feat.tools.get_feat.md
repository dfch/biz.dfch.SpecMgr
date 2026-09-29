# `biz.dfch.specmgr.feat.tools.get_feat`

``@mcp.tool()`` wrapper: get_feat (Task 2.3).

Mirrors ``dec.tools.get_dec`` -- a thin file-I/O/id-lookup adapter. The
``README.md`` file itself remains the sole source of truth (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3); the underlying single-file read now
routes through ``feat``'s own bespoke content-hash-validated in-memory
cache (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d, ``._cache``) that skips
re-parsing when a file's content hash is unchanged since its last read, so
a stale entry is structurally impossible.

This tool is the sole id-based read path for FEAT: there is no
``specmgr://feat/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as every other domain's own ``get_*`` tools).

``raw=True`` returns the frontmatter-stripped body text verbatim instead of
the parsed document -- produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against. With optional read-style ``offset``/``limit`` coordinates
(feat-28-get-update, Phase 2), the same raw read instead returns the window
of that text, served by the shared
:func:`~biz.dfch.specmgr.general.tools._splice.window_body` helper (clamping
out-of-range values, never erroring). With an optional ``numbered=True``
(feat-153-off-by-n, Phase 3), each returned body line is additionally
prefixed with its 1-based absolute body-line number in the ``"<n>: "``
form.

## Functions

### `get_feat(id: 'str', raw: 'bool' = False, offset: 'int | None' = None, limit: 'int | None' = None, numbered: 'bool' = False) -> 'FeatDocument | str | ParseFailureResult'`

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
numbered:
    With ``raw=True`` only: when ``True``, prefix every returned body
    line with its 1-based absolute body-line number in the ``"<n>: "``
    form (plain decimal, no padding) -- under ``offset``/``limit``
    windowing the numbers start at the clamped ``offset`` and never
    restart at 1, so a number seen in the output can be fed straight
    back into the generic ``update`` tool's ``offset``. Numbered
    output must never be fed back verbatim as ``content`` for
    ``update`` or ``create_feat`` -- strip the ``"<n>: "`` prefix from
    each line first (it is likewise never a valid ``edit`` ``old_str``).
    Combining it with ``raw=False`` raises ``ValueError`` (see
    ``Raises``).

Returns
-------
FeatDocument | str | ParseFailureResult
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text (or its
    ``offset``/``limit`` window) as a plain string. With
    ``numbered=True``, every returned line is additionally prefixed
    with its ``"<n>: "`` 1-based absolute body-line number. When the
    document
    exists but fails to parse, a
    :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
    (``error``/``path``/``id``) is returned instead of raising --
    ``error`` carries the same parse defect as the domain's own ``list``
    tool's failed-row ``error`` for the same file (identical field path
    and cause, though the trailing pydantic documentation line may
    differ by read order/cache state; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c,
    Option B, 2026-09-26 -- the str-faithful reconstruction is tracked
    as a follow-up issue);
    ``raw=True`` never returns a broken document's raw text.
    Raises :class:`._paths.FeatNotFoundError` if no feature has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a well-formed
    ``feat-NNN-slug`` (raised before any filesystem access), or
    ``offset``/``limit`` coordinates are given with ``raw=False``
    (a parsed document requires the whole body), or
    ``numbered=True`` is given with ``raw=False`` (numbering is a
    ``raw=True``-only feature) -- both read-argument misuses raised
    before any file access.

