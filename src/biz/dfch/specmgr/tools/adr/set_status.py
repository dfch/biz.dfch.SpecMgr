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

"""``@mcp.tool()`` wrapper: set_status (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.set_status``:
re-reads and re-parses the current on-disk state, then re-renders and
re-writes the full file; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth. The whole sequence runs under ``_lock.adr_lock(id)`` so a
concurrent mutation against the same id cannot interleave with it and
cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.
"""

from __future__ import annotations

from ...models.adr import Adr
from ...models.adr.v1 import mutations
from ...server import mcp
from ._io import load_by_id, write_adr
from ._lock import adr_lock
from ._paths import adr_base_dir


@mcp.tool(
    name="set_status",
    title="Set ADR Status",
    description="Narrow convenience wrapper over a frontmatter update for the common status-change case.",
)
def set_status(id: str, status: str, superseded_by: str | None = None) -> Adr:
    """Replace the status of the ADR identified by ``id``.

    Delegates to ``models.adr.v1.mutations.set_status``: when
    ``superseded_by`` is given, ``status`` is composed as
    ``f"superseded by {superseded_by}"`` instead of being used verbatim.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    status:
        The new status. Ignored if ``superseded_by`` is given.
    superseded_by:
        When given, composes the ``"superseded by ..."`` status string.

    Returns
    -------
    Adr
        The updated document.
    """
    base_dir = adr_base_dir()
    with adr_lock(id):
        path, adr = load_by_id(base_dir, id)
        new_adr = mutations.set_status(adr, status, superseded_by)
        write_adr(path, new_adr)
    return new_adr
