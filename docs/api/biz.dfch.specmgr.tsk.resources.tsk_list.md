# `biz.dfch.specmgr.tsk.resources.tsk_list`

Resource: specmgr://tsk/list (Task 3.10).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``req.resources.req_list``/``specmgr://req/list``.

## Functions

### `tsk_list() -> 'list[TskSummary]'`

Return a one-line summary of every task list in the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.tsk.models.v1.parse_tsk` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``tsk.tools._paths.find_tsk_path``'s own
skip-on-parse-failure rule).

Returns
-------
list[TskSummary]
    One entry per successfully-parsed ``*.md`` file, in filename-sorted
    order. Empty if the base directory does not exist or holds no
    task lists.

