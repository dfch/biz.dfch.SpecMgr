# `biz.dfch.specmgr.feat.resources`

MCP resource registrations for Feature (FEAT) documents (feat-31 Task 3.5).

``feat_schema`` registers the persisted-JSON-Schema resource
(``specmgr://feat/schema``). ``feat_example`` registers the packaged sample
feature document resource (``specmgr://feat/example``). ``feat_template``
registers the packaged feature template resource (``specmgr://feat/template``)
-- every section present, populated with short placeholder ("blind text")
content that still round-trips through ``parse_feat`` (the DEC/RSK
precedent). Import this package to register all feature resources against
the shared ``mcp`` application instance::

    from biz.dfch.specmgr.feat import resources  # noqa: F401 (side-effects only)

Like DEC/GOL, FEAT has no by-id single-document *resource* -- id-based reads
go through the ``get_feat`` tool only (``feat.tools.get_feat``), and no
``specmgr://feat/list`` resource either -- listing goes through the
``list_feat`` ``@mcp.tool()`` (``feat.tools.list_feat``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
