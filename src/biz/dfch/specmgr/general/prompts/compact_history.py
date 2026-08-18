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

"""``@mcp.prompt()``: compact_history (Various improvements, Task 0.21).

Returns instructional text -- not itself a tool call -- that guides an LLM
through rotating older ``### Recent Updates`` entries out of a `.specmgr`
feature folder's ``README.md`` and into an optional sibling ``history.md``,
per ADR e369ee2e-3353-4f92-991c-6367d76d832e's chosen option (which
documents this rotation mechanism but deliberately leaves its exact
trigger/cutoff undecided, to be resolved case-by-case). This complements
the domain-specific ``create_*``/``update_*``/``refine`` prompts but is
itself cross-cutting: it operates on *any* feature folder under
``.specmgr/feat/<feature_id>/``, not on a specific document domain, so it
lives under ``general.prompts`` rather than any single domain package.

Unlike every domain document type (ADR/REQ/UC/TSK/QA), feature folders have
no dedicated parser/get/update MCP tools of their own -- there is no
``get_feature``/``update_feature`` to call here. This prompt's instructions
therefore rely entirely on the LLM's own file read/edit/write tools
operating directly on ``README.md``/``history.md``, not on any specmgr
tool.

The actual instructional text lives in its own packaged data file,
``general/data/general_compact_history_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text`` --
following the same packaging convention already used for prompt
instructions in the ``qa``/``adr``/``req``/``tsk`` domains (Task 0.19.1,
Task 0.20). Placeholders use ``string.Template``
(``$feature_id``/``$cutoff_hint``), not ``str.format``, so the packaged
file is free to use plain, unescaped ``{...}`` braces of its own.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="compact_history",
    title="Compact a feature folder's Recent Updates history",
    description=(
        "Guides the LLM through rotating older 'Recent Updates' entries out of a .specmgr "
        "feature folder's README.md and into an optional sibling history.md, leaving a pointer "
        "line behind, per ADR e369ee2e-3353-4f92-991c-6367d76d832e."
    ),
)
def compact_history(feature_id: str, cutoff_hint: str | None = None) -> str:
    """Return instructional text for compacting a feature folder's Recent Updates section.

    Parameters
    ----------
    feature_id:
        The `.specmgr/feat/<feature_id>/` folder name (e.g.
        ``"feat-7-various-improvements"``), whose `README.md` should be
        compacted.
    cutoff_hint:
        Free-text description of the rotation rule to apply, e.g. "keep
        the last 3 dated entries" or "keep entries from the last 30 days".
        When absent or ambiguous, the returned instructions tell the LLM
        to ask the user via the `question` tool rather than guessing.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    template = Template(read_packaged_text("general", "compact_history_instructions", "md"))
    return template.substitute(
        feature_id=feature_id,
        cutoff_hint=cutoff_hint or "(not given -- ask the user before choosing a rotation rule)",
    )
