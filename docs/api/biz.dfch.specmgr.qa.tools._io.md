# `biz.dfch.specmgr.qa.tools._io`

Thin file read helpers over ``parse_qa`` (feat-107-doc-cache Phase 4).

Read-only, mirroring ``req.tools._io`` exactly: there is no
``write_qa``/``render_qa`` counterpart here, since ``create_qa`` and the
generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_qa`` itself now lives in ``._cache`` (feat-107-doc-cache Phase 4) --
it is re-exported here unchanged (same name, same signature) so every
existing external caller (e.g. ``qa.tools.list_qa``'s
``from ._io import read_qa``) keeps working with zero changes to its own
import line. See ``._cache``'s module docstring for why ``read_qa`` had to
move out of this module in the first place (avoiding a circular import
between ``_io.py`` and ``_paths.py``) and for the module-level cache
singleton it now reads through.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, QaDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching QA document.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, QaDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
QaNotFoundError
    If no file matches (propagated from :func:`._paths.find_qa_path`).

