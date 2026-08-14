# `biz.dfch.specmgr.req.resources`

MCP resource registrations for Requirement (REQ) documents (Tasks 3.5, 3.6).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). ``req_example`` registers the packaged sample
requirement document resource (``specmgr://req/example``). This sub-package
also holds the ``data/`` directory of packaged, build-guaranteed example
markdown files (declared package data, not Python modules). Import this
package to register all requirement resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)
