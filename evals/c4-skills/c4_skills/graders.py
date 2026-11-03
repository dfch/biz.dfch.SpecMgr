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

The split is: :func:`collect_inputs` (Docker-dependent, one real CLI run per
command) and :func:`grade_case` (pure, unit-tested).
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import pins, preflight
from .cases import MIN_DSL_BYTES, Case, WORKSPACE_KEYWORD

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


def iter_containers(export_json: dict | None) -> list[dict]:
    """Return every container element (inside software systems)."""
    result: list[dict] = []
    for system in iter_systems(export_json):
        for e in system.get("containers") or []:
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


#: The pure gate functions, keyed by gate name (the case's `gates` entries).
GATES: dict[str, object] = {
    "dsl_written": gate_dsl_written,
    "cli_valid": gate_cli_valid,
    "cli_export": gate_cli_export,
    "has_system": gate_has_system,
    "has_person": gate_has_person,
    "two_containers": gate_two_containers,
    "relationship_technology": gate_relationship_technology,
    "has_view": gate_has_view,
}


def grade_case(case: Case, inputs: GraderInputs) -> list[GateResult]:
    """Evaluate every gate of `case` over the collected inputs (pure).

    Args:
        case: The case whose `gates` are evaluated, in order.
        inputs: The collected CLI/work-dir inputs.

    Returns:
        One GateResult per gate, in the case's order.

    Raises:
        KeyError: On an unknown gate name.
    """
    assert isinstance(case, Case)
    results: list[GateResult] = []
    for name in case.gates:
        gate = GATES[name]
        assert callable(gate), name
        results.append(gate(inputs))  # type: ignore[operator]
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

    Returns:
        The exit code and the combined stderr/stdout text.
    """
    assert workdir.is_dir()
    cmd = [
        "docker",
        "run",
        "--rm",
        *preflight.host_user_flags(),
        "-v",
        f"{workdir}:/w",
        "-w",
        "/w",
        pins.STRUCTURIZR_CLI_IMAGE,
        *args,
    ]
    proc = subprocess.run(  # noqa: S603 -- fixed pinned image, no user input
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
    )
    result: tuple[int, str] = (proc.returncode, (proc.stderr or "") + (proc.stdout or ""))
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

    findings: list[str] = []
    for line in inspect_out.splitlines():
        stripped = line.strip()
        if stripped.startswith(("ERROR", "WARNING", "INFO", "IGNORE")) and "|" in stripped:
            findings.append(stripped.split("|", 2)[-1].strip())
        elif stripped.startswith(("ERROR", "WARNING")):
            findings.append(stripped)

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
