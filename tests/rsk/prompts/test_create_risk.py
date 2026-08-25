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

"""Tests for the ``create_risk`` ``@mcp.prompt()`` (Task 3.13)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.rsk.prompts.create_risk import create_risk


class TestCreateRiskPrompt(unittest.TestCase):
    """Tests for the create_risk prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_risk("Untrusted file uploads parsed by an unmaintained library")
        self.assertIn("Untrusted file uploads parsed by an unmaintained library", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_rsk tool first."""
        result = create_risk("Some topic")
        self.assertIn("list_rsk", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_risk("Some topic")
        self.assertIn("specmgr://rsk/template", result)
        self.assertIn("specmgr://rsk/example", result)
        self.assertIn("specmgr://rsk/schema", result)

    def test_mentions_domain_knowledge_resources(self):
        """The prompt must point at the TARA and risk-matrix domain-knowledge resources."""
        result = create_risk("Some topic")
        self.assertIn("specmgr://rsk/tara", result)
        self.assertIn("specmgr://rsk/risk-matrix", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_rsk tool, the template/example
        resources, specmgr://rsk/schema, and create_rsk, in that order,
        matching the intended sequence."""
        result = create_risk("Some topic")
        markers = [
            "list_rsk",
            "specmgr://rsk/template",
            "specmgr://rsk/schema",
            "create_rsk(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_sections(self):
        """The mandatory RSK sections must all be named in the recap."""
        result = create_risk("Some topic")
        for heading in (
            "Cause",
            "Trigger",
            "Consequence",
            "Scope",
            "Initial Assessment",
            "Strategy",
            "Mitigation",
            "Residual Assessment",
        ):
            self.assertIn(heading, result)

    def test_mentions_tara_words(self):
        """The four TARA strategy words must all be named."""
        result = create_risk("Some topic")
        for word in ("transfer", "accept", "reduce", "avoid"):
            self.assertIn(word, result)

    def test_mentions_update_risk_for_later_revisions(self):
        """The prompt must point at the update_risk prompt for later changes."""
        result = create_risk("Some topic")
        self.assertIn("update_risk", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from rsk/data/rsk_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "rsk_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_risk("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_risk("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_risk("Some topic")


if __name__ == "__main__":
    unittest.main()
