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

"""Tests for the ``create_sysrs`` ``@mcp.prompt()`` (Task 5.1, ACC-008).

``create_sysrs`` (the prompt) only ever returns instructional text -- it
never calls ``TodoWrite``/``question``/``list_sysrs``/``create_sysrs`` (the
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
from biz.dfch.specmgr.sysrs.prompts.create_sysrs import create_sysrs


class TestCreateSysrsPrompt(unittest.TestCase):
    """Tests for the create_sysrs prompt."""

    def test_returns_substituted_instruction_text(self):
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_sysrs("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        sysrs/data/sysrs_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_sysrs("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool_first(self):
        """The prompt must instruct the LLM to check the list_sysrs tool
        first, before drafting anything (ACC-008 dedup-check-first)."""
        result = create_sysrs("Some topic")
        self.assertIn("list_sysrs", result)
        self.assertLess(result.index("list_sysrs"), result.index("## 1. Structure recap"))

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a todo list covering the mandatory
        sections and each optional section."""
        result = create_sysrs("Some topic")
        self.assertIn("todo list", result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit information."""
        result = create_sysrs("Some topic")
        self.assertIn("question", result)

    def test_mentions_sysrs_sections(self):
        """The key SYSRS section headings must appear in the narrated structure."""
        result = create_sysrs("Some topic")
        for section in (
            "## System Purpose",
            "## System Scope",
            "## Business Context and Goals",
            "### Goals",
            "## Requirements",
            "## Other Characteristics",
            "## Verification",
            "## Updates",
        ):
            self.assertIn(section, result)

    def test_mentions_iso25010_read_first_step(self):
        """The prompt must include an explicit step to read specmgr://iso25010
        for the nine canonical characteristic names before filling
        ## Requirements (ACC-008 iso25010 read-first step)."""
        result = create_sysrs("Some topic")
        self.assertIn("specmgr://iso25010", result)
        self.assertIn("## Requirements", result)
        self.assertLess(result.index("specmgr://iso25010"), result.index("## 3. Build a todo list"))

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_sysrs("Some topic")
        self.assertIn("specmgr://sysrs/template", result)
        self.assertIn("specmgr://sysrs/example", result)
        self.assertIn("specmgr://sysrs/schema", result)

    def test_mentions_create_and_validate_tools(self):
        """The prompt must name the create_sysrs and validate_sysrs tools."""
        result = create_sysrs("Some topic")
        self.assertIn("create_sysrs(content)", result)
        self.assertIn("validate_sysrs(content, full=False)", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention list_sysrs, the iso25010 resource, the
        template/schema resources, and create_sysrs, in that order,
        matching the intended sequence."""
        result = create_sysrs("Some topic")
        markers = [
            "list_sysrs",
            "specmgr://iso25010",
            "specmgr://sysrs/template",
            "specmgr://sysrs/schema",
            "create_sysrs(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_update_sysrs_for_later_revisions(self):
        """The prompt must point at the update_sysrs prompt for later
        changes, with the generic update/set_status/set_classification
        tools named as the direct alternative (sysrs is dispatch-only)."""
        result = " ".join(create_sysrs("Some topic").split())
        self.assertIn("`update_sysrs`", result)
        self.assertIn("prompt", result)
        self.assertIn('update(id, type="sysrs", content)', result)
        self.assertIn('set_status(id, type="sysrs", status)', result)
        self.assertIn('set_classification(id, type="sysrs", classification)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from sysrs/data/sysrs_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "sysrs_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_sysrs("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_sysrs("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_sysrs("Some topic")


if __name__ == "__main__":
    unittest.main()
