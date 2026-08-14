# `biz.dfch.specmgr.req.prompts.create_req`

``@mcp.prompt()``: create_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Requirement (REQ) document using the existing
``req/tools/``/``req/resources/`` surface (``specmgr://req/list``,
``specmgr://req/template``/``specmgr://req/example``, ``specmgr://req/schema``,
``create_req``, ``validate_req``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_req`` builds the entire REQ frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_req``, the same name as the
``@mcp.tool()`` in ``req/tools/create_req.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

## Functions

### `create_req(topic: 'str') -> 'str'`

Return instructional text for drafting a new requirement about ``topic``.

Parameters
----------
topic:
    Free-text description of the requirement to be drafted -- becomes
    the seed for the document's title and requirement statement.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

