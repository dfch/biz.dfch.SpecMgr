# `biz.dfch.specmgr.vcr.resources`

MCP resource registrations for Verification Case Record (VCR) documents (Task 3.1).

``vcr_example`` registers the packaged sample
verification case record document resource (``specmgr://vcr/example``).
``vcr_template`` registers the packaged verification case record template
resource (``specmgr://vcr/template``) -- every section present, populated
with short placeholder ("blind text") content that still round-trips
through ``parse_vcr`` (the DEC/RSK precedent). Import this package to
register all verification case record resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.vcr import resources  # noqa: F401 (side-effects only)

Like DEC/GOL, VCR has no by-id single-document *resource* -- id-based reads
go through the ``get_vcr`` tool only (``vcr.tools.get_vcr``), and no
``specmgr://vcr/list`` resource either -- listing goes through the
``list_vcr`` ``@mcp.tool()`` (``vcr.tools.list_vcr``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
The former schema resource (``vcr_schema``, ``specmgr://vcr/schema``) was
converted the same way into the ``get_vcr_schema`` ``@mcp.tool()``
(``vcr.tools.get_vcr_schema``), so that the generated JSON Schema is
discoverable from the always-in-context tool surface instead of the
resource layer -- see ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3
(feat-189 Phase 105).
