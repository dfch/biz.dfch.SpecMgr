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

"""``@mcp.tool()`` wrapper: set_status_gol (Task 3.5).

The only path that changes a goal's ``status`` -- mirrors
``prb.tools.set_status_prb``/``req.tools.set_status_req``:
:class:`~biz.dfch.specmgr.gol.models.v1.GolFrontmatter.status` has no
``"superseded by ..."`` pattern, just the closed seven-value set
(``draft``/``proposed``/``accepted``/``superseded``/``deprecated``/
``rejected``/``implemented`` -- REQ's exact set, with goal-specific meanings
for ``implemented`` = the goal has genuinely been reached and
``superseded`` = replaced by another goal). Neither ``create_gol`` nor the
generic ``update`` tool in ``general.tools`` accepts a ``status`` argument
at all -- this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.gol.models.v1.GolDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``gol_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.
"""

from __future__ import annotations

from datetime import datetime

import frontmatter

from ...server import mcp
from ..models.v1 import GolDocument, GolFrontmatter
from ._io import load_by_id
from ._lock import gol_lock
from ._paths import gol_base_dir
from ._write import write_gol_file


@mcp.tool(
    name="set_status_gol",
    title="Set goal status",
    description="The only path that changes a goal's status. Also bumps `updated`.",
)
def set_status_gol(id: str, status: str) -> GolDocument:
    """Replace the status of the goal identified by ``id``.

    Reconstructs the frontmatter via :class:`GolFrontmatter`'s own
    constructor (not ``model_copy``), so ``status``'s closed-set validator
    actually runs -- an invalid ``status`` raises ``pydantic.ValidationError``
    uncaught, and nothing is written. Also bumps ``updated`` to the current
    timestamp; every other frontmatter field (``id``/``type``/``created``/
    ``version``) is carried over unchanged. The body is never touched --
    its raw, on-disk markdown (not a render of the parsed model) is read
    back and re-persisted verbatim, so this tool cannot introduce any
    render-fidelity drift into the body at all.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    status:
        The new status. Must be one of ``"draft"``, ``"proposed"``,
        ``"accepted"``, ``"superseded"``, ``"deprecated"``, ``"rejected"``,
        ``"implemented"`` --
        :class:`~biz.dfch.specmgr.gol.models.v1.GolFrontmatter.status`'s
        seven accepted values.

    Returns
    -------
    GolDocument
        The updated document. Raises :class:`._paths.GolNotFoundError` if
        no goal has this id.
    """
    base_dir = gol_base_dir()
    with gol_lock(id):
        path, existing = load_by_id(base_dir, id)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = GolFrontmatter(**fm_data)
        new_doc = GolDocument(frontmatter=new_frontmatter, body=existing.body)
        write_gol_file(path, new_frontmatter, raw_body)
    return new_doc
