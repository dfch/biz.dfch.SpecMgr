# `biz.dfch.specmgr.qa.tools.list_qa`

``@mcp.tool()`` wrapper: list_qa (feat-13-list-paging Task 2.5).

Replaces the earlier ``specmgr://qa/list`` resource (``qa.resources.qa_list``).
Converted from a resource to a tool because MCP resources cannot take
arbitrary parameters (only URI-template path segments), and
``max_results``/``offset`` paging needs exactly that -- the same
resource->tool reasoning already applied to ``get_req``
(ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Deliberately unfiltered --
characteristics/tags filtering was explicitly deferred for REQ's own
equivalent, and the same deferral applies here. See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
contract shared by every ``list_<domain>`` tool.

## Functions

### `list_qa(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[QaSummary]'`

Return one page of one-line QA document summaries from the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.qa.models.v1.parse_qa` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``qa.tools._paths.find_qa_path``'s own
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
PagedResult[QaSummary]
    One entry per successfully-parsed ``*.md`` file within the
    requested page, in filename-sorted order. ``results`` is empty if
    the base directory does not exist, holds no QA documents, or
    ``offset`` is past the end of the full list.

