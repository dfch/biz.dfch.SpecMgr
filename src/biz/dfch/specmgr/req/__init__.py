"""Requirement (REQ) domain -- requirement specifications.

This is a domain-first package containing models, tools, prompts, and resources
for managing requirement documents.

Import this package to register all requirement tools/prompts/resources against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)

Currently ``tools`` (``parse_req``, ``get_req_example``, ``get_req_template``,
``create_req``, ``update_req``, ``set_status_req``, ``delete_req``,
``validate_req``) and ``resources`` (``specmgr://req/schema``,
``specmgr://req/example``, ``specmgr://req/template``,
``specmgr://req/{id}``, ``specmgr://req/list``) exist; ``prompts`` is not
implemented yet.
"""

from . import resources, tools  # noqa: F401

__all__ = [
    "resources",
    "tools",
]
