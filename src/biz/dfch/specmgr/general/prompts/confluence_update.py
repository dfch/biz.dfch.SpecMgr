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

"""``@mcp.prompt()``: confluence_update (feat-50-confluence Phase 8, REQ-012/ACC-011).

Returns instructional text -- not itself a tool call -- that tells an LLM
to call the ``confluence_update`` ``@mcp.tool()`` (``general/tools/
confluence_update.py``) with the same two parameters given here, so a user
can trigger a Confluence page upload with a single, simple instruction
instead of needing to know the underlying tool's exact name/parameters.

Naming note: this prompt is named ``confluence_update``, the same name as
the ``@mcp.tool()`` in ``general/tools/confluence_update.py``. This is not
a collision -- the MCP protocol keeps prompts and tools in separate
registries (``prompts/list`` vs. ``tools/list``) -- but is called out here
explicitly so the two are not mistaken for the same registration, same
precedent as ``dec.prompts.create_dec``/``gol.prompts.create_gol``/
``req.prompts.create_req``.

Unlike the multi-step, ``TodoWrite``/``question``-tool-driven interview
prompts elsewhere in this codebase (e.g. ``dec.prompts.create_dec``), this
is a thin, single-tool-call prompt: it never reads the Markdown file,
never renders anything, and never calls ``confluence_update`` itself --
exactly like every other prompt in this codebase, it only narrates the one
tool call for the LLM to carry out and asks it to report back the
`version`/`failed_images` values the tool itself returns.

The actual instructional text lives in its own packaged data file,
``general/data/general_confluence_update_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text``.
Placeholders use ``string.Template`` (``$page_url_or_id``/
``$markdown_file_path``), not ``str.format``, so the packaged file is free
to use plain, unescaped ``{...}`` braces of its own.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="confluence_update",
    title="Upload a local Markdown file to a Confluence page",
    description=(
        "Guides the LLM through calling the confluence_update tool with the given "
        "page_url_or_id/markdown_file_path to upload a local Markdown file's rendered "
        "content to an existing Confluence page."
    ),
)
def confluence_update(page_url_or_id: str, markdown_file_path: str) -> str:
    """Return instructional text for uploading ``markdown_file_path`` to ``page_url_or_id``.

    Parameters
    ----------
    page_url_or_id:
        The same value the ``confluence_update`` tool accepts: a bare
        numeric page id, a browsable Confluence page URL, or a REST
        content URL.
    markdown_file_path:
        The same value the ``confluence_update`` tool accepts: the local
        filesystem path to the Markdown file to render and push as the
        page's new body.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        the ``confluence_update`` tool itself -- it only narrates that one
        call for the LLM to carry out.
    """
    template = Template(read_packaged_text("general", "confluence_update_instructions", "md"))
    return template.substitute(page_url_or_id=page_url_or_id, markdown_file_path=markdown_file_path)
