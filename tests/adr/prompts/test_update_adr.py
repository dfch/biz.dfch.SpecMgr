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

"""Tests for the ``update_adr`` ``@mcp.prompt()`` (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.adr.prompts.update_adr import update_adr
from biz.dfch.specmgr.general.tools import _packaged_data


class TestUpdateAdrPrompt(unittest.TestCase):
    """Tests for the update_adr prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_adr("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_adr_first(self):
        """The prompt must instruct the LLM to read current state via get_adr first."""
        result = update_adr("abc-123")
        self.assertIn("get_adr", result)
        self.assertLess(result.index("get_adr"), result.index("validate_adr"))

    def test_mentions_all_mutation_tools(self):
        """Every mutation tool the LLM might need must be named somewhere."""
        result = update_adr("abc-123")
        for tool in (
            "update_section",
            "update_frontmatter",
            "set_status",
            "option_create",
            "option_update",
            "option_delete",
            "validate_adr",
        ):
            self.assertIn(tool, result)

    def test_mentions_generic_set_status_with_type_adr(self):
        """The set_status call site must show the generic call shape,
        always with type="adr" for an ADR."""
        result = update_adr("abc-123")
        self.assertIn('set_status(id, type="adr", status, superseded_by=...)', result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_adr("abc-123", instructions="Change the status to accepted.")
        self.assertIn("Change the status to accepted.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_adr("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_frontmatter_whole_object_replace_warning(self):
        """The whole-object-replace caveat for update_frontmatter must be present."""
        result = update_adr("abc-123")
        self.assertIn("whole-object replace", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from adr/data/adr_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "adr_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_adr("abc-123", instructions="Change the status to accepted.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_adr("abc-123", instructions="Change the status to accepted.")

            self.assertEqual(first, "first abc-123 / Change the status to accepted.")
            self.assertEqual(second, "second abc-123 / Change the status to accepted.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_adr("abc-123")


if __name__ == "__main__":
    unittest.main()
