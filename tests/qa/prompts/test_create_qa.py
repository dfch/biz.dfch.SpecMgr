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

"""Tests for the ``create_qa`` ``@mcp.prompt()``."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.qa.prompts.create_qa import create_qa


class TestCreateQaPrompt(unittest.TestCase):
    """Tests for the create_qa prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_qa("Widget registry migration")
        self.assertIn("Widget registry migration", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_qa tool first."""
        result = create_qa("Some topic")
        self.assertIn("list_qa", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_qa("Some topic")
        self.assertIn("specmgr://qa/template", result)
        self.assertIn("specmgr://qa/example", result)
        self.assertIn("specmgr://qa/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_qa tool, the template/example
        resources, specmgr://qa/schema, and create_qa, in that order,
        matching the intended sequence."""
        result = create_qa("Some topic")
        markers = [
            "list_qa",
            "specmgr://qa/template",
            "specmgr://qa/schema",
            "create_qa(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_all_nine_iso25010_characteristics(self):
        """All nine ISO/IEC 25010:2023 characteristic headings must be named."""
        result = create_qa("Some topic")
        for heading in (
            "Functional Suitability",
            "Performance Efficiency",
            "Compatibility",
            "Interaction Capability",
            "Reliability",
            "Security",
            "Maintainability",
            "Flexibility",
            "Safety",
        ):
            self.assertIn(heading, result)

    def test_mentions_general_and_more_information_sections(self):
        """The `General` and `More Information` sections must be named."""
        result = create_qa("Some topic")
        self.assertIn("## General", result)
        self.assertIn("### Introduction", result)
        self.assertIn("### Raw Requirements", result)
        self.assertIn("## More Information", result)

    def test_mentions_update_qa_for_later_revisions(self):
        """The prompt must point at the update_qa prompt for later changes."""
        result = create_qa("Some topic")
        self.assertIn("update_qa", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from qa/data/qa_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "qa_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_qa("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_qa("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_qa("Some topic")


if __name__ == "__main__":
    unittest.main()
