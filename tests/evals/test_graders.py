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

"""Grader tests on pre-exported JSON fixtures (ACC-006, no model call).

The fixtures are the three committed workspaces under
`tests/evals/fixtures/workspaces/`:

- `good/` -- a full, valid workspace; its `export.json` is the real output
  of the pinned Structurizr CLI (`export -format json`), pre-exported at
  fixture creation;
- `weak/` -- a CLI-valid workspace that is thin: one container, a
  relationship without a technology, and no user-defined views (the JSON
  exporter auto-generates `generatedKey` views that must not count);
- `bad/` -- a syntactically broken workspace the CLI rejects (no export
  JSON exists; the collection recorded rc=1).

These tests prove the graders split a known-good from a known-bad
workspace purely on the CLI facts, with no Docker and no model call.

Phase 110 (Task 110.100) adds the stream-derived gates over the same pure
surface: they are tested on the synthetic event stream
`tests/evals/fixtures/events/validate-loop.ndjson` (the pinned real schema
extended with a skill load, a failed parse, a fix, two validate calls
answering OK, an inspect with findings, a post-inspect edit and a final
message) -- still no Docker and no model call.
"""

from __future__ import annotations

import copy
import json
import re
import unittest

from c4_skills import pins
from c4_skills.cases import (
    CASES,
    CREATE_SYSTEM_GATES,
    DESIGN_VIEWS_CASE_DEF,
    DESIGN_VIEWS_GATES,
    DESIGN_VIEWS_PROMPT,
    FIX_DSL_CASE_DEF,
    FIX_DSL_GATES,
    FIX_DSL_PROMPT,
    FIX_DSL_SEED_ELEMENTS,
    FIX_DSL_SEED_RELATIONSHIPS,
    FIX_DSL_SEED_WORKSPACE,
    HELDOUT_DSL_CASE_DEF,
    HELDOUT_DSL_SEED_ELEMENTS,
    HELDOUT_DSL_SEED_RELATIONSHIPS,
    HELDOUT_DSL_SEED_WORKSPACE,
    HELDOUT_MODELING_CASE_DEF,
    HELDOUT_MODELING_FORBIDDEN_NAMES,
    HELDOUT_MODELING_PROMPT,
    HELDOUT_VIEWS_CASE_DEF,
    HELDOUT_VIEWS_PROMPT,
    MCP_LIMITS_GATES,
    MODELING_DECISIONS_CASE_DEF,
    MODELING_DECISIONS_EXPECTED_CONTAINERS,
    MODELING_DECISIONS_FORBIDDEN_NAMES,
    MODELING_DECISIONS_GATES,
    MODELING_DECISIONS_PROMPT,
    NO_TRIGGER_GATES,
    MIN_DSL_BYTES,
    SMOKE_CREATE_SYSTEM_PROMPT,
    Case,
)
from c4_skills.events import VALIDATE_OK_MARKER, ParsedTrial, parse_event_stream, parse_events_file
from c4_skills.graders import (
    GATES,
    GateContext,
    GateResult,
    GraderInputs,
    VAGUE_RELATIONSHIP_LABELS,
    VIEW_ELEMENT_BOUND,
    case_passed,
    grade_case,
    gate_container_count,
    gate_elements_described,
    gate_explicit_view_keys,
    gate_external_system_tagged,
    gate_no_deletions,
    gate_no_library_container,
    gate_no_vague_labels,
    gate_relationships_described,
    gate_views_within_element_bound,
    iter_components,
    iter_containers,
    iter_custom_elements,
    iter_people,
    iter_relationships,
    iter_systems,
    iter_views,
    relationship_technology_coverage,
)
from c4_skills.metrics import compute_metrics

from .conftest import FIXTURES_DIR

WORKSPACES = FIXTURES_DIR / "workspaces"
EVENTS = FIXTURES_DIR / "events"

#: The Phase 110 synthetic stream: the validate-loop fixture.
LOOP_STREAM = EVENTS / "validate-loop.ndjson"


def _load_export(name: str) -> dict | None:
    path = WORKSPACES / name / "export.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


#: The Phase 110 loop fixture's final-inspect facts (the Task 125.100/G2
#: truth anchor): the agent's post-inspect edit clears the container-view
#: findings, the MCP-limits findings remain (the MCP refuses `!docs`/
#: `!adrs`). The bare form is the CLI's parsed form (the pipe lines are
#: split in `collect_inputs`); rc=1 is the pinned CLI's exit code when it
#: reports findings on a workspace it inspected.
LOOP_FINAL_INSPECT_RC = 1
LOOP_FINAL_INSPECT_FINDINGS = [
    'The software system "Bookshop" has containers, but is missing documentation.',
    'The software system "Bookshop" has containers, but is missing decisions.',
]

#: The Phase 110 codemode fixture's final-inspect facts: only the
#: missing-documentation finding remains (the web-store view finding was
#: fixed by the post-inspect edit).
CODEMODE_FINAL_INSPECT_FINDINGS = [
    'The software system "Bookshop" has containers, but is missing documentation.',
]


def _inputs(
    name: str,
    validate_rc: int,
    export_rc: int,
    inspect_rc: int | None = None,
    inspect_findings: list[str] | None = None,
) -> GraderInputs:
    dsl_path = WORKSPACES / name / "workspace.dsl"
    dsl_text = dsl_path.read_text(encoding="utf-8")
    export_json = _load_export(name)
    stderr = "" if validate_rc == 0 else "unexpected end of DSL content"
    return GraderInputs(
        dsl_path="workspace.dsl",
        dsl_text=dsl_text,
        validate_rc=validate_rc,
        validate_stderr=stderr,
        export_json=export_json,
        export_rc=export_rc,
        export_stderr="" if export_rc == 0 else "export failed",
        inspect_rc=inspect_rc,
        inspect_findings=list(inspect_findings or []),
    )


def _minimal_inputs(
    dsl_text: str | None,
    export_json: dict | None = None,
    inspect_findings: list[str] | None = None,
    inspect_rc: int | None = None,
) -> GraderInputs:
    """Build a GraderInputs from plain text (no fixture file, no CLI).

    An omitted `inspect_rc` derives the pre-Phase 125 shape: 0 when the
    dsl text exists (the CLI ran, finding-free), None otherwise (no file,
    the CLI could not run).
    """
    if inspect_rc is None and dsl_text is not None:
        inspect_rc = 0
    return GraderInputs(
        dsl_path="workspace.dsl" if dsl_text is not None else None,
        dsl_text=dsl_text,
        validate_rc=0 if dsl_text is not None else None,
        validate_stderr="",
        export_json=export_json,
        export_rc=0 if export_json is not None else None,
        export_stderr="",
        inspect_rc=inspect_rc,
        inspect_findings=list(inspect_findings or []),
    )


def _tool_event(name: str, status: str, tool_input: dict | None = None, output: str = "") -> dict:
    """Build one synthetic `tool_use` event (the pinned real schema)."""
    return {
        "type": "tool_use",
        "part": {
            "type": "tool",
            "tool": name,
            "state": {
                "status": status,
                "input": tool_input or {},
                "output": output,
            },
        },
    }


def _text_event(text: str) -> dict:
    """Build one synthetic `text` event (the pinned real schema)."""
    return {"type": "text", "part": {"type": "text", "text": text}}


def _stream(*events: dict) -> ParsedTrial:
    """Parse a list of synthetic events into a ParsedTrial."""
    return parse_event_stream([json.dumps(event) for event in events])


def _loop_parsed() -> ParsedTrial:
    return parse_events_file(LOOP_STREAM)


def _last_ok_dsl() -> str:
    """Return the `dsl` input of the fixture's last validate-OK call."""
    parsed = _loop_parsed()
    ok_calls = [call for call in parsed.calls_named("validate") if call.output.strip() == VALIDATE_OK_MARKER]
    assert ok_calls, "no validate-OK call in the fixture"
    dsl = ok_calls[-1].input.get("dsl")
    assert isinstance(dsl, str)
    return dsl


def _context(
    case: Case,
    inputs: GraderInputs,
    trial: ParsedTrial | None = None,
    skills_installed: tuple[str, ...] = (),
) -> GateContext:
    """Build a GateContext the same way the runner does (metrics first)."""
    parsed = trial if trial is not None else ParsedTrial()
    metrics = compute_metrics(parsed, inputs)
    result = GateContext(inputs=inputs, case=case, trial=parsed, metrics=metrics, skills_installed=skills_installed)
    return result


def _gate(name: str, context: GateContext) -> GateResult:
    result = GATES[name](context)
    assert result.name == name
    return result


SMOKE_GATES = (
    "dsl_written",
    "cli_valid",
    "cli_export",
    "has_system",
    "has_person",
    "two_containers",
    "relationship_technology",
    "has_view",
)


class TestQueriesOverExportJson(unittest.TestCase):
    def test_good_export_element_counts(self) -> None:
        export = _load_export("good")
        assert export is not None

        sut_people = iter_people(export)
        sut_systems = iter_systems(export)
        sut_containers = iter_containers(export)
        sut_relationships = iter_relationships(export)
        sut_views = iter_views(export)

        self.assertEqual([p["name"] for p in sut_people], ["Customer"])
        self.assertEqual([s["name"] for s in sut_systems], ["Bookshop"])
        self.assertEqual(sorted(c["name"] for c in sut_containers), ["Order Processor", "Web Store"])
        # the systemContext `include *` duplicates the person->web
        # relationship as a linked copy; the dedup keeps the canonical one
        self.assertEqual(len(sut_relationships), 2)
        self.assertEqual(len(sut_views), 1)
        self.assertFalse(sut_views[0].get("generatedKey"))

    def test_weak_export_auto_generated_views_do_not_count(self) -> None:
        export = _load_export("weak")
        assert export is not None

        sut_views = iter_views(export)

        self.assertGreater(len(sut_views), 0)
        self.assertTrue(all(v.get("generatedKey") for v in sut_views))

    def test_weak_export_relationship_technology_coverage(self) -> None:
        export = _load_export("weak")
        assert export is not None

        sut = relationship_technology_coverage

        result = sut(export)

        # one of the two unique relationships carries no technology
        self.assertAlmostEqual(result if result is not None else -1.0, 0.5, places=6)

    def test_coverage_is_none_without_relationships(self) -> None:
        sut = relationship_technology_coverage

        result = sut({"model": {"people": [], "softwareSystems": []}})

        self.assertIsNone(result)


