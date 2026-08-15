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

"""``@mcp.tool()`` wrapper: get_req_example (Task 3.6).

Returns a complete, valid sample requirement document as raw markdown --
useful as a learning example for drafting a new REQ document by hand, or for
an LLM to see the expected shape without re-deriving it from the JSON Schema
alone. Named ``get_req_example`` rather than the bare ``get_example`` (Task
3.6's own wording) since tool names are global across the whole MCP server --
domain-qualifying it now avoids a future collision if ADR/UC ever grow their
own equivalent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.tool(
    name="get_req_example",
    title="Get REQ example",
    description=(
        "Return a complete, valid sample requirement document as raw markdown -- frontmatter "
        "and body -- exercising every section, for use as a learning example."
    ),
)
def get_req_example() -> str:
    """Return the packaged REQ example's full markdown text, verbatim.

    The example file is shipped as package data (declared in ``pyproject.toml``'s
    ``[tool.setuptools.package-data]``), so its presence is a build-time
    guarantee, not something that can be missing at runtime in a correctly
    installed package. Reads the file fresh on every call (no in-memory
    cache). A missing or corrupted packaged file is not caught or wrapped
    here -- it propagates as a hard :class:`FileNotFoundError`, the same
    let-it-raise convention every other tool/resource in this codebase
    follows.

    Returns
    -------
    str
        The example document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("req", "example")
