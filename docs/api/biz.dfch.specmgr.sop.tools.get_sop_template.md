# `biz.dfch.specmgr.sop.tools.get_sop_template`

``@mcp.tool()`` wrapper: get_sop_template (Task 2.2).

Returns a SOP document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new SOP document by hand, distinct from ``get_sop_example``, which returns
a complete, *valid* sample document. Named ``get_sop_template`` rather than
the bare ``get_template``, mirroring ``get_sop_example``'s own
domain-qualified naming rationale -- tool names are global across the whole
MCP server.

The packaged template data file (``sop/data/sop_template.md``) is created in
Phase 3 (Task 3.2); until then this tool registers fine (``read_packaged_text``
is called at call time, not import time) but raises ``FileNotFoundError`` if
invoked against the not-yet-present data file.

## Functions

### `get_sop_template() -> 'str'`

Return the packaged SOP template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_sop_example``, the returned text is **not** guaranteed to
satisfy ``parse_sop``/``SopDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