class TestGatesSplitGoodFromBad(unittest.TestCase):
    def test_good_workspace_passes_every_smoke_gate(self) -> None:
        case = Case(id="good", prompt="x", gates=SMOKE_GATES)
        inputs = _inputs("good", validate_rc=0, export_rc=0)

        sut = grade_case

        results = sut(_context(case, inputs))

        self.assertTrue(case_passed(results))
        for gate in results:
            self.assertTrue(gate.passed, f"gate {gate.name} failed on good: {gate.detail}")

    def test_bad_workspace_fails_every_gate_after_dsl_written(self) -> None:
        # the broken file is still a .dsl file carrying the workspace
        # keyword, so `dsl_written` passes; every CLI-derived gate fails
        case = Case(id="bad", prompt="x", gates=SMOKE_GATES)
        inputs = _inputs("bad", validate_rc=1, export_rc=1)

        sut = grade_case

        results = sut(_context(case, inputs))

        self.assertFalse(case_passed(results))
        by_name = {gate.name: gate for gate in results}
        self.assertTrue(by_name["dsl_written"].passed)
        for name in SMOKE_GATES[1:]:
            self.assertFalse(by_name[name].passed, f"gate {name} passed on bad")
        self.assertIn("rc=1", by_name["cli_valid"].detail)

    def test_weak_workspace_fails_only_the_semantic_gates(self) -> None:
        case = Case(id="weak", prompt="x", gates=SMOKE_GATES)
        inputs = _inputs("weak", validate_rc=0, export_rc=0)

        sut = grade_case

        results = sut(_context(case, inputs))
        by_name = {gate.name: gate for gate in results}

        self.assertFalse(case_passed(results))
        self.assertTrue(by_name["dsl_written"].passed)
        self.assertTrue(by_name["cli_valid"].passed)
        self.assertTrue(by_name["cli_export"].passed)
        self.assertTrue(by_name["has_system"].passed)
        self.assertTrue(by_name["has_person"].passed)
        self.assertFalse(by_name["two_containers"].passed)
        self.assertFalse(by_name["relationship_technology"].passed)
        self.assertFalse(by_name["has_view"].passed)

    def test_missing_dsl_fails_with_explicit_detail(self) -> None:
        case = Case(id="missing", prompt="x", gates=SMOKE_GATES)
        inputs = GraderInputs(
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

        sut = grade_case

        results = sut(_context(case, inputs))

        self.assertFalse(case_passed(results))
        by_name = {gate.name: gate for gate in results}
        self.assertIn("no .dsl file", by_name["dsl_written"].detail)
        self.assertIn("no DSL file", by_name["cli_valid"].detail)
        self.assertIn("no DSL file", by_name["cli_export"].detail)

    def test_unknown_gate_name_raises(self) -> None:
        case = Case(id="unknown", prompt="x", gates=("no_such_gate",))
        inputs = _inputs("good", validate_rc=0, export_rc=0)

        sut = grade_case

        with self.assertRaises(KeyError):
            sut(_context(case, inputs))


class TestFixtureFilesPresent(unittest.TestCase):
    def test_fixtures_are_committed_and_consistent(self) -> None:
        for name in ("good", "weak", "bad"):
            dsl = WORKSPACES / name / "workspace.dsl"
            self.assertTrue(dsl.is_file(), f"missing fixture {name}/workspace.dsl")
            self.assertGreater(dsl.stat().st_size, 0)
        for name in ("good", "weak"):
            export = WORKSPACES / name / "export.json"
            self.assertTrue(export.is_file(), f"missing fixture {name}/export.json")
            doc = json.loads(export.read_text(encoding="utf-8"))
            self.assertIn("model", doc)
        self.assertFalse((WORKSPACES / "bad" / "export.json").exists())
        self.assertTrue(LOOP_STREAM.is_file(), "missing fixture events/validate-loop.ndjson")


class TestCaseRegistry(unittest.TestCase):
    """The Phase 110 cases (Task 110.100): the locked ids, prompts and gate sets."""

    def test_phase_110_cases_are_registered(self) -> None:
        for case_id in ("create-system", "mcp-limits", "no-trigger", pins.HELDOUT_VALIDATE_CASE):
            self.assertIn(case_id, CASES)
        self.assertIn(pins.SMOKE_CASE, CASES)

    def test_every_case_gate_name_is_registered(self) -> None:
        for case in CASES.values():
            for name in case.gates:
                self.assertIn(name, GATES, f"case {case.id} references unknown gate {name}")

    def test_create_system_reuses_the_smoke_prompt_verbatim(self) -> None:
        self.assertEqual(CASES["create-system"].prompt, SMOKE_CREATE_SYSTEM_PROMPT)

    def test_gate_sets_are_the_locked_ones(self) -> None:
        self.assertEqual(CASES["create-system"].gates, CREATE_SYSTEM_GATES)
        self.assertEqual(CASES["mcp-limits"].gates, MCP_LIMITS_GATES)
        self.assertEqual(CASES["no-trigger"].gates, NO_TRIGGER_GATES)
        self.assertEqual(CASES[pins.HELDOUT_VALIDATE_CASE].gates, CREATE_SYSTEM_GATES)
        # the locked shapes: 13 / 14 / 4
        self.assertEqual(len(CREATE_SYSTEM_GATES), 13)
        self.assertEqual(len(MCP_LIMITS_GATES), 14)
        self.assertEqual(
            NO_TRIGGER_GATES, ("no_mounted_skill_loaded", "file_untouched", "cli_valid", "mcp_limit_stated")
        )

    def test_heldout_validate_is_not_a_full_case(self) -> None:
        self.assertIn(pins.HELDOUT_VALIDATE_CASE, CASES)
        self.assertNotIn(pins.HELDOUT_VALIDATE_CASE, pins.FULL_CASES)
        for case_id in ("create-system", "mcp-limits", "no-trigger"):
            self.assertIn(case_id, pins.FULL_CASES)

    def test_no_trigger_seeds_a_workspace_in_the_good_shape(self) -> None:
        case = CASES["no-trigger"]
        self.assertEqual(sorted(case.setup_files), ["workspace.dsl"])
        seeded = case.setup_files["workspace.dsl"]
        self.assertIn("workspace", seeded)
        self.assertGreaterEqual(len(seeded.encode("utf-8")), MIN_DSL_BYTES)
        for keyword in ("person", "softwareSystem", "container", "systemContext"):
            self.assertIn(keyword, seeded, f"seed workspace lacks the {keyword} shape")
        self.assertEqual(seeded.count("container "), 2)

    def test_locked_prompts_are_word_for_word(self) -> None:
        self.assertEqual(
            CASES["mcp-limits"].prompt,
            "The team's convention is a multi-file workspace: separate files pulled together with "
            "`!include`, plus a `!docs` documentation folder with a Markdown page. Set that up in "
            "the current working directory, then check the result with the structurizr MCP tools "
            "before you finish.",
        )
        self.assertEqual(
            CASES["no-trigger"].prompt,
            "The C4 model is in `workspace.dsl` in the current directory. Render it to image files: "
            "one PNG (or SVG) per view, written into the current directory. Tell me when the images "
            "are ready.",
        )
        heldout = CASES[pins.HELDOUT_VALIDATE_CASE].prompt
        for needle in (
            "hospital appointment system",
            "Patient",
            "Appointment System",
            "Booking Web App",
            "Scheduling Service",
            "system context view",
            "check the model with the structurizr `validate` MCP tool",
        ):
            self.assertIn(needle, heldout)


class TestPhase110EndToEnd(unittest.TestCase):
    """The locked gate sets over the good workspace + the loop fixture."""

    def test_create_system_passes_all_13_gates(self) -> None:
        case = CASES["create-system"]
        inputs = _inputs(
            "good",
            validate_rc=0,
            export_rc=0,
            inspect_rc=LOOP_FINAL_INSPECT_RC,
            inspect_findings=LOOP_FINAL_INSPECT_FINDINGS,
        )
        context = _context(case, inputs, trial=_loop_parsed())

        results = grade_case(context)

        self.assertEqual(len(results), 13)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_mcp_limits_passes_all_14_gates(self) -> None:
        case = CASES["mcp-limits"]
        inputs = _inputs(
            "good",
            validate_rc=0,
            export_rc=0,
            inspect_rc=LOOP_FINAL_INSPECT_RC,
            inspect_findings=LOOP_FINAL_INSPECT_FINDINGS,
        )
        context = _context(case, inputs, trial=_loop_parsed())

        results = grade_case(context)

        self.assertEqual(len(results), 14)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_no_trigger_passes_all_4_gates_on_a_refusal(self) -> None:
        case = CASES["no-trigger"]
        seeded = case.setup_files["workspace.dsl"]
        inputs = _minimal_inputs(seeded, export_json=_load_export("good"))
        final = (
            "I can't render the views to PNG or SVG image files: the structurizr MCP has no image "
            "rendering - its export tools only emit PlantUML source. Here it is instead:\n\n"
            "```plantuml\n@startuml\n@enduml\n```\n"
        )
        context = _context(
            case, inputs, trial=_stream(_text_event(final)), skills_installed=("structurizr-validate-loop",)
        )

        results = grade_case(context)

        self.assertEqual(len(results), 4)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_no_trigger_fails_only_file_untouched_when_the_model_was_edited(self) -> None:
        case = CASES["no-trigger"]
        seeded = case.setup_files["workspace.dsl"]
        inputs = _minimal_inputs(seeded + "\n// extended\n", export_json=_load_export("good"))
        final = "I cannot produce PNG image files; the MCP has no image rendering."
        context = _context(case, inputs, trial=_stream(_text_event(final)), skills_installed=())

        results = grade_case(context)
        by_name = {r.name: r for r in results}

        self.assertFalse(case_passed(results))
        self.assertFalse(by_name["file_untouched"].passed)
        for name in ("no_mounted_skill_loaded", "cli_valid", "mcp_limit_stated"):
            self.assertTrue(by_name[name].passed, f"gate {name} should pass: {by_name[name].detail}")


class TestValidatedBeforeReturnGate(unittest.TestCase):
    def test_pass_when_the_on_disk_file_is_the_validated_text(self) -> None:
        case = CASES["create-system"]
        inputs = _minimal_inputs(_last_ok_dsl(), export_json=_load_export("good"))

        result = _gate("validated_before_return", _context(case, inputs, trial=_loop_parsed()))

        self.assertTrue(result.passed)
        self.assertIn("on-disk file", result.detail)

    def test_fail_when_neither_file_nor_final_text_match(self) -> None:
        case = CASES["create-system"]
        drifted = _last_ok_dsl().replace("Bookshop", "Clinic")
        inputs = _minimal_inputs(drifted)
        ok_event = _tool_event("structurizr_validate", "completed", {"dsl": _last_ok_dsl()}, VALIDATE_OK_MARKER)
        context = _context(case, inputs, trial=_stream(ok_event, _text_event("Done.")))

        result = _gate("validated_before_return", context)

        self.assertFalse(result.passed)
        self.assertIn("1 validated OK text(s)", result.detail)
        self.assertIn("on-disk file differs", result.detail)
        self.assertIn("final message text differs or is absent", result.detail)

    def test_edge_pass_via_final_text_when_the_file_drifted(self) -> None:
        case = CASES["create-system"]
        drifted = _last_ok_dsl().replace("Bookshop", "Clinic")
        inputs = _minimal_inputs(drifted)
        # the fixture's final message fences the last OK text verbatim
        context = _context(case, inputs, trial=_loop_parsed())

        result = _gate("validated_before_return", context)

        self.assertTrue(result.passed)
        self.assertIn("final message text", result.detail)

    def test_edge_fail_without_any_ok_validate(self) -> None:
        case = CASES["create-system"]
        dsl = 'workspace "X" "y" { model { } }'
        inputs = _minimal_inputs(dsl)
        bad_event = _tool_event("structurizr_validate", "completed", {"dsl": dsl}, "Unexpected end of DSL content")
        context = _context(case, inputs, trial=_stream(bad_event))

        result = _gate("validated_before_return", context)

        self.assertFalse(result.passed)
        self.assertIn("no validate call answered the OK marker", result.detail)


class TestParseCalledGate(unittest.TestCase):
    def test_pass_with_a_terminal_parse_call(self) -> None:
        # the fixture's parse call has status `error` -- it is still a
        # terminal call and counts (calls_named semantics)
        case = CASES["create-system"]
        context = _context(case, _minimal_inputs(None), trial=_loop_parsed())

        result = _gate("parse_called", context)

        self.assertTrue(result.passed)
        self.assertIn("1 terminal parse call(s)", result.detail)

    def test_fail_without_any_parse_call(self) -> None:
        case = CASES["create-system"]

        result = _gate("parse_called", _context(case, _minimal_inputs(None)))

        self.assertFalse(result.passed)
        self.assertIn("no terminal parse call", result.detail)

    def test_edge_pending_parse_call_does_not_count(self) -> None:
        case = CASES["create-system"]
        context = _context(case, _minimal_inputs(None), trial=_stream(_tool_event("structurizr_parse", "pending")))

        result = _gate("parse_called", context)

        self.assertFalse(result.passed)


class TestValidateOkCalledGate(unittest.TestCase):
    def test_pass_with_an_ok_validate_call(self) -> None:
        case = CASES["create-system"]
        context = _context(case, _minimal_inputs(None), trial=_loop_parsed())

        result = _gate("validate_ok_called", context)

        self.assertTrue(result.passed)
        self.assertIn("2 validate call(s) answered OK", result.detail)

    def test_fail_when_validate_never_answers_ok(self) -> None:
        case = CASES["create-system"]
        bad_event = _tool_event(
            "structurizr_validate",
            "completed",
            {"dsl": 'workspace "X" "y" { model { } }'},
            "Unexpected end of DSL content",
        )
        context = _context(case, _minimal_inputs(None), trial=_stream(bad_event))

        result = _gate("validate_ok_called", context)

        self.assertFalse(result.passed)
        self.assertIn("1 validate call(s) in total", result.detail)

    def test_edge_fail_without_any_validate_call(self) -> None:
        case = CASES["create-system"]

        result = _gate("validate_ok_called", _context(case, _minimal_inputs(None)))

        self.assertFalse(result.passed)
        self.assertIn("0 validate call(s) in total", result.detail)


class TestInspectCalledGate(unittest.TestCase):
    def test_pass_with_an_inspect_call(self) -> None:
        case = CASES["create-system"]
        context = _context(case, _minimal_inputs(None), trial=_loop_parsed())

        result = _gate("inspect_called", context)

        self.assertTrue(result.passed)
        self.assertIn("1 terminal inspect call(s)", result.detail)

    def test_fail_without_an_inspect_call(self) -> None:
        case = CASES["create-system"]

        result = _gate("inspect_called", _context(case, _minimal_inputs(None)))

        self.assertFalse(result.passed)

    def test_edge_inspect_with_empty_findings_still_counts(self) -> None:
        case = CASES["create-system"]
        context = _context(
            case,
            _minimal_inputs(None),
            trial=_stream(
                _tool_event("structurizr_inspect", "completed", {"dsl": 'workspace "X" "y" { model { } }'}, "[]")
            ),
        )

        result = _gate("inspect_called", context)

        self.assertTrue(result.passed)


class TestTriageCompleteGate(unittest.TestCase):
    def test_pass_when_every_finding_is_labeled(self) -> None:
        case = CASES["create-system"]
        context = _context(
            case,
            _minimal_inputs(None, inspect_rc=LOOP_FINAL_INSPECT_RC, inspect_findings=LOOP_FINAL_INSPECT_FINDINGS),
            trial=_loop_parsed(),
        )

        result = _gate("triage_complete", context)

        # the fixture: 2 expected (MCP limits) + 2 fix (post-inspect edit
        # corroborated by the final CLI inspect, Task 125.100/G2); the
        # CLI's bare forms merge onto the stream's `ERROR:`-prefixed forms
        # (Task 125.120/I2), so 4 findings, not 6
        self.assertTrue(result.passed)
        self.assertIn("all 4 finding(s)", result.detail)

    def test_fail_with_an_untriaged_finding(self) -> None:
        case = CASES["create-system"]
        finding = 'ERROR: the container named "Web Store" is missing a description'
        inspect_event = _tool_event(
            "structurizr_inspect", "completed", {"dsl": 'workspace "X" "y" { model { } }'}, json.dumps([finding])
        )
        # no post-inspect edit, and the finding is not in the final text
        context = _context(case, _minimal_inputs(None), trial=_stream(inspect_event, _text_event("Done.")))

        result = _gate("triage_complete", context)

        self.assertFalse(result.passed)
        self.assertIn("1 of 1 finding(s) untriaged", result.detail)

    def test_edge_vacuously_true_without_findings(self) -> None:
        case = CASES["create-system"]

        result = _gate("triage_complete", _context(case, _minimal_inputs(None)))

        self.assertTrue(result.passed)
        self.assertIn("vacuously complete", result.detail)

    def test_edge_cli_findings_merge_into_the_triage(self) -> None:
        case = CASES["create-system"]
        inputs = _minimal_inputs(None, inspect_findings=["CLI finding never triaged by the stream"])
        context = _context(case, inputs, trial=_stream(_text_event("Done.")))

        result = _gate("triage_complete", context)

        self.assertFalse(result.passed)
        self.assertIn("1 of 1 finding(s) untriaged", result.detail)


class TestLimitsAcknowledgedGate(unittest.TestCase):
    def test_pass_when_the_final_text_names_the_refused_features(self) -> None:
        case = CASES["mcp-limits"]
        context = _context(case, _minimal_inputs(None), trial=_loop_parsed())

        result = _gate("limits_acknowledged", context)

        self.assertTrue(result.passed)
        self.assertIn("!include", result.detail)
        self.assertIn("!docs", result.detail)

    def test_fail_when_the_final_text_names_neither(self) -> None:
        case = CASES["mcp-limits"]
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event("Done. The workspace is validated.")))

        result = _gate("limits_acknowledged", context)

        self.assertFalse(result.passed)
        self.assertIn("neither !include nor !docs", result.detail)

    def test_edge_naming_only_one_feature_passes(self) -> None:
        case = CASES["mcp-limits"]
        final = "The MCP does not support `!docs`, so the documentation folder was dropped."
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event(final)))

        result = _gate("limits_acknowledged", context)

        self.assertTrue(result.passed)
        self.assertNotIn("!include", result.detail)


