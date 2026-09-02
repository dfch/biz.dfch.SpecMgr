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

"""``@mcp.tool()`` wrapper: create_gol (Task 3.3).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_gol`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``prb.tools.create_prb``/``req.tools.create_req`` exactly.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.gol.models.v1.GolDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.
"""

from __future__ import annotations

import uuid

from ...general.tools._doc_paths import slugify
from ...general.tools._timestamps import now_timestamp
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import GolFrontmatter, Goal
from ._paths import ensure_gol_base_dir
from ._write import write_gol_file


@mcp.tool(
    name="create_gol",
    title="Create goal",
    description=(
        "Create a new goal: assigns a fresh id, derives a filename from the body's "
        "H1 title, validates the submitted body-only content, and writes the new "
        "document to the goal base directory. Returns the newly created document's "
        "frontmatter only (no body); use the corresponding `get_gol` tool to fetch "
        "the full document afterward."
    ),
)
def create_gol(content: str) -> GolFrontmatter:
    """Create and write a new goal document.

    ``content`` is body markdown only (the ``Goal`` H1 and its sections) --
    it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh id (``uuid.uuid4()``), ``type="gol"``,
    ``status="draft"`` (always, never caller-supplied on create),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.gol.models.v1.Goal` from it
    (``Goal.from_text(format_text(content))``); a structural failure raises
    ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both re-raised with domain/tool context
    prepended (see Raises below) -- nothing is written in
    either case.

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    GolFrontmatter
        The newly created document's frontmatter only (no body), with its
        assigned id in ``.id``. Use the corresponding ``get_gol`` tool to
        fetch the full document afterward.

    Raises
    ------
    AssertionError
        A structural failure in ``content``. The message is prefixed with domain/tool/channel
        context (e.g. ``"gol create_gol (body): ..."``) by the shared tool-boundary
        wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
        of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
        Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
        written.
    """
    with wrap_tool_errors(domain="gol", tool="create_gol", channel=BODY_CHANNEL):
        body = Goal.from_text(format_text(content))

    new_id = str(uuid.uuid4())
    now = now_timestamp()
    new_frontmatter = GolFrontmatter(
        id=new_id,
        type="gol",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    filename = f"gol-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_gol_base_dir()
    write_gol_file(base_dir / filename, new_frontmatter, content)
    return new_frontmatter
