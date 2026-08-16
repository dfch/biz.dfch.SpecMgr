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

"""``@mcp.prompt()``: create_task (Task 3.13).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Task List (TSK) document using the existing
``tsk/tools/``/``tsk/resources/`` surface (``specmgr://tsk/list``,
``specmgr://tsk/template``/``specmgr://tsk/example``, ``specmgr://tsk/schema``,
``create_tsk``, ``validate_tsk``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_tsk`` builds the entire TSK frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_task`` (the issue's literal
wording), not ``create_tsk`` -- deliberately distinct from the
``tsk``-prefixed convention the tools/resources use, per the feature
README's Design Notes. This is not a collision with the ``create_tsk``
``@mcp.tool()`` either way -- the MCP protocol keeps prompts and tools in
separate registries (``prompts/list`` vs. ``tools/list``).
"""

from __future__ import annotations

from ...server import mcp

_INSTRUCTIONS_TEMPLATE = """\
You are drafting a new Task List (TSK) document about: {topic}

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_tsk` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_tsk` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing task list on this topic first
Read the `specmgr://tsk/list` resource before creating anything. If a
task list with a similar title or topic already exists, tell the user
about it and ask whether they want to revise that one (via the
`update_task` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new task list.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {{title}}` -- H1, mandatory, free-form.
- `<!-- optional leading comment -->` -- optional HTML comment right
  after the H1, giving context for the task list as a whole.
- A flat checklist, one `- [ ] ...`/`- [x] ...` entry per line --
  mandatory, at least one item. No phases, no per-item `depends on`/
  `status` metadata -- this is a deliberately lightweight, flat list.
- `## Recent Updates` -- mandatory H2 section holding at least one
  `### {{free-form title}}` entry (e.g. `### Created`), each followed by
  a short paragraph of update text. A freshly drafted task list must
  include at least one Recent Updates entry describing why this list
  was made -- `RecentUpdates.updates` requires `min_length>=1`, so an
  empty section (or omitting it) will fail validation. `create_tsk`
  does not seed this entry automatically; you must include it yourself.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the checklist items to
track, and a short description of why this task list is being created
for the first `## Recent Updates` entry.

## 3. Use the template/example/schema as references
Fetch `specmgr://tsk/template` or `specmgr://tsk/example` as a starting
point/style reference, then check `specmgr://tsk/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above, including at
   least one checklist item and at least one `## Recent Updates` entry.
2. Call `create_tsk(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_tsk(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_tsk` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 5. Later revisions
Any later change to this task list should go through the `update_task`
prompt (or directly through `update_tsk`/`set_status_tsk`), not by
re-running this prompt. To work through the checklist itself, use the
`implement_task` prompt instead.
"""


@mcp.prompt(
    name="create_task",
    title="Create a task list",
    description=(
        "Guides the LLM through checking for an existing similar task list, gathering the "
        "required information, and driving create_tsk/validate_tsk to author a new TSK document."
    ),
)
def create_task(topic: str) -> str:
    """Return instructional text for drafting a new task list about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the task list to be drafted -- becomes
        the seed for the document's title and checklist items.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    return _INSTRUCTIONS_TEMPLATE.format(topic=topic)
