# `biz.dfch.specmgr.sysrs.tools.list_sysrs`

``@mcp.tool()`` wrapper: list_sysrs (Task 3.2).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13: "Expose ``list_<domain>`` as a paged
MCP tool, not a resource") -- like GOL/DEC/SOP/VCR (domains built after that
ADR was accepted), SYSRS must not repeat the resource-then-convert history
of REQ/UC/TSK/QA/PRB (launched as a ``specmgr://<domain>/list`` resource,
converted later in feat-13-list-paging). See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging contract
shared by every ``list_<domain>`` tool.

## Functions

### `list_sysrs(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[SysrsSummary]'`

Return one page of one-line System Requirements Specification summaries from the configured base directory.

A file that fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.sysrs.models.v1.parse_sysrs` raises) is silently
skipped -- a single malformed file must not break listing every other
valid one (mirrors ``sysrs.tools._paths.find_sysrs_path``'s own
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
PagedResult[SysrsSummary]
    One entry per successfully-parsed ``*.md`` file within the
    requested page, in filename-sorted order. ``results`` is empty if
    the base directory does not exist, holds no System Requirements
    Specifications, or ``offset`` is past the end of the full list.

