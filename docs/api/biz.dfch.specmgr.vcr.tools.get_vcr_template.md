# `biz.dfch.specmgr.vcr.tools.get_vcr_template`

``@mcp.tool()`` wrapper: get_vcr_template (Task 2.1).

Returns a verification case record document with every field present,
populated with short placeholder ("blind text") content -- a structural
authoring aid for drafting a new VCR document by hand, distinct from
``get_vcr_example``, which returns a complete, *valid* sample document.
Named ``get_vcr_template`` rather than the bare ``get_template``, mirroring
``get_vcr_example``'s own domain-qualified naming rationale -- tool names
are global across the whole MCP server.

## Functions

### `get_vcr_template() -> 'str'`

Return the packaged VCR template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_vcr_example``, the returned text is **not** guaranteed to
satisfy ``parse_vcr``/``VcrDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

