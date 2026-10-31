# `biz.dfch.specmgr.txt.resources`

MCP resource registrations for free-form text (TXT) documents (feat-229-txt Phase 120).

``txt_example`` registers the packaged sample
free-form text document resource (``specmgr://txt/example``).
``txt_template`` registers the packaged free-form text template
resource (``specmgr://txt/template``) -- every field present, populated
with short placeholder ("blind text") content that still round-trips
through ``parse_txt`` (the DEC/RSK precedent). Import this package to
register all free-form text resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.txt import resources  # noqa: F401 (side-effects only)

Like VCR/SYSRS, TXT has no by-id single-document *resource* -- id-based
reads go through the ``get_txt`` tool only (``txt.tools.get_txt``), and
no ``specmgr://txt/list`` resource either -- listing goes through the
``list_txt`` ``@mcp.tool()`` (``txt.tools.list_txt``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
TXT ships the generated JSON Schema as the ``get_txt_schema`` ``@mcp.tool()``
(``txt.tools.get_txt_schema``) from day one, per ADR
112b6498-078b-4a59-88b8-8ffb7a5041b3 (feat-189 Phase 105) -- there is no
``specmgr://txt/schema`` resource in its history.
