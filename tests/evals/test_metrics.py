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

"""Metrics tests (Task 100.140 / Task 100.160; Code Mode detection, Phase 110).

All fixtures are committed files (the synthetic event streams plus the
pre-exported workspace JSON); no model call, no Docker.

The Phase 110 locked harness fix rewires the stream-derived metrics over
the normalized MCP-call view (`metrics.normalized_mcp_calls`): native
`tool_use` calls count exactly as before, and Code Mode `execute` blocks
(`tools.structurizr.<tool>({...})` JavaScript -- the only remote-MCP
access path of the pinned opencode 2.2.5 image) count under the locked
conservative rules of `c4_skills.codemode`. The regression tests here
prove that native-only streams produce byte-identical metrics to before
the fix.
"""

import json
import unittest
from pathlib import Path

from c4_skills.cases import CASES
from c4_skills.codemode import FAMILY_EXPORT
from c4_skills.events import ParsedTrial, parse_event_stream, parse_events_file
from c4_skills.graders import GateContext, GraderInputs, grade_case, parse_inspect_findings
from c4_skills.metrics import (
    EDIT_TOOL_NAMES,
    SOURCE_CODEMODE,
    SOURCE_NATIVE,
    TRIAGE_EXPECTED,
    TRIAGE_FIX,
    TRIAGE_REPORTED,
    TRIAGE_UNTRIAGED,
    _edited_after_inspect,
    _findings_from_output,
    compute_metrics,
    extract_final_dsl,
    final_inspect_findings_set,
    normalized_mcp_calls,
    normalize_finding,
    triage_findings,
    validated_texts,
)

from .conftest import FIXTURES_DIR


def _tool_stream() -> str:
    return (FIXTURES_DIR / "events" / "tool-stream.ndjson").read_text(encoding="utf-8")


def _validated_dsl() -> str:
    lines = _tool_stream().splitlines()
    for line in lines:
        event = json.loads(line)
        part = event.get("part") or {}
        if part.get("type") == "tool" and part.get("tool") == "structurizr_validate":
            return part["state"]["input"]["dsl"]
    raise AssertionError("no validate call in the fixture")


def _good_export() -> dict:
    return json.loads((FIXTURES_DIR / "workspaces" / "good" / "export.json").read_text(encoding="utf-8"))


def _inputs(
    dsl_text: str | None,
    export_json: dict | None,
    inspect_rc: int | None = 0,
    inspect_findings: list[str] | None = None,
) -> GraderInputs:
    return GraderInputs(
        dsl_path="workspace.dsl" if dsl_text is not None else None,
        dsl_text=dsl_text,
        validate_rc=0 if dsl_text is not None else 1,
        validate_stderr="" if dsl_text is not None else "boom",
        export_json=export_json,
        export_rc=0 if export_json is not None else 1,
        export_stderr="" if export_json is not None else "boom",
        inspect_rc=inspect_rc,
        inspect_findings=list(inspect_findings or []),
    )


class TestValidatedBeforeReturn(unittest.TestCase):
    def test_file_matches_validated_text(self) -> None:
        parsed = parse_events_file(FIXTURES_DIR / "events" / "tool-stream.ndjson")
        inputs = _inputs(_validated_dsl(), _good_export())

        sut = compute_metrics(parsed, inputs)

        self.assertTrue(sut.validated_before_return)
        self.assertTrue(sut.validated_by_file)
        self.assertTrue(sut.validated_by_final_text)

    def test_file_differs_from_validated_text_but_final_text_matches(self) -> None:
        # the on-disk file drifted after validation, but the final message
        # still returns the exact validated text: the metric holds via the
        # final-text sub-check (the sub-checks are reported separately)
        parsed = parse_events_file(FIXTURES_DIR / "events" / "tool-stream.ndjson")
        drifted = _validated_dsl().replace("A small online bookshop.", "A different description.")
        inputs = _inputs(drifted, _good_export())

        sut = compute_metrics(parsed, inputs)

        self.assertTrue(sut.validated_before_return)
        self.assertFalse(sut.validated_by_file)
        self.assertTrue(sut.validated_by_final_text)

    def test_final_text_differs_from_validated_text(self) -> None:
        from c4_skills.events import parse_event_stream

        drifted_final = 'Done.\n\n```dsl\nworkspace "Bookshop" "A different description." { model { } }\n```\n'
        event = {
            "type": "text",
            "part": {"type": "text", "text": drifted_final},
        }
        parsed = parse_event_stream([json.dumps(event)])
        inputs = _inputs(None, None)

        sut = compute_metrics(parsed, inputs)

        self.assertFalse(sut.validated_before_return)
        self.assertFalse(sut.validated_by_final_text)

    def test_no_validate_call_at_all(self) -> None:
        from c4_skills.events import ParsedTrial

        inputs = _inputs('workspace "X" "y" { model { } }', None)

        sut = compute_metrics(ParsedTrial(), inputs)

        self.assertFalse(sut.validated_before_return)
        self.assertEqual(sut.validate_calls, 0)

    def test_failed_validate_output_is_not_ok(self) -> None:
        from c4_skills.events import parse_event_stream

        event = {
            "type": "tool",
            "part": {
                "type": "tool",
                "tool": "structurizr_validate",
                "state": {
                    "status": "completed",
                    "input": {"dsl": "workspace X {"},
                    "output": "Unexpected end of DSL content",
                    "time": {"start": 1, "end": 2},
                },
            },
        }
        lines = [json.dumps(event)]
        parsed = parse_event_stream(lines)
        inputs = _inputs("workspace X {", None)

        sut = compute_metrics(parsed, inputs)

        self.assertEqual(sut.validate_calls, 1)
        self.assertEqual(sut.validate_ok_calls, 0)
        self.assertFalse(sut.validated_before_return)


