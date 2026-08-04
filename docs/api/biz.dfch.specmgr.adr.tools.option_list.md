# `biz.dfch.specmgr.adr.tools.option_list`

``@mcp.tool()`` wrapper: option_list (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.option_list``:
re-reads and re-parses the current on-disk state; there is no in-memory
cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file itself is
always the source of truth.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `option_list(id: 'str') -> 'list[str]'`

Return the full titles of every option on the ADR identified by ``id``.

Read-only -- does not write.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
list[str]
    Full titles, e.g. ``["Option 1: A title"]``, in document order.

