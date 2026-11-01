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

"""``@mcp.tool()`` wrapper: get_uc_plantuml_example (feat-185-uc-diagrams, Phase 120).

Returns the packaged, complete, fully attributed PlantUML sequence diagram
for the "Buy Goods" example UC as raw PlantUML source, verbatim -- the
tool-side half of the ``specmgr://uc/plantuml-example`` packaged-data pair
(REQ-008). It is ``render_uc_sequence_skeleton`` of the packaged example
UC with each ``UNATTRIBUTED`` marker replaced by its reasoned
attribution (the ``generate_uc_sequence_diagram`` prompt flow's model).
The file is PlantUML source, not markdown and not a specmgr document (no
frontmatter, not ``validate``-able).
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.tool(
    name="get_uc_plantuml_example",
    title="Get the PlantUML sequence-diagram example",
    description=(
        "Return the complete, fully attributed PlantUML sequence diagram for the packaged "
        "'Buy Goods' example UC as raw PlantUML source, verbatim -- the model for the "
        "generate_uc_sequence_diagram prompt flow (rulebook §2.9 attribution, every "
        "UNATTRIBUTED marker resolved). The file is not markdown and not a specmgr document "
        "(no frontmatter, not validate-able). Reads the packaged data file fresh on every call."
    ),
)
def get_uc_plantuml_example() -> str:
    """Return the packaged sequence-diagram example's full PlantUML text, verbatim.

    The example file is shipped as package data (declared in
    ``pyproject.toml``'s ``[tool.setuptools.package-data]``), so its
    presence is a build-time guarantee, not something that can be missing
    at runtime in a correctly installed package. Reads the file fresh on
    every call (no in-memory cache). A missing or corrupted packaged file
    is not caught or wrapped here -- it propagates as a hard
    :class:`FileNotFoundError`, the same let-it-raise convention every
    other tool/resource in this codebase follows.

    Returns
    -------
    str
        The example's raw PlantUML source.
    """
    result: str = read_packaged_text("uc", "plantuml_example")
    return result
