# `biz.dfch.specmgr.prb.tools.get_prb_example`

``@mcp.tool()`` wrapper: get_prb_example (Task 3.10).

Returns a complete, valid sample problem statement document as raw markdown
-- useful as a learning example for drafting a new PRB document by hand, or
for an LLM to see the expected shape without re-deriving it from the JSON
Schema alone. Named ``get_prb_example`` rather than a bare ``get_example``,
mirroring ``get_tsk_example``/``get_qa_example``'s own domain-qualified
naming rationale -- tool names are global across the whole MCP server.

## Functions

### `get_prb_example() -> 'str'`

Return the packaged PRB example's full markdown text, verbatim.

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

