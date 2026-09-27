# `biz.dfch.specmgr.general.tools._doc_paths`

Generic, doc-type-agnostic base directory resolution, filename slugification,
and id -> path lookup (plan Task 3.10).

Generalizes ``adr.tools._paths``'s shape into a single module shared across
document domains (REQ now, UC later) instead of a copy per domain: one root
env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
for ``type_name="req"``).

**ADR is deliberately left untouched** -- it keeps its own
``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).
Migrating ADR onto this shared module is optional future cleanup, not
bundled into this change.

As with ``adr.tools._paths``, this module has no ``mcp``/file-write
dependency beyond read-only directory listing: :func:`doc_base_dir` never
creates the directory (a read-only tool shouldn't have that side effect),
only :func:`ensure_doc_base_dir` does.

**Cache-backed scan (feat-107-doc-cache Phase 3/4).** :func:`find_doc_path_by_id`
no longer re-parses a file's raw text unconditionally on every scan. Its
``read_fn`` parameter (formerly a text-taking ``parse_fn``) is expected to
be a domain's own content-hash-validated, cache-backed reader (e.g.
``req.tools._cache.read_req``) -- when a candidate file's on-disk content
hash is unchanged since the last time that path was read, ``read_fn``
returns the cached result without re-invoking the underlying parser
(ADR bfd76370-b59b-4d65-b550-a969f6c93c9d). Callers may also pass
``reconcile_fn`` (a domain's own cache-reconcile callable, e.g.
``req.tools._cache.reconcile_req_cache``), invoked once against the freshly
materialized live path listing *before* any per-file work, dropping any
cached entry for a file deleted outside specmgr's own tooling (REQ-005) --
this keeps orphan cleanup to a cheap set comparison rather than additional
file reads. The filesystem nonetheless remains the sole source of truth
(ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache entry is only ever a
memoization keyed by a validated content hash, so a stale entry is
structurally impossible -- it can only ever cost one extra parse, never an
incorrect result.

**Skip-on-parse-failure now also catches ``yaml.YAMLError`` (feat-107-doc-cache
Phase 6, REQ-010).** :func:`find_doc_path_by_id`'s per-file scan loop skips
a file that fails to parse so one broken file never blocks lookup of a
different, valid id. Before Phase 6 this only caught ``AssertionError``/
``ValueError``, which does not include ``yaml.YAMLError`` (not a
``ValueError`` subclass) -- even though every ``parse_<domain>`` genuinely
raises it unwrapped for malformed frontmatter YAML, and both ``DocCache``'s
own ``CACHEABLE_ERROR_TYPES`` and ``general.tools._listing.build_summaries``
already treated it as a normal, skippable failure. This was confirmed
pre-existing and unrelated to the cache mechanism itself (unchanged since
before Phase 3), but folded into this same remediation pass since it sits
in code this feature already touches and directly contradicts the cache's
own failure-handling contract.

**Skip-on-parse-failure now also catches ``FileNotFoundError`` (feat-107-doc-cache
Phase 8, REQ-014).** This scan iterates over a path list materialized at
one point in time (the directory-listing snapshot up front), but the
generic ``delete`` tool in ``general.tools`` only holds the *target*
document's own per-id lock, never a whole-domain lock, while ``get_*``/
``list_*`` intentionally take no lock at all (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3) -- so a concurrent ``delete`` of *any
other* document in the same domain can remove a file between the scan's
directory listing and that file's own turn in the loop, raising
``FileNotFoundError`` out of ``read_fn``. Before Phase 8 this was not
caught here, even though it is the identical race class REQ-012 (Phase 6)
closed for ``feat`` alone, whose rename-based cache integration REQ-012
originally (and, per its own now-corrected text, incorrectly) claimed was
the only trigger for this class of bug -- the generic ``delete`` tool
triggers the exact same race for every one of the other domains. A file
vanishing mid-scan this way is now skipped exactly like any other
unparseable file, and the scan continues looking for the target id.

**A companion :func:`find_parse_failure` surfaces the parse-failure a skipped id
encodes (feat-150-mcp-lifecycle-commands Phase 1a, ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c).** :func:`find_doc_path_by_id`'s
skip-on-parse-failure behavior above is deliberate and unchanged -- but it
means ``get_<d>`` on a document whose own file is broken raised only the
generic not-found error, with no parse cause/path/line, and that generic
error was being discarded client-side anyway (the ADR 519d1206
``isError: true`` truncation chain). :func:`find_parse_failure` recovers
exactly that case: it scans for the single file whose stem encodes the id
(``f"{id_}-"`` prefix), attempts the domain's own cache-backed reader on it,
and returns ``(path, str(exc))`` when that read raises a parse error, so
``get_<d>`` can return a non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` whose ``error``
text carries the same parse defect as the domain's ``list_<d>`` failed-row ``error``
(both are ``str()`` of the same exception from the same reader -- identical field
path and cause; the trailing pydantic documentation line may differ by read
order/cache state, since the ``DocCache``'s exception reconstruction drops it
on warm re-raises -- Option B, 2026-09-26, follow-up issue #162). It returns
``None`` otherwise (no name match, a vanished file, or a name-matching file
that parses cleanly), leaving the caller to re-raise its original not-found
error unchanged. It does not alter :func:`find_doc_path_by_id`'s documented
skip behavior; ``update``/``delete``/``set_status``/
``set_classification``/``validate``/``list_references`` keep raising exactly
as before.

## Classes

### `DocNotFoundError`

No document file found matching the given id, under a given base directory.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_docs_root() -> 'Path'`

Return the configured documents root directory, without creating it.


### `doc_base_dir(type_name: 'str') -> 'Path'`

Return the base directory for ``type_name`` documents, without creating it.

Reads :data:`DOCS_DIR_ENV_VAR` from the environment, falling back to
:data:`DEFAULT_DOCS_ROOT`, then appends ``type_name`` as a subdirectory
(e.g. ``docs/req`` for ``type_name="req"``). Read-only tools/resources
use this so merely reading never has the side effect of creating the
directory -- see :func:`ensure_doc_base_dir` for the write path.

Parameters
----------
type_name:
    The document type's subdirectory name, e.g. ``"req"``.

Returns
-------
Path
    The resolved base directory for ``type_name`` documents.


### `ensure_doc_base_dir(type_name: 'str') -> 'Path'`

Return the base directory for ``type_name`` documents, creating it if missing.

Only a doc type's ``create_*`` tool should call this -- every other
tool/resource uses the read-only :func:`doc_base_dir` instead.

Parameters
----------
type_name:
    The document type's subdirectory name, e.g. ``"req"``.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist base directory for
    ``type_name`` documents.


### `find_doc_path_by_id(base_dir: 'Path', id_: 'str', read_fn: 'Callable[[Path], _DocT]', get_id_fn: 'Callable[[_DocT], str | None]', reconcile_fn: 'Callable[[Iterable[Path]], None] | None' = None) -> 'Path'`

Resolve an ``id`` to its on-disk file path, for any doc type.

Materializes the full ``*.md`` path listing under ``base_dir`` up
front, reconciles a cache against it (via ``reconcile_fn``, if given)
before doing any per-file work, then scans that same materialized
listing, reading each path via ``read_fn`` and comparing
``get_id_fn(parsed)`` against ``id_``. A file that fails to parse
(``AssertionError`` or ``ValueError``, which ``pydantic.ValidationError``
and every parser-specific error in this codebase -- e.g.
``AdrParseError`` -- subclass; ``yaml.YAMLError``, raised unwrapped
for malformed frontmatter YAML by every ``parse_<domain>`` function,
Phase 6, REQ-010; or ``FileNotFoundError``, raised by ``read_fn`` when
a file vanishes between this function's own directory-listing
snapshot and its own turn in the per-file scan loop -- e.g. a
concurrent ``delete`` tool call racing this lock-free scan, Phase 8,
REQ-014) is silently skipped -- one broken (or vanished) file must not
prevent lookup of a different, valid id. Before Phase 6, ``yaml.YAMLError``
was not caught here (it is not a ``ValueError`` subclass), even though
``DocCache``'s own ``CACHEABLE_ERROR_TYPES`` and
``general.tools._listing.build_summaries`` (the ``list_*`` read
callback) both already treated it as a normal, skippable failure -- a
domain directory with one file whose frontmatter YAML was malformed
crashed this scan with an uncaught ``yaml.YAMLError`` for *any* id in
that domain, not just the malformed file's own id. Before Phase 8,
``FileNotFoundError`` was likewise not caught here, even though it is
the identical delete/scan race class REQ-012 (Phase 6) closed for
``feat`` alone -- see this module's own docstring above for the full
explanation.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.
read_fn:
    Reads and parses a file at the given path into a document object
    (e.g. a domain's own cache-backed ``read_<domain>``, such as
    ``req.tools._cache.read_req``). Unlike the retired ``parse_fn`` this
    replaces, ``read_fn`` takes a ``Path``, not text -- a cache-backed
    reader decides for itself whether to re-read/re-parse ``path`` or
    return an already-validated cached result.
get_id_fn:
    Extracts the id (or ``None``) from a parsed document object (e.g.
    ``lambda doc: doc.frontmatter.id``).
reconcile_fn:
    When given, called once with the full materialized live path
    listing before any per-file work, to drop any cache entry for a
    path no longer present on disk (e.g.
    ``req.tools._cache.reconcile_req_cache``, REQ-005). ``None`` (the
    default) skips reconciliation entirely -- e.g. for a domain that
    has not yet wired a cache through this function.

Returns
-------
Path
    The resolved file path.

Raises
------
DocNotFoundError
    If no file's parsed id matches ``id_``.


### `find_parse_failure(base_dir: 'Path', id_: 'str', read_fn: 'Callable[[Path], _DocT]') -> 'tuple[Path, str] | None'`

Resolve the parse-failure for an id whose on-disk file exists but is unparseable.

Companion to :func:`find_doc_path_by_id` for the one case that function
deliberately cannot surface: a file whose own stem encodes ``id_``
(exactly one file can match, since names are unique) but whose content
fails to parse. :func:`find_doc_path_by_id`
silently skips such a file during its id scan (one broken file must not
block lookup of a different, valid id), so ``get_<d>`` on a broken
document would otherwise only raise the domain's generic not-found error,
with no parse cause, path, or line. This function recovers exactly that
case: it scans :func:`iter_doc_paths` for the single name-matching file -- a stem that
carries ``id_`` as a hyphen-bounded token, i.e. ``f"-{id_}-" in stem``
(the flat-file naming is ``<type>-<id>-<slug>.md``, so ``id_`` sits
between the type prefix and the slug) or a ``f"{id_}-"`` prefix (the
``<id>-<slug>.md`` form) -- attempts the domain's own cache-backed
``read_fn`` on it, and returns
``(path, str(exc))`` if that read raises a parse error
(``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError`` --
the same channels :func:`general.tools._listing.build_summaries` catches
for the ``list_<d>`` failed row, so ``str(exc)`` here carries the same
parse defect as that row's ``error`` field -- identical field path and
cause; the trailing pydantic documentation line may differ by read
order/cache state, since the ``DocCache``'s exception reconstruction
drops it on warm re-raises -- Option B, 2026-09-26, follow-up issue
#162). It returns ``None`` for every other
outcome -- no name match, a name-matching file that vanishes mid-scan
(``FileNotFoundError``), or a name-matching file that parses cleanly
(a frontmatter-id mismatch, i.e. the file is not the requested document)
-- so a caller can re-raise its original not-found error unchanged.

feat-150-mcp-lifecycle-commands Phase 1a, ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c: the ``get_<d>`` tools call this on
the domain's ``XNotFoundError`` and return a non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` for a
non-``None`` result.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id whose on-disk file may exist but be unparseable.
read_fn:
    The domain's own cache-backed reader (e.g. ``req.tools._cache.
    read_req``) -- the same callable the domain's ``list_<d>`` tool reads
    with, so the captured ``str(exc)`` matches its failed row.

Returns
-------
tuple[Path, str] | None
    ``(path, error_text)`` for the name-matching, unparseable file, or
    ``None`` if there is no parse failure to surface (no name match, a
    vanished file, or a name-matching file that parses cleanly).


### `iter_doc_paths(base_dir: 'Path') -> 'Iterator[Path]'`

Yield every ``*.md`` file directly under ``base_dir``, sorted by name.

Yields nothing (rather than raising) if ``base_dir`` does not exist.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `slugify(title: 'str') -> 'str'`

Derive a filename-safe slug from a document title.

Ported from ``adr.tools._paths.slugify`` unchanged: lowercases
``title``, collapses every run of non-``[a-z0-9]`` characters into a
single ``-``, strips leading/trailing ``-``, truncates to
:data:`_SLUG_MAX_LENGTH` characters (stripping a trailing ``-`` again in
case the truncation lands mid-run), and falls back to
:data:`_FALLBACK_SLUG` if the result would otherwise be empty (e.g. a
title with no alphanumeric characters at all).

Parameters
----------
title:
    The document title to slugify.

Returns
-------
str
    The filename-safe slug.

