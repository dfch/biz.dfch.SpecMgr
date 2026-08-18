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

"""``@mcp.prompt()``: create_adr_test (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Experimental, strictly step-gated variant of ``create_adr`` (see
``adr/prompts/create_adr.py``), kept as a *separate* prompt -- not a
replacement -- so the two can be registered side by side and compared: the
same underlying MADR structure and ``adr/tools/`` sequence, but rewritten
as a series of hard numbered gates ("do not proceed to gate N+1 until gate
N's exit condition is met", "never fabricate a value to pass a gate")
instead of the softer step-by-step narration used by ``create_adr``. This
lets a caller switch between ``create_adr`` and ``create_adr_test`` for
the same topic and observe whether the stricter phrasing measurably
improves compliance (e.g. fewer fabricated mandatory-field values, fewer
skipped duplicate checks) -- see the conversation in
.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11 for the rationale.

Naming note: like ``create_adr`` itself, this prompt's name does not
collide with any ``@mcp.tool()`` -- ``adr/tools/`` has no ``create_adr_test``
tool; the underlying tool sequence driven by this prompt is unchanged
(``create_adr``, ``option_create``, ``set_status``, ``validate_adr``).

The actual instructional text lives in its own packaged data file,
``adr/data/adr_create_test_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``/``$decision_makers``/...), not ``str.format``, precisely so
the instructions file itself is free to use plain, unescaped ``{...}``
braces for the MADR markdown headings it narrates to the LLM (e.g.
``# {title}``) without those colliding with this module's own
substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_adr_test",
    title="Create an ADR (step-gated test variant)",
    description=(
        "Experimental, strictly step-gated variant of create_adr for A/B comparison: "
        "the same MADR-4.0.0 structure and create_adr/option_create/set_status/validate_adr "
        "tool sequence, rewritten as hard numbered gates instead of narrated steps."
    ),
)
def create_adr_test(
    topic: str,
    decision_makers: str | None = None,
    consulted: str | None = None,
    informed: str | None = None,
) -> str:
    """Return step-gated instructional text for drafting a new ADR about ``topic``.

    See ``create_adr`` (``adr/prompts/create_adr.py``) for the non-gated
    baseline this variant is meant to be compared against; the parameters
    and returned-value contract are identical.

    Parameters
    ----------
    topic:
        Free-text description of the decision to be made -- becomes the
        seed for ``title``/``context_and_problem_statement``.
    decision_makers:
        Pre-known ``decision-makers`` frontmatter value, if any; otherwise
        the returned instructions tell the LLM to ask the user.
    consulted:
        Pre-known ``consulted`` frontmatter value, if any.
    informed:
        Pre-known ``informed`` frontmatter value, if any.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.
    """
    template = Template(read_packaged_text("adr", "create_test_instructions", "md"))
    return template.substitute(
        topic=topic,
        decision_makers=decision_makers or "(not given -- ask the user, or omit)",
        consulted=consulted or "(not given -- ask the user, or omit)",
        informed=informed or "(not given -- ask the user, or omit)",
    )
