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

"""Resource: specmgr://ears -- the EARS requirement-phrasing templates (feat-92-resources REQ-006).

Static, domain-knowledge resource: what EARS (Easy Approach to
Requirements Syntax) is, the five canonical sentence templates
(Ubiquitous, Event-driven, State-driven, Unwanted behavior, Optional
feature), when to use each, and how "complex" EARS sentences combine
more than one trigger/condition keyword.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://iso25010``/``specmgr://dtais``/``specmgr://rsk/tara``/
``specmgr://rsk/risk-matrix``/``specmgr://rasci``, per ADR
356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw markdown
output, backed by a dedicated model that is parsed on every resource call
purely to fail fast on structural drift, with the parsed result discarded
and the original raw text returned unchanged) -- the audience is an LLM
agent that needs to read guidance, not code that needs data. Registered
as a flat, top-level ``specmgr://ears`` URI (like ``specmgr://dtais``/
``specmgr://iso25010``, not e.g. ``specmgr://req/ears``) since EARS is
domain-knowledge that any requirement-phrasing document type (`req`,
`gol`, `sysrs`, ...) may want to reference, not owned by any single
domain's own schema -- mirroring `general/resources/dtais.py`'s cross-
domain placement rationale.
"""

from __future__ import annotations

from ...server import mcp
from ..models import parse_ears
from ..tools._packaged_data import read_packaged_text


@mcp.resource(
    "specmgr://ears",
    name="ears",
    title="EARS Requirement-Phrasing Templates",
    description=(
        "The EARS (Easy Approach to Requirements Syntax) five requirement-phrasing templates "
        "(Ubiquitous, Event-driven, State-driven, Unwanted behavior, Optional feature) and when "
        "to use each, as raw markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def ears() -> str:
    """Return the packaged EARS guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other cross-cutting ``general`` resource -- reads the
    file fresh on every call. Also parses the text via
    :func:`~biz.dfch.specmgr.general.models.parse_ears` on every call
    purely to fail fast on structural drift in production (ADR
    356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
    and the raw text is returned unchanged.

    Returns
    -------
    str
        The EARS guidance document's raw markdown source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``general_ears.md`` is missing.
    AssertionError
        If the packaged file's heading/list structure is malformed.
    pydantic.ValidationError
        If the packaged file is structurally sound but a field value fails
        schema validation.
    """
    text = read_packaged_text("general", "ears")
    parse_ears(text)
    return text
