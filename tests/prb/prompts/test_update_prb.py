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

"""Tests for the ``update_prb`` ``@mcp.prompt()`` (Task 3.15, ACC-006).

``update_prb`` (the prompt) only ever returns instructional text -- it never
calls ``get_prb``/``question``/``update``/``set_status`` (the tools) itself
-- so these are string-content/ordering assertions on the narrated text
confirming every required step from the feature README's Design Notes is
actually present, in the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.prb.prompts.update_prb import update_prb


class TestUpdatePrbPrompt(unittest.TestCase):
    """Tests for the update_prb prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_prb("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_prb_tool_first(self):
        """The prompt must instruct the LLM to call get_prb first,
        before the generic `update` write call."""
        result = update_prb("abc-123")
        self.assertIn("get_prb(id)", result)
        self.assertLess(result.index("get_prb(id)"), result.index('update(id, type="prb", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="prb") and `set_status`
        (type="prb") call shapes must be named."""
        result = update_prb("abc-123")
        for tool in ('update(id, type="prb", content)', 'set_status(id, type="prb", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_prb(id, raw=True), identify the 1-based inclusive range
        (N+1 is end-of-body), call `update` with begin/end passing only
        the replacement lines; whole-body for multi-section or uncertain
        changes."""
        result = update_prb("abc-123")
        self.assertIn("get_prb(id, raw=True)", result)
        self.assertIn("1-based, inclusive line range", result)
        self.assertIn("begin = end = N+1", result)
        self.assertIn('update(id, type="prb", content, begin=..., end=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_prb(id, raw=True)"),
            result.index('update(id, type="prb", content, begin=..., end=...)'),
        )

    def test_mentions_showing_which_questions_are_answered(self):
        """The prompt must instruct showing which of the 7 questions are already answered."""
        result = update_prb("abc-123")
        self.assertIn("already have answers", result)
        for heading in (
            "What Is the Problem?",
            "Why Is It a Problem?",
            "Where Is the Problem Observed?",
            "Who Is Impacted?",
            "When Was the Problem First Observed?",
            "How Is the Problem Observed?",
            "How Often Is the Problem Observed?",
        ):
            self.assertIn(heading, result)

    def test_mentions_full_resynthesis_not_append(self):
        """The prompt must call out that Summary regeneration is a full re-synthesis, not an append."""
        result = update_prb("abc-123")
        self.assertIn("full re-synthesis", result)
        self.assertIn("not an append", result)

    def test_mentions_redrafting_and_confirming_gap(self):
        """The prompt must instruct re-drafting Gap and confirming it via the question tool."""
        result = update_prb("abc-123")
        self.assertIn("Re-draft", result)
        self.assertIn("confirm", result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_prb("abc-123", instructions="Add a new Impact statement.")
        self.assertIn("Add a new Impact statement.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_prb("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_prb("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_prb("abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_set_status_as_separate_optional_followup(self):
        """The generic `set_status` tool (type="prb") must be framed as a
        separate, optional follow-up."""
        result = update_prb("abc-123")
        self.assertIn("separate, optional", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from prb/data/prb_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "prb_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_prb("abc-123", instructions="Add a new Impact statement.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_prb("abc-123", instructions="Add a new Impact statement.")

            self.assertEqual(first, "first abc-123 / Add a new Impact statement.")
            self.assertEqual(second, "second abc-123 / Add a new Impact statement.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_prb("abc-123")


if __name__ == "__main__":
    unittest.main()
