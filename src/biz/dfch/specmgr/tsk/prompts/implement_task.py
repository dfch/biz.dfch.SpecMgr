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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

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

The actual instructional text lives in its own packaged data file,
``tsk/data/tsk_implement_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``), not ``str.format``, precisely so the instructions file itself
is free to use plain, unescaped ``{...}`` braces for the TSK markdown it
narrates to the LLM without those colliding with this module's own
substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


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
    template = Template(read_packaged_text("tsk", "implement_instructions", "md"))
    return template.substitute(id=id)
