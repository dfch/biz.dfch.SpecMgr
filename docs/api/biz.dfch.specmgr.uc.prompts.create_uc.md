# `biz.dfch.specmgr.uc.prompts.create_uc`

``@mcp.prompt()``: create_uc (feat-57-uc-commands).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Use Case (UC) document using the existing
``uc/tools/``/``uc/resources/`` surface (``list_uc``,
``specmgr://uc/template``/``specmgr://uc/example``, ``specmgr://uc/schema``,
``create_uc``, ``validate_uc``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_uc`` builds the entire UC frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_uc``, the same name as the
``@mcp.tool()`` in ``uc/tools/create_uc.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

The actual instructional text lives in its own packaged data file,
``uc/data/uc_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the UC
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_uc(topic: 'str') -> 'str'`

Return instructional text for drafting a new use case about ``topic``.

Parameters
----------
topic:
    Free-text description of the use case to be drafted -- becomes
    the seed for the document's title and goal in context.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

