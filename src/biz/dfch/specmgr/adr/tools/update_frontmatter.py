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

"""``@mcp.tool()`` wrapper: update_frontmatter (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state, then re-renders and re-writes the full file; there is no
in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file
itself is always the source of truth. The whole sequence runs under
``_lock.adr_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.
"""

from __future__ import annotations

from ...models.adr import Adr, AdrFrontmatter
from ...server import mcp
from ._io import load_by_id, write_adr
from ._lock import adr_lock
from ._paths import adr_base_dir


@mcp.tool(
    name="update_frontmatter",
    title="Update ADR Frontmatter",
    description="Whole-object replace of an ADR's frontmatter (plan §3), preserving its existing id.",
)
def update_frontmatter(id: str, frontmatter: AdrFrontmatter) -> Adr:
    """Replace the frontmatter of the ADR identified by ``id``.

    Whole-object, full-replace semantics (plan §3): the submitted
    ``frontmatter`` entirely replaces the current one. The one exception
    is ``id`` itself -- it is always re-injected from the currently
    resolved document, ignoring whatever ``frontmatter.id`` the caller
    submitted, because the id is system-managed and never changes via this
    tool (plan §9a), even though every other frontmatter key follows
    normal full-replace semantics.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    frontmatter:
        The new frontmatter to write (its ``id`` field is ignored).

    Returns
    -------
    Adr
        The updated document. Raises :class:`._paths.AdrNotFoundError` if
        no ADR has this id.
    """
    base_dir = adr_base_dir()
    with adr_lock(id):
        path, adr = load_by_id(base_dir, id)
        new_frontmatter = frontmatter.model_copy(update={"id": adr.frontmatter.id})
        new_adr = adr.model_copy(update={"frontmatter": new_frontmatter})
        write_adr(path, new_adr)
    return new_adr
