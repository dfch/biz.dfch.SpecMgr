# `biz.dfch.specmgr.uc.tools._io`

Thin file read helpers over ``parse_uc`` (feat-107-doc-cache Phase 4).

Read-only, mirroring ``req.tools._io`` exactly: there is no
``write_uc``/``render_uc`` counterpart here, since ``create_uc`` and the
generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_uc`` itself now lives in ``._cache`` (feat-107-doc-cache Phase 4) --
it is re-exported here unchanged (same name, same signature) so every
existing external caller (e.g. ``uc.tools.list_uc``'s
``from ._io import read_uc``) keeps working with zero changes to its own
import line. See ``._cache``'s module docstring for why ``read_uc`` had to
move out of this module in the first place (avoiding a circular import
between ``_io.py`` and ``_paths.py``) and for the module-level cache
singleton it now reads through.

**The second, independent ``read_uc`` call is also guarded against a
vanished file (feat-107-doc-cache Phase 8, REQ-015).** :func:`load_by_id`
calls ``read_uc(path)`` again immediately after ``find_uc_path`` already
resolved and read the same ``path`` once during its own scan. The generic
``delete`` tool in ``general.tools`` only holds the *target* document's own
per-id lock, never a whole-domain lock, while ``get_uc``/``list_uc``
intentionally take no lock at all (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3) -- so a concurrent ``delete`` of this
same document can remove ``path`` in the narrow window between
``find_uc_path``'s own read and this one, raising ``FileNotFoundError``.
This mirrors ``feat.tools._io.load_by_id``'s already-shipped shape exactly
(the identical race, closed there in Phase 6 for REQ-012's narrower,
rename-only claim): ``AssertionError``/``pydantic.ValidationError``/
``yaml.YAMLError``/``FileNotFoundError`` around this second read are all
translated into :class:`._paths.UcNotFoundError` here, rather than left to
propagate uncaught.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, UcDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching use case.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, UcDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
UcNotFoundError
    If no file matches (propagated from :func:`._paths.find_uc_path`),
    or if ``path`` -- already resolved successfully by
    :func:`._paths.find_uc_path` an instant earlier -- fails this
    function's own second, independent :func:`._cache.read_uc` call
    (``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``/
    ``FileNotFoundError``, feat-107-doc-cache Phase 8, REQ-015 -- e.g. a
    concurrent ``delete`` tool call racing this lock-free read, the
    same race class ``feat.tools._io.load_by_id`` already guards
    against).

