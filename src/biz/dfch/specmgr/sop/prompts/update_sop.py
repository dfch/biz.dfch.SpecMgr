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

"""``@mcp.prompt()``: update_sop (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Standard Operating Procedure (SOP) document
by id, using the existing ``sop/tools/`` surface (``get_sop``,
generic ``validate`` tool) plus the generic ``update``/``set_status`` tools in
``general/tools/`` (called with ``type="sop"``; ``get_sop``'s ``raw=True``
parameter serves the line-range flow's line numbers). There is no
``specmgr://sop/{id}`` resource to point at -- id-based reads always go
through the ``get_sop`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

SOP is the first domain built with **no** per-domain mutation tools at
all: there is no ``update_sop``/``set_status_sop`` tool -- every body
change goes through the generic ``update`` tool with ``type="sop"``
(whole-body or line-range), and every status change goes through the
generic ``set_status`` tool with ``type="sop"`` (ADR
36905d5b-8057-4294-8665-c7eed5534db0). The narration names those generic
tools explicitly, never a per-domain ``update_sop(...)``/
``set_status_sop(...)`` call shape. The cross-cutting ``specmgr://rasci``
resource is read first when the change touches ``## Roles and
Responsibilities``.

Like ``dec.prompts.update_dec``/``rsk.prompts.update_risk`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via ``get_sop``, showing which sections are present vs. empty, reading
``specmgr://rasci`` when the roles section is touched, eliciting revisions
via the ``question`` tool, then calling the generic ``update`` tool with
``type="sop"``, with the generic ``set_status`` tool with ``type="sop"``
mentioned as a separate, optional follow-up) -- it never calls
``get_sop``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``sop/data/sop_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the SOP markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_sop",
    title="Update a standard operating procedure",
    description=(
        "Guides the LLM through revising an existing SOP by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_sop(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the SOP identified by ``id``.

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
        ``get_sop``, ``question``, ``update``, or ``set_status`` itself
        -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("sop", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
