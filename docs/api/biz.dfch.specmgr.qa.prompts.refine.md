# `biz.dfch.specmgr.qa.prompts.refine`

``@mcp.prompt()``: refine (Phase 4, Task 4.3).

Returns instructional text -- not itself a tool call -- that guides an LLM
through adding a fresh batch of open interview questions to an *existing*
Question and Answer (QA) document, one or more of the nine ISO/IEC
25010:2023 quality characteristics at a time (e.g. "5 questions each about
Functional Suitability, Security, Maintainability", or "3 questions for
each of the 9 main characteristics"). Unlike ``create_qa``/``update_qa``,
this prompt never elicits or writes an actual answer itself -- each new
question is appended with an empty ``_(awaiting response)_`` placeholder in
place of an answer, for a human to fill in directly in the document
afterwards.

Like ``update_qa``, this targets an existing document via the ``qa/tools/``
surface (``get_qa``, ``update_qa``, ``list_qa`` -- the last to resolve a
title to an id when no id is given) and the ``specmgr://iso25010`` resource
(to ground each new question in that characteristic's actual definition).
This prompt deliberately does not
implement or call any ``/resolve`` follow-up step itself -- it only tells
the human user, in its final instructions to the LLM, that such a step
exists and comes next.

The actual instructional text lives in its own packaged data file,
``qa/data/qa_refine_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text`` -- the same
example/template/schema packaging convention this domain already uses
(``qa_example.md``/``qa_template.md``/``qa_schema.json``), rather than as
an inline Python string constant like every other prompt in this codebase.
Placeholders use ``string.Template`` (``$id_or_name``/``$scope``), not
``str.format``, precisely so the instructions file itself is free to use
plain, unescaped ``{...}`` braces for the Q&A markdown placeholders it
narrates to the LLM (e.g. ``{the question}``) without those colliding with
this module's own substitution.

## Functions

### `refine(id_or_name: 'str', scope: 'str | None' = None) -> 'str'`

Return instructional text for adding new interview questions to an existing QA document.

Parameters
----------
id_or_name:
    Either the target document's specmgr-assigned id, or a free-text
    title/topic to look up via the `list_qa` tool when no id is known.
scope:
    Free-text description of which characteristics to target and how
    many questions to add to each, e.g. "5 questions each about
    Functional Suitability, Security, Maintainability" or "3 questions
    for each of the 9 main characteristics". When absent or ambiguous,
    the returned instructions tell the LLM to ask the user via the
    `question` tool rather than guessing.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

