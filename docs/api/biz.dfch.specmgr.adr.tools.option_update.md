# `biz.dfch.specmgr.adr.tools.option_update`

``@mcp.tool()`` wrapper: option_update (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over
``models.adr.v1.mutations.option_update``: re-reads and re-parses the
current on-disk state, then re-renders and re-writes the full file; there
is no in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md``
file itself is always the source of truth. The whole sequence runs
under ``_lock.adr_lock(id)`` so a concurrent mutation against the same
id cannot interleave with it and cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `option_update(id: 'str', full_title: 'str', value: 'str') -> 'str'`

Replace the content of one option on the ADR identified by ``id``.

Lets :class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError`
propagate if no option matches ``full_title``; nothing is written in
that case.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
full_title:
    The option's current full title, e.g. ``"Option 1: A title"``.
value:
    The option's new content.

Returns
-------
str
    The option's new content (i.e. ``value``).