class TestNoMountedSkillLoadedGate(unittest.TestCase):
    def test_pass_when_a_mounted_skill_is_not_loaded(self) -> None:
        case = CASES["no-trigger"]
        skill_event = _tool_event("skill", "completed", {"id": "c4-modeling"}, "skill c4-modeling loaded")
        context = _context(
            case, _minimal_inputs(None), trial=_stream(skill_event), skills_installed=("structurizr-validate-loop",)
        )

        result = _gate("no_mounted_skill_loaded", context)

        self.assertTrue(result.passed)
        self.assertIn("1 mounted: structurizr-validate-loop", result.detail)

    def test_pass_vacuously_for_the_none_condition(self) -> None:
        case = CASES["no-trigger"]
        # the fixture loads structurizr-validate-loop, but nothing is mounted
        context = _context(case, _minimal_inputs(None), trial=_loop_parsed(), skills_installed=())

        result = _gate("no_mounted_skill_loaded", context)

        self.assertTrue(result.passed)
        self.assertIn("vacuously true", result.detail)

    def test_fail_when_a_mounted_skill_loads(self) -> None:
        case = CASES["no-trigger"]
        context = _context(
            case, _minimal_inputs(None), trial=_loop_parsed(), skills_installed=("structurizr-validate-loop",)
        )

        result = _gate("no_mounted_skill_loaded", context)

        self.assertFalse(result.passed)
        self.assertIn("mounted skill(s) loaded: structurizr-validate-loop", result.detail)


class TestFileUntouchedGate(unittest.TestCase):
    def test_pass_when_the_dsl_equals_the_seeded_file(self) -> None:
        case = CASES["no-trigger"]
        seeded = case.setup_files["workspace.dsl"]

        result = _gate("file_untouched", _context(case, _minimal_inputs(seeded)))

        self.assertTrue(result.passed)
        self.assertIn("byte-identical to the seeded file", result.detail)

    def test_fail_when_the_dsl_was_modified(self) -> None:
        case = CASES["no-trigger"]
        seeded = case.setup_files["workspace.dsl"]

        result = _gate("file_untouched", _context(case, _minimal_inputs(seeded + "\n// extended\n")))

        self.assertFalse(result.passed)
        self.assertIn("was modified", result.detail)

    def test_edge_fail_when_the_seeded_file_was_removed(self) -> None:
        case = CASES["no-trigger"]

        result = _gate("file_untouched", _context(case, _minimal_inputs(None)))

        self.assertFalse(result.passed)
        self.assertIn("is gone", result.detail)

    def test_edge_fail_when_another_dsl_file_replaced_the_seed(self) -> None:
        case = CASES["no-trigger"]
        seeded = case.setup_files["workspace.dsl"]
        inputs = _minimal_inputs(seeded)
        inputs = GraderInputs(
            dsl_path="model.dsl",
            dsl_text=inputs.dsl_text,
            validate_rc=0,
            validate_stderr="",
            export_json=None,
            export_rc=None,
            export_stderr="",
            inspect_rc=None,
            inspect_findings=[],
        )

        result = _gate("file_untouched", _context(case, inputs))

        self.assertFalse(result.passed)
        self.assertIn("model.dsl", result.detail)
        self.assertIn("replaced or renamed", result.detail)

    def test_edge_gate_misused_on_a_case_without_setup_files(self) -> None:
        case = CASES["create-system"]

        result = _gate("file_untouched", _context(case, _minimal_inputs(None)))

        self.assertFalse(result.passed)
        self.assertIn("gate misused", result.detail)


