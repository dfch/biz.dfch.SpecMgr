# `biz.dfch.specmgr.set.tools._io`

Thin file read helpers over ``parse_set`` (feat-173-req-iso29148-level-set Phase 180).

Read-only, mirroring ``vcr.tools._io`` exactly: there is no
``write_set``/``render_set`` counterpart here, since ``create_set`` and the
generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_set`` itself now lives in ``._cache`` -- it is re-exported here
unchanged (same name, same signature) so every existing external caller
(e.g. ``set.tools.list_set``'s ``from ._io import read_set``) keeps working
with zero changes to its own import line. See ``._cache``'s module
docstring for why ``read_set`` had to move out of this module in the first
place (avoiding a circular import between ``_io.py`` and ``_paths.py``) and
for the module-level cache singleton it now reads through.

**The second, independent ``read_set`` call is also guarded against a
vanished file (feat-107-doc-cache Phase 8, REQ-015 shape, repeated here).**
:func:`load_by_id` calls ``read_set(path)`` again immediately after
``find_set_path`` already resolved and read the same ``path`` once during
its own scan. The generic ``delete`` tool in ``general.tools`` only holds
the *target* document's own per-id lock, never a whole-domain lock, while
``get_set``/``list_set`` intentionally take no lock at all (DEC
33c5ab08-ff58-4c73-8c32-23abaf3838e3) -- so a concurrent ``delete`` of this
same document can remove ``path`` in the narrow window between
``find_set_path``'s own read and this one, raising ``FileNotFoundError``.
This mirrors ``vcr.tools._io.load_by_id``'s already-shipped shape exactly
(the identical race, closed there in Phase 8):
``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``/
``FileNotFoundError`` around this second read are all translated into
:class:`._paths.SetNotFoundError` here, rather than left to propagate
uncaught.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, SetDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching set document.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, SetDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
SetNotFoundError
    If no file matches (propagated from :func:`._paths.find_set_path`),
    or if ``path`` -- already resolved successfully by
    :func:`._paths.find_set_path` an instant earlier -- fails this
    function's own second, independent :func:`._cache.read_set` call
    (``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``/
    ``FileNotFoundError`` -- e.g. a concurrent ``delete`` tool call
    racing this lock-free read, the same race class
    ``vcr.tools._io.load_by_id`` guards against).

