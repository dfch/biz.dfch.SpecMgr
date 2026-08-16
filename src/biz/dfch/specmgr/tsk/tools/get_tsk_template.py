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

"""``@mcp.tool()`` wrapper: get_tsk_template (Task 3.9).

Returns a TSK document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new TSK document by hand, distinct from ``get_tsk_example``, which returns a
complete, *valid* sample document. Named ``get_tsk_template`` rather than a
bare ``get_template``, mirroring ``get_req_template``'s own domain-qualified
naming rationale -- tool names are global across the whole MCP server.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.tool(
    name="get_tsk_template",
    title="Get TSK template",
    description=(
        "Return a TSK document template -- frontmatter and every body field present, populated "
        "with short placeholder ('blind text') content -- as raw markdown, for use as a starting "
        "point when drafting a new task list."
    ),
)
def get_tsk_template() -> str:
    """Return the packaged TSK template's full markdown text, verbatim.

    The template file is shipped as package data (declared in ``pyproject.toml``'s
    ``[tool.setuptools.package-data]``), so its presence is a build-time
    guarantee, not something that can be missing at runtime in a correctly
    installed package. Reads the file fresh on every call (no in-memory
    cache). A missing or corrupted packaged file is not caught or wrapped
    here -- it propagates as a hard :class:`FileNotFoundError`, the same
    let-it-raise convention every other tool/resource in this codebase
    follows.

    Unlike ``get_tsk_example``, the returned text is **not** guaranteed to
    satisfy every field-level validator beyond structure -- this is a
    structural authoring aid, not a valid document instance. It does,
    however, include a placeholder ``### Created`` entry under
    ``## Recent Updates`` so it stays a useful starting point given that
    section's ``min_length=1`` requirement.

    Returns
    -------
    str
        The template document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("tsk", "template")
