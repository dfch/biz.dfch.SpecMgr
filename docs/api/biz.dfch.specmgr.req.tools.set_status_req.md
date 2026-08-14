# `biz.dfch.specmgr.req.tools.set_status_req`

``@mcp.tool()`` wrapper: set_status_req (Task 3.14).

The only path that changes a requirement's ``status`` -- mirrors
``adr.tools.set_status``, minus the ``superseded_by``-composition special
case: :class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter.status` has no
``"superseded by ..."`` pattern, just the closed seven-value set
(``draft``/``proposed``/``accepted``/``superseded``/``deprecated``/
``rejected``/``implemented``). Neither ``create_req`` nor ``update_req``
accept a ``status`` argument at all -- this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``req_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_req(id: 'str', status: 'str') -> 'ReqDocument'`

Replace the status of the requirement identified by ``id``.

Reconstructs the frontmatter via :class:`ReqFrontmatter`'s own
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
    The new status. Must be one of the seven values
    :class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter.status`
    accepts.

Returns
-------
ReqDocument
    The updated document. Raises :class:`._paths.ReqNotFoundError` if
    no requirement has this id.

