# `biz.dfch.specmgr.rsk.prompts.create_risk`

``@mcp.prompt()``: create_risk (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Risk (RSK) document using the existing
``rsk/tools/``/``rsk/resources/`` surface (``list_rsk``,
``specmgr://rsk/template``/``specmgr://rsk/example``, ``specmgr://rsk/schema``,
``specmgr://rsk/tara``, ``specmgr://rsk/risk-matrix``, ``create_rsk``,
generic ``validate`` tool).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_rsk`` builds the entire RSK frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_risk`` (the issue's literal
wording), not ``create_rsk`` -- deliberately distinct from the
``rsk``-prefixed convention the tools/resources use, per the feature
README's Design Notes (the ``tsk``-prompt precedent of the issue's literal
wording, e.g. ``create_task``). This is not a collision with the
``create_rsk`` ``@mcp.tool()`` either way -- the MCP protocol keeps prompts
and tools in separate registries (``prompts/list`` vs. ``tools/list``).

The actual instructional text lives in its own packaged data file,
``rsk/data/rsk_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the RSK
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_risk(topic: 'str') -> 'str'`

Return instructional text for drafting a new risk about ``topic``.

Parameters
----------
topic:
    Free-text description of the risk to be drafted -- becomes the seed
    for the document's title and its cause/trigger/consequence
    scenario.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

