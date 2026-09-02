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

"""``@mcp.tool()`` wrapper: create_tsk (Task 3.3).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_tsk`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``req.tools.create_req`` exactly.

**No auto-seeding of ``## Recent Updates``.** ``Task.recent_updates.updates``
requires ``min_length=1`` (see the feature README's Decisions Made): this
tool does *not* inject a "Created" entry on the caller's behalf -- it simply
validates whatever ``content`` is submitted via
``Task.from_text(format_text(content))``, exactly like ``create_req`` never
special-cases any of its own mandatory sections. A caller whose submitted
body lacks a ``## Recent Updates`` section with at least one ``### `` entry
gets a validation failure, the same way an empty ``items`` checklist would.
It is the packaged example/template files and the ``create_task`` prompt's
own instructional text that demonstrate/instruct seeding a first entry (e.g.
``### Created``) so a caller drafting new content naturally satisfies the
constraint.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument` -- the ``.md`` file
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
from ..models.v1 import Task, TskFrontmatter
from ._paths import ensure_tsk_base_dir
from ._write import write_tsk_file


@mcp.tool(
    name="create_tsk",
    title="Create task list",
    description=(
        "Create a new task list: assigns a fresh id, derives a filename from the body's "
        "H1 title, validates the submitted body-only content, and writes the new document "
        "to the task list base directory. Returns the newly created document's frontmatter "
        "only (no body); use the corresponding `get_tsk` tool to fetch the full document "
        "afterward."
    ),
)
def create_tsk(content: str) -> TskFrontmatter:
    """Create and write a new task list document.

    ``content`` is body markdown only (the ``Task`` H1 and its sections) --
    it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh id (``uuid.uuid4()``), ``type="tsk"``,
    ``status="draft"`` (always, never caller-supplied on create),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.tsk.models.v1.Task` from it
    (``Task.from_text(format_text(content))``); a structural failure raises
    ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both re-raised with domain/tool context
    prepended (see Raises below) -- nothing is written in
    either case. In particular, a ``content`` whose ``## Recent Updates``
    section has zero ``### `` entries fails this same way
    (``RecentUpdates.updates`` requires ``min_length=1``) -- this tool does
    not auto-seed a first entry; see this module's own docstring.

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    TskFrontmatter
        The newly created document's frontmatter only (no body), with its
        assigned id in ``.id``. Use the corresponding ``get_tsk`` tool to
        fetch the full document afterward.

    Raises
    ------
    AssertionError
        A structural failure in ``content``. The message is prefixed with domain/tool/channel
        context (e.g. ``"tsk create_tsk (body): ..."``) by the shared tool-boundary
        wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
        of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
        Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
        written.
    """
    with wrap_tool_errors(domain="tsk", tool="create_tsk", channel=BODY_CHANNEL):
        body = Task.from_text(format_text(content))

    new_id = str(uuid.uuid4())
    now = now_timestamp()
    new_frontmatter = TskFrontmatter(
        id=new_id,
        type="tsk",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    filename = f"tsk-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_tsk_base_dir()
    write_tsk_file(base_dir / filename, new_frontmatter, content)
    return new_frontmatter
