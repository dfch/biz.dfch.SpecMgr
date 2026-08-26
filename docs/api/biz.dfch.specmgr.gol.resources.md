# `biz.dfch.specmgr.gol.resources`

MCP resource registrations for Goal (GOL) documents (Task 3.11).

``gol_schema`` registers the persisted-JSON-Schema resource
(``specmgr://gol/schema``). ``gol_example`` registers the packaged sample
goal document resource (``specmgr://gol/example``). ``gol_template``
registers the packaged goal template resource (``specmgr://gol/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. Import this package to
register all goal resources against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.gol import resources  # noqa: F401 (side-effects only)

Like PRB/REQ/TSK/QA, GOL has no by-id single-document *resource* -- id-based
reads go through the ``get_gol`` tool only (``gol.tools.get_gol``), and no
``specmgr://gol/list`` resource either -- listing goes through the
``list_gol`` ``@mcp.tool()`` (``gol.tools.list_gol``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
