# `biz.dfch.specmgr.vcr.tools._io`

Thin file read helpers over ``parse_vcr`` (Task 2.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_vcr``/``render_vcr`` counterpart here, since ``create_vcr``
and the generic ``update`` tool in ``general.tools`` persist the caller's
own already-validated body markdown byte-for-byte rather than rendering it
back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``dec.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, VcrDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching verification case record.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, VcrDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
VcrNotFoundError
    If no file matches (propagated from :func:`._paths.find_vcr_path`).


### `read_vcr(path: 'Path') -> 'VcrDocument'`

Read and parse the verification case record at ``path``.

Parameters
----------
path:
    The filesystem path to the verification case record ``.md`` file.

Returns
-------
VcrDocument
    The parsed, validated document.

