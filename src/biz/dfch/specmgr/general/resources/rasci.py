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

"""Resource: specmgr://rasci (feat-30 Task 3.5, REQ-011).

Cross-cutting resource defining the generic RASCI (Responsible/
Accountable/Support/Consulted/Informed) responsibility-assignment
framework -- what RASCI is, the five roles' standard definitions, and how
RASCI differs from plain RACI. Motivated by the ``sop`` domain but
deliberately not scoped to it: RASCI, like ISO/IEC 25010, is a well-known
external framework rather than domain-coupled guidance, so this resource
follows ``specmgr://iso25010``'s cross-cutting placement under
``general/resources/`` rather than ``rsk/tara``'s domain-scoped one (whose
content is inseparable from RSK's own ``## Strategy`` vocabulary). The
content is limited to the five roles' generic definitions -- no
``sop``-specific heading names or cardinality rules leak in here; those
stay exclusively in ``sop``'s own schema field docstrings (surfaced via
``specmgr://sop/schema``) and packaged instructions.

Served as raw packaged markdown (``text/markdown``, mirroring
``rsk/resources/tara``'s raw passthrough rather than ``iso25010``'s
structured parse) -- the audience is an LLM agent that needs to read
guidance, not code that needs data. The ``sop`` domain reaches this
resource via four explicit cross-references (the six RASCI-family class
docstrings in ``sop/models/v1/body.py``, the ``create_sop``/``update_sop``
packaged instructions, ``sop/__init__.py``'s module docstring, and
``server.py``'s module docstring) rather than by copying the role
definitions into the ``sop`` schema.
"""

from __future__ import annotations

from ..tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://rasci",
    name="rasci",
    title="RASCI Responsibility Assignment Guidance",
    description=(
        "What RASCI is (Responsible, Accountable, Support, Consulted, Informed), the five roles' "
        "standard definitions, and how RASCI differs from plain RACI, as raw markdown guidance."
    ),
    mime_type="text/markdown",
)
def rasci() -> str:
    """Return the packaged RASCI guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``general`` resource -- reads the file fresh on
    every call. Unlike ``iso25010`` (parsed into a structured model), this
    is a raw passthrough: the content is prose guidance, not
    machine-readable reference data.

    Returns
    -------
    str
        The RASCI guidance document's raw markdown source.
    """
    return read_packaged_text("general", "rasci")
