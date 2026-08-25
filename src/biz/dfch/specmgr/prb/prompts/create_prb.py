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

"""``@mcp.prompt()``: create_prb (Task 3.14).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Problem Statement (PRB) document using the
existing ``prb/tools/``/``prb/resources/`` surface (``list_prb``,
``specmgr://prb/template``/``specmgr://prb/example``, ``specmgr://prb/schema``,
``create_prb``, ``validate_prb``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_prb`` builds the entire PRB frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_prb``, the same name as the
``@mcp.tool()`` in ``prb/tools/create_prb.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``req.prompts.create_req``).

This prompt only ever *narrates* a 10-step interview flow (checking for a
duplicate via `list_prb`, building a ``TodoWrite`` list, eliciting the 7
5W2H answers via the ``question`` tool, synthesizing `Summary`, drafting and
confirming `Gap`, optionally asking for `Impact`/`Future State`/
`References`/`More Information`, then calling `create_prb`) -- it never
calls ``TodoWrite``/``question``/``list_prb``/``create_prb`` itself, exactly
like every other prompt in this codebase (see ``tsk.prompts.implement_task``'s
own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``prb/data/prb_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the PRB
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_prb",
    title="Create a problem statement",
    description=(
        "Guides the LLM through checking for an existing similar problem statement, "
        "interviewing the user for the 5W2H current-state questions, synthesizing the Summary "
        "and Gap, and driving create_prb/validate_prb to author a new PRB document."
    ),
)
def create_prb(topic: str) -> str:
    """Return instructional text for drafting a new problem statement about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the problem statement to be drafted --
        becomes the seed for the document's title and interview.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_prb``, or ``create_prb``
        itself -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("prb", "create_instructions", "md"))
    return template.substitute(topic=topic)
