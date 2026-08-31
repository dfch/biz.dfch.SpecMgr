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

"""``@mcp.prompt()``: create_vcr (Task 3.2).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Verification Case Record (VCR) document using
the existing ``vcr/tools/``/``vcr/resources/`` surface (``list_vcr``,
``specmgr://vcr/template``/``specmgr://vcr/example``,
``specmgr://vcr/schema``, ``specmgr://dtais``, ``create_vcr``,
``validate_vcr``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_vcr`` builds the entire VCR frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body narrates VCR's own
section names: a single-value `## Verifies` cross-reference, a closed-
vocabulary `## Coverage` assessment, and the dynamic `## Acceptance
Criteria` collection with its closed DTAIS method vocabulary.

Naming note: this prompt is named ``create_vcr``, the same name as the
``@mcp.tool()`` in ``vcr/tools/create_vcr.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``dec.prompts.create_dec``/``gol.prompts.create_gol``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_vcr``, building a ``TodoWrite`` list, eliciting the
mandatory sections and each optional section via the ``question`` tool,
then calling ``create_vcr``) -- it never calls
``TodoWrite``/``question``/``list_vcr``/``create_vcr`` itself, exactly like
every other prompt in this codebase (see ``tsk.prompts.implement_task``'s
own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``vcr/data/vcr_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the VCR
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_vcr",
    title="Create a verification case record",
    description=(
        "Guides the LLM through checking for an existing similar verification case record, "
        "gathering the required information, and driving create_vcr/validate_vcr to author a "
        "new VCR document."
    ),
)
def create_vcr(topic: str) -> str:
    """Return instructional text for drafting a new verification case record about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the verification case record to be
        drafted -- becomes the seed for the document's title and the
        REQ/UC it verifies.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_vcr``, or ``create_vcr``
        itself -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("vcr", "create_instructions", "md"))
    return template.substitute(topic=topic)
