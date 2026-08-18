# `biz.dfch.specmgr.qa.resources.qa_list`

Resource: specmgr://qa/list (Phase 4, Task 4.2).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``adr.resources.adr_list``/``req.resources.req_list``. Deliberately
unfiltered -- characteristics/tags filtering was explicitly deferred for
REQ's own equivalent, and the same deferral applies here.

## Functions

### `qa_list() -> 'list[QaSummary]'`

Return a one-line summary of every QA document in the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.qa.models.v1.parse_qa` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``qa.tools._paths.find_qa_path``'s own
skip-on-parse-failure rule).

Returns
-------
list[QaSummary]
    One entry per successfully-parsed ``*.md`` file, in filename-sorted
    order. Empty if the base directory does not exist or holds no QA
    documents.

