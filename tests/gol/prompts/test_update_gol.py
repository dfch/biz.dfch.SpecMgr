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

"""Tests for the ``update_gol`` ``@mcp.prompt()`` (Task 3.15, ACC-006).

``update_gol`` (the prompt) only ever returns instructional text -- it never
calls ``get_gol``/``question``/``update``/``set_status`` (the tools) itself
-- so these are string-content/ordering assertions on the narrated text
confirming every required step from the feature README's Design Notes is
actually present, in the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.gol.prompts.update_gol import update_gol


class TestUpdateGolPrompt(unittest.TestCase):
    """Tests for the update_gol prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_gol("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_gol_tool_first(self):
        """The prompt must instruct the LLM to call get_gol first,
        before the generic `update` write call."""
        result = update_gol("abc-123")
        self.assertIn("get_gol(id)", result)
        self.assertLess(result.index("get_gol(id)"), result.index('update(id, type="gol", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="gol") and `set_status`
        (type="gol") call shapes must be named."""
        result = update_gol("abc-123")
        for tool in ('update(id, type="gol", content)', 'set_status(id, type="gol", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_gol(id, raw=True), identify the 1-based inclusive range
        (N+1 is end-of-body), call `update` with begin/end passing only
        the replacement lines; whole-body for multi-section or uncertain
        changes."""
        result = update_gol("abc-123")
        self.assertIn("get_gol(id, raw=True)", result)
        self.assertIn("1-based, inclusive line range", result)
        self.assertIn("begin = end = N+1", result)
        self.assertIn('update(id, type="gol", content, begin=..., end=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_gol(id, raw=True)"),
            result.index('update(id, type="gol", content, begin=..., end=...)'),
        )

    def test_mentions_showing_which_sections_are_present(self):
        """The prompt must instruct showing which sections are already present
        vs. empty, and asking which to add or revise."""
        result = " ".join(update_gol("abc-123").split())
        self.assertIn("are already present with content and which are still absent", result)
        for section in (
            "## Description",
            "## Priority",
            "## Tags",
            "## Related Artifacts",
            "## More Information",
            "## Notes",
        ):
            self.assertIn(section, result)

    def test_mentions_eliciting_revisions_via_question_tool(self):
        """The prompt must instruct using the question tool to elicit new/revised text."""
        result = update_gol("abc-123")
        self.assertIn("question", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_gol("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_gol("abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_set_status_as_separate_optional_followup(self):
        """The generic `set_status` tool (type="gol") must be framed as a separate,
        optional follow-up, with the goal-specific `implemented`/`rejected`/
        `superseded` semantics."""
        result = update_gol("abc-123")
        self.assertIn("separate, optional", result)
        self.assertIn("implemented", result)
        self.assertIn("rejected", result)
        self.assertIn("superseded", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from gol/data/gol_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "gol_update_instructions.md"
            instructions_path.write_text("first $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_gol("abc-123")
                instructions_path.write_text("second $id", encoding="utf-8")
                second = update_gol("abc-123")

            self.assertEqual(first, "first abc-123")
            self.assertEqual(second, "second abc-123")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_gol("abc-123")


if __name__ == "__main__":
    unittest.main()
