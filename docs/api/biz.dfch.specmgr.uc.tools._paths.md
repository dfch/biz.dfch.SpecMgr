# `biz.dfch.specmgr.uc.tools._paths`

Use-case base directory resolution and id -> path lookup (Task 3.1.5).

A thin, use-case-specific layer over the generic
``general.tools._doc_paths`` module, mirroring ``req.tools._paths`` exactly.

Mirrors ``req.tools._paths``'s read-only/write split: :func:`uc_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_uc_base_dir` does, for ``create_uc``. There is
deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.

## Classes

### `UcNotFoundError`

No use-case file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- mirrors ``req.tools._paths.ReqNotFoundError``'s own
relationship, so callers can keep catching a use-case-specific exception
type without depending on the generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_uc_id(doc: 'UcDocument') -> 'str | None'`

Extract the id from a parsed :class:`UcDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `ensure_uc_base_dir() -> 'Path'`

Return the configured use-case base directory, creating it if missing.

Only ``create_uc`` should call this -- every other tool/resource uses
the read-only :func:`uc_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist use-case base directory.


### `find_uc_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, parsing each via
:func:`~biz.dfch.specmgr.uc.models.v2.parse_uc` and comparing
``frontmatter.id`` against ``id_``. A file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``req.tools._paths.find_req_path``'s own skip-on-parse-failure
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
UcNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_uc_paths() -> 'Iterator[Path]'`

Yield every use-case ``*.md`` file under :func:`uc_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `uc_base_dir() -> 'Path'`

Return the configured use-case base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(UC_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved use-case base directory.

