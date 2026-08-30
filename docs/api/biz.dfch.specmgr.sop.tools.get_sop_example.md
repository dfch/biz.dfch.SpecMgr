# `biz.dfch.specmgr.sop.tools.get_sop_example`

``@mcp.tool()`` wrapper: get_sop_example (Task 2.2).

Returns a complete, valid sample SOP document as raw markdown -- useful as a
learning example for drafting a new SOP document by hand, or for an LLM to
see the expected shape without re-deriving it from the JSON Schema alone.
Named ``get_sop_example`` rather than the bare ``get_example`` since tool
names are global across the whole MCP server -- domain-qualifying it now
avoids a future collision.

The packaged example data file (``sop/data/sop_example.md``) is created in
Phase 3 (Task 3.1); until then this tool registers fine (``read_packaged_text``
is called at call time, not import time) but raises ``FileNotFoundError`` if
invoked against the not-yet-present data file -- exactly mirroring DEC's own
build history (``get_dec_example`` shipped in one phase, its real packaged
data in a later one).

## Functions

### `get_sop_example() -> 'str'`

Return the packaged SOP example's full markdown text, verbatim.

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

