# `biz.dfch.specmgr.feat.tools._io`

Thin file read helpers over ``parse_feat`` (Task 2.2).

Read-only, mirroring ``dec.tools._io``'s own shape and rationale: there is
no ``write_feat``/``render_feat`` counterpart here, since ``create_feat``
and the generic ``update`` tool in ``general.tools`` (``type="feat"``)
persist the caller's own already-validated body markdown byte-for-byte
rather than rendering it back out from a parsed model -- see
``feat.tools._write.write_feat_file``.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any ``@mcp.tool()``-decorated function so they stay
independently testable.

## Functions

### `load_by_id(base_dir: 'Path', id_: 'str') -> 'tuple[Path, FeatDocument]'`

Resolve ``id_`` under ``base_dir`` and read the matching feature document.

Parameters
----------
base_dir:
    The feature base directory (typically :func:`._paths.feat_base_dir`'s
    return value).
id_:
    The id to look up.

Returns
-------
tuple[Path, FeatDocument]
    The resolved ``README.md`` path and the parsed document -- callers
    that mutate the document need the path to write it back afterward.

Raises
------
FeatNotFoundError
    If no folder matches (propagated from :func:`._paths.find_feat_path_by_id`).


### `read_feat(path: 'Path') -> 'FeatDocument'`

Read and parse the feature document at ``path``.

Parameters
----------
path:
    The filesystem path to the feature's ``README.md`` file.

Returns
-------
FeatDocument
    The parsed, validated document.

