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

"""``@mcp.tool()`` wrapper: update_req (Task 3.13).

Same body-only ``content`` shape as ``create_req`` (Task 3.12), but against
an *existing* document: ``id``/``type``/``status``/``created``/``version``
are all read back from the file currently on disk and preserved unchanged;
only ``updated`` is bumped to the current timestamp. ``status`` is never
settable here -- see the dedicated ``set_status_req`` tool (Task 3.14).

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
of a parsed :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the
``.md`` file itself is always the source of truth. The whole sequence runs
under ``req_lock(id)`` so a concurrent mutation against the same id cannot
interleave with it and cause a lost update (mirrors every ADR mutation
tool's own ``adr_lock`` usage).
"""

from __future__ import annotations

from datetime import datetime

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import ReqDocument, ReqFrontmatter, Requirement
from ._io import load_by_id
from ._lock import req_lock
from ._paths import req_base_dir
from ._write import write_req_file


@mcp.tool(
    name="update_req",
    title="Update requirement",
    description=(
        "Whole-body replace of an existing requirement's content, preserving its "
        "id/type/status/created/version; only `updated` changes. Use `set_status_req` to "
        "change status instead."
    ),
)
def update_req(id: str, content: str) -> ReqDocument:
    """Replace the body of the requirement identified by ``id``.

    ``content`` is body markdown only, same shape as :func:`.create_req.create_req`
    -- it must not carry a YAML frontmatter block. Validated the same way:
    ``Requirement.from_text(format_text(content))``, letting ``AssertionError``
    (structural failure) or ``pydantic.ValidationError`` (field/cross-field
    failure) propagate uncaught, with nothing written in either case.

    The existing file is read first (under ``req_lock(id)``) to resolve its
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
    ReqDocument
        The updated document. Raises :class:`._paths.ReqNotFoundError` if
        no requirement has this id.
    """
    body = Requirement.from_text(format_text(content))

    base_dir = req_base_dir()
    with req_lock(id):
        path, existing = load_by_id(base_dir, id)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = ReqFrontmatter(**fm_data)
        new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
        write_req_file(path, new_frontmatter, content)
    return new_doc
