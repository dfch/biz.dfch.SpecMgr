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

"""``@mcp.prompt()``: create_adr (.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md §11).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new MADR 4.0.0-based ADR using the existing
``adr/tools/`` surface (``create_adr``, ``option_create``, ``set_status``,
``validate_adr``).

Naming note: this prompt is named ``create_adr``, the same name as the
``@mcp.tool()`` in ``adr/tools/create_adr.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are drafting a new Architecture Decision Record (ADR) about: {topic}

Follow this MADR 4.0.0-based structure and tool sequence exactly. Do not
write raw markdown yourself -- every change to the document goes through
the specmgr MCP tools listed below.

## 0. Check for an existing ADR on this topic first
Read the `specmgr://adr/list` resource before creating anything. If an
ADR with a similar title or topic already exists, tell the user about it
and ask whether they want to revise that one (via the `update_adr`
prompt) instead of creating a duplicate. Only proceed to step 1 if this is
genuinely a new decision.

## 1. Structure recap
- `# {{title}}` -- H1, mandatory.
- `## Context and Problem Statement` -- mandatory.
- `## Decision Drivers` -- optional.
- `## Considered Options` -- mandatory, a freeform bullet list of option
  names (kept independent of the `Option` sub-sections in step 3 -- no
  consistency check is enforced between them, but keep them aligned in
  practice).
- `## Decision Outcome` -- mandatory: the chosen option and why.
- `### Consequences` -- optional, under Decision Outcome.
- `### Confirmation` -- optional, under Decision Outcome.
- `## Pros and Cons of the Options` -- derived automatically from whatever
  `Option` sub-sections exist; never write it directly.
- `## More Information` -- optional, always last.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the context/problem
statement, decision drivers (if any), the list of considered options, the
chosen outcome and its rationale, and optionally decision-makers/
consulted/informed.

## 3. Tool call sequence
1. Call `create_adr(frontmatter, body)` first:
   - `frontmatter.status` = `"draft"` or `"proposed"` (never invent an
     `id` -- it is always server-assigned).
   - `body.title`, `body.context_and_problem_statement`,
     `body.considered_options`, `body.decision_outcome` are mandatory and
     must be non-blank; `body.decision_drivers`/`consequences`/
     `confirmation`/`more_information` are optional.
   - Leave `body.options` empty at this point.
2. For each considered option worth writing up in detail, call
   `option_create(id, partial_title, value)` once per option -- write
   `value` as a short intro paragraph followed by
   `- Good, because ...` / `- Bad, because ...` / `- Neutral, because ...`
   bullets. Option numbering is assigned automatically, is never reused,
   and is never renumbered.
3. If the decision is being finalized now rather than left as a draft,
   call `set_status(id, "accepted")` (or `"rejected"`, or
   `"proposed"`, as appropriate).
4. Always finish by calling `validate_adr(id)` to self-correct before
   reporting success back to the user.

## 4. Later revisions
Any later change to this ADR should go through the `update_adr` prompt
(or directly through `update_section`/`update_frontmatter`/`option_*`),
not by re-running this prompt.

Decision-makers: {decision_makers}
Consulted: {consulted}
Informed: {informed}
"""


@mcp.prompt(
    name="create_adr",
    title="Create an ADR",
    description=(
        "Guides the LLM through checking for an existing similar ADR, gathering the "
        "required information, and driving create_adr/option_create/set_status/"
        "validate_adr to author a new MADR-4.0.0-based Architecture Decision Record."
    ),
)
def create_adr(
    topic: str,
    decision_makers: str | None = None,
    consulted: str | None = None,
    informed: str | None = None,
) -> str:
    """Return instructional text for drafting a new ADR about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the decision to be made -- becomes the
        seed for ``title``/``context_and_problem_statement``.
    decision_makers:
        Pre-known ``decision-makers`` frontmatter value, if any; otherwise
        the returned instructions tell the LLM to ask the user.
    consulted:
        Pre-known ``consulted`` frontmatter value, if any.
    informed:
        Pre-known ``informed`` frontmatter value, if any.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    return _INSTRUCTIONS_TEMPLATE.format(
        topic=topic,
        decision_makers=decision_makers or "(not given -- ask the user, or omit)",
        consulted=consulted or "(not given -- ask the user, or omit)",
        informed=informed or "(not given -- ask the user, or omit)",
    )
