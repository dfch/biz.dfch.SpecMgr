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
held-out ``heldout-dsl``; Phase 130 (Task 130.100) adds ``modeling-
decisions`` and the held-out ``heldout-modeling``; Phase 140 (Task
140.100) adds ``design-views`` and the held-out ``heldout-views``. The
remaining shared case (``review-model``) and the last held-out land with
their phase.
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
        forbidden_element_names: Names the case forbids from appearing as a
            container or a component of the produced model (for the Phase
            130 `no_library_container` gate -- the scenario's shared
            library, which C4 models as no element at all). Phase 130
            (Task 130.100) adds this; earlier cases carry nothing.
        expected_container_count: The exact number of containers the
            scenario implies (for the Phase 130 `container_count` gate --
            the scenario's two application parts plus its own database; a
            library or a third-party service modeled as a container raises
            the count). None when the case pins no count.
    """

    id: str
    prompt: str
    gates: tuple[str, ...] = field(default_factory=tuple)
    setup_files: dict[str, str] = field(default_factory=dict)
    seed_elements: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    seed_relationships: tuple[tuple[str, str, str], ...] = field(default_factory=tuple)
    forbidden_element_names: tuple[str, ...] = field(default_factory=tuple)
    expected_container_count: int | None = None


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

# ---------------------------------------------------------------------------
# Phase 130 gate set (Task 130.100)
# ---------------------------------------------------------------------------

#: The `modeling-decisions` gate set: the standard create-family shape
#: gates (the workspace validates and exports, carries a person, a system,
#: exactly the scenario's container count -- two application parts plus the
#: scenario's own database -- technologies on every relationship, a
#: description on every element, a user-defined view) plus
#: `validate_ok_called` (the prompt carries the create-family
#: "check with the structurizr MCP tools before you finish" tail,
#: deliberately naming no tool -- the Phase 110 precedent) and the three
#: new modeling-decision gates: `no_library_container` (the scenario's
#: shared library is NOT a container or component -- the C4 answer),
#: `external_system_tagged` (the third-party service is a TOP-LEVEL element
#: carrying the `External` tag -- the pinned DSL has no `externalSystem`
#: keyword, so the export's `model.externalSystems` is never the place to
#: look), and `no_vague_labels` (no relationship carries a forbidden vague
#: description). Deliberately NO loop-discipline gates (`parse_called`/
#: `inspect_called`/`triage_complete`/`validated_before_return`): that
#: discipline belongs to the `structurizr-validate-loop` skill (the locked
#: Phase 120 separation) -- this skill's delta is the modeling knowledge,
#: and its primary case carries that delta.
MODELING_DECISIONS_GATES: tuple[str, ...] = (
    "dsl_written",
    "cli_valid",
    "cli_export",
    "has_system",
    "has_person",
    "container_count",
    "relationship_technology",
    "elements_described",
    "has_view",
    "validate_ok_called",
    "no_library_container",
    "external_system_tagged",
    "no_vague_labels",
)

# ---------------------------------------------------------------------------
# Phase 130 cases (Task 130.100)
# ---------------------------------------------------------------------------

#: The `modeling-decisions` prompt: a CREATE task (a fresh
#: `workspace.dsl` from a scenario prompt -- the create-family shape, NOT a
#: fix/seeded case). The scenario is plain business language that never
#: states the C4 answers: it names one user role, one owned system with two
#: application parts, a shared library embedded in both, a third-party
#: service operated by a different organization, and one in-house database.
#: The answers (the library is no element, the third-party service is a
#: top-level `External`-tagged element, the database IS a container) are
#: exactly what the `c4-modeling` skill teaches. The tail carries the
#: create-family "check with the structurizr MCP tools" wording without
#: naming any tool (the Phase 110 precedent: the prompt never names
#: parse/inspect).
MODELING_DECISIONS_PROMPT = """\
Create a C4 model of our parcel delivery tracking platform in the current working directory.

Write exactly one file named `workspace.dsl` containing a Structurizr DSL workspace for the following situation:

- Customers use the platform to look up the status of their parcels.
- The platform is the Parcel Tracker system, owned and operated by our company. It has two application parts:
  a web portal where customers look up shipments, and a dispatch service that assigns parcels to couriers.
