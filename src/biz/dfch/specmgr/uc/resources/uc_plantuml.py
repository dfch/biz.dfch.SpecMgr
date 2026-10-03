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

"""Resource: specmgr://uc/plantuml (feat-185-uc-diagrams, Phase 100).

Static, domain-knowledge resource: the frozen UC → PlantUML mapping rulebook. It
specifies, verbatim, the deterministic mapping from a parsed v2 ``UseCase`` to the
per-UC usecase diagram, the package usecase diagram, and the sequence skeleton
(including the full UNATTRIBUTED marker grammar), plus the validation chain's
strict source-selection semantics, the local jar/bin invocation contract, the URL
protocol's frozen classification matrix, the two-mode structure checker contract,
and the user-owned platform-adapter reference snippets.

Served as raw packaged markdown (``text/markdown`` — frozen in the plan's §11
resource mime-type contract; the rulebook *is* markdown, unlike the later
``text/plain`` PlantUML-source template/example resources), mirroring the
domain-knowledge shape of ``specmgr://rsk/tara`` / ``specmgr://dtais``: the
audience is an LLM agent (and the Phase 110+ implementer) that needs to read a
frozen spec, not code that needs data. Unlike ``rsk_tara`` there is no
dedicated model to parse the rulebook with, so there is no per-call drift-guard
parse — the sanity pins in ``tests/uc/resources/test_uc_plantuml.py`` play that
role instead. The content is the Phase 100 freeze of the feature plan's §2–§6
and §8; a change to the rulebook is a spec change, not a content edit.

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://uc/plantuml",
    name="uc_plantuml",
    title="UC → PlantUML Diagram Rulebook",
    description=(
        "The frozen UC → PlantUML mapping and validation rulebook (per-UC usecase and "
        "package diagram mapping, sequence-skeleton attribution and UNATTRIBUTED marker "
        "grammar, the strict 3-source validation chain, the jar/bin and URL invocation "
        "contracts, the two-mode structure checker, and user-owned platform-adapter "
        "snippets) as raw markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def uc_plantuml() -> str:
    """Return the packaged UC → PlantUML rulebook's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``uc`` resource/tool — reads the file fresh on
    every call.

    Returns
    -------
    str
        The rulebook's raw markdown source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``uc_plantuml.md`` is missing.
    """
    result: str = read_packaged_text("uc", "plantuml")
    return result
