# `biz.dfch.specmgr.rsk.prompts.update_risk`

``@mcp.prompt()``: update_risk (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Risk (RSK) document by id, using the existing
``rsk/tools/`` surface (``get_rsk``, generic ``validate`` tool) plus the generic
``update``/``set_status`` tools in ``general/tools/`` (called with
``type="rsk"``; ``get_rsk``'s ``raw=True`` parameter serves the line-range
flow's line numbers). There is no ``specmgr://rsk/{id}`` resource to point at
-- id-based reads always go through the ``get_rsk`` tool only (there was no
earlier resource to remove, unlike REQ's own history -- ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: RSK's lifecycle surface is deliberately small
-- a whole-body or line-range replace (the generic ``update`` tool with
``type="rsk"``) plus a single, dedicated status-change path (the generic
``set_status`` tool with ``type="rsk"``) -- so the tool-mapping section
below is correspondingly short, mirroring ``tsk.prompts.update_task``.

Naming note: this prompt is named ``update_risk`` (the issue's literal
wording), not ``update_rsk`` -- see ``create_risk``'s own docstring for the
naming rationale.

The actual instructional text lives in its own packaged data file,
``rsk/data/rsk_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the RSK markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_risk(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the risk identified by ``id``.

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

