# `biz.dfch.specmgr.req.prompts.update_req`

``@mcp.prompt()``: update_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Requirement (REQ) document by id, using the
existing ``req/tools/``/``req/resources/`` surface (``specmgr://req/{id}``,
``update_req``, ``set_status_req``, ``validate_req``).

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

