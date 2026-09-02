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

"""``@mcp.tool()`` wrapper: create_adr (plan §8, §9a, §10 item 4; Task 3.2).

Thin file-I/O adapter -- writes a brand-new ``.md`` file; there is no
in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file
itself is always the source of truth.

Unlike the eleven whole-body domains' ``create_<d>`` tools, ``frontmatter``/
``body`` here are already-typed Pydantic models (validated by the MCP SDK's
own parameter parsing *before* this function body ever runs) rather than a
raw ``content: str`` this function validates itself -- so there is little
left for :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors` to
catch at this call site (see the feature README's Decisions Made); it is
still applied around the final :class:`Adr` construction for consistency
with every other domain's ``create_<d>`` (REQ-005).
"""

from __future__ import annotations

import uuid

from ...models.adr import Adr, AdrBody, AdrFrontmatter
from ...models.md._errors import wrap_tool_errors
from ...server import mcp
from ._io import write_adr
from ._paths import ensure_adr_base_dir, slugify


@mcp.tool(
    name="create_adr",
    title="Create ADR",
    description=(
        "Create a new ADR: assigns a fresh id, derives a filename from the title, "
        "validates, renders, and writes the new document to the ADR base directory."
    ),
)
def create_adr(frontmatter: AdrFrontmatter, body: AdrBody) -> Adr:
    """Create and write a new ADR document.

    A fresh id (``uuid.uuid4()``) is generated and always overwrites
    whatever ``frontmatter.id`` the caller submitted -- the id is
    system-managed and assigned exactly once, at creation time (plan §9a),
    the same "system-owned id" rule :func:`~.update_frontmatter.update_frontmatter`
    applies on every subsequent edit. The filename is ``f"{id}-{slug}.md"``,
    where ``slug`` is derived from ``body.title`` (plan §9a).

    Parameters
    ----------
    frontmatter:
        The new document's frontmatter. Any submitted ``id`` is ignored.
    body:
        The new document's body.

    Returns
    -------
    Adr
        The newly created document, with its assigned id in
        ``frontmatter.id``.

    Raises
    ------
    pydantic.ValidationError
        ``frontmatter``/``body`` themselves are validated by the MCP SDK's own parameter
        parsing before this function is even called (not caught here); the message is
        prefixed with domain/tool context by the shared tool-boundary wrapper
        (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`) only for the unlikely
        case of a failure in the final :class:`Adr` construction below.
    """
    new_id = str(uuid.uuid4())
    final_frontmatter = frontmatter.model_copy(update={"id": new_id})
    filename = f"{new_id}-{slugify(body.title)}.md"

    base_dir = ensure_adr_base_dir()
    with wrap_tool_errors(domain="adr", tool="create_adr"):
        new_adr = Adr(frontmatter=final_frontmatter, body=body)
    write_adr(base_dir / filename, new_adr)
    return new_adr
