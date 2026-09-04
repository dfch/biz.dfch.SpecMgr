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

"""Resource: specmgr://dtais -- the DTAIS verification-method vocabulary (feat-33-vcr Task 3.3).

Static, domain-knowledge resource: what DTAIS is (Demonstration, Test,
Analysis, Inspection, Special), the five valid ``### AC-NNN (Method):
...`` method words verbatim (exactly `vcr.models.v1.body`'s closed set),
when and how to apply each, and how the chosen method interacts with a
verification case record's document-level ``## Coverage`` signal.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://iso25010``/``specmgr://rsk/tara``/``specmgr://rsk/risk-matrix``,
per ADR 356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw
markdown output, backed by a dedicated model that is parsed on every
resource call purely to fail fast on structural drift, with the parsed
result discarded and the original raw text returned unchanged) -- the
audience is an LLM agent that needs to read guidance, not code that needs
data. Registered as a flat,
top-level ``specmgr://dtais`` URI (like
``specmgr://iso25010``, not ``specmgr://vcr/dtais``) since the DTAIS
vocabulary is domain-knowledge that other domains (e.g. a future `sysrs`)
may want to reference too, not owned by `vcr`'s own schema -- see
`.specmgr/feat/feat-33-vcr/README.md` REQ-006/Design Notes for the full
rationale.
"""

from __future__ import annotations

from ...server import mcp
from ..models import parse_dtais
from ..tools._packaged_data import read_packaged_text


@mcp.resource(
    "specmgr://dtais",
    name="dtais",
    title="DTAIS Verification Method Vocabulary",
    description=(
        "What DTAIS is (Demonstration, Test, Analysis, Inspection, Special), the five valid "
        "`### AC-NNN (Method): ...` method words, and when and how to apply each, as raw "
        "markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def dtais() -> str:
    """Return the packaged DTAIS guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other cross-cutting ``general`` resource -- reads the
    file fresh on every call. Also parses the text via
    :func:`~biz.dfch.specmgr.general.models.parse_dtais` on every call
    purely to fail fast on structural drift in production (ADR
    356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
    and the raw text is returned unchanged.

    Returns
    -------
    str
        The DTAIS guidance document's raw markdown source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``general_dtais.md`` is missing.
    AssertionError
        If the packaged file's heading/list structure is malformed.
    pydantic.ValidationError
        If the packaged file is structurally sound but a field value fails
        schema validation.
    """
    text = read_packaged_text("general", "dtais")
    parse_dtais(text)
    return text
