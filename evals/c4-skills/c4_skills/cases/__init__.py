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

"""Case definitions for the c4-skills harness (feat-250).

A case is a prompt plus the gates that decide pass/fail. Phase 100 carries
only the smoke case (Task 100.170); the shared case set of the full run
(``create-system``, ``fix-dsl``, ``mcp-limits``, ``design-views``,
``review-model``, ``no-trigger``) and the per-phase cases land with their
phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import pins

#: The minimum number of bytes a workspace DSL must carry to count as
#: "written" (guards against an empty or stub file).
MIN_DSL_BYTES = 40

#: The DSL keyword every workspace must contain to count as "written".
WORKSPACE_KEYWORD = "workspace"


@dataclass(frozen=True)
class Case:
    """One measurement case.

    Attributes:
        id: Stable case id (the `SMOKE_CASE`/`FULL_CASES` names).
        prompt: The exact prompt sent to `opencode run`.
        gates: The ordered gate names the graders evaluate for this case.
        setup_files: Files pre-placed in the trial work dir before the agent
            starts (relative path -> text), for fix-style cases. Phase 100
            cases place nothing.
    """

    id: str
    prompt: str
    gates: tuple[str, ...] = field(default_factory=tuple)
    setup_files: dict[str, str] = field(default_factory=dict)


SMOKE_CREATE_SYSTEM_PROMPT = """\
Create a small C4 system model of a simple online bookshop in the current working directory.

Write exactly one file named `workspace.dsl` containing a Structurizr DSL workspace with:

- one person (a Customer),
- one software system (Bookshop),
- at least two containers inside the Bookshop system (a Web Store and an Order Processor),
- a relationship from the Customer to the Web Store, and a relationship from the Web Store to the
  Order Processor, each with a technology,
- a system context view for the Bookshop system.

Keep the model minimal: no components, no dynamic views, no deployment views.

Before you finish, check the model with the structurizr `validate` MCP tool and fix every error it
reports. Make sure the final `workspace.dsl` on disk is the exact text you last validated.
"""


#: The Phase 100 smoke case: the smallest shared-case shape, used to
#: measure the real time per trial (Task 100.170).
SMOKE_CASE_DEF = Case(
    id=pins.SMOKE_CASE,
    prompt=SMOKE_CREATE_SYSTEM_PROMPT,
    gates=(
        "dsl_written",
        "cli_valid",
        "cli_export",
        "has_system",
        "has_person",
        "two_containers",
        "relationship_technology",
        "has_view",
    ),
)

#: Every case the harness knows, in canonical order.
CASES: dict[str, Case] = {SMOKE_CASE_DEF.id: SMOKE_CASE_DEF}


def get_case(case_id: str) -> Case:
    """Return the case with `case_id`.

    Args:
        case_id: The stable case id.

    Returns:
        The Case.

    Raises:
        KeyError: If the case is unknown.
    """
    assert isinstance(case_id, str) and case_id
    result = CASES[case_id]
    return result
