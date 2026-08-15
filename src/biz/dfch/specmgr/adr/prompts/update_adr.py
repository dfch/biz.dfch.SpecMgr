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

"""``@mcp.prompt()``: update_adr (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing MADR 4.0.0-based ADR by id, using the
existing ``adr/tools/`` surface (``get_adr``, ``update_section``,
``update_frontmatter``, ``set_status``, ``option_create``/``option_update``/
``option_delete``, ``validate_adr``).
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are revising an existing Architecture Decision Record (ADR), id: {id}

Requested change: {instructions}

Follow this sequence exactly. Do not write raw markdown yourself -- every
change to the document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_adr(id)` (or read the `specmgr://adr/{{id}}` resource) to load
the document's current frontmatter, body, and options. Never assume prior
state -- the on-disk file is always the source of truth and may have been
hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to prose in `context_and_problem_statement`, `decision_drivers`,
  `considered_options`, `decision_outcome`, `consequences`, `confirmation`,
  or `more_information` -> `update_section(id, key, value)`. Submitting a
  blank string or the literal `"REMOVE"` clears an *optional* section;
  this is rejected with an error for a *mandatory* one
  (`title`/`context_and_problem_statement`/`considered_options`/
  `decision_outcome`).
- A change to `title` -> also `update_section(id, "title", value)`.
- A change to `status` (e.g. accepting/rejecting/deprecating the
  decision, or marking it superseded) -> `set_status(id, status,
  superseded_by=...)`, the narrow convenience wrapper -- prefer this over
  `update_frontmatter` for status-only changes.
- Any other frontmatter change (`date`, `decision_makers`, `consulted`,
  `informed`) -> `update_frontmatter(id, frontmatter)`. This is a
  **whole-object replace**: read the current frontmatter first (step 1)
  and carry forward every field you are not intentionally changing, or
  they will be dropped. `id` itself is always preserved automatically by
  the tool regardless of what you submit.
- Adding a new considered option's pros/cons write-up ->
  `option_create(id, partial_title, value)`.
- Revising an existing option's content -> `option_update(id, full_title,
  value)`.
- Removing an option entirely -> `option_delete(id, full_title)`. This
  never renumbers or reorders the remaining options -- deleting one
  leaves a permanent gap in the numbering.

## 4. Always finish with validation
Call `validate_adr(id)` last, to self-correct before reporting success
back to the user.
"""


@mcp.prompt(
    name="update_adr",
    title="Update an ADR",
    description=(
        "Guides the LLM through revising an existing ADR by id: reading current state, "
        "applying the requested change with the right tool, and validating."
    ),
)
def update_adr(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the ADR identified by ``id``.

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
