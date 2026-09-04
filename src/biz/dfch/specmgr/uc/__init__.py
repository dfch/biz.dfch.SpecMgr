"""Use Case (UC) domain — Cockburn-based use case specification and validation.

This is a domain-first package containing models, tools, prompts, and resources
for managing use case documents.

Import this package to register all use-case tools/resources against the
shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import uc  # noqa: F401 (side-effects only)

``tools`` (``parse_uc``, ``get_uc``, ``list_uc``, ``get_uc_example``,
``get_uc_template``, ``create_uc``), ``resources``
(``specmgr://uc/schema``,
``specmgr://uc/example``, ``specmgr://uc/template``), and ``prompts``
(``create_uc``, ``update_uc``) all exist; whole-body and
line-range updates of an existing document go through the generic
``update`` tool in ``general.tools`` (``type="uc"``), and status changes
go through the generic ``set_status`` tool in ``general.tools``
(``type="uc"``). Disk-free, id-free dry-run content validation goes
through the generic ``validate`` tool in ``general.tools`` (``type="uc"``)
-- the former ``validate_uc`` tool was removed in favor of it
(feat-81-83-validation). The former
``specmgr://uc/list`` resource was replaced by the ``list_uc`` tool, so
that paging parameters could be accepted (feat-13-list-paging).
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
