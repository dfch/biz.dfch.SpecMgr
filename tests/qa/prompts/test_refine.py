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

"""Tests for the ``refine`` ``@mcp.prompt()``."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.qa.prompts.refine import refine


class TestRefinePrompt(unittest.TestCase):
    """Tests for the refine prompt."""

    def test_mentions_id_or_name(self):
        """The id_or_name argument must be interpolated into the returned text."""
        result = refine("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_list_qa_tool_for_lookup(self):
        """The prompt must instruct the LLM to resolve id/title via the list_qa tool."""
        result = refine("abc-123")
        self.assertIn("list_qa", result)

    def test_mentions_get_qa_before_update_qa(self):
        """get_qa must be called before update_qa."""
        result = refine("abc-123")
        self.assertIn("get_qa(id)", result)
        self.assertLess(result.index("get_qa(id)"), result.index("update_qa(id,"))

    def test_mentions_iso25010_resource(self):
        """The prompt must instruct the LLM to look up characteristic definitions."""
        result = refine("abc-123")
        self.assertIn("specmgr://iso25010", result)

    def test_mentions_all_nine_characteristics(self):
        """All nine ISO/IEC 25010:2023 characteristics must be named as selectable options."""
        result = refine("abc-123")
        for characteristic in (
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
            self.assertIn(characteristic, result)

    def test_mentions_response_placeholder(self):
        """The literal empty-answer placeholder must be present."""
        result = refine("abc-123")
        self.assertIn("_(awaiting response)_", result)

    def test_scope_interpolated_when_given(self):
        """A given scope string must appear verbatim in the returned text."""
        result = refine("abc-123", scope="5 questions each about Security, Maintainability")
        self.assertIn("5 questions each about Security, Maintainability", result)

    def test_prompts_for_input_when_scope_absent(self):
        """Absent scope must tell the LLM to ask the user, not guess."""
        result = refine("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_question_tool(self):
        """The question tool must be named for resolving ambiguity."""
        result = refine("abc-123")
        self.assertIn("`question` tool", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for update_qa must be present."""
        result = refine("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_resolve_command_as_next_step(self):
        """The prompt must tell the user to run /resolve next, without running it itself."""
        result = refine("abc-123")
        self.assertIn("/resolve", result)
        self.assertIn("Do not attempt to run `/resolve` yourself", result)

    def test_never_touch_existing_pairs(self):
        """Existing Q&A pairs must not be modified -- only new pairs appended."""
        result = refine("abc-123")
        self.assertIn("Never touch", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from qa/data/qa_refine_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "qa_refine_instructions.md"
            instructions_path.write_text("first $id_or_name / $scope", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = refine("abc-123", scope="5 questions about Security")
                instructions_path.write_text("second $id_or_name / $scope", encoding="utf-8")
                second = refine("abc-123", scope="5 questions about Security")

            self.assertEqual(first, "first abc-123 / 5 questions about Security")
            self.assertEqual(second, "second abc-123 / 5 questions about Security")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    refine("abc-123")


if __name__ == "__main__":
    unittest.main()
