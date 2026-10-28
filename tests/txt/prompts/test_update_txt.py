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

"""Tests for the ``update_txt`` ``@mcp.prompt()`` (feat-229-txt Phase 120).

``update_txt`` (the prompt) only ever returns instructional text -- it
never calls ``get_txt``/``question``/``update``/``edit``/``set_status``
(the tools) itself -- so these are string-content/ordering assertions on
the narrated text confirming every required step is actually present, in
the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.txt.prompts.update_txt import update_txt


class TestUpdateTxtPrompt(unittest.TestCase):
    """Tests for the update_txt prompt."""

    def test_returns_substituted_id(self) -> None:
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = update_txt("id-abc-123")
        self.assertIsInstance(result, str)
        self.assertIn("id-abc-123", result)
        self.assertNotIn("$id", result)

    def test_instructions_interpolated_when_given(self) -> None:
        """A given instructions string must appear verbatim in the returned text, and no literal
        $instructions placeholder may remain."""
        result = update_txt("id-abc-123", instructions="Mark the notes as final.")
        self.assertIn("Mark the notes as final.", result)
        self.assertNotIn("$instructions", result)

    def test_prompts_for_input_when_instructions_absent(self) -> None:
        """Absent instructions must be replaced by the standard fallback telling the LLM to ask
        the user before making any change, not guess."""
        result = update_txt("id-abc-123")
        self.assertIn("(not given -- ask the user before making any change)", result)

    def test_instructions_match_packaged_file(self) -> None:
        """The returned text must contain a distinctive, stable sentence from the real
        txt/data/txt_update_instructions.md -- evidence the text comes from packaged data."""
        result = update_txt("id-abc-123")
        self.assertIn("Never assume prior state", result)

    def test_mentions_get_txt_tool_first(self) -> None:
        """The prompt must instruct the LLM to call get_txt first,
        before the generic `update` write call."""
        result = update_txt("id-abc-123")
        self.assertIn("get_txt(id)", result)
        self.assertLess(result.index("get_txt(id)"), result.index('update(id, type="txt", content)'))

    def test_mentions_all_generic_mutation_tools(self) -> None:
        """The generic `update` (type="txt"), `edit` (type="txt"), and `set_status`
        (type="txt") call shapes must all be named -- TXT is dispatch-only."""
        result = update_txt("id-abc-123")
        for tool in (
            'update(id, type="txt", content)',
            'edit(id, type="txt", old_str, new_str)',
            'set_status(id, type="txt", status)',
        ):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self) -> None:
        """The prompt must teach the line-range flow: read the exact body
        via get_txt(id, raw=True, numbered=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_txt("id-abc-123")
        self.assertIn("get_txt(id, raw=True, numbered=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="txt", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_txt(id, raw=True, numbered=True)"),
            result.index('update(id, type="txt", content, offset=..., limit=...)'),
        )

    def test_mentions_edit_exact_match_flow(self) -> None:
        """The prompt must teach the surgical `edit` flow: byte-exact old_str, uniqueness
        (replace_all), validate-as-whole, and reading the body via get_txt(id, raw=True)
        first."""
        result = update_txt("id-abc-123")
        self.assertIn("byte-exactly", result)
        self.assertIn("replace_all=True", result)
        self.assertIn("get_txt(id, raw=True)", result)

    def test_mentions_showing_what_the_document_holds(self) -> None:
        """The prompt must instruct showing the document's current free-form body and its
        Updates log entries, and asking what to add or revise."""
        result = " ".join(update_txt("id-abc-123").split())
        self.assertIn("current free-form body", result)
        self.assertIn("## Updates", result)

    def test_mentions_eliciting_revisions_via_question_tool(self) -> None:
        """The prompt must instruct using the question tool to elicit revisions."""
        result = update_txt("id-abc-123")
        self.assertIn("question", result)

    def test_mentions_whole_body_replace_warning(self) -> None:
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_txt("id-abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self) -> None:
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_txt("id-abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_set_status_as_separate_optional_followup(self) -> None:
        """The generic `set_status` tool (type="txt") must be framed as a separate,
        optional follow-up, with the TXT-specific status vocabulary."""
        result = update_txt("id-abc-123")
        self.assertIn("separate, optional", result)
        self.assertIn("draft", result)
        self.assertIn("progress", result)
        self.assertIn("done", result)

    def test_mentions_boundary_rule(self) -> None:
        """The prompt must narrate the body-boundary rule: no second ``## Updates`` and no
        other H2 after it (both fail validation)."""
        result = update_txt("id-abc-123")
        self.assertIn("first top-level", result)
        self.assertIn("second `## Updates`", result)

    def test_instructions_loaded_from_packaged_data_file(self) -> None:
        """The instructional text must come from txt/data/txt_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "txt_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_txt("id-abc-123", instructions="Mark the notes as final.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_txt("id-abc-123", instructions="Mark the notes as final.")

            self.assertEqual(first, "first id-abc-123 / Mark the notes as final.")
            self.assertEqual(second, "second id-abc-123 / Mark the notes as final.")

    def test_raises_file_not_found_when_instructions_missing(self) -> None:
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_txt("id-abc-123")


if __name__ == "__main__":
    unittest.main()
