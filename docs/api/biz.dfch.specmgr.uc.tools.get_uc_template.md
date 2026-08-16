# `biz.dfch.specmgr.uc.tools.get_uc_template`

``@mcp.tool()`` wrapper: get_uc_template (Task 3.1.3).

Returns a UC document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new UC document by hand, distinct from ``get_uc_example``, which returns a
complete, *valid* sample document. Mirrors ``req.tools.get_req_template``.

## Functions

### `get_uc_template() -> 'str'`

Return the packaged UC template's full markdown text, verbatim.

The template file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike ``get_uc_example``, the returned text is **not** guaranteed to
satisfy ``parse_uc``/``UcDocument``'s field-level validators -- this is a
structural authoring aid, not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

