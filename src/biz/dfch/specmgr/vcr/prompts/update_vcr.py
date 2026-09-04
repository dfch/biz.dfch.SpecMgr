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

"""``@mcp.prompt()``: update_vcr (Task 3.2).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Verification Case Record (VCR) document by
id, using the existing ``vcr/tools/`` surface (``get_vcr``,
generic ``validate`` tool) plus the generic ``update``/``set_status`` tools in
``general/tools/`` (called with ``type="vcr"``; ``get_vcr``'s ``raw=True``
parameter serves the line-range flow's line numbers). There is no
``specmgr://vcr/{id}`` resource to point at -- id-based reads always go
through the ``get_vcr`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: VCR's lifecycle surface is deliberately
small -- a whole-body or line-range replace (the generic ``update`` tool
with ``type="vcr"``) plus a single, dedicated status-change path (the
generic ``set_status`` tool with ``type="vcr"``) -- mirroring
``dec.prompts.update_dec``/``req.prompts.update_req``.

Like ``dec.prompts.update_dec``/``req.prompts.update_req`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via ``get_vcr``, showing which sections are present vs. empty, eliciting
revisions via the ``question`` tool, then calling the generic ``update``
tool with ``type="vcr"``, with the generic ``set_status`` tool with
``type="vcr"`` mentioned as a separate, optional follow-up) -- it never
calls ``get_vcr``/``question``/``update``/``set_status`` itself, exactly
like every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``vcr/data/vcr_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the VCR markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_vcr",
    title="Update a verification case record",
    description=(
        "Guides the LLM through revising an existing verification case record by id: reading "
        "current state, applying the requested change with the right tool, and validating."
    ),
)
def update_vcr(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the verification case record identified by ``id``.

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
        ``get_vcr``, ``question``, ``update``, or ``set_status`` itself
        -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("vcr", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
