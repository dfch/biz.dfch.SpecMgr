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

"""Tests for the ``create_prb`` ``@mcp.prompt()`` (Task 3.14, ACC-006).

``create_prb`` (the prompt) only ever returns instructional text -- it never
calls ``TodoWrite``/``question``/``list_prb``/``create_prb`` (the tool)
itself -- so these are string-content/ordering assertions on the narrated
text confirming every required step from the feature README's Design Notes
is actually present, in the right order, rather than behavioral tests of a
live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.prb.prompts.create_prb import create_prb


class TestCreatePrbPrompt(unittest.TestCase):
    """Tests for the create_prb prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_prb("Widget registry migration rollback failures")
        self.assertIn("Widget registry migration rollback failures", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_prb tool first."""
        result = create_prb("Some topic")
        self.assertIn("list_prb", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a TodoWrite list covering Summary + 7
        questions + Gap + Impact + Future State."""
        result = create_prb("Some topic")
        self.assertIn("todo list", result)
        self.assertIn("Summary", result)
        self.assertIn("Gap", result)
        self.assertIn("Impact", result)
        self.assertIn("Future State", result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit answers."""
        result = create_prb("Some topic")
        self.assertIn("question", result)

    def test_mentions_all_seven_5w2h_questions(self):
        """All 7 fixed 5W2H question headings must be named verbatim."""
        result = create_prb("Some topic")
        for heading in (
            "What Is the Problem?",
            "Why Is It a Problem?",
            "Where Is the Problem Observed?",
            "Who Is Impacted?",
            "When Was the Problem First Observed?",
            "How Is the Problem Observed?",
            "How Often Is the Problem Observed?",
        ):
            self.assertIn(heading, result)

    def test_mentions_allowing_skip(self):
        """The prompt must explicitly allow the user to skip any of the 7 questions."""
        result = create_prb("Some topic")
        self.assertIn("skip", result)

    def test_mentions_synthesizing_summary(self):
        """The prompt must instruct synthesizing a Summary from whichever answers were given."""
        result = create_prb("Some topic")
        self.assertIn("Synthesize", result)

    def test_mentions_drafting_and_confirming_gap(self):
        """The prompt must instruct drafting a Gap statement and confirming it via the question tool."""
        result = create_prb("Some topic")
        self.assertIn("Draft", result)
        self.assertIn("confirm", result)

    def test_mentions_no_root_cause_section(self):
        """The prompt must not narrate a `## Root Cause` heading as part of the structure
        recap -- deliberately excluded by design, though the prompt is allowed to explain
        the exclusion in prose (which does mention "Root Cause" by name, quoted as a
        code span, never as its own heading line)."""
        result = create_prb("Some topic")
        heading_lines = [line for line in result.splitlines() if line.strip() == "## Root Cause"]
        self.assertEqual(heading_lines, [])
        self.assertIn("No `## Root Cause` section exists", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_prb("Some topic")
        self.assertIn("specmgr://prb/template", result)
        self.assertIn("specmgr://prb/example", result)
        self.assertIn("specmgr://prb/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_prb tool, the template/example
        resources, specmgr://prb/schema, and create_prb, in that order,
        matching the intended sequence."""
        result = create_prb("Some topic")
        markers = [
            "list_prb",
            "specmgr://prb/template",
            "specmgr://prb/schema",
            "create_prb(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_update_prb_for_later_revisions(self):
        """The prompt must point at the update_prb prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_prb("Some topic")
        self.assertIn("`update_prb` prompt", result)
        self.assertIn('update(id, type="prb", content)', result)
        self.assertIn('set_status(id, type="prb", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from prb/data/prb_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "prb_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_prb("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_prb("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_prb("Some topic")


if __name__ == "__main__":
    unittest.main()
