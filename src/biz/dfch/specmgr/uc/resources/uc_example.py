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

"""Resource: specmgr://uc/example (Task 3.1.4).

Read-only, addressable counterpart of the ``get_uc_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``req.tools.get_req_example``
/ ``specmgr://req/example``) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``uc.tools`` (nor vice versa): both this resource and the ``get_uc_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://uc/example",
    name="uc_example",
    title="UC Example",
    description=(
        "A complete, valid sample use case document as raw markdown -- frontmatter and "
        "body -- exercising every section, for use as a learning example."
    ),
    mime_type="text/markdown",
)
def uc_example() -> str:
    """Return the packaged UC example's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as ``uc.tools.get_uc_example.get_uc_example`` -- this is simply
    that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

    Returns
    -------
    str
        The example document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("uc", "example")
