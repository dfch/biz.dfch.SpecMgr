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

"""``@mcp.prompt()``: update_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Requirement (REQ) document by id, using the
existing ``req/tools/`` surface (``get_req``, generic ``validate`` tool) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="req"``). Unlike an earlier revision of this prompt, step 1 no
longer points at a ``specmgr://req/{id}`` resource -- that resource was
removed in favor of the ``get_req`` tool (feat-7-various-improvements
Task 0.9, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614); ``get_req``'s
``raw=True`` parameter serves the line-range flow's line numbers.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: REQ's lifecycle surface (Task 3.9's design) is
deliberately small -- a whole-body or line-range replace (the generic
``update`` tool with ``type="req"``) plus a single, dedicated
status-change path (the generic ``set_status`` tool with ``type="req"``)
-- so the tool-mapping section below is correspondingly shorter.

The actual instructional text lives in its own packaged data file,
``req/data/req_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for markdown headings it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_req",
    title="Update a requirement",
    description=(
        "Guides the LLM through revising an existing requirement by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_req(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the requirement identified by ``id``.

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
    template = Template(read_packaged_text("req", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