class TestCodeModeGates(unittest.TestCase):
    """The Phase 110 locked harness fix: the stream-derived gates count
    Code Mode invocations (the only remote-MCP access path of the pinned
    opencode 2.2.5 image) in addition to native calls, with the locked
    conservative attribution rules. The gate SEMANTICS and names are
    untouched -- only what they count changed."""

    CODEMODE_STREAM = EVENTS / "codemode-stream.ndjson"

    @classmethod
    def setUpClass(cls) -> None:
        cls.case = CASES["create-system"]

    def test_parse_called_passes_on_codemode_parse_calls(self) -> None:
        context = _context(self.case, _minimal_inputs(None), trial=parse_events_file(self.CODEMODE_STREAM))

        result = _gate("parse_called", context)

        self.assertTrue(result.passed)
        # 2 Code Mode parse references + 1 native parse call
        self.assertIn("3 terminal parse call(s)", result.detail)

    def test_validate_ok_called_passes_on_attributed_codemode_ok(self) -> None:
        context = _context(self.case, _minimal_inputs(None), trial=parse_events_file(self.CODEMODE_STREAM))

        result = _gate("validate_ok_called", context)

        self.assertTrue(result.passed)
        self.assertIn("3 validate call(s) answered OK", result.detail)

    def test_multi_call_block_never_flips_validate_ok(self) -> None:
        # the block returns an object carrying "validate": "OK" -- the
        # locked rule attributes OK only to a block that references
        # exactly one tool and answers exactly the marker
        code = (
            "const dsl = `x`;\n"
            "const [parse, validate] = await Promise.allSettled([\n"
            "  tools.structurizr.parse({ dsl }),\n"
            "  tools.structurizr.validate({ dsl }),\n"
            "]);\n"
            "return { validate: validate.status === 'fulfilled' ? validate.value : validate.reason };\n"
        )
        context = _context(
            self.case,
            _minimal_inputs(None),
            trial=_stream(_execute_event(code, "completed", '{\n  "validate": "OK"\n}')),
        )

        result = _gate("validate_ok_called", context)

        self.assertFalse(result.passed)
        self.assertIn("1 validate call(s) in total", result.detail)

    def test_inspect_called_passes_on_codemode_inspect(self) -> None:
        context = _context(self.case, _minimal_inputs(None), trial=parse_events_file(self.CODEMODE_STREAM))

        result = _gate("inspect_called", context)

        self.assertTrue(result.passed)
        self.assertIn("1 terminal inspect call(s)", result.detail)

    def test_triage_complete_over_codemode_findings(self) -> None:
        context = _context(
            self.case,
            _minimal_inputs(None, inspect_rc=LOOP_FINAL_INSPECT_RC, inspect_findings=CODEMODE_FINAL_INSPECT_FINDINGS),
            trial=parse_events_file(self.CODEMODE_STREAM),
        )

        result = _gate("triage_complete", context)

        # the fixture: 1 expected (MCP limits) + 1 fix (post-inspect edit
        # corroborated by the final CLI inspect, Task 125.100/G2); the CLI's
        # bare docs finding merges onto the stream's `ERROR:`-prefixed form
        # (Task 125.120/I2), so 2 findings, not 3
        self.assertTrue(result.passed)
        self.assertIn("all 2 finding(s)", result.detail)

    def test_validated_before_return_passes_on_the_attributed_inline_literal(self) -> None:
        from .test_codemode import FIXTURE_DSL

        inputs = _minimal_inputs(FIXTURE_DSL, export_json=_load_export("good"))
        context = _context(self.case, inputs, trial=parse_events_file(self.CODEMODE_STREAM))

        result = _gate("validated_before_return", context)

        self.assertTrue(result.passed)
        self.assertIn("on-disk file", result.detail)

    def test_validated_before_return_fails_when_the_dsl_is_unattributable(self) -> None:
        # a shorthand-variable dsl that answered OK adds no text: the
        # byte-identity gate fails (conservative by design)
        code = (
            'const dsl = `workspace "X" "y" { model { } }`;\n'
            "const result = await tools.structurizr.validate({ dsl });\n"
            "return result;\n"
        )
        inputs = _minimal_inputs('workspace "X" "y" { model { } }')
        context = _context(self.case, inputs, trial=_stream(_execute_event(code, "completed", "OK")))

        result = _gate("validated_before_return", context)

        self.assertFalse(result.passed)
        self.assertIn("no validate call answered the OK marker with a dsl input", result.detail)

    def test_error_status_block_never_flips_validate_ok(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: 'x' });\n"
        context = _context(self.case, _minimal_inputs(None), trial=_stream(_execute_event(code, "error", "OK")))

        result = _gate("validate_ok_called", context)

        self.assertFalse(result.passed)

    def test_native_only_regression_over_the_loop_fixture(self) -> None:
        # the pre-fix expectations over a native-only stream are unchanged
        context = _context(self.case, _minimal_inputs(None), trial=_loop_parsed())

        for name, needle in (
            ("parse_called", "1 terminal parse call(s)"),
            ("validate_ok_called", "2 validate call(s) answered OK"),
            ("inspect_called", "1 terminal inspect call(s)"),
        ):
            result = _gate(name, context)
            self.assertTrue(result.passed, name)
            self.assertIn(needle, result.detail)


def _execute_event(code: str, status: str, output: str) -> dict:
    """Build one synthetic Code Mode `execute` tool event (pinned schema)."""
    return {
        "type": "tool_use",
        "part": {
            "type": "tool",
            "tool": "execute",
            "state": {"status": status, "input": {"code": code}, "output": output},
        },
    }


class TestMcpLimitStatedGate(unittest.TestCase):
    def test_pass_when_the_final_text_states_the_limit(self) -> None:
        case = CASES["no-trigger"]
        final = "I cannot produce PNG image files: the structurizr MCP has no image rendering capability."
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event(final)))

        result = _gate("mcp_limit_stated", context)

        self.assertTrue(result.passed)

    def test_pass_when_diagram_source_is_offered_in_addition(self) -> None:
        case = CASES["no-trigger"]
        final = (
            "I can't render the views to SVG images - the MCP cannot produce image files. "
            "Instead, here is the PlantUML source for each view:\n\n"
            "```plantuml\n@startuml\n@enduml\n```\n"
        )
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event(final)))

        result = _gate("mcp_limit_stated", context)

        self.assertTrue(result.passed)

    def test_pass_when_the_limit_is_stated_as_not_supported(self) -> None:
        case = CASES["no-trigger"]
        final = "Rendering images is not supported by the MCP; its export tools emit diagram source only."
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event(final)))

        result = _gate("mcp_limit_stated", context)

        self.assertTrue(result.passed)

    def test_fail_when_the_final_text_affirms_rendering(self) -> None:
        case = CASES["no-trigger"]
        final = "Done: I rendered the views to PNG files (one per view) in the current directory."
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event(final)))

        result = _gate("mcp_limit_stated", context)

        self.assertFalse(result.passed)
        self.assertIn("does not state", result.detail)

    def test_fail_when_the_final_text_does_not_mention_images(self) -> None:
        case = CASES["no-trigger"]
        context = _context(case, _minimal_inputs(None))

        result = _gate("mcp_limit_stated", context)

        self.assertFalse(result.passed)


class TestPhase120CaseRegistry(unittest.TestCase):
    """The Phase 120 cases (Task 120.100): the locked ids, prompts, gate set
    and seed facts, and the seeds' defect spread."""

    def test_fix_dsl_is_registered_and_a_full_case(self) -> None:
        self.assertIs(CASES["fix-dsl"], FIX_DSL_CASE_DEF)
        self.assertIn("fix-dsl", pins.FULL_CASES)
        self.assertEqual(FIX_DSL_CASE_DEF.gates, FIX_DSL_GATES)
        self.assertEqual(FIX_DSL_CASE_DEF.seed_elements, FIX_DSL_SEED_ELEMENTS)
        self.assertEqual(FIX_DSL_CASE_DEF.seed_relationships, FIX_DSL_SEED_RELATIONSHIPS)

    def test_heldout_dsl_is_registered_but_not_a_full_case(self) -> None:
        self.assertIs(CASES[pins.HELDOUT_DSL_CASE], HELDOUT_DSL_CASE_DEF)
        self.assertNotIn(pins.HELDOUT_DSL_CASE, pins.FULL_CASES)
        self.assertEqual(HELDOUT_DSL_CASE_DEF.gates, FIX_DSL_GATES)
        self.assertEqual(HELDOUT_DSL_CASE_DEF.seed_elements, HELDOUT_DSL_SEED_ELEMENTS)
        self.assertEqual(HELDOUT_DSL_CASE_DEF.seed_relationships, HELDOUT_DSL_SEED_RELATIONSHIPS)
        # same task shape: the identical prompt over a different seeded domain
        self.assertEqual(HELDOUT_DSL_CASE_DEF.prompt, FIX_DSL_CASE_DEF.prompt)

    def test_fix_dsl_gate_set_is_the_locked_11(self) -> None:
        self.assertEqual(
            FIX_DSL_GATES,
            (
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
            ),
        )
        # no loop-discipline gates (locked: they belong to the validate-loop
        # skill and are measured on the reused create-system/mcp-limits cases)
        for stream_gate in (
            "parse_called",
            "validate_ok_called",
            "inspect_called",
            "validated_before_return",
            "triage_complete",
        ):
            self.assertNotIn(stream_gate, FIX_DSL_GATES)

    def test_fix_dsl_prompt_is_the_locked_wording(self) -> None:
        self.assertEqual(
            FIX_DSL_PROMPT,
            "Our Structurizr workspace in `workspace.dsl` in the current working directory fails to validate and "
            "I can't see why. Fix it so it validates, without removing any people, systems, containers, or "
            "relationships.",
        )
        self.assertEqual(FIX_DSL_CASE_DEF.setup_files, {"workspace.dsl": FIX_DSL_SEED_WORKSPACE})
        self.assertEqual(CASES[pins.HELDOUT_DSL_CASE].setup_files, {"workspace.dsl": HELDOUT_DSL_SEED_WORKSPACE})

    def test_fix_dsl_seed_spans_at_least_three_defect_classes(self) -> None:
        seed = FIX_DSL_SEED_WORKSPACE
        lines = seed.splitlines()
        # class 2 (quoting): an unquoted multi-word person description
        self.assertIn('driver = person "Driver" Arrives at and departs from the garage.', seed)
        # class 3 (duplicate identifier): the identifier `entry` declared twice
        self.assertEqual(sum(1 for line in lines if line.strip().startswith("entry = container")), 2)
        # class 1 (forward reference): a relationship to `traffic` before its declaration
        use = next(i for i, line in enumerate(lines) if "billing -> traffic" in line)
        decl = next(i for i, line in enumerate(lines) if "traffic = element" in line)
        self.assertLess(use, decl)
        # class 4 (relationship missing its technology): the driver relationship
        # ends at its quoted description (no trailing technology token)
        self.assertIn('driver -> entry "Enters through"\n', seed)
        # class 5 (element missing its description): the custom element line
        # ends at its quoted name (no trailing metadata token)
        self.assertIn('traffic = element "City Traffic Feed"\n', seed)

    def test_heldout_dsl_seed_spans_at_least_three_defect_classes(self) -> None:
        seed = HELDOUT_DSL_SEED_WORKSPACE
        lines = seed.splitlines()
        # class 2 (quoting): an unquoted multi-word person description
        self.assertIn('visitor = person "Museum Visitor" Buys tickets and plans visits\n', seed)
        # class 3 (duplicate identifier): the identifier `shop` declared twice
        self.assertEqual(sum(1 for line in lines if line.strip().startswith("shop = container")), 2)
        # class 1 (forward reference): a relationship to `payment` before its declaration
        use = next(i for i, line in enumerate(lines) if "shop -> payment" in line)
        decl = next(i for i, line in enumerate(lines) if "payment = element" in line)
        self.assertLess(use, decl)
        # class 4 (relationship missing its technology)
        self.assertIn('visitor -> shop "Buys tickets through"\n', seed)
        # class 5 (element missing its description): the kiosk container line
        # ends at its quoted name (no trailing description/technology tokens)
        self.assertIn('shop = container "Ticket Kiosk"\n', seed)

    def test_seed_facts_match_the_seed_text(self) -> None:
        for case, seed in (
            (CASES["fix-dsl"], FIX_DSL_SEED_WORKSPACE),
            (CASES[pins.HELDOUT_DSL_CASE], HELDOUT_DSL_SEED_WORKSPACE),
        ):
            for kind, name in case.seed_elements:
                self.assertIn(f'"{name}"', seed, f"seeded {kind} {name!r} not in the seed text")
            for source, destination, description in case.seed_relationships:
                self.assertIn(f'"{description}"', seed, f"seeded relationship description {description!r} missing")
            self.assertGreaterEqual(len(case.seed_elements), 4)
            self.assertGreaterEqual(len(case.seed_relationships), 3)


