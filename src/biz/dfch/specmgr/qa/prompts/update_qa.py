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

"""``@mcp.prompt()``: update_qa (Phase 4, Task 4.3).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Question and Answer (QA) document by id, using
the existing ``qa/tools/`` surface (``get_qa``, ``update_qa``,
``set_status_qa``, ``validate_qa``). Structural shape ported 1:1 from
``req.prompts.update_req``, with the instructional content rewritten to
describe QA's own schema and lifecycle instead of REQ's. Like ``get_req``,
step 1 points at the ``get_qa`` tool, not a ``specmgr://qa/{id}`` resource
-- there is no such resource; see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: QA's lifecycle surface is deliberately small
-- a whole-body replace (``update_qa``) plus a single, dedicated
status-change path (``set_status_qa``) -- so the tool-mapping section below
is correspondingly shorter.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are revising an existing Question and Answer (QA) document, id: {id}

Requested change: {instructions}

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_qa` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_qa(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the introduction, raw requirements, any of the
  nine ISO/IEC 25010:2023 category sections (`Functional Suitability`,
  `Performance Efficiency`, `Compatibility`, `Interaction Capability`,
  `Reliability`, `Security`, `Maintainability`, `Flexibility`,
  `Safety`), a Q&A pair's `comment`/`requirement`/`question`/`answer`,
  or `more_information` -- -> `update_qa(id, content)`. `content` is
  body markdown only (no frontmatter block) and is a **whole-body replace**:
  read the current body first (step 1) and carry forward every section you
  are not intentionally changing, or it will be dropped, including the
  nine fixed category headings even when you have nothing new to add
  under a given one. `id`/`type`/`status`/`created`/`version` are
  preserved automatically regardless of what you submit; only `updated`
  changes.
- A change to `status` -> `set_status_qa(id, status)` instead --
  `update_qa` never accepts or changes `status`. `status` must be one
  of: draft, active, done, cancelled.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://qa/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_qa(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_qa` already performs the same
validation internally, so this step is never required, only a
convenience.
"""


@mcp.prompt(
    name="update_qa",
    title="Update a QA document",
    description=(
        "Guides the LLM through revising an existing QA document by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_qa(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the QA document identified by ``id``.

    Parameters
    ----------
    id:
        The existing document's specmgr-assigned identifier.
    instructions:
        Free-text description of the requested change. When absent, the
        returned instructions tell the LLM to ask the user first rather
        than guessing.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    return _INSTRUCTIONS_TEMPLATE.format(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
