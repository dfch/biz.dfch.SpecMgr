# `biz.dfch.specmgr.req.tools`

MCP tool wrappers for requirements (mirrors ``uc/tools/``'s own shape).

Currently just ``parse_req`` -- a single, narrowly-scoped tool added ahead of
the full Phase 3/4 tool specification/sequencing. Unlike ``adr/tools/``, there
is no id-based file storage layer for requirements yet (no
``req_base_dir``/``_paths.py``/``_io.py`` equivalent), so this tool takes a raw
filepath, reads it, and parses it into a structured document model. Import
this package to register all requirement tools at once::

    from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
