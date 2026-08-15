# `biz.dfch.specmgr.req`

Requirement (REQ) domain -- requirement specifications.

This is a domain-first package containing models, tools, prompts, and resources
for managing requirement documents.

Import this package to register all requirement tools/prompts/resources against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)

``tools`` (``parse_req``, ``get_req``, ``get_req_example``,
``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``,
``delete_req``, ``validate_req``), ``resources`` (``specmgr://req/schema``,
``specmgr://req/example``, ``specmgr://req/template``,
``specmgr://req/list``), and ``prompts`` (``create_req``, ``update_req``)
all exist. Unlike ADR, REQ has no ``specmgr://req/{id}`` resource --
id-based reads go through the ``get_req`` tool only (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614).
