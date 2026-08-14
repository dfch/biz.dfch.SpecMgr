# `biz.dfch.specmgr.req.tools._io`

Thin file read helpers over ``parse_req`` (Task 3.11).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_req``/``render_req`` counterpart here, since Task 3.9's design
settled on ``create_req``/``update_req`` (Tasks 3.12/3.13) persisting the
caller's already-validated body markdown byte-for-byte rather than rendering
it back out from a parsed model -- no renderer is needed for that shape, so
none is added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

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


### `read_req(path: 'Path') -> 'ReqDocument'`

Read and parse the requirement at ``path``.

Parameters
----------
path:
    The filesystem path to the requirement ``.md`` file.

Returns
-------
ReqDocument
    The parsed, validated document.

