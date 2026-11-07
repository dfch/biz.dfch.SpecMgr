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

import json
import unittest

from c4_skills import pins
from c4_skills.cases import (
    CASES,
    CREATE_SYSTEM_GATES,
    MCP_LIMITS_GATES,
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
    case_passed,
    grade_case,
    iter_containers,
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


def _inputs(name: str, validate_rc: int, export_rc: int) -> GraderInputs:
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
        inspect_rc=None,
        inspect_findings=[],
    )


def _minimal_inputs(
    dsl_text: str | None,
    export_json: dict | None = None,
    inspect_findings: list[str] | None = None,
) -> GraderInputs:
    """Build a GraderInputs from plain text (no fixture file, no CLI)."""
    return GraderInputs(
        dsl_path="workspace.dsl" if dsl_text is not None else None,
        dsl_text=dsl_text,
        validate_rc=0 if dsl_text is not None else None,
        validate_stderr="",
        export_json=export_json,
        export_rc=0 if export_json is not None else None,
        export_stderr="",
        inspect_rc=0 if dsl_text is not None else None,
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
        inputs = _inputs("good", validate_rc=0, export_rc=0)
        context = _context(case, inputs, trial=_loop_parsed())

        results = grade_case(context)

        self.assertEqual(len(results), 13)
        self.assertTrue(case_passed(results), [(r.name, r.detail) for r in results if not r.passed])

    def test_mcp_limits_passes_all_14_gates(self) -> None:
        case = CASES["mcp-limits"]
        inputs = _inputs("good", validate_rc=0, export_rc=0)
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
        context = _context(case, _minimal_inputs(None), trial=_loop_parsed())

        result = _gate("triage_complete", context)

        # the fixture: 2 expected (MCP limits) + 2 fix (post-inspect edit)
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
        context = _context(self.case, _minimal_inputs(None), trial=parse_events_file(self.CODEMODE_STREAM))

        result = _gate("triage_complete", context)

        # the fixture: 1 expected (MCP limits) + 1 fix (post-inspect edit)
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
        context = _context(case, _minimal_inputs(None), trial=_stream(_text_event("Done.")))

        result = _gate("mcp_limit_stated", context)

        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
