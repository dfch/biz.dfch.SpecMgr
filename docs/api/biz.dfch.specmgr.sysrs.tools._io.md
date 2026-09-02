# `biz.dfch.specmgr.sysrs.tools._io`

Thin file read helpers over ``parse_sysrs`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_sysrs``/``render_sysrs`` counterpart here, since ``create_sysrs``
and the generic ``update`` tool in ``general.tools`` persist the caller's
own already-validated body markdown byte-for-byte rather than rendering it
back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``vcr.tools._io``/``dec.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, SysrsDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching System Requirements Specification.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, SysrsDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
SysrsNotFoundError
    If no file matches (propagated from :func:`._paths.find_sysrs_path`).


### `read_sysrs(path: 'Path') -> 'SysrsDocument'`

Read and parse the System Requirements Specification at ``path``.

Parameters
----------
path:
    The filesystem path to the System Requirements Specification ``.md`` file.

Returns
-------
SysrsDocument
    The parsed, validated document.

