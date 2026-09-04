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

"""``@mcp.prompt()``: create_sop (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Standard Operating Procedure (SOP) document
using the existing ``sop/tools/``/``sop/resources/`` surface (``list_sop``,
``specmgr://sop/template``/``specmgr://sop/example``,
``specmgr://sop/schema``, ``create_sop``, generic ``validate`` tool) plus the
cross-cutting ``specmgr://rasci`` resource (read before drafting
``## Roles and Responsibilities``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_sop`` builds the entire SOP frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown (and ``status`` is always fixed
to ``"draft"``). The body keeps the structured SOP shape (mandatory
``## Purpose`` and ``## Procedure`` with ``### Step N`` entries, optional
scope/definitions/roles-and-responsibilities/safety/related-artifacts/more-
information/updates) narrated through SOP's own section names.

Naming note: this prompt is named ``create_sop``, the same name as the
``@mcp.tool()`` in ``sop/tools/create_sop.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``dec.prompts.create_dec``/``gol.prompts.create_gol``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_sop``, building a ``TodoWrite`` list, reading
``specmgr://rasci`` before the RASCI ``## Roles and Responsibilities``
section, eliciting the mandatory purpose and procedure plus each optional
section via the ``question`` tool, then calling ``create_sop``) -- it
never calls ``TodoWrite``/``question``/``list_sop``/``create_sop`` itself,
exactly like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``sop/data/sop_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the SOP
markdown headings it narrates to the LLM (e.g. ``# {title}`` or
``### Step {N}: {name}``) without those colliding with this module's own
substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_sop",
    title="Create a standard operating procedure",
    description=(
        "Guides the LLM through checking for an existing similar SOP, gathering the "
        "required information, and driving create_sop/validate to author a new SOP document."
    ),
)
def create_sop(topic: str) -> str:
    """Return instructional text for drafting a new SOP about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the standard operating procedure to be
        drafted -- becomes the seed for the document's title and purpose.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_sop``, or ``create_sop``
        itself -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("sop", "create_instructions", "md"))
    return template.substitute(topic=topic)
