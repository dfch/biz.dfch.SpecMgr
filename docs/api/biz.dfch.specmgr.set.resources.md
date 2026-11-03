# `biz.dfch.specmgr.set.resources`

MCP resource registrations for set (set) documents (feat-173-req-iso29148-level-set Phase 180).

``set_example`` registers the packaged sample
set document resource (``specmgr://set/example``).
``set_template`` registers the packaged set template
resource (``specmgr://set/template``) -- every field present, populated
with short placeholder ("blind text") content that still round-trips
through ``parse_set`` (the DEC/RSK precedent). Import this package to
register all set resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.set import resources  # noqa: F401 (side-effects only)

Like VCR/SYSRS, SET has no by-id single-document *resource* -- id-based
reads go through the ``get_set`` tool only (``set.tools.get_set``), and
no ``specmgr://set/list`` resource either -- listing goes through the
``list_set`` ``@mcp.tool()`` (``set.tools.list_set``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
set ships the generated JSON Schema as the ``get_set_schema`` ``@mcp.tool()``
(``set.tools.get_set_schema``) from day one, per ADR
112b6498-078b-4a59-88b8-8ffb7a5041b3 (feat-189 Phase 105) -- there is no
``specmgr://set/schema`` resource in its history.
