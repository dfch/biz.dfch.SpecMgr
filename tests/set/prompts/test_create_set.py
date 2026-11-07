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

"""Tests for the ``create_set`` ``@mcp.prompt()`` (feat-173-req-iso29148-level-set Phase 180).

``create_set`` (the prompt) only ever returns instructional text -- it
never calls ``TodoWrite``/``question``/``list_set``/``create_set`` (the
tool) itself -- so these are string-content/ordering assertions on the
narrated text confirming every required step is actually present, in the
right order, rather than behavioral tests of a live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.set.prompts.create_set import create_set


class TestCreateSetPrompt(unittest.TestCase):
    """Tests for the create_set prompt."""

    def test_returns_substituted_instruction_text(self) -> None:
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_set("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self) -> None:
        """The returned text must contain a distinctive, stable sentence from the real
        set/data/set_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_set("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool(self) -> None:
        """The prompt must instruct the LLM to check the list_set tool first."""
        result = create_set("Some topic")
        self.assertIn("list_set", result)

    def test_mentions_todowrite_list(self) -> None:
        """The prompt must instruct building a todo list covering the H1 title, the
        `## Description` content, and the `## Items` list."""
        result = create_set("Some topic")
        self.assertIn("todo list", result)
        for section in ("H1", "## Description", "## Items"):
            self.assertIn(section, result)

    def test_mentions_question_tool(self) -> None:
        """The prompt must instruct using the question tool to elicit information."""
        result = create_set("Some topic")
        self.assertIn("question", result)

    def test_mentions_no_other_sections(self) -> None:
        """The prompt must state that both sections are mandatory and that no other section
        exists (no `## Owner`, no `## Source`, no `## Tags`, no `## More Information`)."""
        result = create_set("Some topic")
        self.assertIn("mandatory", result)
        self.assertIn("no other sections", result)
        for section in ("## Owner", "## Source", "## Tags", "## More Information"):
            self.assertIn(section, result)

    def test_mentions_binding_section_order(self) -> None:
        """The prompt must narrate the binding section order H1 -> Description -> Items and
        that any further H2 is rejected."""
        result = create_set("Some topic")
        self.assertIn("Section order is binding", result)
        self.assertIn("H1 -> Description -> Items", result)
        self.assertIn("any further H2 is rejected", result)

    def test_mentions_template_example_tools_and_conditional_schema(self) -> None:
        """The prompt must point at the get_set_template/get_set_example tools and name the
        conditional get_set_schema fetch."""
        result = create_set("Some topic")
        self.assertIn("get_set_template", result)
        self.assertIn("get_set_example", result)
        self.assertIn("get_set_schema", result)

    def test_mentions_tool_sequence_in_order(self) -> None:
        """The prompt must mention the list_set tool, the template/example tools,
        get_set_schema, and create_set, in that order, matching the intended sequence."""
        result = create_set("Some topic")
        markers = [
            "list_set",
            "get_set_template",
            "get_set_schema",
            "create_set(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_update_set_for_later_revisions(self) -> None:
        """The prompt must point at the update_set prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_set("Some topic")
        self.assertIn("`update_set` prompt", result)
        self.assertIn('update(id, type="set", content)', result)
        self.assertIn('set_status(id, type="set", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self) -> None:
        """The instructional text must come from set/data/set_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "set_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_set("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_set("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self) -> None:
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_set("Some topic")


if __name__ == "__main__":
    unittest.main()
