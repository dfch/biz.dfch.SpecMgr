# `biz.dfch.specmgr.rsk.tools._io`

Thin file read helpers over ``parse_rsk`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_rsk``/``render_rsk`` counterpart here, since ``create_rsk``
and the generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.
Mirrors ``tsk.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, RskDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching risk.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, RskDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
RskNotFoundError
    If no file matches (propagated from :func:`._paths.find_rsk_path`).


### `read_rsk(path: 'Path') -> 'RskDocument'`

Read and parse the risk at ``path``.

Parameters
----------
path:
    The filesystem path to the risk ``.md`` file.

Returns
-------
RskDocument
    The parsed, validated document.

