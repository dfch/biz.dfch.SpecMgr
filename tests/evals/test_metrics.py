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

"""Metrics tests (Task 100.140 / Task 100.160).

All fixtures are committed files (the synthetic event stream plus the
pre-exported workspace JSON); no model call, no Docker.
"""

import json
import unittest

from c4_skills.events import parse_events_file
from c4_skills.graders import GraderInputs
from c4_skills.metrics import TRIAGE_EXPECTED, TRIAGE_UNTRIAGED, compute_metrics, extract_final_dsl

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


def _inputs(dsl_text: str | None, export_json: dict | None) -> GraderInputs:
    return GraderInputs(
        dsl_path="workspace.dsl" if dsl_text is not None else None,
        dsl_text=dsl_text,
        validate_rc=0 if dsl_text is not None else 1,
        validate_stderr="" if dsl_text is not None else "boom",
        export_json=export_json,
        export_rc=0 if export_json is not None else 1,
        export_stderr="" if export_json is not None else "boom",
        inspect_rc=0,
        inspect_findings=[],
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


if __name__ == "__main__":
    unittest.main()
