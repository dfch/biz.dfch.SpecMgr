# `biz.dfch.specmgr.qa`

Question and Answer (QA) domain -- requirements-elicitation interview specifications.

This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
mirroring ``req``'s/``tsk``'s layout, containing models, tools, prompts, and
resources for managing ``qa`` documents.

Import this package to register all QA tools/prompts/resources against the
shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import qa  # noqa: F401 (side-effects only)

``tools`` (``parse_qa``, ``get_qa``, ``list_qa``, ``get_qa_example``,
``get_qa_template``, ``create_qa``,
``delete_qa``, ``validate_qa``), ``resources`` (``specmgr://qa/schema``,
``specmgr://qa/example``, ``specmgr://qa/template``), and ``prompts``
(``create_qa``, ``update_qa``) all exist; whole-body and line-range updates
of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="qa"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="qa"``). Like
REQ, QA has no
``specmgr://qa/{id}`` resource -- id-based reads go through the ``get_qa``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, the former
``specmgr://qa/list`` resource was replaced by the ``list_qa`` tool, so
that paging parameters could be accepted (feat-13-list-paging).

Note: as of Phase 4 (MCP Surface), this domain's tools/resources/prompts are
implemented and importable standalone, but ``server.py``'s own bottom-of-file
import list does not import ``qa`` yet -- that registration wiring is Phase
5's Task 5.1.
