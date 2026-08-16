# `biz.dfch.specmgr.tsk.tools.get_tsk_template`

``@mcp.tool()`` wrapper: get_tsk_template (Task 3.9).

Returns a TSK document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new TSK document by hand, distinct from ``get_tsk_example``, which returns a
complete, *valid* sample document. Named ``get_tsk_template`` rather than a
bare ``get_template``, mirroring ``get_req_template``'s own domain-qualified
naming rationale -- tool names are global across the whole MCP server.

## Functions

### `get_tsk_template() -> 'str'`

Return the packaged TSK template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_tsk_example``, the returned text is **not** guaranteed to
satisfy every field-level validator beyond structure -- this is a
structural authoring aid, not a valid document instance. It does,
however, include a placeholder ``### Created`` entry under
``## Recent Updates`` so it stays a useful starting point given that
section's ``min_length=1`` requirement.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

