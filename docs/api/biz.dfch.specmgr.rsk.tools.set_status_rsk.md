# `biz.dfch.specmgr.rsk.tools.set_status_rsk`

``@mcp.tool()`` wrapper: set_status_rsk (Task 3.5).

The only path that changes a risk's ``status`` -- mirrors
``tsk.tools.set_status_tsk``:
:class:`~biz.dfch.specmgr.rsk.models.v1.RskFrontmatter.status` has a closed
six-value set (``open``/``mitigating``/``accepted``/``occurred``/``closed``/
``dropped``), a purpose-fit risk lifecycle (identified/monitored, treatment
in progress, residual risk accepted, event materialized, resolved/expired,
or dropped from the register) rather than reusing REQ's larger, ADR-like
set. Neither ``create_rsk`` nor the generic ``update`` tool in
``general.tools`` accepts a ``status`` argument at all -- this is the sole
entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``rsk_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_rsk(id: 'str', status: 'str') -> 'RskDocument'`

Replace the status of the risk identified by ``id``.

Reconstructs the frontmatter via :class:`RskFrontmatter`'s own
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
    The new status. Must be one of ``"open"``, ``"mitigating"``,
    ``"accepted"``, ``"occurred"``, ``"closed"``, ``"dropped"`` --
    :class:`~biz.dfch.specmgr.rsk.models.v1.RskFrontmatter.status`'s
    six accepted values.

Returns
-------
RskDocument
    The updated document. Raises :class:`._paths.RskNotFoundError` if
    no risk has this id.

