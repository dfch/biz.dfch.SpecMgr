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

"""``@mcp.tool()`` wrapper: option_delete (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over
``models.adr.v1.mutations.option_delete``: re-reads and re-parses the
current on-disk state, then re-renders and re-writes the full file; there
is no in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md``
file itself is always the source of truth. The whole sequence runs
under ``_lock.adr_lock(id)`` so a concurrent mutation against the same
id cannot interleave with it and cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.
"""

from __future__ import annotations

from ...models.adr.v1 import mutations
from ...server import mcp
from ._io import load_by_id, write_adr
from ._lock import adr_lock
from ._paths import adr_base_dir


@mcp.tool(
    name="option_delete",
    title="Delete ADR Option",
    description="Remove the option named full_title (plan §5), returning the remaining full titles.",
)
def option_delete(id: str, full_title: str) -> list[str]:
    """Remove one option from the ADR identified by ``id``.

    Does not renumber or reorder the remaining options -- deleting one
    leaves a gap in the numbering (plan §5). Lets
    :class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError` propagate
    if no option matches ``full_title``; nothing is written in that case.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    full_title:
        The option's full title, e.g. ``"Option 1: A title"``.

    Returns
    -------
    list[str]
        The remaining options' full titles, in their original order.
    """
    base_dir = adr_base_dir()
    with adr_lock(id):
        path, adr = load_by_id(base_dir, id)
        new_adr, remaining = mutations.option_delete(adr, full_title)
        write_adr(path, new_adr)
    return remaining
