# `biz.dfch.specmgr.sysrs.tools.get_sysrs_example`

``@mcp.tool()`` wrapper: get_sysrs_example (Task 3.2).

Returns a complete, valid sample System Requirements Specification document
as raw markdown -- useful as a learning example for drafting a new SYSRS
document by hand, or for an LLM to see the expected shape without
re-deriving it from the JSON Schema alone. Named ``get_sysrs_example``
rather than the bare ``get_example`` since tool names are global across the
whole MCP server -- domain-qualifying it now avoids a future collision.

The packaged ``sysrs_example.md`` data file itself does not exist yet as of
this phase (Phase 3) -- it arrives in Phase 4 (``sysrs/data/``); calling this
tool before then raises ``FileNotFoundError``, the same let-it-raise
convention every other tool/resource in this codebase follows for a missing
packaged file.

## Functions

### `get_sysrs_example() -> 'str'`

Return the packaged SYSRS example's full markdown text, verbatim.

The example file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

