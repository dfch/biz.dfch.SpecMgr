# `biz.dfch.specmgr.adr.tools.list_adr`

``@mcp.tool()`` wrapper: list_adr (feat-13-list-paging Task 2.1).

Replaces the earlier ``specmgr://adr/list`` resource
(``adr.resources.adr_list``). Converted from a resource to a tool because
MCP resources cannot take arbitrary parameters (only URI-template path
segments), and ``max_results``/``offset`` paging needs exactly that -- the
same resource->tool reasoning already applied to ``get_req``
(ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
contract shared by every ``list_<domain>`` tool.

## Functions

### `list_adr(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[AdrSummary]'`

Return one page of one-line ADR summaries from the configured base directory.

A file that fails to parse (:class:`AdrParseError` or
``pydantic.ValidationError``) is silently skipped -- a single malformed
file must not break listing every other valid one (mirrors
``adr.tools._paths.find_adr_path``'s own skip-on-parse-failure rule).
The complete, skip-broken-file-filtered list is materialized first, then
paginated in memory, so the returned ``total`` always reflects the count
of parseable documents only, independent of paging.

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
PagedResult[AdrSummary]
    One entry per successfully-parsed ``*.md`` file within the
    requested page, in filename-sorted order. ``results`` is empty if
    the base directory does not exist, holds no ADRs, or ``offset`` is
    past the end of the full list.

