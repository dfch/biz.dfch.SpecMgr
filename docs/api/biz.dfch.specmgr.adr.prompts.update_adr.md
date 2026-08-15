# `biz.dfch.specmgr.adr.prompts.update_adr`

``@mcp.prompt()``: update_adr (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing MADR 4.0.0-based ADR by id, using the
existing ``adr/tools/`` surface (``get_adr``, ``update_section``,
``update_frontmatter``, ``set_status``, ``option_create``/``option_update``/
``option_delete``, ``validate_adr``).

## Functions

### `update_adr(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the ADR identified by ``id``.

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

