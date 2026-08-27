# `biz.dfch.specmgr.dec.tools._io`

Thin file read helpers over ``parse_dec`` (Task 2.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_dec``/``render_dec`` counterpart here, since ``create_dec``
and the generic ``update`` tool in ``general.tools`` persist the caller's
own already-validated body markdown byte-for-byte rather than rendering it
back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``gol.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, DecDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching decision.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, DecDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
DecNotFoundError
    If no file matches (propagated from :func:`._paths.find_dec_path`).


### `read_dec(path: 'Path') -> 'DecDocument'`

Read and parse the decision at ``path``.

Parameters
----------
path:
    The filesystem path to the decision ``.md`` file.

Returns
-------
DecDocument
    The parsed, validated document.

