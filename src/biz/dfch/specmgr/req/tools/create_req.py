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

Thin file-I/O adapter. The ``.md`` file itself is always the source of
truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3); the in-memory cache
warmed after the write below (feat-107-doc-cache Phase 3, REQ-003) is only
ever a content-hash-validated memoization of that file's own current
state, never an independent fact.
"""

from __future__ import annotations

import uuid

from ...general.models import ValidateResult, ValidationErrorEntry
from ...general.tools._doc_paths import slugify
from ...general.tools._timestamps import now_timestamp
from ...general.tools.validate import _CAUGHT_EXCEPTIONS, _MAX_VALIDATE_ERROR_CHARS
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text, snippet
from ...server import mcp
from ..models.v1 import ReqFrontmatter, Requirement
from ._io import read_req
from ._paths import ensure_req_base_dir
from ._write import write_req_file


@mcp.tool(
    name="create_req",
    title="Create requirement",
    description=(
        "Create a new requirement: assigns a fresh id, derives a filename from the body's "
        "H1 title, validates the submitted body-only content, and writes the new document "
        "to the requirement base directory. A content-validation failure of the submitted body "
        "returns a non-raising `ValidateResult` (`valid=False`, a single `errors[].message` capped "
        "at 300 chars as the generic `validate` tool caps it, feat-110) instead of raising "
        "`AssertionError`/`pydantic.ValidationError` (ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e, "
        "GitHub issue #204 -- case 5 of the ADR 519d1206 non-raising-structured-result workaround "
        "chain); nothing is written in that case. Returns the newly created document's frontmatter "
        "only (no body); use the corresponding `get_req` tool to fetch the full document "
        "afterward."
    ),
)
def create_req(content: str) -> ReqFrontmatter | ValidateResult:
    """Create and write a new requirement document.

    ``content`` is body markdown only (the ``Requirement`` H1 and its
    sections) -- it must not carry a YAML frontmatter block. The entire
    frontmatter is built by this tool: a fresh id (``uuid.uuid4()``),
    ``type="req"``, ``status="draft"`` (always, never caller-supplied on
    create), ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.req.models.v1.Requirement` from it
    (``Requirement.from_text(format_text(content))``). A structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError`` -- but this tool catches both
    (feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
    case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
    structured-result workaround chain) and returns the enriched message
    (domain/tool/channel context prepended by the shared tool-boundary
    wrapper, :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`,
    on top of the engine's own field-path/line/snippet enrichment,
    feat-27-validation Phases 1/2) as the non-raising
    ``ValidateResult(valid=False, ...)`` (see Returns below) instead --
    nothing is written in that case.

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    ReqFrontmatter | ValidateResult
        The newly created document's frontmatter only (no body), with its
        assigned id in ``.id``. Use the corresponding ``get_req`` tool to
        fetch the full document afterward. On a content-validation failure
        of ``content``, a non-raising
        :class:`~biz.dfch.specmgr.general.models.ValidateResult`
        (``valid=False``) with exactly one ``errors`` entry whose
        ``message`` is the enriched exception text capped at 300 chars
        exactly as the generic ``validate`` tool caps it (feat-110, via
        :func:`~biz.dfch.specmgr.models.md._markdown.snippet`), instead of
        ``AssertionError``/``pydantic.ValidationError`` -- nothing is written
        in that case (feat-204-create-error, ADR
        f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case 5 of the ADR
        519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result
        workaround chain).
    """
    try:
        with wrap_tool_errors(domain="req", tool="create_req", channel=BODY_CHANNEL):
            body = Requirement.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    new_id = str(uuid.uuid4())
    now = now_timestamp()
    new_frontmatter = ReqFrontmatter(
        id=new_id,
        type="req",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    filename = f"req-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_req_base_dir()
    path = base_dir / filename
    write_req_file(path, new_frontmatter, content)
    read_req(path)  # warm the cache with this write's own validated content (feat-107-doc-cache Phase 3, REQ-003)
    return new_frontmatter
