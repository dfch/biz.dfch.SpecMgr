# `biz.dfch.specmgr.general.tools._paging`

Generic, doc-type-agnostic paging helpers (feat-13 Task 1.2).

Mirrors ``general.tools._doc_paths``'s shape: a single module shared across
every ``list_<domain>`` MCP tool (Phase 2 of
``.specmgr/feat/feat-13-list-paging/README.md``) instead of a copy per
domain. As with ``_doc_paths.py``, this module has no ``mcp`` import
dependency -- it is plain Python plus :class:`~biz.dfch.specmgr.general.
models.paged_result.PagedResult`.

**Full materialize, then slice.** :func:`paginate` takes the complete,
already-materialized item list (e.g. every parseable document summary for a
domain, skip-broken-file semantics already applied by the caller) and slices
it in memory; it never re-scans a directory itself. This keeps ``total``
accurate (a count of *parseable* documents) and keeps behavior identical to
each domain's pre-pagination full-scan, at the cost of a streaming/early-stop
optimization that is explicitly out of scope (see the feature's Design
Notes).

## Functions

### `normalize_paging(max_results: 'int | None', offset: 'int | None') -> 'tuple[int, int]'`

Clamp/floor caller-supplied paging inputs into safe bounds.

``max_results`` defaults to :data:`DEFAULT_MAX_RESULTS` when not given
(``None``), and is otherwise clamped into
``[``:data:`MIN_MAX_RESULTS`\ ``, ``:data:`MAX_MAX_RESULTS`\ ``]``
(e.g. a caller-supplied ``500`` becomes :data:`MAX_MAX_RESULTS`, a
caller-supplied ``0`` becomes :data:`MIN_MAX_RESULTS`). ``offset``
defaults to :data:`MIN_OFFSET` when not given, and is otherwise floored
to :data:`MIN_OFFSET` (never negative).

Parameters
----------
max_results:
    The caller-requested page size, or ``None`` if not given.
offset:
    The caller-requested start index, or ``None`` if not given.

Returns
-------
tuple[int, int]
    ``(offset, max_results)`` -- in that order, so callers can pass this
    straight into :func:`paginate` as
    ``paginate(items, *normalize_paging(max_results, offset))``.


### `paginate(items: 'list[_ItemT]', offset: 'int', max_results: 'int') -> 'PagedResult[_ItemT]'`

Slice a fully materialized item list into one page, plus paging metadata.

Parameters
----------
items:
    The complete, already-materialized list of items (e.g. every
    parsed document summary for a domain). Callers should normalize
    ``offset``/``max_results`` via :func:`normalize_paging` first.
offset:
    Zero-based start index into ``items``. Must be non-negative.
max_results:
    Maximum number of items to include in the returned page. Must be at
    least :data:`MIN_MAX_RESULTS`.

Returns
-------
PagedResult[_ItemT]
    ``total`` is ``len(items)``; ``results`` is
    ``items[offset : offset + max_results]``; ``truncated`` is ``True``
    iff further items exist beyond this page.

