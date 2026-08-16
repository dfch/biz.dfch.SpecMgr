# `biz.dfch.specmgr.uc.resources.uc_list`

Resource: specmgr://uc/list (Task 3.1.6).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``req.resources.req_list``/``specmgr://req/list``.

## Functions

### `uc_list() -> 'list[UcSummary]'`

Return a one-line summary of every use case in the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.uc.models.v2.parse_uc` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``uc.tools._paths.find_uc_path``'s own
skip-on-parse-failure rule).

Returns
-------
list[UcSummary]
    One entry per successfully-parsed ``*.md`` file, in filename-sorted
    order. Empty if the base directory does not exist or holds no use
    cases.

