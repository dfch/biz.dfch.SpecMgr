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

"""Tests for the ``create_task`` ``@mcp.prompt()`` (Task 3.13)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.tsk.prompts.create_task import create_task


class TestCreateTaskPrompt(unittest.TestCase):
    """Tests for the create_task prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_task("Migrate widgets to the new registry")
        self.assertIn("Migrate widgets to the new registry", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_tsk tool first."""
        result = create_task("Some topic")
        self.assertIn("list_tsk", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_task("Some topic")
        self.assertIn("specmgr://tsk/template", result)
        self.assertIn("specmgr://tsk/example", result)
        self.assertIn("specmgr://tsk/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_tsk tool, the template/example
        resources, specmgr://tsk/schema, and create_tsk, in that order,
        matching the intended sequence."""
        result = create_task("Some topic")
        markers = [
            "list_tsk",
            "specmgr://tsk/template",
            "specmgr://tsk/schema",
            "create_tsk(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_sections(self):
        """The mandatory TSK sections must all be named in the recap."""
        result = create_task("Some topic")
        for heading in (
            "Recent Updates",
            "checklist",
        ):
            self.assertIn(heading, result)

    def test_mentions_recent_updates_min_length_requirement(self):
        """The prompt must explicitly call out the min_length=1 Recent Updates constraint."""
        result = create_task("Some topic")
        self.assertIn("min_length", result)

    def test_mentions_update_task_for_later_revisions(self):
        """The prompt must point at the update_task prompt for later changes."""
        result = create_task("Some topic")
        self.assertIn("update_task", result)

    def test_mentions_implement_task_for_working_the_checklist(self):
        """The prompt must point at the implement_task prompt for working the checklist."""
        result = create_task("Some topic")
        self.assertIn("implement_task", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from tsk/data/tsk_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "tsk_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_task("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_task("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_task("Some topic")


if __name__ == "__main__":
    unittest.main()
