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

"""``@mcp.prompt()``: update_prb (Task 3.15).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Problem Statement (PRB) document by id, using
the existing ``prb/tools/`` surface (``get_prb``, ``validate_prb``) plus
the generic ``update``/``set_status`` tools in ``general/tools/`` (called
with ``type="prb"``; ``get_prb``'s ``raw=True`` parameter serves the
line-range flow's line numbers). There is no ``specmgr://prb/{id}``
resource to point at -- id-based reads always go through the ``get_prb``
tool only.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: PRB's lifecycle surface is deliberately small
-- a whole-body or line-range replace (the generic ``update`` tool with
``type="prb"``) plus a single, dedicated status-change path (the generic
``set_status`` tool with ``type="prb"``) -- mirroring
``tsk.prompts.update_task``/``qa.prompts.update_qa``.

This prompt only ever *narrates* an 9-step revision flow (reading current
state via `get_prb`, showing which of the 7 questions are already answered,
eliciting revisions via the `question` tool, re-synthesizing `Summary` and
`Gap`, optionally revising `Impact`/`Future State`/`References`/
`More Information`, then calling the generic `update` tool with
`type="prb"`, with the generic `set_status` tool with `type="prb"`
mentioned as a separate, optional follow-up) -- it never calls
``get_prb``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``prb/data/prb_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the PRB markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_prb",
    title="Update a problem statement",
    description=(
        "Guides the LLM through revising an existing problem statement by id: reading "
        "current state, showing which of the 7 5W2H questions are answered, eliciting "
        "revisions, re-synthesizing Summary/Gap, applying the change with the right tool, "
        "and validating."
    ),
)
def update_prb(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the problem statement identified by ``id``.

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
        the MCP SDK), not itself a tool call. This function never calls
        ``get_prb``, ``question``, ``update``, or ``set_status`` itself
        -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("prb", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
