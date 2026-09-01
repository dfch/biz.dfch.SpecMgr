"""Use Case (UC) domain — Cockburn-based use case specification and validation.

This is a domain-first package containing models, tools, prompts, and resources
for managing use case documents.

Import this package to register all use-case tools/resources against the
shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import uc  # noqa: F401 (side-effects only)

``tools`` (``parse_uc``, ``get_uc``, ``list_uc``, ``get_uc_example``,
``get_uc_template``, ``create_uc``,
``validate_uc``) and ``resources`` (``specmgr://uc/schema``,
``specmgr://uc/example``, ``specmgr://uc/template``) exist; whole-body and
line-range updates of an existing document go through the generic
``update`` tool in ``general.tools`` (``type="uc"``), and status changes
go through the generic ``set_status`` tool in ``general.tools``
(``type="uc"``). The former
``specmgr://uc/list`` resource was replaced by the ``list_uc`` tool, so
that paging parameters could be accepted (feat-13-list-paging). There is
no ``prompts`` sub-package yet (see
``.specmgr/feat/feat-4-use-cases/README.md`` Phase 3).
"""

from . import resources, tools  # noqa: F401

__all__ = [
    "resources",
    "tools",
]
