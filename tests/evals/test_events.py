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

"""Parser tests for the `opencode run --format json` event stream.

The fixtures pin the real schema: `probe-hello.ndjson` is a verbatim
capture from the probe trial against the pinned opencode image (2.2.5) and
the pinned vLLM model (a one-line reply, no tools); `tool-stream.ndjson`
is the same schema extended with the tool/skill/step-finish shapes the
metrics tests need. No model call is involved in these tests.
"""

import unittest

from c4_skills.events import ParsedTrial, parse_event, parse_events_file, parse_event_stream

from .conftest import FIXTURES_DIR


class TestParseProbeFixture(unittest.TestCase):
    def test_probe_fixture_parses_to_one_step_and_one_text_part(self) -> None:
        expected_steps = 1
        expected_texts = 1
        fixture = FIXTURES_DIR / "events" / "probe-hello.ndjson"

        sut = parse_events_file(fixture)

        self.assertEqual(sut.steps, expected_steps)
        self.assertEqual(len(sut.text_parts), expected_texts)
        self.assertEqual(len(sut.tool_calls), 0)
        self.assertIn("PROBE-OK", sut.final_text())
        self.assertEqual(sut.session_id, "ses_e674aa5bdffe2iXpD3tZyEL3IF")
        self.assertEqual(sut.errors, [])
        self.assertEqual(dict(sut.unknown_types), {})

    def test_probe_fixture_token_and_wall_time_figures(self) -> None:
        expected_input = 4936
        expected_output = 29
        fixture = FIXTURES_DIR / "events" / "probe-hello.ndjson"

        sut = parse_events_file(fixture)

        self.assertEqual(sut.tokens["input"], expected_input)
        self.assertEqual(sut.tokens["output"], expected_output)
        self.assertEqual(sut.tokens["reasoning"], 0)
        self.assertEqual(sut.tokens["cache_read"], 0)
        self.assertEqual(sut.tokens["cache_write"], 0)
        wall = sut.wall_time_s()
        self.assertIsNotNone(wall)
        assert wall is not None
        self.assertAlmostEqual(wall, 1.334, places=3)


class TestParseToolStream(unittest.TestCase):
    def test_tool_stream_indexes_every_tool_call_with_state(self) -> None:
        expected_tools = 4
        expected_skill = "c4-model"
        fixture = FIXTURES_DIR / "events" / "tool-stream.ndjson"

        sut = parse_events_file(fixture)

        self.assertEqual(len(sut.tool_calls), expected_tools)
        self.assertEqual(sut.tool_calls[0].name, "skill")
        self.assertEqual(sut.tool_calls[0].status, "completed")
        # the pinned opencode image takes the skill identifier as `id`
        self.assertEqual(sut.tool_calls[0].input.get("id"), expected_skill)
        self.assertEqual(sut.tool_calls[3].name, "structurizr_inspect")
        self.assertEqual(sut.calls_named("validate")[0].output, "OK")
        self.assertEqual(sut.steps, 1)
        self.assertEqual(sut.tokens["input"], 1000)
        self.assertEqual(sut.tokens["cache_read"], 50)
        self.assertEqual(dict(sut.unknown_types), {})

    def test_tool_call_name_classification_with_mcp_prefix(self) -> None:
        expected_parse = 1
        expected_validate = 1
        fixture = FIXTURES_DIR / "events" / "tool-stream.ndjson"

        sut = parse_events_file(fixture)

        self.assertEqual(len(sut.calls_named("parse")), expected_parse)
        self.assertEqual(len(sut.calls_named("validate")), expected_validate)
        self.assertEqual(len(sut.calls_named("inspect")), expected_validate)
        self.assertEqual(len(sut.calls_named("export")), 0)


class TestParseLeniency(unittest.TestCase):
    def test_blank_and_unparseable_lines_are_counted_not_raised(self) -> None:
        lines = ["", "   ", "not json at all", '{"type": "text", "part": {"type": "text", "text": "hi"}}']

        sut = parse_event_stream(lines)

        self.assertEqual(dict(sut.unknown_types), {"<unparseable-line>": 1})
        self.assertEqual(sut.final_text(), "hi")

    def test_non_object_line_is_counted_as_unknown(self) -> None:
        lines = ["[1, 2, 3]"]

        sut = parse_event_stream(lines)

        self.assertEqual(dict(sut.unknown_types), {"<non-object-line>": 1})

    def test_error_event_is_recorded_separately(self) -> None:
        event = {"type": "error", "timestamp": 1, "sessionID": "s", "error": {"name": "X", "data": {"message": "boom"}}}
        parsed = ParsedTrial()

        sut = parse_event

        sut(event, parsed)

        self.assertEqual(len(parsed.errors), 1)
        self.assertEqual(parsed.events[-1]["type"], "error")

    def test_pending_tool_call_is_not_completed(self) -> None:
        event = {
            "type": "tool",
            "part": {
                "type": "tool",
                "tool": "structurizr_validate",
                "state": {"status": "pending", "input": {"dsl": "workspace"}},
            },
        }
        parsed = ParsedTrial()

        sut = parse_event

        sut(event, parsed)

        self.assertEqual(len(parsed.tool_calls), 1)
        self.assertEqual(len(parsed.completed_tool_calls()), 0)

    def test_truncated_stream_still_parses(self) -> None:
        lines = ['{"type": "step_start", "part": {"type": "step-start"}}']

        sut = parse_event_stream(lines)

        self.assertEqual(sut.steps, 1)
        self.assertIsNone(sut.wall_time_s())


if __name__ == "__main__":
    unittest.main()