class TestCallCountsAndSkills(unittest.TestCase):
    def test_mcp_tool_call_counts_and_skill_loading(self) -> None:
        parsed = parse_events_file(FIXTURES_DIR / "events" / "tool-stream.ndjson")
        inputs = _inputs(_validated_dsl(), _good_export())

        sut = compute_metrics(parsed, inputs)

        self.assertEqual(sut.parse_calls, 1)
        self.assertEqual(sut.validate_calls, 1)
        self.assertEqual(sut.inspect_calls, 1)
        self.assertEqual(sut.export_calls, 0)
        self.assertEqual(sut.skills_loaded, ["c4-model"])
        self.assertEqual(sut.steps, 1)
        self.assertEqual(sut.tool_calls, 4)

    def test_skill_input_name_key_is_the_fallback(self) -> None:
        from c4_skills.events import parse_event_stream

        event = {
            "type": "tool",
            "part": {
                "type": "tool",
                "tool": "skill",
                "state": {"status": "completed", "input": {"name": "legacy-skill"}, "output": "loaded"},
            },
        }
        parsed = parse_event_stream([json.dumps(event)])
        inputs = _inputs(None, None)

        sut = compute_metrics

        result = sut(parsed, inputs)

        self.assertEqual(result.skills_loaded, ["legacy-skill"])

    def test_relationship_coverage_comes_from_the_export_json(self) -> None:
        parsed = parse_events_file(FIXTURES_DIR / "events" / "tool-stream.ndjson")
        inputs = _inputs(_validated_dsl(), _good_export())

        sut = compute_metrics(parsed, inputs)

        self.assertEqual(sut.relationship_technology_coverage, 1.0)


class TestInspectTriage(unittest.TestCase):
    def test_mcp_limit_findings_are_expected_the_rest_untriaged(self) -> None:
        parsed = parse_events_file(FIXTURES_DIR / "events" / "tool-stream.ndjson")
        inputs = _inputs(_validated_dsl(), _good_export())

        sut = compute_metrics(parsed, inputs)

        self.assertEqual(len(sut.inspect_findings), 3)
        triage = sut.inspect_triage
        expected_count = sum(1 for label in triage.values() if label == TRIAGE_EXPECTED)
        untriaged_count = sum(1 for label in triage.values() if label == TRIAGE_UNTRIAGED)
        self.assertEqual(expected_count, 2)
        self.assertEqual(untriaged_count, 1)
        for finding, label in triage.items():
            if "views" in finding:
                self.assertEqual(label, TRIAGE_UNTRIAGED)
            else:
                self.assertEqual(label, TRIAGE_EXPECTED)

    def test_no_findings_no_triage(self) -> None:
        from c4_skills.events import ParsedTrial

        inputs = _inputs('workspace "X" "y" { model { } }', None)

        sut = compute_metrics(ParsedTrial(), inputs)

        self.assertEqual(sut.inspect_findings, [])
        self.assertEqual(sut.inspect_triage, {})


class TestEditToolNames(unittest.TestCase):
    """I6: the `fix` triage signal counts the command-execution tools too.

    The committed smoke streams show agents mutating files through the
    pinned opencode image's command tools `shell` (a `command` input) and
    `execute` (a `code` input), not only through `edit`/`write`.
    """

    def _stream_after_inspect(self, tool_name: str) -> ParsedTrial:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "structurizr_inspect",
                    "state": {
                        "status": "completed",
                        "output": '["ERROR: the container named Web Store is not included on any views"]',
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": tool_name,
                    "state": {
                        "status": "completed",
                        "input": {"command": "sed -i s/old/new/ workspace.dsl"}
                        if tool_name == "shell"
                        else {"code": "process.exit(0)"},
                        "output": "",
                    },
                },
            },
        ]
        return parse_event_stream([json.dumps(event) for event in events])

    def test_shell_call_after_inspect_is_a_fix(self) -> None:
        parsed = self._stream_after_inspect("shell")
        inputs = _inputs('workspace "X" "y" { model { } }', None)

        result = compute_metrics(parsed, inputs)

        finding = "ERROR: the container named Web Store is not included on any views"
        self.assertEqual(result.inspect_triage, {finding: TRIAGE_FIX})

    def test_execute_call_after_inspect_is_a_fix(self) -> None:
        parsed = self._stream_after_inspect("execute")
        inputs = _inputs('workspace "X" "y" { model { } }', None)

        result = compute_metrics(parsed, inputs)

        finding = "ERROR: the container named Web Store is not included on any views"
        self.assertEqual(result.inspect_triage, {finding: TRIAGE_FIX})

    def test_read_only_tools_do_not_count_as_edits(self) -> None:
        self.assertNotIn("read", EDIT_TOOL_NAMES)
        self.assertNotIn("skill", EDIT_TOOL_NAMES)

    def test_command_execution_tools_are_in_the_edit_set(self) -> None:
        for name in ("shell", "execute", "edit", "write"):
            self.assertIn(name, EDIT_TOOL_NAMES)