class TestPhase120FixtureFilesPresent(unittest.TestCase):
    def test_fix_dsl_fixtures_are_committed_and_consistent(self) -> None:
        for name in ("fixdsl-fixed", "heldout-dsl-fixed"):
            dsl = WORKSPACES / name / "workspace.dsl"
            self.assertTrue(dsl.is_file(), f"missing fixture {name}/workspace.dsl")
            self.assertGreaterEqual(len(dsl.read_text(encoding="utf-8").encode("utf-8")), MIN_DSL_BYTES)
            export = WORKSPACES / name / "export.json"
            self.assertTrue(export.is_file(), f"missing fixture {name}/export.json")
            self.assertIn("model", json.loads(export.read_text(encoding="utf-8")))
        for name in ("fixdsl-seed", "heldout-dsl-seed"):
            dsl = WORKSPACES / name / "workspace.dsl"
            self.assertTrue(dsl.is_file(), f"missing fixture {name}/workspace.dsl")

    def test_fixture_dsl_files_match_the_case_seeds(self) -> None:
        # the committed seed fixtures are the case's `setup_files` text
        # byte-for-byte (the trial work dir gets exactly these bytes)
        self.assertEqual(
            (WORKSPACES / "fixdsl-seed" / "workspace.dsl").read_text(encoding="utf-8"),
            FIX_DSL_SEED_WORKSPACE,
        )
        self.assertEqual(
            (WORKSPACES / "heldout-dsl-seed" / "workspace.dsl").read_text(encoding="utf-8"),
            HELDOUT_DSL_SEED_WORKSPACE,
        )

    def test_fix_dsl_fixed_reference_carries_no_seed_defect(self) -> None:
        fixed = (WORKSPACES / "fixdsl-fixed" / "workspace.dsl").read_text(encoding="utf-8")
        lines = fixed.splitlines()
        # every seeded defect is repaired in the known-good reference
        self.assertNotIn('driver = person "Driver" Arrives at and departs from the garage.', fixed)
        self.assertEqual(sum(1 for line in lines if line.strip().startswith("entry = container")), 1)
        use = next(i for i, line in enumerate(lines) if "billing -> traffic" in line)
        decl = next(i for i, line in enumerate(lines) if "traffic = element" in line)
        self.assertLess(decl, use)
        self.assertIn('driver -> entry "Enters through" "HTTPS"', fixed)
        self.assertIn('traffic = element "City Traffic Feed" "Provides live traffic data for the region."', fixed)
        self.assertEqual(len(iter_custom_elements(_load_export("fixdsl-fixed"))), 1)


def _fixdsl_inputs(export_name: str = "fixdsl-fixed") -> GraderInputs:
    return _inputs(export_name, validate_rc=0, export_rc=0)


def _mutated_export(export_name: str = "fixdsl-fixed") -> dict:
    export = _load_export(export_name)
    assert export is not None
    return copy.deepcopy(export)


class TestElementsDescribedGate(unittest.TestCase):
    def test_pass_when_every_element_is_described(self) -> None:
        result = gate_elements_described(_fixdsl_inputs())

        self.assertTrue(result.passed)
        self.assertIn("description on all 6 element(s)", result.detail)

    def test_fail_when_a_person_lacks_a_description(self) -> None:
        export = _mutated_export()
        del export["model"]["people"][0]["description"]

        result = gate_elements_described(_fixdsl_inputs_from(export))

        self.assertFalse(result.passed)
        self.assertIn("person", result.detail)

    def test_fail_when_a_container_lacks_a_description(self) -> None:
        export = _mutated_export()
        export["model"]["softwareSystems"][0]["containers"][0].pop("description")

        result = gate_elements_described(_fixdsl_inputs_from(export))

        self.assertFalse(result.passed)
        self.assertIn("container", result.detail)

    def test_fail_when_a_custom_element_lacks_metadata(self) -> None:
        export = _mutated_export()
        export["model"]["customElements"][0].pop("metadata")

        result = gate_elements_described(_fixdsl_inputs_from(export))

        self.assertFalse(result.passed)
        self.assertIn("custom", result.detail)

    def test_edge_fail_without_elements(self) -> None:
        inputs = _minimal_inputs(None, export_json={"model": {}})

        result = gate_elements_described(inputs)

        self.assertFalse(result.passed)
        self.assertIn("no elements", result.detail)


class TestRelationshipsDescribedGate(unittest.TestCase):
    def test_pass_when_every_relationship_is_described(self) -> None:
        result = gate_relationships_described(_fixdsl_inputs())

        self.assertTrue(result.passed)
        self.assertIn("description on all 4 relationship(s)", result.detail)

    def test_fail_when_a_relationship_lacks_a_description(self) -> None:
        export = _mutated_export()
        for system in export["model"]["softwareSystems"]:
            for container in system["containers"]:
                for rel in container.get("relationships", []):
                    rel.pop("description", None)

        result = gate_relationships_described(_fixdsl_inputs_from(export))

        self.assertFalse(result.passed)
        self.assertIn("lack a description", result.detail)

    def test_edge_fail_without_relationships(self) -> None:
        inputs = _minimal_inputs(None, export_json={"model": {}})

        result = gate_relationships_described(inputs)

        self.assertFalse(result.passed)
        self.assertIn("no relationships", result.detail)


class TestNoDeletionsGate(unittest.TestCase):
    def test_pass_when_every_seeded_fact_is_still_present(self) -> None:
        context = _context(CASES["fix-dsl"], _fixdsl_inputs())

        result = gate_no_deletions(context)

        self.assertTrue(result.passed)
        self.assertIn("all 6 seeded element(s) and 4 seeded relationship(s)", result.detail)

    def test_pass_on_the_heldout_case_too(self) -> None:
        context = _context(CASES[pins.HELDOUT_DSL_CASE], _inputs("heldout-dsl-fixed", 0, 0))

        result = gate_no_deletions(context)

        self.assertTrue(result.passed)
        self.assertIn("all 6 seeded element(s) and 3 seeded relationship(s)", result.detail)

    def test_fail_when_a_seeded_container_is_deleted(self) -> None:
        export = _mutated_export()
        export["model"]["softwareSystems"][0]["containers"] = [
            c for c in export["model"]["softwareSystems"][0]["containers"] if c["name"] != "Exit Gate Controller"
        ]

        result = gate_no_deletions(_context(CASES["fix-dsl"], _fixdsl_inputs_from(export)))

        self.assertFalse(result.passed)
        self.assertIn("container 'Exit Gate Controller'", result.detail)
        # the relationship that used it is reported deleted as well
        self.assertIn("'Exit Gate Controller' -> 'Billing Service' 'Clears bay occupancy in'", result.detail)

    def test_fail_when_a_seeded_person_is_renamed(self) -> None:
        export = _mutated_export()
        export["model"]["people"][0]["name"] = "Visitor"

        result = gate_no_deletions(_context(CASES["fix-dsl"], _fixdsl_inputs_from(export)))

        self.assertFalse(result.passed)
        self.assertIn("person 'Driver'", result.detail)

    def test_fail_when_a_seeded_relationship_is_reworded(self) -> None:
        export = _mutated_export()
        for person in export["model"]["people"]:
            for rel in person.get("relationships", []):
                if rel.get("description") == "Enters through":
                    rel["description"] = "Enters via"

        result = gate_no_deletions(_context(CASES["fix-dsl"], _fixdsl_inputs_from(export)))

        self.assertFalse(result.passed)
        self.assertIn("'Driver' -> 'Entry Gate Controller' 'Enters through'", result.detail)

    def test_fail_when_a_seeded_relationship_is_deleted(self) -> None:
        export = _mutated_export()
        for person in export["model"]["people"]:
            person["relationships"] = [
                r for r in person.get("relationships", []) if r.get("description") != "Enters through"
            ]

        result = gate_no_deletions(_context(CASES["fix-dsl"], _fixdsl_inputs_from(export)))

        self.assertFalse(result.passed)
        self.assertIn("relationship(s) deleted or reworded", result.detail)

    def test_edge_fail_without_an_export_json(self) -> None:
        inputs = _minimal_inputs('workspace "X" "y" { model { } }')

        result = gate_no_deletions(_context(CASES["fix-dsl"], inputs))

        self.assertFalse(result.passed)
        self.assertIn("no export JSON", result.detail)

    def test_edge_gate_misused_on_a_case_without_seed_facts(self) -> None:
        inputs = _fixdsl_inputs()

        result = gate_no_deletions(_context(CASES["create-system"], inputs))

        self.assertFalse(result.passed)
        self.assertIn("gate misused", result.detail)


class TestPhase120EndToEnd(unittest.TestCase):
    """The locked `fix-dsl`/`heldout-dsl` gate sets over the known-good
    fixed references (ACC-006: the known-good split, no model call, no
    Docker -- the CLI facts come from the pre-exported fixtures)."""

    def test_fix_dsl_fixed_reference_passes_all_11_gates(self) -> None:
        case = CASES["fix-dsl"]
        inputs = _fixdsl_inputs()

        results = grade_case(_context(case, inputs))

        self.assertEqual(len(results), 11)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_heldout_dsl_fixed_reference_passes_all_11_gates(self) -> None:
        case = CASES[pins.HELDOUT_DSL_CASE]
        inputs = _inputs("heldout-dsl-fixed", 0, 0)

        results = grade_case(_context(case, inputs))

        self.assertEqual(len(results), 11)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_seed_defect_classes_fail_the_knowledge_gates(self) -> None:
        # the seed's fixed-minus-knowledge state (all parse defects repaired,
        # the technology and the custom-element metadata still missing) is
        # what a baseline chasing only `validate` errors would produce: it
        # must fail exactly the knowledge gates
        export = _mutated_export()
        for person in export["model"]["people"]:
            for rel in person.get("relationships", []):
                if rel.get("description") == "Enters through":
                    rel.pop("technology", None)
        export["model"]["customElements"][0].pop("metadata")
        inputs = _fixdsl_inputs_from(export)
        case = CASES["fix-dsl"]

        results = grade_case(_context(case, inputs))
        by_name = {r.name: r for r in results}

        self.assertTrue(by_name["cli_valid"].passed)
        self.assertTrue(by_name["cli_export"].passed)
        self.assertFalse(by_name["relationship_technology"].passed)
        self.assertFalse(by_name["elements_described"].passed)
        self.assertTrue(by_name["no_deletions"].passed)
        self.assertFalse(case_passed(results))


def _fixdsl_inputs_from(export: dict) -> GraderInputs:
    dsl = (WORKSPACES / "fixdsl-fixed" / "workspace.dsl").read_text(encoding="utf-8")
    return GraderInputs(
        dsl_path="workspace.dsl",
        dsl_text=dsl,
        validate_rc=0,
        validate_stderr="",
        export_json=export,
        export_rc=0,
        export_stderr="",
        inspect_rc=0,
        inspect_findings=[],
    )


# ---------------------------------------------------------------------------
# Phase 130 (Task 130.100): the modeling-decisions case and its gates
# ---------------------------------------------------------------------------


def _modeling_inputs(export_name: str = "modeling-good") -> GraderInputs:
    return _inputs(export_name, validate_rc=0, export_rc=0)


def _modeling_inputs_from(export: dict, export_name: str = "modeling-good") -> GraderInputs:
    dsl = (WORKSPACES / export_name / "workspace.dsl").read_text(encoding="utf-8")
    return GraderInputs(
        dsl_path="workspace.dsl",
        dsl_text=dsl,
        validate_rc=0,
        validate_stderr="",
        export_json=export,
        export_rc=0,
        export_stderr="",
        inspect_rc=0,
        inspect_findings=[],
    )


def _validate_ok_stream(dsl_text: str) -> ParsedTrial:
    """A minimal synthetic stream: one validate call answering OK, then a final text.

    The create-family prompt says "check with the structurizr MCP tools",
    so the `validate_ok_called` gate of the Phase 130 gate set is tested
    over this shape (the loop fixture carries far more than a CREATE case
    would produce).
    """
    return _stream(
        _tool_event("structurizr_validate", "completed", {"dsl": dsl_text}, VALIDATE_OK_MARKER), _text_event("done")
    )


