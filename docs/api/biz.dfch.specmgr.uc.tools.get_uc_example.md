# `biz.dfch.specmgr.uc.tools.get_uc_example`

``@mcp.tool()`` wrapper: get_uc_example (Task 3.1.2).

Returns a complete, valid sample use-case document as raw markdown -- useful
as a learning example for drafting a new UC document by hand, or for an LLM
to see the expected shape without re-deriving it from the JSON Schema alone.
Mirrors ``req.tools.get_req_example``.

## Functions

### `get_uc_example() -> 'str'`

Return the packaged UC example's full markdown text, verbatim.

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

