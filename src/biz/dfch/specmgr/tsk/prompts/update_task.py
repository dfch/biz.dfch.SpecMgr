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

"""``@mcp.prompt()``: update_task (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Task List (TSK) document by id, using the
existing ``tsk/tools/`` surface (``get_tsk``, ``update_tsk``,
``set_status_tsk``, ``validate_tsk``). There is no
``specmgr://tsk/{id}`` resource to point at -- id-based reads always went
through the ``get_tsk`` tool only (there was no earlier resource to remove,
unlike REQ's own history -- ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: TSK's lifecycle surface is deliberately small
-- a whole-body replace (``update_tsk``) plus a single, dedicated
status-change path (``set_status_tsk``) -- so the tool-mapping section
below is correspondingly short, mirroring ``req.prompts.update_req``.

Naming note: this prompt is named ``update_task`` (the issue's literal
wording), not ``update_tsk`` -- see ``create_task``'s own docstring for the
naming rationale.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are revising an existing Task List (TSK) document, id: {id}

Requested change: {instructions}

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_tsk` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_tsk(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the checklist items, the leading comment, or
  adding a new `## Recent Updates` entry -- -> `update_tsk(id, content)`.
  `content` is body markdown only (no frontmatter block) and is a
  **whole-body replace**: read the current body first (step 1) and carry
  forward every section you are not intentionally changing, or it will
  be dropped. `id`/`type`/`status`/`created`/`version` are preserved
  automatically regardless of what you submit; only `updated` changes.
  In particular, `## Recent Updates` requires at least one entry at all
  times -- if you are not adding a new one, carry forward every existing
  entry; removing the last remaining entry would fail validation
  (`RecentUpdates.updates` requires `min_length>=1`).
- A change to `status` -> `set_status_tsk(id, status)` instead --
  `update_tsk` never accepts or changes `status`. `status` must be one
  of: draft, active, done, cancelled.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://tsk/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_tsk(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_tsk` already performs the same
validation internally, so this step is never required, only a
convenience.

To actually work through the checklist items themselves (marking them
done, asking clarifying questions), use the `implement_task` prompt
instead of this one.
"""


@mcp.prompt(
    name="update_task",
    title="Update a task list",
    description=(
        "Guides the LLM through revising an existing task list by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_task(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the task list identified by ``id``.

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
