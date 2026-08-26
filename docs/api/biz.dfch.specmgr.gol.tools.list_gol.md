# `biz.dfch.specmgr.gol.tools.list_gol`

``@mcp.tool()`` wrapper: list_gol (Task 3.9).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13: "Expose ``list_<domain>`` as a paged
MCP tool, not a resource") -- unlike REQ/UC/TSK/QA/PRB (which launched as a
``specmgr://<domain>/list`` resource and were converted later in
feat-13-list-paging), GOL is a new domain built after that ADR was accepted,
so it must not repeat that resource-then-convert history. See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging contract
shared by every ``list_<domain>`` tool.

## Functions

### `list_gol(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[GolSummary]'`

Return one page of one-line goal summaries from the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.gol.models.v1.parse_gol` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``gol.tools._paths.find_gol_path``'s own
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
PagedResult[GolSummary]
    One entry per successfully-parsed ``*.md`` file within the
    requested page, in filename-sorted order. ``results`` is empty if
    the base directory does not exist, holds no goals, or ``offset`` is
    past the end of the full list.

