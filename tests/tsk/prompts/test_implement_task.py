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

"""Tests for the ``implement_task`` ``@mcp.prompt()`` (Task 3.14).

``implement_task`` only returns instructional text -- it never calls
``get_tsk``/``TodoWrite``/``question`` itself -- so these are string-content
assertions on the returned text, not behavioral tests: there is nothing to
execute beyond the prompt function itself.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.tsk.prompts.implement_task import implement_task


class TestImplementTaskPrompt(unittest.TestCase):
    """Tests for the implement_task prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = implement_task("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_tsk_tool(self):
        """The prompt must instruct the LLM to call get_tsk to load the current document."""
        result = implement_task("abc-123")
        self.assertIn("get_tsk(id)", result)

    def test_mentions_building_a_todo_list_from_items(self):
        """The prompt must instruct building a TodoWrite list from the document's items."""
        result = implement_task("abc-123")
        self.assertIn("TodoWrite", result)
        self.assertIn("items", result)

    def test_mentions_question_tool_for_ambiguous_items(self):
        """The prompt must instruct using the question tool to resolve ambiguity."""
        result = implement_task("abc-123")
        self.assertIn("question", result)
        self.assertIn("ambiguous", result)

    def test_mentions_get_tsk_before_todowrite(self):
        """Reading the document must be instructed before building the TodoWrite list."""
        result = implement_task("abc-123")
        self.assertLess(result.index("get_tsk(id)"), result.index("TodoWrite"))

    def test_mentions_update_as_separate_persistence_step(self):
        """The prompt must clarify that persisting completed work is a separate
        generic `update` (type="tsk") call."""
        result = implement_task("abc-123")
        self.assertIn('update(id, type="tsk", content)', result)
        self.assertIn("separate", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from tsk/data/tsk_implement_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "tsk_implement_instructions.md"
            instructions_path.write_text("first $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = implement_task("abc-123")
                instructions_path.write_text("second $id", encoding="utf-8")
                second = implement_task("abc-123")

            self.assertEqual(first, "first abc-123")
            self.assertEqual(second, "second abc-123")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    implement_task("abc-123")


if __name__ == "__main__":
    unittest.main()
