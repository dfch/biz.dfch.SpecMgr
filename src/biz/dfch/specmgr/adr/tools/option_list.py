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

"""``@mcp.tool()`` wrapper: option_list (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.option_list``:
re-reads and re-parses the current on-disk state; there is no in-memory
cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file itself is
always the source of truth.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.
"""

from __future__ import annotations

from ...models.adr.v1 import mutations
from ...server import mcp
from ._io import load_by_id
from ._paths import adr_base_dir


@mcp.tool(
    name="option_list",
    title="List ADR Options",
    description="Full titles of every current 'Option N: ...' sub-section, in document order (plan §5).",
)
def option_list(id: str) -> list[str]:
    """Return the full titles of every option on the ADR identified by ``id``.

    Read-only -- does not write.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    list[str]
        Full titles, e.g. ``["Option 1: A title"]``, in document order.
    """
    base_dir = adr_base_dir()
    _, adr = load_by_id(base_dir, id)
    return mutations.option_list(adr)
