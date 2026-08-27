# `biz.dfch.specmgr.uc.tools.set_status_uc`

``@mcp.tool()`` wrapper: set_status_uc (Task 3.1.5).

The only path that changes a use case's ``status`` -- mirrors
``req.tools.set_status_req``, except
:class:`~biz.dfch.specmgr.uc.models.v2.UcFrontmatter.status` has its own
closed five-value set (``draft``/``proposed``/``accepted``/``deprecated``/
``superseded``), not REQ's seven-value set. Neither ``create_uc`` nor the
generic ``update`` tool in ``general.tools`` accepts a ``status`` argument
at all -- this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.uc.models.v2.UcDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``uc_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_uc(id: 'str', status: 'str') -> 'UcDocument'`

Replace the status of the use case identified by ``id``.

Reconstructs the frontmatter via :class:`UcFrontmatter`'s own
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
    The new status. Must be one of the five values
    :class:`~biz.dfch.specmgr.uc.models.v2.UcFrontmatter.status`
    accepts.

Returns
-------
UcDocument
    The updated document. Raises :class:`._paths.UcNotFoundError` if
    no use case has this id.

