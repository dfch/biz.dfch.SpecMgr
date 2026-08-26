# `biz.dfch.specmgr.rsk.tools.update_rsk`

``@mcp.tool()`` wrapper: update_rsk (Task 3.4).

Same body-only ``content`` shape as ``create_rsk``, but against an
*existing* document: ``id``/``type``/``status``/``created``/``version`` are
all read back from the file currently on disk and preserved unchanged; only
``updated`` is bumped to the current timestamp. ``status`` is never settable
here -- see the dedicated ``set_status_rsk`` tool. Mirrors
``tsk.tools.update_tsk`` exactly.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``rsk_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `update_rsk(id: 'str', content: 'str') -> 'RskDocument'`

Replace the body of the risk identified by ``id``.

``content`` is body markdown only, same shape as :func:`.create_rsk.create_rsk`
-- it must not carry a YAML frontmatter block. Validated the same way:
``Risk.from_text(format_text(content))``, letting ``AssertionError``
(structural failure) or ``pydantic.ValidationError`` (field/cross-field
failure) propagate uncaught, with nothing written in either case.

The existing file is read first (under ``rsk_lock(id)``) to resolve its
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
RskDocument
    The updated document. Raises :class:`._paths.RskNotFoundError` if
    no risk has this id.

