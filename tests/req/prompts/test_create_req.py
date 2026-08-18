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

"""Tests for the ``create_req`` ``@mcp.prompt()`` (Task 3.19)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.req.prompts.create_req import create_req


class TestCreateReqPrompt(unittest.TestCase):
    """Tests for the create_req prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_req("API rate limiting")
        self.assertIn("API rate limiting", result)

    def test_mentions_duplicate_check_resource(self):
        """The prompt must instruct the LLM to check specmgr://req/list first."""
        result = create_req("Some topic")
        self.assertIn("specmgr://req/list", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_req("Some topic")
        self.assertIn("specmgr://req/template", result)
        self.assertIn("specmgr://req/example", result)
        self.assertIn("specmgr://req/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention specmgr://req/list, the template/example
        resources, specmgr://req/schema, and create_req, in that order,
        matching the intended sequence."""
        result = create_req("Some topic")
        markers = [
            "specmgr://req/list",
            "specmgr://req/template",
            "specmgr://req/schema",
            "create_req(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_sections(self):
        """The mandatory REQ sections must all be named in the recap."""
        result = create_req("Some topic")
        for heading in (
            "Characteristics",
            "Level",
            "Source",
        ):
            self.assertIn(heading, result)

    def test_mentions_update_req_for_later_revisions(self):
        """The prompt must point at the update_req prompt for later changes."""
        result = create_req("Some topic")
        self.assertIn("update_req", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from req/data/req_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "req_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_req("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_req("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_req("Some topic")


if __name__ == "__main__":
    unittest.main()
