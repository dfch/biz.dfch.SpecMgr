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

"""Tests for the ``update_task`` ``@mcp.prompt()`` (Task 3.13)."""

import unittest

from biz.dfch.specmgr.tsk.prompts.update_task import update_task


class TestUpdateTaskPrompt(unittest.TestCase):
    """Tests for the update_task prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_task("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_tsk_tool_first(self):
        """The prompt must instruct the LLM to call get_tsk first,
        before the update_tsk write tool."""
        result = update_task("abc-123")
        self.assertIn("get_tsk(id)", result)
        self.assertLess(result.index("get_tsk(id)"), result.index("update_tsk(id, content)"))

    def test_mentions_both_mutation_tools(self):
        """Both update_tsk and set_status_tsk must be named."""
        result = update_task("abc-123")
        for tool in ("update_tsk", "set_status_tsk"):
            self.assertIn(tool, result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_task("abc-123", instructions="Mark the first item as done.")
        self.assertIn("Mark the first item as done.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_task("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for update_tsk must be present."""
        result = update_task("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update_tsk(self):
        """The prompt must clarify that update_tsk never changes status."""
        result = update_task("abc-123")
        self.assertIn("update_tsk` never accepts or changes `status`", result)

    def test_mentions_recent_updates_min_length_constraint(self):
        """The prompt must call out the min_length=1 Recent Updates constraint."""
        result = update_task("abc-123")
        self.assertIn("min_length", result)

    def test_mentions_implement_task_for_working_the_checklist(self):
        """The prompt must point at the implement_task prompt for working the checklist itself."""
        result = update_task("abc-123")
        self.assertIn("implement_task", result)


if __name__ == "__main__":
    unittest.main()
