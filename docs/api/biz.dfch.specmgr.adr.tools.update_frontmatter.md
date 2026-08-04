# `biz.dfch.specmgr.adr.tools.update_frontmatter`

``@mcp.tool()`` wrapper: update_frontmatter (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state, then re-renders and re-writes the full file; there is no
in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file
itself is always the source of truth. The whole sequence runs under
``_lock.adr_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `update_frontmatter(id: 'str', frontmatter: 'AdrFrontmatter') -> 'Adr'`

Replace the frontmatter of the ADR identified by ``id``.

Whole-object, full-replace semantics (plan §3): the submitted
``frontmatter`` entirely replaces the current one. The one exception
is ``id`` itself -- it is always re-injected from the currently
resolved document, ignoring whatever ``frontmatter.id`` the caller
submitted, because the id is system-managed and never changes via this
tool (plan §9a), even though every other frontmatter key follows
normal full-replace semantics.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
frontmatter:
    The new frontmatter to write (its ``id`` field is ignored).

Returns
-------
Adr
    The updated document. Raises :class:`._paths.AdrNotFoundError` if
    no ADR has this id.

