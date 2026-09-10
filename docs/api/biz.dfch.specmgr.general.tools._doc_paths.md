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
``AdrParseError`` -- subclass) is silently skipped -- one broken file
must not prevent lookup of a different, valid id.

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

