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

"""``@mcp.prompt()``: update_adr_test (doc/adr-tool-plan.md §11).

Experimental, strictly step-gated variant of ``update_adr`` (see
``adr/prompts/update_adr.py``), kept as a *separate* prompt -- not a
replacement -- so the two can be registered side by side and compared:
the same underlying read-first/map-to-tool/validate-last flow, but
rewritten as a series of hard numbered gates ("do not proceed to gate
N+1 until gate N's exit condition is met", "never fabricate a value to
pass a gate") instead of the softer step-by-step narration used by
``update_adr``. This lets a caller switch between ``update_adr`` and
``update_adr_test`` for the same revision and observe whether the
stricter phrasing measurably improves compliance (e.g. always reading
current state first, never guessing at an unspecified change) -- see
the conversation in doc/adr-tool-plan.md §11 for the rationale.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
[STRICT STEP-GATED VARIANT -- for A/B comparison against the `update_adr` prompt]

You are revising an existing Architecture Decision Record (ADR), id: {id}

Requested change: {instructions}

You MUST follow the numbered gates below IN ORDER. A gate is a hard stop:
you may not perform any action described in a later gate until the
current gate's exit condition is explicitly satisfied. Never fabricate a
value in order to pass a gate. Do not write raw markdown yourself --
every change to the document goes through the specmgr MCP tools named
below.

## GATE 0 -- Read current state (mandatory, no exceptions)
Action: call `get_adr(id)` (or read the `specmgr://adr/{{id}}` resource).
Exit condition: you have the document's actual current frontmatter,
body, and options in hand. Never assume prior state from earlier in this
conversation -- the on-disk file is always the source of truth and may
have been hand-edited since you last saw it.
Do not call any write tool before this gate passes, even for a
seemingly-obvious change.

## GATE 1 -- Confirm the requested change
If "Requested change" above literally says "(not given)": stop here, ask
the user what they want to change, and wait for their reply before
continuing. Do not guess a plausible-sounding change and proceed anyway.
Exit condition: you have an explicit, user-stated change to make.

## GATE 2 -- Map the change to exactly one tool family
Pick the single right tool for the confirmed change -- do not call a
broader set of tools than the confirmed change actually implicates:
- A change to prose in `context_and_problem_statement`,
  `decision_drivers`, `considered_options`, `decision_outcome`,
  `consequences`, `confirmation`, `more_information`, or `title` ->
  `update_section(id, key, value)`. A blank string or the literal
  `"REMOVE"` clears an *optional* section; this is rejected with an
  error for a *mandatory* one (`title`/`context_and_problem_statement`/
  `considered_options`/`decision_outcome`).
- A change to `status` (e.g. accepting/rejecting/deprecating the
  decision, or marking it superseded) -> `set_status(id, status,
  superseded_by=...)`. Never use `update_frontmatter` for a status-only
  change.
- Any other frontmatter change (`date`, `decision_makers`, `consulted`,
  `informed`) -> `update_frontmatter(id, frontmatter)`. This is a
  **whole-object replace**: you MUST carry forward every field from
  GATE 0's read that you are not intentionally changing, or it is
  silently dropped. `id` itself is always preserved automatically by the
  tool regardless of what you submit.
- Adding a new considered option's pros/cons write-up ->
  `option_create(id, partial_title, value)`.
- Revising an existing option's content -> `option_update(id,
  full_title, value)`.
- Removing an option entirely -> `option_delete(id, full_title)`. This
  never renumbers or reorders the remaining options -- deleting one
  leaves a permanent gap in the numbering.
Exit condition: exactly the tool call(s) implied by the confirmed change
have been made -- nothing broader, nothing skipped.

## GATE 3 -- Validate before reporting success
Action: call `validate_adr(id)`.
Exit condition: it returns successfully. If it raises, fix the
offending change (re-enter GATE 2 with corrected input) before telling
the user anything succeeded.
Do not report success to the user until this gate passes.
"""


@mcp.prompt(
    name="update_adr_test",
    title="Update an ADR (step-gated test variant)",
    description=(
        "Experimental, strictly step-gated variant of update_adr for A/B comparison: "
        "the same read-first/map-to-tool/validate-last flow, rewritten as hard numbered "
        "gates instead of narrated steps."
    ),
)
def update_adr_test(id: str, instructions: str | None = None) -> str:
    """Return step-gated instructional text for revising the ADR identified by ``id``.

    See ``update_adr`` (``adr/prompts/update_adr.py``) for the non-gated
    baseline this variant is meant to be compared against; the parameters
    and returned-value contract are identical.

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
        the MCP SDK), not itself a tool call.
    """
    return _INSTRUCTIONS_TEMPLATE.format(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
