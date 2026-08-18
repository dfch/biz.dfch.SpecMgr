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

"""Tests for the ``update_qa`` ``@mcp.prompt()``."""

import unittest

from biz.dfch.specmgr.qa.prompts.update_qa import update_qa


class TestUpdateQaPrompt(unittest.TestCase):
    """Tests for the update_qa prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_qa("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_qa_tool_first(self):
        """The prompt must instruct the LLM to call get_qa first,
        before the update_qa write tool."""
        result = update_qa("abc-123")
        self.assertIn("get_qa(id)", result)
        self.assertLess(result.index("get_qa(id)"), result.index("update_qa(id, content)"))

    def test_mentions_both_mutation_tools(self):
        """Both update_qa and set_status_qa must be named."""
        result = update_qa("abc-123")
        for tool in ("update_qa", "set_status_qa"):
            self.assertIn(tool, result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_qa("abc-123", instructions="Change the status to done.")
        self.assertIn("Change the status to done.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_qa("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for update_qa must be present."""
        result = update_qa("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update_qa(self):
        """The prompt must clarify that update_qa never changes status."""
        result = update_qa("abc-123")
        self.assertIn("update_qa` never accepts or changes `status`", result)

    def test_mentions_valid_status_values(self):
        """The four valid status values must be named."""
        result = update_qa("abc-123")
        for status in ("draft", "active", "done", "cancelled"):
            self.assertIn(status, result)


if __name__ == "__main__":
    unittest.main()
