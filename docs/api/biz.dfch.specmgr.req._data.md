# `biz.dfch.specmgr.req._data`

Private, dependency-free access to REQ's packaged example/template markdown
(Tasks 3.6, 3.7).

Unlike ``docs/req_schema.json`` (read via ``biz.dfch.specmgr._paths.DOCS_DIR``,
which only resolves correctly from an editable/source checkout), the files this
module reads are shipped as real *package data* -- declared under
``[tool.setuptools.package-data]`` for ``biz.dfch.specmgr.req.resources`` and
loaded via :mod:`importlib.resources` -- so their presence is a genuine
build-time guarantee that survives a real, non-editable ``pip install`` too,
not just a dev checkout.

Kept in a neutral module directly under ``req/`` (not under ``req/tools/`` or
``req/resources/``) so neither of those two sub-packages has to import from
the other just to share these file reads -- ``req.tools.get_req_example``/
``get_req_template`` and ``req.resources.req_example``/``req_template`` all
import this module directly, mirroring the top-level ``_paths.py``'s own
"shared, dependency-free" role.

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


### `read_req_template_text() -> 'str'`

Return the packaged REQ template's full markdown text, verbatim.

Reads the file fresh on every call (no in-memory cache, consistent with
every other resource/tool in this codebase). The file's presence is a
build-time guarantee (declared package data, not user-authored content
living elsewhere), so a missing or corrupted file is a hard, uncaught
failure -- there is no defensive handling here.

Unlike :func:`read_req_example_text`, the returned text is **not**
guaranteed to satisfy ``parse_req``/``ReqDocument``'s field-level
validators (e.g. ``## Level``/``## Priority`` hold descriptive
placeholder prose, not a value matching their strict patterns) -- the
template is a structural authoring aid (every field present, with short
"blind text"), not a valid document instance.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block, exactly as committed on disk.

Raises
------
FileNotFoundError
    If the packaged template file is missing (should never happen
    outside a broken installation).

