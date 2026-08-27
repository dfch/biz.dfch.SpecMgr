# `biz.dfch.specmgr.qa.tools._io`

Thin file read helpers over ``parse_qa`` (Phase 4, Task 4.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_qa``/``render_qa`` counterpart here, since ``create_qa`` and
the generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here. 1:1 port of ``req.tools._io``.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, QaDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching QA document.

Parameters
----------
base_dir:
    The directory to scan for ``*.md`` files.
id_:
    The id to look up.

Returns
-------
tuple[Path, QaDocument]
    The resolved file path and the parsed document -- callers that
    mutate the document need the path to write it back afterward.

Raises
------
QaNotFoundError
    If no file matches (propagated from :func:`._paths.find_qa_path`).


### `read_qa(path: 'Path') -> 'QaDocument'`

Read and parse the Question and Answer (QA) document at ``path``.

Parameters
----------
path:
    The filesystem path to the QA ``.md`` file.

Returns
-------
QaDocument
    The parsed, validated document.