- Both application parts embed our shared pricing rules library, which computes delivery prices from weight and zone.
- The dispatch service sends customer notification emails through an email delivery provider that is operated by
  a different organization.
- The platform stores shipments and dispatch records in its own database, which we operate.

Keep the model minimal: nothing beyond what the situation above contains.

Before you finish, check with the structurizr MCP tools and fix every error they report. Make sure the final
`workspace.dsl` on disk is the exact text you last checked.
"""

#: The `modeling-decisions` scenario facts (locked, Task 130.100): the
#: shared library's name -- forbidden as a container or component
#: (`no_library_container`) -- and the exact container count the scenario
#: implies (`container_count`): the two application parts plus the in-house
#: database.
MODELING_DECISIONS_FORBIDDEN_NAMES: tuple[str, ...] = ("Pricing Rules Library",)
MODELING_DECISIONS_EXPECTED_CONTAINERS = 3

MODELING_DECISIONS_CASE_DEF = Case(
    id="modeling-decisions",
    prompt=MODELING_DECISIONS_PROMPT,
    gates=MODELING_DECISIONS_GATES,
    forbidden_element_names=MODELING_DECISIONS_FORBIDDEN_NAMES,
    expected_container_count=MODELING_DECISIONS_EXPECTED_CONTAINERS,
)

#: `heldout-modeling`: the same task shape as `modeling-decisions` (a fresh
#: workspace from a business scenario whose modeling decisions are the
#: test), a different domain (home energy management -- not
#: bookshop/hospital/library/parking/museum, per the locked guardrail) and
#: the same gate family with its own scenario facts (the shared rates
#: library, the same three-container count). Held out: registered by its
#: own id constant, never part of `FULL_CASES`, never tuned with, run once
#: at the end of the phase (the `HELDOUT_DSL_CASE` precedent).
HELDOUT_MODELING_PROMPT = """\
Create a C4 model of our home energy management platform in the current working directory.

Write exactly one file named `workspace.dsl` containing a Structurizr DSL workspace for the following situation:

- Homeowners use the platform to manage their household's energy use and costs.
- The platform is the Energy Manager system, owned and operated by our company. It has two application parts:
  a dashboard web app where homeowners see consumption and costs, and a scheduling service that plans charging
  and heating.
- Both application parts embed our shared rates library, which computes energy prices from tariff and time of day.
- The scheduling service fetches live meter readings from a smart meter provider that is operated by a different
  organization.
- The platform stores meter readings and schedules in its own database, which we operate.

Keep the model minimal: nothing beyond what the situation above contains.

