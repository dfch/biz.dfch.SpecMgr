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

"""``@mcp.tool()`` wrapper: create_qa (Phase 4, Task 4.1).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_qa`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended (mirrors
``req.tools.create_req``'s design exactly). There is therefore no
``write_qa``/``render_qa`` in ``qa.tools._io`` for this tool to call -- the
frontmatter+content composition is factored into
``qa.tools._write.write_qa_file`` instead, shared with ``update_qa``.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.qa.models.v1.QaDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from ...general.tools._doc_paths import slugify
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Qa, QaDocument, QaFrontmatter
from ._paths import ensure_qa_base_dir
from ._write import write_qa_file


@mcp.tool(
    name="create_qa",
    title="Create QA document",
    description=(
        "Create a new Question and Answer (QA) document: assigns a fresh id, derives a filename "
        "from the body's H1 title, validates the submitted body-only content, and writes the new "
        "document to the QA base directory."
    ),
)
def create_qa(content: str) -> QaDocument:
    """Create and write a new Question and Answer (QA) document.

    ``content`` is body markdown only (the ``Qa`` H1 and its sections) --
    it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh id (``uuid.uuid4()``), ``type="qa"``,
    ``status="draft"`` (always, never caller-supplied on create),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.qa.models.v1.Qa` from it
    (``Qa.from_text(format_text(content))``); a structural failure raises
    ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both uncaught -- nothing is written in
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
    QaDocument
        The newly created document, with its assigned id in
        ``frontmatter.id``.
    """
    body = Qa.from_text(format_text(content))

    new_id = str(uuid.uuid4())
    now = datetime.now().isoformat(timespec="microseconds")
    new_frontmatter = QaFrontmatter(
        id=new_id,
        type="qa",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    new_doc = QaDocument(frontmatter=new_frontmatter, body=body)

    filename = f"qa-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_qa_base_dir()
    write_qa_file(base_dir / filename, new_frontmatter, content)
    return new_doc