class TestPhase130CaseRegistry(unittest.TestCase):
    """The Phase 130 cases (Task 130.100): the locked ids, prompts, gate
    set and scenario facts."""

    def test_modeling_decisions_is_registered_and_a_full_case(self) -> None:
        self.assertIs(CASES["modeling-decisions"], MODELING_DECISIONS_CASE_DEF)
        self.assertIn("modeling-decisions", pins.FULL_CASES)
        self.assertEqual(MODELING_DECISIONS_CASE_DEF.gates, MODELING_DECISIONS_GATES)
        self.assertEqual(MODELING_DECISIONS_CASE_DEF.forbidden_element_names, MODELING_DECISIONS_FORBIDDEN_NAMES)
        self.assertEqual(MODELING_DECISIONS_CASE_DEF.expected_container_count, MODELING_DECISIONS_EXPECTED_CONTAINERS)

    def test_heldout_modeling_is_registered_but_not_a_full_case(self) -> None:
        self.assertIs(CASES[pins.HELDOUT_MODELING_CASE], HELDOUT_MODELING_CASE_DEF)
        self.assertNotIn(pins.HELDOUT_MODELING_CASE, pins.FULL_CASES)
        # the same gate family (locked: same task shape, same gates, different domain)
        self.assertEqual(HELDOUT_MODELING_CASE_DEF.gates, MODELING_DECISIONS_GATES)
        self.assertEqual(HELDOUT_MODELING_CASE_DEF.forbidden_element_names, HELDOUT_MODELING_FORBIDDEN_NAMES)
        self.assertEqual(HELDOUT_MODELING_CASE_DEF.expected_container_count, 3)

    def test_modeling_decisions_gate_set_is_the_locked_13(self) -> None:
        self.assertEqual(
            MODELING_DECISIONS_GATES,
            (
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
            ),
        )
        # no loop-discipline gates (locked: they belong to the validate-loop
        # skill and are measured on the create-system-family cases); the
        # create-family `validate_ok_called` gate IS in the set
        for stream_gate in ("parse_called", "inspect_called", "validated_before_return", "triage_complete"):
            self.assertNotIn(stream_gate, MODELING_DECISIONS_GATES)
        self.assertIn("validate_ok_called", MODELING_DECISIONS_GATES)

    def test_modeling_decisions_prompt_is_the_locked_wording(self) -> None:
        self.assertEqual(MODELING_DECISIONS_CASE_DEF.setup_files, {})
        # the prompt names the scenario's facts in business language
        self.assertIn("pricing rules library", MODELING_DECISIONS_PROMPT)
        self.assertIn("email delivery provider", MODELING_DECISIONS_PROMPT)
        self.assertIn("its own database", MODELING_DECISIONS_PROMPT)
        self.assertIn("two application parts", MODELING_DECISIONS_PROMPT)
        # ...and never states the C4 answers
        lowered = MODELING_DECISIONS_PROMPT.lower()
        for answer_word in ("container", "softwaresystem", "component", "external", "person"):
            self.assertNotIn(answer_word, lowered, f"the prompt states a C4 answer: {answer_word}")
        # the create-family tail, naming no tool (the Phase 110 precedent)
        self.assertIn(
            "Before you finish, check with the structurizr MCP tools and fix every error they report.",
            MODELING_DECISIONS_PROMPT,
        )
        for tool_name in ("validate", "parse", "inspect"):
            self.assertNotIn(tool_name, lowered, f"the prompt names a tool: {tool_name}")

    def test_heldout_modeling_prompt_keeps_the_same_task_shape(self) -> None:
        # same shape, different domain (home energy -- not bookshop/hospital/
        # library/parking/museum, per the locked guardrail; the domain words
        # are matched as domain markers, since the scenario's own shared
        # library is named "rates library")
        lowered = HELDOUT_MODELING_PROMPT.lower()
        for domain in ("bookshop", "hospital", "parking", "museum", "library system", "public library"):
            self.assertNotIn(domain, lowered)
        self.assertIn("rates library", HELDOUT_MODELING_PROMPT)
        self.assertIn("smart meter provider", HELDOUT_MODELING_PROMPT)
        self.assertIn(
            "Before you finish, check with the structurizr MCP tools and fix every error they report.",
            HELDOUT_MODELING_PROMPT,
        )
        lowered = HELDOUT_MODELING_PROMPT.lower()
        for answer_word in ("container", "softwaresystem", "component", "external"):
            self.assertNotIn(answer_word, lowered)

    def test_scenario_container_count_is_three(self) -> None:
        # two application parts + the scenario's own database; the library
        # and the third-party service are NOT containers (the C4 answers)
        self.assertEqual(MODELING_DECISIONS_EXPECTED_CONTAINERS, 3)
        self.assertEqual(HELDOUT_MODELING_CASE_DEF.expected_container_count, 3)


class TestPhase130FixtureFilesPresent(unittest.TestCase):
    def test_modeling_fixtures_are_committed_and_consistent(self) -> None:
        for name in ("modeling-good", "modeling-bad", "heldout-modeling-good"):
            dsl = WORKSPACES / name / "workspace.dsl"
            self.assertTrue(dsl.is_file(), f"missing fixture {name}/workspace.dsl")
            self.assertGreaterEqual(len(dsl.read_text(encoding="utf-8").encode("utf-8")), MIN_DSL_BYTES)
            export = WORKSPACES / name / "export.json"
            self.assertTrue(export.is_file(), f"missing fixture {name}/export.json")
            self.assertIn("model", json.loads(export.read_text(encoding="utf-8")))
            validate_txt = WORKSPACES / name / "validate.txt"
            self.assertTrue(validate_txt.is_file(), f"missing fixture {name}/validate.txt")

    def test_modeling_bad_fixture_is_cli_valid(self) -> None:
        # the known-bad reference's defects are SEMANTIC (the wrong modeling
        # decisions), not syntactic: the pinned CLI validates it cleanly
        self.assertEqual((WORKSPACES / "modeling-bad" / "validate.txt").read_text(encoding="utf-8"), "")


class TestIterComponentsQuery(unittest.TestCase):
    def test_no_components_in_the_modeling_fixtures(self) -> None:
        self.assertEqual(iter_components(_load_export("modeling-good")), [])
        self.assertEqual(iter_components(_load_export("modeling-bad")), [])

    def test_components_are_iterated_inside_their_containers(self) -> None:
        export = _mutated_export("modeling-good")
        export["model"]["softwareSystems"][0]["containers"][0].setdefault("components", []).append(
            {"id": 99, "name": "Pricing Rules Library", "description": "Computes prices.", "tags": "Element,Component"}
        )

        result = iter_components(export)

        self.assertEqual([c["name"] for c in result], ["Pricing Rules Library"])


class TestContainerCountGate(unittest.TestCase):
    def test_pass_at_exactly_the_expected_count(self) -> None:
        context = _context(CASES["modeling-decisions"], _modeling_inputs())

        result = gate_container_count(context)

        self.assertTrue(result.passed)
        self.assertIn("exactly 3 container(s)", result.detail)

    def test_fail_when_the_library_is_a_container(self) -> None:
        context = _context(CASES["modeling-decisions"], _modeling_inputs("modeling-bad"))

        result = gate_container_count(context)

        self.assertFalse(result.passed)
        self.assertIn("5 container(s), expected 3", result.detail)
        self.assertIn("'Pricing Rules Library'", result.detail)

    def test_fail_when_the_database_is_not_a_container(self) -> None:
        export = _mutated_export("modeling-good")
        export["model"]["softwareSystems"][0]["containers"] = [
            c for c in export["model"]["softwareSystems"][0]["containers"] if c["name"] != "Shipments Database"
        ]

        result = gate_container_count(_context(CASES["modeling-decisions"], _modeling_inputs_from(export)))

        self.assertFalse(result.passed)
        self.assertIn("2 container(s), expected 3", result.detail)

    def test_edge_gate_misused_on_a_case_without_a_count(self) -> None:
        context = _context(CASES["create-system"], _modeling_inputs())

        result = gate_container_count(context)

        self.assertFalse(result.passed)
        self.assertIn("gate misused", result.detail)


class TestNoLibraryContainerGate(unittest.TestCase):
    def test_pass_when_the_library_is_no_element(self) -> None:
        context = _context(CASES["modeling-decisions"], _modeling_inputs())

        result = gate_no_library_container(context)

        self.assertTrue(result.passed)
        self.assertIn("none of the 1 forbidden element name(s)", result.detail)

    def test_fail_when_the_library_is_a_container(self) -> None:
        context = _context(CASES["modeling-decisions"], _modeling_inputs("modeling-bad"))

        result = gate_no_library_container(context)

        self.assertFalse(result.passed)
        self.assertIn("container 'Pricing Rules Library'", result.detail)

    def test_fail_when_the_library_is_a_component(self) -> None:
        export = _mutated_export("modeling-good")
        export["model"]["softwareSystems"][0]["containers"][0].setdefault("components", []).append(
            {"id": 99, "name": "Pricing Rules Library", "description": "Computes prices.", "tags": "Element,Component"}
        )

        result = gate_no_library_container(_context(CASES["modeling-decisions"], _modeling_inputs_from(export)))

        self.assertFalse(result.passed)
        self.assertIn("component 'Pricing Rules Library'", result.detail)

    def test_pass_for_a_different_name(self) -> None:
        # the gate is a by-name membership test: a renamed library-as-
        # container is this gate's blind spot by design (the scenario names
        # the library, so a conforming agent uses that name), caught instead
        # by the container_count gate
        export = _mutated_export("modeling-good")
        export["model"]["softwareSystems"][0]["containers"][0].setdefault("components", []).append(
            {"id": 99, "name": "Pricing Library", "description": "Computes prices.", "tags": "Element,Component"}
        )

        result = gate_no_library_container(_context(CASES["modeling-decisions"], _modeling_inputs_from(export)))

        self.assertTrue(result.passed)

    def test_edge_gate_misused_on_a_case_without_forbidden_names(self) -> None:
        context = _context(CASES["create-system"], _modeling_inputs())

        result = gate_no_library_container(context)

        self.assertFalse(result.passed)
        self.assertIn("gate misused", result.detail)


class TestExternalSystemTaggedGate(unittest.TestCase):
    def test_pass_for_a_top_level_system_with_the_tag(self) -> None:
        result = gate_external_system_tagged(_modeling_inputs())

        self.assertTrue(result.passed)
        self.assertIn("'Email Delivery Service'", result.detail)

    def test_fail_when_the_provider_is_a_container(self) -> None:
        result = gate_external_system_tagged(_modeling_inputs("modeling-bad"))

        self.assertFalse(result.passed)
        self.assertIn("no top-level softwareSystem or custom element carries the External tag", result.detail)

    def test_pass_for_a_custom_element_with_the_tag(self) -> None:
        # the pinned DSL fact: a top-level `element` (custom element) with
        # the External tag is the other legal shape
        export = _mutated_export("modeling-good")
        provider = next(s for s in export["model"]["softwareSystems"] if s["name"] == "Email Delivery Service")
        export["model"]["softwareSystems"] = [s for s in export["model"]["softwareSystems"] if s is not provider]
        export["model"].setdefault("customElements", []).append(provider)

        result = gate_external_system_tagged(_modeling_inputs_from(export))

        self.assertTrue(result.passed)

    def test_fail_when_the_tag_is_missing(self) -> None:
        export = _mutated_export("modeling-good")
        for system in export["model"]["softwareSystems"]:
            if system["name"] == "Email Delivery Service":
                system["tags"] = system["tags"].replace("External", "").replace(",,", ",").strip(",")

        result = gate_external_system_tagged(_modeling_inputs_from(export))

        self.assertFalse(result.passed)

    def test_the_external_systems_section_is_never_consulted(self) -> None:
        # the pinned DSL has no `externalSystem` keyword, so
        # `model.externalSystems` is never populated by it -- the gate must
        # not look there: a fabricated entry with the tag cannot pass a
        # workspace whose top-level elements carry no tag
        export = _mutated_export("modeling-good")
        for system in export["model"]["softwareSystems"]:
            if system["name"] == "Email Delivery Service":
                system["tags"] = system["tags"].replace("External", "").replace(",,", ",").strip(",")
        export["model"]["externalSystems"] = [{"id": 98, "name": "Ghost Provider", "tags": "External"}]

        result = gate_external_system_tagged(_modeling_inputs_from(export))

        self.assertFalse(result.passed)


