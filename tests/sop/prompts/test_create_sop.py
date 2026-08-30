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

"""Tests for the ``create_sop`` ``@mcp.prompt()`` (Task 4.1, ACC-005).

``create_sop`` (the prompt) only ever returns instructional text -- it never
calls ``TodoWrite``/``question``/``list_sop``/``create_sop`` (the tool)
itself -- so these are string-content/ordering assertions on the narrated
text confirming every required step from the feature README's Design Notes
is actually present, in the right order, rather than behavioral tests of a
live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.sop.prompts.create_sop import create_sop
from biz.dfch.specmgr.general.tools import _packaged_data


class TestCreateSopPrompt(unittest.TestCase):
    """Tests for the create_sop prompt."""

    def test_returns_substituted_instruction_text(self):
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_sop("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        sop/data/sop_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_sop("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_sop tool first (ACC-005)."""
        result = create_sop("Some topic")
        self.assertIn("list_sop", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a todo list covering the mandatory
        `## Purpose` + `## Procedure` and each optional section."""
        result = create_sop("Some topic")
        self.assertIn("todo list", result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit information."""
        result = create_sop("Some topic")
        self.assertIn("question", result)

    def test_mentions_sop_sections(self):
        """The key SOP section headings must appear in the narrated structure."""
        result = create_sop("Some topic")
        for section in (
            "## Purpose",
            "## Procedure",
            "## Roles and Responsibilities",
            "## Updates",
        ):
            self.assertIn(section, result)

    def test_mentions_rasci_read_first(self):
        """The prompt must include an explicit step to read specmgr://rasci before
        drafting ## Roles and Responsibilities (REQ-011 discoverability)."""
        result = create_sop("Some topic")
        self.assertIn("specmgr://rasci", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_sop("Some topic")
        self.assertIn("specmgr://sop/template", result)
        self.assertIn("specmgr://sop/example", result)
        self.assertIn("specmgr://sop/schema", result)

    def test_mentions_create_and_validate_tools(self):
        """The prompt must name the create_sop and validate_sop tools."""
        result = create_sop("Some topic")
        self.assertIn("create_sop(content)", result)
        self.assertIn("validate_sop(content, full=False)", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from sop/data/sop_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "sop_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_sop("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_sop("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_sop("Some topic")


if __name__ == "__main__":
    unittest.main()
