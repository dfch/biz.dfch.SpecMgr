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

"""``@mcp.prompt()``: create_req (Task 3.19).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Requirement (REQ) document using the existing
``req/tools/``/``req/resources/`` surface (``specmgr://req/list``,
``specmgr://req/template``/``specmgr://req/example``, ``specmgr://req/schema``,
``create_req``, ``validate_req``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_req`` builds the entire REQ frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_req``, the same name as the
``@mcp.tool()`` in ``req/tools/create_req.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are drafting a new Requirement (REQ) document about: {topic}

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_req` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_req` builds
id/type/status/created/updated/version automatically.

## 0. Check for an existing requirement on this topic first
Read the `specmgr://req/list` resource before creating anything. If a
requirement with a similar title or topic already exists, tell the user
about it and ask whether they want to revise that one (via the
`update_req` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new requirement.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {{title}}` -- H1, mandatory, free-form.
- Lead paragraph directly under the H1 -- the requirement statement
  itself, mandatory.
- `## Description` -- optional prose giving context/rationale.
- `## Characteristics` -- mandatory bullet list of ISO 25010:2023 quality
  attributes (e.g. "Functional Suitability", "Performance", "Security");
  at least one item.
- `## Level` -- mandatory single-line obligation strength: one of
  MUST / SHOULD / MUST NOT / SHOULD NOT / MAY.
- `## Priority` -- optional single-line value, 0-99 (lower means more
  important).
- `## Tags` -- optional bullet list of free-form labels.
- `## Source` -- mandatory single-line value naming the origin/authority
  of this requirement.
- `## Related Artifacts` -- optional container for up to four `### `
  cross-reference bullet lists: Requirements, Decisions, Goals,
  Acceptance Criteria (each `{{ID}}: {{description}}` per line).
- `## More Information` -- optional freeform supplementary text.
- `## Notes` -- optional freeform remarks.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the requirement statement,
its characteristics, obligation level, and source, and optionally
priority, tags, related artifacts, description, and notes.

## 3. Use the template/example/schema as references
Fetch `specmgr://req/template` or `specmgr://req/example` as a starting
point/style reference, then check `specmgr://req/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above.
2. Call `create_req(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_req(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_req` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 5. Later revisions
Any later change to this requirement should go through the `update_req`
prompt (or directly through `update_req`/`set_status_req`), not by
re-running this prompt.
"""


@mcp.prompt(
    name="create_req",
    title="Create a requirement",
    description=(
        "Guides the LLM through checking for an existing similar requirement, gathering the "
        "required information, and driving create_req/validate_req to author a new REQ document."
    ),
)
def create_req(topic: str) -> str:
    """Return instructional text for drafting a new requirement about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the requirement to be drafted -- becomes
        the seed for the document's title and requirement statement.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    return _INSTRUCTIONS_TEMPLATE.format(topic=topic)
