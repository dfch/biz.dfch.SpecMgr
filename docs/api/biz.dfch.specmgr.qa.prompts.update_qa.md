# `biz.dfch.specmgr.qa.prompts.update_qa`

``@mcp.prompt()``: update_qa (Phase 4, Task 4.3).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Question and Answer (QA) document by id, using
the existing ``qa/tools/`` surface (``get_qa``, ``update_qa``,
``set_status_qa``, ``validate_qa``). Structural shape ported 1:1 from
``req.prompts.update_req``, with the instructional content rewritten to
describe QA's own schema and lifecycle instead of REQ's. Like ``get_req``,
step 1 points at the ``get_qa`` tool, not a ``specmgr://qa/{id}`` resource
-- there is no such resource; see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: QA's lifecycle surface is deliberately small
-- a whole-body replace (``update_qa``) plus a single, dedicated
status-change path (``set_status_qa``) -- so the tool-mapping section below
is correspondingly shorter.

The actual instructional text lives in its own packaged data file,
``qa/data/qa_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the QA markdown headings it narrates to the LLM without those
colliding with this module's own substitution.

## Functions

### `update_qa(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the QA document identified by ``id``.

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

