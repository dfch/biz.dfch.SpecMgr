# `biz.dfch.specmgr.tsk.prompts.update_task`

``@mcp.prompt()``: update_task (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Task List (TSK) document by id, using the
existing ``tsk/tools/`` surface (``get_tsk``, generic ``validate`` tool) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called
with ``type="tsk"``; ``get_tsk``'s ``raw=True`` parameter serves the
line-range flow's line numbers). There is no
``specmgr://tsk/{id}`` resource to point at -- id-based reads always went
through the ``get_tsk`` tool only (there was no earlier resource to remove,
unlike REQ's own history -- ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: TSK's lifecycle surface is deliberately small
-- a whole-body or line-range replace (the generic ``update`` tool with
``type="tsk"``) plus a single, dedicated status-change path (the generic
``set_status`` tool with ``type="tsk"``) -- so the tool-mapping section
below is correspondingly short, mirroring ``req.prompts.update_req``.

Naming note: this prompt is named ``update_task`` (the issue's literal
wording), not ``update_tsk`` -- see ``create_task``'s own docstring for the
naming rationale.

The actual instructional text lives in its own packaged data file,
``tsk/data/tsk_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the TSK markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_task(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the task list identified by ``id``.

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

