# `biz.dfch.specmgr.sysrs.tools.get_sysrs_template`

``@mcp.tool()`` wrapper: get_sysrs_template (Task 3.2).

Returns a System Requirements Specification document with every field
present, populated with short placeholder ("blind text") content -- a
structural authoring aid for drafting a new SYSRS document by hand, distinct
from ``get_sysrs_example``, which returns a complete, *valid* sample
document. Named ``get_sysrs_template`` rather than the bare ``get_template``,
mirroring ``get_sysrs_example``'s own domain-qualified naming rationale --
tool names are global across the whole MCP server.

The packaged ``sysrs_template.md`` data file itself does not exist yet as of
this phase (Phase 3) -- it arrives in Phase 4 (``sysrs/data/``); calling
this tool before then raises ``FileNotFoundError``, the same let-it-raise
convention every other tool/resource in this codebase follows for a missing
packaged file.

## Functions

### `get_sysrs_template() -> 'str'`

Return the packaged SYSRS template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_sysrs_example``, the returned text is **not** guaranteed to
satisfy ``parse_sysrs``/``SysrsDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

