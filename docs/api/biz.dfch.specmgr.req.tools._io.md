# `biz.dfch.specmgr.req.tools._io`

Thin file read helpers over ``parse_req`` (Task 3.11).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_req``/``render_req`` counterpart here, since Task 3.9's design
settled on ``create_req`` and the generic ``update`` tool in ``general.tools``
persisting the caller's already-validated body markdown byte-for-byte rather
than rendering it back out from a parsed model -- no renderer is needed for
that shape, so none is added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_req`` itself now lives in ``._cache`` (feat-107-doc-cache Phase 3) --
it is re-exported here unchanged (same name, same signature) so every
existing external caller (e.g. ``req.tools.list_req``'s
``from ._io import read_req``) keeps working with zero changes to its own
import line. See ``._cache``'s module docstring for why ``read_req`` had to
move out of this module in the first place (avoiding a circular import
between ``_io.py`` and ``_paths.py``) and for the module-level cache
singleton it now reads through.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, ReqDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching requirement.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, ReqDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
ReqNotFoundError
    If no file matches (propagated from :func:`._paths.find_req_path`).

