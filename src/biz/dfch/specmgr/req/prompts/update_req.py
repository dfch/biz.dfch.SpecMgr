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

"""``@mcp.prompt()``: update_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Requirement (REQ) document by id, using the
existing ``req/tools/`` surface (``get_req``, ``update_req``,
``set_status_req``, ``validate_req``). Unlike an earlier revision of this
prompt, step 1 no longer points at a ``specmgr://req/{id}`` resource -- that
resource was removed in favor of the ``get_req`` tool (feat-7-various-
improvements Task 0.9, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: REQ's lifecycle surface (Task 3.9's design) is
deliberately small -- a whole-body replace (``update_req``) plus a single,
dedicated status-change path (``set_status_req``) -- so the tool-mapping
section below is correspondingly shorter.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are revising an existing Requirement (REQ) document, id: {id}

Requested change: {instructions}

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_req` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_req(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the requirement statement, `description`,
  `characteristics`, `level`, `priority`, `tags`, `source`,
  `related_artifacts`, `more_information`, or `notes` -- ->
  `update_req(id, content)`. `content` is body markdown only (no
  frontmatter block) and is a **whole-body replace**: read the current
  body first (step 1) and carry forward every section you are not
  intentionally changing, or it will be dropped. `id`/`type`/`status`/
  `created`/`version` are preserved automatically regardless of what you
  submit; only `updated` changes.
- A change to `status` -> `set_status_req(id, status)` instead --
  `update_req` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, superseded, deprecated, rejected,
  implemented.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://req/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_req(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_req` already performs the same
validation internally, so this step is never required, only a
convenience.
"""


@mcp.prompt(
    name="update_req",
    title="Update a requirement",
    description=(
        "Guides the LLM through revising an existing requirement by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_req(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the requirement identified by ``id``.

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
