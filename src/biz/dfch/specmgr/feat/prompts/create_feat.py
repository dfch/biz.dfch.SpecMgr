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

"""``@mcp.prompt()``: create_feat (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Feature (FEAT) document using the existing
``feat/tools/``/``feat/resources/`` surface (``list_feat``,
``specmgr://feat/template``/``specmgr://feat/example``,
``specmgr://feat/schema``, ``create_feat``, ``validate_feat``).

``create_feat`` (the tool) builds the entire FEAT frontmatter itself
(``id``/``type``/``status``/``created``/``updated``/``version``) -- the
caller only ever supplies body markdown. Unlike every other domain in this
codebase, ``id`` is not a server-generated UUID but a fresh
``feat-NNN-slug`` derived from the H1 title (REQ-004); ``created``/
``updated`` use the same shared date+time timestamp format as every other
domain.

Naming note: this prompt is named ``create_feat``, the same name as the
``@mcp.tool()`` in ``feat/tools/create_feat.py``. This is not a collision
-- the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``gol.prompts.create_gol``/``dec.prompts.create_dec``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_feat``, building a ``TodoWrite`` list, eliciting the
mandatory sections and each optional section via the ``question`` tool,
then calling ``create_feat``) -- it never calls
``TodoWrite``/``question``/``list_feat``/``create_feat`` itself, exactly
like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``feat/data/feat_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the FEAT
markdown headings it narrates to the LLM (e.g. ``# Feature: {title}``)
without those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_feat",
    title="Create a feature",
    description=(
        "Guides the LLM through checking for an existing similar feature, gathering the "
        "required information, and driving create_feat/validate_feat to author a new FEAT document."
    ),
)
def create_feat(topic: str) -> str:
    """Return instructional text for drafting a new feature about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the feature to be drafted -- becomes
        the seed for the document's title and overview.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_feat``, or ``create_feat``
        itself -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("feat", "create_instructions", "md"))
    return template.substitute(topic=topic)
