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

"""Tests for the ``update_set`` ``@mcp.prompt()`` (feat-173-req-iso29148-level-set Phase 180).

``update_set`` (the prompt) only ever returns instructional text -- it
never calls ``get_set``/``question``/``update``/``edit``/``set_status``
(the tools) itself -- so these are string-content/ordering assertions on
the narrated text confirming every required step is actually present, in
the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.set.prompts.update_set import update_set


class TestUpdateSetPrompt(unittest.TestCase):
    """Tests for the update_set prompt."""

    def test_returns_substituted_id(self) -> None:
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = update_set("id-abc-123")
        self.assertIsInstance(result, str)
        self.assertIn("id-abc-123", result)
        self.assertNotIn("$id", result)

    def test_instructions_interpolated_when_given(self) -> None:
        """A given instructions string must appear verbatim in the returned text, and no literal
        $instructions placeholder may remain."""
        result = update_set("id-abc-123", instructions="Mark the notes as final.")
        self.assertIn("Mark the notes as final.", result)
        self.assertNotIn("$instructions", result)

    def test_prompts_for_input_when_instructions_absent(self) -> None:
        """Absent instructions must be replaced by the standard fallback telling the LLM to ask
        the user before making any change, not guess."""
        result = update_set("id-abc-123")
        self.assertIn("(not given -- ask the user before making any change)", result)

    def test_instructions_match_packaged_file(self) -> None:
        """The returned text must contain a distinctive, stable sentence from the real
        set/data/set_update_instructions.md -- evidence the text comes from packaged data."""
        result = update_set("id-abc-123")
        self.assertIn("Never assume prior state", result)

    def test_mentions_get_set_tool_first(self) -> None:
        """The prompt must instruct the LLM to call get_set first,
        before the generic `update` write call."""
        result = update_set("id-abc-123")
        self.assertIn("get_set(id)", result)
        self.assertLess(result.index("get_set(id)"), result.index('update(id, type="set", content)'))

    def test_mentions_all_generic_mutation_tools(self) -> None:
        """The generic `update` (type="set"), `edit` (type="set"), and `set_status`
        (type="set") call shapes must all be named -- set is dispatch-only."""
        result = update_set("id-abc-123")
        for tool in (
            'update(id, type="set", content)',
            'edit(id, type="set", old_str, new_str)',
            'set_status(id, type="set", status)',
        ):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self) -> None:
        """The prompt must teach the line-range flow: read the exact body
        via get_set(id, raw=True, numbered=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_set("id-abc-123")
        self.assertIn("get_set(id, raw=True, numbered=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="set", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_set(id, raw=True, numbered=True)"),
            result.index('update(id, type="set", content, offset=..., limit=...)'),
        )

    def test_mentions_edit_exact_match_flow(self) -> None:
        """The prompt must teach the surgical `edit` flow: byte-exact old_str, uniqueness
        (replace_all), validate-as-whole, and reading the body via get_set(id, raw=True)
        first."""
        result = update_set("id-abc-123")
        self.assertIn("byte-exactly", result)
        self.assertIn("replace_all=True", result)
        self.assertIn("get_set(id, raw=True)", result)

    def test_mentions_showing_what_the_document_holds(self) -> None:
        """The prompt must instruct showing the document's current `## Description` content
        and its `## Items` list, and asking what to add or revise."""
        result = " ".join(update_set("id-abc-123").split())
        self.assertIn("current `## Description` content", result)
        self.assertIn("`## Items` list", result)

    def test_mentions_eliciting_revisions_via_question_tool(self) -> None:
        """The prompt must instruct using the question tool to elicit revisions."""
        result = update_set("id-abc-123")
        self.assertIn("question", result)

    def test_mentions_whole_body_replace_warning(self) -> None:
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_set("id-abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self) -> None:
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_set("id-abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_set_status_as_separate_optional_followup(self) -> None:
        """The generic `set_status` tool (type="set") must be framed as a separate,
        optional follow-up, with the set-specific status vocabulary."""
        result = update_set("id-abc-123")
        self.assertIn("separate, optional", result)
        for status in ("draft", "progress", "done", "review"):
            self.assertIn(status, result)

    def test_mentions_two_section_rule(self) -> None:
        """The prompt must narrate the two-section rule: exactly `## Description` then
        `## Items`, no other H2 introduced, no reordering (both fail validation)."""
        result = update_set("id-abc-123")
        self.assertIn("exactly two H2 sections", result)
        self.assertIn("do not introduce any other H2", result)
        self.assertIn("no `## Owner`", result)

    def test_instructions_loaded_from_packaged_data_file(self) -> None:
        """The instructional text must come from set/data/set_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "set_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_set("id-abc-123", instructions="Mark the notes as final.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_set("id-abc-123", instructions="Mark the notes as final.")

            self.assertEqual(first, "first id-abc-123 / Mark the notes as final.")
            self.assertEqual(second, "second id-abc-123 / Mark the notes as final.")

    def test_raises_file_not_found_when_instructions_missing(self) -> None:
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_set("id-abc-123")


if __name__ == "__main__":
    unittest.main()