class TestNoVagueLabelsGate(unittest.TestCase):
    def test_pass_when_every_label_states_an_intent(self) -> None:
        result = gate_no_vague_labels(_modeling_inputs())

        self.assertTrue(result.passed)
        self.assertIn("5 relationship(s)", result.detail)

    def test_fail_on_the_known_bad_labels(self) -> None:
        result = gate_no_vague_labels(_modeling_inputs("modeling-bad"))

        self.assertFalse(result.passed)
        self.assertIn("'uses'", result.detail)
        self.assertIn("'connects to'", result.detail)

    def test_fail_on_each_forbidden_label(self) -> None:
        for label in sorted(VAGUE_RELATIONSHIP_LABELS):
            export = _mutated_export("modeling-good")
            for person in export["model"]["people"]:
                for rel in person.get("relationships", []):
                    if rel.get("description") == "tracks parcels through":
                        rel["description"] = label

            result = gate_no_vague_labels(_modeling_inputs_from(export))

            self.assertFalse(result.passed, label)
            self.assertIn(f"'{label}'", result.detail, label)

    def test_the_test_is_case_insensitive_and_trimmed(self) -> None:
        export = _mutated_export("modeling-good")
        for person in export["model"]["people"]:
            for rel in person.get("relationships", []):
                if rel.get("description") == "tracks parcels through":
                    rel["description"] = "  USES  "

        result = gate_no_vague_labels(_modeling_inputs_from(export))

        self.assertFalse(result.passed)

    def test_a_specific_label_containing_a_forbidden_word_passes(self) -> None:
        # membership, not substring: "user uses the portal to track parcels"
        # states an intent and is not a member of the forbidden set
        export = _mutated_export("modeling-good")
        for person in export["model"]["people"]:
            for rel in person.get("relationships", []):
                if rel.get("description") == "tracks parcels through":
                    rel["description"] = "uses the portal to track parcels"

        result = gate_no_vague_labels(_modeling_inputs_from(export))

        self.assertTrue(result.passed)

    def test_edge_fail_without_relationships(self) -> None:
        inputs = _minimal_inputs(None, export_json={"model": {}})

        result = gate_no_vague_labels(inputs)

        self.assertFalse(result.passed)
        self.assertIn("no relationships", result.detail)


class TestPhase130EndToEnd(unittest.TestCase):
    """The locked `modeling-decisions`/`heldout-modeling` gate sets over the
    committed references (ACC-006: the known-good reference passes every
    gate, the known-bad reference fails exactly the decision gates -- no
    model call, no Docker; the stream half is the minimal validate-OK
    shape a CREATE case produces)."""

    def test_modeling_good_reference_passes_all_13_gates(self) -> None:
        case = CASES["modeling-decisions"]
        inputs = _modeling_inputs()
        trial = _validate_ok_stream(inputs.dsl_text)
        context = _context(case, inputs, trial=trial)

        results = grade_case(context)

        self.assertEqual(len(results), 13)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_heldout_modeling_good_reference_passes_all_13_gates(self) -> None:
        case = CASES[pins.HELDOUT_MODELING_CASE]
        inputs = _modeling_inputs("heldout-modeling-good")
        trial = _validate_ok_stream(inputs.dsl_text)
        context = _context(case, inputs, trial=trial)

        results = grade_case(context)

        self.assertEqual(len(results), 13)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_modeling_bad_reference_fails_exactly_the_decision_gates(self) -> None:
        case = CASES["modeling-decisions"]
        inputs = _modeling_inputs("modeling-bad")
        trial = _validate_ok_stream(inputs.dsl_text)
        context = _context(case, inputs, trial=trial)

        results = grade_case(context)
        by_name = {r.name: r for r in results}

        self.assertEqual(
            sorted(r.name for r in results if not r.passed),
            ["container_count", "external_system_tagged", "no_library_container", "no_vague_labels"],
        )
        for shape_gate in (
            "dsl_written",
            "cli_valid",
            "cli_export",
            "has_system",
            "has_person",
            "relationship_technology",
            "elements_described",
            "has_view",
            "validate_ok_called",
        ):
            self.assertTrue(by_name[shape_gate].passed, shape_gate)
        self.assertFalse(case_passed(results))


# ---------------------------------------------------------------------------
# Phase 140 (Task 140.100): the design-views case and its gates
# ---------------------------------------------------------------------------

DESIGN_VIEWS_FORBIDDEN_PROMPT_WORDS: tuple[str, ...] = (
    # the view-design answers (the skill's delta -- never in the prompt)
    "view",
    "diagram",
    "split",
    "crowded",
    "readable",
    "include",
    "layout",
    "key",
    # the C4 modeling answers (the Phase 130 precedent)
    "container",
    "softwaresystem",
    "component",
    "external",
    "person",
)


def _views_inputs(export_name: str) -> GraderInputs:
    return _inputs(export_name, validate_rc=0, export_rc=0)


def _views_inputs_from(export: dict, export_name: str = "views-good") -> GraderInputs:
    dsl = (WORKSPACES / export_name / "workspace.dsl").read_text(encoding="utf-8")
    return GraderInputs(
        dsl_path="workspace.dsl",
        dsl_text=dsl,
        validate_rc=0,
        validate_stderr="",
        export_json=export,
        export_rc=0,
        export_stderr="",
        inspect_rc=0,
        inspect_findings=[],
    )


def _synthetic_export(views: dict) -> dict:
    """A minimal export JSON carrying only the given `views` section."""
    result = {
        "model": {"people": [], "softwareSystems": [], "customElements": []},
        "views": views,
    }
    return result


class TestPhase140CaseRegistry(unittest.TestCase):
    """The Phase 140 cases (Task 140.100): the locked ids, prompts, gate
    set and scenario facts."""

    def test_design_views_is_registered_and_a_full_case(self) -> None:
        self.assertIs(CASES["design-views"], DESIGN_VIEWS_CASE_DEF)
        self.assertIn("design-views", pins.FULL_CASES)
        self.assertEqual(DESIGN_VIEWS_CASE_DEF.gates, DESIGN_VIEWS_GATES)

    def test_heldout_views_is_registered_but_not_a_full_case(self) -> None:
        self.assertIs(CASES[pins.HELDOUT_VIEWS_CASE], HELDOUT_VIEWS_CASE_DEF)
        self.assertNotIn(pins.HELDOUT_VIEWS_CASE, pins.FULL_CASES)
        # the same gate family (locked: same task shape, same gates, different domain)
        self.assertEqual(HELDOUT_VIEWS_CASE_DEF.gates, DESIGN_VIEWS_GATES)

    def test_design_views_gate_set_is_the_locked_12(self) -> None:
        self.assertEqual(
            DESIGN_VIEWS_GATES,
            (
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
            ),
        )
        # no loop-discipline gates (locked: they belong to the validate-loop
        # skill; this skill's delta is the view design); the create-family
        # `validate_ok_called` gate IS in the set (the prompt carries the
        # tool-nameless "check with the structurizr MCP tools" tail)
        for stream_gate in ("parse_called", "inspect_called", "validated_before_return", "triage_complete"):
            self.assertNotIn(stream_gate, DESIGN_VIEWS_GATES)
        self.assertIn("validate_ok_called", DESIGN_VIEWS_GATES)

    def test_design_views_prompt_is_the_locked_wording(self) -> None:
        self.assertEqual(DESIGN_VIEWS_CASE_DEF.setup_files, {})
        # the create-family tail, naming no tool (the Phase 110/130 precedent)
        self.assertIn(
            "Before you finish, check with the structurizr MCP tools and fix every error they report.",
            DESIGN_VIEWS_PROMPT,
        )
        lowered = DESIGN_VIEWS_PROMPT.lower()
        for tool_name in ("validate", "parse", "inspect"):
            self.assertNotIn(tool_name, lowered, f"the prompt names a tool: {tool_name}")
        # the scenario facts in plain business language
        self.assertIn("Bank Portal system", DESIGN_VIEWS_PROMPT)
        self.assertIn("card payment network", DESIGN_VIEWS_PROMPT)
        self.assertIn("credit reference agency", DESIGN_VIEWS_PROMPT)
        # ...and never the view-design answers or the C4 answers
        for answer_word in DESIGN_VIEWS_FORBIDDEN_PROMPT_WORDS:
            self.assertNotIn(answer_word, lowered, f"the prompt states an answer: {answer_word}")

    def test_design_views_scenario_has_more_than_20_elements(self) -> None:
        # one person role + one owned system + 19 application parts + two
        # third-party services = 23 elements, so a single `include *`
        # container view necessarily carries 22 (19 + person + 2 externals)
        # -- over the locked 20-element bound
        self.assertEqual(
            len(re.findall(r"^  - ", DESIGN_VIEWS_PROMPT, re.MULTILINE)), 19, "the scenario names 19 application parts"
        )
        self.assertEqual(DESIGN_VIEWS_PROMPT.count("operated by a different organization"), 2)

    def test_heldout_views_prompt_keeps_the_same_task_shape(self) -> None:
        # same shape, different domain (insurance claims -- not any earlier
        # phase's domain, per the locked guardrail)
        lowered = HELDOUT_VIEWS_PROMPT.lower()
        for domain in (
            "bookshop",
            "hospital",
            "library",
            "parking",
            "museum",
            "parcel",
            "home energy",
            "banking",
            "bank portal",
        ):
            self.assertNotIn(domain, lowered, f"the held-out prompt reuses an earlier domain: {domain}")
        # the held-out scenario's own facts
        self.assertIn("Claims Center system", HELDOUT_VIEWS_PROMPT)
        self.assertIn("national claims data bureau", HELDOUT_VIEWS_PROMPT)
        self.assertIn("clearing house", HELDOUT_VIEWS_PROMPT)
        self.assertEqual(
            len(re.findall(r"^  - ", HELDOUT_VIEWS_PROMPT, re.MULTILINE)), 19, "the scenario names 19 application parts"
        )
        self.assertEqual(HELDOUT_VIEWS_PROMPT.count("operated by a different organization"), 2)
        self.assertIn(
            "Before you finish, check with the structurizr MCP tools and fix every error they report.",
            HELDOUT_VIEWS_PROMPT,
        )
        for answer_word in DESIGN_VIEWS_FORBIDDEN_PROMPT_WORDS:
            self.assertNotIn(answer_word, lowered, f"the prompt states an answer: {answer_word}")


