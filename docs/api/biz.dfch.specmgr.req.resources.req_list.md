# `biz.dfch.specmgr.req.resources.req_list`

Resource: specmgr://req/list (Task 3.18).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``adr.resources.adr_list``/``specmgr://adr/list``. Deliberately unfiltered
-- characteristics/tags filtering (ACC-002) was explicitly deferred during
Task 3.9's design discussion.

## Functions

### `req_list() -> 'list[ReqSummary]'`

Return a one-line summary of every requirement in the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.req.models.v1.parse_req` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``req.tools._paths.find_req_path``'s own
skip-on-parse-failure rule).

Returns
-------
list[ReqSummary]
    One entry per successfully-parsed ``*.md`` file, in filename-sorted
    order. Empty if the base directory does not exist or holds no
    requirements.

