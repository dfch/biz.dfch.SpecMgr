# `biz.dfch.specmgr.sysrs.prompts.create_sysrs`

``@mcp.prompt()``: create_sysrs (Task 5.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new System Requirements Specification (SYSRS)
document using the existing ``sysrs/tools/``/``sysrs/resources/`` surface
(``list_sysrs``, ``specmgr://sysrs/template``/``specmgr://sysrs/example``,
``specmgr://sysrs/schema``, ``create_sysrs``, generic ``validate`` tool) plus the
existing cross-cutting ``specmgr://iso25010`` resource (read before grouping
``## Requirements`` by its nine canonical characteristic names).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_sysrs`` builds the entire SYSRS frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown (and ``status`` is always fixed
to ``"draft"``). The body aggregates already-existing specmgr artifacts
(``gol``, ``prb``, ``qa``, ``uc``, ``req``, ``rsk``, ``dec``/``adr``,
``vcr``) into one coherent, navigable specification via per-section
type-tagged cross-reference lists, rather than duplicating their content.

Naming note: this prompt is named ``create_sysrs``, the same name as the
``@mcp.tool()`` in ``sysrs/tools/create_sysrs.py``. This is not a collision
-- the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``dec.prompts.create_dec``/``gol.prompts.create_gol``/``sop.prompts.create_sop``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_sysrs``, building a ``TodoWrite`` list, reading
``specmgr://iso25010`` before grouping ``## Requirements``, eliciting the
mandatory sections and each optional section via the ``question`` tool,
then calling ``create_sysrs``) -- it never calls
``TodoWrite``/``question``/``list_sysrs``/``create_sysrs`` itself, exactly
like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``sysrs/data/sysrs_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the SYSRS
markdown headings it narrates to the LLM (e.g.
``# System Requirements Specification: {title}``) without those colliding
with this module's own substitution.

## Functions

### `create_sysrs(topic: 'str') -> 'str'`

Return instructional text for drafting a new SYSRS about ``topic``.

Parameters
----------
topic:
    Free-text description of the system requirements specification to
    be drafted -- becomes the seed for the document's title and
    ``## System Purpose``.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_sysrs``, or ``create_sysrs``
    itself -- it only narrates that sequence for the LLM to carry out.

