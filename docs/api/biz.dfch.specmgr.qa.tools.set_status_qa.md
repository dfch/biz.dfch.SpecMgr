# `biz.dfch.specmgr.qa.tools.set_status_qa`

``@mcp.tool()`` wrapper: set_status_qa (Phase 4, Task 4.1).

The only path that changes a QA document's ``status`` -- mirrors
``adr.tools.set_status``/``req.tools.set_status_req``, minus the
``superseded_by``-composition special case:
:class:`~biz.dfch.specmgr.qa.models.v2.QaFrontmatter.status` has no
``"superseded by ..."`` pattern, just the closed four-value set (reused
from TSK) -- ``draft``/``active``/``done``/``cancelled``. Neither
``create_qa`` nor the generic ``update`` tool in ``general.tools`` accepts
a ``status`` argument at all -- this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.qa.models.v2.QaDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``qa_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `set_status_qa(id: 'str', status: 'str') -> 'QaDocument'`

Replace the status of the Question and Answer (QA) document identified by ``id``.

Reconstructs the frontmatter via :class:`QaFrontmatter`'s own
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
    The new status. Must be one of the four values
    :class:`~biz.dfch.specmgr.qa.models.v2.QaFrontmatter.status`
    accepts (``draft``/``active``/``done``/``cancelled``).

Returns
-------
QaDocument
    The updated document. Raises :class:`._paths.QaNotFoundError` if
    no QA document has this id.

