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

"""Resource: specmgr://uc/list (Task 3.1.6).

Implemented as an MCP resource rather than an ``@mcp.tool()``, mirroring
``req.resources.req_list``/``specmgr://req/list``.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...server import mcp
from ..models.v2 import UcSummary
from ..tools._io import read_uc
from ..tools._paths import iter_uc_paths


@mcp.resource(
    "specmgr://uc/list",
    name="uc_list",
    title="Use Case List",
    description=(
        "Ids, titles, statuses, and refs of every use case in the configured "
        "use-case base directory, for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from "
        "disk -- for documents that have no assigned id; use it with the get_uc tool "
        "instead."
    ),
    mime_type="application/json",
)
def uc_list() -> list[UcSummary]:
    """Return a one-line summary of every use case in the configured base directory.

    A file that fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.uc.models.v2.parse_uc` raises) is silently
    skipped -- a single malformed file must not break listing every other
    valid one (mirrors ``uc.tools._paths.find_uc_path``'s own
    skip-on-parse-failure rule).

    Returns
    -------
    list[UcSummary]
        One entry per successfully-parsed ``*.md`` file, in filename-sorted
        order. Empty if the base directory does not exist or holds no use
        cases.
    """
    summaries: list[UcSummary] = []
    for path in iter_uc_paths():
        try:
            doc = read_uc(path)
        except (AssertionError, ValidationError):
            continue
        summaries.append(
            UcSummary(
                id=doc.frontmatter.id,
                title=doc.body.text,
                status=doc.frontmatter.status,
                ref=path.stem,
            )
        )
    return summaries
