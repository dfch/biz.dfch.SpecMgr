# `biz.dfch.specmgr.feat.tools._cache`

Per-domain content-hash-validated read cache singleton for features (feat-107-doc-cache Phase 4, Task 4.1a).

``feat`` is the one domain whose cache integration is necessarily bespoke
(the feature plan's own Design Notes, and ADR bfd76370-b59b-4d65-b550-a969f6c93c9d):
``feat.tools._paths``/``feat.tools.set_feat_id`` never route through the
shared ``general.tools._doc_paths`` module the other eleven whole-body
domains' ``_cache.py`` modules plug into (Phase 4's mechanical rollout) --
``feat`` is folder-per-document (``<base>/<id>/README.md``) and its own
``find_feat_path_by_id`` shortcuts directly to that path instead of scanning
and comparing parsed ids. This module still follows the other eleven
domains' *shape* as closely as that difference allows: a module-level
:class:`DocCache` singleton (mirroring ``_lock.py``'s ``_locks`` registry),
``read_feat``/``invalidate_feat_cache``/``reconcile_feat_cache``/
``reset_feat_cache`` -- plus one function unique to this domain,
:func:`move_feat_cache_entry`, wrapping :meth:`DocCache.move` for
``set_feat_id``'s rename case (no other domain in this codebase ever
renames a document's own on-disk path in place; every other rename-shaped
operation is actually a delete+create instead).

**Why this is its own module, not folded into ``_io.py``/``_paths.py``
directly.** Same circular-import rationale as every other domain's own
``_cache.py`` (see e.g. ``req.tools._cache``'s module docstring): ``_io.py``
imports ``find_feat_path_by_id`` from ``_paths.py``; with the cache wired
in, ``_paths.py``'s ``find_feat_path_by_id`` needs a cache-backed
``read_feat`` to avoid re-parsing the same file twice per ``get_feat`` call
(the same double-parse bug ADR bfd76370-b59b-4d65-b550-a969f6c93c9d fixes
for every other domain) -- and the only cache-backed reader available is
``read_feat``. Pulling the cache singleton and ``read_feat`` out into this
standalone ``_cache.py`` module breaks the ``_io.py -> _paths.py -> _io.py``
cycle that would otherwise result.

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime. No call
site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_feat_cache` exists purely so tests can clear every cached
entry in ``setUp``/``tearDown`` and never observe another test's cached
state. It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``feat`` domain, and
``.specmgr/feat/feat-107-doc-cache/README.md`` for the feature plan this
implements (Phase 4, Task 4.1a).

## Functions

### `_parse(path: 'Path') -> 'FeatDocument'`

Read and parse ``path``'s full text into a :class:`FeatDocument` (the cache's own ``parse_fn``).


### `invalidate_feat_cache(path: 'Path') -> 'None'`

Drop ``path``'s cached entry, if present.

Called by the generic ``delete`` tool's ``feat`` adapter immediately
after a successful ``shutil.rmtree(folder)`` (REQ-004), so a deleted
document's stale cache entry is never served. ``path`` is the cached
``README.md`` file path (the cache's own key), not the containing
folder ``rmtree`` actually removed.

Parameters
----------
path:
    The filesystem path whose cache entry to drop (the feature's
    ``README.md`` file, not its containing folder).


### `move_feat_cache_entry(old_path: 'Path', new_path: 'Path') -> 'None'`

Relocate ``old_path``'s cache entry (if present) to ``new_path``.

Called by ``set_feat_id`` as the *last* step, only after
``write_feat_file(new_path, ...)`` has already succeeded -- never at the
earlier ``old_path.parent.rename(new_path.parent)`` step -- so a failure
between the rename and the write never leaves a cache entry addressing
a file that was never actually written (REQ-004). Thin wrapper over
:meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.move`.

Parameters
----------
old_path:
    The feature's previous ``README.md`` path (the cache's old key).
new_path:
    The feature's new ``README.md`` path (the cache's new key).


### `read_feat(path: 'Path') -> 'FeatDocument'`

Read and parse the feature document at ``path``, through the cache.

A file is only ever re-parsed when its on-disk content hash no longer
matches the hash recorded at the last read of ``path`` (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
re-raised cached failure) is returned without re-invoking
:func:`~biz.dfch.specmgr.feat.models.v1.parse_feat`.

Parameters
----------
path:
    The filesystem path to the feature's ``README.md`` file.

Returns
-------
FeatDocument
    The cached or freshly-parsed, validated document.


### `reconcile_feat_cache(live_paths: 'Iterable[Path]') -> 'None'`

Drop every cached entry whose path is not in ``live_paths`` (REQ-005).

Called before any per-file work in ``list_feat`` (there is no directory
scan in ``find_feat_path_by_id`` itself to reconcile against -- see this
domain's own ``_paths.py`` docstring for why: the shortcut-only lookup
never scans), so a folder deleted outside specmgr's own tooling does
not leak in memory indefinitely.

Parameters
----------
live_paths:
    The current, live set of on-disk ``README.md`` paths for the
    ``feat`` domain.


### `reset_feat_cache() -> 'None'`

Clear every cached entry.

Test-only: not for production use. See the module docstring's "Test
isolation" section.

