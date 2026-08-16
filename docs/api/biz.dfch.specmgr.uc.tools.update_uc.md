# `biz.dfch.specmgr.uc.tools.update_uc`

``@mcp.tool()`` wrapper: update_uc (Task 3.1.5).

Same body-only ``content`` shape as ``create_uc``, but against an *existing*
document: ``id``/``type``/``status``/``created``/``version`` are all read
back from the file currently on disk and preserved unchanged; only
``updated`` is bumped to the current timestamp. ``status`` is never settable
here -- see the dedicated ``set_status_uc`` tool. Mirrors
``req.tools.update_req``.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.uc.models.v2.UcDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``uc_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `update_uc(id: 'str', content: 'str') -> 'UcDocument'`

Replace the body of the use case identified by ``id``.

``content`` is body markdown only, same shape as :func:`.create_uc.create_uc`
-- it must not carry a YAML frontmatter block. Validated the same way:
``UseCase.from_text(format_text(content))``, letting ``AssertionError``
(structural failure) or ``pydantic.ValidationError`` (field/cross-field
failure) propagate uncaught, with nothing written in either case.

The existing file is read first (under ``uc_lock(id)``) to resolve its
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
UcDocument
    The updated document. Raises :class:`._paths.UcNotFoundError` if
    no use case has this id.

