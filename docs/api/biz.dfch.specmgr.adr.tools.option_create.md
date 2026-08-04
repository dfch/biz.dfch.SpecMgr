# `biz.dfch.specmgr.adr.tools.option_create`

``@mcp.tool()`` wrapper: option_create (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over
``models.adr.v1.mutations.option_create``: re-reads and re-parses the
current on-disk state, then re-renders and re-writes the full file; there
is no in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md``
file itself is always the source of truth. The whole sequence runs
under ``_lock.adr_lock(id)`` so a concurrent mutation against the same
id cannot interleave with it and cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `option_create(id: 'str', partial_title: 'str', value: 'str') -> 'str'`

Append a new option to the ADR identified by ``id``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
partial_title:
    The ``{title}`` portion after ``"Option {number}: "``.
value:
    The new option's content.

Returns
-------
str
    The assigned full title, e.g. ``"Option 3: A title"``.

