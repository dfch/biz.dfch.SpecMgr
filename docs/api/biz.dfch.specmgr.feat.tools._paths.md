# `biz.dfch.specmgr.feat.tools._paths`

Feature (FEAT) base directory resolution and id -> path lookup (Task 2.1).

**Hand-rolled, ADR-style** (mirrors ``adr.tools._paths``), deliberately
**not** built on the shared, flat-file ``general.tools._doc_paths`` --
that module assumes one file per document directly under the base
directory (``<base>/<type>-<uuid>-<slug>.md``); ``feat`` is folder-per-
document instead (``<base>/<id>/README.md``, a fixed filename), and
``id`` is a chosen ``feat-NNN-slug`` string, not a server-generated UUID.
See ``.specmgr/feat/feat-31-feature/README.md`` Design Notes
("Addressing") for the full rationale.

Mirrors ``adr.tools._paths``'s read-only/write split: :func:`feat_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_feat_base_dir` does, for ``create_feat``. There
is deliberately no in-memory id -> path cache either -- every lookup
re-reads whatever is currently on disk, matching this codebase's "the
on-disk file is the sole source of truth" design.

**The key behavioral divergence from every other (UUID-addressed) domain**:
since ``id`` *is* the containing folder's own name by convention (REQ-004),
:func:`find_feat_path_by_id` shortcuts directly to ``<base>/<id_>/README.md``
instead of scanning every document under the base directory and comparing
each one's parsed ``frontmatter.id`` -- there is no directory scan, and
therefore no partial-id-match support either (a bare ``"feat-31"`` never
resolves to ``"feat-31-feature"``; see this feature's own Decisions Made log
for why that was considered and explicitly rejected).

**Parse-failure handling on the shortcut read.** Every other domain's
``find_*_path`` scans multiple files and *skips* a file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) so one broken file never
blocks lookup of a different, valid id -- there is no "different file" to
fall back to here, since the shortcut only ever reads one path. A parse
failure on that single target file is therefore treated the same as the
file not existing at all: both raise :class:`FeatNotFoundError`, just with
a message that distinguishes "the folder/file is missing" from "the folder
exists but its content is unparseable, or its frontmatter ``id`` does not
match the folder name it lives in" -- so ``load_by_id``/``get_feat``/every
mutating tool built on this module gets one single, consistent
not-found-shaped error to handle, without needing to separately catch
``AssertionError``/``ValidationError`` themselves.

## Classes

### `FeatNotFoundError`

No feature folder/document found matching the given id.

Raised both when ``<base>/<id_>/README.md`` does not exist at all, and
when it exists but fails to parse or its frontmatter ``id`` does not
match the folder name it was found under -- see this module's own
docstring for why both cases collapse to the same exception type here.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `ensure_feat_base_dir() -> 'Path'`

Return the configured feature base directory, creating it if missing.

Only ``create_feat`` should call this -- every other tool uses the
read-only :func:`feat_base_dir` instead.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist feature base directory.


### `feat_base_dir() -> 'Path'`

Return the configured feature base directory, without creating it.

Reads :data:`FEAT_DIR_ENV_VAR` from the environment, falling back to
:data:`DEFAULT_FEAT_DIR`. Read-only tools (``get_feat``, ``list_feat``,
...) use this so merely reading never has the side effect of creating
the directory -- see :func:`ensure_feat_base_dir` for the write path.

Returns
-------
Path
    The resolved feature base directory.


### `feature_title(text: 'str') -> 'str'`

Strip the literal ``"Feature: "`` prefix off a ``Feature.text`` heading value.

Parameters
----------
text:
    A ``Feature.text`` value, e.g. ``"Feature: My Title"``.

Returns
-------
str
    ``text`` with the literal ``"Feature: "`` prefix removed, if
    present (it always is for any ``Feature`` that parsed
    successfully, since the prefix is enforced by `Feature`'s own
    ``@alias`` regex) -- returned unchanged otherwise.


### `find_feat_path_by_id(base_dir: 'Path', id_: 'str') -> 'Path'`

Resolve ``id_`` to its on-disk ``README.md`` path under ``base_dir``.

Shortcuts directly to ``<base_dir>/<id_>/README.md`` -- since ``id`` is,
by REQ-004's addressing convention, the containing folder's own name,
there is no need (and deliberately no support) for a full directory
scan or partial-id matching (see this module's own docstring).

Parameters
----------
base_dir:
    The feature base directory (typically :func:`feat_base_dir`'s
    return value).
id_:
    The id to look up -- must be the *exact* folder name, e.g.
    ``"feat-31-feature"``, not a bare ``"feat-31"`` prefix.

Returns
-------
Path
    The resolved ``README.md`` path.

Raises
------
FeatNotFoundError
    If ``<base_dir>/<id_>/README.md`` does not exist, if it exists but
    fails to parse (``AssertionError``/``pydantic.ValidationError``),
    or if it parses but its frontmatter ``id`` does not match ``id_``
    (a folder/frontmatter mismatch, surfaced rather than silently
    worked around).


### `iter_feat_paths(base_dir: 'Path') -> 'Iterator[Path]'`

Yield every ``<base_dir>/*/README.md`` path, sorted by folder name.

Unlike every generic-``_doc_paths``-based domain's ``iter_*_paths``
(which globs ``*.md`` directly under the base directory), this globs
one level deeper -- ``*/README.md`` -- since ``feat`` is folder-per-
document, not flat-file. Yields nothing (rather than raising) if
``base_dir`` does not exist.

Parameters
----------
base_dir:
    The feature base directory to scan (typically :func:`feat_base_dir`'s
    return value).

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.

