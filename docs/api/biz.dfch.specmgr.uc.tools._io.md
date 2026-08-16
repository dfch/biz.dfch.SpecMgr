# `biz.dfch.specmgr.uc.tools._io`

Thin file read helpers over ``parse_uc`` (Task 3.1.5).

Read-only, mirroring ``req.tools._io`` exactly: there is no
``write_uc``/``render_uc`` counterpart here, since ``create_uc``/``update_uc``
persist the caller's already-validated body markdown byte-for-byte rather
than rendering it back out from a parsed model -- no renderer is needed for
that shape, so none is added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

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
    If no file matches (propagated from :func:`._paths.find_uc_path`).


### `read_uc(path: 'Path') -> 'UcDocument'`

Read and parse the use case at ``path``.

Parameters
----------
path:
    The filesystem path to the use-case ``.md`` file.

Returns
-------
UcDocument
    The parsed, validated document.

