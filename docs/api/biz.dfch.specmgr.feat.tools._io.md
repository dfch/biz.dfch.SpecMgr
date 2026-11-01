# `biz.dfch.specmgr.feat.tools._io`

Thin file read helpers over ``parse_feat`` (Task 2.2).

Read-only, mirroring ``dec.tools._io``'s own shape and rationale: there is
no ``write_feat``/``render_feat`` counterpart here, since ``create_feat``
and the generic ``update`` tool in ``general.tools`` (``type="feat"``)
persist the caller's own already-validated body markdown byte-for-byte
rather than rendering it back out from a parsed model -- see
``feat.tools._write.write_feat_file``.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_feat`` itself now lives in ``._cache`` (feat-107-doc-cache Phase 4,
Task 4.1a) -- it is re-exported here unchanged (same name, same signature)
so every existing external caller (e.g. ``feat.tools.list_feat``'s
``from ._io import read_feat``) keeps working with zero changes to its own
import line. See ``._cache``'s module docstring for why ``read_feat`` had
to move out of this module in the first place (avoiding a circular import
between ``_io.py`` and ``_paths.py``) and for the module-level cache
singleton it now reads through.

**Malformed frontmatter YAML is also skipped, not left to crash uncaught
(feat-107-doc-cache Phase 7, REQ-013).** :func:`load_by_id`'s own second,
independent ``read_feat(path)`` call now also catches ``yaml.YAMLError``
alongside ``AssertionError``/``ValidationError``/``FileNotFoundError`` and
translates it into the same :class:`._paths.FeatNotFoundError` --
consistency/defense-in-depth with :func:`._paths.find_feat_path_by_id`'s
own identical fix, even though this call site is currently moot in
practice since ``find_feat_path_by_id`` already raises first on the shared
cache-backed read.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, FeatDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching feature document.

Parameters
----------
base_dir:
    The feature base directory (typically :func:`._paths.feat_base_dir`'s
    return value).
id_:
    The id to look up.

Returns
-------
tuple[Path, FeatDocument]
    The resolved ``README.md`` path and the parsed document -- callers
    that mutate the document need the path to write it back afterward.

Raises
------
FeatNotFoundError
    If no folder matches (propagated from :func:`._paths.find_feat_path_by_id`),
    if ``path`` -- already resolved successfully by
    :func:`._paths.find_feat_path_by_id` an instant earlier -- vanishes
    out from under this function's own subsequent :func:`._cache.read_feat`
    call, racing a concurrent ``set_feat_id`` rename in the same narrow
    window :func:`._paths.find_feat_path_by_id`'s own docstring describes
    (feat-107-doc-cache Phase 6, REQ-012): this second, independent read
    has exactly the same ``FileNotFoundError`` exposure as the first one
    does, and is translated into the same :class:`._paths.FeatNotFoundError`
    here rather than left to propagate uncaught; or if this second read
    raises ``yaml.YAMLError`` for malformed frontmatter YAML
    (feat-107-doc-cache Phase 7, REQ-013 -- consistency/defense-in-depth
    with :func:`._paths.find_feat_path_by_id`'s own identical fix, even
    though this call site is currently moot in practice since
    ``find_feat_path_by_id`` already raises first on the shared
    cache-backed read).

