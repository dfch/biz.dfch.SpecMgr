# `biz.dfch.specmgr.qa.tools._paths`

Question and Answer (QA) base directory resolution and id -> path lookup (Phase 4, Task 4.1).

A thin, QA-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``adr.tools._paths`` --
the base-directory/id-lookup plumbing is identical in shape, only the parsed
document type and its id accessor differ. 1:1 port of ``req.tools._paths``.

Mirrors ``adr.tools._paths``'s/``req.tools._paths``'s read-only/write split:
:func:`qa_base_dir` never creates the directory (a read-only tool shouldn't
have that side effect), only :func:`ensure_qa_base_dir` does, for the
``create_qa`` tool.

**Cache-backed scan (feat-107-doc-cache Phase 4).** :func:`find_qa_path`
now scans through the content-hash-validated per-domain cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s own
``read_qa`` (not ``parse_qa``) as ``find_doc_path_by_id``'s ``read_fn``,
so a file whose on-disk content hash is unchanged since its last read is
not re-parsed, and it passes ``._cache``'s ``reconcile_qa_cache`` as
``reconcile_fn`` so an orphaned cache entry (a file deleted outside
specmgr's own tooling) is dropped before any per-file work on every scan.
``read_qa``/``reconcile_qa_cache`` are imported from ``._cache``, not
``._io``, to avoid a circular import -- see ``._cache``'s own module
docstring for the full rationale. The filesystem remains the sole source
of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache entry is only
ever a memoization keyed by validated content hash, never an independent
fact about what exists on disk.

## Classes

### `QaNotFoundError`

No Question and Answer (QA) file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``adr.tools._paths.AdrNotFoundError``/
``req.tools._paths.ReqNotFoundError`` have to nothing generic, so callers
can keep catching a QA-specific exception type without depending on the
generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_qa_id(doc: 'QaDocument') -> 'str | None'`

Extract the id from a parsed :class:`QaDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `ensure_qa_base_dir() -> 'Path'`

Return the configured Question and Answer (QA) base directory, creating it if missing.

Only ``create_qa`` should call this -- every other tool/resource uses
the read-only :func:`qa_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist QA base directory.


### `find_qa_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, reading each through the
cache-backed :func:`~._cache.read_qa` (feat-107-doc-cache Phase 4) and
comparing ``frontmatter.id`` against ``id_`` -- a file whose on-disk
content hash is unchanged since its last read is not re-parsed. A file
that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``adr.tools._paths.find_adr_path``'s/``req.tools._paths.find_req_path``'s
own skip-on-parse-failure rule. Before scanning, the cache is reconciled
against the freshly materialized live path listing
(:func:`~._cache.reconcile_qa_cache`), dropping any cached entry for a
file deleted outside specmgr's own tooling (REQ-005).

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
Path
    The resolved file path.

Raises
------
QaNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_qa_paths() -> 'Iterator[Path]'`

Yield every QA ``*.md`` file under :func:`qa_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `qa_base_dir() -> 'Path'`

Return the configured Question and Answer (QA) base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(QA_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved QA base directory.

