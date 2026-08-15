# `biz.dfch.specmgr.req.prompts.update_req`

``@mcp.prompt()``: update_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Requirement (REQ) document by id, using the
existing ``req/tools/`` surface (``get_req``, ``update_req``,
``set_status_req``, ``validate_req``). Unlike an earlier revision of this
prompt, step 1 no longer points at a ``specmgr://req/{id}`` resource -- that
resource was removed in favor of the ``get_req`` tool (feat-7-various-
improvements Task 0.9, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: REQ's lifecycle surface (Task 3.9's design) is
deliberately small -- a whole-body replace (``update_req``) plus a single,
dedicated status-change path (``set_status_req``) -- so the tool-mapping
section below is correspondingly shorter.

## Functions

### `update_req(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the requirement identified by ``id``.

Parameters
----------
id:
    The existing document's specmgr-assigned identifier.
instructions:
    Free-text description of the requested change. When absent, the
    returned instructions tell the LLM to ask the user first rather
    than guessing.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

