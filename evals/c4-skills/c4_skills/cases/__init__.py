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
the smoke case (Task 100.170); Phase 110 (Task 110.100) adds its own
cases: ``create-system``, ``mcp-limits``, ``no-trigger`` and the held-out
``heldout-validate``. The remaining shared cases (``fix-dsl``,
``design-views``, ``review-model``) and the other per-phase held-outs land
with their phases.
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


# ---------------------------------------------------------------------------
# Phase 110 gate sets (locked, Task 110.100)
# ---------------------------------------------------------------------------

#: The stream-derived gate set the model-creation cases share: the 8
#: CLI/export gates plus the mandatory validate-loop discipline -- `parse`
#: and `inspect` were called, a `validate` call answered OK, the returned
#: DSL is the exact text that got OK, and every `inspect` finding is
#: triaged (REQ-003).
CREATE_SYSTEM_GATES: tuple[str, ...] = (
    "dsl_written",
    "cli_valid",
    "cli_export",
    "has_system",
    "has_person",
    "two_containers",
    "relationship_technology",
    "has_view",
    "parse_called",
    "validate_ok_called",
    "inspect_called",
    "validated_before_return",
    "triage_complete",
)

#: The `mcp-limits` gate set: the create-system gates plus the
#: acknowledgement that the MCP refused `!include`/`!docs` in the final
#: message (14 gates).
MCP_LIMITS_GATES: tuple[str, ...] = CREATE_SYSTEM_GATES + ("limits_acknowledged",)

#: The `no-trigger` gate set: none of the mounted skills may load, the
#: seeded model file must stay untouched and CLI-valid, and the final
#: message must state the no-image-rendering MCP limit (rendering to image
#: files is a capability none of the five skills owns).
NO_TRIGGER_GATES: tuple[str, ...] = (
    "no_mounted_skill_loaded",
    "file_untouched",
    "cli_valid",
    "mcp_limit_stated",
)

# ---------------------------------------------------------------------------
# Phase 110 cases (locked prompts, Task 110.100)
# ---------------------------------------------------------------------------

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

#: `create-system`: the Phase 100 smoke prompt verbatim (it deliberately
#: mentions only `validate`, never parse/inspect -- that discipline is what
#: the Phase 110 skill injects), graded with the full loop gate set.
CREATE_SYSTEM_CASE_DEF = Case(
    id="create-system",
    prompt=SMOKE_CREATE_SYSTEM_PROMPT,
    gates=CREATE_SYSTEM_GATES,
)

#: `mcp-limits`: the locked multi-file request. The MCP refuses both
#: `!include` and `!docs` (the CLI would accept them), so the
#: discriminating facts are the MCP `OK` byte-identity gates plus the
#: final-message acknowledgement.
MCP_LIMITS_PROMPT = (
    "The team's convention is a multi-file workspace: separate files pulled together with "
    "`!include`, plus a `!docs` documentation folder with a Markdown page. Set that up in "
    "the current working directory, then check the result with the structurizr MCP tools "
    "before you finish."
)

MCP_LIMITS_CASE_DEF = Case(
    id="mcp-limits",
    prompt=MCP_LIMITS_PROMPT,
    gates=MCP_LIMITS_GATES,
)

#: `no-trigger`: the locked prompt asks for a capability none of the five
#: skills owns (rendering image files). The shape must stay valid in
#: Phases 120-150 (a review- or view-flavored prompt would trigger the
#: correct skill in Phase 150/140 and fail the case there).
NO_TRIGGER_PROMPT = (
    "The C4 model is in `workspace.dsl` in the current directory. Render it to image files: "
    "one PNG (or SVG) per view, written into the current directory. Tell me when the images "
    "are ready."
)

#: The `no-trigger` seed: a valid workspace in the shape of the known-good
#: fixture (person, system, two containers, relationships with technology,
#: a system context view), verified against the pinned CLI image at
#: creation (Task 110.100).
NO_TRIGGER_SEED_WORKSPACE = """\
workspace "Library" "A small public library system." {
    model {
        patron = person "Patron" "Borrows books at the library."
        library = softwareSystem "Library" "Manages books and loans." {
            catalog = container "Catalog Web App" "Lets patrons browse the catalogue." "Python"
            circulation = container "Circulation Service" "Records loans and returns." "Java"
        }
        patron -> catalog "Browses the catalogue through" "HTTPS"
        catalog -> circulation "Records loans via" "gRPC"
    }
    views {
        systemContext library "SystemContext" {
            include *
            autoLayout
        }
    }
}
"""

NO_TRIGGER_CASE_DEF = Case(
    id="no-trigger",
    prompt=NO_TRIGGER_PROMPT,
    gates=NO_TRIGGER_GATES,
    setup_files={"workspace.dsl": NO_TRIGGER_SEED_WORKSPACE},
)

#: `heldout-validate`: the same task shape as `create-system` (a person, a
#: software system, at least two containers, relationships with technology,
#: a system context view, the "check with validate before you finish"
#: tail) in a different domain. Held out: registered by its own id
#: constant, never part of `FULL_CASES`, run once at the end of the phase.
HELDOUT_VALIDATE_PROMPT = """\
Create a small C4 system model of a hospital appointment system in the current working directory.

Write exactly one file named `workspace.dsl` containing a Structurizr DSL workspace with:

- one person (a Patient),
- one software system (Appointment System),
- at least two containers inside the Appointment System (a Booking Web App and a Scheduling Service),
- a relationship from the Patient to the Booking Web App, and a relationship from the Booking Web App to the
  Scheduling Service, each with a technology,
- a system context view for the Appointment System.

Keep the model minimal: no components, no dynamic views, no deployment views.

Before you finish, check the model with the structurizr `validate` MCP tool and fix every error it
reports. Make sure the final `workspace.dsl` on disk is the exact text you last validated.
"""

HELDOUT_VALIDATE_CASE_DEF = Case(
    id=pins.HELDOUT_VALIDATE_CASE,
    prompt=HELDOUT_VALIDATE_PROMPT,
    gates=CREATE_SYSTEM_GATES,
)

#: Every case the harness knows, in canonical order.
CASES: dict[str, Case] = {
    CREATE_SYSTEM_CASE_DEF.id: CREATE_SYSTEM_CASE_DEF,
    MCP_LIMITS_CASE_DEF.id: MCP_LIMITS_CASE_DEF,
    NO_TRIGGER_CASE_DEF.id: NO_TRIGGER_CASE_DEF,
    HELDOUT_VALIDATE_CASE_DEF.id: HELDOUT_VALIDATE_CASE_DEF,
    SMOKE_CASE_DEF.id: SMOKE_CASE_DEF,
}


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
