# `biz.dfch.specmgr.dec.resources`

MCP resource registrations for Decision (DEC) documents (feat-21 Task 3.4).

``dec_schema`` registers the persisted-JSON-Schema resource
(``specmgr://dec/schema``). ``dec_example`` registers the packaged sample
decision document resource (``specmgr://dec/example``). ``dec_template``
registers the packaged decision template resource (``specmgr://dec/template``)
-- every section present, populated with short placeholder ("blind text")
content that still round-trips through ``parse_dec`` (the RSK precedent).
Import this package to register all decision resources against the shared
``mcp`` application instance::

    from biz.dfch.specmgr.dec import resources  # noqa: F401 (side-effects only)

Like GOL, DEC has no by-id single-document *resource* -- id-based reads go
through the ``get_dec`` tool only (``dec.tools.get_dec``), and no
``specmgr://dec/list`` resource either -- listing goes through the
``list_dec`` ``@mcp.tool()`` (``dec.tools.list_dec``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
