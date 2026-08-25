# `biz.dfch.specmgr.rsk.resources`

MCP resource registrations for Risk (RSK) documents (Tasks 3.10-3.11, 3.15).

``rsk_schema`` registers the persisted-JSON-Schema resource
(``specmgr://rsk/schema``). ``rsk_example`` registers the packaged sample
risk document resource (``specmgr://rsk/example``). ``rsk_template``
registers the packaged risk template resource (``specmgr://rsk/template``)
-- every field present, populated with short placeholder ("blind text")
content. ``rsk_tara`` registers the static TARA domain-knowledge resource
(``specmgr://rsk/tara``) and ``rsk_risk_matrix`` the static 5x5 risk-matrix
domain-knowledge resource (``specmgr://rsk/risk-matrix``) -- both raw
packaged markdown, the audience being an LLM agent reading guidance rather
than code consuming data. Import this package to register all risk
resources against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.rsk import resources  # noqa: F401 (side-effects only)

Like REQ/TSK, RSK has no by-id single-document *resource* -- id-based reads
go through the ``get_rsk`` tool only (``rsk.tools.get_rsk``); there never
was a ``specmgr://rsk/{id}`` resource to remove in the first place (same
rationale as ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). There is no
``specmgr://rsk/list`` resource either -- listing is the paged ``list_rsk``
tool (``rsk.tools.list_rsk``), so that paging parameters
(``max_results``/``offset``) can be accepted (feat-13-list-paging, ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13).
