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

"""The case gates: pass/fail decisions from the real Structurizr CLI.

The gates never grep the DSL. They run against the trial work dir through
the pinned Structurizr CLI image (``validate``, ``export -format json``,
``inspect``) and then decide purely on the collected inputs:

- the parsed JSON export (``export -format json``) -- the jq-style queries
  are implemented as pure Python over that dict so the unit tests (Task
  100.160, ACC-006) can run on committed pre-exported JSON fixtures with no
  Docker and no model call;
- the CLI exit codes (a workspace the CLI rejects fails the gates, whatever
  the agent said it did).

Phase 110 (Task 110.100) adds the stream-derived gates over the same pure
surface: they decide on the trial's parsed event stream and its computed
metrics (the agent's MCP calls, skills loaded, `inspect`-finding triage,
the final message), carried by :class:`GateContext` alongside the
CLI/work-dir inputs. Phase 120 (Task 120.100) adds the `fix-dsl`
knowledge gates over the export JSON: `elements_described` and
`relationships_described` (completeness rules `validate` cannot surface --
a relationship's missing technology/description and a custom element's
missing metadata pass `validate` cleanly, and the latter is not even
flagged by `inspect` in the pinned CLI), and `no_deletions` (every element
and relationship the case seeded is still present, matched by name over
the export JSON -- the anti-deletion half of the fix-style cases).
Phase 130 (Task 130.100) adds the modeling-decision gates over the export
JSON: `container_count` (the model carries exactly the scenario's
container count -- the scenario's two application parts plus its own
database, so a library or a third-party service modeled as a container
raises the count), `no_library_container` (the scenario's shared library
appears as no container or component -- a negative-presence gate by name),
`external_system_tagged` (a TOP-LEVEL `softwareSystem` or custom `element`
carries the `External` tag -- the pinned DSL has no `externalSystem`
keyword, so the export's `model.externalSystems` section is never the
place to look), and `no_vague_labels` (no relationship carries a
forbidden vague description). Phase 140 (Task 140.100) adds the
view-design gates over the export JSON: `views_within_element_bound`
(every user-defined view -- `generatedKey` filtered out, the `has_view`
precedent -- carries at most the locked `VIEW_ELEMENT_BOUND` of 20
elements, the spike's practical bound; a view's element list is the
exported `elements` array -- the scoped containers/components plus every
linked element, the scoped system itself not counted -- and a filtered
view, which the pinned exporter writes without an `elements` list, is
bounded by its base view's count) and `explicit_view_keys` (every view in
the export JSON carries an explicit key -- a view whose DSL omitted the
key is exported under an auto-generated `<Kind>-NNN` key, e.g.
`Container-001`, with `generatedKey: true`, verified against the pinned
CLI). All gates -- the original 8 (unwrapped over `GateContext.inputs`,
behavior unchanged) and the new ones -- are keyed in :data:`GATES`;
:func:`grade_case` evaluates a case's gate names over one context.

The split is: :func:`collect_inputs` (Docker-dependent, one real CLI run per
command) and :func:`grade_case` (pure, unit-tested).
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from . import pins, preflight
from .cases import MIN_DSL_BYTES, Case, WORKSPACE_KEYWORD
from .events import ParsedTrial

if TYPE_CHECKING:
    # metrics imports graders (GraderInputs, the coverage query), so the
    # metrics names graders needs are imported locally inside the gates
    # that use them (a top-level import would be a cycle); the annotation
    # only needs the name.
    from .metrics import TrialMetrics

# ---------------------------------------------------------------------------
# the collected inputs (the pure side never touches Docker)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraderInputs:
    """Everything the pure gates need, collected from one trial work dir.

    Attributes:
        dsl_path: The workspace DSL file the trial produced (path relative
            to the work dir), or None if no .dsl file exists.
        dsl_text: Its content, or None.
        validate_rc: The CLI `validate` exit code, or None if it could not
            run (missing file).
        validate_stderr: The CLI `validate` stderr (the error text).
        export_json: The parsed `export -format json` document, or None on
            any export failure.
        export_rc: The CLI `export` exit code, or None if it could not run.
        export_stderr: The CLI `export` stderr.
        inspect_rc: The CLI `inspect` exit code, or None if it could not run.
        inspect_findings: The CLI `inspect` finding lines (empty if none or
            inspect could not run).
    """

    dsl_path: str | None
    dsl_text: str | None
    validate_rc: int | None
    validate_stderr: str
    export_json: dict | None
    export_rc: int | None
    export_stderr: str
    inspect_rc: int | None
    inspect_findings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GateResult:
    """The outcome of one gate.

    Attributes:
        name: The gate name (the case's `gates` entry).
        passed: Whether the gate passed.
        detail: A one-line human-readable explanation (failure reasons).
    """

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class GateContext:
    """Everything one gate may need, for one trial (Phase 110).

    The original 8 gates only look at `inputs`; the stream-derived gates
    look at `trial`/`metrics` (and, for `no_mounted_skill_loaded`,
    `skills_installed`). `case` is carried so gates may read the case's own
    facts (e.g. `setup_files` for `file_untouched`).

    Attributes:
        inputs: The collected CLI/work-dir inputs (`collect_inputs`).
        case: The case being graded (its `gates` and `setup_files`).
        trial: The trial's parsed event stream (`events.parse_events_file`).
        metrics: The trial's computed metrics (`metrics.compute_metrics`,
            run over `trial` + `inputs` before grading).
        skills_installed: The skill names the condition installed into the
            work dir before the agent started (empty for `none`).
    """

    inputs: GraderInputs
    case: Case
    trial: ParsedTrial
    metrics: "TrialMetrics"
    skills_installed: tuple[str, ...]


# ---------------------------------------------------------------------------
# the jq-style queries as pure Python over the export JSON
# ---------------------------------------------------------------------------


def _model(export_json: dict | None) -> dict:
    """Return the `model` section of an export JSON (empty if absent)."""
    if not export_json:
        return {}
    result = export_json.get("model")
    return result if isinstance(result, dict) else {}


def iter_people(export_json: dict | None) -> list[dict]:
    """Return every person element of the export JSON."""
    result = _model(export_json).get("people")
    return [e for e in (result or []) if isinstance(e, dict)]


def iter_systems(export_json: dict | None) -> list[dict]:
    """Return every software system element of the export JSON."""
    result = _model(export_json).get("softwareSystems")
    return [e for e in (result or []) if isinstance(e, dict)]


def iter_external_systems(export_json: dict | None) -> list[dict]:
    """Return every external system element of the export JSON."""
    result = _model(export_json).get("externalSystems")
    return [e for e in (result or []) if isinstance(e, dict)]


def iter_custom_elements(export_json: dict | None) -> list[dict]:
    """Return every custom element of the export JSON.

    The DSL `element` keyword (elements that sit outside the C4 model,
    e.g. hardware or third-party feeds) exports to `model.customElements`;
    unlike every other element kind, a custom element's description is the
    `metadata` field (absent, not empty, when the DSL gave none).
    """
    result = _model(export_json).get("customElements")
    return [e for e in (result or []) if isinstance(e, dict)]


def iter_containers(export_json: dict | None) -> list[dict]:
    """Return every container element (inside software systems)."""
    result: list[dict] = []
    for system in iter_systems(export_json):
        for e in system.get("containers") or []:
            if isinstance(e, dict):
                result.append(e)
    return result


def iter_components(export_json: dict | None) -> list[dict]:
    """Return every component element (inside containers)."""
    result: list[dict] = []
    for container in iter_containers(export_json):
        for e in container.get("components") or []:
            if isinstance(e, dict):
                result.append(e)
    return result


def iter_relationships(export_json: dict | None) -> list[dict]:
    """Return every unique model relationship of the export JSON.

    Relationships are nested per element. Views duplicate them as linked
    relationships (carrying `linkedRelationshipId` -- the view-scoped copy
    of a canonical model relationship); those are excluded, and the rest
    are deduped by id.
    """
    seen: set[str] = set()
    result: list[dict] = []
    for elements in (
        iter_people(export_json),
        iter_systems(export_json),
        iter_external_systems(export_json),
        iter_containers(export_json),
    ):
        for element in elements:
            for r in element.get("relationships") or []:
                if not isinstance(r, dict) or "linkedRelationshipId" in r:
                    continue
                rid = r.get("id")
                if rid is None or rid in seen:
                    continue
                seen.add(rid)
                result.append(r)
    return result


def iter_views(export_json: dict | None) -> list[dict]:
    """Return every view of every kind in the export JSON."""
    views = export_json.get("views") if export_json else None
    if not isinstance(views, dict):
        return []
    result: list[dict] = []
    for value in views.values():
        if isinstance(value, list):
            result.extend(v for v in value if isinstance(v, dict))
        elif isinstance(value, dict):
            for nested in value.values():
                if isinstance(nested, list):
                    result.extend(v for v in nested if isinstance(v, dict))
    return result


def relationship_technology_coverage(export_json: dict | None) -> float | None:
    """Return the fraction of relationships carrying a technology.

    Returns:
        0.0-1.0, or None when the model has no relationships at all.
    """
    rels = iter_relationships(export_json)
    if not rels:
        return None
    with_tech = sum(1 for r in rels if str(r.get("technology") or "").strip())
    result = with_tech / len(rels)
    return result


# ---------------------------------------------------------------------------
# the gates (pure)
# ---------------------------------------------------------------------------


def gate_dsl_written(inputs: GraderInputs) -> GateResult:
    """`dsl_written`: a non-trivial workspace DSL exists in the work dir."""
    if inputs.dsl_path is None or inputs.dsl_text is None:
        return GateResult("dsl_written", False, "no .dsl file in the work dir")
    text = inputs.dsl_text
    if len(text.encode("utf-8")) < MIN_DSL_BYTES or WORKSPACE_KEYWORD not in text:
        return GateResult(
            "dsl_written",
            False,
            f"{inputs.dsl_path} is empty or carries no '{WORKSPACE_KEYWORD}' keyword",
        )
    return GateResult("dsl_written", True, f"{inputs.dsl_path} ({len(text)} bytes)")


def gate_cli_valid(inputs: GraderInputs) -> GateResult:
    """`cli_valid`: the real Structurizr CLI validates the workspace."""
    if inputs.validate_rc is None:
        return GateResult("cli_valid", False, "CLI validate could not run (no DSL file)")
    if inputs.validate_rc != 0:
        detail = inputs.validate_stderr.strip().splitlines()
        return GateResult("cli_valid", False, f"CLI validate rc={inputs.validate_rc}: {detail[-1] if detail else ''}")
    return GateResult("cli_valid", True, "CLI validate rc=0")


def gate_cli_export(inputs: GraderInputs) -> GateResult:
    """`cli_export`: the CLI exports the workspace to JSON."""
    if inputs.export_rc is None:
        return GateResult("cli_export", False, "CLI export could not run (no DSL file)")
    if inputs.export_rc != 0 or inputs.export_json is None:
        detail = inputs.export_stderr.strip().splitlines()
        return GateResult(
            "cli_export",
            False,
            f"CLI export rc={inputs.export_rc}: {detail[-1] if detail else 'no JSON produced'}",
        )
    return GateResult("cli_export", True, "CLI export rc=0")


def gate_has_system(inputs: GraderInputs) -> GateResult:
    """`has_system`: at least one software system with a name and description."""
    systems = iter_systems(inputs.export_json)
    if not systems:
        return GateResult("has_system", False, "no softwareSystem in the export JSON")
    named = [s for s in systems if str(s.get("name") or "").strip() and str(s.get("description") or "").strip()]
    if not named:
        return GateResult("has_system", False, "every softwareSystem lacks a name or description")
    return GateResult("has_system", True, f"{len(named)}/ {len(systems)} softwareSystem(s) named and described")


def gate_has_person(inputs: GraderInputs) -> GateResult:
    """`has_person`: at least one person with a description."""
    people = iter_people(inputs.export_json)
    if not people:
        return GateResult("has_person", False, "no person in the export JSON")
    described = [p for p in people if str(p.get("description") or "").strip()]
    if not described:
        return GateResult("has_person", False, "every person lacks a description")
    return GateResult("has_person", True, f"{len(described)}/{len(people)} person(s) described")


def gate_two_containers(inputs: GraderInputs) -> GateResult:
    """`two_containers`: at least two containers in the model."""
    containers = iter_containers(inputs.export_json)
    if len(containers) < 2:
        return GateResult("two_containers", False, f"only {len(containers)} container(s) in the export JSON")
    described = [c for c in containers if str(c.get("description") or "").strip()]
    if len(described) < 2:
        return GateResult(
            "two_containers",
            False,
            f"only {len(described)} of {len(containers)} containers carry a description",
        )
    return GateResult("two_containers", True, f"{len(containers)} container(s)")


def gate_relationship_technology(inputs: GraderInputs) -> GateResult:
    """`relationship_technology`: every relationship carries a technology."""
    rels = iter_relationships(inputs.export_json)
    if not rels:
        return GateResult("relationship_technology", False, "no relationships in the export JSON")
    coverage = relationship_technology_coverage(inputs.export_json)
    assert coverage is not None
    if coverage < 1.0:
        missing = [str(r.get("description") or r.get("id")) for r in rels if not str(r.get("technology") or "").strip()]
        return GateResult(
            "relationship_technology",
            False,
            f"technology on {coverage:.0%} of {len(rels)} relationship(s); missing: {missing}",
        )
    return GateResult("relationship_technology", True, f"technology on all {len(rels)} relationship(s)")


def gate_has_view(inputs: GraderInputs) -> GateResult:
    """`has_view`: at least one user-defined view in the model.

    The JSON exporter auto-generates empty views for every workspace
    (a container view per system, a system context view, a system
    landscape view) and marks them `generatedKey: true`; only a view the
    DSL itself defined counts.
    """
    views = iter_views(inputs.export_json)
    defined = [v for v in views if not v.get("generatedKey")]
    if not defined:
        return GateResult("has_view", False, "no user-defined views in the export JSON (only auto-generated)")
    return GateResult("has_view", True, f"{len(defined)} user-defined view(s)")


# ---------------------------------------------------------------------------
# the Phase 120 knowledge and anti-deletion gates (Task 120.100)
# ---------------------------------------------------------------------------


def _iter_all_elements(export_json: dict | None) -> list[tuple[str, dict]]:
    """Return every model element as (kind, element) pairs.

    Kinds: `person`, `system`, `external`, `container`, `custom` -- the
    same kind vocabulary `Case.seed_elements` uses.
    """
    result: list[tuple[str, dict]] = []
    for kind, elements in (
        ("person", iter_people(export_json)),
        ("system", iter_systems(export_json)),
        ("external", iter_external_systems(export_json)),
        ("custom", iter_custom_elements(export_json)),
    ):
        for element in elements:
            result.append((kind, element))
    for element in iter_containers(export_json):
        result.append(("container", element))
    return result


def gate_elements_described(inputs: GraderInputs) -> GateResult:
    """`elements_described`: every element carries a description.

    People, systems, external systems and containers carry a non-blank
    `description`; custom elements carry a non-blank `metadata` (their
    description field in the export). A model with no elements at all
    fails (there is nothing to be complete about).
    """
    missing: list[str] = []
    total = 0
    for kind, element in _iter_all_elements(inputs.export_json):
        total += 1
        value = element.get("metadata") if kind == "custom" else element.get("description")
        if not str(value or "").strip():
            missing.append(f"{kind} {str(element.get('name') or element.get('id'))!r}")
    if total == 0:
        return GateResult("elements_described", False, "no elements in the export JSON")
    if missing:
        return GateResult(
            "elements_described", False, f"{len(missing)} of {total} element(s) lack a description: {missing}"
        )
    return GateResult("elements_described", True, f"description on all {total} element(s)")


def gate_relationships_described(inputs: GraderInputs) -> GateResult:
    """`relationships_described`: every relationship carries a description.

    The description-coverage counterpart of `relationship_technology`:
    the DSL distinguishes same-pair relationships by description only, so
    a relationship without one is both incomplete and unidentifiable.
    """
    rels = iter_relationships(inputs.export_json)
    if not rels:
        return GateResult("relationships_described", False, "no relationships in the export JSON")
    missing = [str(r.get("description") or r.get("id")) for r in rels if not str(r.get("description") or "").strip()]
    if missing:
        return GateResult(
            "relationships_described",
            False,
            f"{len(missing)} of {len(rels)} relationship(s) lack a description: {missing}",
        )
    return GateResult("relationships_described", True, f"description on all {len(rels)} relationship(s)")


def gate_no_deletions(context: GateContext) -> GateResult:
    """`no_deletions`: every seeded element and relationship is still present.

    The anti-deletion gate of the fix-style cases (Phase 120): the prompt
    forbids removing any people, systems, containers or relationships, and
    `validate` cannot enforce that -- a workspace with a whole element
    deleted still parses. Elements are matched by name over the export
    JSON (`Case.seed_elements` kinds); relationships are matched by
    (source name, destination name, description) -- the description is the
    relationship's identity in the DSL, so rewording a seeded relationship
    removes it.
    """
    case = context.case
    if not case.seed_elements and not case.seed_relationships:
        return GateResult("no_deletions", False, "the case seeds no elements or relationships (gate misused)")
    export_json = context.inputs.export_json
    if export_json is None:
        return GateResult("no_deletions", False, "no export JSON to check against the seeded model")

    # name -> every element id with that name (containers are matched
    # across all systems; names may collide across kinds, so each kind
    # maps independently)
    ids_by_kind: dict[str, dict[str, set[str]]] = {}
    for kind, element in _iter_all_elements(export_json):
        name = str(element.get("name") or "").strip()
        elem_id = element.get("id")
        if name and elem_id is not None:
            ids_by_kind.setdefault(kind, {}).setdefault(name, set()).add(str(elem_id))

    missing_elements: list[str] = []
    for kind, name in case.seed_elements:
        if name not in ids_by_kind.get(kind, {}):
            missing_elements.append(f"{kind} {name!r}")

    source_ids: dict[str, set[str]] = {}
    for kind, names in ids_by_kind.items():
        for name, ids in names.items():
            source_ids.setdefault(name, set()).update(ids)

    def _ids_for(name: str) -> set[str]:
        return source_ids.get(name, set())

    rels = iter_relationships(export_json)
    missing_relationships: list[str] = []
    for source_name, destination_name, description in case.seed_relationships:
        source_ids_ = _ids_for(source_name)
        destination_ids_ = _ids_for(destination_name)
        present = any(
            str(r.get("sourceId")) in source_ids_
            and str(r.get("destinationId")) in destination_ids_
            and str(r.get("description") or "").strip() == description
            for r in rels
        )
        if not present:
            missing_relationships.append(f"{source_name!r} -> {destination_name!r} {description!r}")

    if missing_elements or missing_relationships:
        detail = "missing: " + ", ".join(missing_elements + missing_relationships)
        return GateResult(
            "no_deletions",
            False,
            f"{len(missing_elements)} element(s) and "
            f"{len(missing_relationships)} relationship(s) deleted or reworded; {detail}",
        )
    return GateResult(
        "no_deletions",
        True,
        f"all {len(case.seed_elements)} seeded element(s) and {len(case.seed_relationships)} "
        "seeded relationship(s) still present",
    )


# ---------------------------------------------------------------------------
# the Phase 130 modeling-decision gates (Task 130.100)
# ---------------------------------------------------------------------------

#: The forbidden vague relationship labels (locked, Task 130.100): a
#: relationship whose description equals one of these (case-insensitive,
#: trimmed) fails `no_vague_labels`. The set is a membership test, not a
#: substring test -- "user uses the portal to track parcels" is specific
#: and passes.
VAGUE_RELATIONSHIP_LABELS: frozenset[str] = frozenset(
    {"uses", "connects to", "interacts with", "talks to", "communicates with"}
)


def _element_tags(element: dict) -> list[str]:
    """Return one element's tags as a clean list.

    The pinned CLI's JSON exporter writes the `tags` property as a
    comma-separated string (e.g. `Element,Software System,External`); a
    list form is tolerated for fixture robustness.
    """
    raw = element.get("tags")
    if isinstance(raw, str):
        result = [t.strip() for t in raw.split(",") if t.strip()]
        return result
    if isinstance(raw, list):
        result = [str(t).strip() for t in raw if str(t).strip()]
        return result
    result = []
    return result


def gate_container_count(context: GateContext) -> GateResult:
    """`container_count`: the model carries exactly the scenario's containers.

    The scenario's container count is its two application parts plus its
    own database (a data store is a C4 container): `3`. The shared
    library is NO element, and the third-party service is top-level --
    either of them modeled as a container raises the count and fails this
    gate alongside the dedicated decision gates.
    """
    expected = context.case.expected_container_count
    if expected is None:
        return GateResult("container_count", False, "the case pins no expected container count (gate misused)")
    containers = iter_containers(context.inputs.export_json)
    if len(containers) != expected:
        names = [str(c.get("name") or c.get("id")) for c in containers]
        return GateResult("container_count", False, f"{len(containers)} container(s), expected {expected}: {names}")
    return GateResult("container_count", True, f"exactly {expected} container(s)")


def gate_no_library_container(context: GateContext) -> GateResult:
    """`no_library_container`: the scenario's shared library is no container or component.

    A negative-presence gate over the export JSON by name (locked, Task
    130.100): none of `Case.forbidden_element_names` (the scenario's
    shared library) may appear as a container of any system or a component
    of any container. C4 treats libraries, JARs, modules and packages as
    code-level constructs -- they run inside another element's process and
    are not modeled as their own element.
    """
    forbidden = context.case.forbidden_element_names
    if not forbidden:
        return GateResult("no_library_container", False, "the case forbids no element names (gate misused)")
    found: list[str] = []
    for kind, elements in (
        ("container", iter_containers(context.inputs.export_json)),
        ("component", iter_components(context.inputs.export_json)),
    ):
        for element in elements:
            name = str(element.get("name") or "").strip()
            if name in forbidden:
                found.append(f"{kind} {name!r}")
    if found:
        return GateResult(
            "no_library_container",
            False,
            "forbidden element(s) modeled as a container or component: " + ", ".join(sorted(found)),
        )
    return GateResult(
        "no_library_container",
        True,
        f"none of the {len(forbidden)} forbidden element name(s) appears as a container or component",
    )


def gate_external_system_tagged(inputs: GraderInputs) -> GateResult:
    """`external_system_tagged`: a top-level element carries the `External` tag.

    The third-party service of the scenario must be modeled as a TOP-LEVEL
    element -- a `softwareSystem` or a custom `element` outside the owned
    system -- carrying the `External` tag. The pinned DSL has no
    `externalSystem` keyword (verified in Phase 120), so the export JSON's
    `model.externalSystems` section is never populated by it and is never
    consulted here: a container of the owned system, or a top-level
    element without the tag, fails the gate.
    """
    top_level = iter_systems(inputs.export_json) + iter_custom_elements(inputs.export_json)
    tagged = [
        str(e.get("name") or e.get("id")) for e in top_level if any(t.lower() == "external" for t in _element_tags(e))
    ]
    if not tagged:
        return GateResult(
            "external_system_tagged",
            False,
            "no top-level softwareSystem or custom element carries the External tag",
        )
    return GateResult("external_system_tagged", True, f"top-level element(s) with the External tag: {tagged}")


def gate_no_vague_labels(inputs: GraderInputs) -> GateResult:
    """`no_vague_labels`: no relationship carries a forbidden vague label.

    Every relationship's description (trimmed, case-insensitive) must not
    be a member of :data:`VAGUE_RELATIONSHIP_LABELS` -- a label that states
    no intent ("uses" says nothing about what happens in that direction).
    A model with no relationships fails (the scenario has some).
    """
    rels = iter_relationships(inputs.export_json)
    if not rels:
        return GateResult("no_vague_labels", False, "no relationships in the export JSON")
    vague = [
        str(r.get("description") or r.get("id"))
        for r in rels
        if str(r.get("description") or "").strip().lower() in VAGUE_RELATIONSHIP_LABELS
    ]
    if vague:
        return GateResult("no_vague_labels", False, f"{len(vague)} vague relationship label(s): {vague}")
    return GateResult("no_vague_labels", True, f"no vague label on any of the {len(rels)} relationship(s)")


# ---------------------------------------------------------------------------
# the Phase 140 view-design gates (Task 140.100)
# ---------------------------------------------------------------------------

#: The practical upper bound on the elements one view may carry (locked,
#: Task 140.100): the spike's Finding 8 -- the 150-element view exported a
#: 29,664-pixel-wide SVG that was unusable as a diagram; "about 20 elements
#: per view".
VIEW_ELEMENT_BOUND = 20


def iter_user_defined_views(export_json: dict | None) -> list[dict]:
    """Return the views the DSL itself defined (`generatedKey` filtered out).

    The `has_view` precedent: the JSON exporter auto-generates default
    views (one container view per system, a system context view, a system
    landscape view) marked `generatedKey: true` when the DSL defines no
    views at all, and it marks a view the DSL defined with an omitted key
    `generatedKey: true` too (giving it an auto-generated `<Kind>-NNN`
    key, e.g. `Container-001` -- verified against the pinned CLI, Task
    140.100). Either way, only a view the DSL defined WITH its key
    explicit counts as user-defined here.
    """
    result = [v for v in iter_views(export_json) if not v.get("generatedKey")]
    return result


def _view_element_count(view: dict, all_views: list[dict], seen: set[str] | None = None) -> int:
    """Return the number of elements one view renders (over the export JSON).

    The pinned exporter's element-scoping fact (verified against the
    pinned CLI, Task 140.100): a regular view's `elements` array is the
    view's `include` result -- for a container view with `include *`, the
    scoped system's containers plus every element linked to them (people,
    other software systems, custom elements); the scoped software system
    itself is NOT in the list (the view references it by its own
    `softwareSystemId`), and linked relationship copies are relationships,
    not elements. An explicit include list carries exactly the listed
    elements. A filtered view has no `elements` array of its own (the
    exporter writes its `baseViewKey`, `mode` and `tags` instead); it
    renders a subset of its base view, so it is bounded by the base's
    count, resolved by key (recursively, cycle-guarded).
    """
    elements = view.get("elements")
    if isinstance(elements, list):
        result = len(elements)
        return result
    if seen is None:
        seen = set()
    key = str(view.get("key") or "")
    if key in seen:
        result = 0
        return result
    seen.add(key)
    base_key = view.get("baseViewKey")
    for other in all_views:
        if other.get("key") == base_key:
            result = _view_element_count(other, all_views, seen)
            return result
    result = 0
    return result


def gate_views_within_element_bound(inputs: GraderInputs) -> GateResult:
    """`views_within_element_bound`: every user-defined view carries at most 20 elements.

    The locked view-size rule of the `c4-view-design` skill (the spike's
    practical bound, `VIEW_ELEMENT_BOUND`): a single `include *` view of a
    larger model is not a readable diagram. Counts every user-defined
    view's rendered element count over the export JSON (the `elements`
    array; a filtered view bounded by its base's count -- see
    `_view_element_count`); a view with more than the bound fails the
    gate. Vacuously true without user-defined views (`has_view` carries
    the presence requirement).
    """
    views = iter_user_defined_views(inputs.export_json)
    if not views:
        return GateResult(
            "views_within_element_bound", True, "no user-defined views to check (vacuously within the bound)"
        )
    all_views = iter_views(inputs.export_json)
    over: list[str] = []
    for view in views:
        count = _view_element_count(view, all_views)
        if count > VIEW_ELEMENT_BOUND:
            over.append(f"{view.get('key')!r} with {count} element(s)")
    if over:
        return GateResult(
            "views_within_element_bound",
            False,
            f"{len(over)} of {len(views)} user-defined view(s) over {VIEW_ELEMENT_BOUND} element(s): "
            + "; ".join(over),
        )
    return GateResult(
        "views_within_element_bound",
        True,
        f"every one of {len(views)} user-defined view(s) carries at most {VIEW_ELEMENT_BOUND} element(s)",
    )


def gate_explicit_view_keys(inputs: GraderInputs) -> GateResult:
    """`explicit_view_keys`: every view the workspace carries has an explicit key.

    The locked explicit-key rule of the `c4-view-design` skill: a view
    whose DSL omitted the key is exported under an auto-generated
    `<Kind>-NNN` key (e.g. `Container-001`) with `generatedKey: true` --
    not guaranteed to be stable over time, and the pinned CLI's `inspect`
    reports it as a `views.view.key` finding (verified against the pinned
    CLI, Task 140.100). The gate is over the export JSON: every view must
    exist, and none may carry the `generatedKey` mark. A workspace whose
    DSL defines no views at all exports only auto-generated default
    views and fails here as well (`has_view` fails it too).
    """
    views = iter_views(inputs.export_json)
    if not views:
        return GateResult("explicit_view_keys", False, "no views at all in the export JSON")
    generated = [str(v.get("key") or "?") for v in views if v.get("generatedKey")]
    if generated:
        return GateResult(
            "explicit_view_keys",
            False,
            f"{len(generated)} of {len(views)} view(s) carry an auto-generated key (the DSL omitted it): {generated}",
        )
    return GateResult("explicit_view_keys", True, f"every one of {len(views)} view(s) has an explicit key")


# ---------------------------------------------------------------------------
# the stream-derived gates (Phase 110, Task 110.100)
# ---------------------------------------------------------------------------


def gate_validated_before_return(context: GateContext) -> GateResult:
    """`validated_before_return`: the returned DSL is the exact text that got OK.

    Reuses `TrialMetrics.validated_before_return` (the on-disk file or the
    final message text is byte-identical to the `dsl` input of a
    `validate`-suffixed call that answered the OK marker); a parsed-only or
    reported-only result is NOT a pass (the ADR 7a626b12 precedent).
    """
    from .metrics import validated_texts  # local: metrics imports graders (cycle)

    ok_texts = validated_texts(context.trial)
    if context.metrics.validated_before_return:
        via = "the on-disk file" if context.metrics.validated_by_file else "the final message text"
        return GateResult(
            "validated_before_return", True, f"returned DSL is byte-identical to the validated OK text ({via})"
        )
    if not ok_texts:
        return GateResult("validated_before_return", False, "no validate call answered the OK marker with a dsl input")
    sub = []
    if not context.metrics.validated_by_file:
        sub.append("on-disk file differs")
    if not context.metrics.validated_by_final_text:
        sub.append("final message text differs or is absent")
    return GateResult("validated_before_return", False, f"{len(ok_texts)} validated OK text(s); " + " and ".join(sub))


def gate_parse_called(context: GateContext) -> GateResult:
    """`parse_called`: at least one terminal call to a `parse`-suffixed MCP tool."""
    if context.metrics.parse_calls < 1:
        return GateResult("parse_called", False, "no terminal parse call in the event stream")
    return GateResult("parse_called", True, f"{context.metrics.parse_calls} terminal parse call(s)")


def gate_validate_ok_called(context: GateContext) -> GateResult:
    """`validate_ok_called`: at least one `validate` call answered the OK marker."""
    if context.metrics.validate_ok_calls < 1:
        total = context.metrics.validate_calls
        return GateResult(
            "validate_ok_called", False, f"no validate call answered the OK marker ({total} validate call(s) in total)"
        )
    return GateResult("validate_ok_called", True, f"{context.metrics.validate_ok_calls} validate call(s) answered OK")


def gate_inspect_called(context: GateContext) -> GateResult:
    """`inspect_called`: at least one terminal call to an `inspect`-suffixed MCP tool."""
    if context.metrics.inspect_calls < 1:
        return GateResult("inspect_called", False, "no terminal inspect call in the event stream")
    return GateResult("inspect_called", True, f"{context.metrics.inspect_calls} terminal inspect call(s)")


def gate_triage_complete(context: GateContext) -> GateResult:
    """`triage_complete`: every merged `inspect` finding is triaged (REQ-003).

    Every finding in `metrics.inspect_triage` (the stream and CLI findings
    merged on the normalized finding text, first-occurrence order) carries
    a `fix`/`expected`/`reported` label -- no `untriaged`. Vacuously true
    with no findings; `inspect_called` carries the requirement that
    inspect was used at all. The gate itself is unchanged by Task
    125.100/G2 -- what changed is which labels the metrics layer
    assigns: a `fix` now needs a post-inspect edit AND the finding's
    absence from the final CLI `inspect` findings (the truth anchor).
    """
    from .metrics import TRIAGE_UNTRIAGED  # local: metrics imports graders (cycle)

    triage = context.metrics.inspect_triage
    if not triage:
        return GateResult("triage_complete", True, "no inspect findings (vacuously complete)")
    untriaged = [finding for finding, label in triage.items() if label == TRIAGE_UNTRIAGED]
    if untriaged:
        return GateResult(
            "triage_complete", False, f"{len(untriaged)} of {len(triage)} finding(s) untriaged: {untriaged[0]}"
        )
    return GateResult("triage_complete", True, f"all {len(triage)} finding(s) labeled fix/expected/reported")


#: Loose matcher for `limits_acknowledged`: the final text names at least
#: one of the MCP-refused features (`!include` / `!docs`); backticks and
#: casing aside, an optional space after the `!` is tolerated.
_LIMITS_FEATURE_RE = re.compile(r"!\s*(include|docs)\b", re.IGNORECASE)


def gate_limits_acknowledged(context: GateContext) -> GateResult:
    """`limits_acknowledged`: the final text names the MCP-refused features.

    Loose by design (the locked spec): naming `!include` and/or `!docs`
    anywhere in the final message suffices.
    """
    final_text = context.trial.final_text()
    named = sorted({match.group(1).lower() for match in _LIMITS_FEATURE_RE.finditer(final_text)})
    if not named:
        return GateResult("limits_acknowledged", False, "final text names neither !include nor !docs")
    return GateResult("limits_acknowledged", True, "final text names: " + ", ".join(f"!{name}" for name in named))


def gate_no_mounted_skill_loaded(context: GateContext) -> GateResult:
    """`no_mounted_skill_loaded`: the agent loaded none of the mounted skills.

    `metrics.skills_loaded` (the `skill` tool calls) intersected with
    `skills_installed` (what the condition put into the work dir before the
    agent started) must be empty; vacuously true for `none` (nothing
    installed).
    """
    loaded = set(context.metrics.skills_loaded)
    installed = set(context.skills_installed)
    triggered = sorted(loaded & installed)
    if triggered:
        return GateResult("no_mounted_skill_loaded", False, f"mounted skill(s) loaded: {', '.join(triggered)}")
    if not installed:
        return GateResult("no_mounted_skill_loaded", True, "no skills mounted (vacuously true)")
    return GateResult(
        "no_mounted_skill_loaded",
        True,
        f"no mounted skill loaded ({len(installed)} mounted: {', '.join(sorted(installed))})",
    )


def gate_file_untouched(context: GateContext) -> GateResult:
    """`file_untouched`: the DSL file on disk is the case's seeded file.

    Compares `inputs.dsl_text` against the `Case.setup_files` entry for the
    same relative path: the seeded file was neither modified, removed nor
    replaced by another .dsl file.
    """
    seeded = context.case.setup_files
    if not seeded:
        return GateResult("file_untouched", False, "the case seeds no files (gate misused)")
    dsl_path = context.inputs.dsl_path
    if dsl_path is None:
        return GateResult(
            "file_untouched", False, f"no .dsl file in the work dir (the seeded {sorted(seeded)} is gone)"
        )
    expected = seeded.get(dsl_path)
    if expected is None:
        return GateResult(
            "file_untouched", False, f"{dsl_path} is not the seeded file {sorted(seeded)} (replaced or renamed)"
        )
    if context.inputs.dsl_text is None or context.inputs.dsl_text != expected:
        return GateResult("file_untouched", False, f"{dsl_path} was modified (differs from the seeded text)")
    return GateResult("file_untouched", True, f"{dsl_path} is byte-identical to the seeded file")


#: Loose matchers for `mcp_limit_stated`: the final text states that images
#: cannot be produced (the MCP has no image rendering; its export tools
#: emit PlantUML/C4-PlantUML/Mermaid *source*). Any one pattern matching is
#: enough, and additional sentences (e.g. offering the diagram source)
#: never break a match.
_IMAGE_LIMIT_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "cannot / can't / ... render/produce/generate/create/export ... image/png/svg"
    re.compile(
        r"\b(can(?:not|'t)|could\s+not|unable\s+to|impossible\s+to|no\s+way\s+to)\b"
        r"[^.\n]{0,60}?\b(render\w*|produc\w+|generat\w+|creat\w+|export\w*|make\w*)\b"
        r"[^.\n]{0,40}?\b(image\w*|png|svg|picture\w*)\b",
        re.IGNORECASE,
    ),
    # "image/png/svg rendering/export ... is not / no"
    re.compile(
        r"\b(image\w*|png|svg)\s+(render\w+|produc\w+|export\w*)\b[^.\n]{0,40}?\b(not|no|impossible|unsupported)\b",
        re.IGNORECASE,
    ),
    # "no / without / not ... image rendering"
    re.compile(
        r"\b(not|no|without)\b[^.\n]{0,30}?\b(image\w*|png|svg)\s+(render\w+|produc\w+|export\w*)\b",
        re.IGNORECASE,
    ),
    # "does not / doesn't / do not / don't support/allow/render/... image ..."
    re.compile(
        r"\b(does\s+not|doesn't|do\s+not|don't)\b[^.\n]{0,40}?\b(support\w*|provide\w*|allow\w*|produce\w*|render\w*|generat\w+|export\w*)\b"
        r"[^.\n]{0,40}?\b(image\w*|png|svg|render\w+)\b",
        re.IGNORECASE,
    ),
    # "rendering/producing/generating ... images ... is/are not ..."
    re.compile(
        r"\b(render\w+|produc\w+|generat\w+|creat\w+|export\w+)\b[^.\n]{0,40}?\b(image\w*|png|svg)\b"
        r"[^.\n]{0,40}?\b(is|are)\s+(not|no|impossible|unsupported)\b",
        re.IGNORECASE,
    ),
)


def _states_image_limitation(text: str) -> bool:
    """Return True iff `text` states that images cannot be produced."""
    assert isinstance(text, str)
    for pattern in _IMAGE_LIMIT_PATTERNS:
        if pattern.search(text):
            return True
    result = False
    return result


def gate_mcp_limit_stated(context: GateContext) -> GateResult:
    """`mcp_limit_stated`: the final text states the no-image-rendering limit.

    The MCP has no image rendering (its export tools emit PlantUML/
    C4-PlantUML/Mermaid source); a final message that only offers diagram
    source without stating the limit fails.
    """
    final_text = context.trial.final_text()
    if _states_image_limitation(final_text):
        return GateResult("mcp_limit_stated", True, "final text states that images cannot be produced")
    return GateResult("mcp_limit_stated", False, "final text does not state that the MCP cannot produce images")


# ---------------------------------------------------------------------------
# the gate registry (name -> gate over the full context)
# ---------------------------------------------------------------------------


def _inputs_only(gate: Callable[[GraderInputs], GateResult]) -> Callable[[GateContext], GateResult]:
    """Wrap one of the original input-based gates over `GateContext.inputs`."""

    def wrapped(context: GateContext) -> GateResult:
        result = gate(context.inputs)
        return result

    return wrapped


#: Every gate function, keyed by gate name (the cases' `gates` entries).
#: The original 8 CLI/export gates are the input-only functions wrapped
#: over `GateContext.inputs`; the Phase 120 `elements_described`/
#: `relationships_described` gates are input-only too; the Phase 130
#: `external_system_tagged`/`no_vague_labels` gates are input-only too;
#: the Phase 140 `views_within_element_bound`/`explicit_view_keys` gates
#: are input-only too; the Phase 110 stream gates and the Phase 120
#: `no_deletions` gate and the Phase 130 `container_count`/
#: `no_library_container` gates (which read the case's own scenario
#: facts) take the context.
GATES: dict[str, Callable[[GateContext], GateResult]] = {
    "dsl_written": _inputs_only(gate_dsl_written),
    "cli_valid": _inputs_only(gate_cli_valid),
    "cli_export": _inputs_only(gate_cli_export),
    "has_system": _inputs_only(gate_has_system),
    "has_person": _inputs_only(gate_has_person),
    "two_containers": _inputs_only(gate_two_containers),
    "relationship_technology": _inputs_only(gate_relationship_technology),
    "has_view": _inputs_only(gate_has_view),
    "elements_described": _inputs_only(gate_elements_described),
    "relationships_described": _inputs_only(gate_relationships_described),
    "no_deletions": gate_no_deletions,
    "container_count": gate_container_count,
    "no_library_container": gate_no_library_container,
    "external_system_tagged": _inputs_only(gate_external_system_tagged),
    "no_vague_labels": _inputs_only(gate_no_vague_labels),
    "views_within_element_bound": _inputs_only(gate_views_within_element_bound),
    "explicit_view_keys": _inputs_only(gate_explicit_view_keys),
    "validated_before_return": gate_validated_before_return,
    "parse_called": gate_parse_called,
    "validate_ok_called": gate_validate_ok_called,
    "inspect_called": gate_inspect_called,
    "triage_complete": gate_triage_complete,
    "limits_acknowledged": gate_limits_acknowledged,
    "no_mounted_skill_loaded": gate_no_mounted_skill_loaded,
    "file_untouched": gate_file_untouched,
    "mcp_limit_stated": gate_mcp_limit_stated,
}


def grade_case(context: GateContext) -> list[GateResult]:
    """Evaluate every gate of `context.case` over the trial context (pure).

    Args:
        context: The GateContext (case + collected inputs + parsed event
            stream + computed metrics + installed skill names).

    Returns:
        One GateResult per gate, in the case's order.

    Raises:
        KeyError: On an unknown gate name.
    """
    assert isinstance(context, GateContext)
    results: list[GateResult] = []
    for name in context.case.gates:
        gate = GATES[name]
        results.append(gate(context))
    return results


def case_passed(results: list[GateResult]) -> bool:
    """Return True iff every gate of the case passed."""
    assert isinstance(results, list)
    result = all(r.passed for r in results)
    return result


# ---------------------------------------------------------------------------
# the Docker-dependent collection (the real Structurizr CLI)
# ---------------------------------------------------------------------------

#: The CLI subcommands the graders run against the work dir.
CLI_VALIDATE_CMD = ("validate",)
CLI_EXPORT_CMD = ("export",)
CLI_INSPECT_CMD = ("inspect",)

#: The per-command timeout of the grader's CLI runs. A
#: `subprocess.TimeoutExpired` is mapped to `RuntimeError` (Task
#: 125.130/I3): a hung docker CLI is a runtime-shaped failure, so the
#: documented CLI exit-code contract (`cli.py`'s module docstring, the
#: harness README) carries it as exit 1 instead of a raw traceback
#: mid-run.
CLI_TIMEOUT_S = 300


def find_dsl_file(workdir: Path) -> Path | None:
    """Return the trial's workspace DSL file, or None.

    Preference: ``workspace.dsl`` (the case prompt names it), then any
    other ``*.dsl`` file at the work dir root, then none.
    """
    assert workdir.is_dir()
    preferred = workdir / "workspace.dsl"
    if preferred.is_file() and preferred.stat().st_size > 0:
        return preferred
    candidates = sorted(p for p in workdir.glob("*.dsl") if p.is_file() and p.stat().st_size > 0)
    result: Path | None = candidates[0] if candidates else None
    return result


def _run_cli(workdir: Path, args: list[str]) -> tuple[int, str]:
    """Run one Structurizr CLI command over the work dir (Docker).

    The CLI container runs with `--network none`: it only reads the
    mounted work dir and writes `out/`, so it needs no network at all
    (verified in the Phase 110 canaries -- the graders never needed
    egress, and the flag removes the last container class that could
    reach the host network).

    Returns:
        The exit code and the combined stderr/stdout text.

    Raises:
        RuntimeError: If the CLI run exceeds the ``CLI_TIMEOUT_S``
            timeout (Task 125.130/I3 -- the documented CLI exit-code
            contract's runtime-shaped failure, exit 1).
    """
    assert workdir.is_dir()
    cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        *preflight.host_user_flags(),
        "-v",
        f"{workdir}:/w",
        "-w",
        "/w",
        pins.STRUCTURIZR_CLI_IMAGE,
        *args,
    ]
    try:
        proc = subprocess.run(  # noqa: S603 -- fixed pinned image, no user input
            cmd,
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        command = " ".join(cmd)
        raise RuntimeError(f"the Structurizr CLI run timed out after {CLI_TIMEOUT_S} s: {command}") from exc
    result: tuple[int, str] = (proc.returncode, (proc.stderr or "") + (proc.stdout or ""))
    return result


def parse_inspect_findings(inspect_out: str) -> list[str]:
    """Return the finding lines one CLI `inspect` output text carries.

    The pure half of `collect_inputs`'s inspect step (extracted for the
    Phase 125 fixture pattern, Task 125.100/110/120): a
    `LEVEL | key | message` line contributes its bare `message` (the
    pipe form the pinned CLI prints for a workspace it inspected); a
    `LEVEL ...` line without a pipe contributes the whole line. Every
    other line (timestamps, the error lines of a workspace the CLI
    cannot even inspect, e.g. a missing `!include` target) contributes
    nothing.
    """
    findings: list[str] = []
    for line in inspect_out.splitlines():
        stripped = line.strip()
        if stripped.startswith(("ERROR", "WARNING", "INFO", "IGNORE")) and "|" in stripped:
            findings.append(stripped.split("|", 2)[-1].strip())
        elif stripped.startswith(("ERROR", "WARNING")):
            findings.append(stripped)
    result = findings
    return result


def collect_inputs(workdir: Path) -> GraderInputs:
    """Collect the grader inputs for one trial work dir (Docker-dependent).

    Runs the pinned Structurizr CLI image three times (validate, export,
    inspect). A missing DSL file short-circuits to the corresponding None
    fields (the gates then fail with an explicit detail).

    Args:
        workdir: The trial work dir (mounted read-only into the CLI).

    Returns:
        The GraderInputs for the pure gates.
    """
    assert workdir.is_dir()
    dsl = find_dsl_file(workdir)
    if dsl is None:
        empty = GraderInputs(
            dsl_path=None,
            dsl_text=None,
            validate_rc=None,
            validate_stderr="no .dsl file in the work dir",
            export_json=None,
            export_rc=None,
            export_stderr="no .dsl file in the work dir",
            inspect_rc=None,
            inspect_findings=[],
        )
        return empty
    dsl_text = dsl.read_text(encoding="utf-8", errors="replace")
    validate_rc, validate_out = _run_cli(workdir, [*CLI_VALIDATE_CMD, "-w", dsl.name])
    export_rc, export_out = _run_cli(workdir, [*CLI_EXPORT_CMD, "-w", dsl.name, "-f", "json", "-o", "/w/out"])
    inspect_rc, inspect_out = _run_cli(workdir, [*CLI_INSPECT_CMD, "-w", dsl.name])

    export_json: dict | None = None
    export_file = workdir / "out" / f"{dsl.stem}.json"
    if export_rc == 0 and export_file.is_file():
        try:
            loaded = json.loads(export_file.read_text(encoding="utf-8"))
            export_json = loaded if isinstance(loaded, dict) else None
        except json.JSONDecodeError:
            export_json = None

    findings = parse_inspect_findings(inspect_out)

    result = GraderInputs(
        dsl_path=dsl.name,
        dsl_text=dsl_text,
        validate_rc=validate_rc,
        validate_stderr=validate_out,
        export_json=export_json,
        export_rc=export_rc,
        export_stderr=export_out,
        inspect_rc=inspect_rc,
        inspect_findings=findings,
    )
    return result
