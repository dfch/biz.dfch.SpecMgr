# `biz.dfch.specmgr.sop.tools._paths`

SOP base directory resolution and id -> path lookup (Task 2.1).

A thin, SOP-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``dec.tools._paths`` file-for-file.

Mirrors ``dec.tools._paths``'s read-only/write split: :func:`sop_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_sop_base_dir` does, for ``create_sop``.

**Cache-backed scan (feat-107-doc-cache Phase 4).** :func:`find_sop_path`
now scans through the content-hash-validated per-domain cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s own
``read_sop`` (not ``parse_sop``) as ``find_doc_path_by_id``'s ``read_fn``,
so a file whose on-disk content hash is unchanged since its last read is
not re-parsed, and it passes ``._cache``'s ``reconcile_sop_cache`` as
``reconcile_fn`` so an orphaned cache entry (a file deleted outside
specmgr's own tooling) is dropped before any per-file work on every scan.
``read_sop``/``reconcile_sop_cache`` are imported from ``._cache``, not
``._io``, to avoid a circular import -- see ``._cache``'s own module
docstring for the full rationale. The filesystem remains the sole source
of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache entry is only
ever a memoization keyed by validated content hash, never an independent
fact about what exists on disk.

## Classes

### `SopNotFoundError`

No SOP file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``dec.tools._paths.DecNotFoundError``
has to nothing generic, so callers can keep catching a SOP-specific
exception type without depending on the generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_sop_id(doc: 'SopDocument') -> 'str | None'`

Extract the id from a parsed :class:`SopDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `_reconcile_sop_scan(scan_paths: 'Iterable[Path]') -> 'None'`

Reconcile the ``sop`` cache against the domain-wide live listing (the ``find_sop_path`` ``reconcile_fn``).

The ``reconcile_fn`` :func:`find_doc_path_by_id` calls once, before any
per-file work, with the scanned directory's own materialized path
listing. With the ``{language}`` subfolder layout (feat-197-i18n
Phase 125, ADR 38efdb66 item 9), a scan of one language directory no
longer covers the whole domain -- reconciling against ``scan_paths``
alone would evict every other language's cached entries -- so this
wrapper instead hands :func:`~._cache.reconcile_sop_cache` the
domain-wide union (the flat EN files plus every file in every
shape-valid ``{language}`` subdirectory,
``general.tools._doc_paths.iter_doc_paths_all_languages``).
``scan_paths`` is intentionally unused: the union is a superset of it.
With no language subdirectory present the union is the scanned listing
itself (the pre-i18n behavior, byte-identical).


### `ensure_sop_base_dir(language: 'str | None' = None) -> 'Path'`

Return the configured SOP base directory, creating it if missing.

Only ``create_sop`` should call this -- every other tool/resource uses
the read-only :func:`sop_base_dir` instead.

The optional ``language`` parameter selects the same flat-vs-subdirectory resolution as
:func:`sop_base_dir` (feat-197-i18n Phase 125) before the directory is created.

Parameters
----------
language:
    The document language to resolve -- see
    :func:`general.tools._doc_paths.ensure_doc_base_dir`.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist SOP base directory.


### `find_sop_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, reading each through the
cache-backed :func:`~._cache.read_sop` (feat-107-doc-cache Phase 4) and
comparing ``frontmatter.id`` against ``id_`` -- a file whose on-disk
content hash is unchanged since its last read is not re-parsed. A file
that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``dec.tools._paths.find_dec_path``'s own skip-on-parse-failure
rule. Before scanning, the cache is reconciled
against the freshly materialized live path listing
(:func:`~._cache.reconcile_sop_cache`, against the domain-wide live listing of every language
-- a scan of one language must not evict the other languages' entries, feat-197-i18n
Phase 125), dropping any cached entry for a
file deleted outside specmgr's own tooling (REQ-005).

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files (the flat EN directory,
    or one ``{language}`` subdirectory).
id_:
    The id to look up.

Returns
-------
Path
    The resolved file path.

Raises
------
SopNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_sop_paths(language: 'str | None' = None) -> 'Iterator[Path]'`

Yield every SOP ``*.md`` file under :func:`sop_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

The optional ``language`` (feat-197-i18n Phase 125) selects the scanned directory:
``None``/omitted or ``"en"`` = the flat ``docs/sop/`` directory (exactly today's
listing); any other shape-validated code = its ``docs/sop/{language}/``
subdirectory (non-recursive; never descends further).

Parameters
----------
language:
    The document language whose directory to scan -- see
    :func:`sop_base_dir`.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `sop_base_dir(language: 'str | None' = None) -> 'Path'`

Return the configured SOP base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(SOP_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

The optional ``language`` (feat-197-i18n Phase 125) selects the flat-vs-subdirectory
resolution: ``None``/omitted or ``"en"`` = the flat ``docs/sop/`` directory exactly
as before; any other shape-validated code = its ``docs/sop/{language}/``
subdirectory.

Parameters
----------
language:
    The document language to resolve -- see
    :func:`general.tools._doc_paths.doc_base_dir`.

Returns
-------
Path
    The resolved SOP base directory.

