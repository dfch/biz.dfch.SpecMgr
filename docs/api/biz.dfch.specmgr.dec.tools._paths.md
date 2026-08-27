# `biz.dfch.specmgr.dec.tools._paths`

Decision base directory resolution and id -> path lookup (Task 2.1).

A thin, decision-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``gol.tools._paths`` file-for-file.

Mirrors ``gol.tools._paths``'s read-only/write split: :func:`dec_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_dec_base_dir` does, for ``create_dec``. There is
deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.

## Classes

### `DecNotFoundError`

No decision file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``gol.tools._paths.GolNotFoundError``
has to nothing generic, so callers can keep catching a decision-specific
exception type without depending on the generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_dec_id(doc: 'DecDocument') -> 'str | None'`

Extract the id from a parsed :class:`DecDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `dec_base_dir() -> 'Path'`

Return the configured decision base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(DEC_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved decision base directory.


### `ensure_dec_base_dir() -> 'Path'`

Return the configured decision base directory, creating it if missing.

Only ``create_dec`` should call this -- every other tool/resource uses
the read-only :func:`dec_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist decision base directory.


### `find_dec_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, parsing each via
:func:`~biz.dfch.specmgr.dec.models.v1.parse_dec` and comparing
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
DecNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_dec_paths() -> 'Iterator[Path]'`

Yield every decision ``*.md`` file under :func:`dec_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.

