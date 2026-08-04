# `biz.dfch.specmgr.adr.resources`

MCP resource registrations for Architecture Decision Records (plan §8, §9a).

``adr_list`` registers the ADR listing resource (``specmgr://adr/list``) and
``adr_get`` registers the by-id template resource (``specmgr://adr/{id}``).
Import this package to register both at once::

    from biz.dfch.specmgr.adr import resources  # noqa: F401 (side-effects only)
