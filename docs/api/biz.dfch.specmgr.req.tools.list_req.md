# `biz.dfch.specmgr.req.tools.list_req`

``@mcp.tool()`` wrapper: list_req (feat-13-list-paging Task 2.2).

Replaces the earlier ``specmgr://req/list`` resource
(``req.resources.req_list``). Converted from a resource to a tool because
MCP resources cannot take arbitrary parameters (only URI-template path
segments), and ``max_results``/``offset`` paging needs exactly that -- the
same resource->tool reasoning already applied to ``get_req``
(ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Deliberately unfiltered --
characteristics/tags filtering (feat-7 Task 0.16) was explicitly deferred
during Task 3.9's design discussion and stays out of scope here too. See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
contract shared by every ``list_<domain>`` tool.

## Functions

### `list_req(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[ReqSummary]'`

Return one page of one-line requirement summaries from the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.req.models.v1.parse_req` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``req.tools._paths.find_req_path``'s own
skip-on-parse-failure rule). The complete, skip-broken-file-filtered
list is materialized first, then paginated in memory, so the returned
``total`` always reflects the count of parseable documents only,
independent of paging.

Parameters
----------
max_results:
    Maximum number of summaries to return in this page. Defaults to
    ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);
    otherwise clamped into range (see
    :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
offset:
    Zero-based index of the first summary to include in this page.
    Defaults to ``0`` when not given (``None``); negative values are
    floored to ``0``.

Returns
-------
PagedResult[ReqSummary]
    One entry per successfully-parsed ``*.md`` file within the
    requested page, in filename-sorted order. ``results`` is empty if
    the base directory does not exist, holds no requirements, or
    ``offset`` is past the end of the full list.

