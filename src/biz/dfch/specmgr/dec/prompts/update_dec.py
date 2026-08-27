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

"""``@mcp.prompt()``: update_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Decision (DEC) document by id, using the
existing ``dec/tools/`` surface (``get_dec``, ``update_dec``,
``set_status_dec``, ``validate_dec``). There is no ``specmgr://dec/{id}``
resource to point at -- id-based reads always go through the ``get_dec``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: DEC's lifecycle surface is deliberately
small -- a whole-body replace (``update_dec``) plus a single, dedicated
status-change path (``set_status_dec``) -- mirroring
``req.prompts.update_req``/``rsk.prompts.update_risk``.

Like ``req.prompts.update_req``/``rsk.prompts.update_risk`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

Naming note: this prompt is named ``update_dec``, the same name as the
``@mcp.tool()`` in ``dec/tools/update_dec.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``gol.prompts.update_gol``/``req.prompts.update_req``).

This prompt only ever *narrates* the revision flow (reading current state
via ``get_dec``, showing which sections are present vs. empty, eliciting
revisions via the ``question`` tool, then calling ``update_dec``, with
``set_status_dec`` mentioned as a separate, optional follow-up) -- it never
calls ``get_dec``/``question``/``update_dec``/``set_status_dec`` itself,
exactly like every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``dec/data/dec_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the DEC markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_dec",
    title="Update a decision",
    description=(
        "Guides the LLM through revising an existing decision by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_dec(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the decision identified by ``id``.

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
    template = Template(read_packaged_text("dec", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
