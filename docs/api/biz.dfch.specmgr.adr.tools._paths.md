# `biz.dfch.specmgr.adr.tools._paths`

ADR base directory resolution, filename slugification, and id -> path
lookup (plan §9a).

Deliberately excludes any ``mcp``/file-write dependency beyond read-only
directory listing/parsing, so this module stays testable without an MCP
server: ``adr_base_dir`` never creates the directory (a read-only tool
shouldn't have that side effect), only ``ensure_adr_base_dir`` does, and
only ``create_adr`` (in ``tools.py``) calls it.

There is deliberately no in-memory id -> path cache (plan §9a): every
lookup re-scans the base directory and re-parses each file's frontmatter,
matching the "the on-disk file is the sole source of truth" design (plan
§7) and avoiding a staleness problem against concurrent human edits.

## Classes

### `AdrNotFoundError`

No ADR file found matching the given id.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `adr_base_dir() -> 'Path'`

Return the configured ADR base directory, without creating it.

Reads :data:`ADR_DIR_ENV_VAR` from the environment, falling back to
:data:`DEFAULT_ADR_DIR`. Read-only tools (``get_adr``, ``option_list``,
...) use this so merely reading never has the side effect of creating
the directory -- see :func:`ensure_adr_base_dir` for the write path.


### `ensure_adr_base_dir() -> 'Path'`

Return the configured ADR base directory, creating it if missing.

Only ``create_adr`` (``tools.py``) calls this -- every other tool uses
the read-only :func:`adr_base_dir` instead.


### `find_adr_path(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve an ``id`` to its on-disk file path (plan §9a).

Scans every ``*.md`` file under ``base_dir``, parsing each and
comparing ``frontmatter.id`` against ``id_``. A file that fails to
parse (:class:`AdrParseError` or ``pydantic.ValidationError``) is
silently skipped -- one broken file must not prevent lookup of a
different, valid id.

Raises
------
AdrNotFoundError
    If no file's ``frontmatter.id`` matches ``id_``.


### `iter_adr_paths(base_dir: 'Path') -> 'Iterator[Path]'`

Yield every ``*.md`` file directly under ``base_dir``, sorted by name.

Yields nothing (rather than raising) if ``base_dir`` does not exist.


### `slugify(title: 'str') -> 'str'`

Derive a filename-safe slug from an ADR title (plan §9a).

Lowercases ``title``, collapses every run of non-``[a-z0-9]``
characters into a single ``-``, strips leading/trailing ``-``,
truncates to :data:`_SLUG_MAX_LENGTH` characters (stripping a trailing
``-`` again in case the truncation lands mid-run), and falls back to
``"adr"`` if the result would otherwise be empty (e.g. a title with no
alphanumeric characters at all).

