# `biz.dfch.specmgr.adr.tools`

MCP tool wrappers for Architecture Decision Records.

Thin file-I/O/id-lookup adapters over ``models/adr/v1/mutations.py`` plus
``parse_adr``/``render_adr``, exposed as ``@mcp.tool()``-decorated functions
against the shared ``mcp`` application instance -- one module per tool.
Status changes of an existing ADR go through the generic ``set_status``
tool in ``general.tools`` (``type="adr"``). Import this package to register
all ADR tools at once::

    from biz.dfch.specmgr.adr import tools  # noqa: F401 (side-effects only)
