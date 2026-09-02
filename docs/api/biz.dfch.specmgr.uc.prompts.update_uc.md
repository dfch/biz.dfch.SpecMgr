# `biz.dfch.specmgr.uc.prompts.update_uc`

``@mcp.prompt()``: update_uc (feat-57-uc-commands).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Use Case (UC) document by id, using the
existing ``uc/tools/`` surface (``get_uc``, ``validate_uc``) plus the
generic ``update``/``set_status``/``set_classification`` tools in
``general/tools/`` (called with ``type="uc"``). UC has no
``specmgr://uc/{id}`` resource -- id-based reads are ``get_uc``-only, ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614; ``get_uc``'s ``raw=True`` parameter
serves the line-range flow's line numbers.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: UC's lifecycle surface is deliberately
small, the same shape as REQ's -- a whole-body or line-range replace (the
generic ``update`` tool with ``type="uc"``), a dedicated status-change
path (the generic ``set_status`` tool with ``type="uc"``), and a dedicated
classification-change path (the generic ``set_classification`` tool with
``type="uc"``) -- so the tool-mapping section below is correspondingly
short.

The actual instructional text lives in its own packaged data file,
``uc/data/uc_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for markdown headings it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_uc(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the use case identified by ``id``.

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

