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

"""``@mcp.prompt()``: create_txt (feat-229-txt Phase 120).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new free-form text (TXT) document using the
existing ``txt/tools/``/``txt/resources/`` surface (``list_txt``,
``specmgr://txt/template``/``specmgr://txt/example``,
``get_txt_schema``, ``create_txt``, generic ``validate`` tool).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_txt`` builds the entire TXT frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body narrates TXT's own
shape: a single ``# {title}`` H1, the mandatory free-form opaque body
(any markdown, including H2 to H6 headings, ending at the first
top-level ``## Updates`` H2), and the mandatory newest-first
``## Updates`` log -- there are no optional sections.

Naming note: this prompt is named ``create_txt``, the same name as the
``@mcp.tool()`` in ``txt/tools/create_txt.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``dec.prompts.create_dec``/``gol.prompts.create_gol``/
``vcr.prompts.create_vcr``).

This prompt only ever *narrates* the interview flow (checking for a
near-duplicate via ``list_txt``, building a ``TodoWrite`` list, eliciting
the title, body content, and ``## Updates`` entry via the ``question``
tool, then calling ``create_txt``) -- it never calls
``TodoWrite``/``question``/``list_txt``/``create_txt`` itself, exactly
like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``txt/data/txt_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the TXT
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_txt",
    title="Create a free-form text document",
    description=(
        "Guides the LLM through checking for an existing similar free-form text document, "
        "gathering the required information, and driving create_txt/validate to author a "
        "new TXT document. The structure reference is the `get_txt_schema` tool (the generated "
        "JSON Schema); the `get_txt_template`/`get_txt_example` tools return the authoring template "
        "and a complete sample."
    ),
)
def create_txt(topic: str) -> str:
    """Return instructional text for drafting a new free-form text document about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the free-form text document to be
        drafted -- becomes the seed for the document's title and body.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_txt``, or ``create_txt``
        (the tool) itself -- it only narrates that sequence for the LLM
        to carry out.
    """
    template = Template(read_packaged_text("txt", "create_instructions", "md"))
    return template.substitute(topic=topic)
