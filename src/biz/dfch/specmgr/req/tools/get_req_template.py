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

"""``@mcp.tool()`` wrapper: get_req_template (Task 3.7).

Returns a REQ document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new REQ document by hand, distinct from ``get_req_example`` (Task 3.6),
which returns a complete, *valid* sample document. Named ``get_req_template``
rather than the bare ``get_template`` (Task 3.7's own wording), mirroring
``get_req_example``'s own domain-qualified naming rationale -- tool names are
global across the whole MCP server.
"""

from __future__ import annotations

from .._data import read_req_template_text
from ...server import mcp


@mcp.tool(
    name="get_req_template",
    title="Get REQ template",
    description=(
        "Return a REQ document template -- frontmatter and every body field present, populated "
        "with short placeholder ('blind text') content -- as raw markdown, for use as a starting "
        "point when drafting a new requirement."
    ),
)
def get_req_template() -> str:
    """Return the packaged REQ template's full markdown text, verbatim.

    The template file is shipped as package data (declared in ``pyproject.toml``'s
    ``[tool.setuptools.package-data]``), so its presence is a build-time
    guarantee, not something that can be missing at runtime in a correctly
    installed package. Reads the file fresh on every call (no in-memory
    cache). A missing or corrupted packaged file is not caught or wrapped
    here -- it propagates as a hard :class:`FileNotFoundError`, the same
    let-it-raise convention every other tool/resource in this codebase
    follows.

    Unlike ``get_req_example``, the returned text is **not** guaranteed to
    satisfy ``parse_req``/``ReqDocument``'s field-level validators (e.g.
    ``## Level``/``## Priority`` hold descriptive placeholder prose, not a
    value matching their strict patterns) -- this is a structural authoring
    aid, not a valid document instance.

    Returns
    -------
    str
        The template document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_req_template_text()
