# `biz.dfch.specmgr.general.tools._embedding_cache`

Global, content-hash-validated in-memory embedding cache (feat-134, Phase 1, REQ-004).

Backs ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's **cache** sub-decision:
computed embeddings are cached in-memory, per process, content-hash
validated -- no on-disk persistence. A document's vector is only ever
recomputed when its on-disk content actually changed.

**One global instance, keyed by ``(domain, resolved path)``.** Unlike
feat-107's :class:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache`
(one instance per domain, keyed by path alone), a similarity search spans
every whole-body domain at once, so this is a single, standalone
module-level singleton whose keys carry the domain name alongside the
resolved path -- two different domains can hold documents at the same
resolved path (e.g. a ``SPECMGR_DOCS_DIR`` override pointing several
domains at one tree) without colliding.

**Content-hash validation guarantee.** Every :meth:`EmbeddingCache.read`
call re-reads ``path``'s full on-disk text and computes its
``hashlib.blake2b`` content hash exactly once per call, regardless of
hit/miss -- and hands that *same* text to the caller-supplied ``embed_fn``
on a miss (the DocCache Phase 6, REQ-007 TOCTOU closure: the exact text
that gets hashed is the exact text embedded, with zero intervening file
I/O, so the stored hash and the stored vector can never originate from
different on-disk snapshots of ``path``). When the computed hash matches
the hash stored for ``(domain, path)`` at its last read, the stored vector
is returned without re-embedding. A stale entry is structurally impossible
-- it can only ever cost one extra embed, never an incorrect result. This
refines, rather than violates, ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3's
"the filesystem is the sole source of truth" invariant, exactly as ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d did for parsing.

**Vectors are stored in the provider's native arrays.** A stored vector is
whatever :data:`~biz.dfch.specmgr.general.tools._embedding.Vector` the
``embed_fn`` returned -- the default provider's ``numpy.ndarray`` (float32),
never converted to a Python ``list[float]`` (~7x memory bloat). A cache hit
therefore returns the *same array object* the cache stores: callers must
treat vectors as read-only (the Phase 2/3 ranking logic only performs dot
products over them).

**Lock-ordering rule (mirrors DocCache, ADR bfd76370).** This cache's own
internal ``threading.Lock`` guards *only* its dict get/set/pop/clear
bookkeeping -- never the file read, never the caller-supplied ``embed_fn``
call itself (the expensive embedding computation), and never held across
any domain-level per-id lock. This cache's lock is always the *innermost*
lock acquired in any call stack: a caller holding a domain lock may acquire
this cache's lock, but this cache never acquires a domain lock itself, and
never holds its own lock across a call back into caller code that could
itself attempt to acquire another lock.

**Lifecycle wiring (Phase 3, Task 3.6 -- this module's own public surface is
complete now).** The generic ``delete`` tool's per-domain adapters call
:func:`invalidate_embedding_cache` immediately after a successful
``unlink``/``rmtree`` (a deleted document's stale vector must never be
served); ``set_feat_id`` calls :func:`move_embedding_cache` after its own
successful rename (the ``feat`` entry follows the document from the old
``README.md`` path to the new one; the moved entry's hash will then
mismatch the rewritten frontmatter on the next :meth:`read` -- a guaranteed,
harmless miss, the same self-healing ``DocCache.move`` documents).

**Dependency-light by construction.** This module imports only the
standard library (plus :mod:`._embedding`, which itself imports nothing
beyond the standard library and the base ``pydantic``-backed
``general.models``) -- no ``fastembed``, no ``numpy``. It is therefore
importable on a base/``mcp``-only install, where the similarity tools
register fine and simply return the structured unavailable result
(REQ-003) without ever touching this cache.

**Explicitly out of scope** (mirroring both ADRs): no TTL/size-based
eviction, no on-disk persistence, and no ``stat()``-based (mtime/size)
pre-check fast path -- content-hash-only for v1.

## Classes

### `EmbeddingCache`

A process-local, content-hash-validated in-memory embedding cache.

