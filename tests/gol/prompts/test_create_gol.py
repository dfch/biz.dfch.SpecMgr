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

"""Tests for the ``create_gol`` ``@mcp.prompt()`` (Task 3.14, ACC-006).

``create_gol`` (the prompt) only ever returns instructional text -- it never
calls ``TodoWrite``/``question``/``list_gol``/``create_gol`` (the tool)
itself -- so these are string-content/ordering assertions on the narrated
text confirming every required step from the feature README's Design Notes
is actually present, in the right order, rather than behavioral tests of a
live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.gol.prompts.create_gol import create_gol


class TestCreateGolPrompt(unittest.TestCase):
    """Tests for the create_gol prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_gol("Competitive engines for the next vehicle generation")
        self.assertIn("Competitive engines for the next vehicle generation", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_gol tool first."""
        result = create_gol("Some topic")
        self.assertIn("list_gol", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a todo list covering the goal
        `statement` + `Source` + each optional section."""
        result = create_gol("Some topic")
        self.assertIn("todo list", result)
        for section in (
            "statement",
            "Source",
            "Description",
            "Priority",
            "Tags",
            "Related Artifacts",
            "More Information",
            "Notes",
        ):
            self.assertIn(section, result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit information."""
        result = create_gol("Some topic")
        self.assertIn("question", result)

    def test_mentions_allowing_skip_for_optional_sections(self):
        """The prompt must explicitly allow the user to skip any optional field."""
        result = create_gol("Some topic")
        self.assertIn("skip", result)

    def test_mentions_no_characteristics_or_level_section(self):
        """The prompt must not narrate `## Characteristics`/`## Level` heading lines as part of the
        structure recap -- both are deliberately excluded by design (REQ-level attributes),
        though the prompt is allowed to explain the exclusion in prose (which does mention both
        by name, quoted as code spans, never as their own heading line)."""
        result = create_gol("Some topic")
        for heading in ("## Characteristics", "## Level"):
            heading_lines = [line for line in result.splitlines() if line.strip() == heading]
            self.assertEqual(heading_lines, [], heading)
        self.assertIn("No `## Characteristics` section exists", result)
        self.assertIn("no `## Level` section", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_gol("Some topic")
        self.assertIn("specmgr://gol/template", result)
        self.assertIn("specmgr://gol/example", result)
        self.assertIn("specmgr://gol/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_gol tool, the template/example
        resources, specmgr://gol/schema, and create_gol, in that order,
        matching the intended sequence."""
        result = create_gol("Some topic")
        markers = [
            "list_gol",
            "specmgr://gol/template",
            "specmgr://gol/schema",
            "create_gol(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_fields(self):
        """The mandatory GOL fields (statement + Source) must be named as the mandatory ones,
        elicited before each optional field."""
        result = " ".join(create_gol("Some topic").split())
        self.assertIn("mandatory fields first -- the goal statement and the source", result)
        self.assertIn("then each optional field in turn", result)

    def test_mentions_update_gol_for_later_revisions(self):
        """The prompt must point at the update_gol prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_gol("Some topic")
        self.assertIn("`update_gol` prompt", result)
        self.assertIn('update(id, type="gol", content)', result)
        self.assertIn('set_status(id, type="gol", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from gol/data/gol_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "gol_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_gol("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_gol("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_gol("Some topic")


if __name__ == "__main__":
    unittest.main()
