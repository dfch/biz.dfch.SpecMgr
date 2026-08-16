# `biz.dfch.specmgr.uc`

Use Case (UC) domain — Cockburn-based use case specification and validation.

This is a domain-first package containing models, tools, prompts, and resources
for managing use case documents.

Import this package to register all use-case tools/resources against the
shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import uc  # noqa: F401 (side-effects only)

``tools`` (``parse_uc``, ``get_uc``, ``get_uc_example``, ``get_uc_template``,
``create_uc``, ``update_uc``, ``set_status_uc``, ``delete_uc``,
``validate_uc``) and ``resources`` (``specmgr://uc/schema``,
``specmgr://uc/example``, ``specmgr://uc/template``, ``specmgr://uc/list``)
exist. There is no ``prompts`` sub-package yet (see
``.specmgr/feat/feat-4-use-cases/README.md`` Phase 3).
