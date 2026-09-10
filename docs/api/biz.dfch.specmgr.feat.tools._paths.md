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
effect), only :func:`ensure_feat_base_dir` does, for ``create_feat``.

**Cache-backed single-file read (feat-107-doc-cache Phase 4, Task 4.1a).**
:func:`find_feat_path_by_id` reads its single target file through the
content-hash-validated ``feat`` cache (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d)
via ``._cache``'s own ``read_feat`` (not ``parse_feat`` directly) -- a file
whose on-disk content hash is unchanged since its last read is not
re-parsed. This also fixes the same double-parse bug every other domain's
``find_<domain>_path`` had: without it, ``load_by_id`` would parse this
single file once here (to validate its frontmatter id) and again via
``read_feat`` right after. There is no directory scan here to reconcile a
cache against (unlike every other domain's ``find_<domain>_path``) -- see
this module's own docstring above for why: the shortcut-only lookup never
scans, so :func:`~._cache.reconcile_feat_cache` is instead called from
``list_feat``, the one place that does scan.

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

**A concurrent, lock-free read racing ``set_feat_id``'s rename is also
treated as not-found (feat-107-doc-cache Phase 6, REQ-012).** ``get_feat``/
``list_feat`` intentionally take no domain lock (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3), so a call landing in the narrow
window after ``set_feat_id``'s ``old_path.parent.rename(new_path.parent)``
succeeds but before its cache-entry move runs would otherwise see
``old_path`` genuinely absent from disk mid-read -- the earlier
``path.exists()`` check above can pass and then the file can vanish before
the cache-backed :func:`~._cache.read_feat` call's own internal read
completes, raising a plain ``FileNotFoundError`` that is not one of
``DocCache``'s own ``CACHEABLE_ERROR_TYPES`` and therefore, before this fix,
propagated uncaught instead of resolving to the same not-found-shaped error
every other parse failure already produces. ``FileNotFoundError`` is now
caught alongside ``AssertionError``/``ValidationError`` around that
``read_feat`` call, below, and translated into the same
:class:`FeatNotFoundError` -- a reader racing the rename this way now sees
a graceful "not found" instead of an uncaught, unrelated-looking OS error.

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
    if it vanishes out from under a concurrent, lock-free read racing
    ``set_feat_id``'s rename (``FileNotFoundError``, feat-107-doc-cache
    Phase 6, REQ-012 -- see this module's own docstring), or if it
    parses but its frontmatter ``id`` does not match ``id_`` (a
    folder/frontmatter mismatch, surfaced rather than silently worked
    around).


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

