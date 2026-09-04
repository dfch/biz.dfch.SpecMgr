# `biz.dfch.specmgr.tsk.prompts.create_task`

``@mcp.prompt()``: create_task (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Task List (TSK) document using the existing
``tsk/tools/``/``tsk/resources/`` surface (``list_tsk``,
``specmgr://tsk/template``/``specmgr://tsk/example``, ``specmgr://tsk/schema``,
``create_tsk``, generic ``validate`` tool).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_tsk`` builds the entire TSK frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_task`` (the issue's literal
wording), not ``create_tsk`` -- deliberately distinct from the
``tsk``-prefixed convention the tools/resources use, per the feature
README's Design Notes. This is not a collision with the ``create_tsk``
``@mcp.tool()`` either way -- the MCP protocol keeps prompts and tools in
separate registries (``prompts/list`` vs. ``tools/list``).

The actual instructional text lives in its own packaged data file,
``tsk/data/tsk_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the TSK
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_task(topic: 'str') -> 'str'`

Return instructional text for drafting a new task list about ``topic``.

Parameters
----------
topic:
    Free-text description of the task list to be drafted -- becomes
    the seed for the document's title and checklist items.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

