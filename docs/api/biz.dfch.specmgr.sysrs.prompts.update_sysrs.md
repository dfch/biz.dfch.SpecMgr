# `biz.dfch.specmgr.sysrs.prompts.update_sysrs`

``@mcp.prompt()``: update_sysrs (Task 5.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing System Requirements Specification (SYSRS)
document by id, using the existing ``sysrs/tools/`` surface (``get_sysrs``,
``validate_sysrs``) plus the generic ``update``/``set_status``/
``set_classification`` tools in ``general/tools/`` (called with
``type="sysrs"``; ``get_sysrs``'s ``raw=True`` parameter serves the
line-range flow's line numbers). There is no ``specmgr://sysrs/{id}``
resource to point at -- id-based reads always go through the ``get_sysrs``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

``sysrs`` is, like SOP/VCR, built with **no** per-domain mutation tools at
all: there is no ``update_sysrs``/``set_status_sysrs`` tool -- every body
change goes through the generic ``update`` tool with ``type="sysrs"``
(whole-body or line-range), every status change goes through the generic
``set_status`` tool with ``type="sysrs"``, and every classification change
goes through the generic ``set_classification`` tool with ``type="sysrs"``
(ADR 36905d5b-8057-4294-8665-c7eed5534db0). The narration names those
generic tools explicitly, never a per-domain ``update_sysrs(...)``/
``set_status_sysrs(...)`` call shape. A change touching ``## Requirements``
reads the cross-cutting ``specmgr://iso25010`` resource first, for the
same nine canonical characteristic names/REQ placement rule
``create_sysrs`` uses.

Like ``dec.prompts.update_dec``/``sop.prompts.update_sop`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via ``get_sysrs``, showing which sections are present vs. empty, reading
``specmgr://iso25010`` when ``## Requirements`` is touched, eliciting
revisions via the ``question`` tool, then calling the generic ``update``
tool with ``type="sysrs"``, with the generic ``set_status``/
``set_classification`` tools with ``type="sysrs"`` mentioned as separate,
optional follow-ups) -- it never calls
``get_sysrs``/``question``/``update``/``set_status``/``set_classification``
itself, exactly like every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``sysrs/data/sysrs_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the SYSRS markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_sysrs(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the SYSRS identified by ``id``.

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
    the MCP SDK), not itself a tool call. This function never calls
    ``get_sysrs``, ``question``, ``update``, ``set_status``, or
    ``set_classification`` itself -- it only narrates that sequence
    for the LLM to carry out.

