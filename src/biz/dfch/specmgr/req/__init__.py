"""Requirement (REQ) domain -- requirement specifications.

This is a domain-first package containing models, tools, prompts, and resources
for managing requirement documents.

Import this package to register all requirement tools/prompts/resources against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)

``tools`` (``parse_req``, ``get_req``, ``list_req``, ``get_req_example``,
``get_req_template``, ``create_req``, ``set_status_req``,
``delete_req``, ``validate_req``), ``resources`` (``specmgr://req/schema``,
``specmgr://req/example``, ``specmgr://req/template``), and ``prompts``
(``create_req``, ``update_req``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="req"``). Unlike ADR, REQ has no
``specmgr://req/{id}`` resource -- id-based reads go through the ``get_req``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, the former
``specmgr://req/list`` resource was replaced by the ``list_req`` tool, so
that paging parameters could be accepted (feat-13-list-paging).
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
