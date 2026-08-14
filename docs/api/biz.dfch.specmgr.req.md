# `biz.dfch.specmgr.req`

Requirement (REQ) domain -- requirement specifications.

This is a domain-first package containing models, tools, prompts, and resources
for managing requirement documents.

Import this package to register all requirement tools/prompts/resources against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)

Currently ``tools`` (``parse_req``) and ``resources`` (``specmgr://req/schema``)
exist; ``prompts`` is not implemented yet.
