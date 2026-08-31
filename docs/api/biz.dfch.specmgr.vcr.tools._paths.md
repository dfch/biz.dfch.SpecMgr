# `biz.dfch.specmgr.vcr.tools._paths`

Verification case record base directory resolution and id -> path lookup (Task 2.1).

A thin, VCR-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``dec.tools._paths`` file-for-file.

Mirrors ``gol.tools._paths``'s read-only/write split: :func:`vcr_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_vcr_base_dir` does, for ``create_vcr``. There is
deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.

## Classes

### `VcrNotFoundError`

No verification case record file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``gol.tools._paths.GolNotFoundError``
has to nothing generic, so callers can keep catching a VCR-specific
exception type without depending on the generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_vcr_id(doc: 'VcrDocument') -> 'str | None'`

Extract the id from a parsed :class:`VcrDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `ensure_vcr_base_dir() -> 'Path'`

Return the configured verification case record base directory, creating it if missing.

Only ``create_vcr`` should call this -- every other tool/resource uses
the read-only :func:`vcr_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist verification case record base directory.


### `find_vcr_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, parsing each via
:func:`~biz.dfch.specmgr.vcr.models.v1.parse_vcr` and comparing
``frontmatter.id`` against ``id_``. A file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``gol.tools._paths.find_gol_path``'s own skip-on-parse-failure
rule.

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
VcrNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_vcr_paths() -> 'Iterator[Path]'`

Yield every verification case record ``*.md`` file under :func:`vcr_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `vcr_base_dir() -> 'Path'`

Return the configured verification case record base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(VCR_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved verification case record base directory.