Shaped as ``dict[tuple[domain, resolved_path], tuple[content_hash,
vector]]`` (ADR 750842b2), where ``content_hash`` is the
``hashlib.blake2b`` digest of ``path``'s full on-disk text at the last
:meth:`read` and ``vector`` is the :data:`Vector` that read produced
(stored in the provider's native array type, unconverted). One
:class:`EmbeddingCache` instance exists per process -- the module-level
:data:`_cache` singleton below, created once at import time and reused
for the process's lifetime (mirroring ``_lock.py``'s per-id lock
registries); no call site threads an explicit cache instance through
function signatures.

**Every public method normalizes its ``Path`` argument(s) via
``.resolve()`` before touching the internal dict**, so two different
string forms of the same on-disk file (e.g. a relative path and its
resolved, absolute form) always address the *same* cache entry -- they
can never be independently tracked or independently invalidated.
Callers may still pass an unresolved ``Path`` in; normalization happens
internally and is invisible to them.

Not thread-hostile, but not a full cross-file synchronization primitive
either: the internal lock (``threading.Lock``) guards only this
instance's dict bookkeeping, so concurrent :meth:`read` calls for
*different* ``(domain, path)`` keys never block each other on that
bookkeeping. A concurrent cold-start race for the *same* key may still
invoke ``embed_fn`` more than once (allowed: embedding is idempotent
and the losing writer's vector is byte-identical to the winner's for
the same content hash -- worst case one extra compute, never a wrong
result); this class does not attempt to de-duplicate in-flight embeds.

**Methods:**

- `invalidate(self, domain: 'str', path: 'Path') -> 'None'`
  Drop ``(domain, path)``'s cache entry, if present.

  A no-op if the key has no cached entry.

  Args:
      domain:
          The document's domain name (see :meth:`read`).
      path:
          The filesystem path whose cache entry to drop. Normalized
          via ``.resolve()`` before use as the cache key.

- `move(self, domain: 'str', old_path: 'Path', new_path: 'Path') -> 'None'`
  Relocate ``(domain, old_path)``'s cache entry (if present) to ``(domain, new_path)``.

  For a rename case (``set_feat_id``'s only caller, Phase 3, Task
  3.6): a no-op if ``(domain, old_path)`` has no cached entry.
  Otherwise, moves the entry's stored ``(hash, vector)`` pair as-is,
  without re-validating it against ``new_path``'s actual on-disk
  content -- exactly ``DocCache.move``'s documented semantics:
  ``set_feat_id`` always rewrites the ``id``/``updated`` frontmatter
  before writing the new path, so the moved entry's stale hash
  mismatches on the very next :meth:`read` of ``new_path`` -- a
  guaranteed, harmless cache miss that recomputes and re-stores a
  correct, fresh entry, self-healing through the same hash-validation
  path every other :meth:`read` uses. The reason to call :meth:`move`
  at all, rather than simply :meth:`invalidate`-ing ``old_path`` and
  letting ``new_path`` start out as a plain miss, is solely to drop
  ``old_path``'s now-defunct entry as part of the same operation.

  Args:
      domain:
          The document's domain name (see :meth:`read`); ``move``
          keeps the domain unchanged (a rename never crosses domains).
      old_path:
          The cache entry's current key. Normalized via
          ``.resolve()`` before use.
      new_path:
          The cache entry's new key. Normalized via ``.resolve()``
          before use.

