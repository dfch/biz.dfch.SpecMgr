# `biz.dfch.specmgr.req.tools`

MCP tool wrappers for requirements (mirrors ``uc/tools/``'s own shape).

``parse_req`` reads a raw filepath, parses, and validates it into a structured
document model -- unlike ``adr/tools/``, there is no id-based file storage
layer for requirements yet (no ``req_base_dir``/``_paths.py``/``_io.py``
equivalent). ``get_req_example`` returns a complete, valid sample requirement
document as raw markdown (Task 3.6); ``get_req_template`` returns a document
with every field present but populated with short placeholder ("blind text")
content instead (Task 3.7) -- both read a packaged, build-guaranteed data file
rather than anything on the caller's filesystem. Import this package to
register all requirement tools at once::

    from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
