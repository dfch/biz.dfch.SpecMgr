# `biz.dfch.specmgr.req.tools._paths`

Requirement base directory resolution and id -> path lookup (Task 3.11).

A thin, requirement-specific layer over the generic
``general.tools._doc_paths`` module (Task 3.10), rather than a second
hand-written copy of ``adr.tools._paths`` -- the base-directory/id-lookup
plumbing is identical in shape, only the parsed document type and its id
accessor differ.

Mirrors ``adr.tools._paths``'s read-only/write split: :func:`req_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_req_base_dir` does, for the eventual
``create_req`` tool (Task 3.12). There is deliberately no in-memory id ->
path cache either -- every lookup re-scans the base directory and re-parses
each file, matching this codebase's "the on-disk file is the sole source of
truth" design.

## Classes

### `ReqNotFoundError`

No requirement file found matching the given id.

A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
a subclass of it -- the same relationship ``adr.tools._paths.AdrNotFoundError``
has to nothing generic, so callers can keep catching a requirement-specific
exception type without depending on the generic module's own exception.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_get_req_id(doc: 'ReqDocument') -> 'str | None'`

Extract the id from a parsed :class:`ReqDocument` (``find_doc_path_by_id``'s ``get_id_fn``).


### `ensure_req_base_dir() -> 'Path'`

Return the configured requirement base directory, creating it if missing.

Only ``create_req`` (Task 3.12) should call this -- every other
tool/resource uses the read-only :func:`req_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist requirement base directory.


### `find_req_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path under ``base_dir``.

Scans every ``*.md`` file under ``base_dir``, parsing each via
:func:`~biz.dfch.specmgr.req.models.v1.parse_req` and comparing
``frontmatter.id`` against ``id_``. A file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) is silently skipped --
one broken file must not prevent lookup of a different, valid id.
Mirrors ``adr.tools._paths.find_adr_path``'s own skip-on-parse-failure
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
ReqNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_req_paths() -> 'Iterator[Path]'`

Yield every requirement ``*.md`` file under :func:`req_base_dir`, sorted by name.

Yields nothing (rather than raising) if the base directory does not exist.

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `req_base_dir() -> 'Path'`

Return the configured requirement base directory, without creating it.

Thin wrapper over ``general.tools._doc_paths.doc_base_dir(REQ_TYPE_NAME)``
-- see that function's own docstring for the env var/default it reads.

Returns
-------
Path
    The resolved requirement base directory.

