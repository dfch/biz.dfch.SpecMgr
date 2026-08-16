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

"""``@mcp.tool()`` wrapper: update_tsk (Task 3.4).

Same body-only ``content`` shape as ``create_tsk``, but against an
*existing* document: ``id``/``type``/``status``/``created``/``version`` are
all read back from the file currently on disk and preserved unchanged; only
``updated`` is bumped to the current timestamp. ``status`` is never settable
here -- see the dedicated ``set_status_tsk`` tool. Mirrors ``req.tools.update_req``
exactly.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``tsk_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update.
"""

from __future__ import annotations

from datetime import datetime

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Task, TskDocument, TskFrontmatter
from ._io import load_by_id
from ._lock import tsk_lock
from ._paths import tsk_base_dir
from ._write import write_tsk_file


@mcp.tool(
    name="update_tsk",
    title="Update task list",
    description=(
        "Whole-body replace of an existing task list's content, preserving its "
        "id/type/status/created/version; only `updated` changes. Use `set_status_tsk` to "
        "change status instead."
    ),
)
def update_tsk(id: str, content: str) -> TskDocument:
    """Replace the body of the task list identified by ``id``.

    ``content`` is body markdown only, same shape as :func:`.create_tsk.create_tsk`
    -- it must not carry a YAML frontmatter block. Validated the same way:
    ``Task.from_text(format_text(content))``, letting ``AssertionError``
    (structural failure) or ``pydantic.ValidationError`` (field/cross-field
    failure) propagate uncaught, with nothing written in either case. In
    particular, a whole-body replace that drops the last remaining
    ``## Recent Updates`` entry fails validation the same way
    (``RecentUpdates.updates`` requires ``min_length=1``) -- carry forward at
    least one entry, appending a new one rather than removing every existing
    one.

    The existing file is read first (under ``tsk_lock(id)``) to resolve its
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
    TskDocument
        The updated document. Raises :class:`._paths.TskNotFoundError` if
        no task list has this id.
    """
    body = Task.from_text(format_text(content))

    base_dir = tsk_base_dir()
    with tsk_lock(id):
        path, existing = load_by_id(base_dir, id)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = TskFrontmatter(**fm_data)
        new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
        write_tsk_file(path, new_frontmatter, content)
    return new_doc
