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

import unittest

from biz.dfch.specmgr.tsk.prompts.create_task import create_task


class TestCreateTaskPrompt(unittest.TestCase):
    """Tests for the create_task prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_task("Migrate widgets to the new registry")
        self.assertIn("Migrate widgets to the new registry", result)

    def test_mentions_duplicate_check_resource(self):
        """The prompt must instruct the LLM to check specmgr://tsk/list first."""
        result = create_task("Some topic")
        self.assertIn("specmgr://tsk/list", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_task("Some topic")
        self.assertIn("specmgr://tsk/template", result)
        self.assertIn("specmgr://tsk/example", result)
        self.assertIn("specmgr://tsk/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention specmgr://tsk/list, the template/example
        resources, specmgr://tsk/schema, and create_tsk, in that order,
        matching the intended sequence."""
        result = create_task("Some topic")
        markers = [
            "specmgr://tsk/list",
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


if __name__ == "__main__":
    unittest.main()
