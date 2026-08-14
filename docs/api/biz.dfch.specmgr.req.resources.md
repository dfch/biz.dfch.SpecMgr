# `biz.dfch.specmgr.req.resources`

MCP resource registrations for Requirement (REQ) documents (Task 3.5).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). Import this package to register it against
the shared ``mcp`` application instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)
