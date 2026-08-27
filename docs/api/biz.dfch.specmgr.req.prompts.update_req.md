# `biz.dfch.specmgr.req.prompts.update_req`

``@mcp.prompt()``: update_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Requirement (REQ) document by id, using the
existing ``req/tools/`` surface (``get_req``, ``validate_req``) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="req"``). Unlike an earlier revision of this prompt, step 1 no
longer points at a ``specmgr://req/{id}`` resource -- that resource was
removed in favor of the ``get_req`` tool (feat-7-various-improvements
Task 0.9, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614); ``get_req``'s
``raw=True`` parameter serves the line-range flow's line numbers.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: REQ's lifecycle surface (Task 3.9's design) is
deliberately small -- a whole-body or line-range replace (the generic
``update`` tool with ``type="req"``) plus a single, dedicated
status-change path (the generic ``set_status`` tool with ``type="req"``)
-- so the tool-mapping section below is correspondingly shorter.

The actual instructional text lives in its own packaged data file,
``req/data/req_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for markdown headings it narrates to the LLM without those colliding with
this module's own substitution.

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

