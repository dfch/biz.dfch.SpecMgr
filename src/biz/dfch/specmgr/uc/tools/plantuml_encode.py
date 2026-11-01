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

"""``@mcp.tool()`` wrapper: plantuml_encode (feat-185-uc-diagrams, Phase 120).

Direct, thin wrapper over ``plantuml.encode.encode_puml`` (Phase 110) --
the PlantUML classic text encoding (custom-base64 ``0-9A-Za-z-_`` over the
raw-deflate stream of the text's UTF-8 bytes, no prefix; the ``SoWkI…``
form, rulebook ``specmgr://uc/plantuml`` §5.1). Fully offline: no source,
no subprocess, no network.

The tool returns the **encoding itself** -- the ``{enc}`` payload of
``GET {base}/svg/{enc}`` -- not a full URL: it takes no base URL, and the
renderable URL is the configured server's base (``SPECMGR_PLANTUML_URL``
for the ``url`` source) with the encoding appended.
"""

from __future__ import annotations

from ...plantuml.encode import encode_puml
from ...server import mcp


@mcp.tool(
    name="plantuml_encode",
    title="Encode text to the PlantUML classic URL encoding",
    description=(
        "Encode PlantUML (or any) text to the PlantUML classic URL encoding (custom-base64 "
        "0-9A-Za-z-_ over the raw-deflate stream of the text's UTF-8 bytes, no prefix -- the "
        "SoWkI... form, rulebook §5.1). Returns the encoding itself, i.e. the {enc} payload of "
        "GET {base}/svg/{enc} -- the tool takes no base URL, so prepend the configured server "
        "base (SPECMGR_PLANTUML_URL for the url source) to build the renderable URL. Fully "
        "offline: no source, subprocess, or network is involved. Decode it back with the "
        "library's decode_puml (round-trip lossless)."
    ),
)
def plantuml_encode(text: str) -> str:
    """Encode ``text`` to the PlantUML classic URL encoding.

    Parameters
    ----------
    text:
        The diagram source (or any text) to encode.

    Returns
    -------
    str
        The classic (``SoWkI…``-form) encoding of ``text``'s UTF-8 bytes --
        the ``{enc}`` payload for ``GET {base}/svg/{enc}``. The tool takes
        no base URL, so the result is the encoding itself, not a full URL:
        prepend the configured server base to make it renderable.
    """
    result: str = encode_puml(text)
    return result
