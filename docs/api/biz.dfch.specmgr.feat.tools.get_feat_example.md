# `biz.dfch.specmgr.feat.tools.get_feat_example`

``@mcp.tool()`` wrapper: get_feat_example (Task 2.3).

Returns a complete, valid sample feature document as raw markdown -- useful
as a learning example for drafting a new FEAT document by hand, or for an
LLM to see the expected shape without re-deriving it from the JSON Schema
alone. Named ``get_feat_example`` rather than the bare ``get_example``,
mirroring ``get_dec_example``'s own domain-qualified naming rationale --
tool names are global across the whole MCP server.

**The packaged ``feat/data/feat_example.md`` file itself does not exist
yet** -- it is Phase 3's job (Task 3.1), not this phase's. This tool is
wired to the same ``read_packaged_text("feat", "example")`` call every
other domain's ``get_<d>_example`` tool uses, so it needs no further
changes once Phase 3 ships the file; until then it raises
``FileNotFoundError`` when actually called (uncaught, same as a
genuinely broken installation of any other domain -- see this module's
own tests for how that's exercised today).

## Functions

### `get_feat_example() -> 'str'`

Return the packaged FEAT example's full markdown text, verbatim.

The example file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package -- see this module's own docstring for its current
Phase 2 status (the file does not exist yet; Phase 3 ships it). Reads
the file fresh on every call (no in-memory cache). A missing or
corrupted packaged file is not caught or wrapped here -- it propagates
as a hard :class:`FileNotFoundError`, the same let-it-raise convention
every other tool/resource in this codebase follows.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

