# `biz.dfch.specmgr.prb.resources`

MCP resource registrations for Problem Statement (PRB) documents (Task 3.11).

``prb_schema`` registers the persisted-JSON-Schema resource
(``specmgr://prb/schema``). ``prb_example`` registers the packaged sample
problem statement document resource (``specmgr://prb/example``).
``prb_template`` registers the packaged problem statement template resource
(``specmgr://prb/template``) -- every field present, populated with short
placeholder ("blind text") content rather than a valid document instance.
Import this package to register all problem statement resources against the
shared ``mcp`` application instance::

    from biz.dfch.specmgr.prb import resources  # noqa: F401 (side-effects only)

Like REQ/TSK/QA, PRB has no by-id single-document *resource* -- id-based
reads go through the ``get_prb`` tool only (``prb.tools.get_prb``), and no
``specmgr://prb/list`` resource either -- listing goes through the
``list_prb`` ``@mcp.tool()`` (``prb.tools.list_prb``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
