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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.prompt()``: update_adr_test (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Experimental, strictly step-gated variant of ``update_adr`` (see
``adr/prompts/update_adr.py``), kept as a *separate* prompt -- not a
replacement -- so the two can be registered side by side and compared:
the same underlying read-first/map-to-tool/validate-last flow, but
rewritten as a series of hard numbered gates ("do not proceed to gate
N+1 until gate N's exit condition is met", "never fabricate a value to
pass a gate") instead of the softer step-by-step narration used by
``update_adr``. This lets a caller switch between ``update_adr`` and
``update_adr_test`` for the same revision and observe whether the
stricter phrasing measurably improves compliance (e.g. always reading
current state first, never guessing at an unspecified change) -- see
the conversation in .specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11 for the rationale.

The actual instructional text lives in its own packaged data file,
``adr/data/adr_update_test_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the ``specmgr://adr/{id}`` resource-template placeholder it narrates
to the LLM without that colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_adr_test",
    title="Update an ADR (step-gated test variant)",
    description=(
        "Experimental, strictly step-gated variant of update_adr for A/B comparison: "
        "the same read-first/map-to-tool/validate-last flow, rewritten as hard numbered "
        "gates instead of narrated steps."
    ),
)
def update_adr_test(id: str, instructions: str | None = None) -> str:
    """Return step-gated instructional text for revising the ADR identified by ``id``.

    See ``update_adr`` (``adr/prompts/update_adr.py``) for the non-gated
    baseline this variant is meant to be compared against; the parameters
    and returned-value contract are identical.

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
    template = Template(read_packaged_text("adr", "update_test_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
