# `biz.dfch.specmgr.req`

Requirement (REQ) domain -- requirement specifications.

This is a domain-first package containing models, tools, prompts, and resources
for managing requirement documents.

Import this package to register all requirement tools/prompts/tools against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)

Currently only ``tools`` (``parse_req``) exists; ``prompts``/``resources`` are
not implemented yet.
