# `biz.dfch.specmgr.txt.tools._paths`

Free-form text (TXT) base directory resolution and id -> path lookup (feat-229-txt Phase 110).

A thin, TXT-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``vcr.tools._paths`` --
the base-directory/id-lookup plumbing is identical in shape, only the
parsed document type and its id accessor differ. Mirrors
``vcr.tools._paths`` file-for-file.

Documents live flat under the shared docs root as
``{docs root}/txt/txt-{uuid}-{slug}.md`` (the plan's "Directory and id"
design note): there is deliberately **no** ``SPECMGR_TXT_DIR`` env var and
**no** ``_envregistry`` entry for this domain -- ``txt`` delegates to the
shared ``SPECMGR_DOCS_DIR``-rooted default exactly like ``vcr``/``sysrs``.

Mirrors ``vcr.tools._paths``'s read-only/write split: :func:`txt_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_txt_base_dir` does, for ``create_txt``.

**Cache-backed scan (feat-107-doc-cache Phase 4 shape, repeated here).**
:func:`find_txt_path` scans through the content-hash-validated per-domain
cache (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s
own ``read_txt`` (not ``parse_txt``) as ``find_doc_path_by_id``'s
``read_fn``, so a file whose on-disk content hash is unchanged since its
last read is not re-parsed, and it passes ``._cache``'s
``reconcile_txt_cache`` as ``reconcile_fn`` so an orphaned cache entry (a
file deleted outside specmgr's own tooling) is dropped before any per-file
work on every scan. ``read_txt``/``reconcile_txt_cache`` are imported from
``._cache``, not ``._io``, to avoid a circular import -- see ``._cache``'s
own module docstring for the full rationale. The filesystem remains the
sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache
entry is only ever a memoization keyed by validated content hash, never an
independent fact about what exists on disk.

## Classes

### `TxtNotFoundError`

No free-form text file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``vcr.tools._paths.
VcrNotFoundError`` has to nothing generic, so callers can keep catching
a TXT-specific exception type without depending on the generic module's
own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_txt_id(doc: 'TxtDocument') -> 'str | None'`

Extract the id from a parsed :class:`TxtDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `ensure_txt_base_dir() -> 'Path'`

Return the configured free-form text base directory, creating it if missing.

Only ``create_txt`` should call this -- every other tool/resource uses
the read-only :func:`txt_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist free-form text base directory.


### `find_txt_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, reading each through the
cache-backed :func:`~._cache.read_txt` and comparing ``frontmatter.id``
against ``id_`` -- a file whose on-disk content hash is unchanged since
its last read is not re-parsed. A file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``vcr.tools._paths.find_vcr_path``'s own skip-on-parse-failure
rule. Before scanning, the cache is reconciled
against the freshly materialized live path listing
(:func:`~._cache.reconcile_txt_cache`), dropping any cached entry for a
file deleted outside specmgr's own tooling.

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
TxtNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_txt_paths() -> 'Iterator[Path]'`

Yield every free-form text ``*.md`` file under :func:`txt_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `txt_base_dir() -> 'Path'`

Return the configured free-form text base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(TXT_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads
(the shared ``SPECMGR_DOCS_DIR``-rooted default; this domain has no
``SPECMGR_TXT_DIR`` of its own).

Returns
-------
Path
    The resolved free-form text base directory.

