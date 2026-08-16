# `biz.dfch.specmgr.tsk.resources`

MCP resource registrations for Task List (TSK) documents (Tasks 3.10-3.11).

``tsk_schema`` registers the persisted-JSON-Schema resource
(``specmgr://tsk/schema``). ``tsk_example`` registers the packaged sample
task list document resource (``specmgr://tsk/example``). ``tsk_template``
registers the packaged task list template resource (``specmgr://tsk/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. ``tsk_list`` registers the
listing resource (``specmgr://tsk/list``), mirroring
``req.resources.req_list``. Import this package to register all task list
resources against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.tsk import resources  # noqa: F401 (side-effects only)

Like REQ, TSK has no by-id single-document *resource* -- id-based reads go
through the ``get_tsk`` tool only (``tsk.tools.get_tsk``); there never was a
``specmgr://tsk/{id}`` resource to remove in the first place.
