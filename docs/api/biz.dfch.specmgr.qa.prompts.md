# `biz.dfch.specmgr.qa.prompts`

MCP prompt registrations for Question and Answer (QA) documents (Phase 4, Task 4.3).

``create_qa`` guides drafting a brand-new QA document. ``update_qa`` guides
revising an existing one by id. Both return instructional text, not tool
calls themselves -- mirroring ``req.prompts``'s own shape. Import this
package to register all QA prompts against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.qa import prompts  # noqa: F401 (side-effects only)
