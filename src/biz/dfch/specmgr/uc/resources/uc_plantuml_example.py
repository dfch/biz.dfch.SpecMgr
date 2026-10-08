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

"""Resource: specmgr://uc/plantuml-example (feat-185-uc-diagrams, Phase 120).

Static packaged-data resource: the complete, fully attributed PlantUML
sequence diagram for the packaged "Buy Goods" example UC as raw PlantUML
source. The resource-side half of the ``get_uc_plantuml_example``
tool's packaged-data pair (REQ-008) -- both read the same file
(``uc/data/uc_plantuml_example.md``) fresh on every call.

Served as ``text/plain`` -- frozen in the plan's §11 resource mime-type
contract: the file is PlantUML source, **not** markdown and **not** a
specmgr document (no frontmatter, not ``validate``-able) -- closer to the
``specmgr://rsk/tara`` domain-knowledge shape than to a document template
(``specmgr://uc/template``, which is a specmgr document and
``text/markdown``). The example is ``render_uc_sequence_skeleton`` of the
packaged example UC with each ``UNATTRIBUTED`` marker replaced by its
reasoned attribution (the ``generate_uc_sequence_diagram`` prompt flow's
model; the pinning test in ``tests/uc/models/v2/test_renderer.py`` keeps
it from drifting from the renderer).

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://uc/plantuml-example",
    name="uc_plantuml_example",
    title="UC → PlantUML Sequence-Diagram Example",
    description=(
        "The complete, fully attributed PlantUML sequence diagram for the packaged 'Buy Goods' "
        "example UC (every UNATTRIBUTED marker of the deterministic skeleton resolved by reasoned "
        "attribution, rulebook §2.9) as raw PlantUML source: not markdown, not a specmgr document "
        "(no frontmatter, not validate-able) -- text/plain. The model for the "
        "generate_uc_sequence_diagram prompt flow."
    ),
    mime_type="text/plain",
)
def uc_plantuml_example() -> str:
    """Return the packaged sequence-diagram example's full PlantUML text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``uc`` resource/tool -- reads the file fresh on
    every call.

    Returns
    -------
    str
        The example's raw PlantUML source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``uc_plantuml_example.md`` is missing.
    """
    result: str = read_packaged_text("uc", "plantuml_example")
    return result
