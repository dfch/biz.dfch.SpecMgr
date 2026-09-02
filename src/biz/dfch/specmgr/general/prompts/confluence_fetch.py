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

"""``@mcp.prompt()``: confluence_fetch (feat-50-confluence Phase 8, REQ-013/ACC-012).

Returns instructional text -- not itself a tool call -- that tells an LLM
to call the ``confluence_fetch`` ``@mcp.tool()`` (``general/tools/
confluence_fetch.py``) with the same parameters given here, so a user can
trigger a Confluence page/attachment download with a single, simple
instruction instead of needing to know the underlying tool's exact name/
parameters.

Naming note: this prompt is named ``confluence_fetch``, the same name as
the ``@mcp.tool()`` in ``general/tools/confluence_fetch.py``. This is not
a collision -- the MCP protocol keeps prompts and tools in separate
registries (``prompts/list`` vs. ``tools/list``) -- but is called out here
explicitly for the same reason as ``general.prompts.confluence_update``'s
own docstring note (precedent: ``dec.prompts.create_dec``/
``gol.prompts.create_gol``/``req.prompts.create_req``).

Same thin, single-tool-call, non-calling contract as
``general.prompts.confluence_update``: this prompt never fetches anything
itself, it only narrates the one tool call for the LLM to carry out.

The actual instructional text lives in its own packaged data file,
``general/data/general_confluence_fetch_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text``.
Placeholders use ``string.Template`` (``$url``/``$destination_path``), not
``str.format``. ``destination_path`` is optional on the underlying tool
(only needed for a binary/non-text fetch, per
``ConfluenceDestinationPathRequiredError``); when it is not given here, a
literal explanatory placeholder string is substituted instead of a blank,
mirroring ``general.prompts.compact_history``'s own
``cutoff_hint or "(not given -- ...)"`` pattern.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="confluence_fetch",
    title="Fetch a Confluence page or attachment",
    description=(
        "Guides the LLM through calling the confluence_fetch tool with the given url (and, "
        "when needed, destination_path) to fetch/download a Confluence page or attachment."
    ),
)
def confluence_fetch(url: str, destination_path: str | None = None) -> str:
    """Return instructional text for fetching ``url`` via the ``confluence_fetch`` tool.

    Parameters
    ----------
    url:
        The same value the ``confluence_fetch`` tool accepts: a URL that
        case-insensitively matches the configured base URL.
    destination_path:
        The same value the ``confluence_fetch`` tool accepts: the
        filesystem path to write non-text/binary response content to.
        Only required when the fetched content turns out to be binary
        (e.g. an image); omit it for a normal page/text fetch.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        the ``confluence_fetch`` tool itself -- it only narrates that one
        call for the LLM to carry out.
    """
    template = Template(read_packaged_text("general", "confluence_fetch_instructions", "md"))
    return template.substitute(
        url=url,
        destination_path=destination_path or "(not given -- only needed if the target is binary/image content)",
    )
