# `biz.dfch.specmgr.adr.tools.option_delete`

``@mcp.tool()`` wrapper: option_delete (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over
``models.adr.v1.mutations.option_delete``: re-reads and re-parses the
current on-disk state, then re-renders and re-writes the full file; there
is no in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md``
file itself is always the source of truth. The whole sequence runs
under ``_lock.adr_lock(id)`` so a concurrent mutation against the same
id cannot interleave with it and cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `option_delete(id: 'str', full_title: 'str') -> 'list[str]'`

Remove one option from the ADR identified by ``id``.

Does not renumber or reorder the remaining options -- deleting one
leaves a gap in the numbering (plan §5). Lets
:class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError` propagate
if no option matches ``full_title``; nothing is written in that case.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
full_title:
    The option's full title, e.g. ``"Option 1: A title"``.

Returns
-------
list[str]
    The remaining options' full titles, in their original order.

