# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

# pylint: disable=redefined-builtin  # id intentionally shadows the builtin: public prompt API, issue #41

"""``@mcp.prompt()``: generate_uc_sequence_diagram (feat-185-uc-diagrams, Phase 120).

Returns instructional text -- not itself a tool call -- that guides an LLM
through the rulebook §3.8 agent flow for one use case's sequence diagram:
read the frozen rulebook ``specmgr://uc/plantuml`` first, build a
``TodoWrite`` plan, read the UC via ``get_uc`` (a ``ParseFailureResult``
stops the flow -- the document must be repaired first), apply the §2.11
Subfunction judgment (a ``Subfunction``-level UC gets its own diagram only
when it adds interactions beyond its user goal's), fetch the deterministic
skeleton via ``get_uc_sequence_skeleton``, attribute every ``UNATTRIBUTED``
marker by understanding the free text (pre-filled arrows are positional,
not semantic -- they may be corrected; the ``question`` tool MUST be used
whenever not confident), enforce the zero-marker rule, loop
``validate_plantuml`` until green at the highest available layer
(``source_state != ok`` with a source set => report ``reason``/``fix_hint``
and do not write; all unset => write with the
``' validated: structure-only`` header), write the ``.puml`` file
host-native at ``diagrams/uc/<id>.sequence.puml`` (no specmgr tool writes
``.puml``), and never commit.

The actual instructional text lives in its own packaged data file,
``uc/data/uc_generate_uc_sequence_diagram_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text`` -- the
same convention as ``create_uc``'s ``uc_create_instructions.md`` and
``general``'s ``repair``. Placeholders use ``string.Template`` (``$id``),
not ``str.format``, so the instructions file is free to use plain,
unescaped ``{...}`` braces of its own.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="generate_uc_sequence_diagram",
    title="Generate the sequence diagram for a use case",
    description=(
        "Guides the LLM through the rulebook §3.8 agent flow for one use case: read the frozen "
        "rulebook (specmgr://uc/plantuml) first, build a TodoWrite plan, read the UC via get_uc "
        "(a ParseFailureResult stops the flow), apply the §2.11 Subfunction judgment, fetch the "
        "deterministic skeleton via get_uc_sequence_skeleton, attribute every UNATTRIBUTED marker "
        "by understanding the free text (pre-filled arrows are positional, not semantic, and may "
        "be corrected; the question tool MUST be used whenever not confident), enforce the "
        "zero-marker rule, loop validate_plantuml until green at the highest available layer "
        "(source_state != ok with a source set => report reason/fix_hint and do not write; all "
        "unset => write with the ' validated: structure-only header), write the .puml file "
        "host-native at diagrams/uc/<id>.sequence.puml (no specmgr tool writes .puml), and never "
        "commit."
    ),
)
def generate_uc_sequence_diagram(id: str) -> str:
    """Return the §3.8 agent-flow instructions for the use case ``id``.

    Parameters
    ----------
    id:
        The use case document's specmgr-assigned identifier (the diagram's
        ``diagrams/uc/<id>.sequence.puml`` file name derives from it).

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.

    Raises
    ------
    ValueError
        ``id`` is blank/whitespace-only (pass a real id; the flow's own
        ``get_uc`` call enforces the well-formed shape).
    """
    if not id.strip():
        raise ValueError(
            "generate_uc_sequence_diagram() received a blank id; pass the use case's real id "
            "(the flow's own get_uc call enforces the well-formed shape)."
        )
    template = Template(read_packaged_text("uc", "generate_uc_sequence_diagram_instructions", "md"))
    result = template.substitute(id=id)
    return result
