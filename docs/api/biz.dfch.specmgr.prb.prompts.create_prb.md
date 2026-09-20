# `biz.dfch.specmgr.prb.prompts.create_prb`

``@mcp.prompt()``: create_prb (Task 3.14, feat-132-prb-update Phase 2).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Problem Statement (PRB) document using the
existing ``prb/tools/``/``prb/resources/`` surface (``list_prb``,
``specmgr://prb/template``/``specmgr://prb/example``, ``specmgr://prb/schema``,
``create_prb``, generic ``validate`` tool), plus -- when an optional QA id
is supplied -- the ``qa/tools/`` surface (``get_qa``) to carry over already-
answered 5W2H questions from that linked Question and Answer (QA) interview.

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_prb`` builds the entire PRB frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_prb``, the same name as the
``@mcp.tool()`` in ``prb/tools/create_prb.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``req.prompts.create_req``).

This prompt only ever *narrates* a 13-step interview flow (checking for a
duplicate via `list_prb`, fetching an optionally-linked QA document via
`get_qa` and scanning it for already-answered 5W2H questions, building a
``TodoWrite`` list, eliciting only the still-unanswered 5W2H answers via the
``question`` tool, synthesizing `Summary`, drafting and confirming `Gap`,
optionally asking for `Impact`/`Future State`/`References`/
`More Information`, composing the mandatory Problem Statement lead sentence
-- derived from the linked QA's answers and confirmed, or elicited fresh in
standalone mode -- then calling `create_prb`) -- it never calls
``TodoWrite``/``question``/``list_prb``/``get_qa``/``create_prb`` itself,
exactly like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``prb/data/prb_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``/``$qa_id``), not ``str.format``, precisely so the instructions
file itself is free to use plain, unescaped ``{...}`` braces for the PRB
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_prb(topic: 'str', qa_id: 'str | None' = None) -> 'str'`

Return instructional text for drafting a new problem statement about ``topic``.

Parameters
----------
topic:
    Free-text description of the problem statement to be drafted --
    becomes the seed for the document's title and interview.
qa_id:
    Optional id of an existing Question and Answer (QA) document whose
    already-answered 5W2H questions should be carried over into
    ``## Current State`` instead of being re-asked. When absent, the
    returned instructions tell the LLM to proceed standalone, asking
    all 7 5W2H questions.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_prb``, ``get_qa``, or
    ``create_prb`` itself -- it only narrates that sequence for the
    LLM to carry out.

