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

"""``@mcp.prompt()``: create_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Requirement (REQ) document using the existing
``req/tools/``/``req/resources/`` surface (``list_req``,
``specmgr://req/template``/``specmgr://req/example``, ``specmgr://req/schema``,
``create_req``, generic ``validate`` tool).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_req`` builds the entire REQ frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_req``, the same name as the
``@mcp.tool()`` in ``req/tools/create_req.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

The actual instructional text lives in its own packaged data file,
``req/data/req_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the REQ
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_req",
    title="Create a requirement",
    description=(
        "Guides the LLM through checking for an existing similar requirement, gathering the "
        "required information, and driving create_req/validate to author a new REQ document."
    ),
)
def create_req(topic: str) -> str:
    """Return instructional text for drafting a new requirement about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the requirement to be drafted -- becomes
        the seed for the document's title and requirement statement.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    template = Template(read_packaged_text("req", "create_instructions", "md"))
    return template.substitute(topic=topic)
