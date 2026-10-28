# `biz.dfch.specmgr.txt.tools._cache`

Per-domain content-hash-validated read cache singleton for free-form text (feat-229-txt Phase 110).

1:1 port of ``vcr.tools._cache``'s shape for the ``txt`` domain -- see that
module's own docstring for the full circular-import rationale this module
also follows: ``txt.tools._io``'s ``load_by_id`` needs ``find_txt_path``
(from ``_paths.py``) to resolve an id to a path; with the cache wired in,
``_paths.py``'s ``find_txt_path`` needs a cache-backed ``read_fn`` to pass
to ``general.tools._doc_paths.find_doc_path_by_id`` -- and the only
cache-backed reader available is ``read_txt``. Pulling the cache singleton
and ``read_txt`` out into this standalone ``_cache.py`` module breaks the
``_io.py -> _paths.py -> _io.py`` cycle that would otherwise result: both
``_io.py`` and ``_paths.py`` depend *downward* on ``_cache.py``, and
``_cache.py`` depends on neither of them -- only on the generic
``general.tools._doc_cache.DocCache`` class and this domain's own
``txt.models.v1`` (TxtDocument/parse_txt).

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime -- the
same shape as ``_lock.py``'s per-id lock registry, just a single instance
here rather than one-per-id, since a domain only ever needs one cache. No
call site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below
(``read_txt``/``invalidate_txt_cache``/``reconcile_txt_cache``), and those
functions close over the module-level ``_cache`` singleton.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_txt_cache` exists purely so tests can clear every cached entry
in ``setUp``/``tearDown`` and never observe another test's cached state.
It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``txt`` domain.

## Functions

### `_parse(text: 'str') -> 'TxtDocument'`

Parse ``text`` into a :class:`TxtDocument` (the cache's own ``parse_fn``).

Receives the exact text :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.read`
already read (and hashed) for this same call -- this function must not
re-read the file itself (feat-107-doc-cache Phase 6, REQ-007: closes the
hash/parse TOCTOU race the previous two-independent-reads shape had).


### `invalidate_txt_cache(path: 'Path') -> 'None'`

Drop ``path``'s cached entry, if present.

Called by the generic ``delete`` tool's ``txt`` adapter immediately
after a successful ``unlink()`` (the adapter lands with the domain's
Phase 130 generic-tool registration), so a deleted document's
stale cache entry is never served.

Parameters
----------
path:
    The filesystem path whose cache entry to drop.


### `read_txt(path: 'Path') -> 'TxtDocument'`

Read and parse the free-form text document at ``path``, through the cache.

A file is only ever re-parsed when its on-disk content hash no longer
matches the hash recorded at the last read of ``path`` (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
re-raised cached failure) is returned without re-invoking
:func:`~biz.dfch.specmgr.txt.models.v1.parse_txt`.

Parameters
----------
path:
    The filesystem path to the free-form text ``.md`` file.

Returns
-------
TxtDocument
    The cached or freshly-parsed, validated document.


### `reconcile_txt_cache(live_paths: 'Iterable[Path]') -> 'None'`

Drop every cached entry whose path is not in ``live_paths``.

Called before any per-file work in both ``find_txt_path``'s scan (via
``general.tools._doc_paths.find_doc_path_by_id``'s ``reconcile_fn``
parameter) and ``list_txt``, so a file deleted outside specmgr's own
tooling does not leak in memory indefinitely.

Parameters
----------
live_paths:
    The current, live set of on-disk paths for the ``txt`` domain.


### `reset_txt_cache() -> 'None'`

Clear every cached entry.

Test-only: not for production use. See the module docstring's "Test
isolation" section.

