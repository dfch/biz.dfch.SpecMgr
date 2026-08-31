# `biz.dfch.specmgr.feat.tools.list_feat`

``@mcp.tool()`` wrapper: list_feat (Task 2.3).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). Mirrors ``dec.tools.list_dec``'s
overall shape, with two feat-only differences: (1) it scans
``<base>/*/README.md`` via :func:`~biz.dfch.specmgr.feat.tools._paths.iter_feat_paths`,
not ``<base>/*.md``; (2) each :class:`~biz.dfch.specmgr.feat.models.v1.FeatSummary`
also carries the real filesystem ``path`` (REQ-004's Addressing section) and
uses ``ref = path.parent.name`` (the containing folder's own name, which by
convention already equals ``id`` for a healthy document) rather than
``path.stem`` (which would just be the fixed, uninformative ``"README"``).

## Functions

### `list_feat(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[FeatSummary]'`

Return one page of one-line feature summaries from the configured base directory.

A folder whose ``README.md`` fails to parse (``AssertionError`` or
``pydantic.ValidationError`` -- the same two error channels
:func:`~biz.dfch.specmgr.feat.models.v1.parse_feat` raises) is silently
skipped -- a single malformed document must not break listing every
other valid one. This includes every one of the 17 pre-existing,
hand-authored feature folders that predate this schema (out of scope
for this feature, see its own README's Scope section) -- they are
simply invisible to this tool until migrated. The complete,
skip-broken-folder-filtered list is materialized first, then paginated
in memory, so the returned ``total`` always reflects the count of
parseable documents only, independent of paging.

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
PagedResult[FeatSummary]
    One entry per successfully-parsed ``README.md`` file within the
    requested page, in folder-name-sorted order. ``results`` is empty
    if the base directory does not exist, holds no parseable feature
    documents, or ``offset`` is past the end of the full list.

