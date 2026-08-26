# `biz.dfch.specmgr.gol.tools._paths`

Goal base directory resolution and id -> path lookup (Task 3.1).

A thin, goal-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``prb.tools._paths``/
``req.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``prb.tools._paths`` file-for-file.

Mirrors ``prb.tools._paths``'s read-only/write split: :func:`gol_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_gol_base_dir` does, for ``create_gol``. There is
deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.

## Classes

### `GolNotFoundError`

No goal file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``prb.tools._paths.PrbNotFoundError``
has to nothing generic, so callers can keep catching a goal-specific
exception type without depending on the generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_gol_id(doc: 'GolDocument') -> 'str | None'`

Extract the id from a parsed :class:`GolDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `ensure_gol_base_dir() -> 'Path'`

Return the configured goal base directory, creating it if missing.

Only ``create_gol`` should call this -- every other tool/resource uses
the read-only :func:`gol_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist goal base directory.


### `find_gol_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, parsing each via
:func:`~biz.dfch.specmgr.gol.models.v1.parse_gol` and comparing
``frontmatter.id`` against ``id_``. A file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``prb.tools._paths.find_prb_path``'s own skip-on-parse-failure
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
GolNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `gol_base_dir() -> 'Path'`

Return the configured goal base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(GOL_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved goal base directory.


### `iter_gol_paths() -> 'Iterator[Path]'`

Yield every goal ``*.md`` file under :func:`gol_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.