class TestFinalDslExtraction(unittest.TestCase):
    def test_last_fenced_block_with_workspace_keyword_wins(self) -> None:
        text = (
            'intro\n```dsl\nworkspace "A" "a" { model { } }\n```\nmore\n```text\nworkspace "B" "b" { model { } }\n```'
        )

        sut = extract_final_dsl

        result = sut(text)

        # verbatim: the fenced capture keeps its trailing newline
        self.assertEqual(result, 'workspace "B" "b" { model { } }\n')

    def test_no_candidate_returns_none(self) -> None:
        sut = extract_final_dsl

        result = sut("no dsl here")

        self.assertIsNone(result)

    def test_unfenced_workspace_text_is_a_candidate(self) -> None:
        text = 'workspace "A" "a" { model { } }'

        sut = extract_final_dsl

        result = sut(text)

        self.assertEqual(result, text)


class TestNormalizedMcpCalls(unittest.TestCase):
    """The normalized MCP-call view: native parity + Code Mode detection."""

    def test_native_only_stream_view_is_all_native(self) -> None:
        # the Phase 110 loop fixture: one error parse, two OK validates,
        # one inspect (plus non-MCP calls the view must not include)
        parsed = parse_events_file(FIXTURES_DIR / "events" / "validate-loop.ndjson")

        view = normalized_mcp_calls(parsed)

        rows = [(entry.position, entry.source, entry.family, entry.status, entry.ok) for entry in view]
        self.assertEqual(
            rows,
            [
                (2, SOURCE_NATIVE, "parse", "error", False),
                (4, SOURCE_NATIVE, "validate", "completed", True),
                (5, SOURCE_NATIVE, "inspect", "completed", False),
                (7, SOURCE_NATIVE, "validate", "completed", True),
            ],
        )
        self.assertEqual({entry.source for entry in view}, {SOURCE_NATIVE})

    def test_native_ok_check_stays_strict(self) -> None:
        event = {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "tool": "structurizr_validate",
                "state": {"status": "completed", "input": {"dsl": "x"}, "output": '{"validation": "OK"}'},
            },
        }
        parsed = parse_event_stream([json.dumps(event)])

        view = normalized_mcp_calls(parsed)

        self.assertEqual(len(view), 1)
        self.assertFalse(view[0].ok)
        self.assertEqual(validated_texts(parsed), set())

    def test_pending_and_non_terminal_calls_are_excluded(self) -> None:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "structurizr_parse",
                    "state": {"status": "pending", "input": {"dsl": "x"}},
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "execute",
                    "state": {"status": "pending", "input": {"code": "tools.structurizr.parse({ dsl: 'x' });"}},
                },
            },
        ]
        parsed = parse_event_stream([json.dumps(event) for event in events])

        self.assertEqual(normalized_mcp_calls(parsed), [])

    def test_execute_without_a_code_input_is_ignored(self) -> None:
        event = {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "tool": "execute",
                "state": {"status": "completed", "input": {"command": "echo hi"}, "output": "hi"},
            },
        }
        parsed = parse_event_stream([json.dumps(event)])

        self.assertEqual(normalized_mcp_calls(parsed), [])

    def test_hyphenated_export_reference_counts_for_the_export_family(self) -> None:
        code = "const r = await tools.structurizr.export-plantuml({ dsl: 'x', viewKey: 'SC' });\n"
        event = {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "tool": "execute",
                "state": {"status": "completed", "input": {"code": code}, "output": "@startuml\n@enduml"},
            },
        }
        parsed = parse_event_stream([json.dumps(event)])

        view = normalized_mcp_calls(parsed)

        self.assertEqual(len(view), 1)
        self.assertEqual(view[0].family, FAMILY_EXPORT)
        self.assertEqual(view[0].source, SOURCE_CODEMODE)
        self.assertEqual(view[0].tool, "export-plantuml")

    def test_codemode_inspect_participates_in_the_call_order(self) -> None:
        # a Code Mode inspect at an earlier position than a later native
        # edit call: the `fix` triage signal must see the Code Mode position
        inspect_code = "const dsl = `x`;\nconst f = await tools.structurizr.inspect({ dsl });\nreturn f;\n"
        events = [
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "execute",
                    "state": {
                        "status": "completed",
                        "input": {"code": inspect_code},
                        "output": '["ERROR: the container named Web Store is not included on any views"]',
                    },
                },
            },
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "write",
                    "state": {"status": "completed", "input": {"filePath": "workspace.dsl"}, "output": "wrote"},
                },
            },
        ]
        parsed = parse_event_stream([json.dumps(event) for event in events])
        inputs = _inputs('workspace "X" "y" { model { } }', None)

        sut = compute_metrics

        result = sut(parsed, inputs)

        finding = "ERROR: the container named Web Store is not included on any views"
        self.assertEqual(result.inspect_triage, {finding: TRIAGE_FIX})

    def test_codemode_inspect_without_a_later_edit_is_not_a_fix(self) -> None:
        inspect_code = "const dsl = `x`;\nconst f = await tools.structurizr.inspect({ dsl });\nreturn f;\n"
        events = [
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "execute",
                    "state": {
                        "status": "completed",
                        "input": {"code": inspect_code},
                        "output": '["ERROR: the container named Web Store is not included on any views"]',
                    },
                },
            },
            {
                "type": "text",
                "part": {
                    "type": "text",
                    # the `reported` label needs the finding text itself
                    # in the final message
                    "text": 'Done: "ERROR: the container named Web Store is not included on any views" - noted.',
                },
            },
        ]
        parsed = parse_event_stream([json.dumps(event) for event in events])
        inputs = _inputs('workspace "X" "y" { model { } }', None)

        sut = compute_metrics

        result = sut(parsed, inputs)

        finding = "ERROR: the container named Web Store is not included on any views"
        self.assertEqual(result.inspect_triage, {finding: TRIAGE_REPORTED})


