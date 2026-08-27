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

"""Tests for the ``create_dec`` ``@mcp.prompt()`` (Task 4.1, ACC-005).

``create_dec`` (the prompt) only ever returns instructional text -- it never
calls ``TodoWrite``/``question``/``list_dec``/``create_dec`` (the tool)
itself -- so these are string-content/ordering assertions on the narrated
text confirming every required step from the feature README's Design Notes
is actually present, in the right order, rather than behavioral tests of a
live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.prompts.create_dec import create_dec
from biz.dfch.specmgr.general.tools import _packaged_data


class TestCreateDecPrompt(unittest.TestCase):
    """Tests for the create_dec prompt."""

    def test_returns_substituted_instruction_text(self):
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_dec("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        dec/data/dec_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_dec("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_dec tool first."""
        result = create_dec("Some topic")
        self.assertIn("list_dec", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a todo list covering the mandatory
        `context` + `outcome` + each optional section."""
        result = create_dec("Some topic")
        self.assertIn("todo list", result)
        for section in (
            "Context and Problem Statement",
            "Decision Drivers",
            "Considered Options",
            "Decision Outcome",
            "Related Artifacts",
            "Pros and Cons",
            "More Information",
            "Updates",
        ):
            self.assertIn(section, result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit information."""
        result = create_dec("Some topic")
        self.assertIn("question", result)

    def test_mentions_allowing_skip_for_optional_sections(self):
        """The prompt must explicitly allow the user to skip any optional field."""
        result = create_dec("Some topic")
        self.assertIn("skip", result)

    def test_does_not_narrate_the_old_adr_options_heading(self):
        """The prompt must not narrate the ADR heading `## Pros and Cons of the Options` as a
        DEC heading line -- that heading is rejected by the DEC schema (the prompt may mention
        it in prose only to forbid it, which it does as a code span, never as its own heading)."""
        result = create_dec("Some topic")
        heading_lines = [line for line in result.splitlines() if line.strip() == "## Pros and Cons of the Options"]
        self.assertEqual(heading_lines, [])
        normalized = " ".join(result.split())
        self.assertIn("is not part of this schema and must not be used", normalized)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_dec("Some topic")
        self.assertIn("specmgr://dec/template", result)
        self.assertIn("specmgr://dec/example", result)
        self.assertIn("specmgr://dec/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_dec tool, the template/example
        resources, specmgr://dec/schema, and create_dec, in that order,
        matching the intended sequence."""
        result = create_dec("Some topic")
        markers = [
            "list_dec",
            "specmgr://dec/template",
            "specmgr://dec/schema",
            "create_dec(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_mandatory_fields(self):
        """The mandatory DEC fields (context + outcome) must be named as the mandatory ones,
        elicited before each optional field."""
        result = " ".join(create_dec("Some topic").split())
        self.assertIn("mandatory fields first -- the context and the outcome", result)
        self.assertIn("then each optional field in turn", result)

    def test_mentions_update_dec_for_later_revisions(self):
        """The prompt must point at the update_dec prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_dec("Some topic")
        self.assertIn("`update_dec` prompt", result)
        self.assertIn('update(id, type="dec", content)', result)
        self.assertIn('set_status(id, type="dec", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from dec/data/dec_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "dec_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_dec("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_dec("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_dec("Some topic")


if __name__ == "__main__":
    unittest.main()
