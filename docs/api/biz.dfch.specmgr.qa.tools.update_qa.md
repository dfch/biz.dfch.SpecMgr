# `biz.dfch.specmgr.qa.tools.update_qa`

``@mcp.tool()`` wrapper: update_qa (Phase 4, Task 4.1).

Same body-only ``content`` shape as ``create_qa``, but against an
*existing* document: ``id``/``type``/``status``/``created``/``version`` are
all read back from the file currently on disk and preserved unchanged; only
``updated`` is bumped to the current timestamp. ``status`` is never
settable here -- see the dedicated ``set_status_qa`` tool. 1:1 port of
``req.tools.update_req``.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.qa.models.v2.QaDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``qa_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update (mirrors every ADR/REQ mutation
tool's own lock usage).

## Functions

### `update_qa(id: 'str', content: 'str') -> 'QaDocument'`

Replace the body of the Question and Answer (QA) document identified by ``id``.

``content`` is body markdown only, same shape as :func:`.create_qa.create_qa`
-- it must not carry a YAML frontmatter block. Validated the same way:
``Qa.from_text(format_text(content))``, letting ``AssertionError``
(structural failure) or ``pydantic.ValidationError`` (field/cross-field
failure) propagate uncaught, with nothing written in either case.

The existing file is read first (under ``qa_lock(id)``) to resolve its
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
QaDocument
    The updated document. Raises :class:`._paths.QaNotFoundError` if
    no QA document has this id.

