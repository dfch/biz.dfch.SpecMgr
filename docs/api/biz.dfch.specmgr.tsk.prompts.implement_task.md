# `biz.dfch.specmgr.tsk.prompts.implement_task`

``@mcp.prompt()``: implement_task (Task 3.14).

Returns instructional text -- not itself a tool call -- that guides an LLM
through actually *working* an existing Task List (TSK) document's checklist:
reading it via ``get_tsk``, building an in-session ``TodoWrite`` list from
its ``items``, and using the ``question`` tool to resolve ambiguity for any
item before starting work on it. Unlike ``create_task``/``update_task``,
there is no ``req``/``adr`` precedent for this prompt -- it is genuinely new
(REQ-006/ACC-006 in the feature README).

This is a **thin-precedent** prompt: like ``req.prompts.create_req``'s one
line "Make a todo list and use the question tool." and
``adr.prompts.create_adr_test``'s similar line, the instructional text below
merely *narrates* two host-provided tools by name -- ``TodoWrite`` and
``question`` -- neither of which is implemented anywhere in this repo as an
``@mcp.tool()``. This module does not, and must not, define stub tools of
those names: they are assumed to be supplied by the MCP host/client the LLM
is running in, exactly like every other reference to them in this codebase.
``implement_task`` itself never calls ``get_tsk``/``TodoWrite``/``question``
either -- it only returns the text instructing an LLM to do so.

## Functions

### `implement_task(id: 'str') -> 'str'`

Return instructional text for working the checklist of the task list identified by ``id``.

Parameters
----------
id:
    The existing document's specmgr-assigned identifier.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``get_tsk``, ``TodoWrite``, or ``question`` itself -- it only
    narrates that sequence for the LLM to carry out.

