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

"""``@mcp.tool()`` wrapper: get_uc_plantuml_template (feat-185-uc-diagrams, Phase 120).

Returns the packaged PlantUML sequence-skeleton template (rulebook
``specmgr://uc/plantuml`` §2.9: placeholder participants + mapping
comments) as raw PlantUML source, verbatim -- the tool-side half of the
``specmgr://uc/plantuml-template`` packaged-data pair (REQ-008). The file
is PlantUML source, not markdown and not a specmgr document (no
frontmatter, not ``validate``-able); the trivial usecase-diagram shape is
frozen in the rulebook §2.6 instead (no template needed for it).
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.tool(
    name="get_uc_plantuml_template",
    title="Get the PlantUML sequence-skeleton template",
    description=(
        "Return the packaged PlantUML sequence-skeleton template (placeholder participants and "
        "mapping comments -- the shape get_uc_sequence_skeleton emits, rulebook §2.9) as raw "
        "PlantUML source, verbatim. The file is not markdown and not a specmgr document (no "
        "frontmatter, not validate-able). Reads the packaged data file fresh on every call."
    ),
)
def get_uc_plantuml_template() -> str:
    """Return the packaged sequence-skeleton template's full PlantUML text, verbatim.

    The template file is shipped as package data (declared in
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
        The template's raw PlantUML source.
    """
    result: str = read_packaged_text("uc", "plantuml_template")
    return result
