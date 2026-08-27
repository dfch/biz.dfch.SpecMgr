# `biz.dfch.specmgr.adr.prompts.update_adr`

``@mcp.prompt()``: update_adr (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing MADR 4.0.0-based ADR by id, using the
existing ``adr/tools/`` surface (``get_adr``, ``update_section``,
``update_frontmatter``, ``option_create``/``option_update``/
``option_delete``, ``validate_adr``) plus the generic ``set_status`` tool
in ``general/tools/`` (always called with ``type="adr"`` for an ADR).

The actual instructional text lives in its own packaged data file,
``adr/data/adr_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the ``specmgr://adr/{id}`` resource-template placeholder it narrates
to the LLM without that colliding with this module's own substitution.

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

