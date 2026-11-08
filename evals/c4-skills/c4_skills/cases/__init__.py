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
``heldout-validate``; Phase 120 (Task 120.100) adds ``fix-dsl`` and the
held-out ``heldout-dsl``. The remaining shared cases (``design-views``,
``review-model``) and the other per-phase held-outs land with their
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
        seed_elements: The seeded elements a fix-style case must keep
            (``(kind, name)`` pairs; `kind` is one of `person`, `system`,
            `container`, `custom`), for the `no_deletions` gate. Phase 120
            (Task 120.100) adds this; earlier cases carry nothing.
        seed_relationships: The seeded relationships a fix-style case must
            keep (``(source_name, destination_name, description)`` triples),
            for the `no_deletions` gate. The description is the relationship
            identity (the DSL distinguishes same-pair relationships by
            description only), so rewording a seeded relationship counts as
            removing it.
    """

    id: str
    prompt: str
    gates: tuple[str, ...] = field(default_factory=tuple)
    setup_files: dict[str, str] = field(default_factory=dict)
    seed_elements: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    seed_relationships: tuple[tuple[str, str, str], ...] = field(default_factory=tuple)


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

# ---------------------------------------------------------------------------
# Phase 120 gate set (Task 120.100)
# ---------------------------------------------------------------------------

#: The `fix-dsl` gate set: the CLI/export gates over the repaired workspace
#: (the file must validate and export), the shape gates (the seeded model
#: structure is still there), the knowledge gates `validate` cannot surface
#: (a technology and a description on every relationship, a description on
#: every element -- a baseline that only chases `validate` errors never
#: sees the second half of these defects), and the anti-deletion gate
#: (every seeded element and relationship is still present, over the export
#: JSON). Deliberately NO loop-discipline gates (`parse_called`/
#: `inspect_called`/`triage_complete`/`validated_before_return`): that
#: discipline belongs to the `structurizr-validate-loop` skill and is
#: already measured on the reused `create-system`/`mcp-limits` cases.
FIX_DSL_GATES: tuple[str, ...] = (
    "dsl_written",
    "cli_valid",
    "cli_export",
    "has_system",
    "has_person",
    "two_containers",
    "has_view",
    "relationship_technology",
    "relationships_described",
    "elements_described",
    "no_deletions",
)

# ---------------------------------------------------------------------------
# Phase 120 cases (Task 120.100)
# ---------------------------------------------------------------------------

#: The `fix-dsl` prompt: the `fix-forward-reference` precedent's wording
#: (that case "did not discriminate" per its own evals -- a single obvious
#: defect; `fix-dsl` is harder: the seeded defects span at least three of
#: the locked gotcha classes, and the knowledge gates enforce the authoring
#: rules `validate` never reports).
FIX_DSL_PROMPT = (
    "Our Structurizr workspace in `workspace.dsl` in the current working directory fails to validate and "
    "I can't see why. Fix it so it validates, without removing any people, systems, containers, or "
    "relationships."
)

#: The `fix-dsl` seed (parking domain): a realistic workspace carrying
#: five defects across all five locked gotcha classes --
#: 1. quoting: the person's description is unquoted (`Too many tokens`);
#: 2. duplicate identifier: the second container reuses `entry`;
#: 3. forward reference: `billing -> traffic` precedes `traffic`'s
#:    declaration;
#: 4. a relationship missing its technology: `driver -> entry "Enters
#:    through"` (neither `validate` nor `inspect` of a *valid* file is
#:    chased by a baseline without the authoring knowledge);
#: 5. an element missing its description: `traffic = element "City
#:    Traffic Feed"` (a custom element's missing metadata is not even
#:    flagged by `inspect` -- pure authoring knowledge).
#: Verified against the pinned CLI image at creation (Task 120.100): the
#: seed fails `validate` (the error cascade is quoting -> duplicate ->
#: forward reference), and the known-good fixed reference
#: (`tests/evals/fixtures/workspaces/fixdsl-fixed/`) passes every gate.
FIX_DSL_SEED_WORKSPACE = """\
workspace "ParkFlow" "Manages a multi-level parking garage." {
    model {
        driver = person "Driver" Arrives at and departs from the garage.
        garage = softwareSystem "Parking Garage" "Manages bays, entry, exit, and billing." {
            entry = container "Entry Gate Controller" "Reads licence plates and drives the entry barrier." "C/C++"
            entry = container "Exit Gate Controller" "Drives the exit barrier." "C/C++"
            billing = container "Billing Service" "Calculates fees and issues invoices." "Java"
        }
        entry -> billing "Registers bay occupancy in" "gRPC"
        exit -> billing "Clears bay occupancy in" "gRPC"
        billing -> traffic "Considers live traffic from" "REST/JSON"
        driver -> entry "Enters through"
        traffic = element "City Traffic Feed"
    }
    views {
        systemContext garage "GarageContext" {
            include *
            autoLayout
        }
    }
}
"""

#: The `fix-dsl` seed's elements and relationships (the `no_deletions`
#: facts): everything the prompt forbids to remove, keyed by name.
FIX_DSL_SEED_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("person", "Driver"),
    ("custom", "City Traffic Feed"),
    ("system", "Parking Garage"),
    ("container", "Entry Gate Controller"),
    ("container", "Exit Gate Controller"),
    ("container", "Billing Service"),
)
FIX_DSL_SEED_RELATIONSHIPS: tuple[tuple[str, str, str], ...] = (
    ("Driver", "Entry Gate Controller", "Enters through"),
    ("Entry Gate Controller", "Billing Service", "Registers bay occupancy in"),
    ("Exit Gate Controller", "Billing Service", "Clears bay occupancy in"),
    ("Billing Service", "City Traffic Feed", "Considers live traffic from"),
)

FIX_DSL_CASE_DEF = Case(
    id="fix-dsl",
    prompt=FIX_DSL_PROMPT,
    gates=FIX_DSL_GATES,
    setup_files={"workspace.dsl": FIX_DSL_SEED_WORKSPACE},
    seed_elements=FIX_DSL_SEED_ELEMENTS,
    seed_relationships=FIX_DSL_SEED_RELATIONSHIPS,
)

#: `heldout-dsl`: the same task shape as `fix-dsl` (a seeded broken
#: workspace to repair without deletions), a different domain (museum
#: ticketing) and a different defect placement (the quoting defect on the
#: person's description, the duplicate on `shop`, the forward reference to
#: `payment`, the missing technology on `visitor -> shop`, the missing
#: description on the `Ticket Kiosk` container). Held out: registered by
#: its own id constant, never part of `FULL_CASES`, run once at the end
#: of the phase.
HELDOUT_DSL_SEED_WORKSPACE = """\
workspace "Museum Ticketing" "Sells and validates museum entry." {
    model {
        visitor = person "Museum Visitor" Buys tickets and plans visits
        ticketing = softwareSystem "Museum Ticketing" "Sells tickets and manages entry." {
            shop = container "Ticket Shop" "Online ticket sales." "Python"
            shop = container "Ticket Kiosk"
            scanner = container "Entry Scanner" "Validates tickets at the door." "C/C++"
        }
        scanner -> shop "Validates tickets in" "gRPC"
        shop -> payment "Authorises charges to" "REST/JSON"
        payment = element "Payment Provider" "Processes card payments."
        visitor -> shop "Buys tickets through"
    }
    views {
        systemContext ticketing "TicketingContext" {
            include *
            autoLayout
        }
    }
}
"""

HELDOUT_DSL_SEED_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("person", "Museum Visitor"),
    ("custom", "Payment Provider"),
    ("system", "Museum Ticketing"),
    ("container", "Ticket Shop"),
    ("container", "Ticket Kiosk"),
    ("container", "Entry Scanner"),
)
HELDOUT_DSL_SEED_RELATIONSHIPS: tuple[tuple[str, str, str], ...] = (
    ("Entry Scanner", "Ticket Shop", "Validates tickets in"),
    ("Ticket Shop", "Payment Provider", "Authorises charges to"),
    ("Museum Visitor", "Ticket Shop", "Buys tickets through"),
)

HELDOUT_DSL_CASE_DEF = Case(
    id=pins.HELDOUT_DSL_CASE,
    prompt=FIX_DSL_PROMPT,
    gates=FIX_DSL_GATES,
    setup_files={"workspace.dsl": HELDOUT_DSL_SEED_WORKSPACE},
    seed_elements=HELDOUT_DSL_SEED_ELEMENTS,
    seed_relationships=HELDOUT_DSL_SEED_RELATIONSHIPS,
)

#: Every case the harness knows, in canonical order.
CASES: dict[str, Case] = {
    CREATE_SYSTEM_CASE_DEF.id: CREATE_SYSTEM_CASE_DEF,
    FIX_DSL_CASE_DEF.id: FIX_DSL_CASE_DEF,
    MCP_LIMITS_CASE_DEF.id: MCP_LIMITS_CASE_DEF,
    NO_TRIGGER_CASE_DEF.id: NO_TRIGGER_CASE_DEF,
    HELDOUT_VALIDATE_CASE_DEF.id: HELDOUT_VALIDATE_CASE_DEF,
    HELDOUT_DSL_CASE_DEF.id: HELDOUT_DSL_CASE_DEF,
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
