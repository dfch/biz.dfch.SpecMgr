"""Query a Structurizr JSON export against the property conventions of the Architecture Model TXT 30983f27, section 8.

Probe script of Task 120.110 (issue 267). Python standard library only. It reports, it never fails on
findings: the exit code is 0 for a readable workspace and 2 for a usage or read error.

Usage: python3 query.py <workspace.json>
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

ORIGINS = {"Extracted", "Inferred", "Proposed"}
DOMAIN_LEVELS = ("host", "zone", "region")
VOCABULARY_KEYS = (
    "trust.boundary",
    "trust.level",
    "failure.domain.host",
    "failure.domain.zone",
    "failure.domain.region",
)
CRITERION_ID = re.compile(r"^(VP0[1-7]|XV)-[A-Z]{2}-\d{3}$")
PLACEMENT_VALUES = {"fixed", "scheduler"}


def walk_model(model: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any], list[dict[str, Any]]]]:
    """Yield (kind, element, ancestors) for every element of the static and the deployment model."""
    for person in model.get("people", []):
        yield "person", person, []
    for system in model.get("softwareSystems", []):
        yield "softwareSystem", system, []
        for container in system.get("containers", []):
            yield "container", container, [system]
            for component in container.get("components", []):
                yield "component", component, [system, container]

    def walk_node(
        node: dict[str, Any], ancestors: list[dict[str, Any]]
    ) -> Iterator[tuple[str, dict[str, Any], list[dict[str, Any]]]]:
        yield "deploymentNode", node, ancestors
        chain = [*ancestors, node]
        for child in node.get("children", []):
            yield from walk_node(child, chain)
        for infra in node.get("infrastructureNodes", []):
            yield "infrastructureNode", infra, chain
        for instance in node.get("containerInstances", []):
            yield "containerInstance", instance, chain
        for instance in node.get("softwareSystemInstances", []):
            yield "softwareSystemInstance", instance, chain

    for node in model.get("deploymentNodes", []):
        yield from walk_node(node, [])


def props(element: dict[str, Any]) -> dict[str, str]:
    """Return the user properties of an element, without the DSL identifier."""
    result = {k: v for k, v in element.get("properties", {}).items() if not k.startswith("structurizr.")}
    return result


def effective(key: str, element: dict[str, Any], ancestors: list[dict[str, Any]]) -> str | None:
    """Derive a property from the element or its nearest ancestor. The JSON export has no inheritance."""
    result = None
    for item in [*ancestors, element]:
        if key in props(item):
            result = props(item)[key]
    return result


def main(argv: list[str]) -> int:
    """Run all checks and print the report."""
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        workspace = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: cannot read {argv[1]}: {error}")
        return 2

    model = workspace.get("model", {})
    elements = list(walk_model(model))
    by_id = {e["id"]: (kind, e, anc) for kind, e, anc in elements}
    relationships = [r for _, e, _ in elements for r in e.get("relationships", [])]
    findings: list[str] = []

    def name(element_id: str) -> str:
        kind, element, ancestors = by_id[element_id]
        return "/".join([a.get("name", "?") for a in ancestors] + [element.get("name", kind)])

    # 1. origin and provenance on every element and explicit relationship
    for kind, element, _ in elements:
        if kind in ("containerInstance", "softwareSystemInstance"):
            continue
        p = props(element)
        if "origin" not in p or "provenance" not in p:
            findings.append(f"provenance: {kind} {name(element['id'])} lacks origin or provenance")
        elif p["origin"] not in ORIGINS:
            findings.append(f"provenance: {kind} {name(element['id'])} has origin '{p['origin']}'")
    for rel in relationships:
        if rel.get("linkedRelationshipId") or "origin" in props(rel):
            continue
        findings.append(
            f"provenance: relationship {name(rel['sourceId'])} -> {name(rel['destinationId'])} lacks origin"
        )

    # 2. failure domains of container instances (derived, no inheritance in JSON)
    print("== Failure domains of container instances")
    domains: dict[tuple[str, str], list[str]] = defaultdict(list)
    for kind, element, ancestors in elements:
        if kind != "containerInstance":
            continue
        placement = effective("failure.domain.placement", element, ancestors)
        replicas = int(ancestors[-1].get("instances", "1")) if ancestors else 1
        row = {lvl: effective(f"failure.domain.{lvl}", element, ancestors) for lvl in DOMAIN_LEVELS}
        container = by_id[element["containerId"]][1]["name"]
        print(
            f"  {container}: replicas={replicas} placement={placement or 'unset'} "
            + " ".join(f"{k}={v or 'unset'}" for k, v in row.items())
        )
        if placement not in (None, *PLACEMENT_VALUES):
            findings.append(f"failure domain: {container} has placement '{placement}'")
        if placement == "scheduler" and row["host"]:
            findings.append(f"failure domain: {container} is placed by the scheduler but sets a host")
        if replicas == 1:
            findings.append(f"failure domain: {container} has one instance and no replica (VP06-RE-100)")
        for lvl in DOMAIN_LEVELS:
            if row[lvl]:
                domains[(lvl, row[lvl])].append(container)
    for (lvl, value), members in sorted(domains.items()):
        if len(set(members)) > 1:
            print(f"  shared {lvl} '{value}': {', '.join(sorted(set(members)))}")

    # 3. parent and child conflicts for the same key
    for kind, element, ancestors in elements:
        for key, value in props(element).items():
            for ancestor in ancestors:
                if key in props(ancestor) and props(ancestor)[key] != value and key.startswith("failure.domain."):
                    outer = f"'{props(ancestor)[key]}' on {ancestor.get('name')}"
                    findings.append(f"conflict: {key} is {outer} and '{value}' on {element.get('name')}")

    # 4. vocabulary values that occur once (possible typos)
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for _, element, _ in elements:
        for key in VOCABULARY_KEYS:
            if key in props(element):
                counts[key][props(element)[key]] += 1
    print("== Vocabulary")
    for key, values in sorted(counts.items()):
        print(f"  {key}: " + ", ".join(f"{v} ({n})" for v, n in sorted(values.items())))

    # 5. trust boundaries: groups never carry them, crossings are derived from the instances and compared
    print("== Trust boundaries")
    for kind, element, _ in elements:
        if (
            element.get("group")
            and "trust.boundary" in props(element)
            and element["group"] != props(element)["trust.boundary"]
        ):
            boundary = props(element)["trust.boundary"]
            findings.append(
                f"trust: {name(element['id'])} is in group '{element['group']}' but trust.boundary is '{boundary}'"
            )
    boundaries: dict[str, set[str]] = defaultdict(set)
    for kind, element, ancestors in elements:
        if kind == "containerInstance":
            value = effective("trust.boundary", element, ancestors)
            if value:
                boundaries[element["containerId"]].add(value)
        elif kind in ("person", "softwareSystem", "container", "component") and "trust.boundary" in props(element):
            boundaries[element["id"]].add(props(element)["trust.boundary"])

    def boundary_of(element_id: str) -> set[str]:
        kind, element, ancestors = by_id[element_id]
        result = set(boundaries.get(element_id, set()))
        if not result and kind == "component":
            result = set(boundaries.get(ancestors[-1]["id"], set()))
        return result

    for rel in relationships:
        if rel.get("linkedRelationshipId"):
            continue
        src, dst = boundary_of(rel["sourceId"]), boundary_of(rel["destinationId"])
        stated = props(rel).get("trust.boundary.crossing") == "yes"
        label = f"{name(rel['sourceId'])} -> {name(rel['destinationId'])}"
        if not src or not dst:
            if stated:
                print(f"  trust: {label} stated as crossing; boundary not derivable (an end has no trust.boundary)")
            continue
        derived = src != dst
        if derived != stated:
            findings.append(
                f"trust: {label} derived crossing={derived} ({sorted(src)} vs {sorted(dst)}), stated={stated}"
            )

    # 6. safety functions: elements and relationships per function, gaps in the chain
    print("== Safety functions")
    functions: dict[str, list[str]] = defaultdict(list)
    for _, element, _ in elements:
        if "safety.function" in props(element):
            functions[props(element)["safety.function"]].append(name(element["id"]))
    for rel in relationships:
        function = props(rel).get("safety.function")
        if function:
            for end in (rel["sourceId"], rel["destinationId"]):
                if props(by_id[end][1]).get("safety.function") != function:
                    findings.append(f"safety: relationship of {function} touches {name(end)}, which is not part of it")
    for function, members in sorted(functions.items()):
        print(f"  {function}: {', '.join(members)}")
        if len(members) < 2:
            findings.append(f"safety: {function} has only one element")

    # 7. perspectives: one per criterion, rating on the top node or software system, others are evidence
    print("== Review results (perspectives)")
    results: dict[str, list[tuple[str, str, bool]]] = defaultdict(list)
    for kind, element, ancestors in elements:
        for perspective in element.get("perspectives", []):
            criterion = perspective.get("name", "")
            if not CRITERION_ID.match(criterion):
                findings.append(f"perspective: '{criterion}' on {name(element['id'])} is not a criterion ID")
            is_rating = (kind == "deploymentNode" and not ancestors) or kind == "softwareSystem"
            results[criterion].append((name(element["id"]), perspective.get("value", ""), is_rating))
    for criterion, rows in sorted(results.items()):
        ratings = [r for r in rows if r[2]]
        print(
            f"  {criterion}: rating "
            + (", ".join(f"{v} on {n}" for n, v, _ in ratings) or "none")
            + f"; evidence {len(rows) - len(ratings)}"
        )
        if not ratings:
            findings.append(f"perspective: {criterion} has evidence but no rating on a top node or software system")

    # 8. views record their viewpoint
    for collection in (
        "systemLandscapeViews",
        "systemContextViews",
        "containerViews",
        "componentViews",
        "deploymentViews",
        "dynamicViews",
    ):
        for view in workspace.get("views", {}).get(collection, []):
            if not view.get("properties", {}).get("viewpoint"):
                findings.append(f"view: {view.get('key')} has no viewpoint property")

    print(f"== Findings ({len(findings)})")
    for finding in findings:
        print(f"  {finding}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
