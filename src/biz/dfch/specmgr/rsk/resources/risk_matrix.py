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

"""Resource: specmgr://rsk/risk-matrix (Task 3.15).

Static, domain-knowledge resource: the 5x5 risk matrix for ``rsk`` documents
-- the probability/impact scale anchors (1 = rare ... 5 = almost certain;
1 = negligible ... 5 = severe), the 5x5 zone table, and the product
thresholds (1-4 ``low``, 5-9 ``medium``, 10-14 ``high``, 15-25 ``very
high``) -- i.e. what 'high risk' and 'low risk' mean, plus the
initial/residual reading rule (a ``reduce`` strategy implies residual <
initial).

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://tsk/example``/``/template``) rather than parsed into structured
models -- the audience is an LLM agent that needs to read guidance, not code
that needs data. The documented zone thresholds are the same ones
``rsk.models.v1.assessment.level_from_product`` derives from; a test
(``tests/rsk/resources/test_risk_matrix.py``) guards the two against drift
(feature README's ACC-005).
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://rsk/risk-matrix",
    name="rsk_risk_matrix",
    title="Risk (RSK) 5x5 Risk Matrix",
    description=(
        "The 5x5 risk matrix: probability/impact scale anchors, the zone table, and the product "
        "thresholds (what 'high risk' and 'low risk' mean), as raw markdown domain-knowledge "
        "guidance."
    ),
    mime_type="text/markdown",
)
def risk_matrix() -> str:
    """Return the packaged risk-matrix guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``rsk`` resource/tool -- reads the file fresh on
    every call.

    Returns
    -------
    str
        The risk-matrix guidance document's raw markdown source.
    """
    return read_packaged_text("rsk", "risk_matrix")
