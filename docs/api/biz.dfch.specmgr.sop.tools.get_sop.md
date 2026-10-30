# `biz.dfch.specmgr.sop.tools.get_sop`

``@mcp.tool()`` wrapper: get_sop (Task 2.2).

Mirrors ``dec.tools.get_dec`` -- a thin file-I/O/id-lookup adapter. The
``.md`` file itself remains the sole source of truth (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3); its underlying ``load_by_id`` now
routes through a content-hash-validated, per-domain in-memory cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d, ``._cache``) that skips re-parsing
when a file's content hash is unchanged since its last read, so a stale
entry is structurally impossible.

This tool is the sole id-based read path for SOP: there is no
``specmgr://sop/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as GOL/DEC/REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

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

**Language variants (feat-197-i18n Phase 125, ADR 38efdb66 items 1/5/6/7).**
A 1:1 port of ``get_dec``'s ``language`` handling. The optional ``language``
parameter (default ``"en"``) selects which on-disk variant of the id to
read: omitted/``"en"`` = the flat ``docs/sop/<id>.md`` document, exactly
today's behavior; any other shape-validated ISO 639-1-shaped code (e.g.
``"de"``) = the variant at ``docs/sop/{language}/<id>.md`` (the EN source's
exact basename). The language is shape-guarded by
:func:`biz.dfch.specmgr.general.tools._path_safety.assert_language` before
any filesystem access (the same discipline as ``id``), and a shape-valid
language without a packaged heading-mapping table is rejected up front with
the table loader's actionable error, also before any filesystem access.
A ``raw=True`` read of a variant returns the variant's on-disk body
verbatim (its translation preserved); a ``raw=False`` read parses through
the variant's heading table, so the structured model holds canonical
heading text (ACC-004/ACC-011). The non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` channel works
for a broken variant file exactly as for EN: the ``error`` text is
byte-identical to ``list_sop(language=...)``'s failed row for the same
file (ADR 9080b37c).

## Functions

### `get_sop(id: 'str', raw: 'bool' = False, offset: 'int | None' = None, limit: 'int | None' = None, numbered: 'bool' = False, language: 'str' = 'en') -> 'SopDocument | str | ParseFailureResult'`

Read and return the SOP identified by ``id``.

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
numbered:
    With ``raw=True`` only: when ``True``, prefix every returned body
    line with its 1-based absolute body-line number in the ``"<n>: "``
    form (plain decimal, no padding) -- under ``offset``/``limit``
    windowing the numbers start at the clamped ``offset`` and never
    restart at 1, so a number seen in the output can be fed straight
    back into the generic ``update`` tool's ``offset``. Numbered
    output must never be fed back verbatim as ``content`` for
    ``update`` or ``create_sop`` -- strip the ``"<n>: "`` prefix from
    each line first (it is likewise never a valid ``edit`` ``old_str``).
    Combining it with ``raw=False`` raises ``ValueError`` (see
    ``Raises``).
language:
    The language variant to read (feat-197-i18n Phase 125, ADR
    38efdb66 items 1/5/6): ``"en"`` (the default, same as omitting it)
    reads the flat ``docs/sop/`` document -- today's exact behavior;
    any other ISO 639-1-shaped lowercase two-letter code (e.g.
    ``"de"``) reads the variant at ``docs/sop/{language}/`` under the
    EN source's exact basename. Shape-guarded before any filesystem
    access (like ``id``); a shape-valid code without a packaged
    heading-mapping table is rejected up front with the table
    loader's actionable error, also before any filesystem access. For
    a variant, ``raw=True`` returns its on-disk body verbatim and
    ``raw=False`` parses through its heading table (canonical heading
    text in the model).

Returns
-------
SopDocument | str | ParseFailureResult
    With ``raw=False``: the current on-disk document, freshly re-read
    and re-parsed. With ``raw=True``: the body text (or its
    ``offset``/``limit`` window) as a plain string. With
    ``numbered=True``, every returned line is additionally prefixed
    with its ``"<n>: "`` 1-based absolute body-line number. When the
    document
    exists but fails to parse, a
    :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
    (``error``/``path``/``id``) is returned instead of raising --
    ``error`` is byte-identical to the domain's own ``list`` tool's failed-row ``error`` for
    the same file (identical field path and cause, including the trailing pydantic
    documentation line; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c);
    ``raw=True`` never returns a broken document's raw text.
    Raises :class:`._paths.SopNotFoundError` if no SOP has this id.

Raises
------
ValueError
    ``language`` is not an ISO 639-1-shaped lowercase two-letter code, or a
    non-default ``language`` has no packaged heading-mapping table (both raised
    before any filesystem access, the same guard discipline as ``id``);
    ``id`` is a path-injection attempt or not a well-formed id for this domain
    (raised before any filesystem access), or ``offset``/``limit`` coordinates
    are given with ``raw=False`` (a parsed document requires the whole body),
    or ``numbered=True`` is given with ``raw=False`` (numbering is a
    ``raw=True``-only feature) -- both read-argument misuses raised before
    any file access.

