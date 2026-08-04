# `biz.dfch.specmgr.adr.tools._io`

Thin file read/write helpers over ``parse_adr``/``render_adr`` (plan §7, §9a).

No ``mcp`` dependency here either -- these are plain file-I/O adapters,
kept separate from the ``@mcp.tool()``-decorated functions in ``tools.py``
so they stay independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, Adr]'`

Resolve ``id_`` under ``base_dir`` and read the matching ADR.

Raises :class:`._paths.AdrNotFoundError` if no file matches.

Returns
-------
tuple[Path, Adr]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.


### `read_adr(path: 'Path') -> 'Adr'`

Read and parse the ADR at ``path`` (plan §7's "re-read, re-parse").


### `write_adr(path: 'Path', adr: 'Adr') -> 'None'`

Render ``adr`` and write it to ``path`` (plan §7's "re-render, re-write").

