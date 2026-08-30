# `biz.dfch.specmgr.feat.prompts.create_feat`

``@mcp.prompt()``: create_feat (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Feature (FEAT) document using the existing
``feat/tools/``/``feat/resources/`` surface (``list_feat``,
``specmgr://feat/template``/``specmgr://feat/example``,
``specmgr://feat/schema``, ``create_feat``, ``validate_feat``).

``create_feat`` (the tool) builds the entire FEAT frontmatter itself
(``id``/``type``/``status``/``created``/``updated``/``version``) -- the
caller only ever supplies body markdown. Unlike every other domain in this
codebase, ``id`` is not a server-generated UUID but a fresh
``feat-NNN-slug`` derived from the H1 title, and ``created``/``updated``
are plain ``YYYY-MM-DD`` dates, not the microsecond timestamp most other
domains use (REQ-004).

Naming note: this prompt is named ``create_feat``, the same name as the
``@mcp.tool()`` in ``feat/tools/create_feat.py``. This is not a collision
-- the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``gol.prompts.create_gol``/``dec.prompts.create_dec``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_feat``, building a ``TodoWrite`` list, eliciting the
mandatory sections and each optional section via the ``question`` tool,
then calling ``create_feat``) -- it never calls
``TodoWrite``/``question``/``list_feat``/``create_feat`` itself, exactly
like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``feat/data/feat_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the FEAT
markdown headings it narrates to the LLM (e.g. ``# Feature: {title}``)
without those colliding with this module's own substitution.

## Functions

### `create_feat(topic: 'str') -> 'str'`

Return instructional text for drafting a new feature about ``topic``.

Parameters
----------
topic:
    Free-text description of the feature to be drafted -- becomes
    the seed for the document's title and overview.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_feat``, or ``create_feat``
    itself -- it only narrates that sequence for the LLM to carry out.

