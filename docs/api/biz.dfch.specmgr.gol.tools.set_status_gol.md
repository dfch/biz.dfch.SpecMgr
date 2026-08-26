# `biz.dfch.specmgr.gol.tools.set_status_gol`

``@mcp.tool()`` wrapper: set_status_gol (Task 3.5).

The only path that changes a goal's ``status`` -- mirrors
``prb.tools.set_status_prb``/``req.tools.set_status_req``:
:class:`~biz.dfch.specmgr.gol.models.v1.GolFrontmatter.status` has no
``"superseded by ..."`` pattern, just the closed seven-value set
(``draft``/``proposed``/``accepted``/``superseded``/``deprecated``/
``rejected``/``implemented`` -- REQ's exact set, with goal-specific meanings
for ``implemented`` = the goal has genuinely been reached and
``superseded`` = replaced by another goal). Neither ``create_gol`` nor
``update_gol`` accept a ``status`` argument at all -- this is the sole entry
point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.gol.models.v1.GolDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``gol_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_gol(id: 'str', status: 'str') -> 'GolDocument'`

Replace the status of the goal identified by ``id``.

Reconstructs the frontmatter via :class:`GolFrontmatter`'s own
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
    ``"accepted"``, ``"superseded"``, ``"deprecated"``, ``"rejected"``,
    ``"implemented"`` --
    :class:`~biz.dfch.specmgr.gol.models.v1.GolFrontmatter.status`'s
    seven accepted values.

Returns
-------
GolDocument
    The updated document. Raises :class:`._paths.GolNotFoundError` if
    no goal has this id.

