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

"""``@mcp.tool()`` wrapper: create_vcr (Task 2.1).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_vcr`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``dec.tools.create_dec`` file-for-file.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.vcr.models.v1.VcrDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.
"""

from __future__ import annotations

import uuid

from ...general.tools._doc_paths import slugify
from ...general.tools._timestamps import now_timestamp
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Vcr, VcrDocument, VcrFrontmatter
from ._paths import ensure_vcr_base_dir
from ._write import write_vcr_file


@mcp.tool(
    name="create_vcr",
    title="Create verification case record",
    description=(
        "Create a new verification case record: assigns a fresh id, derives a filename from the "
        "body's H1 title, validates the submitted body-only content, and writes the new "
        "document to the verification case record base directory."
    ),
)
def create_vcr(content: str) -> VcrDocument:
    """Create and write a new verification case record document.

    ``content`` is body markdown only (the ``Vcr`` H1 and its sections) --
    it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh id (``uuid.uuid4()``), ``type="vcr"``,
    ``status="draft"`` (always, never caller-supplied on create),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.vcr.models.v1.Vcr` from it
    (``Vcr.from_text(format_text(content))``); a structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
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
    VcrDocument
        The newly created document, with its assigned id in
        ``frontmatter.id``.
    """
    body = Vcr.from_text(format_text(content))

    new_id = str(uuid.uuid4())
    now = now_timestamp()
    new_frontmatter = VcrFrontmatter(
        id=new_id,
        type="vcr",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    new_doc = VcrDocument(frontmatter=new_frontmatter, body=body)

    filename = f"vcr-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_vcr_base_dir()
    write_vcr_file(base_dir / filename, new_frontmatter, content)
    return new_doc
