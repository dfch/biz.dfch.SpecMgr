# `biz.dfch.specmgr.uc.resources`

MCP resource registrations for Use Case (UC) documents (Task 3.1.4, 3.1.6).

``uc_schema`` registers the persisted-JSON-Schema resource
(``specmgr://uc/schema``). ``uc_example`` registers the packaged sample
use-case document resource (``specmgr://uc/example``). ``uc_template``
registers the packaged use-case template resource (``specmgr://uc/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. ``uc_list`` registers the
listing resource (``specmgr://uc/list``, Task 3.1.6), mirroring
``req.resources.req_list``. Import this package to register all use-case
resources against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.uc import resources  # noqa: F401 (side-effects only)

Unlike ADR, UC has no by-id single-document *resource* --
``specmgr://uc/{id}`` was never added; ``get_uc`` (``uc.tools.get_uc``) is
the id-based read path instead, mirroring REQ's own precedent (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614).
