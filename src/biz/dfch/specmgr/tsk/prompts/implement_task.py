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

"""``@mcp.prompt()``: implement_task (Task 3.14).

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
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are implementing the checklist of an existing Task List (TSK)
document, id: {id}

Follow this sequence exactly.

## 1. Read the current document
Call `get_tsk(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. Build a TodoWrite list from its items
Create one TodoWrite entry per checklist item in `body.items`, in the
same order:
- An item whose `checked` is already `true` -> mark its TodoWrite entry
  `completed`.
- An item whose `checked` is `false` -> mark its TodoWrite entry
  `pending` (moving it to `in_progress` only once you actually start
  working on it -- keep at most one `in_progress` at a time, per
  TodoWrite's own usage conventions).
Use each item's `description` as the TodoWrite entry's own content.

## 3. Resolve ambiguity before starting an item
Before marking any pending item `in_progress`, check whether its
`description` is clear enough to act on. If its intent or scope is
ambiguous or underspecified, use the `question` tool to ask the user
for clarification first -- do not guess and start working on an
unclear item.

## 4. Work the list
Proceed item by item, updating your TodoWrite list's statuses as you
go (one `in_progress` at a time, then `completed` once genuinely done).

## 5. Persisting completed work back to the document (separate, deliberate step)
Completing TodoWrite entries in-session does **not** update the
underlying `tsk` document -- its checkboxes on disk are left exactly as
they were read in step 1. If you want the persisted document to reflect
the work you completed, you must separately call
`update_tsk(id, content)` with the updated checklist (`- [x] ...` for
items you completed) -- a whole-body replace, so carry forward every
other section unchanged, including at least one `## Recent Updates`
entry (add a new one summarizing the work, or keep the existing ones --
never end up with zero). This is a distinct, deliberate step: do not
assume finishing the TodoWrite list alone is enough.

Optionally, check `specmgr://tsk/schema` if you need to double-check
the document's structure before drafting the replacement body.
"""


@mcp.prompt(
    name="implement_task",
    title="Implement a task list",
    description=(
        "Reads an existing task list by id, builds a TodoWrite list from its items, and "
        "uses the question tool to resolve ambiguity before proceeding."
    ),
)
def implement_task(id: str) -> str:
    """Return instructional text for working the checklist of the task list identified by ``id``.

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
    """
    return _INSTRUCTIONS_TEMPLATE.format(id=id)
