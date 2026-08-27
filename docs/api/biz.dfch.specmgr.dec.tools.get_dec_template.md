# `biz.dfch.specmgr.dec.tools.get_dec_template`

``@mcp.tool()`` wrapper: get_dec_template (Task 2.2).

Returns a decision document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new DEC document by hand, distinct from ``get_dec_example``, which returns
a complete, *valid* sample document. Named ``get_dec_template`` rather than
the bare ``get_template``, mirroring ``get_dec_example``'s own
domain-qualified naming rationale -- tool names are global across the whole
MCP server.

## Functions

### `get_dec_template() -> 'str'`

Return the packaged DEC template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_dec_example``, the returned text is **not** guaranteed to
satisfy ``parse_dec``/``DecDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

