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

"""``@mcp.tool()`` wrapper: create_req (Task 3.12).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_req`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended (Task 3.9's
design). There is therefore no ``write_req``/``render_req`` in
``req.tools._io`` for this tool to call -- the frontmatter+content
composition is factored into ``req.tools._write.write_req_file`` instead,
shared with the generic ``update`` tool in ``general.tools``.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from ...general.tools._doc_paths import slugify
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import ReqDocument, ReqFrontmatter, Requirement
from ._paths import ensure_req_base_dir
from ._write import write_req_file


@mcp.tool(
    name="create_req",
    title="Create requirement",
    description=(
        "Create a new requirement: assigns a fresh id, derives a filename from the body's "
        "H1 title, validates the submitted body-only content, and writes the new document "
        "to the requirement base directory."
    ),
)
def create_req(content: str) -> ReqDocument:
    """Create and write a new requirement document.

    ``content`` is body markdown only (the ``Requirement`` H1 and its
    sections) -- it must not carry a YAML frontmatter block. The entire
    frontmatter is built by this tool: a fresh id (``uuid.uuid4()``),
    ``type="req"``, ``status="draft"`` (always, never caller-supplied on
    create), ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.req.models.v1.Requirement` from it
    (``Requirement.from_text(format_text(content))``); a structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
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
    ReqDocument
        The newly created document, with its assigned id in
        ``frontmatter.id``.

    Raises
    ------
    AssertionError
        A structural failure in ``content``. The message is prefixed with domain/tool/channel
        context (e.g. ``"req create_req (body): ..."``) by the shared tool-boundary
        wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
        of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
        Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
        written.
    """
    with wrap_tool_errors(domain="req", tool="create_req", channel=BODY_CHANNEL):
        body = Requirement.from_text(format_text(content))

    new_id = str(uuid.uuid4())
    now = datetime.now().isoformat(timespec="microseconds")
    new_frontmatter = ReqFrontmatter(
        id=new_id,
        type="req",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)

    filename = f"req-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_req_base_dir()
    write_req_file(base_dir / filename, new_frontmatter, content)
    return new_doc
