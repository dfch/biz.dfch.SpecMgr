# `biz.dfch.specmgr.qa.resources`

MCP resource registrations for Question and Answer (QA) documents (Phase 4, Task 4.2).

``qa_schema`` registers the persisted-JSON-Schema resource
(``specmgr://qa/schema``). ``qa_example`` registers the packaged sample QA
document resource (``specmgr://qa/example``). ``qa_template`` registers the
packaged QA template resource (``specmgr://qa/template``) -- every field
present, populated with short placeholder ("blind text") content rather
than a valid document instance. ``qa_list`` registers the listing resource
(``specmgr://qa/list``), mirroring ``req.resources.req_list``. Import this
package to register all QA resources against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.qa import resources  # noqa: F401 (side-effects only)

Like REQ, QA has no by-id single-document *resource* -- id-based reads go
through the ``get_qa`` tool only; see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource").
