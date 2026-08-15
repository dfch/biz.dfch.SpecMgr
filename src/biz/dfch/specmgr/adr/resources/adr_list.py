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

"""Resource: specmgr://adr/list (plan §8, §9a).

Implemented as an MCP resource rather than an ``@mcp.tool()`` (plan §9a),
matching this repo's existing ``specmgr://version`` convention.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...models.adr import AdrParseError, AdrSummary
from ...server import mcp
from ..tools._io import read_adr
from ..tools._paths import adr_base_dir, iter_adr_paths


@mcp.resource(
    "specmgr://adr/list",
    name="adr_list",
    title="ADR List",
    description=(
        "Ids, titles, statuses, and refs of every ADR in the configured ADR base "
        "directory (SPECMGR_ADR_DIR), for context before addressing one by id. "
        "'ref' is an opaque, extensionless identifier -- not a filename to read from "
        "disk -- for documents that have no assigned id; use get_adr/specmgr://adr/{id} "
        "with it instead."
    ),
    mime_type="application/json",
)
def adr_list() -> list[AdrSummary]:
    """Return a one-line summary of every ADR in the configured base directory.

    A file that fails to parse (:class:`AdrParseError` or
    ``pydantic.ValidationError``) is silently skipped -- a single malformed
    file must not break listing every other valid one (mirrors
    ``adr.tools._paths.find_adr_path``'s own skip-on-parse-failure rule).

    Returns
    -------
    list[AdrSummary]
        One entry per successfully-parsed ``*.md`` file, in filename-sorted
        order. Empty if the base directory does not exist or holds no ADRs.
    """
    base_dir = adr_base_dir()
    summaries: list[AdrSummary] = []
    for path in iter_adr_paths(base_dir):
        try:
            adr = read_adr(path)
        except (AdrParseError, ValidationError):
            continue
        summaries.append(
            AdrSummary(id=adr.frontmatter.id, title=adr.body.title, status=adr.frontmatter.status, ref=path.stem)
        )
    return summaries
