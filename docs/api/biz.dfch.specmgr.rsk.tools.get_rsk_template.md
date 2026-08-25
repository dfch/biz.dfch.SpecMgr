# `biz.dfch.specmgr.rsk.tools.get_rsk_template`

``@mcp.tool()`` wrapper: get_rsk_template (Task 3.9).

Returns a RSK document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new RSK document by hand, distinct from ``get_rsk_example``, which returns
a complete, *valid* sample document. Named ``get_rsk_template`` rather than a
bare ``get_template``, mirroring ``get_tsk_template``'s own domain-qualified
naming rationale -- tool names are global across the whole MCP server.

## Functions

### `get_rsk_template() -> 'str'`

Return the packaged RSK template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_rsk_example``, the returned text is a structural authoring
aid rather than a valid document instance in its own right -- though the
packaged template does round-trip through ``parse_rsk`` unchanged (it
carries every mandatory section, both 5x5 assessments, and a valid TARA
strategy word).

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

