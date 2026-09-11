# `biz.dfch.specmgr.req.tools._cache`

Per-domain content-hash-validated read cache singleton for requirements (feat-107-doc-cache Phase 3).

**Why this is its own module, not folded into ``_io.py``/``_paths.py``
directly.** ``req.tools._io``'s ``load_by_id`` needs ``find_req_path``
(from ``_paths.py``) to resolve an id to a path. With the cache wired in,
``_paths.py``'s ``find_req_path`` needs a cache-backed ``read_fn`` to pass
to ``general.tools._doc_paths.find_doc_path_by_id`` -- and the only
cache-backed reader available is ``read_req``. If ``read_req`` stayed
defined in ``_io.py`` (as it was before this cache was wired in),
``_paths.py`` would have to import it from there, but ``_io.py`` already
imports ``find_req_path`` from ``_paths.py`` -- a straight circular import
(``_io.py -> _paths.py -> _io.py``). Pulling the cache singleton and
``read_req`` out into this new, standalone ``_cache.py`` module breaks the
cycle: both ``_io.py`` and ``_paths.py`` now depend *downward* on
``_cache.py``, and ``_cache.py`` depends on neither of them -- only on the
generic ``general.tools._doc_cache.DocCache`` class and this domain's own
``req.models.v1`` (``ReqDocument``/``parse_req``).

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime -- the
same shape as ``_lock.py``'s per-id lock registry, just a single instance
here rather than one-per-id, since a domain only ever needs one cache. No
call site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below
(``read_req``/``invalidate_req_cache``/``reconcile_req_cache``), and those
functions close over the module-level ``_cache`` singleton.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_req_cache` exists purely so tests can clear every cached entry
in ``setUp``/``tearDown`` and never observe another test's cached state.
It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``req`` domain, and
``.specmgr/feat/feat-107-doc-cache/README.md`` for the feature plan this
implements (Phase 3, the pilot domain -- this module's shape is the
template Phase 4 repeats for every other generic whole-body domain).

## Functions

### `_parse(text: 'str') -> 'ReqDocument'`

Parse ``text`` into a :class:`ReqDocument` (the cache's own ``parse_fn`` -- Phase 6: text in, not ``Path``).

Receives the exact text :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.read`
already read (and hashed) for this same call -- this function must not
re-read the file itself (feat-107-doc-cache Phase 6, REQ-007: closes the
hash/parse TOCTOU race the previous two-independent-reads shape had).


### `invalidate_req_cache(path: 'Path') -> 'None'`

Drop ``path``'s cached entry, if present.

Called by the generic ``delete`` tool's ``req`` adapter immediately
after a successful ``unlink()`` (REQ-004), so a deleted document's
stale cache entry is never served.

Parameters
----------
path:
    The filesystem path whose cache entry to drop.


### `read_req(path: 'Path') -> 'ReqDocument'`

Read and parse the requirement at ``path``, through the cache.

A file is only ever re-parsed when its on-disk content hash no longer
matches the hash recorded at the last read of ``path`` (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
re-raised cached failure) is returned without re-invoking
:func:`~biz.dfch.specmgr.req.models.v1.parse_req`.

Parameters
----------
path:
    The filesystem path to the requirement ``.md`` file.

Returns
-------
ReqDocument
    The cached or freshly-parsed, validated document.


### `reconcile_req_cache(live_paths: 'Iterable[Path]') -> 'None'`

Drop every cached entry whose path is not in ``live_paths`` (REQ-005).

Called before any per-file work in both ``find_req_path``'s scan (via
``general.tools._doc_paths.find_doc_path_by_id``'s ``reconcile_fn``
parameter) and ``list_req``, so a file deleted outside specmgr's own
tooling does not leak in memory indefinitely.

Parameters
----------
live_paths:
    The current, live set of on-disk paths for the ``req`` domain.


### `reset_req_cache() -> 'None'`

Clear every cached entry.

Test-only: not for production use. See the module docstring's "Test
isolation" section.

