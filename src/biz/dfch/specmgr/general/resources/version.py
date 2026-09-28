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

"""Resource: specmgr://version — MCP server package version number."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ...models import VersionInfo
from ...server import mcp


@mcp.resource(
    "specmgr://version",
    name="version",
    title="SpecMgr MCP Server Version",
    description=(
        "Installed version number of the biz-dfch-specmgr package that backs "
        "this MCP server, plus the installed fastembed package version (the "
        "similarity extra's embedding backend) or null when that extra is not "
        "installed (read via importlib.metadata, never an import of fastembed "
        "itself; feat-134 Phase 7). Lets a client check compatibility without "
        "a tool round-trip."
    ),
    mime_type="application/json",
)
def version_info() -> VersionInfo:
    """
    Return the installed version numbers of the packages that back this MCP server.

    ``specmgr``: the ``biz-dfch-specmgr`` package version. ``fastembed`` (feat-134
    Phase 7, REQ-014): the installed ``fastembed`` package version (the
    ``similarity`` extra's embedding backend), or ``None`` when the extra is
    not installed (``PackageNotFoundError``) -- read via ``importlib.metadata``,
    never by importing ``fastembed`` itself.

    Returns
    -------
    VersionInfo
        The version of this ``biz-dfch-specmgr`` package, plus the installed
        ``fastembed`` version (or ``None``).
    """
    try:
        fastembed_version: str | None = version("fastembed")
    except PackageNotFoundError:
        fastembed_version = None

    result = VersionInfo(specmgr=version("biz-dfch-specmgr"), fastembed=fastembed_version)
    return result
