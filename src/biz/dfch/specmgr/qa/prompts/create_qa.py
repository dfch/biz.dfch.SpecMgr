# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``@mcp.prompt()``: create_qa (Phase 4, Task 4.3).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Question and Answer (QA) document using the
existing ``qa/tools/``/``qa/resources/`` surface (``specmgr://qa/list``,
``specmgr://qa/template``/``specmgr://qa/example``, ``specmgr://qa/schema``,
``create_qa``, ``validate_qa``). Structural shape ported 1:1 from
``req.prompts.create_req``, with the instructional content rewritten to
describe QA's own schema instead of REQ's.

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_qa`` builds the entire QA frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_qa``, the same name as the
``@mcp.tool()`` in ``qa/tools/create_qa.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are drafting a new Question and Answer (QA) document about: {topic}

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_qa` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_qa` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing QA document on this topic first
Read the `specmgr://qa/list` resource before creating anything. If a QA
document with a similar title or topic already exists, tell the user
about it and ask whether they want to revise that one (via the
`update_qa` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new interview.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {{title}}` -- H1, mandatory, free-form.
- `## General` -- mandatory, always present.
  - `### Introduction` -- mandatory. Free-form prose framing the
    interview: who was interviewed, when, and why.
  - `### Raw Requirements` -- mandatory. Free-form, pre-existing raw
    requirement notes (e.g. from a wiki page), preserved verbatim for
    traceability. May simply note there were none.
- Nine fixed `##` category headings, each always present, in this exact
  order and exact wording (ISO/IEC 25010:2023 quality characteristics):
  `Functional Suitability`, `Performance Efficiency`, `Compatibility`,
  `Interaction Capability`, `Reliability`, `Security`,
  `Maintainability`, `Flexibility`, `Safety`. Do not rename, reorder, or
  omit any of these nine headings -- a category with nothing to ask yet
  is still written as an empty heading with no `###` children under it.
  Under each category heading, add zero or more `### {{question-ish
  heading}}` Q&A pairs (a free-form H3 per pair). Each pair may
  optionally include, in this order:
  - an HTML comment (`<!-- ... -->`) directly under the H3, giving
    context (e.g. when/by whom this was elicited);
  - a `#### Requirement` callout: free-form, agent-authored prose
    promoting this answer to a concrete, testable requirement, only
    when you judge the answer implies one -- there is no fixed shape
    for this callout's content;
  - `> {{the interviewer's question}}` as a block quote;
  - the interviewee's free-form prose answer, as plain paragraphs
    immediately after the block quote (no heading of its own).
  All four of comment/requirement/question/answer are optional on every
  Q&A pair -- include whichever apply.
- `## More Information` -- optional freeform supplementary text (e.g.
  noting which category was deliberately left empty, and why).

## 2. Gather information before calling any tool
Elicit (asking the user if not already given) the introduction/context,
any pre-existing raw requirements, and then work through the nine
ISO/IEC 25010:2023 categories one at a time, asking plausible
characteristic-relevant questions and recording the answers. Not every
category needs a question -- an internal-only change, for example, may
legitimately leave `Compatibility` empty. Only add a `#### Requirement`
callout when an answer clearly implies a concrete, testable requirement.

## 3. Use the template/example/schema as references
Fetch `specmgr://qa/template` or `specmgr://qa/example` as a starting
point/style reference, then check `specmgr://qa/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there, and do not rename or reorder the nine fixed category headings.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above.
2. Call `create_qa(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_qa(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_qa` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 5. Later revisions
Any later change to this QA document should go through the `update_qa`
prompt (or directly through `update_qa`/`set_status_qa`), not by
re-running this prompt.
"""


@mcp.prompt(
    name="create_qa",
    title="Create a QA document",
    description=(
        "Guides the LLM through checking for an existing similar QA document, gathering answers "
        "to ISO/IEC 25010:2023 characteristic-relevant questions, and driving "
        "create_qa/validate_qa to author a new QA document."
    ),
)
def create_qa(topic: str) -> str:
    """Return instructional text for drafting a new QA document about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the interview's subject -- becomes the
        seed for the document's title and introduction.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    return _INSTRUCTIONS_TEMPLATE.format(topic=topic)
