# `biz.dfch.specmgr.adr.tools.set_status`

``@mcp.tool()`` wrapper: set_status (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.set_status``:
re-reads and re-parses the current on-disk state, then re-renders and
re-writes the full file; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth. The whole sequence runs under ``_lock.adr_lock(id)`` so a
concurrent mutation against the same id cannot interleave with it and
cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `set_status(id: 'str', status: 'str', superseded_by: 'str | None' = None) -> 'Adr'`

Replace the status of the ADR identified by ``id``.

Delegates to ``models.adr.v1.mutations.set_status``: when
``superseded_by`` is given, ``status`` is composed as
``f"superseded by {superseded_by}"`` instead of being used verbatim.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
status:
    The new status. Ignored if ``superseded_by`` is given.
superseded_by:
    When given, composes the ``"superseded by ..."`` status string.

Returns
-------
Adr
    The updated document.

