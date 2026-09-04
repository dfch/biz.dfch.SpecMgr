# `biz.dfch.specmgr.gol`

Goal (GOL) domain -- high-level business goal specifications.

This is a domain-first package, mirroring ``prb``/``req``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``gol`` documents.

Import this package to register all goal tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import gol  # noqa: F401 (side-effects only)

``tools`` (``parse_gol``, ``get_gol``, ``list_gol``, ``get_gol_example``,
``get_gol_template``, ``create_gol``), ``resources``
(``specmgr://gol/schema``,
``specmgr://gol/example``, ``specmgr://gol/template``), and ``prompts``
(``create_gol``, ``update_gol``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="gol"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="gol"``).
Disk-free, id-free dry-run content validation goes through the generic
``validate`` tool in ``general.tools`` (``type="gol"``) -- the former
``validate_gol`` tool was removed in favor of it (feat-81-83-validation).
Like REQ/PRB/TSK/QA, GOL has no
``specmgr://gol/{id}`` resource -- id-based reads go through the ``get_gol``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://gol/list`` resource -- ``list_gol`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13),
unlike REQ/UC/TSK/QA/PRB's own resource-then-converted history.
