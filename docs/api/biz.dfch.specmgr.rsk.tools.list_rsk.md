# `biz.dfch.specmgr.rsk.tools.list_rsk`

``@mcp.tool()`` wrapper: list_rsk (Task 3.14).

Per feat-13 / ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, listing is a paged
``@mcp.tool()`` rather than a ``specmgr://rsk/list`` resource: MCP resources
cannot take arbitrary parameters (only URI-template path segments), and
``max_results``/``offset`` paging needs exactly that -- the same resource->
tool reasoning already applied to ``get_req`` (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614) and ``list_tsk``. Mirrors
``tsk.tools.list_tsk`` line-for-line in mechanism, with one deliberate
difference: each summary line is built by
:meth:`~biz.dfch.specmgr.rsk.models.v1.RskSummary.from_document` (a
model-layer factory) instead of inline construction, because ``RskSummary``
carries six risk-specific derived fields (the zone levels, the TARA word,
the first ``## Scope`` entry, and the residual-risk coordinates) that the
factory derives from the parsed assessments in one place -- see the feature
README's Decisions Made.

## Functions

### `list_rsk(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[RskSummary]'`

Return one page of one-line risk summaries from the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.rsk.models.v1.parse_rsk` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``rsk.tools._paths.find_rsk_path``'s own
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
PagedResult[RskSummary]
    One entry per successfully-parsed ``*.md`` file within the
    requested page, in filename-sorted order. ``results`` is empty if
    the base directory does not exist, holds no risks, or ``offset`` is
    past the end of the full list.