Before you finish, check with the structurizr MCP tools and fix every error they report. Make sure the final
`workspace.dsl` on disk is the exact text you last checked.
"""

#: The `heldout-modeling` scenario facts (the same locked family, the
#: held-out domain's own names).
HELDOUT_MODELING_FORBIDDEN_NAMES: tuple[str, ...] = ("Rates Library",)
HELDOUT_MODELING_EXPECTED_CONTAINERS = 3

HELDOUT_MODELING_CASE_DEF = Case(
    id=pins.HELDOUT_MODELING_CASE,
    prompt=HELDOUT_MODELING_PROMPT,
    gates=MODELING_DECISIONS_GATES,
    forbidden_element_names=HELDOUT_MODELING_FORBIDDEN_NAMES,
    expected_container_count=HELDOUT_MODELING_EXPECTED_CONTAINERS,
)

# ---------------------------------------------------------------------------
# Phase 140 gate set (Task 140.100)
# ---------------------------------------------------------------------------

#: The `design-views` gate set: the standard create-family shape gates
#: (the workspace validates and exports, carries a person, a system, a
#: description on every element, a technology on every relationship, a
#: user-defined view) plus `validate_ok_called` (the prompt carries the
#: create-family "check with the structurizr MCP tools before you finish"
#: tail, deliberately naming no tool -- the Phase 110/130 precedent),
#: `external_system_tagged` (the scenario's two third-party services are
#: operated by a different organization -- a TOP-LEVEL element carrying
#: the `External` tag, the Phase 130 gate) and the two new view-design
#: gates: `views_within_element_bound` (every user-defined view carries at
#: most the locked 20-element bound -- the scenario's 23 elements make a
#: single `include *` container view 22 elements, necessarily over) and
#: `explicit_view_keys` (every view has an explicit key -- a view the DSL
#: wrote without a key exports under an auto-generated `<Kind>-NNN` key
#: with `generatedKey: true`). Deliberately NO loop-discipline gates
#: (`parse_called`/`inspect_called`/`triage_complete`/
#: `validated_before_return`): the locked Phase 120/130 separation -- this
#: skill's delta is the view design.
DESIGN_VIEWS_GATES: tuple[str, ...] = (
    "dsl_written",
    "cli_valid",
    "cli_export",
    "has_system",
    "has_person",
    "elements_described",
    "relationship_technology",
    "has_view",
    "validate_ok_called",
    "external_system_tagged",
    "views_within_element_bound",
    "explicit_view_keys",
)

# ---------------------------------------------------------------------------
# Phase 140 cases (Task 140.100)
# ---------------------------------------------------------------------------

#: The `design-views` prompt: a CREATE task (a fresh `workspace.dsl` from
#: a scenario prompt -- the create-family shape, NOT a fix/seeded case),
#: larger than any earlier case: 23 elements in total (one person role,
#: one owned system, 19 application parts, two third-party services
#: operated by a different organization), so a single `include *`
#: container view necessarily carries 22 elements -- over the locked
#: 20-element bound -- while a well-designed split (several views with
#: explicit include lists, each within the bound, explicit keys) satisfies
#: every gate. The scenario is plain business language that never states
#: the view-design answers (no "view", no "split", no element-per-view
#: numbers -- the view design is the skill's delta), with the create-
#: family tail "check with the structurizr MCP tools before you finish"
#: (no tool named -- the Phase 110/130 precedent).
DESIGN_VIEWS_PROMPT = """\
Create a C4 model of our online banking platform in the current working directory.

Write exactly one file named `workspace.dsl` containing a Structurizr DSL workspace for the following situation:

- Bank customers use the platform to manage their accounts, move money, and track their activity.
- The platform is the Bank Portal system, owned and operated by our company. Its application parts are:
  - a web portal where customers log in and manage their accounts,
  - a mobile app backend that serves the bank's mobile app,
  - an account service that holds the customer account records,
  - a transaction service that processes deposits, withdrawals, and transfers,
  - a payment service that executes card payments and bank transfers,
  - a card service that manages debit and credit cards,
  - a fraud detection service that scores transactions for fraud,
  - a notification service that sends email and SMS alerts,
  - an onboarding service that verifies new customers,
  - a statements service that generates monthly statements,
  - a direct debit service that processes standing orders and direct debits,
  - an exchange rates service that provides currency conversion rates,
  - a batch scheduler that runs the nightly interest calculation and reconciliation,
  - an event queue that carries internal events between the application parts,
  - a ledger database that stores every account movement,
  - a customer database that stores account and profile records,
  - an audit database that stores the compliance audit trail,
  - a cache that stores sessions and frequently read account data, and
  - a document store that holds the generated statement PDFs.
- The payment service routes card authorisations through a card payment network that is
  operated by a different organization.
- The onboarding service performs credit checks through a credit reference agency that is
  operated by a different organization.
- The web portal and the mobile app backend reach the account, transaction, payment, card,
  statements, and direct debit services.
- The transaction service updates the ledger, scores transactions with the fraud detection
  service, and publishes events to the event queue.
- The notification service consumes events from the event queue, the statements service
  reads the ledger and writes to the document store, and the batch scheduler reads and
  writes the ledger and the customer database.
- The card service and the exchange rates service serve the payment service, and the
  onboarding service reads the customer database.

Keep the model minimal: nothing beyond what the situation above contains.

