# `biz.dfch.specmgr.gol.tools._io`

Thin file read helpers over ``parse_gol`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_gol``/``render_gol`` counterpart here, since ``create_gol``
and the generic ``update`` tool in ``general.tools`` persist the caller's
own already-validated body markdown byte-for-byte rather than rendering it
back out from a parsed model -- no renderer is needed for that shape, so
none is added speculatively here.
Mirrors ``prb.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, GolDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching goal.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, GolDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
GolNotFoundError
    If no file matches (propagated from :func:`._paths.find_gol_path`).


### `read_gol(path: 'Path') -> 'GolDocument'`

Read and parse the goal at ``path``.

Parameters
----------
path:
    The filesystem path to the goal ``.md`` file.

Returns
-------
GolDocument
    The parsed, validated document.

