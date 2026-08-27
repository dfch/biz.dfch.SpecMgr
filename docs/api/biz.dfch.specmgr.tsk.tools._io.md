# `biz.dfch.specmgr.tsk.tools._io`

Thin file read helpers over ``parse_tsk`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_tsk``/``render_tsk`` counterpart here, since ``create_tsk``
and the generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.
Mirrors ``req.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, TskDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching task list.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, TskDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
TskNotFoundError
    If no file matches (propagated from :func:`._paths.find_tsk_path`).


### `read_tsk(path: 'Path') -> 'TskDocument'`

Read and parse the task list at ``path``.

Parameters
----------
path:
    The filesystem path to the task list ``.md`` file.

Returns
-------
TskDocument
    The parsed, validated document.

