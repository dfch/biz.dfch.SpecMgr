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

"""Tests for the ``update_dec`` ``@mcp.prompt()`` (Task 4.1, ACC-005).

``update_dec`` (the prompt) only ever returns instructional text -- it never
calls ``get_dec``/``question``/``update``/``set_status`` (the tools) itself
-- so these are string-content/ordering assertions on the narrated text
confirming every required step from the feature README's Design Notes is
actually present, in the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.prompts.update_dec import update_dec
from biz.dfch.specmgr.general.tools import _packaged_data


class TestUpdateDecPrompt(unittest.TestCase):
    """Tests for the update_dec prompt."""

    def test_returns_substituted_id(self):
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = update_dec("id-abc-123")
        self.assertIsInstance(result, str)
        self.assertIn("id-abc-123", result)
        self.assertNotIn("$id", result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text, and no literal
        $instructions placeholder may remain."""
        result = update_dec("id-abc-123", instructions="Change the outcome to option 2.")
        self.assertIn("Change the outcome to option 2.", result)
        self.assertNotIn("$instructions", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must be replaced by the standard fallback telling the LLM to ask
        the user before making any change, not guess."""
        result = update_dec("id-abc-123")
        self.assertIn("(not given -- ask the user before making any change)", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        dec/data/dec_update_instructions.md -- evidence the text comes from packaged data."""
        result = update_dec("id-abc-123")
        self.assertIn("Never assume prior state", result)

    def test_mentions_get_dec_tool_first(self):
        """The prompt must instruct the LLM to call get_dec first,
        before the generic `update` write call."""
        result = update_dec("id-abc-123")
        self.assertIn("get_dec(id)", result)
        self.assertLess(result.index("get_dec(id)"), result.index('update(id, type="dec", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="dec") and `set_status`
        (type="dec") call shapes must be named."""
        result = update_dec("id-abc-123")
        for tool in ('update(id, type="dec", content)', 'set_status(id, type="dec", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_dec(id, raw=True), identify the 1-based inclusive range
        (N+1 is end-of-body), call `update` with begin/end passing only
        the replacement lines; whole-body for multi-section or uncertain
        changes."""
        result = update_dec("id-abc-123")
        self.assertIn("get_dec(id, raw=True)", result)
        self.assertIn("1-based, inclusive line range", result)
        self.assertIn("begin = end = N+1", result)
        self.assertIn('update(id, type="dec", content, begin=..., end=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_dec(id, raw=True)"),
            result.index('update(id, type="dec", content, begin=..., end=...)'),
        )

    def test_mentions_showing_which_sections_are_present(self):
        """The prompt must instruct showing which sections are already present
        vs. empty, and asking which to add or revise."""
        result = " ".join(update_dec("id-abc-123").split())
        self.assertIn("are already present with content and which are still absent", result)
        for section in (
            "## Context and Problem Statement",
            "## Decision Outcome",
            "## Decision Drivers",
            "## Considered Options",
            "## Related Artifacts",
            "## Pros and Cons",
            "## More Information",
            "## Updates",
        ):
            self.assertIn(section, result)

    def test_mentions_eliciting_revisions_via_question_tool(self):
        """The prompt must instruct using the question tool to elicit new/revised text."""
        result = update_dec("id-abc-123")
        self.assertIn("question", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_dec("id-abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_dec("id-abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_set_status_as_separate_optional_followup(self):
        """The generic `set_status` tool (type="dec") must be framed as a separate,
        optional follow-up, with the decision-specific `accepted`/`rejected`/
        `superseded` semantics."""
        result = update_dec("id-abc-123")
        self.assertIn("separate, optional", result)
        self.assertIn("accepted", result)
        self.assertIn("rejected", result)
        self.assertIn("superseded", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from dec/data/dec_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "dec_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_dec("id-abc-123", instructions="Change the outcome to option 2.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_dec("id-abc-123", instructions="Change the outcome to option 2.")

            self.assertEqual(first, "first id-abc-123 / Change the outcome to option 2.")
            self.assertEqual(second, "second id-abc-123 / Change the outcome to option 2.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_dec("id-abc-123")


if __name__ == "__main__":
    unittest.main()
