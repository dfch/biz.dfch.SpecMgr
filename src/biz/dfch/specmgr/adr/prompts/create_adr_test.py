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

"""``@mcp.prompt()``: create_adr_test (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Experimental, strictly step-gated variant of ``create_adr`` (see
``adr/prompts/create_adr.py``), kept as a *separate* prompt -- not a
replacement -- so the two can be registered side by side and compared: the
same underlying MADR structure and ``adr/tools/`` sequence, but rewritten
as a series of hard numbered gates ("do not proceed to gate N+1 until gate
N's exit condition is met", "never fabricate a value to pass a gate")
instead of the softer step-by-step narration used by ``create_adr``. This
lets a caller switch between ``create_adr`` and ``create_adr_test`` for
the same topic and observe whether the stricter phrasing measurably
improves compliance (e.g. fewer fabricated mandatory-field values, fewer
skipped duplicate checks) -- see the conversation in
.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11 for the rationale.

Naming note: like ``create_adr`` itself, this prompt's name does not
collide with any ``@mcp.tool()`` -- ``adr/tools/`` has no ``create_adr_test``
tool; the underlying tool sequence driven by this prompt is unchanged
(``create_adr``, ``option_create``, ``set_status``, ``validate_adr``).
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
[STRICT STEP-GATED VARIANT -- for A/B comparison against the `create_adr` prompt]

You are drafting a new Architecture Decision Record (ADR) about:

"{topic}"

You MUST follow the numbered gates below IN ORDER. A gate is a hard stop:
you may not perform any action described in a later gate until the
current gate's exit condition is explicitly satisfied. Never fabricate an
answer in order to pass a gate -- if information is missing, stop and ask
the user, then wait for their reply before continuing. Do not write raw
markdown yourself -- every change to the document goes through the
specmgr MCP tools named below.

## GATE 0 -- Duplicate check
Action: read the `specmgr://adr/list` resource.
Exit condition: EITHER (a) you have confirmed no existing ADR covers this
topic, OR (b) you found one, told the user about it, offered the
`update_adr`/`update_adr_test` prompt instead, and the user has explicitly
told you to proceed with a new ADR anyway.
Do not proceed to GATE 1 until this exit condition is met.

## GATE 1 -- Structure acknowledgement
Action: silently confirm you know the MADR 4.0.0 structure:
- `# {{title}}` -- H1, mandatory.
- `## Context and Problem Statement` -- mandatory.
- `## Decision Drivers` -- optional.
- `## Considered Options` -- mandatory, a freeform bullet list of option
  names (kept independent of the `Option` sub-sections created later via
  `option_create` -- no consistency check is enforced between them, but
  keep them aligned in practice).
- `## Decision Outcome` -- mandatory: the chosen option and why.
- `### Consequences` -- optional, under Decision Outcome.
- `### Confirmation` -- optional, under Decision Outcome.
- `## Pros and Cons of the Options` -- derived automatically from
  whatever `Option` sub-sections exist; never write it directly.
- `## More Information` -- optional, always last.
Exit condition: none of these headings are novel to you. This gate has no
observable output of its own -- it exists to force the recap before
elicitation in GATE 2.

## GATE 2 -- Mandatory field checklist (the hard gate)
Action: for EACH of the four mandatory fields below, either use a value
the user has already given you verbatim in this conversation, or
explicitly ask the user for it and wait for their reply. Do not invent,
infer, or paraphrase-and-guess a value for any of these four:
  [ ] title
  [ ] context_and_problem_statement
  [ ] considered_options
  [ ] decision_outcome
Exit condition: all four checklist items are backed by an explicit user
answer, never a model guess. Optional fields (decision_drivers,
consequences, confirmation, more_information, and the
decision-makers/consulted/informed frontmatter below) may be asked for
once and omitted if the user declines to answer -- they are not gated.
Use the todo tool. Do not use the question tool or call any adr tools
until this gate is passed.

## GATE 3 -- Tool call sequence (only after GATE 2 has passed)
1. Call `create_adr(frontmatter, body)` first:
   - `frontmatter.status` = `"draft"` or `"proposed"` (never invent an
     `id` -- it is always server-assigned).
   - `body.title`, `body.context_and_problem_statement`,
     `body.considered_options`, `body.decision_outcome` must be exactly
     the GATE 2 checklist values; `body.decision_drivers`/`consequences`/
     `confirmation`/`more_information` are optional.
   - Leave `body.options` empty at this point.
2. For each considered option worth writing up in detail, call
   `option_create(id, partial_title, value)` once per option -- write
   `value` as a short intro paragraph followed by
   `- Good, because ...` / `- Bad, because ...` / `- Neutral, because ...`
   bullets. Option numbering is assigned automatically, is never reused,
   and is never renumbered.
3. If, and only if, the user explicitly asked you to finalize the
   decision now rather than leave it as a draft, call
   `set_status(id, "accepted")` (or `"rejected"`, or `"proposed"`).
4. Mandatory, always last: call `validate_adr(id)` to self-correct before
   reporting success back to the user.
Exit condition: `create_adr` succeeded, every considered option worth
writing up has an `Option` sub-section, and `validate_adr` returned
successfully. If step 1 fails validation, do not retry with a fabricated
or paraphrased value for the rejected field -- return to GATE 2 and
re-elicit that field from the user instead.

## GATE 4 -- Handoff
Tell the user the new ADR's id and title, and that any later change goes
through the `update_adr`/`update_adr_test` prompt (or directly through
`update_section`/`update_frontmatter`/`option_*`), not by re-running this
prompt.

Decision-makers: {decision_makers}
Consulted: {consulted}
Informed: {informed}
"""


@mcp.prompt(
    name="create_adr_test",
    title="Create an ADR (step-gated test variant)",
    description=(
        "Experimental, strictly step-gated variant of create_adr for A/B comparison: "
        "the same MADR-4.0.0 structure and create_adr/option_create/set_status/validate_adr "
        "tool sequence, rewritten as hard numbered gates instead of narrated steps."
    ),
)
def create_adr_test(
    topic: str,
    decision_makers: str | None = None,
    consulted: str | None = None,
    informed: str | None = None,
) -> str:
    """Return step-gated instructional text for drafting a new ADR about ``topic``.

    See ``create_adr`` (``adr/prompts/create_adr.py``) for the non-gated
    baseline this variant is meant to be compared against; the parameters
    and returned-value contract are identical.

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
