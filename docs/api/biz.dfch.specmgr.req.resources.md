# `biz.dfch.specmgr.req.resources`

MCP resource registrations for Requirement (REQ) documents (Tasks 3.5-3.7, 3.17-3.18).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). ``req_example`` registers the packaged sample
requirement document resource (``specmgr://req/example``). ``req_template``
registers the packaged requirement template resource (``specmgr://req/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. This sub-package also holds
the ``data/`` directory of packaged, build-guaranteed example/template
markdown files (declared package data, not Python modules). ``req_get``
registers the by-id single-document resource (``specmgr://req/{id}``, Task
3.17) and ``req_list`` registers the listing resource (``specmgr://req/list``,
Task 3.18), both mirroring ``adr.resources.adr_get``/``adr_list``. Import
this package to register all requirement resources against the shared
``mcp`` application instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)
