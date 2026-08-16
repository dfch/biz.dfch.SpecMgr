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

"""Resource: specmgr://iso25010 (Task 0.8.3).

Reads the packaged ISO/IEC 25010:2023 product quality model markdown
(``general/data/general_iso25010.md``, via
``general.tools._packaged_data.read_packaged_text``) and parses it into a
structured :class:`~biz.dfch.specmgr.models.Iso25010`, mirroring
``req/resources/req_schema.py``'s packaged-data-read style.
"""

from __future__ import annotations

from ...models import Iso25010, parse_iso25010
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
    mime_type="application/json",
)
def iso25010() -> Iso25010:
    """Return the parsed ISO/IEC 25010:2023 product quality model.

    Reads the packaged copy (``general/data/general_iso25010.md``) fresh on
    every call (no in-memory cache, consistent with every other resource/tool
    in this codebase) but never regenerates it -- this is static reference
    data, not a user-edited/versioned document type.

    Returns
    -------
    Iso25010
        The nine main characteristics (each with its sub-characteristics),
        the ordered list of characteristic names, and the copyright notice.

    Raises
    ------
    FileNotFoundError
        If the packaged ``general_iso25010.md`` is missing.
    AssertionError
        If the packaged file's heading/list structure is malformed.
    """
    result: Iso25010 = parse_iso25010(read_packaged_text("general", "iso25010", "md"))
    return result