Before you finish, check with the structurizr MCP tools and fix every error they report. Make sure the final
`workspace.dsl` on disk is the exact text you last checked.
"""

DESIGN_VIEWS_CASE_DEF = Case(
    id="design-views",
    prompt=DESIGN_VIEWS_PROMPT,
    gates=DESIGN_VIEWS_GATES,
)

#: `heldout-views`: the same task shape as `design-views` (a fresh
#: workspace from a >20-element business scenario whose view design is
#: the test), a different domain (insurance claims -- not
#: bookshop/hospital/library/parking/museum/parcel/home-energy/banking,
#: per the locked guardrail) with its own scenario facts (19 application
#: parts, the two third-party services a national claims data bureau and
#: a clearing house) and the same locked gate family. Held out:
#: registered by its own id constant, never part of `FULL_CASES`, never
#: tuned with, run once at the end of the phase (the
#: `HELDOUT_MODELING_CASE` precedent).
HELDOUT_VIEWS_PROMPT = """\
Create a C4 model of our insurance claims platform in the current working directory.

Write exactly one file named `workspace.dsl` containing a Structurizr DSL workspace for the following situation:

- Policyholders use the platform to report claims and track their progress.
- The platform is the Claims Center system, owned and operated by our insurance company. Its application parts are:
  - a web portal where policyholders report claims and track their progress,
  - a mobile app backend that serves the insurer's mobile app,
  - a claims intake service that registers new claims,
  - a triage service that classifies and prioritizes claims,
  - an assessment service that calculates settlement amounts,
  - a payout service that executes claim settlements,
  - a fraud screening service that flags suspicious claims,
  - a document service that accepts claim photos and reports,
  - a notification service that emails and messages policyholders,
  - an assignment service that routes claims to adjusters,
  - an adjuster workbench where staff process their assigned claims,
  - a policy verification service that checks that a claim is covered by the policy,
  - a reinsurance allocation service that apportions large losses across reinsurance partners,
  - a batch scheduler that runs the nightly reserves calculation,
  - an event queue that carries claim events between the application parts,
  - a claims database that stores claim records,
  - a policy database that stores policy and cover records,
  - an audit database that stores the compliance audit trail, and
  - a document store that holds claim photos, reports, and correspondence.
- The fraud screening service consults a national claims data bureau that is
  operated by a different organization.
- The payout service executes settlements through a clearing house that is
  operated by a different organization.
- The web portal and the mobile app backend reach the intake, assessment, payout, document,
  and notification services.
- The claims intake service hands accepted claims to the triage service, the triage service
  routes them to the assessment service, and the assessment service requests settlements
  from the payout service.
- The fraud screening service screens each incoming claim, the policy verification service
  checks the cover, and the assignment service routes the claim to the adjuster workbench.
- The document service reads from the document store, the batch scheduler reads and writes
  the claims and policy databases, and the notification service reports claim status changes.

Keep the model minimal: nothing beyond what the situation above contains.

Before you finish, check with the structurizr MCP tools and fix every error they report. Make sure the final
`workspace.dsl` on disk is the exact text you last checked.
"""

HELDOUT_VIEWS_CASE_DEF = Case(
    id=pins.HELDOUT_VIEWS_CASE,
    prompt=HELDOUT_VIEWS_PROMPT,
    gates=DESIGN_VIEWS_GATES,
)

#: Every case the harness knows, in canonical order.
CASES: dict[str, Case] = {
    CREATE_SYSTEM_CASE_DEF.id: CREATE_SYSTEM_CASE_DEF,
    DESIGN_VIEWS_CASE_DEF.id: DESIGN_VIEWS_CASE_DEF,
    FIX_DSL_CASE_DEF.id: FIX_DSL_CASE_DEF,
    MODELING_DECISIONS_CASE_DEF.id: MODELING_DECISIONS_CASE_DEF,
    MCP_LIMITS_CASE_DEF.id: MCP_LIMITS_CASE_DEF,
    NO_TRIGGER_CASE_DEF.id: NO_TRIGGER_CASE_DEF,
    HELDOUT_VALIDATE_CASE_DEF.id: HELDOUT_VALIDATE_CASE_DEF,
    HELDOUT_DSL_CASE_DEF.id: HELDOUT_DSL_CASE_DEF,
    HELDOUT_MODELING_CASE_DEF.id: HELDOUT_MODELING_CASE_DEF,
    HELDOUT_VIEWS_CASE_DEF.id: HELDOUT_VIEWS_CASE_DEF,
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
