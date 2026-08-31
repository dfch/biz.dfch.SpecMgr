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

"""Tests for the ``create_vcr`` ``@mcp.prompt()`` (Task 3.2).

``create_vcr`` (the prompt) only ever returns instructional text -- it
never calls ``TodoWrite``/``question``/``list_vcr``/``create_vcr`` (the
tool) itself -- so these are string-content/ordering assertions on the
narrated text confirming every required step from the feature README's
Design Notes is actually present, in the right order, rather than
behavioral tests of a live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.vcr.prompts.create_vcr import create_vcr


class TestCreateVcrPrompt(unittest.TestCase):
    """Tests for the create_vcr prompt."""

    def test_returns_substituted_instruction_text(self):
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_vcr("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        vcr/data/vcr_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_vcr("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_vcr tool first."""
        result = create_vcr("Some topic")
        self.assertIn("list_vcr", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a todo list covering the mandatory
        `Verifies`/`Coverage`/`Acceptance Criteria` + each optional section."""
        result = create_vcr("Some topic")
        self.assertIn("todo list", result)
        for section in (
            "Verifies",
            "Coverage",
            "Acceptance Criteria",
            "More Information",
            "Updates",
        ):
            self.assertIn(section, result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit information."""
        result = create_vcr("Some topic")
        self.assertIn("question", result)

    def test_mentions_allowing_skip_for_optional_sections(self):
        """The prompt must explicitly allow the user to skip any optional field."""
        result = create_vcr("Some topic")
        self.assertIn("skip", result)

    def test_mentions_dtais_closed_vocabulary(self):
        """The prompt must name all five closed DTAIS method words verbatim."""
        result = create_vcr("Some topic")
        for method in ("Demonstration", "Test", "Analysis", "Inspection", "Special"):
            self.assertIn(method, result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources plus specmgr://dtais."""
        result = create_vcr("Some topic")
        self.assertIn("specmgr://vcr/template", result)
        self.assertIn("specmgr://vcr/example", result)
        self.assertIn("specmgr://vcr/schema", result)
        self.assertIn("specmgr://dtais", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_vcr tool, the template/example
        resources, specmgr://vcr/schema, and create_vcr, in that order,
        matching the intended sequence."""
        result = create_vcr("Some topic")
        markers = [
            "list_vcr",
            "specmgr://vcr/template",
            "specmgr://vcr/schema",
            "create_vcr(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_update_vcr_for_later_revisions(self):
        """The prompt must point at the update_vcr prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_vcr("Some topic")
        self.assertIn("`update_vcr` prompt", result)
        self.assertIn('update(id, type="vcr", content)', result)
        self.assertIn('set_status(id, type="vcr", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from vcr/data/vcr_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "vcr_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_vcr("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_vcr("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_vcr("Some topic")


if __name__ == "__main__":
    unittest.main()
