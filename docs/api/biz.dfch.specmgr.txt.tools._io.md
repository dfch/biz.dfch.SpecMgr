# `biz.dfch.specmgr.txt.tools._io`

Thin file read helpers over ``parse_txt`` (feat-229-txt Phase 110).

Read-only, mirroring ``vcr.tools._io`` exactly: there is no
``write_txt``/``render_txt`` counterpart here, since ``create_txt`` and the
generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_txt`` itself now lives in ``._cache`` -- it is re-exported here
unchanged (same name, same signature) so every existing external caller
(e.g. ``txt.tools.list_txt``'s ``from ._io import read_txt``) keeps working
with zero changes to its own import line. See ``._cache``'s module
docstring for why ``read_txt`` had to move out of this module in the first
place (avoiding a circular import between ``_io.py`` and ``_paths.py``) and
for the module-level cache singleton it now reads through.

**The second, independent ``read_txt`` call is also guarded against a
vanished file (feat-107-doc-cache Phase 8, REQ-015 shape, repeated here).**
:func:`load_by_id` calls ``read_txt(path)`` again immediately after
``find_txt_path`` already resolved and read the same ``path`` once during
its own scan. The generic ``delete`` tool in ``general.tools`` only holds
the *target* document's own per-id lock, never a whole-domain lock, while
``get_txt``/``list_txt`` intentionally take no lock at all (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3) -- so a concurrent ``delete`` of this
same document can remove ``path`` in the narrow window between
``find_txt_path``'s own read and this one, raising ``FileNotFoundError``.
This mirrors ``vcr.tools._io.load_by_id``'s already-shipped shape exactly
(the identical race, closed there in Phase 8):
``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``/
``FileNotFoundError`` around this second read are all translated into
:class:`._paths.TxtNotFoundError` here, rather than left to propagate
uncaught.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, TxtDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching free-form text document.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, TxtDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
TxtNotFoundError
    If no file matches (propagated from :func:`._paths.find_txt_path`),
    or if ``path`` -- already resolved successfully by
    :func:`._paths.find_txt_path` an instant earlier -- fails this
    function's own second, independent :func:`._cache.read_txt` call
    (``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``/
    ``FileNotFoundError`` -- e.g. a concurrent ``delete`` tool call
    racing this lock-free read, the same race class
    ``vcr.tools._io.load_by_id`` guards against).

