# `biz.dfch.specmgr.tsk.tools.update_tsk`

``@mcp.tool()`` wrapper: update_tsk (Task 3.4).

Same body-only ``content`` shape as ``create_tsk``, but against an
*existing* document: ``id``/``type``/``status``/``created``/``version`` are
all read back from the file currently on disk and preserved unchanged; only
``updated`` is bumped to the current timestamp. ``status`` is never settable
here -- see the dedicated ``set_status_tsk`` tool. Mirrors ``req.tools.update_req``
exactly.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``tsk_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.

## Functions

### `update_tsk(id: 'str', content: 'str') -> 'TskDocument'`

Replace the body of the task list identified by ``id``.

``content`` is body markdown only, same shape as :func:`.create_tsk.create_tsk`
-- it must not carry a YAML frontmatter block. Validated the same way:
``Task.from_text(format_text(content))``, letting ``AssertionError``
(structural failure) or ``pydantic.ValidationError`` (field/cross-field
failure) propagate uncaught, with nothing written in either case. In
particular, a whole-body replace that drops the last remaining
``## Recent Updates`` entry fails validation the same way
(``RecentUpdates.updates`` requires ``min_length=1``) -- carry forward at
least one entry, appending a new one rather than removing every existing
one.

The existing file is read first (under ``tsk_lock(id)``) to resolve its
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
TskDocument
    The updated document. Raises :class:`._paths.TskNotFoundError` if
    no task list has this id.