class TestPhase140FixtureFilesPresent(unittest.TestCase):
    def test_views_fixtures_are_committed_and_consistent(self) -> None:
        for name in ("views-good", "views-bad", "heldout-views-good"):
            dsl = WORKSPACES / name / "workspace.dsl"
            self.assertTrue(dsl.is_file(), f"missing fixture {name}/workspace.dsl")
            self.assertGreaterEqual(len(dsl.read_text(encoding="utf-8").encode("utf-8")), MIN_DSL_BYTES)
            export = WORKSPACES / name / "export.json"
            self.assertTrue(export.is_file(), f"missing fixture {name}/export.json")
            self.assertIn("model", json.loads(export.read_text(encoding="utf-8")))
            validate_txt = WORKSPACES / name / "validate.txt"
            self.assertTrue(validate_txt.is_file(), f"missing fixture {name}/validate.txt")

    def test_views_bad_fixture_is_cli_valid(self) -> None:
        # the known-bad reference's defects are SEMANTIC (the wrong view
        # design), not syntactic: the pinned CLI validates it cleanly
        self.assertEqual((WORKSPACES / "views-bad" / "validate.txt").read_text(encoding="utf-8"), "")

    def test_views_good_fixture_carries_the_split_view_design(self) -> None:
        export = _load_export("views-good")
        assert export is not None
        views = iter_views(export)
        self.assertEqual(len(views), 4)
        self.assertTrue(all(not v.get("generatedKey") for v in views))
        for view in views:
            self.assertLessEqual(len(view.get("elements") or []), VIEW_ELEMENT_BOUND)

    def test_views_bad_fixture_carries_both_view_defect_classes(self) -> None:
        export = _load_export("views-bad")
        assert export is not None
        views = iter_views(export)
        self.assertEqual(len(views), 3)
        # an explicit-key view over the bound ...
        over = [v for v in views if not v.get("generatedKey") and len(v.get("elements") or []) > VIEW_ELEMENT_BOUND]
        self.assertEqual([v["key"] for v in over], ["AllContainers"])
        # ... and a keyless view (auto-generated key, the `generatedKey` mark)
        generated = [v for v in views if v.get("generatedKey")]
        self.assertEqual([v["key"] for v in generated], ["Container-001"])


class TestViewElementScopingFacts(unittest.TestCase):
    """The pinned exporter's element-scoping facts (verified against the
    pinned CLI, Task 140.100) as the gates rely on them."""

    def test_include_star_counts_containers_plus_linked_elements_not_the_system(self) -> None:
        # the views-bad `AllContainers` view (`include *` over 19
        # containers): the element list is the 19 containers + the linked
        # person + the two linked external software systems = 22; the
        # scoped system itself is NOT in the list (the view references it
        # by its own `softwareSystemId`)
        export = _load_export("views-bad")
        assert export is not None
        all_containers = next(v for v in iter_views(export) if v.get("key") == "AllContainers")
        self.assertEqual(len(all_containers["elements"]), 22)
        self.assertIn("softwareSystemId", all_containers)
        system_id = str(all_containers["softwareSystemId"])
        self.assertNotIn(system_id, [str(e["id"]) for e in all_containers["elements"]])

    def test_an_explicit_include_list_counts_exactly_the_listed_elements(self) -> None:
        export = _load_export("views-good")
        assert export is not None
        front_office = next(v for v in iter_views(export) if v.get("key") == "FrontOffice")
        # customer + web + mobile + accounts + transactions + payments +
        # notifications + cache = 8, nothing else
        self.assertEqual(len(front_office["elements"]), 8)

    def test_a_filtered_view_carries_no_elements_list_of_its_own(self) -> None:
        # the pinned exporter writes a filtered view as `baseViewKey` +
        # `mode` + `tags` (no `elements` array): the gate bounds it by its
        # base's count (`_view_element_count`)
        export = _synthetic_export(
            {
                "containerViews": [
                    {"key": "Big", "elements": [{"id": i} for i in range(21)]},
                    {"key": "Small", "elements": [{"id": i} for i in range(3)]},
                ],
                "filteredViews": [
                    {"key": "MyFiltered", "baseViewKey": "Big", "mode": "Include", "tags": ["X"]},
                ],
            }
        )
        inputs = _views_inputs_from(export)

        result = gate_views_within_element_bound(inputs)

        self.assertFalse(result.passed)
        # `Big` itself is over; `MyFiltered` resolves through its base
        self.assertIn("'Big' with 21 element(s)", result.detail)
        self.assertIn("'MyFiltered' with 21 element(s)", result.detail)

    def test_the_filtered_base_resolution_is_recursive_and_cycle_guarded(self) -> None:
        export = _synthetic_export(
            {
                "containerViews": [
                    {"key": "Root", "elements": [{"id": i} for i in range(21)]},
                ],
                "filteredViews": [
                    {"key": "F1", "baseViewKey": "Root"},
                    {"key": "F2", "baseViewKey": "F1"},
                    {"key": "LoopA", "baseViewKey": "LoopB"},
                    {"key": "LoopB", "baseViewKey": "LoopA"},
                ],
            }
        )
        inputs = _views_inputs_from(export)

        result = gate_views_within_element_bound(inputs)

        # Root + F1 + F2 resolve to 21; the pathological LoopA/LoopB pair
        # terminates (cycle guard) instead of recursing forever and
        # resolves to 0 -- not flagged over the bound
        self.assertFalse(result.passed)
        self.assertEqual(result.detail.count("with 21 element(s)"), 3)
        self.assertNotIn("LoopA", result.detail)
        self.assertNotIn("LoopB", result.detail)


class TestViewsWithinElementBoundGate(unittest.TestCase):
    def test_pass_when_every_user_defined_view_is_within_the_bound(self) -> None:
        result = gate_views_within_element_bound(_views_inputs("views-good"))

        self.assertTrue(result.passed)
        self.assertIn("every one of 4 user-defined view(s) carries at most 20 element(s)", result.detail)

    def test_fail_when_a_view_exceeds_the_bound(self) -> None:
        result = gate_views_within_element_bound(_views_inputs("views-bad"))

        self.assertFalse(result.passed)
        self.assertIn("'AllContainers' with 22 element(s)", result.detail)

    def test_fail_at_one_over_the_bound_and_pass_at_exactly_the_bound(self) -> None:
        export = _load_export("views-good")
        assert export is not None
        # grow the CustomerContext view (4 elements) to exactly 20 -> pass
        context_view = next(v for v in iter_views(export) if v.get("key") == "CustomerContext")
        for i in range(16):
            context_view["elements"].append({"id": 100 + i})

        at_bound = gate_views_within_element_bound(_views_inputs_from(copy.deepcopy(export)))

        self.assertTrue(at_bound.passed)
        self.assertIn("at most 20 element(s)", at_bound.detail)
        # one more -> 21 -> fail
        context_view["elements"].append({"id": 200})

        over = gate_views_within_element_bound(_views_inputs_from(copy.deepcopy(export)))

        self.assertFalse(over.passed)
        self.assertIn("'CustomerContext' with 21 element(s)", over.detail)

    def test_pass_vacuously_without_user_defined_views(self) -> None:
        # the `weak` fixture defines no views: the exporter's auto-generated
        # `generatedKey` defaults are filtered out (the `has_view` precedent
        # carries the presence requirement)
        result = gate_views_within_element_bound(_inputs("weak", validate_rc=0, export_rc=0))

        self.assertTrue(result.passed)
        self.assertIn("vacuously within the bound", result.detail)

    def test_a_keyless_crowded_view_is_not_bound_checked(self) -> None:
        # the locked complementarity: a view the DSL wrote without a key
        # exports under `generatedKey: true` and is filtered out of the
        # bound check (it fails `explicit_view_keys` instead) -- the
        # views-bad `Container-001` view carries 22 elements but is not
        # named in the bound gate's failure
        result = gate_views_within_element_bound(_views_inputs("views-bad"))

        self.assertFalse(result.passed)
        self.assertNotIn("Container-001", result.detail)
        self.assertIn("1 of 2 user-defined view(s)", result.detail)

    def test_edge_fail_without_an_export_json(self) -> None:
        result = gate_views_within_element_bound(_minimal_inputs('workspace "X" "y" { model { } }'))

        self.assertTrue(result.passed)
        self.assertIn("vacuously within the bound", result.detail)


class TestExplicitViewKeysGate(unittest.TestCase):
    def test_pass_when_every_view_has_an_explicit_key(self) -> None:
        result = gate_explicit_view_keys(_views_inputs("views-good"))

        self.assertTrue(result.passed)
        self.assertIn("every one of 4 view(s) has an explicit key", result.detail)

    def test_fail_when_a_view_key_was_auto_generated(self) -> None:
        result = gate_explicit_view_keys(_views_inputs("views-bad"))

        self.assertFalse(result.passed)
        self.assertIn("1 of 3 view(s) carry an auto-generated key", result.detail)
        self.assertIn("['Container-001']", result.detail)

    def test_fail_when_the_dsl_defines_no_views_at_all(self) -> None:
        # the `weak` fixture: only the exporter's auto-generated default
        # views exist, every one carrying the `generatedKey` mark
        result = gate_explicit_view_keys(_inputs("weak", validate_rc=0, export_rc=0))

        self.assertFalse(result.passed)
        self.assertIn("3 of 3 view(s) carry an auto-generated key", result.detail)
        for key in ("Container-001", "SystemContext-001", "SystemLandscape-001"):
            self.assertIn(key, result.detail)

    def test_edge_fail_without_any_views_in_the_export(self) -> None:
        inputs = _minimal_inputs('workspace "X" "y" { model { } }', export_json={"views": {}})

        result = gate_explicit_view_keys(inputs)

        self.assertFalse(result.passed)
        self.assertIn("no views at all", result.detail)


class TestPhase140EndToEnd(unittest.TestCase):
    """The locked `design-views`/`heldout-views` gate sets over the
    committed references (ACC-006: the known-good reference passes every
    gate, the known-bad reference fails exactly the two new view-design
    gates -- no model call, no Docker; the stream half is the minimal
    validate-OK shape a CREATE case produces)."""

    def test_views_good_reference_passes_all_12_gates(self) -> None:
        case = CASES["design-views"]
        inputs = _views_inputs("views-good")
        trial = _validate_ok_stream(inputs.dsl_text)
        context = _context(case, inputs, trial=trial)

        results = grade_case(context)

        self.assertEqual(len(results), 12)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_heldout_views_good_reference_passes_all_12_gates(self) -> None:
        case = CASES[pins.HELDOUT_VIEWS_CASE]
        inputs = _views_inputs("heldout-views-good")
        trial = _validate_ok_stream(inputs.dsl_text)
        context = _context(case, inputs, trial=trial)

        results = grade_case(context)

        self.assertEqual(len(results), 12)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_views_bad_reference_fails_exactly_the_view_design_gates(self) -> None:
        case = CASES["design-views"]
        inputs = _views_inputs("views-bad")
        trial = _validate_ok_stream(inputs.dsl_text)
        context = _context(case, inputs, trial=trial)

        results = grade_case(context)
        by_name = {r.name: r for r in results}

        self.assertEqual(
            sorted(r.name for r in results if not r.passed),
            ["explicit_view_keys", "views_within_element_bound"],
        )
        for shape_gate in (
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
        ):
            self.assertTrue(by_name[shape_gate].passed, shape_gate)
        self.assertFalse(case_passed(results))


if __name__ == "__main__":
    unittest.main()
