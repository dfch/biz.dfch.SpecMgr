# `biz.dfch.specmgr.rsk`

Risk (RSK) domain -- risk registers for system specifications.

This is a domain-first package, mirroring ``tsk``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``rsk`` documents.

Import this package to register all risk tools/prompts/resources
against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import rsk  # noqa: F401 (side-effects only)

``tools`` (``parse_rsk``, ``get_rsk``, ``list_rsk``, ``get_rsk_example``,
``get_rsk_template``, ``create_rsk``), ``resources``
(``specmgr://rsk/schema``,
``specmgr://rsk/example``, ``specmgr://rsk/template``,
``specmgr://rsk/tara``, ``specmgr://rsk/risk-matrix``), and ``prompts``
(``create_risk``, ``update_risk``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="rsk"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="rsk"``).
Disk-free, id-free dry-run content validation goes through the generic
``validate`` tool in ``general.tools`` (``type="rsk"``) -- the former
``validate_rsk`` tool was removed in favor of it (feat-81-83-validation).
Like REQ/TSK, RSK has no
``specmgr://rsk/{id}`` resource -- id-based reads go through the
``get_rsk`` tool only (same rationale as ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
"Expose id-based document reads as a tool, not a resource" -- RSK never had
such a resource to remove in the first place). Likewise, there is no
``specmgr://rsk/list`` resource -- listing is the paged ``list_rsk`` tool,
so that paging parameters could be accepted (feat-13-list-paging, ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13).
