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

"""Resource: specmgr://iso25010 (Task 0.8.3; feat-92-resources Phase 1).

Reads the packaged ISO/IEC 25010:2023 product quality model markdown
(``general/data/general_iso25010.md``, via
``general.tools._packaged_data.read_packaged_text``) and returns it
verbatim as raw markdown, mirroring ``specmgr://dtais``/``specmgr://rsk/tara``'s
raw-passthrough style. Unlike its plain-passthrough siblings, it still
parses the text into a :class:`~biz.dfch.specmgr.models.Iso25010` on every
call purely to fail fast on structural drift (ADR
356d8781-e446-4c26-917a-eda85648ce9d): the parsed result is discarded and
the original raw text is what's returned.
"""

from __future__ import annotations

from ...models import parse_iso25010
from ...server import mcp
from ..tools._packaged_data import read_packaged_text


@mcp.resource(
    "specmgr://iso25010",
    name="iso25010",
    title="ISO/IEC 25010:2023 Product Quality Model",
    description=(
        "The nine main characteristics (and their sub-characteristics) of the ISO/IEC "
        "25010:2023 system/software product quality model, each with a description."
    ),
    mime_type="text/markdown",
)
def iso25010() -> str:
    """Return the packaged ISO/IEC 25010:2023 guidance's full markdown text, verbatim.

    Reads the packaged copy (``general/data/general_iso25010.md``) fresh on
    every call (no in-memory cache, consistent with every other resource/tool
    in this codebase) but never regenerates it -- this is static reference
    data, not a user-edited/versioned document type. Also parses the text
    via :func:`~biz.dfch.specmgr.models.parse_iso25010` on every call purely
    to fail fast on structural drift in production; the parsed result is
    discarded and the raw text is returned unchanged.

    Returns
    -------
    str
        The ISO/IEC 25010:2023 product quality model document's raw
        markdown source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``general_iso25010.md`` is missing.
    AssertionError
        If the packaged file's heading/list structure is malformed.
    pydantic.ValidationError
        If the packaged file is structurally sound but a field value fails
        schema validation.
    """
    text = read_packaged_text("general", "iso25010", "md")
    parse_iso25010(text)
    return text
