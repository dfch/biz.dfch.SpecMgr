# `biz.dfch.specmgr.general.tools._doc_cache`

Generic, doc-type-agnostic content-hash-validated in-memory read cache (feat-107-doc-cache, Phase 2/Phase 6).

``get_*``/``list_*`` MCP tool calls currently re-scan and fully re-parse an
entire domain directory on every single invocation
(``general.tools._doc_paths.find_doc_path_by_id``,
``general.tools._listing.build_summaries``), paying full markdown-it
tokenizing plus nested Pydantic validation cost on every call, for every
candidate file scanned -- CPU-bound work that holds the GIL and therefore
serializes regardless of how many threads/cores are available. This module
supplies :class:`DocCache`, a reusable, domain-agnostic cache class that
eliminates that redundant re-parsing: a file is only ever re-parsed when its
on-disk content actually changed.

**Process-local, one instance per domain.** This module supplies only the
reusable :class:`DocCache` class itself -- it is Phase 3/4's job to
instantiate one module-level singleton per domain (mirroring the existing
per-domain ``threading.Lock`` registries in each domain's own ``_lock.py``)
and route that domain's ``read_<domain>``/``find_doc_path_by_id`` scan/
``list_<domain>`` summary-building callback through it. **ADR
(``models/adr/v1``) is deliberately excluded from this cache mechanism
entirely** -- it is expected to be phased out later and does not justify
its own independently-implemented cache module, since it has no dependency
on ``general`` to begin with.

**Content-hash validation guarantee.** Every :meth:`DocCache.read` call
re-hashes ``path``'s full on-disk text (``hashlib.blake2b``) and compares it
against the hash recorded at the last successful/failed read of that path
*before* deciding whether to skip re-parsing -- a stale entry is
structurally impossible, it can only ever cost one extra parse. This
refines, rather than violates, ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3's
"the filesystem is the sole source of truth" invariant. See ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d for the full design this module
implements, including its relationship to ADR 33c5ab08 and the explicit
ADR-domain exclusion above.

**Phase 6 (feat-107-doc-cache): a hash/parse TOCTOU race, and two latent
design risks, closed.** An independent post-closeout review of the Phase
1-5 implementation found that :meth:`read` originally hashed ``path`` via
one ``path.read_text()`` call and then called a ``parse_fn(path)`` that
every domain's own ``_parse`` wrapper implemented as its *own*, second,
independent ``path.read_text()`` call -- the two reads were not atomic, so
a concurrent write racing between them could produce a cache entry whose
stored hash did not correspond to its stored, parsed result (REQ-007).
:meth:`read`'s ``parse_fn`` parameter is now ``Callable[[str], _DocT]``
(text in, not ``Path`` in): the exact text that gets hashed is also the
exact text handed to ``parse_fn``, with zero intervening file I/O, closing
the race structurally rather than by convention. The same review also
found two latent, previously-untriggered risks, both now closed: a cache
hit returned the exact same, shared, mutable document object on every
call, so a future accidental in-place mutation by caller code could corrupt
every subsequent caller's view of that entry (REQ-008, closed by returning
a fresh :meth:`~pydantic.BaseModel.model_copy` on every hit); and cache
entries were keyed by raw, unnormalized ``Path`` objects, so two different
string forms of the same on-disk file (e.g. relative vs. ``.resolve()``d)
could in principle produce two independently-tracked, independently-
invalidated entries for one physical file (REQ-009, closed by normalizing
every key via ``Path.resolve()`` on entry to every public method). A
second review of the Phase 6 remediation plan itself, before any of it was
coded, found one further gap in the REQ-008 fix as originally scoped: a
cache hit on a previously-*failed* parse still re-raised the exact same
stored exception *instance* on every hit, extending its ``__traceback__``
indefinitely and eventually mixing frames from unrelated call stacks
(REQ-011, closed by :func:`_fresh_exception`, reconstructing a fresh,
equivalent exception object -- same type, same message -- on every hit
instead).

