# `biz.dfch.specmgr.prb.tools.get_prb_template`

``@mcp.tool()`` wrapper: get_prb_template (Task 3.10).

Returns a PRB document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new PRB document by hand, distinct from ``get_prb_example``, which returns a
complete, *valid* sample document. Named ``get_prb_template`` rather than a
bare ``get_template``, mirroring ``get_tsk_template``/``get_qa_template``'s
own domain-qualified naming rationale -- tool names are global across the
whole MCP server.

## Functions

### `get_prb_template() -> 'str'`

Return the packaged PRB template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_prb_example``, the returned text is **not** guaranteed to
satisfy every field-level validator beyond structure -- this is a
structural authoring aid, not a valid document instance (though it does,
in fact, satisfy every mandatory field here).

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

