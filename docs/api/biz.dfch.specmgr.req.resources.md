# `biz.dfch.specmgr.req.resources`

MCP resource registrations for Requirement (REQ) documents (Tasks 3.5-3.7, 3.18).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). ``req_example`` registers the packaged sample
requirement document resource (``specmgr://req/example``). ``req_template``
registers the packaged requirement template resource (``specmgr://req/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. ``req_list`` registers the
listing resource (``specmgr://req/list``, Task 3.18), mirroring
``adr.resources.adr_list``. Import this package to register all requirement
resources against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)

Unlike ADR, REQ has no by-id single-document *resource* --
``specmgr://req/{id}`` (``req_get``, Task 3.17) was removed in favor of the
``get_req`` tool (``req.tools.get_req``); see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource").
