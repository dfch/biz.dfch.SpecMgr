# `biz.dfch.specmgr.txt.tools.get_txt_template`

``@mcp.tool()`` wrapper: get_txt_template (feat-229-txt Phase 110).

Returns a free-form text document with every field present, populated with
short placeholder ("blind text") content -- a structural authoring aid for
drafting a new TXT document by hand, distinct from ``get_txt_example``,
which returns a complete, *valid* sample document. Named
``get_txt_template`` rather than the bare ``get_template``, mirroring
``get_txt_example``'s own domain-qualified naming rationale -- tool names
are global across the whole MCP server.

## Functions

### `get_txt_template() -> 'str'`

Return the packaged TXT template's full markdown text, verbatim.

The template file is shipped as package data, so its presence is a
build-time guarantee, not something that can be missing at runtime in a
correctly installed package (the ``pyproject.toml`` package-data
declaration lands with the domain's Phase 160 build registration).
Reads the file fresh on every call (no in-memory cache). A missing or
corrupted packaged file is not caught or wrapped here -- it propagates
as a hard :class:`FileNotFoundError`, the same let-it-raise convention
every other tool/resource in this codebase follows.

Unlike ``get_txt_example``, the returned text is **not** guaranteed to
satisfy ``parse_txt``/``TxtDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

