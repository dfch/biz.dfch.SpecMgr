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

"""Tests for the ``create_uc`` ``@mcp.prompt()`` (feat-57-uc-commands)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.uc.prompts.create_uc import create_uc


class TestCreateUcPrompt(unittest.TestCase):
    """Tests for the create_uc prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_uc("Buyer purchases items")
        self.assertIn("Buyer purchases items", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_uc tool first."""
        result = create_uc("Some topic")
        self.assertIn("list_uc", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_uc("Some topic")
        self.assertIn("specmgr://uc/template", result)
        self.assertIn("specmgr://uc/example", result)
        self.assertIn("specmgr://uc/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_uc tool, the template/schema
        resources, and create_uc, in that order, matching the intended
        sequence."""
        result = create_uc("Some topic")
        markers = [
            "list_uc",
            "specmgr://uc/template",
            "specmgr://uc/schema",
            "create_uc(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_sections(self):
        """The mandatory UC sections must all be named in the recap."""
        result = create_uc("Some topic")
        for heading in (
            "Goal in Context",
            "Scope",
            "Level",
            "Preconditions",
            "Success End Condition",
            "Primary Actor",
            "Trigger",
        ):
            self.assertIn(heading, result)

    def test_mentions_update_uc_for_later_revisions(self):
        """The prompt must point at the update_uc prompt for later changes,
        with the generic update/set_status/set_classification tools as the
        direct alternative."""
        result = create_uc("Some topic")
        self.assertIn("`update_uc` prompt", result)
        self.assertIn('update(id, type="uc", content)', result)
        self.assertIn('set_status(id, type="uc", status)', result)
        self.assertIn('set_classification(id, type="uc", classification)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from uc/data/uc_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "uc_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_uc("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_uc("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_uc("Some topic")


if __name__ == "__main__":
    unittest.main()
