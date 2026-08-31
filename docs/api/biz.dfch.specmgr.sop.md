# `biz.dfch.specmgr.sop`

Standard Operating Procedure (SOP) domain -- structured, step-by-step
operational documents with a RASCI-style responsibility assignment and a
closed approval/effectivity lifecycle.

This is a domain-first package, mirroring ``dec``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``sop`` documents. An SOP is built on the
generic ``models/md`` parser with the simple surface used by GOL/RSK/QA/DEC
-- no fine-grained mutation tools, no by-id resource.

SOP is the **first domain built from scratch entirely on the post-feat-22
generic mutation tools** (ADR 36905d5b-8057-4294-8665-c7eed5534db0): it has
no ``update_sop``/``set_status_sop`` tools of its own -- it dispatches
straight into the generic ``update``/``set_status`` tools in
``general.tools`` from day one, per the convention ``AGENTS.md`` already
reserves for future domains.

Import this package to register all SOP tools/prompts/resources (7 tools,
3 resources, 2 prompts) against the shared ``mcp`` application instance at
once::

    from biz.dfch.specmgr import sop  # noqa: F401 (side-effects only)

``tools`` (``create_sop``, ``parse_sop``, ``list_sop``, ``get_sop``,
``get_sop_example``, ``get_sop_template``,
``validate_sop``), ``resources`` (``specmgr://sop/schema``,
``specmgr://sop/example``, ``specmgr://sop/template``), and ``prompts``
(``create_sop``, ``update_sop``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="sop"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="sop"``). Like
DEC, SOP has no ``specmgr://sop/{id}`` resource -- id-based reads go
through the ``get_sop`` tool only (ADR
ddf1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://sop/list`` resource -- ``list_sop`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

SOP relies on the cross-cutting ``specmgr://rasci`` resource
(``general.resources.rasci``, REQ-011) for the generic RASCI
(Responsible/Accountable/Support/Consulted/Informed) role definitions,
not a domain-local one -- RASCI is a well-known external framework, so
its definitions live under ``general/`` and are reached via
cross-references in the six RASCI-family class docstrings, the
``create_sop``/``update_sop`` packaged instructions, this docstring, and
``server.py``'s docstring.
