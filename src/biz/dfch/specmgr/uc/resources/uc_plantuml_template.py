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

"""Resource: specmgr://uc/plantuml-template (feat-185-uc-diagrams, Phase 120).

Static packaged-data resource: the PlantUML sequence-skeleton template
(placeholder participants + mapping comments, rulebook §2.9) as raw
PlantUML source. The resource-side half of the ``get_uc_plantuml_template``
tool's packaged-data pair (REQ-008) -- both read the same file
(``uc/data/uc_plantuml_template.md``) fresh on every call.

Served as ``text/plain`` -- frozen in the plan's §11 resource mime-type
contract: the file is PlantUML source, **not** markdown and **not** a
specmgr document (no frontmatter, not ``validate``-able) -- closer to the
``specmgr://rsk/tara`` domain-knowledge shape than to a document template
(``specmgr://uc/template``, which is a specmgr document and
``text/markdown``). The trivial usecase-diagram shape is frozen in the
rulebook §2.6 instead (no template needed for it).

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://uc/plantuml-template",
    name="uc_plantuml_template",
    title="UC → PlantUML Sequence-Skeleton Template",
    description=(
        "The packaged PlantUML sequence-skeleton template (placeholder participants and mapping "
        "comments -- the shape get_uc_sequence_skeleton emits, rulebook §2.9) as raw PlantUML "
        "source: not markdown, not a specmgr document (no frontmatter, not validate-able) -- "
        "text/plain."
    ),
    mime_type="text/plain",
)
def uc_plantuml_template() -> str:
    """Return the packaged sequence-skeleton template's full PlantUML text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``uc`` resource/tool -- reads the file fresh on
    every call.

    Returns
    -------
    str
        The template's raw PlantUML source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``uc_plantuml_template.md`` is missing.
    """
    result: str = read_packaged_text("uc", "plantuml_template")
    return result
