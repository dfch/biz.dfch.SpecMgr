# `biz.dfch.specmgr.tsk.tools.set_status_tsk`

``@mcp.tool()`` wrapper: set_status_tsk (Task 3.5).

The only path that changes a task list's ``status`` -- mirrors
``req.tools.set_status_req``:
:class:`~biz.dfch.specmgr.tsk.models.v1.TskFrontmatter.status` has a closed
four-value set (``draft``/``active``/``done``/``cancelled``), a small,
purpose-fit set matching how a task list is actually used (start it, work
it, finish it, or drop it) rather than REQ's larger, ADR-like set. Neither
``create_tsk`` nor the generic ``update`` tool in ``general.tools`` accepts
a ``status`` argument at all -- this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``tsk_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_tsk(id: 'str', status: 'str') -> 'TskDocument'`

Replace the status of the task list identified by ``id``.

Reconstructs the frontmatter via :class:`TskFrontmatter`'s own
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
    The new status. Must be one of ``"draft"``, ``"active"``,
    ``"done"``, ``"cancelled"`` --
    :class:`~biz.dfch.specmgr.tsk.models.v1.TskFrontmatter.status`'s
    four accepted values.

Returns
-------
TskDocument
    The updated document. Raises :class:`._paths.TskNotFoundError` if
    no task list has this id.

