# `biz.dfch.specmgr.dec.tools._cache`

Per-domain content-hash-validated read cache singleton for decisions (feat-107-doc-cache Phase 4).

1:1 port of ``req.tools._cache``'s shape (feat-107-doc-cache Phase 3, the
pilot domain) for the ``dec`` domain -- see that module's own docstring for
the full circular-import rationale this module also follows: ``dec.tools._io``'s
``load_by_id`` needs ``find_dec_path`` (from ``_paths.py``) to resolve an id to
a path; with the cache wired in, ``_paths.py``'s ``find_dec_path`` needs a
cache-backed ``read_fn`` to pass to
``general.tools._doc_paths.find_doc_path_by_id`` -- and the only cache-backed
reader available is ``read_dec``. Pulling the cache singleton and ``read_dec``
out into this standalone ``_cache.py`` module breaks the
``_io.py -> _paths.py -> _io.py`` cycle that would otherwise result: both
``_io.py`` and ``_paths.py`` depend *downward* on ``_cache.py``, and
``_cache.py`` depends on neither of them -- only on the generic
``general.tools._doc_cache.DocCache`` class and this domain's own
``dec.models.v1`` (DecDocument/parse_dec).

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime -- the
same shape as ``_lock.py``'s per-id lock registry, just a single instance
here rather than one-per-id, since a domain only ever needs one cache. No
call site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below
(``read_dec``/``invalidate_dec_cache``/``reconcile_dec_cache``), and those
functions close over the module-level ``_cache`` singleton.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_dec_cache` exists purely so tests can clear every cached entry
in ``setUp``/``tearDown`` and never observe another test's cached state.
It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``dec`` domain, and
``.specmgr/feat/feat-107-doc-cache/README.md`` for the feature plan this
implements (Phase 4, mechanically repeating Phase 3's ``req`` template).

## Functions

### `_parse(path: 'Path') -> 'DecDocument'`

Read and parse ``path``'s full text into a :class:`DecDocument` (the cache's own ``parse_fn``).


### `invalidate_dec_cache(path: 'Path') -> 'None'`

Drop ``path``'s cached entry, if present.

Called by the generic ``delete`` tool's ``dec`` adapter immediately
after a successful ``unlink()`` (REQ-004), so a deleted document's
stale cache entry is never served.

Parameters
----------
path:
    The filesystem path whose cache entry to drop.


### `read_dec(path: 'Path') -> 'DecDocument'`

Read and parse the decision at ``path``, through the cache.

A file is only ever re-parsed when its on-disk content hash no longer
matches the hash recorded at the last read of ``path`` (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
re-raised cached failure) is returned without re-invoking
:func:`~biz.dfch.specmgr.dec.models.v1.parse_dec`.

Parameters
----------
path:
    The filesystem path to the decision ``.md`` file.

Returns
-------
DecDocument
    The cached or freshly-parsed, validated document.


### `reconcile_dec_cache(live_paths: 'Iterable[Path]') -> 'None'`

Drop every cached entry whose path is not in ``live_paths`` (REQ-005).

Called before any per-file work in both ``find_dec_path``'s scan (via
``general.tools._doc_paths.find_doc_path_by_id``'s ``reconcile_fn``
parameter) and ``list_dec``, so a file deleted outside specmgr's own
tooling does not leak in memory indefinitely.

Parameters
----------
live_paths:
    The current, live set of on-disk paths for the ``dec`` domain.


### `reset_dec_cache() -> 'None'`

Clear every cached entry.

Test-only: not for production use. See the module docstring's "Test
isolation" section.

