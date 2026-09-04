# `biz.dfch.specmgr.dec`

Decision (DEC) domain -- decisions in general (not architecture-only).

This is a domain-first package, mirroring ``gol``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``dec`` documents. A DEC keeps the ADR's general
structure (MADR-style headings, ``Options`` collection) but is built on the
generic ``models/md`` parser with the simple surface used by GOL/RSK/QA --
no fine-grained mutation tools, no by-id resource.

Import this package to register all decision tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import dec  # noqa: F401 (side-effects only)

``tools`` (``create_dec``, ``parse_dec``,
``list_dec``, ``get_dec``, ``get_dec_example``, ``get_dec_template``),
``resources`` (``specmgr://dec/schema``,
``specmgr://dec/example``, ``specmgr://dec/template``), and ``prompts``
(``create_dec``, ``update_dec``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="dec"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="dec"``).
Disk-free, id-free dry-run content validation goes through the generic
``validate`` tool in ``general.tools`` (``type="dec"``) -- the former
``validate_dec`` tool was removed in favor of it (feat-81-83-validation).
Like GOL, DEC has no
``specmgr://dec/{id}`` resource -- id-based reads go through the ``get_dec``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
