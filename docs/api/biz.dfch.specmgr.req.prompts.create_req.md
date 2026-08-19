# `biz.dfch.specmgr.req.prompts.create_req`

``@mcp.prompt()``: create_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Requirement (REQ) document using the existing
``req/tools/``/``req/resources/`` surface (``list_req``,
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

The actual instructional text lives in its own packaged data file,
``req/data/req_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the REQ
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

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

