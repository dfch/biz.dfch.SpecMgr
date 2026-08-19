# `biz.dfch.specmgr.adr.resources`

MCP resource registrations for Architecture Decision Records (plan §8, §9a).

``adr_get`` registers the by-id template resource (``specmgr://adr/{id}``).
The former ADR listing resource (``adr_list``, ``specmgr://adr/list``) was
replaced by the ``list_adr`` ``@mcp.tool()`` (``adr.tools.list_adr``), so
that paging parameters (``max_results``/``offset``) could be accepted --
see ``.specmgr/feat/feat-13-list-paging/README.md``. Import this package to
register the remaining ADR resource::

    from biz.dfch.specmgr.adr import resources  # noqa: F401 (side-effects only)
