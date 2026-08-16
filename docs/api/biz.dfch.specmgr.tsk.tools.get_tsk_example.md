# `biz.dfch.specmgr.tsk.tools.get_tsk_example`

``@mcp.tool()`` wrapper: get_tsk_example (Task 3.9).

Returns a complete, valid sample task list document as raw markdown --
useful as a learning example for drafting a new TSK document by hand, or for
an LLM to see the expected shape without re-deriving it from the JSON Schema
alone. Named ``get_tsk_example`` rather than a bare ``get_example``, mirroring
``get_req_example``'s own domain-qualified naming rationale -- tool names are
global across the whole MCP server.

## Functions

### `get_tsk_example() -> 'str'`

Return the packaged TSK example's full markdown text, verbatim.

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

