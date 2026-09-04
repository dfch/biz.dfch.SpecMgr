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

feat-81-83-validation Phase 3 (REQ-006/REQ-007) routed this tool through
the shared ``general.tools._listing.build_summaries`` helper: a file that
fails to parse now appears inline in ``results`` as a failed entry (marker
``title``/``status``, ``ref``, ``path``, and ``error``) and contributes to
both ``total`` and the new ``error_count``, instead of being silently
skipped.

## Functions

### `_to_failed_summary(path: 'Path', error: 'Exception') -> 'SysrsSummary'`


### `_to_summary(doc: 'SysrsDocument', path: 'Path') -> 'SysrsSummary'`


### `list_sysrs(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[SysrsSummary]'`

Return one page of one-line System Requirements Specification summaries from the configured base directory.

A file that fails to parse (``AssertionError``, ``pydantic.ValidationError``,
or ``yaml.YAMLError`` -- the same channels
:func:`~biz.dfch.specmgr.sysrs.models.v1.parse_sysrs` raises) appears
inline in ``results`` as its own failed entry (``id=None``,
``title``/``status`` both the fixed marker ``"<failed to parse>"``,
``ref``/``path`` populated the same way as a successful entry, and
``error`` carrying the exception's message) rather than being silently
skipped (feat-81-83-validation Phase 3, REQ-006) -- a single malformed
file must not break listing every other valid one. The complete list
(successes and failures both) is materialized first, then paginated in
memory, so the returned ``total``/``error_count`` always reflect the
whole directory, independent of paging.

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
    One entry per ``*.md`` file within the requested page (successes
    and failures both), in filename-sorted order. ``results`` is empty
    if the base directory does not exist, holds no System Requirements
    Specifications, or ``offset`` is past the end of the full list.

