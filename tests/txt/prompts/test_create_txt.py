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

"""Tests for the ``create_txt`` ``@mcp.prompt()`` (feat-229-txt Phase 120).

``create_txt`` (the prompt) only ever returns instructional text -- it
never calls ``TodoWrite``/``question``/``list_txt``/``create_txt`` (the
tool) itself -- so these are string-content/ordering assertions on the
narrated text confirming every required step is actually present, in the
right order, rather than behavioral tests of a live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.txt.prompts.create_txt import create_txt


class TestCreateTxtPrompt(unittest.TestCase):
    """Tests for the create_txt prompt."""

    def test_returns_substituted_instruction_text(self) -> None:
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_txt("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self) -> None:
        """The returned text must contain a distinctive, stable sentence from the real
        txt/data/txt_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_txt("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool(self) -> None:
        """The prompt must instruct the LLM to check the list_txt tool first."""
        result = create_txt("Some topic")
        self.assertIn("list_txt", result)

    def test_mentions_todowrite_list(self) -> None:
        """The prompt must instruct building a todo list covering the H1 title, the free-form
        body, and the Updates log."""
        result = create_txt("Some topic")
        self.assertIn("todo list", result)
        for section in ("H1", "free-form body", "Updates"):
            self.assertIn(section, result)

    def test_mentions_question_tool(self) -> None:
        """The prompt must instruct using the question tool to elicit information."""
        result = create_txt("Some topic")
        self.assertIn("question", result)

    def test_mentions_no_optional_sections(self) -> None:
        """The prompt must state that the body and the Updates log are both mandatory -- there
        are no optional sections to skip in a free-form text document."""
        result = create_txt("Some topic")
        self.assertIn("no optional sections", result)
        self.assertIn("mandatory", result)

    def test_mentions_boundary_rule(self) -> None:
        """The prompt must narrate the body-boundary rule: the body ends at the first
        top-level ``## Updates`` H2, and no second ``## Updates`` or trailing H2 is allowed."""
        result = create_txt("Some topic")
        self.assertIn("first top-level", result)
        self.assertIn("## Updates", result)

    def test_mentions_template_example_tools_and_conditional_schema(self) -> None:
        """The prompt must point at the get_txt_template/get_txt_example tools and name the
        conditional get_txt_schema fetch."""
        result = create_txt("Some topic")
        self.assertIn("get_txt_template", result)
        self.assertIn("get_txt_example", result)
        self.assertIn("get_txt_schema", result)

    def test_mentions_tool_sequence_in_order(self) -> None:
        """The prompt must mention the list_txt tool, the template/example tools,
        get_txt_schema, and create_txt, in that order, matching the intended sequence."""
        result = create_txt("Some topic")
        markers = [
            "list_txt",
            "get_txt_template",
            "get_txt_schema",
            "create_txt(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_update_txt_for_later_revisions(self) -> None:
        """The prompt must point at the update_txt prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_txt("Some topic")
        self.assertIn("`update_txt` prompt", result)
        self.assertIn('update(id, type="txt", content)', result)
        self.assertIn('set_status(id, type="txt", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self) -> None:
        """The instructional text must come from txt/data/txt_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "txt_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_txt("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_txt("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self) -> None:
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_txt("Some topic")


if __name__ == "__main__":
    unittest.main()
