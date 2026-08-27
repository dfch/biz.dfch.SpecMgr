# `biz.dfch.specmgr.dec.tools.set_status_dec`

``@mcp.tool()`` wrapper: set_status_dec (Task 2.2).

The only path that changes a decision's ``status`` -- mirrors
``gol.tools.set_status_gol``: :class:`~biz.dfch.specmgr.dec.models.v1.DecFrontmatter.status`
has no ``"superseded by ..."`` pattern, just the closed six-value set
(``draft``/``proposed``/``accepted``/``rejected``/``deprecated``/
``superseded`` -- GOL's exact set minus ``implemented``, with decision-specific
meanings for ``deprecated`` = no longer in force, kept for reference, and
``superseded`` = replaced by another decision). Neither ``create_dec`` nor
``update_dec`` accept a ``status`` argument at all -- this is the sole entry
point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``dec_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_dec(id: 'str', status: 'str') -> 'DecDocument'`

Replace the status of the decision identified by ``id``.

Reconstructs the frontmatter via :class:`DecFrontmatter`'s own
constructor (not ``model_copy``), so ``status``'s closed-set validator
actually runs -- an invalid ``status`` raises ``pydantic.ValidationError``
uncaught, and nothing is written. Also bumps ``updated`` to the current
timestamp; every other frontmatter field (``id``/``type``/``created``/
``version``) is carried over unchanged. The body is never touched --
its raw, on-disk markdown (not a render of the parsed model) is read
back and re-persisted verbatim, so this tool cannot introduce any
render-fidelity drift into the body at all.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
status:
    The new status. Must be one of ``"draft"``, ``"proposed"``,
    ``"accepted"``, ``"rejected"``, ``"deprecated"``,
    ``"superseded"`` --
    :class:`~biz.dfch.specmgr.dec.models.v1.DecFrontmatter.status`'s
    six accepted values.

Returns
-------
DecDocument
    The updated document. Raises :class:`._paths.DecNotFoundError` if
    no decision has this id.

