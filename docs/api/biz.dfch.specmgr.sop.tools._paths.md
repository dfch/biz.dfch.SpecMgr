# `biz.dfch.specmgr.sop.tools._paths`

SOP base directory resolution and id -> path lookup (Task 2.1).

A thin, SOP-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``dec.tools._paths`` file-for-file.

Mirrors ``dec.tools._paths``'s read-only/write split: :func:`sop_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_sop_base_dir` does, for ``create_sop``. There is
deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.

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


### `ensure_sop_base_dir() -> 'Path'`

Return the configured SOP base directory, creating it if missing.

Only ``create_sop`` should call this -- every other tool/resource uses
the read-only :func:`sop_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist SOP base directory.


### `find_sop_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, parsing each via
:func:`~biz.dfch.specmgr.sop.models.v1.parse_sop` and comparing
``frontmatter.id`` against ``id_``. A file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``dec.tools._paths.find_dec_path``'s own skip-on-parse-failure
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
SopNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_sop_paths() -> 'Iterator[Path]'`

Yield every SOP ``*.md`` file under :func:`sop_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `sop_base_dir() -> 'Path'`

Return the configured SOP base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(SOP_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved SOP base directory.

