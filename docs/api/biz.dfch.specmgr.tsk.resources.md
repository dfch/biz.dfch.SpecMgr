# `biz.dfch.specmgr.tsk.resources`

MCP resource registrations for Task List (TSK) documents (Tasks 3.10-3.11).

``tsk_example`` registers the packaged sample
task list document resource (``specmgr://tsk/example``). ``tsk_template``
registers the packaged task list template resource (``specmgr://tsk/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. Import this package to
register all task list resources against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.tsk import resources  # noqa: F401 (side-effects only)

Like REQ, TSK has no by-id single-document *resource* -- id-based reads go
through the ``get_tsk`` tool only (``tsk.tools.get_tsk``); there never was a
``specmgr://tsk/{id}`` resource to remove in the first place. The former
listing resource (``tsk_list``, ``specmgr://tsk/list``) was replaced the
same way by the ``list_tsk`` ``@mcp.tool()`` (``tsk.tools.list_tsk``), so
that paging parameters (``max_results``/``offset``) could be accepted --
see ``.specmgr/feat/feat-13-list-paging/README.md``.
The former schema resource (``tsk_schema``, ``specmgr://tsk/schema``) was
converted the same way into the ``get_tsk_schema`` ``@mcp.tool()``
(``tsk.tools.get_tsk_schema``), so that the generated JSON Schema is
discoverable from the always-in-context tool surface instead of the
resource layer -- see ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3
(feat-189 Phase 105).
