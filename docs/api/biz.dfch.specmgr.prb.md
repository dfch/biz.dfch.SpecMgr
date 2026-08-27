# `biz.dfch.specmgr.prb`

Problem Statement (PRB) domain -- Six-Sigma-style problem statement specifications.

This is a domain-first package, mirroring ``tsk``/``qa``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``prb`` documents.

Import this package to register all problem statement tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import prb  # noqa: F401 (side-effects only)

``tools`` (``parse_prb``, ``get_prb``, ``list_prb``, ``get_prb_example``,
``get_prb_template``, ``create_prb``,
``delete_prb``, ``validate_prb``), ``resources`` (``specmgr://prb/schema``,
``specmgr://prb/example``, ``specmgr://prb/template``), and ``prompts``
(``create_prb``, ``update_prb``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="prb"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="prb"``). Like
REQ/TSK/QA, PRB has no
``specmgr://prb/{id}`` resource -- id-based reads go through the ``get_prb``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://prb/list`` resource -- ``list_prb`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13),
unlike REQ/TSK/QA's own resource-then-converted history.
