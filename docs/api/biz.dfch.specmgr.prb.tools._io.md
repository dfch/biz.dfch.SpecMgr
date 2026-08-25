# `biz.dfch.specmgr.prb.tools._io`

Thin file read helpers over ``parse_prb`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_prb``/``render_prb`` counterpart here, since ``create_prb``/
``update_prb`` persist the caller's own already-validated body markdown
byte-for-byte rather than rendering it back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``tsk.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, PrbDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching problem statement.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, PrbDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
PrbNotFoundError
    If no file matches (propagated from :func:`._paths.find_prb_path`).


### `read_prb(path: 'Path') -> 'PrbDocument'`

Read and parse the problem statement at ``path``.

Parameters
----------
path:
    The filesystem path to the problem statement ``.md`` file.

Returns
-------
PrbDocument
    The parsed, validated document.

