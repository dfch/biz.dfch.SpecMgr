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
only :func:`ensure_doc_base_dir` does. There is deliberately no in-memory
id -> path cache either -- every lookup re-scans the base directory and
re-parses each file, matching this codebase's "the on-disk file is the sole
source of truth" design.

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


### `find_doc_path_by_id(base_dir: 'Path', id_: 'str', parse_fn: 'Callable[[str], _DocT]', get_id_fn: 'Callable[[_DocT], str | None]') -> 'Path'`

Resolve an ``id`` to its on-disk file path, for any doc type.

Scans every ``*.md`` file under ``base_dir``, parsing each via
``parse_fn`` and comparing ``get_id_fn(parsed)`` against ``id_``. A file
that fails to parse (``AssertionError`` or ``ValueError``, which
``pydantic.ValidationError`` and every parser-specific error in this
codebase -- e.g. ``AdrParseError`` -- subclass) is silently skipped --
one broken file must not prevent lookup of a different, valid id.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.
parse_fn:
    Parses a file's full text into a document object (e.g. ``parse_adr``,
    ``parse_req``).
get_id_fn:
    Extracts the id (or ``None``) from a parsed document object (e.g.
    ``lambda doc: doc.frontmatter.id``).

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

