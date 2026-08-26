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

"""``@mcp.tool()`` wrapper: update_rsk (Task 3.4).

Same body-only ``content`` shape as ``create_rsk``, but against an
*existing* document: ``id``/``type``/``status``/``created``/``version`` are
all read back from the file currently on disk and preserved unchanged; only
``updated`` is bumped to the current timestamp. ``status`` is never settable
here -- see the dedicated ``set_status_rsk`` tool. Mirrors
``tsk.tools.update_tsk`` exactly.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``rsk_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.
"""

from __future__ import annotations

from datetime import datetime

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Risk, RskDocument, RskFrontmatter
from ._io import load_by_id
from ._lock import rsk_lock
from ._paths import rsk_base_dir
from ._write import write_rsk_file


@mcp.tool(
    name="update_rsk",
    title="Update risk",
    description=(
        "Whole-body replace of an existing risk's content, preserving its "
        "id/type/status/created/version; only `updated` changes. Use `set_status_rsk` to "
        "change status instead."
    ),
)
def update_rsk(id: str, content: str) -> RskDocument:
    """Replace the body of the risk identified by ``id``.

    ``content`` is body markdown only, same shape as :func:`.create_rsk.create_rsk`
    -- it must not carry a YAML frontmatter block. Validated the same way:
    ``Risk.from_text(format_text(content))``, letting ``AssertionError``
    (structural failure) or ``pydantic.ValidationError`` (field/cross-field
    failure) propagate uncaught, with nothing written in either case.

    The existing file is read first (under ``rsk_lock(id)``) to resolve its
    path and current frontmatter; every frontmatter field except ``updated``
    is carried over unchanged -- ``status`` in particular is never settable
    through this tool.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    content:
        The replacement body markdown, with no frontmatter block.

    Returns
    -------
    RskDocument
        The updated document. Raises :class:`._paths.RskNotFoundError` if
        no risk has this id.
    """
    body = Risk.from_text(format_text(content))

    base_dir = rsk_base_dir()
    with rsk_lock(id):
        path, existing = load_by_id(base_dir, id)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = RskFrontmatter(**fm_data)
        new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
        write_rsk_file(path, new_frontmatter, content)
    return new_doc
