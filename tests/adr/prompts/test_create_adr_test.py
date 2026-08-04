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

"""Tests for the ``create_adr_test`` ``@mcp.prompt()`` (doc/adr-tool-plan.md §11)."""

import unittest

from biz.dfch.specmgr.adr.prompts.create_adr_test import create_adr_test


class TestCreateAdrTestPrompt(unittest.TestCase):
    """Tests for the step-gated create_adr_test prompt variant."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_adr_test("Choice of message queue")
        self.assertIn("Choice of message queue", result)

    def test_mentions_duplicate_check_resource(self):
        """The prompt must instruct the LLM to check specmgr://adr/list first."""
        result = create_adr_test("Some topic")
        self.assertIn("specmgr://adr/list", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention create_adr, option_create, set_status, and
        validate_adr, in that order, matching the intended tool call sequence."""
        result = create_adr_test("Some topic")
        tools = ["create_adr", "option_create", "set_status", "validate_adr"]
        positions = [result.index(tool) for tool in tools]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_sections(self):
        """The mandatory MADR sections must all be named in the recap."""
        result = create_adr_test("Some topic")
        for heading in (
            "Context and Problem Statement",
            "Considered Options",
            "Decision Outcome",
        ):
            self.assertIn(heading, result)

    def test_optional_frontmatter_args_interpolated_when_given(self):
        """decision_makers/consulted/informed must appear verbatim when provided."""
        result = create_adr_test(
            "Some topic",
            decision_makers="Platform Team",
            consulted="Security Team",
            informed="All Engineering",
        )
        self.assertIn("Platform Team", result)
        self.assertIn("Security Team", result)
        self.assertIn("All Engineering", result)

    def test_optional_frontmatter_args_prompt_for_input_when_absent(self):
        """Absent optional args must produce a tell-the-LLM-to-ask placeholder,
        not a blank or 'None' string."""
        result = create_adr_test("Some topic")
        self.assertNotIn("None", result)
        self.assertIn("ask the user", result)

    def test_has_numbered_gates_in_order(self):
        """The step-gated variant's defining feature: GATE 0..4 markers, in order."""
        result = create_adr_test("Some topic")
        gates = [f"GATE {n}" for n in range(5)]
        positions = [result.index(gate) for gate in gates]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_never_fabricate(self):
        """The strict variant must explicitly forbid fabricating values to pass a gate."""
        result = create_adr_test("Some topic")
        self.assertIn("fabricate", result.lower())

    def test_mentions_exit_condition_for_each_gate(self):
        """Each gate must carry an explicit, checkable exit condition."""
        result = create_adr_test("Some topic")
        self.assertGreaterEqual(result.count("Exit condition"), 4)

    def test_differs_from_non_gated_baseline(self):
        """Sanity check: this variant's text must not be identical to create_adr's."""
        from biz.dfch.specmgr.adr.prompts.create_adr import create_adr

        self.assertNotEqual(create_adr_test("Some topic"), create_adr("Some topic"))


if __name__ == "__main__":
    unittest.main()