class TestCodeModeMetrics(unittest.TestCase):
    """The locked contract over the committed Code Mode fixture stream."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_events_file(FIXTURES_DIR / "events" / "codemode-stream.ndjson")

    def _inputs_for(self, dsl_text: str | None) -> GraderInputs:
        return _inputs(dsl_text, None)

    def test_call_counts_mix_native_and_codemode(self) -> None:
        # A: validate (OK, inline literal); B: inspect (variable);
        # C: parse + validate (multi-call); D: parse (error); F: validate
        # (OK, interpolated); G: validate (OK, shorthand); H: native parse
        inputs = self._inputs_for(None)

        sut = compute_metrics(self.parsed, inputs)

        self.assertEqual(sut.parse_calls, 3)
        self.assertEqual(sut.validate_calls, 4)
        self.assertEqual(sut.inspect_calls, 1)
        self.assertEqual(sut.export_calls, 0)
        self.assertEqual(sut.validate_ok_calls, 3)

    def test_multi_call_block_validate_does_not_count_as_ok(self) -> None:
        # the C block's returned object carries "validate": "OK", but a
        # multi-call block never attributes OK (the locked conservative rule)
        inputs = self._inputs_for(None)

        sut = compute_metrics(self.parsed, inputs)

        ok_view = [entry for entry in normalized_mcp_calls(self.parsed) if entry.ok]
        self.assertEqual({entry.position for entry in ok_view}, {0, 5, 6})
        self.assertEqual(sut.validate_ok_calls, len(ok_view))

    def test_validated_texts_carry_only_the_attributed_inline_literal(self) -> None:
        from .test_codemode import FIXTURE_DSL

        result = validated_texts(self.parsed)

        self.assertEqual(result, {FIXTURE_DSL})

    def test_stream_findings_come_from_the_codemode_inspect(self) -> None:
        from .test_codemode import FIXTURE_DSL

        inputs = self._inputs_for(FIXTURE_DSL)

        sut = compute_metrics(self.parsed, inputs)

        self.assertEqual(len(sut.inspect_findings), 2)
        self.assertTrue(any("missing documentation" in finding for finding in sut.inspect_findings))
        self.assertEqual(
            sut.inspect_triage,
            {
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.': TRIAGE_EXPECTED,
                'ERROR: The container named "Web Store" is not included on any views - add it to a view.': TRIAGE_FIX,
            },
        )

    def test_validated_before_return_passes_on_the_attributed_text(self) -> None:
        from .test_codemode import FIXTURE_DSL

        inputs = self._inputs_for(FIXTURE_DSL)

        sut = compute_metrics(self.parsed, inputs)

        self.assertTrue(sut.validated_before_return)
        self.assertTrue(sut.validated_by_file)

    def test_unattributable_ok_calls_add_nothing_to_validated_texts(self) -> None:
        # G answers OK but its dsl is a shorthand variable: the byte-identity
        # metric must NOT pass on weaker evidence (conservative by design)
        inputs = self._inputs_for('workspace "Bookshop" "A different text." {\n    model {\n    }\n}')

        sut = compute_metrics(self.parsed, inputs)

        self.assertFalse(sut.validated_by_file)


class TestNativeOnlyRegression(unittest.TestCase):
    """Native-only streams produce byte-identical metrics to the pre-fix code.

    The expected values below are the PRE-FIX outputs (the Task 100/110
    test expectations, pinned here so a future change cannot silently move
    the native semantics).
    """

    def test_tool_stream_metrics_are_the_pinned_pre_fix_values(self) -> None:
        parsed = parse_events_file(FIXTURES_DIR / "events" / "tool-stream.ndjson")
        inputs = _inputs(_validated_dsl(), _good_export())

        sut = compute_metrics(parsed, inputs)

        metrics = sut.to_json()
        self.assertEqual(metrics["parse_calls"], 1)
        self.assertEqual(metrics["validate_calls"], 1)
        self.assertEqual(metrics["inspect_calls"], 1)
        self.assertEqual(metrics["export_calls"], 0)
        self.assertEqual(metrics["validate_ok_calls"], 1)
        self.assertEqual(metrics["validated_before_return"], True)
        self.assertEqual(metrics["skills_loaded"], ["c4-model"])
        self.assertEqual(metrics["tool_calls"], 4)
        self.assertEqual(metrics["steps"], 1)
        self.assertEqual(
            metrics["inspect_findings"],
            [
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.',
                'ERROR: The software system "Bookshop" has containers, but is missing decisions.',
                'ERROR: The container named "Web Store" is not included on any views - add it to a view.',
            ],
        )
        self.assertEqual(
            metrics["inspect_triage"],
            {
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.': "expected",
                'ERROR: The software system "Bookshop" has containers, but is missing decisions.': "expected",
                'ERROR: The container named "Web Store" is not included on any views - add it to a view.': "untriaged",
            },
        )

    def test_validate_loop_metrics_are_the_pinned_pre_fix_values(self) -> None:
        parsed = parse_events_file(FIXTURES_DIR / "events" / "validate-loop.ndjson")
        inputs = _inputs(_validated_dsl(), _good_export())

        sut = compute_metrics(parsed, inputs)

        metrics = sut.to_json()
        self.assertEqual(metrics["parse_calls"], 1)
        self.assertEqual(metrics["validate_calls"], 2)
        self.assertEqual(metrics["inspect_calls"], 1)
        self.assertEqual(metrics["export_calls"], 0)
        self.assertEqual(metrics["validate_ok_calls"], 2)
        self.assertEqual(metrics["validated_before_return"], True)
        self.assertEqual(metrics["skills_loaded"], ["structurizr-validate-loop"])
        # 8 terminal tool calls (skill, 2 write, 1 parse[error],
        # 2 validate, 1 inspect, 1 edit)
        self.assertEqual(metrics["tool_calls"], 8)
        self.assertEqual(len(metrics["inspect_findings"]), 4)
        self.assertEqual(set(metrics["inspect_triage"].values()), {"expected", "fix"})

    def test_native_only_streams_carry_no_codemode_entries(self) -> None:
        for name in ("tool-stream.ndjson", "validate-loop.ndjson", "probe-hello.ndjson"):
            parsed = parse_events_file(FIXTURES_DIR / "events" / name)
            view = normalized_mcp_calls(parsed)
            self.assertEqual({entry.source for entry in view} & {SOURCE_CODEMODE}, set(), name)


class TestFindingsFromOutput(unittest.TestCase):
    """Task 125.110/I1: the line fallback applies to single-line outputs only."""

    def test_json_array_single_line(self) -> None:
        result = _findings_from_output('["a", "b"]')

        self.assertEqual(result, ["a", "b"])

    def test_json_array_multi_line(self) -> None:
        text = '["ERROR: a",\n "ERROR: b"]\n'

        result = _findings_from_output(text)

        self.assertEqual(result, ["ERROR: a", "ERROR: b"])

    def test_single_line_non_array_is_the_finding(self) -> None:
        result = _findings_from_output("ERROR: the model is empty")

        self.assertEqual(result, ["ERROR: the model is empty"])

    def test_multi_line_bundled_object_yields_no_findings(self) -> None:
        # the committed mcp-limits/none-k0 shape: a bundled Code Mode
        # answer (a valid JSON object, NOT an array) -- before I1 every
        # non-blank line of it became a "finding" (11 in that trial,
        # including `{`, `}` and the lines of the object itself)
        text = (
            "{\n"
            '  "testC_sysToSys": "The source element \\"A\\" does not exist at line 5: \\"A\\" -> \\"B\\" \\"Calls\\"",\n'
            '  "testD_inspect": [\n'
            '    "ERROR: The person \\"Customer\\" is disconnected - add a relationship to/from it, or consider removing it from the model.",\n'
            '    "ERROR: This workspace has no views."\n'
            "  ]\n"
            "}\n"
        )

        result = _findings_from_output(text)

        self.assertEqual(result, [])

    def test_multi_line_non_json_yields_no_findings(self) -> None:
        result = _findings_from_output("ERROR: a\nERROR: b")

        self.assertEqual(result, [])

    def test_empty_and_blank_text_yield_no_findings(self) -> None:
        self.assertEqual(_findings_from_output(""), [])
        self.assertEqual(_findings_from_output("   \n  "), [])


class TestNormalizeFinding(unittest.TestCase):
    """Task 125.120/I2: the severity prefix is the stream/CLI merge key."""

    def test_severity_prefixes_are_stripped(self) -> None:
        for text, bare in [
            ("ERROR: X", "X"),
            ("ERROR X", "X"),
            ("WARNING: X", "X"),
            ("WARNING X", "X"),
            ("INFO: X", "X"),
            ("IGNORE X", "X"),
        ]:
            with self.subTest(text=text):
                self.assertEqual(normalize_finding(text), bare)

    def test_bare_finding_is_unchanged(self) -> None:
        self.assertEqual(normalize_finding("The model is empty"), "The model is empty")

    def test_longer_word_is_not_a_severity_prefix(self) -> None:
        # a finding that merely starts with the word keeps its text: the
        # prefix is a WHOLE severity token followed by a colon or
        # whitespace, so `ERRORS ...` is untouched
        self.assertEqual(normalize_finding("ERRORS in the model"), "ERRORS in the model")

    def test_sentence_starting_with_the_token_follows_the_delimiter_rule(self) -> None:
        # the locked delimiter rule (a whole token + colon OR whitespace)
        # strips the `ERROR ` prefix here too; the keeping case is the
        # longer-word one above (a token without such a delimiter)
        self.assertEqual(normalize_finding("ERROR handling failed"), "handling failed")

    def test_merge_collapses_stream_and_cli_forms_to_one_entry(self) -> None:
        # the committed mcp-limits/skill-k1 shape: the stream answers the
        # findings `ERROR:`-prefixed, the CLI carries their bare forms --
        # the merge keeps ONE entry per finding (first-seen form, order
        # preserved) and appends the CLI-only finding
        events = [
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "structurizr_inspect",
                    "state": {
                        "status": "completed",
                        "output": json.dumps(
                            [
                                'ERROR: The system "S" is missing documentation.',
                                'ERROR: The system "S" is missing decisions.',
                            ]
                        ),
                    },
                },
            },
        ]
        parsed = parse_event_stream([json.dumps(event) for event in events])
        inputs = _inputs(
            'workspace "S" "s" { model { } }',
            None,
            inspect_rc=1,
            inspect_findings=[
                'The system "S" is missing documentation.',
                'The system "S" is missing decisions.',
                'The relationship "R" is missing its technology.',
            ],
        )

        result = compute_metrics(parsed, inputs)

        self.assertEqual(
            result.inspect_findings,
            [
                'ERROR: The system "S" is missing documentation.',
                'ERROR: The system "S" is missing decisions.',
                'The relationship "R" is missing its technology.',
            ],
        )
        self.assertEqual(
            result.inspect_triage,
            {
                'ERROR: The system "S" is missing documentation.': TRIAGE_EXPECTED,
                'ERROR: The system "S" is missing decisions.': TRIAGE_EXPECTED,
                'The relationship "R" is missing its technology.': TRIAGE_UNTRIAGED,
            },
        )


class TestFinalInspectFindingsSet(unittest.TestCase):
    """Task 125.100/G2: the truth anchor of the `fix` triage label."""

    def test_clean_final_is_the_empty_set(self) -> None:
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=0, inspect_findings=[])

        self.assertEqual(final_inspect_findings_set(inputs), set())

    def test_inspected_findings_are_the_normalized_set(self) -> None:
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=1, inspect_findings=["ERROR: X", "Y"])

        self.assertEqual(final_inspect_findings_set(inputs), {"X", "Y"})

    def test_no_cli_run_is_none(self) -> None:
        inputs = _inputs(None, None, inspect_rc=None, inspect_findings=[])

        self.assertIsNone(final_inspect_findings_set(inputs))

    def test_broken_workspace_with_no_parsed_finding_is_none(self) -> None:
        # the committed mcp-limits/none-k0 shape: the final CLI inspect
        # answered rc=1 with an error line that carries no parseable
        # finding -- no `fix` label is valid at all
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=1, inspect_findings=[])

        self.assertIsNone(final_inspect_findings_set(inputs))


class TestTriageFixLabel(unittest.TestCase):
    """Task 125.100/G2: `fix` needs the post-inspect edit AND the absence."""

    FINDING = 'ERROR: The container "C" is not included on any views'

    def _stream(self, *, edited: bool, final_text: str = "") -> ParsedTrial:
        events = [
            {
                "type": "tool_use",
                "part": {
                    "type": "tool",
                    "tool": "structurizr_inspect",
                    "state": {"status": "completed", "output": json.dumps([self.FINDING])},
                },
            },
        ]
        if edited:
            events.append(
                {
                    "type": "tool_use",
                    "part": {
                        "type": "tool",
                        "tool": "write",
                        "state": {"status": "completed", "input": {"filePath": "workspace.dsl"}, "output": "wrote"},
                    },
                }
            )
        if final_text:
            events.append({"type": "text", "part": {"type": "text", "text": final_text}})
        return parse_event_stream([json.dumps(event) for event in events])

    def test_edit_with_the_finding_still_present_in_the_final_cli_is_untriaged(self) -> None:
        # the G2 edge: the edit happened, but the finding is STILL in the
        # grader's own final CLI inspect findings -- no `fix`
        parsed = self._stream(edited=True)
        inputs = _inputs(
            'workspace "X" "y" { model { } }',
            None,
            inspect_rc=1,
            inspect_findings=['The container "C" is not included on any views'],
        )

        result = triage_findings([self.FINDING], parsed, inputs)

        self.assertEqual(result, {self.FINDING: TRIAGE_UNTRIAGED})

    def test_edit_with_the_finding_absent_from_the_final_cli_is_fix(self) -> None:
        parsed = self._stream(edited=True)
        inputs = _inputs(
            'workspace "X" "y" { model { } }', None, inspect_rc=1, inspect_findings=["A different finding"]
        )

        result = triage_findings([self.FINDING], parsed, inputs)

        self.assertEqual(result, {self.FINDING: TRIAGE_FIX})

    def test_clean_final_makes_the_finding_fix(self) -> None:
        # rc=0: a clean final inspect, the empty set -- every finding is
        # absent from it, so the corroborated edit earns `fix`
        parsed = self._stream(edited=True)
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=0, inspect_findings=[])

        result = triage_findings([self.FINDING], parsed, inputs)

        self.assertEqual(result, {self.FINDING: TRIAGE_FIX})

    def test_no_edit_is_never_fix(self) -> None:
        parsed = self._stream(edited=False)
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=0, inspect_findings=[])

        result = triage_findings([self.FINDING], parsed, inputs)

        self.assertEqual(result, {self.FINDING: TRIAGE_UNTRIAGED})

    def test_broken_final_falls_through_to_reported_when_the_finding_is_in_the_final_message(self) -> None:
        # rc=1 with no parsed finding: no `fix` is valid at all, and the
        # locked priority (expected -> fix -> reported -> untriaged)
        # falls through to `reported` when the finding's text is in the
        # final message
        parsed = self._stream(edited=True, final_text=f"The known issue: {self.FINDING}")
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=1, inspect_findings=[])

        result = triage_findings([self.FINDING], parsed, inputs)

        self.assertEqual(result, {self.FINDING: TRIAGE_REPORTED})

    def test_broken_final_is_untriaged_when_the_finding_is_not_reported(self) -> None:
        parsed = self._stream(edited=True)
        inputs = _inputs('workspace "X" "y" { model { } }', None, inspect_rc=1, inspect_findings=[])

        result = triage_findings([self.FINDING], parsed, inputs)

        self.assertEqual(result, {self.FINDING: TRIAGE_UNTRIAGED})


#: The committed Phase 110 iteration-2 run (the G2/I1/I2 evidence, cited
#: never modified -- the trial records' own `metrics` carry the pre-fix
#: values; the final-CLI facts for its three evidence trials are the
#: pinned fixtures under `fixtures/cli-inspect/`).
_P110_ITER2_TRIALS = (
    Path(__file__).resolve().parents[2] / "evals" / "c4-skills" / "results" / "p110-iter2-2026-11-05T143241Z" / "trials"
)


class TestPhase125CommittedEvidence(unittest.TestCase):
    """Tasks 125.100-125.120 re-graded over the committed p110-iter2 streams.

    For each evidence trial the test parses the committed event stream,
    builds the `GraderInputs` from the pinned final-CLI fixture (the
    trial's final on-disk workspace, the pinned CLI `inspect` output and
    its rc + parsed findings -- rc=1 in every case; `mcp-limits-none-k0`
    is the broken-workspace shape whose error line carries no parseable
    finding), and asserts the NEW metrics and the `triage_complete`
    verdict. `parse_inspect_findings` over the fixture's `inspect.txt` is
    pinned against the fixture's `inspect.json` as well, so the CLI-text
    parsing is part of the evidence.
    """

    def _graded(self, case_name: str, fix_dir: str, stream_name: str):
        record = json.loads((_P110_ITER2_TRIALS / case_name / f"{stream_name}.json").read_text(encoding="utf-8"))
        parsed = parse_events_file(_P110_ITER2_TRIALS / case_name / f"{stream_name}.events.ndjson")
        fix = FIXTURES_DIR / "cli-inspect" / fix_dir
        pin = json.loads((fix / "inspect.json").read_text(encoding="utf-8"))
        self.assertEqual(
            parse_inspect_findings((fix / "inspect.txt").read_text(encoding="utf-8")),
            pin["inspect_findings"],
        )
        inputs = GraderInputs(
            dsl_path="workspace.dsl",
            dsl_text=(fix / "workspace.dsl").read_text(encoding="utf-8"),
            validate_rc=0,
            validate_stderr="",
            export_json=None,
            export_rc=None,
            export_stderr="",
            inspect_rc=pin["inspect_rc"],
            inspect_findings=list(pin["inspect_findings"]),
        )
        metrics = compute_metrics(
            parsed,
            inputs,
            timeout=record.get("timeout", False),
            contended=record.get("contended", False),
        )
        context = GateContext(
            inputs=inputs,
            case=CASES[case_name],
            trial=parsed,
            metrics=metrics,
            skills_installed=tuple(record.get("skills_installed") or ()),
        )
        return inputs, parsed, metrics, grade_case(context), record

    def test_none_k0_line_fragments_are_gone_and_no_fix_is_valid(self) -> None:
        inputs, parsed, metrics, results, record = self._graded("mcp-limits", "mcp-limits-none-k0", "none-k0")

        # I1: the trial's single inspect output is a bundled Code Mode
        # object answer (a multi-line non-JSON-array) -- the 11 old
        # line-fragment "findings" (including `{`, `}` and the JSON lines
        # of the object itself) are gone from the stream extraction
        self.assertEqual(metrics.inspect_findings, [])
        self.assertEqual(metrics.inspect_triage, {})
        # G2: the final CLI inspect met a broken workspace (rc=1, an
        # error line with no parseable finding) -- no `fix` label is
        # valid at all, even though this stream DID edit after its
        # (bundled) inspect
        self.assertIsNone(final_inspect_findings_set(inputs))
        self.assertTrue(_edited_after_inspect(parsed))
        gate = next(result for result in results if result.name == "triage_complete")
        self.assertTrue(gate.passed)
        self.assertEqual(gate.detail, "no inspect findings (vacuously complete)")
        # the pre-fix record (cited, never modified) shows what the old
        # logic graded over this same stream: 11 findings, every one
        # labeled `fix` -- the G2 edge
        self.assertEqual(len(record["metrics"]["inspect_findings"]), 11)
        self.assertTrue(all(label == "fix" for label in record["metrics"]["inspect_triage"].values()))

    def test_mcp_limits_skill_k1_collapse_to_two_expected(self) -> None:
        inputs, parsed, metrics, results, record = self._graded("mcp-limits", "mcp-limits-skill-k1", "skill-k1")

        # I2: the 4 old findings (2 real x 2 forms) collapse to exactly
        # 2 -- the stream's `ERROR:`-prefixed first-seen forms; the bare
        # CLI forms merge onto them
        self.assertEqual(
            metrics.inspect_findings,
            [
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.',
                'ERROR: The software system "Bookshop" has containers, but is missing decisions.',
            ],
        )
        self.assertEqual(
            metrics.inspect_triage,
            {
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.': TRIAGE_EXPECTED,
                'ERROR: The software system "Bookshop" has containers, but is missing decisions.': TRIAGE_EXPECTED,
            },
        )
        # G2: the final CLI inspect still reports both MCP-limits findings
        self.assertEqual(
            final_inspect_findings_set(inputs),
            {
                'The software system "Bookshop" has containers, but is missing documentation.',
                'The software system "Bookshop" has containers, but is missing decisions.',
            },
        )
        gate = next(result for result in results if result.name == "triage_complete")
        self.assertTrue(gate.passed)
        self.assertEqual(gate.detail, "all 2 finding(s) labeled fix/expected/reported")
        self.assertEqual(len(record["metrics"]["inspect_findings"]), 4)

    def test_create_system_skill_k1_fix_labels_are_truth_anchored(self) -> None:
        inputs, parsed, metrics, results, record = self._graded("create-system", "create-system-skill-k1", "skill-k1")

        # I2: the 6 old findings collapse to 4 (the bare CLI forms merge
        # onto the stream's `ERROR:` forms)
        self.assertEqual(
            metrics.inspect_findings,
            [
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.',
                'ERROR: The software system "Bookshop" has containers, but is missing decisions.',
                'ERROR: The container named "Web Store" is not included on any views - add it to a view.',
                'ERROR: The container named "Order Processor" is not included on any views - add it to a view.',
            ],
        )
        # G2: the two container-view findings the post-inspect edit
        # cleared are ABSENT from the final CLI inspect findings -> `fix`
        # (the legitimate case); the two MCP-limits findings are STILL in
        # them -> `expected`
        self.assertEqual(
            metrics.inspect_triage,
            {
                'ERROR: The software system "Bookshop" has containers, but is missing documentation.': TRIAGE_EXPECTED,
                'ERROR: The software system "Bookshop" has containers, but is missing decisions.': TRIAGE_EXPECTED,
                'ERROR: The container named "Web Store" is not included on any views - add it to a view.': TRIAGE_FIX,
                'ERROR: The container named "Order Processor" is not included on any views - add it to a view.': TRIAGE_FIX,
            },
        )
        final_set = final_inspect_findings_set(inputs)
        self.assertIsNotNone(final_set)
        self.assertNotIn('The container named "Web Store" is not included on any views - add it to a view.', final_set)
        self.assertIn('The software system "Bookshop" has containers, but is missing documentation.', final_set)
        self.assertTrue(_edited_after_inspect(parsed))
        gate = next(result for result in results if result.name == "triage_complete")
        self.assertTrue(gate.passed)
        self.assertEqual(gate.detail, "all 4 finding(s) labeled fix/expected/reported")
        self.assertEqual(len(record["metrics"]["inspect_findings"]), 6)


if __name__ == "__main__":
    unittest.main()
