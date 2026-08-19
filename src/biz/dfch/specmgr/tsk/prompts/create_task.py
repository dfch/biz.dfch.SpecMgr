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

"""``@mcp.prompt()``: create_task (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Task List (TSK) document using the existing
``tsk/tools/``/``tsk/resources/`` surface (``list_tsk``,
``specmgr://tsk/template``/``specmgr://tsk/example``, ``specmgr://tsk/schema``,
``create_tsk``, ``validate_tsk``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_tsk`` builds the entire TSK frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_task`` (the issue's literal
wording), not ``create_tsk`` -- deliberately distinct from the
``tsk``-prefixed convention the tools/resources use, per the feature
README's Design Notes. This is not a collision with the ``create_tsk``
``@mcp.tool()`` either way -- the MCP protocol keeps prompts and tools in
separate registries (``prompts/list`` vs. ``tools/list``).

The actual instructional text lives in its own packaged data file,
``tsk/data/tsk_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the TSK
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_task",
    title="Create a task list",
    description=(
        "Guides the LLM through checking for an existing similar task list, gathering the "
        "required information, and driving create_tsk/validate_tsk to author a new TSK document."
    ),
)
def create_task(topic: str) -> str:
    """Return instructional text for drafting a new task list about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the task list to be drafted -- becomes
        the seed for the document's title and checklist items.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    template = Template(read_packaged_text("tsk", "create_instructions", "md"))
    return template.substitute(topic=topic)
