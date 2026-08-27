# `biz.dfch.specmgr.tsk`

TaskList (TSK) domain -- lightweight task/todo-list specifications.

This is a domain-first package, mirroring ``req``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``tsk`` documents.

Import this package to register all task list tools/prompts/resources
against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import tsk  # noqa: F401 (side-effects only)

``tools`` (``parse_tsk``, ``get_tsk``, ``list_tsk``, ``get_tsk_example``,
``get_tsk_template``, ``create_tsk``,
``delete_tsk``, ``validate_tsk``), ``resources`` (``specmgr://tsk/schema``,
``specmgr://tsk/example``, ``specmgr://tsk/template``), and ``prompts``
(``create_task``, ``update_task``, ``implement_task``) all exist; whole-body
and line-range updates of an existing document go through the generic
``update`` tool in ``general.tools`` (``type="tsk"``), and status changes
go through the generic ``set_status`` tool in ``general.tools``
(``type="tsk"``). Like REQ,
TSK has no ``specmgr://tsk/{id}`` resource -- id-based reads go through the
``get_tsk`` tool only (same rationale as ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
"Expose id-based REQ document reads as a tool (get_req), not a resource" --
TSK never had such a resource to remove in the first place). Likewise, the
former ``specmgr://tsk/list`` resource was replaced by the ``list_tsk``
tool, so that paging parameters could be accepted (feat-13-list-paging).
