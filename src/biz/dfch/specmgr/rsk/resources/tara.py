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

"""Resource: specmgr://rsk/tara (Task 3.15).

Static, domain-knowledge resource: what TARA is (Transfer, Accept, Reduce,
Avoid), the four valid ``## Strategy`` words verbatim (exactly the model's
closed set), when and how to apply each, and how the strategy interacts with
``## Mitigation`` and the frontmatter ``status`` vocabulary.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://iso25010``/``specmgr://tsk/example``/``/template``, per ADR
356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw markdown
output, backed by a dedicated model that is parsed on every resource call
purely to fail fast on structural drift, with the parsed result discarded
and the original raw text returned unchanged) -- the audience is an LLM
agent that needs to read guidance, not code that needs data. The content
was drafted in Phase 1 of
``.specmgr/feat/feat-15-add-artifact-type-risk`` and packaged here in
Phase 3; the TARA words have a single source of truth
(``rsk.models.v1.body.Strategy``'s closed set).
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp
from ..models.v1 import parse_tara


@mcp.resource(
    "specmgr://rsk/tara",
    name="rsk_tara",
    title="Risk (RSK) TARA Guidance",
    description=(
        "What TARA is (Transfer, Accept, Reduce, Avoid), the four valid `## Strategy` words, "
        "and when and how to apply each, as raw markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def tara() -> str:
    """Return the packaged TARA guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``rsk`` resource/tool -- reads the file fresh on
    every call. Also parses the text via
    :func:`~biz.dfch.specmgr.rsk.models.v1.parse_tara` on every call purely
    to fail fast on structural drift in production (ADR
    356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
    and the raw text is returned unchanged.

    Returns
    -------
    str
        The TARA guidance document's raw markdown source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``rsk_tara.md`` is missing.
    AssertionError
        If the packaged file's heading/list structure is malformed.
    pydantic.ValidationError
        If the packaged file is structurally sound but a field value fails
        schema validation.
    """
    text = read_packaged_text("rsk", "tara")
    parse_tara(text)
    return text
