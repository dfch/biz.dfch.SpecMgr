# `biz.dfch.specmgr.prb.tools.set_status_prb`

``@mcp.tool()`` wrapper: set_status_prb (Task 3.5).

The only path that changes a problem statement's ``status`` -- mirrors
``tsk.tools.set_status_tsk``/``qa.tools.set_status_qa``:
:class:`~biz.dfch.specmgr.prb.models.v1.PrbFrontmatter.status` has a closed
four-value set (``draft``/``active``/``resolved``/``cancelled``). Neither
``create_prb`` nor the generic ``update`` tool in ``general.tools`` accepts
a ``status`` argument at all -- this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.prb.models.v1.PrbDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``prb_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_prb(id: 'str', status: 'str') -> 'PrbDocument'`

Replace the status of the problem statement identified by ``id``.

Reconstructs the frontmatter via :class:`PrbFrontmatter`'s own
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
    ``"resolved"``, ``"cancelled"`` --
    :class:`~biz.dfch.specmgr.prb.models.v1.PrbFrontmatter.status`'s
    four accepted values.

Returns
-------
PrbDocument
    The updated document. Raises :class:`._paths.PrbNotFoundError` if
    no problem statement has this id.