**Lock-ordering rule.** :class:`DocCache`'s own internal ``threading.Lock``
guards *only* its dict get/set/pop bookkeeping -- never the file read, never
the caller-supplied ``parse_fn`` call itself, and never held across any
domain-level per-id lock (e.g. ``req_lock``, ``feat_create_lock``/
``feat_lock``). Per ADR bfd76370-b59b-4d65-b550-a969f6c93c9d, this cache's
lock is always the *innermost* lock acquired in any call stack: a caller
holding a domain lock may acquire this cache's lock, but this cache never
acquires a domain lock itself, and never holds its own lock across a call
back into caller code (the file read or ``parse_fn``) that could itself
attempt to acquire another lock.

**Explicitly out of scope** (mirroring the feature's own Scope section): no
TTL/size-based eviction, and no ``stat()``-based (mtime/size) pre-check fast
path -- content-hash-only for this first version.

## Classes

### `DocCache`

A process-local, content-hash-validated in-memory read cache for one domain.

Shaped as ``dict[Path, tuple[content_hash, result]]`` (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d), where ``result`` is either the
successfully parsed document or the exception a prior parse attempt
raised. One :class:`DocCache` instance is intended per domain, created
once as a module-level singleton (Phase 3/4's job, not this module's) --
this class carries no assumption about which domain it caches for
beyond the generic ``_DocT`` type parameter.

**Every public method normalizes its ``Path`` argument(s) via
``.resolve()`` before touching the internal dict (REQ-009, Phase 6).**
Two different string forms of the same on-disk file (e.g. a relative
path and its resolved, absolute form) therefore always address the
*same* cache entry -- they can never be independently tracked or
independently invalidated. Callers may still pass an unresolved
``Path`` in; normalization happens internally and is invisible to
them.

Not thread-hostile, but not a full cross-file synchronization
primitive either: the internal lock (``threading.Lock``) guards only
this instance's dict bookkeeping, so concurrent :meth:`read` calls for
*different* paths never block each other on that bookkeeping. A
concurrent cold-start race for the *same* path may still invoke
``parse_fn`` more than once (allowed for by ACC-006, a Phase 3 concern);
this class does not attempt to de-duplicate in-flight parses.

**Methods:**

- `invalidate(self, path: 'Path') -> 'None'`
  Drop ``path``'s cache entry, if present.

  A no-op if ``path`` has no cached entry.

  Parameters
  ----------
  path:
      The filesystem path whose cache entry to drop. Normalized via
      ``.resolve()`` before use as the cache key (REQ-009).

- `move(self, old_path: 'Path', new_path: 'Path') -> 'None'`
  Relocate ``old_path``'s cache entry (if present) to ``new_path``.

  For a rename case (``set_feat_id``'s only current caller): a no-op
  if ``old_path`` has no cached entry. Otherwise, moves the entry's
  stored ``(hash, result)`` pair as-is, without re-validating it
  against ``new_path``'s actual on-disk content.

  **This is not a byte-identical-content optimization** (a prior
  version of this docstring incorrectly claimed it was, Phase 6):
  ``set_feat_id``, ``move``'s only caller, always rewrites both the
  ``id`` and ``updated`` frontmatter fields before writing
  ``new_path``, so ``old_path``'s and ``new_path``'s content are
  *never* byte-for-byte identical in the realistic case. The moved
  entry's stale hash therefore always mismatches on the very next
  :meth:`read` of ``new_path`` -- a guaranteed, harmless cache miss
  that reparses ``new_path`` once and re-stores a correct, fresh
  entry for it, self-healing the moved-but-now-stale entry through
  the exact same hash-validation path every other :meth:`read` call
  already uses. The reason to call :meth:`move` at all, rather than
  simply calling :meth:`invalidate` on ``old_path`` and letting
  ``new_path`` start out as a plain cache miss, is solely to drop
  ``old_path``'s now-defunct entry as part of the same operation
  (old and new are always handled together, one call instead of
  two) -- not to preserve a hit that was never actually achievable.

  Parameters
  ----------
  old_path:
      The cache entry's current key. Normalized via ``.resolve()``
      before use (REQ-009).
  new_path:
      The cache entry's new key. Normalized via ``.resolve()``
      before use (REQ-009).

- `read(self, path: 'Path', parse_fn: 'Callable[[str], _DocT]') -> '_DocT'`
  Return the cached or freshly-parsed result for ``path``.

  Reads ``path``'s full on-disk text and computes its content hash
  exactly once per call, regardless of hit/miss (Phase 6, REQ-007):
  that same text is both what gets hashed and, on a miss, what gets
  handed to ``parse_fn`` -- there is no second, independent file
  read between the two, so the stored hash and the stored result
  can never originate from different on-disk snapshots of ``path``
  (the TOCTOU race the Phase 1-5 implementation had, where ``read``
  hashed one ``path.read_text()`` call and then called
  ``parse_fn(path)``, which every domain's own ``_parse`` wrapper
  implemented as its own second, independent ``path.read_text()``
  call).

  When the computed hash matches the hash stored for ``path`` at its
  last read, the stored result is returned/re-raised without
  invoking ``parse_fn`` again:

  - On a cached **success**, a fresh, deep copy of the stored
    document is returned (via :meth:`~pydantic.BaseModel.model_copy`,
    Phase 6, REQ-008) rather than the exact same object instance
    held in this cache's own dict -- so no accidental in-place
    mutation by caller code can ever corrupt the shared entry for
    every subsequent caller. A non-``BaseModel`` result (not
    expected from any ``parse_<domain>`` in this codebase today, but
    not assumed away either) is returned as-is, uncopied.
  - On a cached **failure**, a *fresh*, equivalent exception object
    is raised -- same type, same message, but never the exact same
    instance raised on a previous hit (Phase 6, REQ-011, via
    :func:`_fresh_exception`) -- so a persistently malformed file's
    exception is never re-raised as the identical object on every
    hit, which would otherwise extend that one object's
    ``__traceback__`` indefinitely and eventually mix frames from
    unrelated call stacks.

  On a hash mismatch or cache miss, ``parse_fn(text)`` is called
  fresh, and the new ``(hash, result)`` pair (or ``(hash,
  exception)`` for one of :data:`CACHEABLE_ERROR_TYPES`) is stored
  before returning/re-raising -- the exact object ``parse_fn`` just
  produced, uncopied, since nothing else could yet hold a reference
  to it.

  Only the dict get/set around ``parse_fn`` is guarded by this
  instance's lock; the file read and the ``parse_fn`` call itself
  happen outside the lock, so a slow parse of one path never blocks a
  concurrent read of a different path.

  Parameters
  ----------
  path:
      The filesystem path to read and, if needed, parse. Normalized
      via ``.resolve()`` before use as the cache key (REQ-009); the
      text is read from ``path`` as given (resolving does not change
      which file is read, only which key addresses its entry).
  parse_fn:
      Parses the given text into a document object on a cache miss
      (e.g. a domain's own ``_parse`` helper in ``<domain>.tools.
      _cache``, such as ``lambda text: parse_req(text)``). Receives
      the *exact* text this call already read and hashed -- it must
      not re-read ``path`` itself (Phase 6, REQ-007).

  Returns
  -------
  _DocT
      The cached (freshly copied, on a hit) or freshly-parsed
      document.

  Raises
  ------
  Exception
      Raises a fresh, equivalent reconstruction (see
      :func:`_fresh_exception`) of a cached parse failure (one of
      :data:`CACHEABLE_ERROR_TYPES`) on a hash match, or propagates a
      fresh ``parse_fn`` failure of one of those types after caching
      it. Any other exception (including a failure to even read
      ``path``, e.g. ``OSError``/``FileNotFoundError``) propagates
      uncaught and is never cached.

- `reconcile(self, live_paths: 'Iterable[Path]') -> 'None'`
  Drop every cached entry whose path is not in ``live_paths``.

  A pure set-difference operation against the given, already
  materialized live path listing (e.g. from a cheap directory glob
  via ``iter_doc_paths``) -- performs no file I/O of its own.

  Parameters
  ----------
  live_paths:
      The current, live set of on-disk paths for this domain. Each
      path is normalized via ``.resolve()`` before comparison
      (REQ-009), matching how every entry's own key is normalized.

- `reset(self) -> 'None'`
  Clear every cached entry.

  Test-only: not for production use. Exists so tests do not leak
  cached entries across test cases within the same process, since a
  domain's cache instance is otherwise a module-level singleton that
  persists for the whole test process's lifetime.


## Functions

### `_fresh_exception(exc: 'Exception') -> 'Exception'`

Reconstruct a fresh, equivalent exception object from a previously-cached one (REQ-011).

Used by :meth:`DocCache.read` on every cache hit against a stored parse
failure, so re-raising a cached failure never re-raises the *exact same
object* twice -- see :meth:`DocCache.read`'s own docstring for why that
matters.

A single, one-size-fits-all reconstruction (e.g. ``type(exc)(*exc.args)``)
does not work for every member of :data:`CACHEABLE_ERROR_TYPES`, so this
function special-cases each:

- ``pydantic.ValidationError``: ``.args`` is always empty (it is a
  ``pydantic_core``-implemented type whose real state lives outside
  ``BaseException.args`` entirely), so ``type(exc)(*exc.args)`` would
  silently reconstruct an exception with an empty message. Instead,
  each of ``exc.errors()``'s per-field dicts is re-wrapped as its own
  ``pydantic_core.PydanticCustomError(detail["type"], detail["msg"])``
  and handed to ``ValidationError.from_exception_data`` -- this exactly
  reproduces ``str(exc)`` for every ``ValidationError`` this codebase's
  own ``parse_<domain>`` functions actually raise (every one of them is
  already "enriched" into a custom error type by
  ``models.md._frontmatter_parse.enrich_frontmatter_validation_error``,
  which this mirrors). A genuinely built-in-kind (non-custom-wrapped)
  ``ValidationError`` -- not something any ``parse_<domain>`` in this
  codebase ever raises -- would still round-trip its message text
  faithfully, only losing the trailing "For further information visit
  ..." documentation-link footer pydantic-core appends to a
  recognized builtin kind.
- ``yaml.error.MarkedYAMLError`` (the concrete type every real
  ``yaml.YAMLError`` this codebase raises actually is, per
  ``models.md._frontmatter_parse.enrich_frontmatter_yaml_error``, which
  always constructs it via keyword arguments): ``.args`` is *also*
  always empty here, for the same underlying reason
  ``enrich_frontmatter_yaml_error`` itself had to work around --
  ``BaseException.args`` only ever captures *positional* constructor
  arguments, and every real construction site in this codebase (both
  PyYAML's own internals and ``enrich_frontmatter_yaml_error``) uses
  keyword arguments. Reconstructed here the same way
  ``enrich_frontmatter_yaml_error`` already does: by keyword, from the
  ``context``/``context_mark``/``problem``/``problem_mark``/``note``
  attributes ``MarkedYAMLError.__init__`` always sets on ``self``.
- Anything else (``AssertionError``, and a plain, non-``Marked``
  ``yaml.YAMLError``): ``type(exc)(*exc.args)`` -- verified to
  round-trip both types' ``str()`` output exactly, since both are
  genuinely constructed from positional arguments in every real
  construction site this codebase or PyYAML itself uses.

Parameters
----------
exc:
    The previously-cached exception to reconstruct a fresh, equivalent
    copy of.

Returns
-------
Exception
    A new exception instance (``is``-distinct from ``exc``) of the
    same type, with an equivalent (for the codebase's own real usage,
    identical) message.

