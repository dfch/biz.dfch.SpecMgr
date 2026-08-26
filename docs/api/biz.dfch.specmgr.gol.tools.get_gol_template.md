# `biz.dfch.specmgr.gol.tools.get_gol_template`

``@mcp.tool()`` wrapper: get_gol_template (Task 3.10).

Returns a goal document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new GOL document by hand, distinct from ``get_gol_example`` (Task 3.10),
which returns a complete, *valid* sample document. Named ``get_gol_template``
rather than the bare ``get_template`` (Task 3.10's own wording), mirroring
``get_gol_example``'s own domain-qualified naming rationale -- tool names are
global across the whole MCP server.

## Functions

### `get_gol_template() -> 'str'`

Return the packaged GOL template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_gol_example``, the returned text is **not** guaranteed to
satisfy ``parse_gol``/``GolDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

