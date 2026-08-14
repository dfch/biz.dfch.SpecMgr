# `biz.dfch.specmgr.req.tools.update_req`

``@mcp.tool()`` wrapper: update_req (Task 3.13).

Same body-only ``content`` shape as ``create_req`` (Task 3.12), but against
an *existing* document: ``id``/``type``/``status``/``created``/``version``
are all read back from the file currently on disk and preserved unchanged;
only ``updated`` is bumped to the current timestamp. ``status`` is never
settable here -- see the dedicated ``set_status_req`` tool (Task 3.14).

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``req_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update (mirrors every ADR mutation
tool's own ``adr_lock`` usage).

## Functions

### `update_req(id: 'str', content: 'str') -> 'ReqDocument'`

Replace the body of the requirement identified by ``id``.

``content`` is body markdown only, same shape as :func:`.create_req.create_req`
-- it must not carry a YAML frontmatter block. Validated the same way:
``Requirement.from_text(format_text(content))``, letting ``AssertionError``
(structural failure) or ``pydantic.ValidationError`` (field/cross-field
failure) propagate uncaught, with nothing written in either case.

The existing file is read first (under ``req_lock(id)``) to resolve its
path and current frontmatter; every frontmatter field except ``updated``
is carried over unchanged -- ``status`` in particular is never settable
through this tool.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
content:
    The replacement body markdown, with no frontmatter block.

Returns
-------
ReqDocument
    The updated document. Raises :class:`._paths.ReqNotFoundError` if
    no requirement has this id.

