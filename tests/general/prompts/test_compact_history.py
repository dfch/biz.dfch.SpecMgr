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

"""Tests for the ``compact_history`` ``@mcp.prompt()``."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.prompts.compact_history import compact_history
from biz.dfch.specmgr.general.tools import _packaged_data


class TestCompactHistoryPrompt(unittest.TestCase):
    """Tests for the compact_history prompt."""

    def test_mentions_feature_id(self):
        """The feature_id argument must be interpolated into the returned text."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("feat-7-various-improvements", result)

    def test_mentions_readme_path(self):
        """The prompt must point at the feature folder's README.md."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn(".specmgr/feat/feat-7-various-improvements/README.md", result)

    def test_mentions_history_md(self):
        """The prompt must instruct the LLM about the sibling history.md file."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("history.md", result)

    def test_mentions_recent_updates_section(self):
        """The prompt must target the Recent Updates section specifically."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("Recent Updates", result)

    def test_mentions_pointer_line_convention(self):
        """The prompt must describe the exact pointer-line wording convention."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("See `history.md` for updates before", result)

    def test_mentions_frontmatter_updated_bump(self):
        """The prompt must instruct bumping the frontmatter updated field."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("frontmatter `updated`", result)

    def test_mentions_question_tool(self):
        """The question tool must be named for resolving cutoff ambiguity."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("`question` tool", result)

    def test_no_dedicated_mcp_tool_note(self):
        """The prompt must note there is no dedicated specmgr tool for feature folders."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("no dedicated specmgr", result)

    def test_cutoff_hint_interpolated_when_given(self):
        """A given cutoff_hint string must appear verbatim in the returned text."""
        result = compact_history("feat-7-various-improvements", cutoff_hint="keep the last 3 entries")
        self.assertIn("keep the last 3 entries", result)

    def test_prompts_for_input_when_cutoff_hint_absent(self):
        """Absent cutoff_hint must tell the LLM to ask the user, not guess."""
        result = compact_history("feat-7-various-improvements")
        self.assertIn("ask the user", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from
        general/data/general_compact_history_instructions.md, not an inline
        Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "general_compact_history_instructions.md"
            instructions_path.write_text("first $feature_id / $cutoff_hint", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = compact_history("feat-7-various-improvements", cutoff_hint="keep last 3")
                instructions_path.write_text("second $feature_id / $cutoff_hint", encoding="utf-8")
                second = compact_history("feat-7-various-improvements", cutoff_hint="keep last 3")

            self.assertEqual(first, "first feat-7-various-improvements / keep last 3")
            self.assertEqual(second, "second feat-7-various-improvements / keep last 3")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    compact_history("feat-7-various-improvements")


if __name__ == "__main__":
    unittest.main()
