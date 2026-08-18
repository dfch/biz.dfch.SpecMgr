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

"""``@mcp.prompt()``: create_adr (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new MADR 4.0.0-based ADR using the existing
``adr/tools/`` surface (``create_adr``, ``option_create``, ``set_status``,
``validate_adr``).

Naming note: this prompt is named ``create_adr``, the same name as the
``@mcp.tool()`` in ``adr/tools/create_adr.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

The actual instructional text lives in its own packaged data file,
``adr/data/adr_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``/``$decision_makers``/...), not ``str.format``, precisely so
the instructions file itself is free to use plain, unescaped ``{...}``
braces for the MADR markdown headings it narrates to the LLM (e.g.
``# {title}``) without those colliding with this module's own
substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_adr",
    title="Create an ADR",
    description=(
        "Guides the LLM through checking for an existing similar ADR, gathering the "
        "required information, and driving create_adr/option_create/set_status/"
        "validate_adr to author a new MADR-4.0.0-based Architecture Decision Record."
    ),
)
def create_adr(
    topic: str,
    decision_makers: str | None = None,
    consulted: str | None = None,
    informed: str | None = None,
) -> str:
    """Return instructional text for drafting a new ADR about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the decision to be made -- becomes the
        seed for ``title``/``context_and_problem_statement``.
    decision_makers:
        Pre-known ``decision-makers`` frontmatter value, if any; otherwise
        the returned instructions tell the LLM to ask the user.
    consulted:
        Pre-known ``consulted`` frontmatter value, if any.
    informed:
        Pre-known ``informed`` frontmatter value, if any.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    template = Template(read_packaged_text("adr", "create_instructions", "md"))
    return template.substitute(
        topic=topic,
        decision_makers=decision_makers or "(not given -- ask the user, or omit)",
        consulted=consulted or "(not given -- ask the user, or omit)",
        informed=informed or "(not given -- ask the user, or omit)",
    )
