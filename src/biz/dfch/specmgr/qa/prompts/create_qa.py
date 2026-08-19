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

"""``@mcp.prompt()``: create_qa (Phase 4, Task 4.3).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Question and Answer (QA) document using the
existing ``qa/tools/``/``qa/resources/`` surface (``list_qa``,
``specmgr://qa/template``/``specmgr://qa/example``, ``specmgr://qa/schema``,
``create_qa``, ``validate_qa``). Structural shape ported 1:1 from
``req.prompts.create_req``, with the instructional content rewritten to
describe QA's own schema instead of REQ's.

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_qa`` builds the entire QA frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_qa``, the same name as the
``@mcp.tool()`` in ``qa/tools/create_qa.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

The actual instructional text lives in its own packaged data file,
``qa/data/qa_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the QA
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_qa",
    title="Create a QA document",
    description=(
        "Guides the LLM through checking for an existing similar QA document, gathering answers "
        "to ISO/IEC 25010:2023 characteristic-relevant questions, and driving "
        "create_qa/validate_qa to author a new QA document."
    ),
)
def create_qa(topic: str) -> str:
    """Return instructional text for drafting a new QA document about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the interview's subject -- becomes the
        seed for the document's title and introduction.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    template = Template(read_packaged_text("qa", "create_instructions", "md"))
    return template.substitute(topic=topic)
