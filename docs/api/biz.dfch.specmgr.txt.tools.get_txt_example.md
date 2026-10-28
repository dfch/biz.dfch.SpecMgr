# `biz.dfch.specmgr.txt.tools.get_txt_example`

``@mcp.tool()`` wrapper: get_txt_example (feat-229-txt Phase 110).

Returns a complete, valid sample free-form text document as raw markdown
-- useful as a learning example for drafting a new TXT document by hand, or
for an LLM to see the expected shape without re-deriving it from the JSON
Schema alone. Named ``get_txt_example`` rather than the bare
``get_example`` since tool names are global across the whole MCP server --
domain-qualifying it now avoids a future collision.

## Functions

### `get_txt_example() -> 'str'`

Return the packaged TXT example's full markdown text, verbatim.

The example file is shipped as package data, so its presence is a
build-time guarantee, not something that can be missing at runtime in a
correctly installed package (the ``pyproject.toml`` package-data
declaration lands with the domain's Phase 160 build registration).
Reads the file fresh on every call (no in-memory cache). A missing or
corrupted packaged file is not caught or wrapped here -- it propagates
as a hard :class:`FileNotFoundError`, the same let-it-raise convention
every other tool/resource in this codebase follows.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

