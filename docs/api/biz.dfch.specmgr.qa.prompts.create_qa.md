# `biz.dfch.specmgr.qa.prompts.create_qa`

``@mcp.prompt()``: create_qa (Phase 4, Task 4.3).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Question and Answer (QA) document using the
existing ``qa/tools/``/``qa/resources/`` surface (``specmgr://qa/list``,
``specmgr://qa/template``/``specmgr://qa/example``, ``specmgr://qa/schema``,
``create_qa``, ``validate_qa``). Structural shape ported 1:1 from
``req.prompts.create_req``, with the instructional content rewritten to
describe QA's own schema instead of REQ's.

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_qa`` builds the entire QA frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_qa``, the same name as the
``@mcp.tool()`` in ``qa/tools/create_qa.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

## Functions

### `create_qa(topic: 'str') -> 'str'`

Return instructional text for drafting a new QA document about ``topic``.

Parameters
----------
topic:
    Free-text description of the interview's subject -- becomes the
    seed for the document's title and introduction.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

