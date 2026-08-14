# `biz.dfch.specmgr.req._data`

Private, dependency-free access to REQ's packaged example markdown (Task 3.6).

Unlike ``docs/req_schema.json`` (read via ``biz.dfch.specmgr._paths.DOCS_DIR``,
which only resolves correctly from an editable/source checkout), the file this
module reads is shipped as real *package data* -- declared under
``[tool.setuptools.package-data]`` for ``biz.dfch.specmgr.req.resources`` and
loaded via :mod:`importlib.resources` -- so its presence is a genuine
build-time guarantee that survives a real, non-editable ``pip install`` too,
not just a dev checkout.

Kept in a neutral module directly under ``req/`` (not under ``req/tools/`` or
``req/resources/``) so neither of those two sub-packages has to import from
the other just to share this one file read -- both ``req.tools.get_req_example``
and ``req.resources.req_example`` import this module directly, mirroring the
top-level ``_paths.py``'s own "shared, dependency-free" role.

Only imports the standard library (``importlib.resources``), so importing this
module never pulls in the ``cli``/``mcp`` extras.

## Functions

### `read_req_example_text() -> 'str'`

Return the packaged REQ example's full markdown text, verbatim.

Reads the file fresh on every call (no in-memory cache, consistent with
every other resource/tool in this codebase). The file's presence is a
build-time guarantee (declared package data, not user-authored content
living elsewhere), so a missing or corrupted file is a hard, uncaught
failure -- there is no defensive handling here.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block, exactly as committed on disk.

Raises
------
FileNotFoundError
    If the packaged example file is missing (should never happen outside
    a broken installation).

