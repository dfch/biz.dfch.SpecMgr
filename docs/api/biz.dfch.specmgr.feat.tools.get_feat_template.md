# `biz.dfch.specmgr.feat.tools.get_feat_template`

``@mcp.tool()`` wrapper: get_feat_template (Task 2.3).

Returns a feature document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for
drafting a new FEAT document by hand, distinct from ``get_feat_example``,
which returns a complete, *valid* sample document. Named
``get_feat_template`` rather than the bare ``get_template``, mirroring
``get_dec_template``'s own domain-qualified naming rationale -- tool names
are global across the whole MCP server.

**The packaged ``feat/data/feat_template.md`` file itself does not exist
yet** -- it is Phase 3's job (Task 3.2), not this phase's. See
``get_feat_example``'s own module docstring for the identical current-status
note (this tool is already wired to the shared
``read_packaged_text("feat", "template")`` call, and needs no further
changes once Phase 3 ships the file).

## Functions

### `get_feat_template() -> 'str'`

Return the packaged FEAT template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package -- see this module's own docstring for its current
Phase 2 status (the file does not exist yet; Phase 3 ships it). Reads
the file fresh on every call (no in-memory cache). A missing or
corrupted packaged file is not caught or wrapped here -- it propagates
as a hard :class:`FileNotFoundError`, the same let-it-raise convention
every other tool/resource in this codebase follows.

Unlike ``get_feat_example``, the returned text is **not** guaranteed to
satisfy ``parse_feat``/``FeatDocument``'s field-level validators -- this
is a structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

