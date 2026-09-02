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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: get_adr (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state on every call; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth.
"""

from __future__ import annotations

from ...general.tools._path_safety import assert_within, validate_id
from ...models.adr import Adr
from ...server import mcp
from ._io import load_by_id
from ._paths import adr_base_dir


@mcp.tool(
    name="get_adr",
    title="Get ADR",
    description=(
        "Read, parse, and return a full ADR document (frontmatter and body) by its id. An "
        "invalid id (path-injection attempt or wrong format) is a ValueError raised before "
        "any file access."
    ),
)
def get_adr(id: str) -> Adr:
    """Read and return the ADR identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier (plan §9a).

    Returns
    -------
    Adr
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`._paths.AdrNotFoundError` if no ADR has this id.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not a canonical
        lowercase-hex UUID (feat-38-39-41-43-44 Phase 4, REQ-009; raised
        before any filesystem access).
    """
    validate_id("adr", id)
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    assert_within(base_dir, path)
    return adr