- `read(self, domain: 'str', path: 'Path', embed_fn: '_EmbedFn') -> 'Vector'`
  Return the cached or freshly-computed embedding vector for ``(domain, path)``.

  Reads ``path``'s full on-disk text and computes its content hash
  exactly once per call, regardless of hit/miss (mirroring DocCache
  Phase 6, REQ-007): that same text is both what gets hashed and, on a
  miss, what gets handed to ``embed_fn`` -- there is no second,
  independent file read between the two, so the stored hash and the
  stored vector can never originate from different on-disk snapshots
  of ``path``.

  When the computed hash matches the hash stored for ``(domain,
  path)`` at its last read, the stored vector is returned as-is (the
  same array object the cache holds -- see the module docstring's
  read-only-vectors rule) without invoking ``embed_fn`` again. On a
  hash mismatch or cache miss, ``embed_fn(text)`` is called fresh and
  the new ``(hash, vector)`` pair is stored before returning.

  Only the dict get/set around ``embed_fn`` is guarded by this
  instance's lock; the file read and the ``embed_fn`` call itself
  happen outside the lock, so a slow embed of one document never
  blocks a concurrent read of a different one (lock-ordering rule,
  ADR bfd76370).

  Args:
      domain:
          The document's domain name (one of the whole-body domains'
          ``type`` values, e.g. ``"req"``) -- part of the cache key,
          see the class docstring.
      path:
          The filesystem path to read and, if needed, embed.
          Normalized via ``.resolve()`` before use as the cache key;
          the text is read from ``path`` as given (resolving does not
          change which file is read, only which key addresses its
          entry).
      embed_fn:
          Computes the document's single :data:`Vector` from the given
          text on a cache miss (Phase 2/3's text extraction plus the
          provider's :meth:`~biz.dfch.specmgr.general.tools._embedding.
          EmbeddingProvider.embed`). Receives the *exact* text this
          call already read and hashed -- it must not re-read ``path``
          itself.

  Returns:
      The cached (same array object, on a hit) or freshly-computed
      vector for ``(domain, path)``.

  Raises:
      Exception:
          Any failure to read ``path`` (e.g. ``OSError``/
          ``FileNotFoundError``) or any ``embed_fn`` failure
          propagates uncaught and is never cached -- the entry for
          ``(domain, path)`` is simply absent (or still holds its
          previous, now-mismatched) state.

- `reset(self) -> 'None'`
  Clear every cached entry.

  Test-only: not for production use. Exists so tests do not leak
  cached entries across test cases within the same process, since
  this cache instance is a module-level singleton that persists for
  the whole test process's lifetime (same precedent as
  ``DocCache.reset`` and every domain's ``reset_<domain>_cache``).


## Functions

### `invalidate_embedding_cache(domain: 'str', path: 'Path') -> 'None'`

Drop ``(domain, path)``'s embedding-cache entry, if present.

Wired into the generic ``delete`` tool's per-domain adapters (Phase 3,
Task 3.6, REQ-008): called immediately after a successful
``unlink``/``rmtree``, so a deleted document's stale vector is never
served. A no-op if the key has no cached entry.

Args:
    domain:
        The deleted document's domain name.
    path:
        The deleted document's filesystem path (the ``README.md`` file
        path for ``feat``, whose whole folder was removed).


### `move_embedding_cache(domain: 'str', old_path: 'Path', new_path: 'Path') -> 'None'`

Move ``(domain, old_path)``'s embedding-cache entry to ``(domain, new_path)``.

Wired into ``set_feat_id`` (Phase 3, Task 3.6, REQ-008): called after
the folder rename succeeds, relocating the ``feat`` entry from the old
``README.md`` path to the new one (same semantics as
:meth:`EmbeddingCache.move`). A no-op if the old key has no cached
entry.

Args:
    domain:
        The renamed document's domain name (always ``"feat"`` today).
    old_path:
        The pre-rename ``README.md`` path.
    new_path:
        The post-rename ``README.md`` path.


### `read_embedding(domain: 'str', path: 'Path', embed_fn: '_EmbedFn') -> 'Vector'`

Read and, if needed, compute the cached embedding vector for ``(domain, path)``.

The public read entry point over the module-level :data:`_cache`
singleton (Phase 3's similarity tools are the first callers): a file is
only ever re-embedded when its on-disk content hash no longer matches
the hash recorded at the last read of ``(domain, path)`` (ADR
750842b2/REQ-004) -- see :meth:`EmbeddingCache.read` for the full
contract.

Args:
    domain:
        The document's domain name (one of the whole-body domains'
        ``type`` values, e.g. ``"req"``).
    path:
        The filesystem path to the document file.
    embed_fn:
        Computes the document's vector from the exact, already-read and
        already-hashed file text on a cache miss (must not re-read
        ``path`` itself).

Returns:
    The cached or freshly-computed vector (read-only -- see the module
    docstring).


### `reset_embedding_cache() -> 'None'`

Clear every embedding-cache entry (test-only).

Not for production use. See :meth:`EmbeddingCache.reset`.

