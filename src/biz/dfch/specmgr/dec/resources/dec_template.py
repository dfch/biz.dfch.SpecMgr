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

"""Resource: specmgr://dec/template (feat-21 Task 3.4).

Read-only, addressable counterpart of the ``get_dec_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_dec_example`` / ``specmgr://dec/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``dec.tools`` (nor vice versa): both this resource and
the ``get_dec_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``gol.resources.gol_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://dec/schema``/``specmgr://dec/example``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://dec/template",
    name="dec_template",
    title="Decision (DEC) Template",
    description=(
        "A DEC document template -- frontmatter and every body field present, populated with "
        "short placeholder ('blind text') content -- as raw markdown, for use as a starting "
        "point when drafting a new decision."
    ),
    mime_type="text/markdown",
)
def dec_template() -> str:
    """Return the packaged DEC template's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as ``dec.tools.get_dec_template.get_dec_template`` -- this is
    simply that same read exposed as an MCP resource instead of a
    ``@mcp.tool()``. Unlike GOL's template, the committed DEC template is
    guaranteed to round-trip through ``parse_dec``: its placeholder content
    satisfies every structural constraint (the RSK precedent, feat-21
    Design Notes).

    Returns
    -------
    str
        The template document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("dec", "template")
